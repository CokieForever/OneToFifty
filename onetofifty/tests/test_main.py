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

"""test_main.py"""

__author__ = "Quoc-Nam Dessoulles"
__email__ = "cokie.forever@gmail.com"
__license__ = "MIT"

from unittest.mock import patch, call

import pytest

from onetofifty import main
from onetofifty.tests.test_util import openResImage
from onetofifty.util.util import Rect


def test_getComponentRects():
    aImg = openResImage("input.png")
    lRects = list(main.getComponentRects(aImg))
    assert len(lRects) == 25
    for oRect in lRects:
        assert oRect.w == oRect.h == 70
    assert lRects[0].x == 10
    assert lRects[0].y == 11
    assert lRects[10].x == 10
    assert lRects[10].y == 159
    assert lRects[20].x == 10
    assert lRects[20].y == 307


@patch("onetofifty.main.screenShot")
def test_getInputImg(oScreenShotMock):
    oScreenShotMock.return_value = openResImage("scene.png")
    aTemplateImg = openResImage("input.png")
    aImg, oRect, (fFactorX, fFactorY) = main.getInputImgFromScreen(aTemplateImg)
    assert oRect.x == 708
    assert oRect.y == 399
    assert oRect.w == 482
    assert oRect.h == 489
    assert round(fFactorX * 1000) == 801
    assert round(fFactorY * 1000) == 800
    assert aImg.shape == aTemplateImg.shape


@patch("pyautogui.press")
@patch("onetofifty.main.screenShot")
def test_getInputImg_whenScrolled(oScreenShotMock, oPressMock):
    oScreenShotMock.return_value = openResImage("scene_cropped.png")
    aTemplateImg = openResImage("input.png")
    with pytest.raises(SystemExit) as oExc:
        main.getInputImgFromScreen(aTemplateImg)
    oPressMock.assert_has_calls([call("down", presses=3, interval=0.2)]*5)
    assert oExc.value.code == 1


def test_getTemplateData():
    (aTemplateImg1, dTemplateComponentImgs1), (aTemplateImg2, dTemplateComponentImgs2) = main.getTemplateData()
    assert aTemplateImg1.size > 0
    assert aTemplateImg2.size > 0
    assert set(dTemplateComponentImgs1.keys()) == set(range(1, 26))
    assert set(dTemplateComponentImgs2.keys()) == set(range(26, 51))


def test_getComponentCoords():
    (_, dTemplateComponentImgs), _ = main.getTemplateData()
    dCoords = main.getComponentsCoords(openResImage("input.png"), dTemplateComponentImgs)
    assert set(dCoords.keys()) == set(range(1, 26))
    assert dCoords[1] == (193.0, 342.0)
    assert dCoords[10] == (341.0, 120.0)
    assert dCoords[20] == (267.0, 46.0)


def test_sortRects():
    lRects = [
        Rect(0, 10, 10, 10),
        Rect(0, 0, 10, 10),
        Rect(0, 20, 10, 10),
        Rect(10, 10, 10, 10)
    ]
    lSortedRects = list(main.sortRects(lRects))
    assert lSortedRects == [lRects[1], lRects[3], lRects[0], lRects[2]]
