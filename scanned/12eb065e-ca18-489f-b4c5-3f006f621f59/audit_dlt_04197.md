# [M] check bytes data length before abi.decode

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-dodo
Published: 2022-11-15
Source: https://github.com/sherlock-audit/2022-11-dodo-judging/issues/70
Type: sherlock-finding

## Details
__141345__

medium

# check bytes data length before abi.decode

## Summary

The data length is not checked before abi.decode, which could result in wrong address being decoded, and lose some fee, or fail the transaction.

## Vulnerability Detail

`_multiSwap()` does not check data length of `swapSequence[j]`, if  bytes data is provided, the pool and adapter addresses could be wrong, the `curAmount` could be lost, or the call in adapter could revert and fail the transaction.

`_routeWithdraw()` does not check `feeData.length == 64` before decoding, if bytes data is provided, the broker address could be wrong and lose the broker fee. Or get wrong broker fee rate. 


## Impact

- Some fee could be lost if decoded the wrong address, such as the broker.
- The `curAmount` for the pool could be lost due to the wrong pool address.
- Some function call might fail if adapter is wrongly decoded.

## Code Snippet

https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L403-L404

https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L475



## Tool used

Manual Review

## Recommendation

Add check for the bytes data length before abi.decode.
