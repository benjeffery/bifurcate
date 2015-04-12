import drawing

class Node:
    __slots__ = ('haplos', 'children', 'parent', 'distance', 'delta_y', 'post_nonsplit', 'splits')

    def __init__(self, haplos, children=(), parent=None, distance=0, delta_y=0, post_nonsplit=False):
        self.haplos = haplos
        self.children = children
        self.parent = parent
        self.distance = distance
        self.delta_y = delta_y
        self.post_nonsplit = post_nonsplit
        self.splits = -1

    def __repr__(self):
        return 'h:' + str(self.haplos) + ' d:' + str(self.distance) + ' y:' + str(self.delta_y) + ' c:' + str(
            len(self.children)) + '(' + ','.join(map(repr, self.children)) + ')'


class Tree:
    def __init__(self, matrix):
        self.matrix = matrix
        self.root_node = None
        self.nodes = []
        self.leaf_nodes = []
        self.create_tree()

    def create_tree(self):
        # First dim is variants
        self.nodes = []
        self.root_node = Node(list(range(self.matrix.shape[1])))
        new_nodes = [self.root_node]
        self.nodes = []
        for i_var in range(self.matrix.shape[0]):
            nodes_todo = []
            calls = self.matrix[i_var]
            for node in new_nodes:
                separation = {}
                for j_hap in node.haplos:
                    val = calls[j_hap]
                    separation.setdefault(val, []).append(j_hap)
                node.distance += 1
                if len(separation) > 1:
                    node.children = (
                        Node(separation[0], parent=node),
                        Node(separation[1], parent=node)
                    )
                    self.nodes += node.children
                    node.haplos = len(node.haplos)
                    nodes_todo += node.children
                else:
                    if (not node.post_nonsplit) and node.distance == 1:
                        new_node = Node(node.haplos, parent=node, post_nonsplit=True)
                        node.children = (new_node,)
                        node.haplos = len(node.haplos)
                        nodes_todo.append(new_node)
                        self.nodes.append(new_node)
                    else:
                        nodes_todo.append(node)

            new_nodes = nodes_todo
        for node in new_nodes:
            node.haplos = len(node.haplos)
        self.leaf_nodes = [node for node in self.nodes if not node.children]

    def arrange_y(self, sample_width, split_width):
        nodes_todo = []
        for node in self.leaf_nodes:
            node.splits = 1
            if node.parent:
                nodes_todo.append(node.parent)
        while nodes_todo:
            node = nodes_todo.pop(0)
            if node.parent:
                nodes_todo.append(node.parent)
            if all(c.splits != -1 for c in node.children):
                if len(node.children) > 1:
                    node.splits = 1+sum(n.splits for n in node.children)
                else:
                    node.splits = node.children[0].splits

        nodes_todo = [self.root_node]
        while nodes_todo:
            node = nodes_todo.pop()
            nodes_todo += node.children
            if node.children:
                if len(node.children) > 1:
                    len_p = node.haplos*sample_width + node.splits*split_width
                    len_0 = node.children[0].haplos*sample_width + node.children[0].splits*split_width
                    len_1 = node.children[1].haplos*sample_width + node.children[1].splits*split_width
                    mid = len_p/2 - (len_0)
                    node.children[0].delta_y=mid + len_0/2
                    node.children[1].delta_y=mid - len_1/2







