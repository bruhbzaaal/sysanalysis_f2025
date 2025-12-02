import numpy as np


def parse(s: str) -> dict:
    if s.startswith('[') and s.endswith(']'):
        s = s[1:-1].strip()
        
    index_map = {}
    index = 0
    i = 0
    n = len(s)

    while i < n:
        if s[i] == '[':
            j = s.find(']', i)
            if j == -1:
                raise ValueError("Нет закрывающей скобки ']'")
            content = s[i+1:j]
            items = [t.strip() for t in content.split(',') if t.strip() != ""]
            for tok in items:
                index_map[tok] = index
            index += 1
            i = j + 1
        elif s[i] == ',' or s[i].isspace():
            i += 1
        else:
            start = i
            while i < n and s[i] not in ',[':
                i += 1
            tok = s[start:i].strip()
            if tok:
                index_map[tok] = index
                index += 1
    return index_map


def matrix(index_map, elements):
    n = len(elements)
    matrix = np.zeros((n, n), bool)
    for first_idx_elem in range(n):
        first_idx_map = index_map[elements[first_idx_elem]]
        for second_idx_elem in range(n):
            second_idx_map = index_map[elements[second_idx_elem]]
            if first_idx_map <= second_idx_map:
                matrix[first_idx_elem][second_idx_elem] = 1
    return matrix


def main(str1: str, str2: str):
    elements = [item.strip(',[]') for item in str1.split(',')]

    index_map_A = parse(str1)
    index_map_B = parse(str2)
    matrix_A = matrix(index_map_A, elements)
    matrix_B = matrix(index_map_B, elements)

    matrix_AT = matrix_A.T
    matrix_BT = matrix_B.T

    matrix_AB = matrix_A * matrix_B
    matrix_ABT = matrix_AT * matrix_BT
    matrix_dis = matrix_AB + matrix_ABT

    # Ядро противоречий
    false_coords = list(zip(*np.where(~matrix_dis)))
    unique_pairs_index = {tuple(sorted(p)) for p in false_coords}
    contradictions = [(elements[i], elements[j])
                      for i, j in unique_pairs_index]

    # Матрица согласованного порядка
    C = matrix_AB.copy()

    # Учёт противоречий
    for (a, b) in contradictions:
        i = elements.index(a)
        j = elements.index(b)
        C[i, j] = 1
        C[j, i] = 1

    # Матрица эквивалентности
    E = C * C.T

    # Транзитивное замыкание матрицы E
    n = len(elements)
    E_star = E.copy()
    for k in range(n):
        for i in range(n):
            for j in range(n):
                E_star[i, j] = E_star[i, j] or (E_star[i, k] and E_star[k, j])

    # Поиск компонентов связности — кластеров
    visited = [False] * n
    clusters = []
    for i in range(n):
        if not visited[i]:
            cluster = []
            for j in range(n):
                if E_star[i, j]:
                    cluster.append(elements[j])
                    visited[j] = True
            clusters.append(cluster)

    # Сортировка кластеров по матрице C
    def cluster_less(c1, c2):
        for a in c1:
            ia = elements.index(a)
            for b in c2:
                ib = elements.index(b)
                if C[ia, ib] == 0:
                    return False
        return True

    changed = True
    while changed:
        changed = False
        for i in range(len(clusters) - 1):
            if cluster_less(clusters[i+1], clusters[i]):
                clusters[i], clusters[i+1] = clusters[i+1], clusters[i]
                changed = True

    result = []
    for c in clusters:
        if len(c) == 1:
            result.append(c[0])
        else:
            result.append(c)

    return result


str1 = '[1,[2,3],4,[5,6,7],8,9,10]'
str2 = '[[1,2],[3,4,5],6,7,9,[8,10]]'
print(main(str1, str2))

str3 = "[x1,[x2,x3],x4,[x5,x6,x7],x8,x9,x10]"
str4 = "[x3,[x1,x4],x2,x6,[x5,x7,x8],[x9,x10]]"
# print(main(str3, str4))

str5 = '[T,[K,M],D,Z]'
str6 = '[[T,K],M,Z,D]'
# print(main(str5, str6))
