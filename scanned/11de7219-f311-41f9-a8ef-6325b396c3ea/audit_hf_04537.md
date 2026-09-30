# [M] M-18 | Account Can Be Made Liquidateable By Cancelling

## Summary
Severity: Medium
Contest weight: 0.0714
Dataset id: 22101
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Cancellation charges account with keeper fee. Which this can put the account into a liquidatable
state. This will result in immediate loss for user who could have withdrawn their funds otherwise.
Order’s cancel-ability can be controlled by manipulating the skew. In addition to the fee for
cancellation, the liquidation fees provide an added incentive to cancel the order which could even
cover the costs of the skew manipulation.

## Recommendation
Validate that account won’t be liquidatable after cancellation.
