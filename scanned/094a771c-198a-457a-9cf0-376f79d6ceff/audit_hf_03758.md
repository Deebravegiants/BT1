# [M] Growing of totalSupply after successive locking cycles

## Summary
Severity: Medium
Contest weight: 0.1102
Dataset id: 19921
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In a protection pool, after enough cycles of locking capital/depositing, totalSupply can grow to overflow uint256.
ProtectionPool.sol#L589-L606
_getExchangeRate() can become arbitrarily small after a funds locking, since locked funds are subtracted from totalSTokenUnderlying; This means that new depositors can get a lot more shares than depositors from before funds locking.
This behavior is correct, because otherwise previous depositors would have an oversized share of the new capital. However this has the negative effect of growing totalSupply exponentially, eventually reaching type(uint256).max and overflowing (reverting every new deposit).
Protocol can come to a halt if totalSupply reaches type(uint256).max.

## Recommendation
Design the token in a way that it can be rebased regularly.
