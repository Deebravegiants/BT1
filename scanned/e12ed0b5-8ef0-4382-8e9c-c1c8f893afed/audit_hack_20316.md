# [M] 5.2.1 Limits inLIFuelFacet

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk
**Context:** LIFuelFacet.sol#L72-L
**Description:** The facetLIFuelFacetis meant for small amounts, however, it doesn't have any limits on the funds
sent. This might result in funds getting stuck due to insufficient liquidity on the receiving side.
function _startBridge(...) ... {
if (LibAsset.isNativeAsset(_bridgeData.sendingAssetId)) {
serviceFeeCollector.collectNativeGasFees{...}(...);
} else {
LibAsset.maxApproveERC20(...);
serviceFeeCollector.collectTokenGasFees(...);
}
}

**Recommendation:** Consider enforcing limits inLIFuelFacet.
**LiFi:** Limits apply to all bridges and depend on the liquidity on the receiving chain. This information is usually not
available on the source chain. For sure some high fixed limits could be added but they don't really check that there
is that much liquidity available.
Checking limits and applying them to the calls is handled by the backend.
**Spearbit:** Acknowledged.
