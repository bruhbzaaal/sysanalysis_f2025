import numpy as np


def parse(s: str) -> dict:
    index_map = {}
    index = 0
    i = 0
    n = len(s)

    while i < n:
        if s[i] == '[':
            # найдем конец группы
            j = s.find(']', i)
            if j == -1:
                raise ValueError("Нет закрывающей скобки ']'")
            content = s[i+1:j]
            # разделим на токены внутри группы (учитываем пробелы)
            items = [t.strip() for t in content.split(',') if t.strip() != ""]
            for tok in items:
                index_map[tok] = index
            index += 1
            i = j + 1
        elif s[i] == ',' or s[i].isspace():
            i += 1
        else:
            # одиночный токен (до запятой или до следующей '[')
            start = i
            while i < n and s[i] not in ',[':
                i += 1
            tok = s[start:i].strip()
            if tok:
                index_map[tok] = index
                index += 1
            # не делаем i += 1 здесь — цикл продолжит с текущей позиции
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


def main(s1: str, s2: str) -> str:
    elements = [item.strip(',[]') for item in s1.split(',')]

    index_map_A = parse(s1)
    index_map_B = parse(s2)

    # Матрицы отношений
    matrix_A = matrix(index_map_A, elements)
    matrix_B = matrix(index_map_B, elements)

    # Транспонированные матрицы отношений
    matrix_AT = matrix_A.T
    matrix_BT = matrix_B.T

    # Поэлементная конъюнкция
    matrix_AB = matrix_A * matrix_B
    matrix_ABT = matrix_AT * matrix_BT

    # Поэлементная дизъюнкция
    matrix_dis = matrix_AB + matrix_ABT

    # Нахождение нулевых элементов в результирующей матрице
    false_coords = list(zip(*np.where(~matrix_dis)))
    unique_pairs_index = {tuple(sorted(p)) for p in false_coords}
    result = [(elements[i], elements[j]) for i, j in unique_pairs_index]

    return result


str1 = "1,[2,3],4,[5,6,7],8,9,10"
str2 = "[1,2],[3,4,5],6,7,9,[8,10]"
str3 = "x1,[x2,x3],x4,[x5,x6,x7],x8,x9,x10"
str4 = "x3,[x1,x4],x2,x6,[x5,x7,x8],[x9,x10]"
print(main(str1, str2))
