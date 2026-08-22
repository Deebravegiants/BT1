# [?] fix: dont panic on note msgs on contracts with no notes (#24852)

## Summary
Severity: Unknown
Chain: Aztec
Component: AztecProtocol/aztec-packages
Published: 2026-07-21
Source: https://github.com/AztecProtocol/aztec-packages/commit/0b4cfbc78c07c42e59e3af4530f769e51e1ff438
Type: security-commit

## Details
fix: dont panic on note msgs on contracts with no notes (#24852)

A contract with no notes might otherwise panic if e.g. it processed an
offchain message related to one. I also made PXE skip the standard
contracts that have no notes and events, both to avoid such a situation
and because there's no need to do it.

(cherry picked from commit dfcdea6756263c09e179861071fa4c64572ebb2d)
