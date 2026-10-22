# [M] QVSimpleStrategy contract does not work with native token

## Summary
Severity: Medium
Reporter: Shiny Gingham Bee
Source: https://github.com/allo-protocol/allo-v2/blob/851571c27df5c16f6586ece2a1cb6fd0acf04ec9/contracts/core/Allo.sol#L516
Type: audit-issue

## Details
# QVSimpleStrategy contract does not work with native token
QVSimpleStrategy strategy can not work with native token

## Vulnerability Detail
`QVSimpleStrategy` does not implement `fallback()` function or `receive()` function ==> The process of funding pool using native token is always reverted

## Impact
Native token pools can not use QVSimpleStrategy

## Code Snippet
https://github.com/allo-protocol/allo-v2/blob/851571c27df5c16f6586ece2a1cb6fd0acf04ec9/contracts/core/Allo.sol#L516

## Tool used
Manual Review

## Recommendation
Implement `fallback()` or `receive()` for `QVSimpleStrategy` contract
