# [H] Incorrect use of `latestMarket` instead of `marketIndex` in several functions of `LongShort`

## Summary
Severity: High
Chain: Smart contract
Component: 2021-08-floatcapital
Published: 2021-08-11
Source: https://github.com/code-423n4/2021-08-floatcapital-findings/issues/92
Type: code-finding

## Details
# Handle

shw


# Vulnerability details

## Impact

Some part of the logic in the `initializeMarket` and `_seedMarketInitially` functions of `LongShort` incorrectly operates on the `latestMarket` instead of `marketIndex`, the provided parameter. Since the `latestMarket` is not necessary to be the market to be initialized, the initializing market could end up losing staker funds or not seeded with initial liquidity.

## Proof of Concept

Referenced code:
[LongShort.sol#L315](https://github.com/code-423n4/2021-08-floatcapital/blob/main/contracts/contracts/LongShort.sol#L315)
[LongShort.sol#L319](https://github.com/code-423n4/2021-08-floatcapital/blob/main/contracts/contracts/LongShort.sol#L319)
[LongShort.sol#L363-L365](https://github.com/code-423n4/2021-08-floatcapital/blob/main/contracts/contracts/LongShort.sol#L363-L365)

## Recommended Mitigation Steps

Change `latestMarket` to `marketIndex` in the referenced lines of code.
