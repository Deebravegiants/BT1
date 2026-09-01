# [?] cl/phase1/stages: fix uint64 underflow in history-download progress log (#22461)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-07-15
Source: https://github.com/erigontech/erigon/commit/8a591912af2d8749e2279f2355d369eb80a7d68a
Type: security-commit

## Details
cl/phase1/stages: fix uint64 underflow in history-download progress log (#22461)

## Problem

Fixes #22455. A user on 3.5.2 reported garbage progress/ETA logs:

```
[INFO] Downloading Execution History progress=16441/18446744073709427663 ETA=-2120675h43m6.2s blk/sec=12.9
[INFO] Downloading Execution History progress=17223/18446744073709427663 ETA=318118h37m52.5s  blk/sec=13.0
```

The denominator is a `uint64` underflow: `2^64 − 18446744073709427663 =
123953`.

## Root cause

In the "Downloading Execution History" branch the total is computed with
unguarded `uint64` subtraction:

```go
toprocess := highestBlockSeen - effectiveLowest   // highestBlockSeen = initialEth1Progress (frozen at start)
                                                  // effectiveLowest  = engine.CurrentHeader().Number (live EL head)
```

`highestBlockSeen` is frozen at the EL block number of the highest
beacon block seen when the backwards history download starts;
`lowestBlockToReach` tracks the **live** EL head, which keeps climbing
as the node follows the tip. Once the EL head advances past the frozen
start point, the subtraction underflows to ~2⁶⁴. That huge value then
feeds `time.Duration(remaining/speed) * time.Second`, overflowing
`int64` nanoseconds and producing the nonsensical (sign-flipping) ETA.

This is a pre-existing latent bug (the subtraction dates back to March
2025), not a regression from a recent change. It's logging-only — no
functional/consensus impact — which is why it went unnoticed and
untested. It surfaces on long-running nodes doing the persistent
background history download while following the chain tip.


_Trimmed to 38 lines — full report: https://github.com/erigontech/erigon/commit/8a591912af2d8749e2279f2355d369eb80a7d68a_
