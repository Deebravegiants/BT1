# [C] C-01 | getPositionPnl Always Returns 0

## Summary
Severity: Critical
Contest weight: 0.1608
Dataset id: 2030
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The getPositionPnl function is utilized to verify the current profit and loss of a position. However, when it calls GMX's getPositionPnlUsd, the sizeDeltaUsd parameter is set to 0. The issue with this is that the getPositionPnlUsd function calculates profit and loss based on the amount of size change. Therefore, in cases where the sizeDelta is zero, it indicates that no profit or loss has occurred for that portion of the position since the portion is 0. This results in margin calculations being inaccurate by the amount of profit and loss the position currently has, impacting PPS.

## Recommendation
To obtain the total profit and loss of the position, pass in the total size of the position.
