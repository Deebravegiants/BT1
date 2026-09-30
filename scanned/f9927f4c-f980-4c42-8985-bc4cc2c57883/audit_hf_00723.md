# [H] H-04 | PnL Wiped Out On Breaking Even

## Summary
Severity: High
Contest weight: 0.1337
Dataset id: 2274
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the realizeAccountPnlAndUpdate function when the amountDeltaUsd is 0 the function early returns. However this early return will errantly leave debt in the account’s margin while the position’s unrealized proﬁt, which is perfectly offsetting debt, is lost. The PnL lost by the trader this way is credited to the LPs as it is removed from the reportedDebt.

## Recommendation
Assign the account’s debt to 0 in the amountDeltaUsd == 0 early return case and account for this debt update in the market.totalTraderDebtUsd.
