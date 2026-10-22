# [H] H-08 | Multi-market Liquidations May Fail

## Summary
Severity: High
Contest weight: 0.2053
Dataset id: 2099
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a position with multi-market exposure becomes liquidatable, the protocol intends to liquidate
and close positions across all markets. However, the current implementation of the liquidate
function can only process one market at a time.
This creates complications:
1. If the broker closes the proﬁtable position in Market A ﬁrst, the overall position may no longer be
liquidatable due to lower margin requirements and increased collateral. This leaves the loss-making
Market B active, which may be unexpected and undesirable for the trader.
2. Conversely, if the broker closes the loss-making position in Market B ﬁrst, there may not be
enough collateral to cover borrowing and position fees as the proﬁts from Market A remain
unrealized. This results in skipped and unpaid fees during liquidation.

## Recommendation
Revise the liquidate function to loop through all associated markets and close every position within a
single transaction.
