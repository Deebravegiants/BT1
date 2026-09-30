# [M] M-07 | Dangerous Price Used For Resolution Callback

## Summary
Severity: Medium
Contest weight: 0.0979
Dataset id: 1962
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
If settlement.settlementPriceD18 in assertionResolvedCallback() is outside the acceptable price range for the given epoch, the new price for the epoch will be capped to either min or max with function setSettlementPriceInRange. However, resolutionCallback() is still called with the original settlement.settlementPriceD18 and not the newly set price of the epoch. Whenever the settlement price is outside the acceptable range, the callback will receive an incorrect price. The protocol team plans to create new epochs with that price which will lead to an epoch starting with prices outside the valid range.

## Recommendation
Pass epoch.settlementPriceD18 instead of settlement.settlementPriceD18 to assertionResolvedCallback().
