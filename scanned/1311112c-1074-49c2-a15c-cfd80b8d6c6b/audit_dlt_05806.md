# [?] Fix off-by-one in PushBlock that causes nil dereference panic (#2924)

## Summary
Severity: Unknown
Chain: Sei
Component: sei-protocol/sei-chain
Published: 2026-02-20
Source: https://github.com/sei-protocol/sei-chain/commit/933111a74ee921e7ea8ccc915c7cea337b5cd052
Type: security-commit

## Details
Fix off-by-one in PushBlock that causes nil dereference panic (#2924)

## Summary

- **Fix off-by-one in `PushBlock`**: The `WaitUntil` condition used `n
<= inner.nextQC`, which allows `PushBlock` to proceed when `n ==
nextQC`. Since `inner.qcs` stores entries for the half-open range
`[first, nextQC)`, the map lookup returns `nil`, and the subsequent
`qc.Headers()` call panics with a nil pointer dereference. Changed to `n
< inner.nextQC` to match every other waiter in the file (`QC`, `Block`,
`GlobalBlock`, `AppProposal`).

---------

Co-authored-by: Cursor <cursoragent@cursor.com>
Co-authored-by: Masih H. Derkani <m@derkani.org>
