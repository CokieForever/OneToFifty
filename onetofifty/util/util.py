#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2020 Quoc-Nam Dessoulles
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""util.py"""

__author__ = "Quoc-Nam Dessoulles"
__email__ = "cokie.forever@gmail.com"
__license__ = "MIT"

import sys

import cv2
import numpy as np
import pyautogui


class Rect:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    @property
    def lCenter(self):
        return self.x + self.w / 2, self.y + self.h / 2


def getBoundingBox(aImg):
    lRowsIdx = np.where(np.any(aImg, axis=1))[0]
    lColsIdx = np.where(np.any(aImg, axis=0))[0]
    return Rect(lColsIdx[0], lRowsIdx[0], lColsIdx[-1] - lColsIdx[0] + 1, lRowsIdx[-1] - lRowsIdx[0] + 1)


def cropImg(aImg, oRect):
    return aImg[oRect.y:oRect.y + oRect.h, oRect.x:oRect.x + oRect.w]


def autocropImg(aImg, iBgValue=0):
    return cropImg(aImg, getBoundingBox(aImg != iBgValue))


def scaleInvariantTemplateMatch(aImg, aSceneImg, fMinCorr=0.95):
    # TODO Test with SURF when Features2D is available
    #  See https://github.com/opencv/opencv/pull/17119
    #  See https://docs.opencv.org/4.3.0/d7/dff/tutorial_feature_homography.html
    fBestCorr = fMinCorr
    oRect = None
    for x in range(-10, 11):
        fFactor = 1 + 0.05 * x
        aResizedImg = cv2.resize(aImg, dsize=(0, 0), fx=fFactor, fy=fFactor, interpolation=cv2.INTER_LINEAR)
        _, fCorr, _, (iPosX, iPosY) = cv2.minMaxLoc(cv2.matchTemplate(aSceneImg, aResizedImg, cv2.TM_CCORR_NORMED))
        if fCorr >= fBestCorr:
            oRect = Rect(iPosX, iPosY, aResizedImg.shape[1], aResizedImg.shape[0])
            fBestCorr = fCorr
            if fCorr >= 1:
                break
    return oRect


def computeImgCorrelation(aImg1, aImg2):
    iWidth = min(aImg1.shape[1], aImg2.shape[1])
    iHeight = min(aImg1.shape[0], aImg2.shape[0])
    aImg1 = cv2.resize(aImg1, (iWidth, iHeight), interpolation=cv2.INTER_LINEAR)
    aImg2 = cv2.resize(aImg2, (iWidth, iHeight), interpolation=cv2.INTER_LINEAR)
    return cv2.matchTemplate(aImg1, aImg2, cv2.TM_CCORR_NORMED)[0, 0]


def screenShot():
    return cv2.cvtColor(np.array(pyautogui.screenshot()), cv2.COLOR_RGB2GRAY)


def clickOnAll(lCoords):
    for lCoord in lCoords:
        pyautogui.moveTo(*lCoord)
        pyautogui.click()


def error(sMessage):
    print("ERROR: %s" % sMessage)
    sys.exit(1)
