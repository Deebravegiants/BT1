# [?] fix: block memory allocation overflow (#3639)

## Summary
Severity: Unknown
Chain: Vyper
Component: vyperlang/vyper
Published: 2023-10-05
Source: https://github.com/vyperlang/vyper/commit/68da04b2e9e010c2e4da288a80eeeb9c8e076025
Type: security-commit

## Details
fix: block memory allocation overflow (#3639)

this fixes potential overflow bugs in pointer calculation by blocking
memory allocation above a certain size. the size limit is set at
`2**64`, which is the size of addressable memory on physical machines.

practically, for EVM use cases, we could limit at a much smaller number
(like `2**24`), but we want to allow for "exotic" targets which may
allow much more addressable memory.
