# [H] Pool Delegates can steal all the pool's funds by setting a malicious Withdrawal Manager.

## Summary
Severity: High
Contest weight: 0.1743
Dataset id: 10227
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The current PoolManager contract allows the pool manager to change the withdrawalManager contract without any checks using the setWithdrawalManager() function. Since the withdrawal manager is responsible for holding the redeemable tokens and informing the pool which tokens can be redeemed, corrupting this contract gives complete control of the pool's funds to the pool delegate.
Exploit scenario
• Pool delegate deposits one token into the Pool to get a single share
• Pool delegate sets a malicious withdrawal manager, allowing them to redeem a single share for the entire pool balance
• Pool delegate redeems their share and receives all the funds in the pool

## Recommendation
Remove the setWithdrawalManager() function or pause it by default.
