# [M] Incorrect tick rounding in TWAP calculation

## Summary
Severity: Medium
Contest weight: 0.5424
Dataset id: 4157
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function _queryTwap(
    PoolKey memory poolKey,
    uint32 twapSecondsAgoStart,
    uint32 twapSecondsAgoEnd
)
    internal
    returns (int24 arithmeticMeanTick)
    int56 tickCumulativesDelta = tickCumulatives[1] - tickCumulatives[0];
    return int24(tickCumulativesDelta / int56(uint56(windowSize))); // @audit rounding towards zero if tickCumulativesDelta < 0
```

## Recommendation
```solidity
function _queryTwap(
    PoolKey memory poolKey,
    uint32 twapSecondsAgoStart,
    uint32 twapSecondsAgoEnd
)
    internal
    returns (int24 arithmeticMeanTick)
    int56 tickCumulativesDelta = tickCumulatives[1] - tickCumulatives[0];
    arithmeticMeanTick = int24(tickCumulativesDelta / int56(uint56(windowSize)));
    // Always round to negative infinity
    if (tickCumulativesDelta < 0 && (tickCumulativesDelta % windowSize != 0)) arithmeticMeanTick--;
    return arithmeticMeanTick;
    // return int24(tickCumulativesDelta / int56(uint56(windowSize)));
```
