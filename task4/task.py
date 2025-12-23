# task4/task.py
# Реализация нечеткого управления (Мамдани) с дефаззификацией методом "первого максимума"
# main(temp_json, heating_json, rules_json, current_temp) -> float

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Dict, List, Tuple, Any, Optional


EPS = 1e-12


@dataclass(frozen=True)
class TermMF:
    """Кусочно-линейная (в т.ч. треугольная/трапециевидная) функция принадлежности.
    Задается точками (x, mu) с mu in [0, 1], x по возрастанию.
    """
    points: List[Tuple[float, float]]

    def mu(self, x: float) -> float:
        pts = self.points
        if not pts:
            return 0.0
        if x <= pts[0][0]:
            return float(max(0.0, min(1.0, pts[0][1])))
        if x >= pts[-1][0]:
            return float(max(0.0, min(1.0, pts[-1][1])))

        # найти отрезок
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            if x1 <= x <= x2:
                if abs(x2 - x1) < EPS:
                    return float(max(0.0, min(1.0, max(y1, y2))))
                t = (x - x1) / (x2 - x1)
                y = y1 + t * (y2 - y1)
                return float(max(0.0, min(1.0, y)))
        return 0.0

    def x_min_max(self) -> Tuple[float, float]:
        pts = self.points
        if not pts:
            return (0.0, 0.0)
        return (pts[0][0], pts[-1][0])

    def clip_first_x_at_level(self, level: float) -> Optional[float]:
        """Найти самое левое x, где mu(x) >= level.
        Возвращает None, если такого x нет на носителе.
        """
        level = float(max(0.0, min(1.0, level)))
        pts = self.points
        if not pts:
            return None

        # если уже в первой точке >= level
        if pts[0][1] >= level - EPS:
            return pts[0][0]

        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            # интересует только если на отрезке возможен переход через level
            # ищем первое x, где y(x) достигает level при движении слева направо
            # условия: либо y1 < level <= y2 (восходящий/частично восходящий),
            # либо y1 >= level (но это было бы поймано ранее), либо plateau.
            if y1 < level - EPS and y2 >= level - EPS:
                # линейная интерполяция, y1 < level <= y2
                if abs(y2 - y1) < EPS:
                    # почти горизонталь, но тогда y2~=y1<level, сюда не попадём
                    continue
                t = (level - y1) / (y2 - y1)
                t = max(0.0, min(1.0, t))
                return x1 + t * (x2 - x1)

            # отдельный случай: на отрезке y1==y2==level (плато ровно на уровне)
            if abs(y1 - level) < EPS and abs(y2 - level) < EPS:
                return x1

            # если на отрезке y1 < level и y2 < level — пропускаем
            # если y1 > level и y2 > level — тогда вход был раньше (но мы бы нашли ранее),
            # либо первая точка была <level, а потом резко >level без пересечения невозможна в линейной.

        return None


def _parse_var_json(s: str) -> Dict[str, Any]:
    try:
        data = json.loads(s)
    except Exception as e:
        raise ValueError(f"Некорректный JSON: {e}") from e
    if not isinstance(data, dict):
        raise ValueError("JSON должен быть объектом (словарём).")
    return data


def _parse_terms(var_data: Dict[str, Any]) -> Tuple[Dict[str, TermMF], Tuple[float, float]]:
    """Поддерживаем несколько форматов:
    1) {"terms": {"cold": [[x,mu], ...], "hot": [[x,mu], ...]}, "universe":[min,max]}
    2) {"cold": [[x,mu], ...], "hot": [[x,mu], ...], "universe":[min,max]}
    3) {"terms": {"cold": {"points":[...]} , ...}, "universe":[min,max]}
    """
    universe = var_data.get("universe")
    if universe is None:
        universe = var_data.get("domain")
    if universe is None:
        # если не задано — возьмём из всех точек позже
        universe = None
    else:
        if (
            not isinstance(universe, (list, tuple))
            or len(universe) != 2
            or not all(isinstance(v, (int, float)) for v in universe)
        ):
            raise ValueError("Поле universe/domain должно быть [min, max].")
        universe = (float(universe[0]), float(universe[1]))

    terms_obj = var_data.get("terms")
    if terms_obj is None:
        # возможно, термы лежат прямо в корне
        terms_obj = {k: v for k, v in var_data.items() if k not in ("universe", "domain")}

    if not isinstance(terms_obj, dict) or not terms_obj:
        raise ValueError("Не найдены термы (ожидается поле 'terms' или термы в корне JSON).")

    terms: Dict[str, TermMF] = {}

    all_x: List[float] = []
    for name, desc in terms_obj.items():
        points = None
        if isinstance(desc, dict):
            points = desc.get("points") or desc.get("mf") or desc.get("vertices")
        else:
            points = desc

        if not isinstance(points, list) or len(points) < 2:
            raise ValueError(f"Терм '{name}': points должен быть списком из >=2 точек [[x,mu], ...].")

        pts: List[Tuple[float, float]] = []
        for p in points:
            if (
                not isinstance(p, (list, tuple))
                or len(p) != 2
                or not isinstance(p[0], (int, float))
                or not isinstance(p[1], (int, float))
            ):
                raise ValueError(f"Терм '{name}': каждая точка должна быть [x, mu].")
            x, mu = float(p[0]), float(p[1])
            mu = max(0.0, min(1.0, mu))
            pts.append((x, mu))
            all_x.append(x)

        pts.sort(key=lambda t: t[0])
        terms[str(name)] = TermMF(points=pts)

    if universe is None:
        if not all_x:
            universe = (0.0, 0.0)
        else:
            universe = (float(min(all_x)), float(max(all_x)))

    return terms, universe


def _parse_rules(rules_data: Any) -> List[Tuple[str, str]]:
    """Правила: ожидаем список или объект с полем rules.
    Форматы:
    - [{"if":"cold","then":"low"}, ...]
    - [{"temperature":"cold","heating":"low"}, ...]
    - {"rules":[...]}
    """
    if isinstance(rules_data, dict) and "rules" in rules_data:
        rules_data = rules_data["rules"]

    if not isinstance(rules_data, list) or not rules_data:
        raise ValueError("rules_json должен описывать список правил (или объект с полем 'rules').")

    rules: List[Tuple[str, str]] = []
    for r in rules_data:
        if not isinstance(r, dict):
            raise ValueError("Каждое правило должно быть объектом (словарём).")
        t = r.get("if") or r.get("temp
