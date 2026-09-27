# [?] fix(forge): fix stack overflow when the lib path is absolute. (#9190)

## Summary
Severity: Unknown
Chain: Tooling
Component: foundry-rs/foundry
Published: 2024-11-07
Source: https://github.com/foundry-rs/foundry/commit/bcdd514a633e27c29d5c00355311f6432cf31e8a
Type: security-commit

## Details
fix(forge): fix stack overflow when the lib path is absolute. (#9190)

* fix(forge): fix stack overflow when the lib path is absolute.

* format

* add test for setting absolute lib path.

* remove useless code:
