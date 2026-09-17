# [M] DODORouteProxy#mixSwap doesn't validate all input array lengths

## Summary
Severity: Medium
Reporter: 0x52
Source: https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L238-L311
Type: audit-issue

## Details
# DODORouteProxy#mixSwap doesn't validate all input array lengths

## Summary

DODORouteProxy#mixSwap validates that most input arrays are the same length but fails to validate the moreInfos array. An array of incorrect length could result in wasted gas on failed swaps or incorrect info being passed to adapters.

## Vulnerability Detail

        require(mixPairs.length > 0, "DODORouteProxy: PAIRS_EMPTY");
        require(mixPairs.length == mixAdapters.length, "DODORouteProxy: PAIR_ADAPTER_NOT_MATCH");
        require(mixPairs.length == assetTo.length - 1, "DODORouteProxy: PAIR_ASSETTO_NOT_MATCH");
        require(minReturnAmount > 0, "DODORouteProxy: RETURN_AMOUNT_ZERO");

In DODORouteProxy#mixSwap input length checks, moreInfos is missing from the length validation. 

## Impact

An array of incorrect length could result in wasted gas on failed swaps or incorrect info being passed to adapters leading to unexpected results.

## Code Snippet

https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L238-L311

## Tool used

Manual Review

## Recommendation

Add a check for moreInfos in the validation block:

    +   require(mixPairs.length == moreInfos.length, "DODORouteProxy: PAIR_MOREINFOS_NOT_MATCH");
