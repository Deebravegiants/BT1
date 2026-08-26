# [?] fix memory corruption in geyser plugin manager tests with recent toolchains (#33097)

## Summary
Severity: Unknown
Chain: Solana
Component: solana-labs/solana
Published: 2023-08-31
Source: https://github.com/solana-labs/solana/commit/7e5cd11b340b3c80285481cc3276a7b002486ef0
Type: security-commit

## Details
fix memory corruption in geyser plugin manager tests with recent toolchains (#33097)

* geyser: genericize manager test dummy plugin generators

* geyser: dlopen self the safe way in test dummy plugin generator

fixes memory corruption
