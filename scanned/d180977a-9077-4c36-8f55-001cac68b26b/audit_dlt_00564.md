# [?] execution/stagedsync: fix parallel-exec "limit" log underflow (#21953)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-06-25
Source: https://github.com/erigontech/erigon/commit/5da12f53f9ddca51134cfa886d356d27e4683c97
Type: security-commit

## Details
execution/stagedsync: fix parallel-exec "limit" log underflow (#21953)

## Problem

The `parallel starting` log line prints a garbage `limit`:

```
[6/8 Execution] parallel starting from=0 to=21715999 limit=18446744073709551615 ...
```

`18446744073709551615` is `math.MaxUint64`: the log computed `limit` as
`startBlockNum+blockLimit-1`, which underflows when `blockLimit == 0`
(the "no per-cycle limit" case — e.g. `integration stage_exec` from
block 0, where `LoopBlockLimit` is 0).

## Fix

Log the effective last block of the cycle:
- `maxBlockNum` when there's no per-cycle limit (`blockLimit == 0`),
- otherwise `min(startBlockNum+blockLimit-1, maxBlockNum)`.

This mirrors how the serial path already computes `toBlockNum`
(`exec3_serial.go`). Log-only change — execution behavior is unaffected.

Now logs:
```
[6/8 Execution] parallel starting from=0 to=21715999 limit=21715999 ...
```
