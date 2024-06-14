# SPDX-FileCopyrightText: Copyright (c) 2021 GaryZ
#
# SPDX-License-Identifier: MIT
"""
`displayio_gauge`
================================================================================

Displayio widget that creates circular gauges that can have their fill value set dynamically.


* Author(s): GaryZ

Implementation Notes
--------------------

**Hardware:**

Any display that supports displayio.

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

"""

# imports
import math
import displayio
import bitmaptools

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/circuitpython/CircuitPython_Org_DisplayIO_Gauge.git"


class Gauge(displayio.TileGrid):
    """A circular gauge that can be filled to a certain value. The origin is set
    using ``x`` and ``y`` coordinates relative to the center of the gauge.

    :param int x: pixel position relative to center
    :param int y: pixel position relative to center
    :param int radius: radius of outer circle of the gauge
    :param int thickness: thickness of the gauge in pixels defaults to 10 pixels
    :param int level: fill level of the gauge (0-100) defaults to 0
    :param int outline_color: the color for the outline of the gauge defaults to 0xFFFFFF
    :param int foreground_color: the color for filled in portion of the gauge 0x00FF00
    :param int background_color: the color for the unfilled portion of the gauge 0x000000

    **Simple example of a gauge with level set by for loop**

    See file: ``examples/displayio_gauge_simpletest.py``

    """

    # pylint: disable=invalid-name, too-many-arguments

    # The dial is a subclass of TileGrid.

    def __init__(
        self,
        x,
        y,
        radius,
        thickness=10,
        level=0,
        outline_color=0xFFFFFF,
        foreground_color=0x00FF00,
        background_color=0x00000,
    ):
        self.xcenter = x
        self.ycenter = y
        self.radius = radius
        self._width = thickness
        if thickness < 2:
            self._width = 2
        self._level = level
        tileGridWidth = 2 * self.radius + 1
        tileGridHeight = math.ceil(0.71 * self.radius) + self.radius + 1
        self._bitmap = displayio.Bitmap(tileGridWidth, tileGridHeight, 3)

        self._palette = displayio.Palette(3)
        self._palette[0] = background_color
        self._palette[1] = outline_color
        self._palette[2] = foreground_color
        x_offset = self.xcenter - self.radius + 1
        y_offset = self.ycenter - self.radius + 1

        super().__init__(
            self._bitmap, pixel_shader=self._palette, x=x_offset, y=y_offset
        )

        self._draw_gauge()

    def _draw_gauge(self):
        # internal helper function to draw the entire gauge
        # including the outline

        x = 0
        y = self.radius
        d = 3 - 2 * self.radius

        # Bresenham's circle algorithm drawing octants 1 - 6, skipping 0 & 7
        # Outer arc
        while x <= y:
            self._bitmap[-x + self.radius, -y + self.radius] = 1
            self._bitmap[x + self.radius, -y + self.radius] = 1
            self._bitmap[y + self.radius, x + self.radius] = 1
            self._bitmap[-y + self.radius, x + self.radius] = 1
            self._bitmap[-y + self.radius, -x + self.radius] = 1
            self._bitmap[y + self.radius, -x + self.radius] = 1

            if d <= 0:
                d = d + (4 * x) + 6
            else:
                d = d + 4 * (x - y) + 10
                y = y - 1
            x = x + 1
        self.yend = self.xend = x - 1

        # Inner Arc
        x = 0
        y = self.radius - self._width + 1
        d = 3 - 2 * y

        while x <= y:
            self._bitmap[-x + self.radius, -y + self.radius] = 1
            self._bitmap[x + self.radius, -y + self.radius] = 1
            self._bitmap[y + self.radius, x + self.radius] = 1
            self._bitmap[-y + self.radius, x + self.radius] = 1
            self._bitmap[-y + self.radius, -x + self.radius] = 1
            self._bitmap[y + self.radius, -x + self.radius] = 1

            if d <= 0:
                d = d + (4 * x) + 6
            else:
                d = d + 4 * (x - y) + 10
                y = y - 1
            x = x + 1
        self.yend2 = x
        self.xend2 = x

        # Connect inner and outer arc at endpoints
        bitmaptools.draw_line(
            self._bitmap,
            self.radius + self.xend,
            self.radius + self.yend,
            self.radius + self.xend2,
            self.radius + self.yend2,
            1,
        )
        bitmaptools.draw_line(
            self._bitmap,
            self.radius - self.xend,
            self.radius + self.yend,
            self.radius - self.xend2,
            self.radius + self.yend2,
            1,
        )
        self._draw_level()

    def _draw_level(self):
        # internal helper function to draw the filled portion of the gauge

        if self.level <= 0:  # Just draw the gauge (which is done now) and leave
            return

        #   Color in up to the level

        #   Find fill level end line
        prog = 315 - (
            self.level * 270 / 100
        )  # what percent of gauge in degrees to fill in
        xs = self.radius + int(
            round(math.sin(math.radians(prog)) * (self.radius - 1), 0)
        )
        ys = self.radius + int(
            round(math.cos(math.radians(prog)) * (self.radius - 1), 0)
        )
        xe = self.radius + int(
            round(math.sin(math.radians(prog)) * (self.radius - self._width + 2), 0)
        )
        ye = self.radius + int(
            round(math.cos(math.radians(prog)) * (self.radius - self._width + 2), 0)
        )

        # Draw end line for level value
        if self.level != 100:  # @ 100%, no need to draw end line
            bitmaptools.draw_line(self._bitmap, xs, ys, xe, ye, 2)
        # Find a point just before the level line as a start point for the  fill

        xp = self.radius + int(
            round(
                math.sin(math.radians(prog + 1)) * (self.radius - int(self._width / 2)),
                0,
            )
        )
        yp = self.radius + int(
            round(
                math.cos(math.radians(prog + 1)) * (self.radius - int(self._width / 2)),
                0,
            )
        )
        i = 1
        while self._bitmap[xp, yp] != 0 and i < 4:  # Search a little for a blank pixel
            i += 1
            xp = self.radius + int(
                round(
                    math.sin(math.radians(prog + i))
                    * (self.radius - int(self._width / 2)),
                    0,
                )
            )
            yp = self.radius + int(
                round(
                    math.cos(math.radians(prog + i))
                    * (self.radius - int(self._width / 2)),
                    0,
                )
            )

        bitmaptools.boundary_fill(self._bitmap, xp, yp, 2, 0)

    def _draw_regress(self):
        # internal helper function to draw the unfilled portion of the gauge.
        # used when user sets a new level that is lower than current level.

        #   Find fill level end line
        prog = 315 - (
            self.level * 270 / 100
        )  # what percent of gauge in degrees to fill in
        xs = self.radius + int(
            round(math.sin(math.radians(prog)) * (self.radius - 1), 0)
        )
        ys = self.radius + int(
            round(math.cos(math.radians(prog)) * (self.radius - 1), 0)
        )
        xe = self.radius + int(
            round(math.sin(math.radians(prog)) * (self.radius - self._width + 2), 0)
        )
        ye = self.radius + int(
            round(math.cos(math.radians(prog)) * (self.radius - self._width + 2), 0)
        )

        # Draw end line for level value
        if self.level not in (100, 0):  # @ 100%, no need to draw end line
            bitmaptools.draw_line(self._bitmap, xs, ys, xe, ye, 0)
        if self.level == 24:
            print(xs, ys, xe, ye)

        # Find a point just after the level line as a start point to blank out to new level line

        xp = self.radius + int(
            round(
                math.sin(math.radians(prog - 1)) * (self.radius - int(self._width / 2)),
                0,
            )
        )
        yp = self.radius + int(
            round(
                math.cos(math.radians(prog - 1)) * (self.radius - int(self._width / 2)),
                0,
            )
        )
        i = 1
        while self._bitmap[xp, yp] != 2 and i < 4:  # Search a little for a blank pixel
            i += 1
            xp = self.radius + int(
                round(
                    math.sin(math.radians(prog - i))
                    * (self.radius - int(self._width / 2)),
                    0,
                )
            )
            yp = self.radius + int(
                round(
                    math.cos(math.radians(prog - i))
                    * (self.radius - int(self._width / 2)),
                    0,
                )
            )

        bitmaptools.boundary_fill(self._bitmap, xp, yp, 0, 2)

    @property
    def level(self):
        """The gauge's current level."""
        return self._level

    @level.setter
    def level(self, new_level):
        """Set a new level into the gauge."""
        if new_level >= self._level:
            self._level = new_level
            self._draw_level()
        else:
            self._level = new_level
            self._draw_regress()

    @property
    def foreground_color(self):
        """The gauge's foreground color that will be used to fill up to the level that is set."""
        return self._palette[2]

    @foreground_color.setter
    def foreground_color(self, new_foreground_color):
        """Set a new foreground color that will be used to fill up to the level that is set."""
        self._palette[2] = new_foreground_color

    @property
    def background_color(self):
        """The gauge's background color that will be used in the unfilled portion of the gauge."""
        return self._palette[0]

    @background_color.setter
    def background_color(self, new_background_color):
        """Set a new background color that will be used in the unfilled portion of the gauge."""
        self._palette[0] = new_background_color

    @property
    def outline_color(self):
        """The gauge's background color that will be used to draw the edge lines of the gauge."""
        return self._palette[1]

    @outline_color.setter
    def outline_color(self, new_outline_color):
        """Set a new outline color that will be used to draw the edge lines of the gauge."""
        self._palette[0] = new_outline_color
