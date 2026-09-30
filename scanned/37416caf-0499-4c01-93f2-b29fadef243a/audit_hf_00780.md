# [M] M-01 | Keeper Frontrunning

## Summary
Severity: Medium
Contest weight: 0.0954
Dataset id: 2414
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The executeOrderByKeeper function allows the keeper to execute orders which are technically fulfillable based on the pools price but that were not executed in the swap which crossed their end tick. However if the pool price is back within their position end tick at the time of keeper execution, then the position is marked as no longer executable by the keeper and is not executed. A bad faith actor could frontrun the keeper’s call to the executeOrderByKeeper function and force the pool price to go below the position’s execution range and thus prevent these positions from being executed.

## Recommendation
Be aware of this risk and consider using MEV protection such as flashbots for the keeper role.
