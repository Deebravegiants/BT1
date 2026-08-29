# [M] Unsound usages of `u8` type casting in spl-token-swap

## Summary
Severity: Medium
Chain: spl-token-swap
Component: spl-token-swap
Published: 2024-12-23
Source: https://github.com/advisories/GHSA-h6xm-c6r4-vmwf
Type: github-advisory

## Details
The library provides a safe public API `unpack` to cast `u8` array to arbitrary types, which can cause to undefined behaviors. The length check of array can only prevent out-of-bound access on the return type. However, it can't prevent misaligned pointer when casting `u8` pointer to a type aligned to larger bytes. For example, if we assign `u16` to `T`, **misaligned raw pointer dereference** could happen and cause to panic. Even if we pass the type aligned to same byte as `u8` (e.g., `bool`), it could construct a illegal type since `bool` can only have 0 or 1 as bit patterns, which is also an undefined behavior. The further exploits of the bug here are still not clear, so we would report this issue as unsound.  

The details of PoC to reproduce undefined behavior are provided in the [issue](https://github.com/solana-labs/solana-program-library/issues/5243).
