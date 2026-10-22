# [M] wrong YAXIS estimates

## Summary
Severity: Medium
Contest weight: 0.3925
Dataset id: 989
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
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

## Recommendation
Fix the estimations computations.

As the estimations are used in `BaseStrategy._payHarvestFees`, the expected behavior seems to be trading `WETH` to `YAXIS`. The path should therefore be changed to `path[0] = WETH; path[1] = YAXIS` in `Harvester.getEstimates`.

Price estimates on Uniswap are dependent on which side of the swap you’re making

Sponsor has mitigated in later PR
