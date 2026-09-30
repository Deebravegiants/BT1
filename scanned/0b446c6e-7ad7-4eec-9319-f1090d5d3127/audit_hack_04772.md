# [M] Lack of 0 address check on receiver on mint and mintWithEth function in UXDController.sol

## Summary
Severity: Medium
Reporter: karanctf
Source: https://github.com/sherlock-audit/2023-01-uxd/blob/main/contracts/core/UXDController.sol#L177-L235
Type: audit-issue

## Details
# Lack of 0 address check on receiver on mint and mintWithEth function in UXDController.sol

## Summary

It's important to include a check to ensure that the receiver address is not the zero address, so the contract can revert the transaction and prevent tokens from being lost.
## Vulnerability Detail
It's important to include a check to ensure that the receiver address is not the zero address,
## Impact
 the contract can revert the transaction and prevent tokens from being lost.
## Code Snippet
https://github.com/sherlock-audit/2023-01-uxd/blob/main/contracts/core/UXDController.sol#L177-L235
## Tool used

Manual Review

## Recommendation
add line
require(receiver != address(0), "Error: Receiver address cannot be the zero address.");
