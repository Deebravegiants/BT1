# [?] fix(lang): prevent panic on undersized zero-copy account deserialization (#4555)

## Summary
Severity: Unknown
Chain: Solana
Component: coral-xyz/anchor
Published: 2026-05-19
Source: https://github.com/otter-sec/anchor/commit/b05a2192f53e2aae3b0cba1b7a1a2d3ca826c89c
Type: security-commit

## Details
fix(lang): prevent panic on undersized zero-copy account deserialization (#4555)

* fix(lang): enhance account deserialization checks to prevent panics

* test(lang): add tests for AccountLoader handling of truncated accounts

* fix(lang/syn): improve error handling for account deserialization failures

* refactor(lang): extract size check into separate method for improved readability and maintainability
