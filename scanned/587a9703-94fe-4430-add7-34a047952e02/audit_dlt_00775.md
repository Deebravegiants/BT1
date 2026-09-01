# [?] Fix PebbleDB iterator stack overflow (#3823)

## Summary
Severity: Unknown
Chain: Sei
Component: sei-protocol/sei-chain
Published: 2026-07-29
Source: https://github.com/sei-protocol/sei-chain/commit/0b3eaf37aeb3a00aacdea8f8c7293cc25bdc9235
Type: security-commit

## Details
Fix PebbleDB iterator stack overflow (#3823)

## Summary

Fixes a node crash (`fatal error: stack overflow`) and a silent
wrong-results bug in the
legacy ascending-encoding MVCC iterator (`iterator_ascending.go`), used
by archive nodes
whose PebbleDB state store predates the descending-encoding migration.

Both bugs were already fixed for the descending iterator in #3513. This
applies the same
iterative design to the ascending path, which was missed.

## Bugs fixed

**1. Stack overflow.** `nextForward` / `nextReverse` called themselves
recursively once per
skipped key. A historical query that had to skip many keys (e.g. a
reverse scan at an old
version over a range dominated by newer writes) consumed one stack frame
per key until the
process died. Go cannot `recover()` from a stack overflow, so this took
down the whole node.

**2. Reverse iteration silently dropped keys.** When seeking backwards,
the iterator jumped
past *every* version of a key as soon as the version it landed on was
newer than the query
version — even if that key had an older version that *was* visible.
Affected keys were
missing from historical query results, with no error returned.

Minimal repro: write `keyA@5`, `keyB@30`, `keyA@100`, `keyB@200`, then
reverse-iterate at
version 50. Expected `keyB=B@30, keyA=A@5`; before this change only
`keyA=A@5` was returned.


_Trimmed to 38 lines — full report: https://github.com/sei-protocol/sei-chain/commit/0b3eaf37aeb3a00aacdea8f8c7293cc25bdc9235_
