#!/usr/bin/env python

import math
import sys
import time
import threading
from msvcrt import getch, kbhit

from PIL import Image
import os
import cv2

import colorama

import subprocess as sp

import re


def sorted_alphanumeric(data):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(data, key=alphanum_key)


# density =  " .:-=+*#%@$"
density = "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'. "
density = density[::-1]
count = len(density) - 1

frames = cv2.VideoCapture(sys.argv[1])


def extract_frame():
    ret, frame = frames.read()

    if ret:
        frame_pil = Image.fromarray(frame)
        return convert_frame(frame_pil)


terminalInfo = os.get_terminal_size()
maxsize = (terminalInfo[0], terminalInfo[1])


def convert_frame(frame):
    img = frame
    img.thumbnail(maxsize)
    w, h = img.size
    ascii_image = []

    for i in range(h):
        row = ""
        for j in range(w):
            # getting the RGB pixel value that we are at
            r, g, b = img.getpixel((j, i))

            # Apply formula of grayscale, just shows how dark the pixel should be, from 0 to 255:
            grayscale = (0.299 * r + 0.587 * g + 0.114 * b) / 255

            density_index = math.floor(grayscale * count)  # multiply it by final index of our density to find char

            try:
                # do the above mentioned to find the relative darkness of the next pixel
                # i realize this could be saved to make this a bit faster but i do not care and it is fast enough
                # to run smoothly at 60 fps and this is not the bottleneck, reading from file is

                n_r, n_g, n_b = img.getpixel((j + 1, i))  # get RGB values of next pixel
                n_grayscale = (0.299 * n_r + 0.587 * n_g + 0.114 * n_b) / 255  # get greyscale of next pixel

                in_between_grayscale = (n_grayscale + grayscale) / 2
                in_between_index = math.floor(in_between_grayscale * count)

                # add both calculated characters to row
                row += density[density_index]
                row += density[in_between_index]
            except:  # dont look at this bare except its not there and i did this the right way
                # on exception, we are on the edge and just duplicate pixel to maintain aspect ratio
                row += density[density_index] * 2

        ascii_image.append(row)
    return ascii_image


def resize():

    global terminalInfo
    global maxsize

    terminalInfo = os.get_terminal_size()
    maxsize = (terminalInfo[0], terminalInfo[1])


def main():
    counter = 10

    adjustment = 1.045  # magic number here don't mind it
    fps = frames.get(cv2.CAP_PROP_FPS) * adjustment
    delay_s = 1 / fps  # 1 frame / desired fps gives needed delay in seconds
    delay_ns = delay_s * 10 ** 9

    start_time = 0
    while 1:

        if kbhit():
            if getch() == b'\xe0':
                char = getch()
                if char == b'K':  # on left arrow press
                    pass  # eventually go back somehow ill have to store old frames or smth
                elif char == b'M':  # on left arrow press
                    frames_to_skip = math.floor(fps * 5)  # skips 5 seconds of video
                    for i in range(frames_to_skip):
                        frames.read()

        if counter <= 0:
            resize()
            counter = 10
        else:
            counter -= 1
        frame = extract_frame()
        if frame is None:
            break

        buffer = ""
        for row in frame:
            buffer += row + '\n'
        buffer

        # i was really excited when this worked
        # basically, start_time is taken right before we print out the buffer
        # then, print the buffer, begin the loop again and do the processing above
        # then, we loop here until current time - start_time is our delay in nanoseconds
        # i 'think' this is the only way to get consistent frame rate without touching asm
        while (time.time_ns() - start_time) < delay_ns:
            continue

        sys.stdout.buffer.write(bytes(buffer, 'utf-8'))
        start_time = time.time_ns()


if __name__ == '__main__':
    main()
