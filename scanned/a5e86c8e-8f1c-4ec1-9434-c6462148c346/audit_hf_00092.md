# [M] M-11 | _calcPositionSizeBonus Errant Token Amount

## Summary
Severity: Medium
Contest weight: 0.1131
Dataset id: 168
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The position size bonus for liquidator remuneration is computed with the _calcPositionSizeBonus function.
The bonus is based upon a difference in the current price and the liquidated ticks price and the documentation for the _calcPositionSizeBonus indicates that the resulting value is denominated in native ether.
However when the asset is wstEth and the WstEthOracleMiddleware is used the price will be for wstEth and thus the _calcPositionSizeBonus function will return a wstEth amount.
However this returned value is treated as native ether and converted to wstEth redundantly on line 108: wstETHRewards_ = _wstEth.getWstETHByStETH(totalRewardETH);

## Recommendation
Instead of converting the position size bonus amount to wstEth with the getWstETHByStETH(totalRewardETH) call, add it to the resulting wstEth value. If this approach is taken be sure to cap the maxReward to the resulting wstEth amount and assign this number as a wstEth value.
