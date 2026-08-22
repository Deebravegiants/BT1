# [?] Prevent panic-causing param values (#875)

## Summary
Severity: Unknown
Chain: Kava
Component: Kava-Labs/kava
Published: 2021-03-15
Source: https://github.com/Kava-Labs/kava/commit/20b3fa53e30ca8789571ef925f583f53a842362d
Type: security-commit

## Details
Prevent panic-causing param values (#875)

* prevent cdp liquidation ratio being 0.0

* fix linter warning

* prevent hard conversin factor being < 1

* add liquidation tests for different keeper rewards
