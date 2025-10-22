from typing import List, Tuple, Dict
from math import log, e

def main(s: str, e_root: str) -> Tuple[float, float]:
    """
    Вход:
      s      — CSV-строка рёбер ориентированного дерева: '1,2\\n1,3\\n3,4\\n3,5'
      e_root — ER-идентификатор корня (строка, допускается любое число/строка)

    Выход:
      (H, h) — кортеж из (энтропия структуры, нормированная оценка),
               оба значения округлены до 1 знака после запятой.
    """

    # ---------- 1) Парсинг рёбер и множество вершин ----------
    edges: List[Tuple[str, str]] = []
    if s.strip():
        for line in s.strip().splitlines():
            u, v = map(str.strip, line.split(","))
            edges.append((u, v))

    nodes = {e_root}
    for u, v in edges:
        nodes.add(u); nodes.add(v)

    # Упорядочим вершины: если все метки числа — по числу, иначе — лексикографически
    def is_int(x: str) -> bool:
        try:
            int(x); return True
        except ValueError:
            return False

    all_int = all(is_int(x) for x in nodes)
    order = sorted(nodes, key=(lambda x: int(x)) if all_int else None)
    idx: Dict[str, int] = {v: i for i, v in enumerate(order)}
    n = len(order)

    # Граничный случай: одна вершина -> связей нет, энтропия ноль
    if n <= 1:
        return (0.0, 0.0)

    # ---------- 2) Дерево: дети и родитель ----------
    children: Dict[str, List[str]] = {v: [] for v in order}
    parent: Dict[str, str] = {}
    for u, v in edges:
        children[u].append(v)
        parent[v] = u

    # ---------- 3) Вспомогательная: расстояние предок->потомок ----------
    def ancestor_distance(u: str, v: str) -> int:
        """d >= 1 если u — предок v на расстоянии d (число рёбер); иначе -1."""
        d, cur = 0, v
        while cur in parent:
            p = parent[cur]; d += 1
            if p == u:
                return d
            cur = p
        return -1

    # ---------- 4) Матрицы отношений r1..r5 ----------
    def mat() -> List[List[bool]]:
        return [[False]*n for _ in range(n)]

    # r1: непосредственное управление (u -> v, прямое ребро)
    r1 = mat()
    for u, v in edges:
        r1[idx[u]][idx[v]] = True

    # r2: непосредственное подчинение = r1^T
    r2 = mat()
    for i in range(n):
        for j in range(n):
            if r1[i][j]:
                r2[j][i] = True

    # r3: опосредованное управление (ancestor -> descendant, dist >= 2)
    # r4: опосредованное подчинение = r3^T
    r3 = mat()
    r4 = mat()
    for a in order:
        ia = idx[a]
        for dnode in order:
            if a == dnode: 
                continue
            dist = ancestor_distance(a, dnode)
            if dist >= 2:
                idd = idx[dnode]
                r3[ia][idd] = True
                r4[idd][ia] = True

    # r5: соподчинение (общий непосредственный родитель; упорядоченные пары)
    r5 = mat()
    for p, vs in children.items():
        m = len(vs)
        for i in range(m):
            for j in range(m):
                if i != j:
                    r5[idx[vs[i]]][idx[vs[j]]] = True

    relations = [r1, r2, r3, r4, r5]  # k = 5 отношений

    # ---------- 5) Энтропия структуры H(M,R) ----------
    # lij — число исходящих связей элемента j в отношении i -> это сумма по строке j матрицы ri
    # P = lij / (n-1); H_part = -P * log2(P); 0*log2(0) считаем 0
    denom = n - 1
    H = 0.0

    # логарифм по основанию 2 через натуральный логарифм
    ln2 = log(2.0)

    for ri in relations:
        for j in range(n):
            lij = sum(1 for val in ri[j] if val)
            if lij == 0 or denom == 0:
                continue
            P = lij / denom
            H -= P * (log(P) / ln2)

    # ---------- 6) Нормированная сложность h ----------
    # H_ref = c * n * k, где c = 1 / (e * ln 2), k = 5
    c = 1.0 / (e * ln2)
    k = 5
    H_ref = c * n * k
    h = (H / H_ref) if H_ref > 0 else 0.0

    # ---------- 7) Округление до 1 знака ----------
    H_rounded = round(H, 1)
    h_rounded = round(h, 1)
    return H_rounded, h_rounded


# --- Пример локальной проверки (совпадает с примером из методички) ---
if __name__ == "__main__":
    E = "1,2\n1,3\n3,4\n3,5"
    root = "1"
    H, h = main(E, root)
    print(H, h)  # Ожидается: 6.5 0.5
