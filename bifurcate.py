import drawing

class Node:
    __slots__ = ('haplos', 'children', 'distance', 'delta_y', 'post_nonsplit')

    def __init__(self, haplos, children=(), distance=0, delta_y=0, post_nonsplit=False):
        self.haplos = haplos
        self.children = children
        self.distance = distance
        self.delta_y = delta_y
        self.post_nonsplit = post_nonsplit

    def __repr__(self):
        return 'h:' + str(self.haplos) + ' d:' + str(self.distance) + ' y:' + str(self.delta_y) + ' c:' + str(
            len(self.children)) + '(' + ','.join(map(repr, self.children)) + ')'

def tree(matrix):
    # First dim is variants
    nodes = (Node(list(range(matrix.shape[1]))),)
    new_nodes = nodes

    for i_var in range(matrix.shape[0]):
        nodes_todo = []
        calls = matrix[i_var]
        for node in new_nodes:
            separation = {}
            for j_hap in node.haplos:
                val = calls[j_hap]
                separation.setdefault(val, []).append(j_hap)
            node.distance += 1
            if len(separation) > 1:
                if len(separation[0]) < len(separation[1]):
                    separation[0], separation[1] = separation[1], separation[0]
                # top down - len_0 is on top
                len_p = len(node.haplos)
                len_0 = len(separation[0])
                len_1 = len(separation[1])
                mid = len_p - (2 * len_0)
                node.children = (
                    Node(separation[0], delta_y=mid + len_0),
                    Node(separation[1], delta_y=mid - len_1)
                )
                node.haplos = len(node.haplos)
                nodes_todo += node.children
            else:
                if (not node.post_nonsplit) and node.distance == 1:
                    new_node = Node(node.haplos, delta_y=0, post_nonsplit=True)
                    node.children = (new_node,)
                    node.haplos = len(node.haplos)
                    nodes_todo.append(new_node)
                else:
                    nodes_todo.append(node)

        new_nodes = nodes_todo
    for node in new_nodes:
        node.haplos = len(node.haplos)
    return nodes

