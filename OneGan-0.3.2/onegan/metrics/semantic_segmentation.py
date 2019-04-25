# Copyright (c) 2018 Salas Lin (leVirve)
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT


import numpy as np
from scipy.optimize import linear_sum_assignment

from onegan import utils


np.seterr(divide='ignore', invalid='ignore')


def confusion_table(preds, labels, num_class: int):
    ''' calculate the confision matrix
        preds: Variable, tensor, ndarray
        labels: Variable, tensor, ndarray

        *credit: refer from [chainer/chainercv] eval_semantic_segmentation.py
    '''
    preds = preds.data if utils.is_variable(preds) else preds
    labels = labels.data if utils.is_variable(labels) else labels

    confusion = np.zeros(num_class * num_class, dtype=np.int64)

    for pred, label in zip(preds, labels):
        pred = pred.view(-1)
        label = label.view(-1)
        mask = label < 255
        hist = num_class * label[mask] + pred[mask]
        confusion += np.bincount(hist.cpu().numpy(), minlength=num_class ** 2)

    return confusion.reshape((num_class, num_class))


def intersection_over_union(confusion: np.ndarray):
    iou_denominator = (confusion.sum(axis=1) + confusion.sum(axis=0) - np.diag(confusion))
    return np.diag(confusion) / (iou_denominator)


def max_bipartite_matching_score(predictions: np.ndarray, targets: np.ndarray):

    def _one_sample(prediction, target):
        ''' calculate the maximum bipartite matching between two labels
            prediction: 2-D numpy array
            target: 2-D numpy array
        '''
        pred_labels = np.unique(prediction)
        gt_labels = np.unique(target)
        cost = np.zeros((len(pred_labels), len(gt_labels)))

        for i, p in enumerate(pred_labels):
            p_mask = prediction == p
            cost[i] = [-np.sum(p_mask & (target == g)) for g in gt_labels]

        row_ind, col_ind = linear_sum_assignment(cost)
        score = -cost[row_ind, col_ind].sum()
        return score / target.size

    predictions, targets = utils.to_numpy(predictions), utils.to_numpy(targets)

    if len(predictions.shape) == len(targets.shape) and len(predictions.shape) == 3:
        scores = [_one_sample(p, t) for p, t in zip(predictions, targets)]
        return np.mean(scores)

    return _one_sample(predictions, targets)


class Metric():

    def __init__(self, num_class, only_scalar=False, prefix='acc/'):
        self.num_class = num_class
        self.only_scalar = only_scalar
        self.prefix = prefix

    def __call__(self, output, target):
        '''
            output: Variable
            target: Variable
        '''
        confusion = confusion_table(output, target, num_class=self.num_class)
        iou = intersection_over_union(confusion)
        pixel_accuracy = np.diag(confusion).sum() / confusion.sum()
        class_accuracy = np.diag(confusion) / np.sum(confusion, axis=1)

        if self.only_scalar:
            return {f'{self.prefix}miou': np.nanmean(iou),
                    f'{self.prefix}pixel': pixel_accuracy,
                    f'{self.prefix}mean_class': np.nanmean(class_accuracy)}
        else:
            return {'iou': iou, 'miou': np.nanmean(iou),
                    'pixel_accuracy': pixel_accuracy,
                    'class_accuracy': class_accuracy,
                    'mean_class_accuracy': np.nanmean(class_accuracy)}
