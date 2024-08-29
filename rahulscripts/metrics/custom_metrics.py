import torch
from torchmetrics import Metric


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
