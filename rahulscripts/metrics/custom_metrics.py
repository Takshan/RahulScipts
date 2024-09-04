import torch
from torchmetrics import Metric
from typing import Any, List, Optional, Tuple
import numpy as np
from torch import Tensor, tensor
from torchmetrics.metric import Metric


class DaconScore(Metric):
    def __init__(self, dist_sync_on_step=False, **kwargs):
        super().__init__(dist_sync_on_step=dist_sync_on_step, **kwargs)
        self.add_state("score", default=torch.tensor(0.0), dist_reduce_fx="sum")
        self.add_state("count", default=torch.tensor(0), dist_reduce_fx="sum")
        self.unit = kwargs.get("unit", 9)

    def update(self, pred: torch.Tensor, target: torch.Tensor):
        score = self.score_compute(pred, target)
        self.score += score
        self.count += 1

    def compute(self) -> torch.Tensor:
        return self.score / self.count

    def rmse_compute(self, pred, target):
        return torch.sqrt(((pred - target) ** 2).mean())

    def normalized_rmse_compute(self, pred, target):
        return self.rmse_compute(pred, target) / (target.max() - target.min())

    def correct_ratio(self, pred, target):
        pIC50_pred = self.ic50_to_pic50(pred, self.unit)
        pIC50_target = self.ic50_to_pic50(target, self.unit)
        diff = pIC50_pred - pIC50_target
        correct = torch.sum(diff <= 0.5)
        return correct / len(pred)

    def score_compute(self, pred, target):
        if not isinstance(pred, torch.Tensor):
            pred = torch.tensor(pred)
        if not isinstance(target, torch.Tensor):
            target = torch.tensor(target)
        score = 0.5 * (1 - min(self.normalized_rmse_compute(pred, target), 1)) + (
            0.5 * self.correct_ratio(pred, target)
        )
        return score

    def ic50_to_pic50(self, ic50_value: float, unit: int = 9) -> float:
        pic50 = unit - torch.log10(ic50_value)
        return pic50


def concordance_index_compute(
    y_pred: torch.Tensor, y_true: torch.Tensor
) -> torch.Tensor:
    """Computes the concordance index between true and predicted values.

    Args:
        y_true (torch.Tensor): True values.
        y_pred (torch.Tensor): Predicted values.

    Returns:
        torch.Tensor: Concordance index.
    """
    # y_true = y_true.cpu().detach().numpy()
    # y_pred = y_pred.cpu().detach().numpy()
    # print(y_true, y_pred)

    matrix_pred: Tensor = _torch_subtract_outer(y_pred, y_pred)
    matrix_pred = (matrix_pred == 0.0) * 0.5 + (matrix_pred > 0.0)
    matrix_true: Tensor = _torch_subtract_outer(y_true, y_true)
    matrix_true = matrix_true > 0.0
    matrix_true_position: Tensor = torch.where(matrix_true == 1)
    matrix_pred_values: Tensor = matrix_pred[matrix_true_position]
    output = torch.where(
        torch.sum(matrix_pred_values) == 0,
        0.0,
        torch.sum(matrix_pred_values) / torch.sum(matrix_true),
    )
    return torch.autograd.Variable(output, requires_grad=True)


def _torch_subtract_outer(A, B) -> torch.Tensor:
    # print(A, B)
    # print(A.shape, B.shape)
    r: torch.Tensor = torch.empty((len(A), len(B)), dtype=torch.float16)
    for i in range(len(A)):
        for j in range(len(B)):
            r[i, j] = torch.subtract(A[i], B[j])
    return r


def _check_same_shape(preds: Tensor, target: Tensor) -> None:
    """Check that predictions and target have the same shape, else raise error."""
    if preds.shape != target.shape:
        raise RuntimeError(
            f"Predictions and targets are expected to have the same shape, but got {preds.shape} and {target.shape}."
        )


class ConcordanceIndex(Metric):
    # TODO
    # higher_is_better: Optional[bool] = True
    is_differentiable = True
    higher_is_better = True
    full_state_update = True
    total: Tensor

    def __init__(
        self,
        **kwargs: Any,
    ) -> None:
        super().__init__()

        self.add_state(
            "concordance_index", default=torch.tensor(0.0), dist_reduce_fx="sum"
        )
        self.add_state("total", default=torch.tensor(0), dist_reduce_fx="sum")

    def update(self, preds: Tensor, target: Tensor) -> None:
        """Update state with predictions and targets.

        Args:
            preds: Predictions from model
            target: Ground truth values
        """
        # print(preds, target, preds.shape, target.shape)
        _check_same_shape(preds, target)
        # self.preds = preds
        # self.target = target
        concordance_index = concordance_index_compute(preds, target)
        self.concordance_index += concordance_index
        n_obs: int = target.numel()
        self.total += n_obs

    def compute(self) -> torch.Tensor:
        """Computes mean ci over state."""
        return self.concordance_index / self.total
