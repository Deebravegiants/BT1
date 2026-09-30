# [M] M-16 | Attacker Profits From Block Stuffing Orders

## Summary
Severity: Medium
Contest weight: 0.0912
Dataset id: 2281
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Because orders only have about 5 blocks to have their order be settled before they become stale an attacker could congest the network so that attempts to call settleOrder fail due to all the gas for that block being used.
If an attacker were to stuff the blocks with their own transactions so that settleOrder will fail for 60 seconds, the attacker would then be able to cancel all of the pending orders and collect the cancelation reward for each one.
The lower the block.baseFee is and the more pending orders there are the more profitable this attack becomes.

## Recommendation
Consider carefully balancing the profit made from cancels and document the risk for users.
