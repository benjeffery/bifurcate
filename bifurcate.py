from collections import namedtuple
from math import sqrt
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


class Point:
    __slots__ = ('x', 'y')

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return "P({0.x}, {0.y})".format(self)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)

    def __mul__(self, o):
        return Point(self.x * o, self.y * o)

    def midpoint(self, other):
        return Point((self.x + other.x) / 2, (self.y + other.y) / 2)

    def distance(self, other):
        return sqrt(pow(self.x - other.x, 2) + pow(self.y - other.y, 2))

    def tuple(self):
        return (self.x, self.y)

class Circle:
    __slots__ = ('c', 'r')

    def __init__(self, c, r):
        if isinstance(r, Point):
            r = c.distance(r)
        self.c = c
        self.r = r

    def intersect(self, other):
        d = self.c.distance(other.c)
        # Too far apart
        if d > self.r + other.r:
            return ()
        #One inside other
        if other.r > d + self.r:
            return ()
        if self.r > d + other.r:
            return ()

        #Identical - actually infinite....
        if self.r == other.r and self.c == other.c:
            return ()

        #Touching point
        a = (self.r * self.r - other.r * other.r + d * d) / (2 * d)
        h = sqrt(self.r * self.r - a * a)
        tp = ((other.c - self.c) * (a / d)) + self.c

        return (Point(tp.x + h * (other.c.y - self.c.y) / d, tp.y - h * (other.c.x - self.c.x) / d),
                Point(tp.x - h * (other.c.y - self.c.y) / d, tp.y + h * (other.c.x - self.c.x) / d))


def find_rectangle(a, c, width, direction):
    mid = a.midpoint(c)
    w_c = Circle(a, width)
    r_c = Circle(mid, mid.distance(a))
    intersects = w_c.intersect(r_c)
    if len(intersects) < 2:
        raise ValueError()
    if direction == 'down':
        b = intersects[0] if intersects[0].y > intersects[1].y else intersects[1]
    else:
        b = intersects[0] if intersects[0].y < intersects[1].y else intersects[1]
    d = a + (c - b)
    return a, b, c, d


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
        self._hex_codes = (Path.MOVETO,
                            Path.LINETO,
                            Path.LINETO,
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

    def width_maintained_segment(self, start, end, width):
        print(start, end, width)
        start_u = (start[0], start[1] + width / 2)
        start_l = (start[0], start[1] - width / 2)
        end_u = (end[0], end[1] + width / 2)
        end_l = (end[0], end[1] - width / 2)

        if start[1] > end[1]:
            a,off_b,c,off_d = find_rectangle(Point(*start_l), Point(*end_u), width, 'down')
            self.codes.append(self._hex_codes)
            self.verts.append((start_u,
                               start_l,
                               off_d.tuple(),
                               end_l,
                               end_u,
                               off_b.tuple(),
                               (None, None)))
        else:
            a,off_b,c,off_d = find_rectangle(Point(*start_u), Point(*end_l), width, 'up')
            self.codes.append(self._hex_codes)
            self.verts.append((start_u,
                               start_l,
                               off_b.tuple(),
                               end_l,
                               end_u,
                               off_d.tuple(),
                               (None, None)))


    def paths(self):
        return (Path(verts, codes) for verts, codes in zip(self.verts, self.codes))


def draw(d, x, y, y_offset, width, delta_x, delta_y, children):
    # d.width_maintained_segment((100, 50), (200, 200), 50)
    # d.width_maintained_segment((100, 500), (200, 350), 50)
    # d.width_maintained_segment((280, 224.01), (360, 720), 16.52)
    # d.line_segment((x, y + y_offset), (x + delta_x, y + delta_y), width)
    try:
        d.width_maintained_segment((x, y + y_offset), (x + delta_x, y + delta_y), width)
    except:
        pass
    # d.line_segment((x, y + y_offset), (x + delta_x, y + delta_y), width)

    top = width
    for c in children:
        child_width = float(c.haplos)/20
        top = top - child_width  #(haplos = width)
        draw(d, x + delta_x, y + delta_y, top + (child_width / 2) - (width / 2), child_width, c.distance * 80, c.delta_y,
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

