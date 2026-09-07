# [?] fix(bits): prevent BitArray.UnmarshalJSON from crashing on 0 bits in the JSON (#2774)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cometbft/cometbft
Published: 2024-04-11
Source: https://github.com/cometbft/cometbft/commit/75d12c32b8f8c504490096082b6217b87f5112ed
Type: security-commit

## Details
fix(bits): prevent BitArray.UnmarshalJSON from crashing on 0 bits in the JSON (#2774)

This change fixes a bug in which BitArray.UnmarshalJSON hadn't accounted
for the fact that invoking NewBitArray(<=0) returns nil and hence when
dereferenced would crash with a runtime nil pointer dereference. This
bug was found by my security analysis and fuzzing too.

Author: @odeke-em 

Fixes https://github.com/cometbft/cometbft/issues/2658

---

#### PR checklist

- [x] Tests written/updated
- [x] Changelog entry added in `.changelog` (we use
[unclog](https://github.com/informalsystems/unclog) to manage our
changelog)
- [ ] ~~Updated relevant documentation (`docs/` or `spec/`) and code
comments~~
- [x] Title follows the [Conventional
Commits](https://www.conventionalcommits.org/en/v1.0.0/) spec

---------

Co-authored-by: Emmanuel T Odeke <emmanuel@orijtech.com>
