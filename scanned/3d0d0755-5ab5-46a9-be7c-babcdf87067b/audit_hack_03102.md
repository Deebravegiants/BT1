# [H] Converter.sol .transfer is bad practice

## Summary
Severity: High
Reporter: Bnke0x0
Source: https://github.com/sherlock-audit/2022-10-illuminate/blob/main/src/Converter.sol#L48
Type: audit-issue

## Details
# Converter.sol .transfer is bad practice

## Summary

## Vulnerability Detail
Converter.sol .transfer is bad practice
## Impact
Using .transfer to send ether is now considered bad practice as gas costs can change, breaking the code. See:https://consensys.net/diligence/blog/2019/09/stop-using-soliditys-transfer-now/https://chainsecurity.com/istanbul-hardfork-eips-increasing-gas-costs-and-more/

## Code Snippet
https://github.com/sherlock-audit/2022-10-illuminate/blob/main/src/Converter.sol#L48

          'Safe.transfer(IERC20(u), msg.sender, unwrapped);'

## Tool used

Manual Review

## Recommendation
Use call instead, and make sure to check for reentrancy.
