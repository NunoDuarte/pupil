"""
(*)~---------------------------------------------------------------------------
Pupil - eye tracking platform
Copyright (C) 2012-2022 Pupil Labs

Distributed under the terms of the GNU
Lesser General Public License (LGPL v3.0).
See COPYING and COPYING.LESSER for license details.
---------------------------------------------------------------------------~(*)
"""

import cv2
from plugin import Plugin
import numpy as np

from pyglui import ui
from methods import denormalize
import logging

logger = logging.getLogger(__name__)


class Vis_Light_Points(Plugin):
    """docstring
    show gaze dots at light dots on numpy.

    """

    uniqueness = "not_unique"
    icon_chr = chr(0xE3A5)
    icon_font = "pupil_icons"

    def __init__(self, g_pool, falloff=20):
        super().__init__(g_pool)
        self.order = 0.8
        self.menu = None

        self.falloff = falloff

    def recent_events(self, events):
        frame = events.get("frame")
        if not frame:
            return
        falloff = self.falloff

        img = frame.img
        pts = [
            denormalize(pt["norm_pos"], frame.img.shape[:-1][::-1], flip_y=True)
            for pt in events.get("gaze", [])
            if pt["confidence"] >= self.g_pool.min_data_confidence
        ]

        overlay = np.ones(img.shape[:-1], dtype=img.dtype)

        # draw recent gaze postions as black dots on an overlay image.
        for gaze_point in pts:
            try:
                overlay[int(gaze_point[1]), int(gaze_point[0])] = 0
            except Exception:
                pass

        out = cv2.distanceTransform(overlay, cv2.DIST_L2, 5)

        # fix for opencv binding inconsitency
        if type(out) == tuple:
            out = out[0]

        overlay = 1 / (out / falloff + 1)

        img[:] = np.multiply(
            img, cv2.cvtColor(overlay, cv2.COLOR_GRAY2RGB), casting="unsafe"
        )

    def init_ui(self):
        self.add_menu()
        self.menu.label = "Light Points"
        self.menu.append(ui.Slider("falloff", self, min=1, step=1, max=1000))

    def deinit_ui(self):
        self.remove_menu()

    def get_init_dict(self):
        return {"falloff": self.falloff}
