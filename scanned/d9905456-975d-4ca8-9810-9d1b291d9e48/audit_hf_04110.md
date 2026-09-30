# [M] DATA-1 | Invalid Live Market Update Validation

## Summary
Severity: Medium
Contest weight: 0.3863
Dataset id: 20568
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When updating an existing market using the `updateExistingMarket` function, at the end of the function there is a check that if the new market argument bundle would set the market to true, meaning directly activate it, then to clear it since the market needs to be unpaused by the admin after update separately. This validation is incorrectly checking if the market is already false, then it sets it to false again, meaning that if `_updatedMarket.isLive` is true, the market would be left as it is and incorrectly remain active after function execution:
```solidity
if (!_updatedMarket.isLive) availableMarkets[_marketId].isLive = false;
```

## Recommendation
Remove the ! operator from the if clause on line 598.
