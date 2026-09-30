# [H] `registerAsset

## Summary
Severity: High
Contest weight: 0.1632
Dataset id: 1022
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Everyone can call the function `registerAsset()` of MochiProfileV0.sol Assuming the liquidity for the asset is sufficient, `registerAsset()` will reset the _assetClass of an already registered asset to `AssetClass.Sigma`.

When the _assetClass is changed to `AssetClass.Sigma` then `liquidationFactor()`, `riskFactor()`, `maxCollateralFactor()`, `liquidationFee()` `keeperFee()` `maxFee()` will also return a different value. Then the entire vault will behave differently. The threshold for liquidation will also be different, possibly leading to a liquidation that isn't supposed to happen.

## Recommendation
Add the following in function `registerAsset()`:
    
    require(_assetClass[_asset] ==0,"Already exists");
