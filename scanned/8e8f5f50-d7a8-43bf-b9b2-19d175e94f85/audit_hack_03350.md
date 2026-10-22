# [H] Ether can be stolen from contract with `externalSwap()`

## Summary
Severity: High
Reporter: yixxas
Source: https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L203
Type: audit-issue

## Details
# Ether can be stolen from contract with `externalSwap()`

## Summary
`externalSwap()` does not do any input verification for `fromTokenAmount` if `toToken == _ETH_ADDRESS_`. User can steal all ether from contract if there is any.

## Vulnerability Detail
`externalSwap()` does a `swapTarget.call{value: fromTokenAmount}` without actually checking if the user sent any ether along with the call. As a result, any ether lying in the contract can be stolen by simply setting `fromTokenAmount` to the amount of ether in the contract and using `toToken == _ETH_ADDRESS_`.

## Impact
Ether in contract can be stolen.

## Code Snippet
https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L203

## Tool used

Manual Review

## Recommendation
Check `msg.value == fromTokenAmount` if `toToken == _ETH_ADDRESS_`.
