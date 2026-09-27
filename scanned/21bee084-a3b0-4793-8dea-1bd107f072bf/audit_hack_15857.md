# [M] `QVSimpleStrategy` cannot fund pools with NATIVE token due to lack of `receive() external payable {}` method.

## Summary
Severity: Medium
Reporter: Tart Citron Platypus
Source: https://github.com/sherlock-audit/2023-09-Gitcoin/blob/main/contracts/core/Allo.sol#L502-L520
Type: audit-issue

## Details
# `QVSimpleStrategy` cannot fund pools with NATIVE token due to lack of `receive() external payable {}` method.

## Vulnerability Detail

Due to the lack of NATIVE token support in QV Strategy, it is not possible to fund pools with native tokens when using such a strategy during pool creation.

https://github.com/sherlock-audit/2023-09-Gitcoin/blob/main/contracts/core/Allo.sol#L502-L520

## Impact

## Code Snippet

https://github.com/sherlock-audit/2023-09-Gitcoin/blob/main/contracts/core/libraries/Transfer.sol#L70-L81

https://github.com/sherlock-audit/2023-09-Gitcoin/blob/main/node_modules/solady/src/utils/SafeTransferLib.sol#L51-L62


## Tool used

Manual Review

## Recommendation
