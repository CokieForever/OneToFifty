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

"""main.py"""

__author__ = "Quoc-Nam Dessoulles"
__email__ = "cokie.forever@gmail.com"
__license__ = "MIT"

import os
import time
import webbrowser
from configparser import ConfigParser

import cv2
import numpy as np
import pyautogui

from onetofifty.util.util import clickOnAll, screenShot, cropImg, autocropImg, error, scaleInvariantTemplateMatch, \
    computeImgCorrelation, getBoundingBox


def main():
    print("Loading config")
    oConfigParser = ConfigParser()
    oConfigParser.read(os.path.join(os.path.dirname(__file__), "config.cfg"))

    print("Loading template data")
    (aTemplateImg1, dTemplateComponentImgs1), (aTemplateImg2, dTemplateComponentImgs2) = getTemplateData()

    print("Opening web page")
    webbrowser.open("http://zzzscore.com/1to50/en/")

    iDelay = max(0, int(oConfigParser["main"].get("loading_delay", "5")))
    print("Waiting %d seconds for the page to be loaded" % iDelay)
    time.sleep(iDelay)

    aInputImg, oRect, (fFactorX, fFactorY) = getInputImgFromScreen(aTemplateImg1)
    dCoordinates = getComponentsCoords(aInputImg, dTemplateComponentImgs1)
    print("Clicking on all numbers")
    clickOnAll((dCoordinates[i][0] / fFactorX + oRect.x, dCoordinates[i][1] / fFactorY + oRect.y)
               for i in range(1, 26))

    print("Moving mouse away")
    pyautogui.moveTo(10, 10)
    time.sleep(0.5)

    print("Extracting second grid from screen")
    aScreenImg = screenShot()
    aInputImg = cv2.resize(cropImg(aScreenImg, oRect), dsize=(0, 0), fx=fFactorX, fy=fFactorY)
    dCoordinates = getComponentsCoords(aInputImg, dTemplateComponentImgs2)
    print("Clicking on all numbers")
    clickOnAll((dCoordinates[i][0] / fFactorX + oRect.x, dCoordinates[i][1] / fFactorY + oRect.y)
               for i in range(26, 51))

    print("All done!")


def getTemplateData():
    def readAndNormalizeImg(sImgFileName):
        sImgPath = os.path.join(os.path.dirname(__file__), "res", sImgFileName)
        return cv2.copyMakeBorder(
            autocropImg(cv2.cvtColor(cv2.imread(sImgPath), cv2.COLOR_BGR2GRAY), iBgValue=255),
            15, 15, 15, 15, cv2.BORDER_CONSTANT, value=255)

    def readTemplateValues(sValuesFileName):
        sFilePath = os.path.join(os.path.dirname(__file__), "res", sValuesFileName)
        with open(sFilePath, "r") as oFile:
            return list(map(int, oFile.read().split()))

    def computeComponentDict(lComponentValues, aTemplateImg):
        iCount = len(lComponentValues)
        lComponentImgs = list(getSortedComponentImgs(aTemplateImg))
        if len(lComponentImgs) < iCount:
            error("Unable to analyze template image 1: found %d numbers, expected at least %d"
                  % (len(lComponentImgs), iCount))
        else:
            return dict(zip(lComponentValues, lComponentImgs[:iCount]))

    aTemplateImg1 = readAndNormalizeImg("template1.png")
    aTemplateImg2 = readAndNormalizeImg("template2.png")
    lComponentValues1 = readTemplateValues("template1.txt")
    lComponentValues2 = readTemplateValues("template2.txt")

    return (aTemplateImg1, computeComponentDict(lComponentValues1, aTemplateImg1)), \
           (aTemplateImg2, computeComponentDict(lComponentValues2, aTemplateImg2))


def getInputImgFromScreen(aTemplateImg):
    for _ in range(5):
        print("Searching for the grid on the screen")
        aScreenShot = screenShot()
        oRect = scaleInvariantTemplateMatch(aTemplateImg, aScreenShot)
        if oRect is not None:
            print("Grid found at %d;%d" % (oRect.x, oRect.y))
            aCroppedImg = cropImg(aScreenShot, oRect)
            fFactorX = aTemplateImg.shape[1] / float(aCroppedImg.shape[1])
            fFactorY = aTemplateImg.shape[0] / float(aCroppedImg.shape[0])
            return cv2.resize(aCroppedImg, dsize=(0, 0), fx=fFactorX, fy=fFactorY), oRect, (fFactorX, fFactorY)
        print("Grid not found, scrolling down")
        pyautogui.press("down", presses=3, interval=0.2)
        time.sleep(0.5)
    error("Unable to locate the grid on your screen")


def getComponentsCoords(aImg, dTemplateComponentImgs):
    print("Analyzing grid and extracting numbers")
    dTable = {}
    for oRect in getComponentRects(aImg):
        dTable[oRect] = {}
        aComponentImg = cropImg(aImg, oRect)
        for iValue, aTemplateComponentImg in dTemplateComponentImgs.items():
            dTable[oRect][iValue] = computeImgCorrelation(aTemplateComponentImg, aComponentImg)

    dCoordinates = {}
    while dTable and next(iter(dTable.values())):
        lBestTuple = None
        fBestCorr = -2
        for oRect, d in dTable.items():
            iValue, fCorr = max(d.items(), key=lambda l: l[1])
            if fCorr > fBestCorr:
                fBestCorr = fCorr
                lBestTuple = oRect, iValue
                if fCorr >= 1:
                    break
        dCoordinates[lBestTuple[1]] = lBestTuple[0].lCenter
        del dTable[lBestTuple[0]]
        for d in dTable.values():
            del d[lBestTuple[1]]

    lDiff = set(dTemplateComponentImgs).difference(set(dCoordinates))
    if lDiff:
        error("Following numbers could not be found: %s" % "; ".join(map(str, lDiff)))
    return dCoordinates


def getSortedComponentImgs(aImg):
    for oRect in sortRects(getComponentRects(aImg)):
        yield cropImg(aImg, oRect)


def getComponentRects(aImg):
    _, aBinaryImg = cv2.threshold(aImg, 128, 255, cv2.THRESH_BINARY_INV)
    aBinaryImg = cv2.morphologyEx(aBinaryImg, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15)))
    _, aComponents = cv2.connectedComponents(aBinaryImg)
    iComponentsCount = np.amax(aComponents)
    for iComponent in range(1, iComponentsCount + 1):
        yield getBoundingBox(aComponents == iComponent)


def sortRects(lRects):
    lRects = list(lRects)
    lOrigin = (0, 0)

    def getClosestRectToOrigin(lRects):
        return min(lRects, key=lambda r: (r.x - lOrigin[0]) ** 2 + (r.y - lOrigin[1]) ** 2)

    oRect = None
    while lRects:
        if oRect is not None:
            lRectsToTheRight = list(filter(lambda r: r.x >= oRect.x + oRect.w, lRects))
            if lRectsToTheRight:
                oRect = getClosestRectToOrigin(lRectsToTheRight)
            else:
                oRect = None
                lOrigin = (0, 0)
        if oRect is None:
            oRect = getClosestRectToOrigin(lRects)

        yield oRect
        lRects.remove(oRect)
        lOrigin = oRect.lCenter


def test():
    pyautogui.press("down")


if __name__ == "__main__":
    main()
