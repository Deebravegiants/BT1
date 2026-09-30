# [M] M-02 | Risk Free Trades Via Pay Debt

## Summary
Severity: Medium
Contest weight: 0.0970
Dataset id: 2259
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
An order can be committed that would attempt to merge with another account upon settlement but would then revert due to not meeting the Initial Margin Requirements. That same order could then be "enabled" by paying down some debt in the account which would allow for the ﬁnal merged account to meet IMR. A trader could use this to create a risk-free trade whereby if the actual price moved enough from the Pyth price at the beginning of the settlement window, the trader could enable the trade and then immediately sell for a proﬁt.

## Recommendation
Consider restricting calls to payDebt when there is a pending order.
