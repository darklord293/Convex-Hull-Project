from which_pyqt import PYQT_VER
if PYQT_VER == 'PYQT5':
    from PyQt5.QtCore import QLineF, QPointF, QObject
#elif PYQT_VER == 'PYQT4':
   # from PyQt4.QtCore import QLineF, QPointF, QObject
else:
    raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))


import time
import math

# Some global color constants that might be useful
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Global variable that controls the speed of the recursion automation, in seconds
#
PAUSE = 0.25

#
# This is the class you have to complete.
#


class ConvexHullSolver(QObject):

    # Class constructor
    def __init__(self):
        super().__init__()
        self.pause = False

# Some helper methods that make calls to the GUI, allowing us to send updates
# to be displayed.

    def showTangent(self, line, color):
        self.view.addLines(line, color)
        if self.pause:
            time.sleep(PAUSE)

    def eraseTangent(self, line):
        self.view.clearLines(line)

    def blinkTangent(self, line, color):
        self.showTangent(line, color)
        self.eraseTangent(line)

    def showHull(self, polygon, color):
        self.view.addLines(polygon, color)
        if self.pause:
            time.sleep(PAUSE)

    def eraseHull(self, polygon):
        self.view.clearLines(polygon)

    def showText(self, text):
        self.view.displayStatusText(text)

    # getting the point on clockwise order
    def getNextCW(self, points, point):
        index = points.index(point)
        if index == len(points)-1:
            return points[0]
        else:
            return points[index + 1]

    # getting the point on counterclockwise order
    def getNextCCW(self, points, point):
        index = points.index(point)
        if index == 0:
            return points[len(points) - 1]
        else:
            return points[index - 1]

    # computing slope
    def get_slope(self, point1, point2):
        return (point2[1] - point1[1]) / (point2[0] - point1[0])

    # computes the convex hull
    def get_convex_hull(self, points):
        if len(points) < 3:
            return points

        mid = len(points)//2

        # using divide and conquer to recursively compute convex hull
        left_hull = self.get_convex_hull(points[:mid])
        right_hull = self.get_convex_hull(points[mid:])

        right_most_left_hull = max(left_hull, key=lambda x: x[0])
        left_most_right_hull = min(right_hull, key=lambda x: x[0])

        left_decreasing = False
        right_decreasing = False

        # finding the upper tangent
        left_point = right_most_left_hull
        right_point = left_most_right_hull

        slope = self.get_slope(right_most_left_hull, left_most_right_hull)

        while left_decreasing == False or right_decreasing == False:
            left_decreasing = True
            right_decreasing = True

            while left_decreasing == True:
                left_point = self.getNextCCW(left_hull, left_point)
                next_slope = self.get_slope(left_point, right_point)

                if next_slope < slope:
                    slope = next_slope
                else:
                    left_point = self.getNextCW(left_hull, left_point)
                    left_decreasing = False
            if self.get_slope(left_point, self.getNextCW(right_hull, right_point)) <= slope:
                break

            while right_decreasing == True:
                right_point = self.getNextCW(right_hull, right_point)
                next_slope = self.get_slope(left_point, right_point)

                if next_slope > slope:
                    slope = next_slope
                else:
                    right_decreasing = False
                    right_point = self.getNextCCW(right_hull, right_point)
            if self.get_slope(self.getNextCCW(left_hull, left_point), right_point) >= slope:
                break

        top_left_tan_point = left_point
        top_right_tan_point = right_point

        # finding the lower tangent
        left_decreasing = False
        right_decreasing = False

        left_point = right_most_left_hull
        right_point = left_most_right_hull

        slope = self.get_slope(right_most_left_hull, left_most_right_hull)

        while (left_decreasing == False or right_decreasing == False):
            left_decreasing = True
            right_decreasing = True
            while left_decreasing == True:
                left_point = self.getNextCW(left_hull, left_point)
                next_slope = self.get_slope(left_point, right_point)
                if next_slope > slope:
                    slope = next_slope

                else:
                    left_point = self.getNextCCW(left_hull, left_point)
                    left_decreasing = False
            if self.get_slope(left_point, self.getNextCCW(right_hull, right_point)) >= slope:
                break

            while right_decreasing == True:
                right_point = self.getNextCCW(right_hull, right_point)
                next_slope = self.get_slope(left_point, right_point)

                if next_slope < slope:
                    slope = next_slope
                else:
                    right_decreasing = False
                    right_point = self.getNextCW(right_hull, right_point)
            if self.get_slope(self.getNextCW(left_hull, left_point), right_point) <= slope:
                break

        # lower tangent from left convex to right convex
        lower_left_tan_point = left_point
        lower_right_tan_point = right_point

        # final convex hull
        final_hull = []

        # starting with the top right tangent point
        right_hull_point = top_right_tan_point
        while right_hull_point != lower_right_tan_point:
            final_hull.append(right_hull_point)
            right_hull_point = self.getNextCW(right_hull, right_hull_point)
        # adding the lower right tangent point
        final_hull.append(lower_right_tan_point)

        # adding the lower left tangent point
        left_hull_point = lower_left_tan_point
        while left_hull_point != top_left_tan_point:
            final_hull.append(left_hull_point)
            left_hull_point = self.getNextCW(left_hull, left_hull_point)
        # adding the top left tangent point
        final_hull.append(top_left_tan_point)

        return final_hull

    def convert_points_to_qlinef_list(self, nodes):
        if len(nodes) < 2:
            raise ValueError(
                "At least two points are required to create QLineF instances.")

        # converting the list of tuples(x,y) back to QPointF instances
        points = [QPointF(x, y) for x, y in nodes]

        # list to store QLineF instances
        lines = []

        for i in range(len(points) - 1):
            line = QLineF(points[i], points[i + 1])
            lines.append(line)

        # adding first point at last to close the polygon
        lines.append(QLineF(points[-1], points[0]))

        return lines


# This is the method that gets called by the GUI and actually executes
# the finding of the hull


    def compute_hull(self, points, pause, view):
        self.pause = pause
        self.view = view
        assert (type(points) == list and type(points[0]) == QPointF)

        t1 = time.time()
        # sorting the points by the increasing x-value
        sorted_points = sorted(points, key=lambda point: point.x())

        # extracting the tuple(x,y) from QPointF instances
        points = [(point.x(), point.y()) for point in sorted_points]

        # TODO: SORT THE POINTS BY INCREASING X-VALUE
        t2 = time.time()

        t3 = time.time()
        # this is a dummy polygon of the first 3 unsorted points
        final_hull = self.get_convex_hull(points)

        polygon = self.convert_points_to_qlinef_list(final_hull)

        # TODO: REPLACE THE LINE ABOVE WITH A CALL TO YOUR DIVIDE-AND-CONQUER CONVEX HULL SOLVER
        t4 = time.time()

        # when passing lines to the display, pass a list of QLineF objects.  Each QLineF
        # object can be created with two QPointF objects corresponding to the endpoints
        self.showHull(polygon, RED)
        self.showText('Time Elapsed (Convex Hull): {:3.3f} sec'.format(t4-t3))





