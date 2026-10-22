# [C] C-06 | Settlement Can Be Impossible Due To Underﬂow

## Summary
Severity: Critical
Contest weight: 0.1441
Dataset id: 22049
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
This Equation in the settle function of Position.sol: self.depositedCollateralAmount += self.vEthAmount - self.borrowedVEth; is slightly different from: self.depositedCollateralAmount = self.depositedCollateralAmount + self.vEthAmount - self.borrowedVEth; Because in the ﬁrst equation, if self.borrowedEth < self.vEthAmount, then the equation will underﬂow, even though this position is fully collateralized. This underﬂow makes certain positions impossible to settle.

## Recommendation
Replace self.depositedCollateralAmount += self.vEthAmount - self.borrowedVEth; With self.depositedCollateralAmount = self.depositedCollateralAmount + self.vEthAmount - self.borrowedVEth;
