# [H] Inflated _sharePrice() from inclusion of lockedAmount funds

## Summary
Severity: High
Contest weight: 0.2108
Dataset id: 13985
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The value used for calculation of _sharePrice() is totalValue(), which consists of lockedValue() and totalProviderValue(). lockedValue(), according to the natspec, is meant to return the amount of the withdrawal token that is held by the yield manager.
This means that the inherited WithdrawalQueue's lockedAmount is also included, which shouldn't be so. For the ETHYieldManager specifically, once requests are finalised, accumulatedNegativeYields is decremented if non-zero, but totalValue() remains unchanged, so sharePrice() would be inflated for subsequent finalisations should accumulatedNegativeYields be non-zero.
Finalized ETH is considered to have been burnt on L2 and out of the system on L1 and (part of the) potential negative yield recovered; so lockedAmount funds should not influence future share prices anymore.

## Recommendation
Subtract the locked amount in value.
```diff
- uint256 value = totalValue();
+ uint256 value = totalValue() - getLockedAmount();
```
