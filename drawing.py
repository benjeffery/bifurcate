from math import sqrt, asin, degrees, atan2, fabs
from matplotlib import patches
from matplotlib.path import Path

def get_ax_size(ax):
    fig = ax.get_figure()
    bbox = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    width, height = bbox.width, bbox.height
    width *= fig.dpi
    height *= fig.dpi
    return width, height

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

    def __len__(self):
        return sqrt(pow(self.x, 2) + pow(self.y, 2))

    def midpoint(self, other):
        return Point((self.x + other.x) / 2, (self.y + other.y) / 2)

    def distance(self, other):
        return sqrt(pow(self.x - other.x, 2) + pow(self.y - other.y, 2))

    def tuple(self):
        return self.x, self.y

    def angle(self):
        return degrees(atan2(self.y, self.x))



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
        # One inside other
        if other.r > d + self.r:
            return ()
        if self.r > d + other.r:
            return ()

        # Identical - actually infinite....
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


def path_maker(func):
    def wrapped(self, *args, **kwargs):
        path = func(self, *args, **kwargs)
        if path:
            patch = patches.PathPatch(Path(*path), **self.drawing_kwargs)
            self.patches.append(patch)
    return wrapped

def path_maker_with_width(func):
    def wrapped(self, *args, **kwargs):
        path, width, col = func(self, *args, **kwargs)
        if path:
            patch = patches.PathPatch(Path(*path), edgecolor=col, lw=width, **self.drawing_kwargs)
            self.patches.append(patch)
    return wrapped


class Drawing:
    def __init__(self, **drawing_kwargs):
        self.drawing_kwargs = drawing_kwargs
        self.patches = []
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
        self._quad_codes = (Path.MOVETO,
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

    @path_maker
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
        return verts, self._bez_codes

    @path_maker
    def line_segment(self, start, end, width):
        one = (start[0], start[1] - width / 2)
        two = (start[0], start[1] + width / 2)
        four = (end[0], end[1] - width / 2)
        three = (end[0], end[1] + width / 2)
        return (one,
                two,
                three,
                four,
                (None, None)), self._quad_codes

    def arc_from_three_points(self, center, a, b):
        h = center.distance(a)
        a = a-center
        b = b-center
        ab = b.angle()
        aa = a.angle()
        #Sometimes we draw a full circle when we should draw nothing due to floating point errors, so test for rough equality
        if not (fabs(aa - ab) < 0.01):
            self.patches.append(patches.Wedge(center.tuple(), h, ab, aa,  **self.drawing_kwargs))

    @path_maker_with_width
    def simple_line(self, start, end, width, colour):
        return (((start,end),
               (Path.MOVETO,
                Path.LINETO,)),
                width/3, colour)

    @path_maker
    def width_maintained_segment(self, start, end, width):
        start_u = (start[0], start[1] + width / 2)
        start_l = (start[0], start[1] - width / 2)
        end_u = (end[0], end[1] + width / 2)
        end_l = (end[0], end[1] - width / 2)

        if start[1] > end[1]:
            try:
                a, off_b, c, off_d = find_rectangle(Point(*start_l), Point(*end_u), width, 'down')
                self.arc_from_three_points(Point(*start_l), Point(*start_u), off_b)
                self.arc_from_three_points(Point(*end_u), Point(*end_l), off_d)
                return (start_l,
                        off_d.tuple(),
                        end_u,
                        off_b.tuple(),
                        (None, None)), self._quad_codes
            except ValueError:
                return
                dist = end_l[0] - start_l[0]
                extra = width - dist
                start_l = (start_l[0] - extra / 2, start_l[1])
                start_u = (start_u[0] - extra / 2, start_u[1])
                end_l = (end_l[0] + extra / 2, end_l[1])
                end_u = (end_u[0] + extra / 2, end_u[1])
                a, off_b, c, off_d = find_rectangle(Point(*start_l), Point(*end_u), width, 'down')
                self.arc_from_three_points(Point(*start_l), Point(*start_u), off_b)
                self.arc_from_three_points(Point(*end_u), Point(*end_l), off_d)
                return (start_l,
                        off_d.tuple(),
                        end_u,
                        off_b.tuple(),
                        (None, None)), self._quad_codes

        else:
            try:
                a, off_b, c, off_d = find_rectangle(Point(*start_u), Point(*end_l), width, 'up')
                self.arc_from_three_points(Point(*start_u), off_b, Point(*start_l))
                self.arc_from_three_points(Point(*end_l), off_d, Point(*end_u))
                return (start_u,
                        off_b.tuple(),
                        end_l,
                        off_d.tuple(),
                        (None, None)), self._quad_codes
            except ValueError:
                # dist = end_l[0] - start_l[0]
                # extra = width - dist
                # start_l = (start_l[0] - extra / 2, start_l[1])
                # start_u = (start_u[0] - extra / 2, start_u[1])
                # end_l = (end_l[0] + extra / 2, end_l[1])
                # end_u = (end_u[0] + extra / 2, end_u[1])
                # a, off_b, c, off_d = find_rectangle(Point(*start_u), Point(*end_l), width, 'up')
                # self.arc_from_three_points(Point(*start_u), off_b, Point(*start_l))
                # self.arc_from_three_points(Point(*end_l), off_d, Point(*end_u))
                # return (start_u,
                #         off_b.tuple(),
                #         end_l,
                #         off_d.tuple(),
                #         (None, None)), self._quad_codes
                start_u = Point(*start_u)
                end_l = Point(*end_l)
                mid = start_u.midpoint(end_l)
                hw = width/2
                extension = hw / start_u.distance(mid)
                start_ext = ((start_u-mid)*extension)+mid
                end_ext = ((end_l-mid)*extension)+mid
                gap = end[0] - start[0]
                overdraw = (width - gap)/2
                mid = mid.tuple()
                left = mid[0] - hw
                right = mid[0] + hw
                top = end_u[1]
                bottom = start_l[1]
                print(top, bottom, left, right)
                self.patches.append(patches.Circle(mid, hw,  **self.drawing_kwargs))
                #self.patches.append(patches.Circle(start_ext.tuple(), hw,  **self.drawing_kwargs))
                return None
                # return ((start_u.tuple(),
                #         start_ext.tuple(),
                #          end_u,
                #          end_l.tuple(),
                #         end_ext.tuple(),
                #         start_l,
                #          (None, None)),
                #         self._hex_codes)
                #
                # return (((left, bottom),
                #         (left, top),
                #          (right, top),
                #          (right, bottom),
                #         (None, None)),
                #         self._quad_codes)


    def patches(self):
        return self.patches


