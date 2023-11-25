import igraph as ig
import plotly.graph_objs as go
import chardet
from collections import deque
import timeit
# Класс, представляющий узел бинарного дерева
class TreeNode:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.left = None
        self.right = None

# Вставка узла в бинарное дерево
def insert(root, key, value):
    if root is None:
        return TreeNode(key, value)
    if key < root.key:
        root.left = insert(root.left, key, value)
    elif key > root.key:
        root.right = insert(root.right, key, value)
    else:
        # Если ключ уже существует в дереве, увеличиваем его значение (количество)
        root.value += value
    return root

# Поиск узла по ключу
def search(root, key):
    if root is None or root.key == key:
        return root
    if key < root.key:
        return search(root.left, key)
    return search(root.right, key)

# Нахождение узла с минимальным ключом в поддереве
def minValueNode(node):
    current = node
    while current.left is not None:
        current = current.left
    return current

# Удаление узла по ключу
def deleteNode(root, key, operations=0):
    if root is None:
        return root, operations, 0

    # Инициализируем счетчики и замер времени выполнения
    start_time = timeit.default_timer()

    if key < root.key:
        root.left, operations, _ = deleteNode(root.left, key, operations)
        operations += 1
    elif key > root.key:
        root.right, operations, _ = deleteNode(root.right, key, operations)
        operations += 1
    else:
        if root.left is None:
            return root.right, operations + 1, timeit.default_timer() - start_time  # Операция удаления
        elif root.right is None:
            return root.left, operations + 1, timeit.default_timer() - start_time  # Операция удаления

        min_right_subtree = minValueNode(root.right)
        original_key = root.key

        root.key = min_right_subtree.key
        root.value = min_right_subtree.value

        root.right, operations, _ = deleteNode(root.right, min_right_subtree.key, operations)
        min_right_subtree.key = original_key

    # Завершаем замер времени выполнения
    end_time = timeit.default_timer()
    elapsed_time = end_time - start_time

    return root, operations, elapsed_time

def deleteNodesByValue(root, value):
    if root is None:
        return root, 0, 0

    # Создаем очередь для обхода BFS
    queue = deque()
    queue.append(root)

    parent_nodes = []  # Список для хранения родительских узлов текущего узла
    nodes_to_keep = []  # Список для хранения узлов, которые не будут удалены
    operations = 0  # Счетчик операций (итераций)

    start_time = timeit.default_timer()  # Начинаем замер времени выполнения

    while queue:
        current_node = queue.popleft()
        operations += 1  # Увеличиваем счетчик операций для каждого узла

        if current_node.value == value:
            # Операция удаления
            if parent_nodes:
                parent_node = parent_nodes[-1]
                if parent_node.left == current_node:
                    parent_node.left = None
                else:
                    parent_node.right = None
            else:
                return None, operations, timeit.default_timer() - start_time  # Операция удаления корневого узла
        else:
            nodes_to_keep.append(current_node)  # Добавляем узел в список для сохранения

        if current_node.left:
            queue.append(current_node.left)  # Добавляем левого потомка в очередь для обхода
            parent_nodes.append(current_node)  # Добавляем текущий узел в список родительских узлов

        if current_node.right:
            queue.append(current_node.right)  # Добавляем правого потомка в очередь для обхода
            parent_nodes.append(current_node)  # Добавляем текущий узел в список родительских узлов

    # Перестраиваем дерево с учетом сохраненных узлов
    new_root = None
    for node in nodes_to_keep:
        new_root = insert(new_root, node.key, node.value)

    # Завершаем замер времени выполнения
    end_time = timeit.default_timer()
    elapsed_time = end_time - start_time

    return new_root, operations, elapsed_time


# Создание графа на основе бинарного дерева
def create_graph(root):
    g = ig.Graph(directed=True)  # Создаем ориентированный граф

    nodes = []  # Список для хранения узлов (вершин) графа
    edges = []  # Список для хранения ребер (связей) графа

    # Функция для добавления узлов и ребер в граф
    def add_node(node):
        node_id = f"{node.key}: {node.value}"  # Создаем уникальный идентификатор узла в формате "ключ: значение"
        nodes.append(node_id)  # Добавляем узел в список узлов

        # Если у узла есть левый потомок, добавляем ребро между текущим узлом и левым потомком
        if node.left:
            edges.append((node_id, f"{node.left.key}: {node.left.value}"))
            add_node(node.left)

        # Если у узла есть правый потомок, добавляем ребро между текущим узлом и правым потомком
        if node.right:
            edges.append((node_id, f"{node.right.key}: {node.right.value}"))
            add_node(node.right)

    if root:
        add_node(root)  # Начинаем добавление узлов и ребер, начиная с корневого узла

    # Добавляем вершины (узлы) и ребра (связи) в граф
    g.add_vertices([str(node) for node in nodes])
    g.add_edges([(str(edge[0]), str(edge[1])) for edge in edges])

    return g  # Возвращаем созданный граф

def visualize_tree(root, search_symbol=None, added_symbol=None):
    g = create_graph(root)
    layt = g.layout('tree')
    position = {k: layt[k] for k in range(len(g.vs))}

    edge_x = []
    edge_y = []
    for edge in g.get_edgelist():
        x0, y0 = position[edge[0]]
        x1, y1 = position[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    node_x = []
    node_y = []
    node_text = []
    node_hovertext = []
    node_colors = []

    for node in g.vs:
        x, y = position[node.index]
        node_x.append(x)
        node_y.append(y)
        node_key, _ = node["name"].split(": ")  # Разделяем имя на ключ и значение
        node_text.append(node["name"])
        node_hovertext.append(node["name"])
        if node_key == str(added_symbol):
            node_colors.append('green')  # Окрашиваем вставленный узел в зеленый цвет
        elif node_key == str(search_symbol):
            node_colors.append('blue')  # Окрашиваем найденный узел в синий цвет
        else:
            node_colors.append('lightgray')

    edge_trace = go.Scatter(x=edge_x, y=edge_y, line=dict(width=0.5, color='#888'), hoverinfo='none', mode='lines')
    node_trace = go.Scatter(x=node_x, y=node_y, mode='markers+text', hoverinfo='text', text=node_text,
                            textposition='bottom center', hovertext=node_hovertext,
                            marker=dict(color=node_colors, size=20))

    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(showlegend=False, hovermode='closest', margin=dict(b=0, l=0, r=0, t=0),
                                     xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                                     yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)))
    fig.show()

# Основная часть программы
root = None
symbol_counts = {}
file_path = 'text.txt'

# Определение кодировки файла
with open(file_path, 'rb') as file:
    result = chardet.detect(file.read())
file_encoding = result['encoding']

# Чтение текста из файла и подсчет символов
with open(file_path, 'r', encoding=file_encoding) as file:
    text = file.read()

for symbol in text:
    symbol_counts[symbol] = symbol_counts.get(symbol, 0) + 1

# Вставка символов и их количества в бинарное дерево
for symbol, count in symbol_counts.items():
    root = insert(root, symbol, count)

# Отображение текстового меню
def display_menu():
    print("Меню бинарного дерева поиска:")
    print("1. Вставить узел")
    print("2. Удалить узел")
    print("3. Удалить узел по количеству символов")
    print("4. Найти узел")
    print("5. Визуализировать дерево")
    print("6. Выход")

if __name__ == "__main__":
    while True:
        display_menu()
        choice = input("Введите ваш выбор: ")
        if choice == "1":
            key = input("Введите символ: ")
            value = int(input("Введите количество: "))
            root = insert(root, key, value)
            visualize_tree(root, None, key)
        elif choice == "2":
            key = input("Введите символ для удаления: ")
            root, operations, elapsed_time = deleteNode(root, key)
            print(f"Выполнено операций: {operations}")
            print(f"Время выполнения: {elapsed_time} секунд")
            visualize_tree(root)
        if choice == "3":
            value = int(input("Введите количество символов для удаления: "))
            root, operations, elapsed_time = deleteNodesByValue(root, value)
            print(f"Выполнено операций: {operations}")
            print(f"Время выполнения: {elapsed_time} секунд")
            visualize_tree(root)
        elif choice == "4":
            key = input("Введите символ для поиска: ")
            node = search(root, key)
            if node:
                print(f"Узел найден: {node.key}: {node.value}")
                visualize_tree(root, key)
            else:
                print("Узел не найден.")
        elif choice == "5":
            visualize_tree(root)
        elif choice == "6":
            break
        else:
            print(" ")
