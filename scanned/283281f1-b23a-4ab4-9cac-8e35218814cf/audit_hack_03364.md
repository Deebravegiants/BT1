# [M] Possible `DOS` inside the `mixSwap` and `_multiSwap` when for loop iteration goes long

## Summary
Severity: Medium
Reporter: ak1
Source: https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L278-L293
Type: audit-issue

## Details
# Possible `DOS` inside the `mixSwap` and `_multiSwap` when for loop iteration goes long

## Summary

When look at the `mixSwap` and `_multiSwap`, for swap, for loop is used to go through for multiple pairs.
When number of pair is more, the loop iteration will go long and this could lead to potential DOS.

## Vulnerability Detail
in external swap,

https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L278-L293

in `_multiSwap`, 
https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L393-L441

For each iteration, there function calling, decoding, transferring the fund is happended.

The number of iteration and work involved will be huge for `_multiSwap`

when there are more number of traversal, the contract can not work and revert due to out of gas.

## Impact
The contract can not function and revert due to out of gas.

## Code Snippet

https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L393-L441

https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L278-L293

## Tool used

Manual Review

## Recommendation

Put ca on the number of pair or splitNumber for iteration. 
Split the swap data and process in separate transaction.
