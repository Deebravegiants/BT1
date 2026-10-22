# [M] DATA-4 | User Can Add Collateral When Market Is Set To closeOnly mode

## Summary
Severity: Medium
Contest weight: 0.3856
Dataset id: 20561
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a market is in closeOnly mode, users are able to add collateral to an existing position. When adding collateral to an existing position, the _increasePosition function is called, which, in turns, calls DataFabric::updateMarketData. In the case of adding collateral, userOrder.deltaSize equals 0, so the updateMarketData function will return in the first check and avoid the LibError.CloseOnlyMode() revert. This can result in a position being kept longer in a market than intended, by continuously adding collateral when needed rather than closing it out.

## Recommendation
Add a check to make sure the market is not in closeOnly mode:
```solidity
if (size == 0 && !closeOnlyMode[marketId]) return;
```
Otherwise, if this functionality is indeed to be supported, clearly document this behavior.
