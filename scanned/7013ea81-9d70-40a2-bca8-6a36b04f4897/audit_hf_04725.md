# [M] BBLeverage::sellCollateral is unusable due to

## Summary
Severity: Medium
Contest weight: 0.3871
Dataset id: 22537
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
sellCollateral enable to leverage up on a borrow position in a BigBang market.
However the endpoint is unusable as is due to collateralId used to deposit in YieldBox, instead of assetId
We can see here that after withdrawing collateral, and swapping it for asset, BBLeverage::sellCollateral attempts to deposit collateralId into YieldBox:
cts/markets/bigBang/BBLeverage.sol#L149
Which will always revert, since at that point we always have asset and not collateral.
This function is thus unusable
The function BBLeverage::sellCollateral will always revert and is unusable

## Recommendation
Change the deposit to use assetId, as is correctly done in SGLLeverage:
```solidity
yieldBox.depositAsset(assetId, address(this), address(this), 0, memoryData.shareOut); // TODO Check for rounding attack?
```
cts/markets/singularity/SGLLeverage.sol#L135
