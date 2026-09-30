# [M] M-07 | Slippage Check Occurs Before Adjustment

## Summary
Severity: Medium
Contest weight: 0.0938
Dataset id: 161
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the _prepareInitiateOpenPositionData function the params.userMaxPrice is validated against the lastPrice, however the user’s execution price will include a fee which is not included in the lastPrice.
On the following line the data_.adjustedPrice is assigned which is adjusted by this fee and more closely estimates the execution price that the user will experience.
Ideally the fee is included in the slippage validation since it will affect the user’s ultimate execution price, and allows users to protect themselves if the _positionFeeBps were to be unexpectedly changed.

## Recommendation
Consider validating the params.userMaxPrice against the adjustedPrice which includes the position fee.
