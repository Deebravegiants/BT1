# [M] Anyone can steal `DODORouteProxy.sol` contract's ETH balance

## Summary
Severity: Medium
Reporter: pashov
Source: https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L164
Type: audit-issue

## Details
# Anyone can steal `DODORouteProxy.sol` contract's ETH balance

## Summary
The swap functions in `DODORouteProxy` are missing a msg.value check

## Vulnerability Detail
The `DODORouteProxy` contract is not usually expected to hold an Ether balance, but has the `fallback` and `receive` functions, both of which are market payable, so it is possible that if a caller uses the wrong function signature for example for a transaction with value, it will get to the contract as balance.
Now the problem is neither of the `swap()` methods check if when the `fromToken` is ETH the `fromTokenAmount` is equal to `msg.value`. This means that if the contract has any Ether balance, an attacker can call the swap methods with `msg.value == 0` and if he is using Ether as the `fromToken` he can swap it to any ERC20 token and receive it to his wallet.

## Impact
Any Ether balance the contract holds can be easily stolen without any preconditions. The contract is not expected to be holding an Ether balance, but has the `fallback` and `receive` functions, so since it is possible I think Medium severity is appropriate.

## Code Snippet
https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L164
https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L238
https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L323
## Tool used

Manual Review

## Recommendation
Add a check in all `swap` methods to verify that when `fromToken` is ETH then `fromTokenAmount == msg.value`
