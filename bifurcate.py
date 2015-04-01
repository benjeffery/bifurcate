from matplotlib.path import Path


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
    for c_width, c_delta_x, c_delta_y, c_children in children:
        top = top - c_width
        draw(d, x+delta_x, y+delta_y, top + (c_width/2) - (width/2), c_width, c_delta_x, c_delta_y, c_children)



