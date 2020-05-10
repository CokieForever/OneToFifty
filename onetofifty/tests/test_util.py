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

"""test_util.py"""

__author__ = "Quoc-Nam Dessoulles"
__email__ = "cokie.forever@gmail.com"
__license__ = "MIT"

import os

import cv2
import numpy as np

from onetofifty.util import util
from onetofifty.util.util import Rect


def openResImage(sImgName):
    sImgPath = os.path.join(os.path.dirname(__file__), "res", sImgName)
    return cv2.cvtColor(cv2.imread(sImgPath), cv2.COLOR_BGR2GRAY)


def test_getBoundingBox():
    oRect = util.getBoundingBox(openResImage("black_rectangle.png") == 0)
    assert oRect.x == 55
    assert oRect.y == 63
    assert oRect.w == 66
    assert oRect.h == 64


def test_cropImg():
    aCroppedImg = util.cropImg(openResImage("black_rectangle.png"), Rect(10, 10, 50, 100))
    assert aCroppedImg.shape == (100, 50)


def test_autocropImg():
    aCroppedImg = util.autocropImg(openResImage("black_rectangle.png"), iBgValue=255)
    assert aCroppedImg.shape == (64, 66)
    assert np.all(aCroppedImg == 0)


def test_computeImgCorrelation():
    aImg1 = openResImage("scene.png")
    aImg2 = cv2.resize(aImg1, dsize=(0, 0), fx=1.25, fy=0.75, interpolation=cv2.INTER_LINEAR)
    assert util.computeImgCorrelation(aImg1, aImg2) >= 0.99


def test_scaleInvariantTemplateMatch():
    aSceneImg = openResImage("scene.png")
    aTemplateImg = openResImage("input.png")

    oRect = util.scaleInvariantTemplateMatch(aTemplateImg, aSceneImg)
    assert oRect is not None
    assert oRect.x == 708
    assert oRect.y == 399
    assert oRect.w == 482
    assert oRect.h == 489

    oRect = util.scaleInvariantTemplateMatch(aTemplateImg, aSceneImg, fMinCorr=0.99)
    assert oRect is None
