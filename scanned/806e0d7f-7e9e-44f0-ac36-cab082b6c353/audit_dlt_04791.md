# [M] TODO M-04 No guarantee of no slippage | No guarantee of proper swap

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-10-mover
Published: 2022-10-28
Source: https://github.com/sherlock-audit/2022-10-mover-judging/issues/51
Type: sherlock-finding

## Details
GalloDaSballo

medium

# TODO M-04 No guarantee of no slippage | No guarantee of proper swap

## Summary

https://github.com/sherlock-audit/2022-10-mover/blob/main/cardtopup_contract/contracts/ExchangeProxy.sol#L174-L175

```solidity
        (bool success, ) = executorAddress.call{value: ethValue}(callData);

```

Except for 1 token, meaning everything else is up to the callData and the executor

## Vulnerability Detail

## Impact

## Code Snippet

## Tool used

Manual Review

## Recommendation
