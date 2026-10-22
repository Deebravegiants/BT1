# [H] 2 variables not indexed by `marketIndex`

## Summary
Severity: High
Contest weight: 0.6291
Dataset id: 753
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the token contract: `batched_stakerNextTokenShiftIndex` is indexed by `marketIndex`, so it can have separate (or the same) values for each different `marketIndex`.

`stakerTokenShiftIndex_to_longShortMarketPriceSnapshotIndex_mapping` and `stakerTokenShiftIndex_to_accumulativeFloatIssuanceSnapshotIndex_mapping` are not indexed by `marketIndex`. So the values of `stakerTokenShiftIndex_to_longShortMarketPriceSnapshotIndex_mapping` and `stakerTokenShiftIndex_to_accumulativeFloatIssuanceSnapshotIndex_mapping` can be overwritten by a different market, if `batched_stakerNextTokenShiftIndex[market1]`==`batched_stakerNextTokenShiftIndex[market2]`

This will lead to weird results in`_calculateAccumulatedFloat`, allocating too much or too little float.

[`Staker.sol` L622](https://github.com/code-423n4/2021-08-floatcapital/blob/main/contracts/contracts/Staker.sol#L622)
    
```solidity
function pushUpdatedMarketPricesToUpdateFloatIssuanceCalculations(
    ...
      stakerTokenShiftIndex_to_longShortMarketPriceSnapshotIndex_mapping[ batched_stakerNextTokenShiftIndex[marketIndex]  ] = stakerTokenShiftIndex_to_longShortMarketPriceSnapshotIndex_mappingIfShiftExecuted;
      stakerTokenShiftIndex_to_accumulativeFloatIssuanceSnapshotIndex_mapping[  batched_stakerNextTokenShiftIndex[marketIndex]  ] = latestRewardIndex[marketIndex] + 1;
      batched_stakerNextTokenShiftIndex[marketIndex] += 1;
    ...
)
```

Recommend adding an index with `marketIndex` to the variables:

  * `stakerTokenShiftIndex_to_longShortMarketPriceSnapshotIndex_mapping`
  * `stakerTokenShiftIndex_to_accumulativeFloatIssuanceSnapshotIndex_mapping`

Also consider shortening the variable names, this way mistakes can be spotted easier.

Confirmed by Jason of Float Capital: Yes, you are totally right, it should use the `marketIndex` since they are specific per market!

Embarrassed by this one!
Thank you for the report.
Fixed!!

## Recommendation
No recommendation
