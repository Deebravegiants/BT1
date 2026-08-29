# [?] fix: don't panic on wasmtime loading errors (#15751)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2026-05-18
Source: https://github.com/near/nearcore/commit/6ecc544e933bf2d29026776a9c24c03305accdde
Type: security-commit

## Details
fix: don't panic on wasmtime loading errors (#15751)

Wasmer didn't have cases where loading could fail after compilation was
successful.

Wasmtime may run into resource limits at load time. We should not panic
on those and instead treat them as deterministic execution errors.
