# [?] [paper] Resolving supposed unsoundness issue around aborts behavioral predicate (#19584)

## Summary
Severity: Unknown
Chain: Aptos
Component: aptos-labs/aptos-core
Published: 2026-04-29
Source: https://github.com/aptos-labs/aptos-core/commit/6a2e4207d1d4ec59686694f2008c662be268cb04
Type: security-commit

## Details
[paper] Resolving supposed unsoundness issue around aborts behavioral predicate (#19584)

It turns out this is a false positive since we can assume the function has verified successfully.

Also updated related work with insights about F* and Dafny.
