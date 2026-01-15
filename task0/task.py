import pandas as pd

graph = pd.read_csv("task2.csv", header=None)

edges = []

for index, row in graph.iterrows():
    a = int(row[0])
    b = int(row[1])
    edges.append([a, b])

print("Ребра:", edges)

number_of_vertexes = 0
for u, v in edges:
        if u > number_of_vertexes:
            number_of_vertexes = u
        if v > number_of_vertexes:
            number_of_vertexes = v

size = number_of_vertexes + 1
matrix = []

for i in range(size):
     row = [0] * size
     matrix.append(row)

for i, j in edges:
     matrix[i][j] = 1
     matrix[j][i] = 1 

for row in matrix:
     print(row)
