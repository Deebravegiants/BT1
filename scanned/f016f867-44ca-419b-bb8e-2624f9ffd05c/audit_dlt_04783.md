# [M] executeSwap() function would always revert.

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-10-mover
Published: 2022-10-28
Source: https://github.com/sherlock-audit/2022-10-mover-judging/issues/78
Type: sherlock-finding

## Details
cryptphi

medium

# executeSwap() function would always revert.

## Summary
The call to ExchangeProxy.executeSwap() reverts due to the access check in ExchangeProxy.executeSwapDirect()

## Vulnerability Detail
Since the call to ExchangeProxy.executeSwapDirect() checks that the caller is the `transferProxyAddress` , then the call to ExchangeProxy.executeSwap()  would always revert

## Impact
Reverts making function unsable.

## Code Snippet

https://github.com/sherlock-audit/2022-10-mover/blob/main/cardtopup_contract/contracts/ExchangeProxy.sol#L91-L103
https://github.com/sherlock-audit/2022-10-mover/blob/main/cardtopup_contract/contracts/ExchangeProxy.sol#L102

Require check in ExchangeProxy.executeSwapDirect()
https://github.com/sherlock-audit/2022-10-mover/blob/main/cardtopup_contract/contracts/ExchangeProxy.sol#L139

## Tool used

Manual Review

## Recommendation
1. If a genuinely redundant function, then remove. Else, add a call to executeSwap() in HardendedTopupProxy contract.
