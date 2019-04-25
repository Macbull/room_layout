import cv2
import numpy as np
from scipy.stats import multivariate_normal
from scipy.ndimage.filters import gaussian_filter


def gen_edge_map(e, image_size, width, sigma):
    binary_map = func_map[e['type']](e, image_size=image_size, width=width)
    return gaussian_filter(binary_map, sigma)


def draw_line(img, pt1, pt2, width=1, color=(255, 255, 255)):

    def to_point(pt):
        return tuple(pt.astype(int))

    cv2.line(img, to_point(pt1), to_point(pt2), color, width)


def _edge_map(e, point_pairs, **kwargs):
    image_size = kwargs.pop('image_size')
    scale = (e['resolution'][1] / image_size[1],
             e['resolution'][0] / image_size[0])
    canvas = np.zeros(image_size)
    for pp in point_pairs:
        pt1 = e['points'][pp[0] - 1] / scale
        pt2 = e['points'][pp[1] - 1] / scale
        draw_line(canvas, pt1, pt2, **kwargs)
    return canvas


def gen_corner_map(e, target_size):
    # create a grid of (x,y) coordinates at which to evaluate the kernels
    xlim = (0, 20)
    ylim = (0, 20)
    xres, yres = target_size

    x = np.linspace(xlim[0], xlim[1], xres)
    y = np.linspace(ylim[0], ylim[1], yres)
    xx, yy = np.meshgrid(x, y)
    xxyy = np.c_[xx.ravel(), yy.ravel()]

    first = True
    origin_size = e['resolution']
    for p in e['points']:
        m0 = (p[0] / origin_size[1]) * 20
        m1 = (p[1] / origin_size[0]) * 20
        k = multivariate_normal(mean=(m0, m1), cov=np.eye(2))
        if first:
            zz = k.pdf(xxyy)
            first = False
        else:
            zz += k.pdf(xxyy)

    # reshape and plot image
    img = zz.reshape((xres, yres))
    return img


def type0(e, **kwargs):
    point_pairs = [
        [1, 2], [3, 4], [5, 6], [7, 8],
        [1, 3], [3, 5], [5, 7], [7, 1]
    ]
    return _edge_map(e, point_pairs, **kwargs)


def type1(e, **kwargs):
    point_pairs = [[1, 2], [1, 3], [1, 4], [4, 5], [4, 6]]
    return _edge_map(e, point_pairs, **kwargs)


def type2(e, **kwargs):
    point_pairs = [[1, 2], [1, 3], [1, 4], [4, 5], [4, 6]]
    return _edge_map(e, point_pairs, **kwargs)


def type3(e, **kwargs):
    point_pairs = [[1, 2], [1, 3], [1, 4]]
    return _edge_map(e, point_pairs, **kwargs)


def type4(e, **kwargs):
    point_pairs = [[1, 2], [1, 3], [1, 4]]
    return _edge_map(e, point_pairs, **kwargs)


def type5(e, **kwargs):
    point_pairs = [[1, 2], [1, 3], [1, 4], [4, 5], [4, 6]]
    return _edge_map(e, point_pairs, **kwargs)


def type6(e, **kwargs):
    point_pairs = [[1, 2], [3, 4]]
    return _edge_map(e, point_pairs, **kwargs)


def type7(e, **kwargs):
    point_pairs = [[1, 2], [3, 4]]
    return _edge_map(e, point_pairs, **kwargs)


def type8(e, **kwargs):
    point_pairs = [[1, 2]]
    return _edge_map(e, point_pairs, **kwargs)


def type9(e, **kwargs):
    point_pairs = [[1, 2]]
    return _edge_map(e, point_pairs, **kwargs)


def type10(e, **kwargs):
    point_pairs = [[1, 2]]
    return _edge_map(e, point_pairs, **kwargs)


func_map = {
    0: type0,
    1: type1,
    2: type2,
    3: type3,
    4: type4,
    5: type5,
    6: type6,
    7: type7,
    8: type8,
    9: type9,
    10: type10,
}
