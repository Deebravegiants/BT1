# [M] wrong YAXIS estimates

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-09-yaxis
Published: 2021-09-15
Source: https://github.com/code-423n4/2021-09-yaxis-findings/issues/112
Type: code-finding

## Details
# Handle

cmichel


# Vulnerability details

The `Harvester.getEstimates` contract tries to estimate a `YAXIS` amount but uses the wrong path and/or amount.

It currently uses a `WETH` **input** amount to compute a `YAXIS -> WETH` trade.

```solidity
address[] memory _path;
_path[0] = IStrategy(_strategy).want();
_path[1] = IStrategy(_strategy).weth();
// ...

_path[0] = manager.yaxis();
// path is YAXIS -> WETH now
// fee is a WETH precision value
uint256 _fee = _estimatedWETH.mul(manager.treasuryFee()).div(ONE_HUNDRED_PERCENT);
// this will return wrong trade amounts
_amounts = _router.getAmountsOut(_fee, _path);
_estimatedYAXIS = _amounts[1];
```

## Impact
The estimations from `getEstimates` are wrong.
They seem to be used to provide min. amount slippage values `(_estimatedWETH, _estimatedYAXIS)` for the harvester when calling `Controller._estimatedYAXIS`.
These are then used in `BaseStrategy._payHarvestFees` and can revert the harvest transactions if the wrongly computed `_estimatedYAXIS` value is above the actual trade value.
Or they can allow a large slippage if the `_estimatedYAXIS` value is below the actual trade value, which can then be used for a sandwich attack.

## Recommended Mitigation Steps
Fix the estimations computations.

As the estimations are used in `BaseStrategy._payHarvestFees`, the expected behavior seems to be trading `WETH` to `YAXIS`.
The path should therefore be changed to `path[0] = WETH; path[1] = YAXIS` in `Harvester.getEstimates`.
