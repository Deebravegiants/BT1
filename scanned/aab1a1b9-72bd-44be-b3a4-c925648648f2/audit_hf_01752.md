# [M] Limits in LIFuelFacet

## Summary
Severity: Medium
Contest weight: 0.3767
Dataset id: 9577
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The facet LIFuelFacet is meant for small amounts, however, it doesn't have any limits on the funds sent. This might result in funds getting stuck due to insufficient liquidity on the receiving side.
```solidity
function _startBridge(...) ... {
    ...
    if (LibAsset.isNativeAsset(_bridgeData.sendingAssetId)) {
        serviceFeeCollector.collectNativeGasFees{...}(...);
    } else {
        LibAsset.maxApproveERC20(...);
        serviceFeeCollector.collectTokenGasFees(...);
        ...
    }
}
```

## Recommendation
Consider enforcing limits in LIFuelFacet.
