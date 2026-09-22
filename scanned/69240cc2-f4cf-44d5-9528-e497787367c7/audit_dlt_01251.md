# [?] db: fix integer overflow vulnerability in FixedSizeBitmapsWriter (#17073)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2025-11-21
Source: https://github.com/erigontech/erigon/commit/ee62d9c9371f4178903553691a18e47735894afd
Type: security-commit

## Details
db: fix integer overflow vulnerability in FixedSizeBitmapsWriter (#17073)

Replace unsafe `multiplication` with` math.SafeMul()` in bitmap size
calculation.

Fixes the TODO

Co-authored-by: Alexey Sharov <AskAlexSharov@gmail.com>
