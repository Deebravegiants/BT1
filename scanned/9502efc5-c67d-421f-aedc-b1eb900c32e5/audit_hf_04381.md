# [M] M-09 | Valor May Be Redeemed At An Undesirable Rate

## Summary
Severity: Medium
Contest weight: 0.0947
Dataset id: 21597
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A user may observe that redeeming valor in batch A is quite profitable so they initiate a redeemValor request. However, due to their transaction taking quite a long time to be executed and delivered to the Orderly Network, their redeem request may now end up in batch B. In batch B the redeeming terms may not be as good as the user desired.
For example, a lot of valor accumulated without much profit or the admin called Valor.setTotalUsdcInTreasure to decrease the usdc. The user will not be able to stop the transaction and in result, they will redeem at undesirable rate.

## Recommendation
Add an additional batchId parameter to the redeemValor function and revert the tx if it doesn't match the current batchId.
