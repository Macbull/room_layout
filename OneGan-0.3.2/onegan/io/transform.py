# Copyright (c) 2017 Salas Lin (leVirve)
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import random

import torch
import numpy as np
import torchvision.transforms as T
import torchvision.transforms.functional as F
from PIL import Image


class SegmentationPair():

    def __init__(self,
                 target_size=None,
                 final_transform=False,
                 random_flip=False, random_crop=False, color_jiiter=False):
        self.target_size = target_size
        self.final_transform = final_transform
        self.random_flip = random_flip
        self.random_crop = random_crop
        self.color_jiiter = color_jiiter

    def __call__(self, image, segmentation, random=False) -> tuple:
        image = image.convert('RGB')
        segment = segmentation.convert('L')

        image, segment = self.tf_random_flip(image, segment)
        image, segment = self.tf_random_crop(image, segment)

        image = F.resize(image, self.target_size, interpolation=Image.BILINEAR)
        segment = F.resize(segment, self.target_size, interpolation=Image.NEAREST)

        return self._transform(image, segment)

    def _transform(self, image, segmentation) -> tuple:
        if self.final_transform:
            image = T.Normalize(mean=[.5, .5, .5], std=[.5, .5, .5])(F.to_tensor(image))
            segmentation = torch.from_numpy(np.array(segmentation) - 1).long()  # make 0 into 255 as ignore index
        return image, segmentation

    def tf_random_flip(self, image, segment):
        if self.random_flip and random.random() >= 0.5:
            image = F.hflip(image)
            segment = F.hflip(segment)
        return image, segment

    def tf_random_crop(self, image, segment):
        if self.random_crop:
            i, j, h, w = F.RandomResizedCrop.get_params(image)
            image = F.crop(image, i, j, h, w)
            segment = F.crop(segment, i, j, h, w)
        return image, segment


class TransformPipeline:

    def __init__(self, target_size=None, color_jiiter=None):
        self.target_size = target_size
        self.color_jitter = color_jiiter or \
            T.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2)
        self.totensor_normalize = T.Compose([
            T.ToTensor(),
            T.Normalize(mean=[.5, .5, .5], std=[.5, .5, .5]),
        ])

    def new_random_state(self):
        self.random = random.random() > 0.5
        self.random_angle = np.random.uniform(-5, 5)

    def _transform(self, x, transform_fn):
        if not self.random:
            return x
        return transform_fn(x)

    def load_image(self, path):
        return Image.open(path)

    def resize(self, x, mode='bilinear'):
        interpolation = {
            'nearest': Image.NEAREST,
            'bilinear': Image.BILINEAR,
            'bicubic': Image.BICUBIC,
        }[mode]
        return T.functional.resize(x, self.target_size, interpolation)

    def colorjiiter(self, x):
        return self.color_jitter(x)

    def fliplr(self, x, func=None):
        if func:
            fn = func
        elif 'numpy' == type(x).__module__:
            fn = np.fliplr
        elif isinstance(x, Image.Image):
            fn = T.functional.hflip
        return self._transform(x, fn)

    def rotate(self, x):
        return self._transform(x, lambda x: T.functional.rotate(x, self.random_angle))
