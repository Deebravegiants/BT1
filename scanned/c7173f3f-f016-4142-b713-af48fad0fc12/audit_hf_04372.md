# [M] M-06 | Users May Receive Rewards For Only 1 Batch

## Summary
Severity: Medium
Contest weight: 0.1005
Dataset id: 21579
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The intended batch flow is as follows:
1. Users redeem valor in batch A.
2. Batch A finishes.
3. A trusted role marks the batch as claimable.
Whenever a user redeems their valor or claim USDC, _collectUserRevenueForClaimableBatch is called to increase their withdrawable amount by adding the withdrawable amounts of the first claimable batch. If there are users that redeem their valor in between steps 2 and 3 from above (so batch A is finished and batch B is active) when they claim USDC when batch B becomes claimable they will be given the reward from only the first claimable batch even though they are entitled to rewards from two batches.

## Recommendation
Accumulate rewards for all claimable batches when claiming
