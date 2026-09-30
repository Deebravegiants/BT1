# [M] CurveAddLiquidityAssetManager::curveAddLiquidity() does not deal correctly with isLegacy = 0b10 and ETH

## Summary
Severity: Medium
Contest weight: 0.0665
Dataset id: 15207
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
If isETH, but args.isLegacy is 1, it wraps to weth and allows pool, see here. 
if args.isLegacy is 0b10 and the asset is ETH, it does not send ETH to the pool, here. 
Additionally, it seems that it expects the ether balance to increase, which is unexpected, 
mintAmount = address(this).balance - initAmount;, as can be seen here.

## Recommendation
It seems that the mintAmount would always be 
IERC20(_args.lpToken).balanceOf(address(this)) - initAmount, where initAmount 
= IERC20(_args.lpToken).balanceOf(address(this));, but a pool example should be 
given to confirm.
