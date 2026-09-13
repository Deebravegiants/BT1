# [M] Usage of transfer can lock out funds if gas cost changes

## Summary
Severity: Medium
Reporter: yixxas
Source: https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/lib/UniversalERC20.sol#L29
Type: audit-issue

## Details
# Usage of transfer can lock out funds if gas cost changes

## Summary
`transfer` uses a fix gas of 2300. Gas cost can and will change. For example, in EIP1884, gas per SLOAD increase from 200 -> 800. Such changes can make such calls to always revert.

## Vulnerability Detail
This is used in `superWithdraw()`, which can prevent funds from being saved, as well in `universalTransfer()` which is used in the whole protocol and can block transfer of ether.

## Impact
Functions that relies on `universalTransfer()` and `superWithdraw()` can no longer be used.

## Code Snippet
https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/lib/UniversalERC20.sol#L29
https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L152

## Tool used

Manual Review

## Recommendation
Use `call.value()` instead of `transfer()`.
