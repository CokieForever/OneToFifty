![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)
![](https://img.shields.io/github/license/CokieForever/OneToFifty)
![](https://img.shields.io/github/workflow/status/CokieForever/OneToFifty/Build)

# 1 to 50

A fun project to automatically play the [1 to 50](http://zzzscore.com/1to50/en/) game.

## Description

This is a little script which will play the [1 to 50](http://zzzscore.com/1to50/en/) game for you. The goal of the
game is to click in the right order, as fast as possible, on randomly arranged boxes tagged from 1 to 50. After being
challenged by a friend, but knowing how bad I usually perform at this kind of tasks, I opted for a more pragmatic
approach 😄

## Installation

To run the script, you first need to install a few dependencies: `pip install -r requirements.txt`

## Usage

Then simply run: `python -m onetofifty.main`

The browser should open and the program will start running. The first phase is the analysis, depending on your
computer, it can take about 10 seconds before anything happens. Once the analysis is done, the script will start
moving your mouse and click on the displayed grid for you. Once all the numbers are clicked, the script exits.

Avoid doing anything with your computer during the whole execution, as the script relies on the content displayed on
the screen to work properly. You can use `Ctrl+C` to interrupt the script and regain control of your mouse at any time.

If your browser is too slow and the script starts doing crazy stuff before the page is fully loaded, you can increase
the delay in the `config.cfg` file. Alternatively, you make sure your browser is already open before launching the
script, that usually helps.

If your screen is too small and the grid is not fully displayed when loading the page, the script will attempt to
scroll down a few times. If the scrolling does not work, or if you find it too slow, you can also help it by scrolling
manually.

## Development status

This is a simple script made for fun. It has no real purpose and is not guaranteed to work on all devices, depending
on the screen and browsers settings.
