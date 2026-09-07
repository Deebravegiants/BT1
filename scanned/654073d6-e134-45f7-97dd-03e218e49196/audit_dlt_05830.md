# [?] tests: fix logged panics in reproducible labels test (#4446)

## Summary
Severity: Unknown
Chain: Algorand
Component: algorand/go-algorand
Published: 2022-08-23
Source: https://github.com/algorand/go-algorand/commit/924d2fbb4872f136c0f5fb545ca5addb50efa774
Type: security-commit

## Details
tests: fix logged panics in reproducible labels test (#4446)

Fix an issue with consensus params not saved in forked ledgers.
Set logging level=info in tests that produce to much debug output while adding thousands of blocks.
