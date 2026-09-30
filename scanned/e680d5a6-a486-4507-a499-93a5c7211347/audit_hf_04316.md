# [M] M-01 | Launch Allows For Anchor Larger Than Target Width

## Summary
Severity: Medium
Contest weight: 0.0479
Dataset id: 21467
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the launch function the anchor position can be more than 10 tick spacings wide as the setTicks call for the anchor position assigns the lower tick as the floor tick + one tick spacing, and the upper tick as the even tick spacing ahead of the active tick.

## Recommendation
Limit the anchor position to have a lower of max(_floorTickL + T_S, activeTS - ANCHOR_WIDTH*).
