from typing import List, Tuple, Dict

def main(s: str, e: str) -> Tuple[
    List[List[bool]],  # A  - матрица смежности
    List[List[bool]],  # r1 - непосредственное управление
    List[List[bool]],  # r2 - непосредственное подчинение (= r1^T)
    List[List[bool]],  # r3 - опосредованное управление
    List[List[bool]],  # r4 - опосредованное подчинение (= r3^T)
    List[List[bool]]   # r5 - соподчинение
]:
    """
    s: CSV-строка рёбер вида "1,2\\n1,3\\n3,4"
    e: идентификатор корня (число в строковом виде)

    Возвращает (A, r1, r2, r3, r4, r5)
    Порядок вершин — числовой (1, 2, 3, ...)
    """

    # ---- 1) Чтение рёбер ----
    edges = []
    for line in s.strip().splitlines():
        u, v = map(str.strip, line.split(","))
        edges.append((u, v))

    # ---- 2) Множество вершин ----
    nodes = {e}
    for u, v in edges:
        nodes.add(u); nodes.add(v)

    # ---- 3) Упорядочиваем вершины по числу ----
    order = sorted(nodes, key=lambda x: int(x))
    idx: Dict[str, int] = {v: i for i, v in enumerate(order)}
    n = len(order)

    # ---- 4) Дерево: дети и родитель ----
    children: Dict[str, List[str]] = {v: [] for v in order}
    parent: Dict[str, str] = {}
    for u, v in edges:
        children[u].append(v)
        parent[v] = u

    # ---- 5) Вспомогательная: расстояние "u → v" ----
    def ancestor_distance(u: str, v: str) -> int:
        """Возвращает длину пути, если u — предок v; иначе -1"""
        d, cur = 0, v
        while cur in parent:
            p = parent[cur]; d += 1
            if p == u:
                return d
            cur = p
        return -1

    # ---- 6) Пустая матрица ----
    def mat() -> List[List[bool]]:
        return [[False]*n for _ in range(n)]

    # ---- 7) Инициализация ----
    A  = mat()
    r1 = mat()
    r2 = mat()
    r3 = mat()
    r4 = mat()
    r5 = mat()

    # ---- 8) A и r1 ----
    for u, v in edges:
        iu, iv = idx[u], idx[v]
        A[iu][iv]  = True
        r1[iu][iv] = True

    # ---- 9) r2 = r1^T ----
    for i in range(n):
        for j in range(n):
            if r1[i][j]:
                r2[j][i] = True

    # ---- 10) r3 и r4 (опосредованные) ----
    for a in order:
        ia = idx[a]
        for d in order:
            if a == d:
                continue
            dist = ancestor_distance(a, d)
            if dist >= 2:
                idd = idx[d]
                r3[ia][idd] = True
                r4[idd][ia] = True

    # ---- 11) r5 (общий непосредственный родитель) ----
    for p, vs in children.items():
        for i in range(len(vs)):
            for j in range(len(vs)):
                if i != j:
                    r5[idx[vs[i]]][idx[vs[j]]] = True

    return A, r1, r2, r3, r4, r5


# --- тест ---
if __name__ == "__main__":
    E = "1,2\n1,3\n3,4\n3,5"
    root = "1"
    A, r1, r2, r3, r4, r5 = main(E, root)
    names = ["A", "r1","r2","r3","r4","r5"]
    order = sorted({root, *[x for pair in E.splitlines() for x in pair.split(",")]}, key=int)
    for M, name in zip((A,r1,r2,r3,r4,r5), names):
        pairs = [(order[i], order[j]) for i in range(len(order)) for j in range(len(order)) if M[i][j]]
        print(name, pairs)
