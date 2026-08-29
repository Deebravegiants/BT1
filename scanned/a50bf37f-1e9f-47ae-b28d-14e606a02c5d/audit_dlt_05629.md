# [?] commitment: fix warmuper arena data race in HashSort (#21432)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-06-09
Source: https://github.com/erigontech/erigon/commit/c15f43363c28f091218ee3803d1992b6321f5c70
Type: security-commit

## Details
commitment: fix warmuper arena data race in HashSort (#21432)

## Problem

`HashSort` streams each batch's hashed/plain keys into a reused
`byteArena` bump buffer and hands every key to the async warmuper as a
sub-slice for MDBX prefetch. At each 10k batch boundary it reset that
single arena while warmup workers were still reading earlier keys — the
next batch's `arenaAlloc` overwrote bytes a worker was mid-read on. Data
race.

Latent on main: `HexToCompact` tolerates the garbage (at worst a wasted
prefetch). On nibblesv2 (#21146) `EncodeKeyV2` validates nibbles and
panics on the corrupted byte: `panic: nibbles v2: nibble at index 68 is
0xff`, mainnet ~blk 24.83M, mid commitment.

## Fix

Replace the single arena with a 2-slot ring (`arenaRingSize`) keyed by a
generation counter. Each warmed key is tagged with the current `gen`;
the warmuper keeps a per-slot in-flight count (`outstanding[gen %
ringSize]`). Before a batch boundary reuses a slot, the producer calls
`WaitBufferFree(slot)`, which blocks until that slot's
previous-generation warm items have drained — so no worker still
references the bytes about to be overwritten. Workers decrement on
completion and broadcast on drain-to-zero; a waker goroutine releases
any waiter on ctx cancellation.

Zero-copy, no per-key allocation: the arena is pre-sized once per batch
(`arenaEnsureCap`), and an over-capacity key falls back to an
independent allocation rather than reallocating the buffer (which would
invalidate live sub-slices). Wired at both `HashSort` batch boundaries
for `ModeDirect` and `ModeUpdate`; the `nil`-warmuper path is unchanged.

## Tests

- `TestHashSort_WarmupArenaNoRace` — `-race` repro; DATA RACE in
`HexToCompact` on the old single-arena wiring, green after. Covers

_Trimmed to 38 lines — full report: https://github.com/erigontech/erigon/commit/c15f43363c28f091218ee3803d1992b6321f5c70_
