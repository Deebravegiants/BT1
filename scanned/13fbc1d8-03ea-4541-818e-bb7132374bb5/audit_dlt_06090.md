# [?] ZKVM-998: fix panic when using embedded allocator and add more details to OOM message (#2761)

## Summary
Severity: Unknown
Chain: ZK
Component: risc0/risc0
Published: 2025-01-27
Source: https://github.com/risc0/risc0/commit/7a8ed2e6b8b54014267967a963c489026b357745
Type: security-commit

## Details
ZKVM-998: fix panic when using embedded allocator and add more details to OOM message (#2761)

This fixes a panic that happens when calling items in std when the
embedded allocator is enabled. Our std implementation calls into
`sys_alloc_aligned` so we should not panic when this is called. Fix this
by calling the embedded allocator's alloc function.
