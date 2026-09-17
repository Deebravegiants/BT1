# [?] Fix override of panic hook during cross-contract testing (#620)

## Summary
Severity: Unknown
Chain: Stellar
Component: stellar/rs-soroban-env
Published: 2023-01-18
Source: https://github.com/stellar/rs-soroban-env/commit/d803b0922d1d9eb4d3cfde5e6d574c7776c23388
Type: security-commit

## Details
Fix override of panic hook during cross-contract testing (#620)

* Fix override of panic hook during cross-contract testing

* Don't mention recursion in call_with_suppressed_panic_hook

Co-authored-by: Graydon Hoare <graydon@pobox.com>
