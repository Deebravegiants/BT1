# [?] cl/phase1/stages: guard forward-sync progress log against under/overflow (#22464)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-07-16
Source: https://github.com/erigontech/erigon/commit/b3ae698d1189eb6eac2cbd7b9b83a6c2d4f7ff57
Type: security-commit

## Details
cl/phase1/stages: guard forward-sync progress log against under/overflow (#22464)

## Problem

Follow-up to #22461 (issue #22455). The "[Caplin] Forward Sync" progress
log uses the same unguarded arithmetic pattern that produced the garbage
`Downloading Execution History` log:

```go
progressMade := chainTipSlot - currentSlot.Load()
distFromChainTip := time.Duration(progressMade*cfg.beaconCfg.SecondsPerSlot) * time.Second
timeProgress := currentSlot.Load() - prevProgress
estimatedTimeRemaining := 999 * time.Hour
if timeProgress > 0 {
    estimatedTimeRemaining = time.Duration(float64(progressMade)/(float64(currentSlot.Load()-prevProgress)/float64(secsPerLog))) * time.Second
}
if distFromChainTip < 0 || estimatedTimeRemaining < 0 {
    continue
}
```

Three latent issues:
- `chainTipSlot - currentSlot` underflows to ~2⁶⁴ when the current slot
overshoots the captured tip.
- `currentSlot - prevProgress` underflows on a reorg (current slot dips
below the previous sample), so the `> 0` guard passes with a garbage
denominator.
- Both feed `time.Duration(...) * time.Second`, which overflows `int64`
nanoseconds. The existing `< 0` guard only catches a wrap to
**negative** — an underflow that wraps back to **positive** still logs a
garbage distance/ETA (same failure mode as the `+318118h` seen in
#22455).

Lower severity than #22461 (in normal forward sync `currentSlot <=
chainTipSlot` and slots advance monotonically), but the same class of
latent bug.

## Fix

_Trimmed to 38 lines — full report: https://github.com/erigontech/erigon/commit/b3ae698d1189eb6eac2cbd7b9b83a6c2d4f7ff57_
