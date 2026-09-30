# [M] M-16 | Min Price Validation Excludes Fee

## Summary
Severity: Medium
Contest weight: 0.0924
Dataset id: 152
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the _prepareClosePositionData function the userMinPrice is validated against the lastPrice, however the price applied to the value of the position and thus the amount received is reduced by the position _positionFeeBps.
Thus the resulting price experienced by the user upon closing their position can often be less than the minimum desired without any unpredictable price action occurring between the initiation and validation of a close.
The position fees are easy to predict ahead of time, and thus should be included in the userMinPrice validation.

## Recommendation
Consider reducing the lastPrice by the _positionFeeBps when validating the userMinPrice in the _prepareClosePositionData function.
