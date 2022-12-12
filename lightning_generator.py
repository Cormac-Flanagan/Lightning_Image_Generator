import math

import numpy as np
from PIL import Image, ImageDraw
from random import randint, random, uniform
import math
# Y by X
SIZE = (1000, 1500)

moist = np.random.rand(SIZE[0], SIZE[1])

for i in range(SIZE[0]):
    moist[i, :] = moist[i, :] * math.log10(i+1)

# canvas RGB
sky = np.zeros((SIZE[0], SIZE[1], 3))


def rescale(arr):
    arr_min = arr.min()
    arr_max = arr.max()
    return (arr - arr_min) / (arr_max - arr_min)


def check_around(matrix, col, row):
    poss = [(row, col - 1), (row, col + 1), (row - 1, col), (row + 1, col)]
    pos_v = [i for i in poss if ((0 <= i[0] < SIZE[0]) and (0 <= i[1] < SIZE[1]))]
    go = [(matrix[i], i) for i in pos_v]
    return max(go, key=lambda x: x[0])


def choose_point(cur_X, cur_Y, theta, length=1):
    point_x = length*math.cos(theta) + cur_X
    point_y = length*math.sin(theta) + cur_Y

    return point_y, point_x


def create_cloud(row, col, floor, canvas=sky, data=moist):
    # set targets
    while row < SIZE[0] - floor:
        b, (row, col) = check_around(data, col, row)

        canvas[row, col, 0] += 25  # R
        canvas[row, col, 1] += 30  # G
        canvas[row, col, 2] += 40  # B
        data[row, col] = (data[row, col])*0.2

    return canvas


def create_lightning(row, col, color=(255, 255, 255), canvas=sky):
    counter = 0
    length = randint(5, 25)
    theta = uniform(0.1*math.pi, 0.9*math.pi)
    # theta = math.pi/2
    while row < SIZE[0] - 10:
        counter += 1
        if counter%length == 0:
            theta = uniform(0.3*math.pi, 0.7*math.pi)
            length = randint(5, 25)
        row, col = choose_point(col, row, theta)
        rrow, rcol = round(row), round(col)

        if 0 <= rrow < SIZE[0] and 0 <= rcol < SIZE[1]:
            canvas[rrow, rcol, 0] = color[0]
            canvas[rrow, rcol, 1] = color[1]
            canvas[rrow, rcol, 2] = color[2]
        print(row, col)
    return canvas


# set ground
ground = 800
moist[SIZE[0]-ground, :] = SIZE[0]

for _ in range(20):
    start_X = randint(0, SIZE[1])
    sky = create_cloud(0, start_X, ground)

for _ in range(15):
    start_X = randint(0, SIZE[1])
    sky = create_lightning(100, start_X)


# sky = 255*rescale(sky)
# sky = np.flipud(sky)
img = Image.fromarray(sky.astype('uint8'), 'RGB')
img.save('Light.png')
# %%
