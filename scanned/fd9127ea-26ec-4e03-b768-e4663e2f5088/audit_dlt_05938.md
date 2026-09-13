# [?] Fix isoltest crash when formatting call arguments in a contract whose ABI includes entries without names

## Summary
Severity: Unknown
Chain: Solidity
Component: ethereum/solidity
Published: 2024-07-17
Source: https://github.com/argotorg/solidity/commit/1a5335a48688bd19dbb95d9279e7e1af5e4044d2
Type: security-commit

## Details
Fix isoltest crash when formatting call arguments in a contract whose ABI includes entries without names

- functionSignatureFromABI() would attempt to calculate signature for a function even if it had no name (i.e. was a constructor, fallback or receive). This would lead to a crash.
- The buggy logic is used only for formatting expectations when an test fails in interactive mode.
