# [H] H-01 | Invalid Remaining Reserves Calculation

## Summary
Severity: High
Contest weight: 0.1595
Dataset id: 2206
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The MarketMaking contract verifies if the protocol can bump by simulating an increase in the blvTick, and later validating some conditions, like bumpedCapacity > circulating. The bumpedAnchorCapacity is calculated based on the _getAnchorReserves. However, the bumpedFloorCapacity is mistakenly uses the remainingReserves as follows: int256 remainingReserves = _getVirtualReserves() + reserve.balanceOf(address(BPOOL)); However, the balance of the BPOOL contains all reserves, as they were all removed from the ranges, so remainingReserves is actually equal to totalReserves.

## Recommendation
Subtract the reserves used to calculate the ANCHOR range to correctly determine how many reserves remain.
