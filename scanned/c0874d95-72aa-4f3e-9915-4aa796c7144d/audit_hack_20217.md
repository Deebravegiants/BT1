# [M] 5.3.7 _slippageToldoes not adjust for decimal differences

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk
**Context:** AssetLogic.sol#L273
**Description:** Users set the slippage tolerance in percentage. TheassetLogiccalculates:
minReceived = (_amount * _slippageTol) / s.LIQUIDITY_FEE_DENOMINATOR

ThenassetLogicusesminReceivedin the swap functions. TheminReceived, however, does not adjust for the
decimal differences betweenassetInandassetOut. Users will either always hit the slippage or suffer huge
slippage whenassetInandassetOuthave a different number of decimals.
Assume the number of decimals ofassetInis 6 and the decimal ofassetOutis 18. TheminReceivedwill be set
to10ˆ-12smaller than the correct value. Users would be vulnerable to sandwich attacks in this case. Assume the
number of decimals ofassetInis 18 and the number of decimals ofassetOutis 6. TheminReceivedwill be set
to10ˆ12larger than the correct value. Users would always hit the slippage and the cross-chain transfer will get
stuck.


```
library AssetLogic {
function _swapAsset(... ) ... {
// Swap the asset to the proper local asset
uint256 minReceived = (_amount * _slippageTol) / s.LIQUIDITY_FEE_DENOMINATOR;
return (pool.swapExact(_amount, _assetIn, _assetOut, minReceived), _assetOut);
}
}
```
**Recommendation:** Recommend to adjust the value withswapStorage.tokenPrecisionMultipliersfor internal
swap. For the external swap, the value should be adjusted according totoken.decimals.
**Connext:** Solved in PR 1574.
**Spearbit:** Verified.
