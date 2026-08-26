# [?] fix(txpool): remove double PopWorst() in pending pool overflow (#18132)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2025-12-04
Source: https://github.com/erigontech/erigon/commit/624d8479417831e929fe01a1ee5a1b6fa03a9bad
Type: security-commit

## Details
fix(txpool): remove double PopWorst() in pending pool overflow (#18132)

PopWorst() called twice per loop iteration when pending pool exceeds
limit.
First tx leaks, second gets discarded. Copy-paste mistake from
diagnostics commit 53dc6c7e977 - baseFee and queued were fixed to use tx
variable, pending was missed.
