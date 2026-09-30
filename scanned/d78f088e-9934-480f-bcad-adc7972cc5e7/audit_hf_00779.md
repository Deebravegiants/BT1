# [H] H-05 | Batch Cancels Cause Users To Cancel Incorrectly

## Summary
Severity: High
Contest weight: 0.2713
Dataset id: 2413
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Imagine you have 10 active limit orders and you want to cancel the first 3 orders. User position keys in storage = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]. We call cancelBatchOrders(poolKey, 0, 3); The loop inside cancelBatchOrders() on the first iteration selects user position key at index 0. Then code executes _cancelOrder() > _claimOrder() [here](https://github.com/GuardianOrg/univ4-limit-order-hook-team1/blob/b9e157b1952193edef4824219f6f3f91a59514e6/src/LimitOrderManager.sol#L385). The user position keys in storage get changed from [0, 1, 2, 3, 4, 5, 6, 7, 8, 9] to [9, 1, 2, 3, 4, 5, 6, 7, 8]. Then on the next iteration code will select [again](https://github.com/GuardianOrg/univ4-limit-order-hook-team1/blob/b9e157b1952193edef4824219f6f3f91a59514e6/src/LimitOrderManager.sol#L242) the first element of the array because i is going to be 1 but canceledCount will be 1 as well. When subtracted we will get the 0th index again. At the end of the looping instead of removing user positions 0, 1 and 2, cancelBatchOrders() will remove 0, 9, 8 - this could be unexpected by the user and cancel orders by mistake. User positions will change in the following way: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9] > [7, 1, 2, 3, 4, 5, 6]

## Recommendation
Consider removing positions that are right after the user specified offset.
