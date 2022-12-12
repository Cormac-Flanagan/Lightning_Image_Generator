import sys
import numpy as np
from PIL import Image
from random import randint, random, uniform
import math
from tqdm import tqdm
import multiprocessing

# Y by X
SIZE = (1000, 1500)

moist = np.random.rand(SIZE[0], SIZE[1])

for i in range(SIZE[0]):
    moist[i, :] = moist[i, :] * math.log10(i+1)

# canvas RGB
sky = np.zeros((SIZE[0], SIZE[1], 3))

branches = []


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


def create_lightning(row, col, color=(255, 255, 255), canvas=sky, floor=SIZE[0]):
    counter = 0
    length = randint(5, 25)
    theta = uniform(0.1*math.pi, 0.9*math.pi)
    # theta = math.pi/2
    while row < SIZE[0] - 10:
        counter += 1
        if counter%length == 0:
            theta = uniform(0*math.pi, 1*math.pi)
            length = randint(5, 25)
            if random() <= 0.05:
                branches.append((row, col))

        row, col = choose_point(col, row, theta)
        rrow, rcol = round(row), round(col)

        if 0 <= rrow < floor and 0 <= rcol < SIZE[1]:
            canvas[rrow, rcol, 0] = color[0]
            canvas[rrow, rcol, 1] = color[1]
            canvas[rrow, rcol, 2] = color[2]
        # print(row, col)
    return canvas


def fade_effect(matrix_info):
    value, pos_y, pos_x = matrix_info
    fade = np.fromfunction(lambda i, j, z: 1/(((i-pos_y+0.001)**2)+((j-pos_x+0.001)**2)), (SIZE[0], SIZE[1], 3), dtype='uint8')
    return value*fade


if __name__ == '__main__':
    lightning_F = np.zeros((SIZE[0], SIZE[1], 3))
    lightning = np.zeros((SIZE[0], SIZE[1], 3))
    # set ground
    ground = 800
    moist[SIZE[0] - ground, :] = SIZE[0]
    print("reached")
    for _ in tqdm(range(20), desc="Creating Clouds"):
        start_X = randint(0, SIZE[1])
        sky = create_cloud(0, start_X, ground)

    for _ in tqdm(range(5), desc="Creating Lightning Main"):
        start_X = randint(0, SIZE[1])
        lightning = create_lightning(100, start_X)

    for i in tqdm(range(len(branches)), desc="Creating Lightning Branches"):
        row, col = branches[i]
        lightning = create_lightning(row, col, floor=row+randint(10, 200))

    pbar = tqdm(total=np.count_nonzero(lightning >= 1)/3, desc="Getting Points for Processing")
    to_process = []
    for (row, col, z), val in np.ndenumerate(lightning):
        if val != 0 and z == 0:
            to_process.append((val, row, col))
            pbar.update(1)
    pbar.close()
    with multiprocessing.Pool(int(sys.argv[1])) as p:
        lightning_F = sum(tqdm(p.imap(fade_effect, to_process), total=len(to_process), desc="Processing Points"))

    final = sky + lightning_F

    final = 255*rescale(final)
    img = Image.fromarray(final.astype('uint8'), 'RGB')
    img.save('Light.png')
