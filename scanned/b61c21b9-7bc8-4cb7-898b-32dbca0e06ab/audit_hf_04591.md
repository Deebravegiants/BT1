# [M] M-07 | Improper Slippage And Deadline During Deposit

## Summary
Severity: Medium
Contest weight: 0.0716
Dataset id: 22195
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When calling deposit, a slippage of 0 and a deadline of block.timestamp is passed to _processRewardsToPodLp. Using 0 for slippage is dangerous as MEV bots could sandwich the swap to steal tokens. Similarly, setting block.timestamp as deadline is ineffective as the transaction could sit in the mempool until it's ready to be processed, at which time block.timestamp is set, therefore offering no protection from sandwich attacks.

## Recommendation
Allow user to input slippage and deadline parameters when depositing.
