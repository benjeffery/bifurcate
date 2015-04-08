from matplotlib.path import Path
from random import random, randrange


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


class Drawing:
    def __init__(self):
        self.codes = []
        self.verts = []
        self._bez_codes = (Path.MOVETO,
                           Path.CURVE4,
                           Path.CURVE4,
                           Path.CURVE4,
                           Path.LINETO,
                           Path.CURVE4,
                           Path.CURVE4,
                           Path.CURVE4,
                           Path.CLOSEPOLY,
                           )
        self._line_codes = (Path.MOVETO,
                            Path.LINETO,
                            Path.LINETO,
                            Path.LINETO,
                            Path.CLOSEPOLY,
                            )

    def horiz_bezier_segment(self, start, end, width):
        mid = (start[0] + end[0]) / 2
        start = (start[0], start[1] + width / 2)
        end = (end[0], end[1] + width / 2)
        verts = [start,
            (mid, start[1]),
            (mid, end[1]),
            end
        ]
        end = (start[0], start[1] - width)
        start = (end[0], end[1] - width)
        verts += [start,
            (mid, start[1]),
            (mid, end[1]),
            end,
            (None, None)
        ]
        self.codes.append(self._bez_codes)
        self.verts.append(verts)

    def line_segment(self, start, end, width):
        one = (start[0], start[1] - width / 2)
        two = (start[0], start[1] + width / 2)
        four = (end[0], end[1] - width / 2)
        three = (end[0], end[1] + width / 2)
        self.codes.append(self._line_codes)
        self.verts.append((one,
                           two,
                           three,
                           four,
                           (None, None)))

    def paths(self):
        return (Path(verts, codes) for verts, codes in zip(self.verts, self.codes))


def draw(d, x, y, y_offset, width, delta_x, delta_y, children):
    #d.horiz_bezier_segment((x, y + y_offset), (x + delta_x, y + delta_y), width)
    d.line_segment((x, y+y_offset), (x+delta_x, y+delta_y), width)

    top = width
    for c in children:
        top = top - c.haplos  #(haplos = width)
        draw(d, x + delta_x, y + delta_y, top + (c.haplos / 2) - (width / 2), c.haplos, c.distance * 10, c.delta_y,
             c.children)


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
                #top down - len_0 is on top
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

