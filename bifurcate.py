from matplotlib.path import Path
from random import random, randrange


class Node:
    __slots__ = ('haplos', 'children', 'distance', 'delta_y')
    def __init__(self, haplos, children=(), distance=0, delta_y=0):
        self.haplos = haplos
        self.children = children
        self.distance = distance
        self.delta_y = delta_y

    def __repr__(self):
        return '' + str(self.haplos) + ':'+ str(self.distance) + '(' + ','.join(map(repr, self.children))+')'

class Drawing:
    def __init__(self):
        self.codes = []
        self.verts = []
        self._bez_codes = (Path.MOVETO,
         Path.CURVE4,
         Path.CURVE4,
         Path.CURVE4,)

    def horiz_bezier(self, start, end):
        mid = (start[0] + end[0]) / 2
        self.verts += (start,
                 (mid, start[1]),
                 (mid, end[1]),
                 end)
        self.codes += self._bez_codes

    def line(self, start, end):
        self.verts += (start, end)
        self.codes += (Path.MOVETO,
                       Path.LINETO)

    def path(self):
        return Path(self.verts, self.codes)

def draw(d, x, y, y_offset, width, delta_x, delta_y, children):
    hwidth = width/2

    d.horiz_bezier((x, y+hwidth+y_offset), (x+delta_x, y+delta_y+hwidth))
    d.horiz_bezier((x, y-hwidth+y_offset), (x+delta_x, y+delta_y-hwidth))

    top = width
    for c in children:
        top = top - c.haplos#(haplos = width)
        draw(d, x+delta_x, y+delta_y, top + (c.haplos/2) - (width/2), c.haplos, c.distance, c.delta_y, c.children)


def tree(matrix):
    #First dim is variants
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
                #top down - len_0 is on top
                len_p = len(node.haplos)
                len_0 = len(separation[0])
                len_1 = len(separation[1])
                mid = len_p-(2*len_0)
                node.children = (
                    Node(separation[0], delta_y=mid+len_0),
                    Node(separation[1], delta_y=mid-len_1)
                )
                node.haplos = len(node.haplos)
                nodes_todo += node.children
            else:
                nodes_todo.append(node)

        new_nodes = nodes_todo
    for node in new_nodes:
        node.haplos = len(node.haplos)
    return nodes

