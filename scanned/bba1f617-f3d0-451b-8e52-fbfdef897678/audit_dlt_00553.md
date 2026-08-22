# [?] common/race: fix darwin -race crashes from file mmaps in the TSAN heap window (#21611)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-07-09
Source: https://github.com/erigontech/erigon/commit/c9b6aed3971fbaf511e84d6076d9b86f16fe54a3
Type: security-commit

## Details
common/race: fix darwin -race crashes from file mmaps in the TSAN heap window (#21611)

## Problem

`go test -race` on darwin (Apple Silicon) flakily dies in mdbx-heavy
packages — reproduced at **6/6** on `main` with `EXEC3_PARALLEL=true go
test -race ./execution/execmodule ./execution/state` on an M-series Mac
— with either of:

```
fatal error: runtime: split stack overflow        (sigpanic → racecall, no DATA RACE report)
fatal error: too many address space collisions for -race mode
```

The same packages pass the Linux race CI legs, which long disguised this
as an environment flake. It isn't — both fatals share one root cause.

## Root cause (caught live in lldb)

Catching the original fault under lldb (before the Go runtime mangles it
into "split stack overflow") shows:

```
thread #26, stop reason = EXC_BAD_ACCESS (code=1, address=0x21882000bbb0)
  frame #0: __tsan_read + 44
  frame #2: txnprovider/txpool.(*TxPool).fromDB
(lldb) memory region `($x1 - 0x200000000000)/2`     ← app address for that shadow
[0x000000c410004000-0x000000c810000000) r--          ← a 16GiB mdbx data map
(lldb) memory region $x1                             ← its TSAN shadow
[0x21884800bbb0-0x219a00000000) ---                  ← unmapped
```

1. Go's race-mode heap lives in TSAN's Go/darwin window `[0x00c0…,
0x00e0…)`; shadow (`shadow = app*2 + 0x2000_0000_0000`) is mapped **per
heap arena**.
2. Each in-mem test env reserves a **16GiB** VA map (`InMem` geometry
upper bound); with dozens of parallel testers the kernel's bottom-up
placement exhausts low VA and drops mdbx maps **between Go heap

_Trimmed to 38 lines — full report: https://github.com/erigontech/erigon/commit/c9b6aed3971fbaf511e84d6076d9b86f16fe54a3_
