# [M] Forget to check `msg.value == fromTokenAmount` in function `externalSwap`

## Summary
Severity: Medium
Reporter: TrungOre
Source: https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L179-L191
Type: audit-issue

## Details
# Forget to check `msg.value == fromTokenAmount` in function `externalSwap`

## Summary
Function `externalSwap` forget to check if `msg.value == fromTokenAmount` or not in case `fromToken` is `ETH`
 
## Vulnerability Detail
If a user wants to do an `externalSwap` with `fromToken = ETH`, (s)he can execute a transaction with `msg.value = fromTokenAmount`. But potentially, there may be some mistakes from the user, (s)he can send amount of ETH bigger than expected. Because there is no check if `msg.value = fromTokenAmount` in function `externalSwap`, it will make the difference amount locked in the contracts.

## Impact
Some ETH can be locked in the contract. 

## Code Snippet
* https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L179-L191
* https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L454

## Tool used
Manual review 

## Recommendation
Require `msg.value = fromTokenAmount` in function `externalSwap`. 

It would be better to add a single requirement in function `_depsoit()`
```solidity=
require(msg.value == 0, 'msg.value != 0'); 
```
to make sure no ETH mistakenly sends along the transaction to swap with `tokenFrom != ETH`.
