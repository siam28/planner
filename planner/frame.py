"""
Represents frame (plane) defined by one or few polygons.
"""
from svgwrite import shapes, path, mm, masking, pattern
from shortuuid import uuid
import math


class Pline(object):

    """ Absctract PolyLine class """

    @property
    def uuid(self):
        if not hasattr(self, "_uuid"):
            self._uuid = uuid()
        return self._uuid

    def _draw(self):
        raise NotImplemented("Draw method is not yet implemented")

    def _mask(self):
        return False

class Rect(Pline):

    """ Rectangle representation """

    def __init__(self, x, y, width, height):
        """
        x, y - coordinates of left top corner
        """
        self.corner = (x, y)
        self.size = (width, height)

    def _draw(self):
        return shapes.Rect(self.corner, self.size)


class RectFrame(Pline):

    """ Rectangle frame representation """

    def __init__(self, x, y, width, height, wall_width):
        self.corner = (x * mm, y * mm)
        self.size = (width * mm, height * mm)
        self.inner_corner = ((x + wall_width) * mm, (y + wall_width) * mm)
        self.inner_size = ((width - 2 * wall_width) * mm, (height - 2 * wall_width) * mm)

    @property
    def _hatching_id(self):
        return "hatching-{}".format(self.uuid)

    def _draw(self):
        rect_params = {"stroke": "black", "stroke-width": "2"}
        res = []
        if hasattr(self, "hatch") and self.hatch:
            rect_params['style'] = "fill: url(#{})".format(self._hatching_id)
            res.append(self.hatch)
        if hasattr(self, "filling"):
            rect_params['fill'] = self.filling
        else:
            rect_params['fill'] = "#fff"
        rect = shapes.Rect(self.corner, self.size, **rect_params)
        inner_rect = shapes.Rect(self.inner_corner, self.inner_size, **{"stroke": "black", "stroke-width": "2", "fill": "#fff"})
        res.append(rect)
        res.append(inner_rect)
        return res

    def add_hatching(self, angle=45, distance=3, width=1, color="black"):
        """
        Add hatching to the walls.
        angle - angle of hatches in deg
        distance - distance between hatches
        width - stroke-width
        **Replaces all previously added hatchings of fillings.**
        """
        if hasattr(self, "filling"):
            del self.filling
        angle = math.radians(angle)
        style = "stroke: {color}; width: {width}".format(color=color, width=width)
        width = distance / math.sin(angle)
        height = width * math.tan(angle)
        self.hatch = pattern.Pattern((0 * mm, 0 * mm), (width * mm, height * mm), id=self._hatching_id, patternUnits="userSpaceOnUse")
        self.hatch.add(shapes.Rect((0 * mm, 0 * mm), (width * mm, height * mm), fill="#fff"))
        self.hatch.add(shapes.Line((0 * mm, 0 * mm), (width * mm, height * mm), style=style))
        self.hatch.add(shapes.Line((-1 * mm, (height - 1) * mm), (1 * mm, (height + 1) * mm), style=style))
        self.hatch.add(shapes.Line(((width - 1) * mm, -1 * mm), ((width + 1) * mm, 1 * mm), style=style))
        return self.hatch

    def add_filling(self, color):
        """
        Add solid filling of frame with specified color.
        **Replaces all previously added hatchings of fillings.**
        """
        if hasattr(self, 'hatch'):
            del self.hatch
        self.filling = color


class Frame(object):

    """
    Frame representation class. 
    """

    def __init__(self):
        self._plines = []

    def add_rect(self, x=0, y=0, width=1, height=1):
        """ Add rectangle to the frame and return it """
        rect = Rect(x, y, width, height)
        self._plines.append(rect)
        return rect

    def add_rect_frame(self, x=0, y=0, width=1, height=1, wall_width=1):
        rect_frame = RectFrame(x, y, width, height, wall_width)
        self._plines.append(rect_frame)
        return rect_frame

    def _draw(self):
        return self._plines
