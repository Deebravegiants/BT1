# [H] `externalSwap()` miss `msg.value` check

## Summary
Severity: High
Reporter: __141345__
Source: https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L164-L192
Type: audit-issue

## Details
# `externalSwap()` miss `msg.value` check

## Summary

In `externalSwap()`, there is no `msg.value` check if swap from eth. The contract could loss fund when there is eth balance.


## Vulnerability Detail

`externalSwap()` does not check for `msg.value`. `mixSwap()` and `dodoMutliSwap()` have `msg.value` check in `_deposit()`. 

Malicious user can monitor the contract balance, all eth balance will be stolen by calling `externalSwap()` swap from eth, just need to indicate the `fromToken` is eth. Then the leftover eth will be used, instead of the user provided eth.

There could be eth mistakenly sent to the contract, although it it not expected. Such as mistakenly sent eth along with erc20 in the payable swap functions.


## Impact

The contract eth will be stolen whenever the eth is positive.


## Code Snippet

https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L164-L192


## Tool used

Manual Review

## Recommendation

Add check for `msg.value` to match the specified amount, just like in `_deposit()`:
```solidity
    function externalSwap() {
        // ...
        if (fromToken == _ETH_ADDRESS_) {
            require(msg.value == fromTokenAmount, "ETH_VALUE_WRONG");
        }
        // ...
    }
```
