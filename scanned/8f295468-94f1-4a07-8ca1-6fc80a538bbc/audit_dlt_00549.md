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

## Fix

- Extract a clamped `clampProgress` helper so `processed`/`total` can
never underflow, and route **both** the Execution and Beacon History log
branches through it.
- Add `historyDownloadProgress` which additionally caps the ETA so the
`time.Duration` (int64 ns) multiplication can't overflow.

## Tests

Added `TestHistoryDownloadProgress_*` and `TestClampProgress`. The
reproduction test fails on the old code with the exact reported
denominator (`18446744073709427663`) and passes with the fix.

## Backport

Will cherry-pick to `release/3.5` (the branch the reporter is on).

### cl/phase1/stages/stage_history_download.go
```diff
@@ -33,6 +33,7 @@ import (
 	"github.com/erigontech/erigon/cl/phase1/execution_client/block_collector"
 	"github.com/erigontech/erigon/cl/phase1/forkchoice"
 	"github.com/erigontech/erigon/cl/phase1/network"
+	"github.com/erigontech/erigon/cl/utils"
 	"github.com/erigontech/erigon/common"
 	"github.com/erigontech/erigon/common/log/v3"
 	"github.com/erigontech/erigon/db/kv"
@@ -100,6 +101,19 @@ func elBackfillFinished(slot, elBlock, destinationSlot, destinationBlock uint64)
 	return false
 }
 
+// clampProgress derives (processed, total) for a backwards download, guarding the
+// unsigned subtractions against underflow when the floor and current counters
+// drift past the frozen highestBlockSeen. total grows to at least processed so a
+// backfill continuing below the floor estimate keeps advancing while the display
+// stays within 100%.
+func clampProgress(highestBlockSeen, floor, current uint64) (processed, total uint64) {
+	current = min(current, highestBlockSeen)
+	floor = min(floor, highestBlockSeen)
+	processed = highestBlockSeen - current
+	total = max(highestBlockSeen-floor, processed)
+	return
+}
+
 // SpawnStageBeaconsForward spawn the beacon forward stage
 func SpawnStageHistoryDownload(cfg StageHistoryReconstructionCfg, ctx context.Context, logger log.Logger) error {
 	// Wait for execution engine to be ready.
@@ -343,26 +357,16 @@ func SpawnStageHistoryDownload(cfg StageHistoryReconstructionCfg, ctx context.Co
 				logger.Debug(logMsg, logArgs...)
 
 				if !isDownloadingForBeacon {
-					// Genesis block (0) is never collected, so the lowest reachable
-					// EL block number is 1. Clamp to avoid an off-by-one that makes
-					// progress stall at N-1/N.
-					effectiveLowest := max(lowestBlockToReach, 1)
-					toprocess := highestBlockSeen - effectiveLowest
-					processed := highestBlockSeen - uint64(currEth1Progress.Load())
-					remaining := float64(toprocess - processed)
+					// Genesis block (0) is never collected, so the lowest reachable EL block is 1.
+					processed, toprocess := clampProgress(highestBlockSeen, max(lowestBlockToReach, 1), uint64(currEth1Progress.Load()))
 					log.Info("Downloading Execution History", "progress",
 						fmt.Sprintf("%d/%d", processed, toprocess),
-						"ETA", (time.Duration(remaining/speed) * time.Second).String(),
+						"ETA", utils.ETA(toprocess-processed, speed),
 						"blk/sec", fmt.Sprintf("%.1f", speed))
 				} else {
-					// Beacon history downloads backward; lowestBlockToReach (the CL
-					// snapshot boundary) is only an estimate of the floor — a full or
-					// archive backfill keeps going below it toward genesis. Clamp the
-					// total to the work done so the X/Y display never runs past 100%.
-					beaconDone := highestBlockSeen - currProgress
-					beaconTotal := max(highestBlockSeen-lowestBlockToReach, beaconDone)
+					processed, toprocess := clampProgress(highestBlockSeen, lowestBlockToReach, currProgress)
 					log.Info("Downloading Beacon History", "progress",
-						fmt.Sprintf("%d/%d", beaconDone, beaconTotal),
+						fmt.Sprintf("%d/%d", processed, toprocess),
 						"blk/sec", fmt.Sprintf("%.1f", speed))
 				}
 				// More UX-friendly logging
```

### cl/phase1/stages/stage_history_download_test.go
```diff
@@ -21,6 +21,36 @@ import (
 	"testing"
 )
 
+// clampProgress must never report a total below processed nor underflow, even
+// when the floor and current counters drift past the frozen highestBlockSeen.
+// The last case mirrors the field report where the live EL head advanced past
+// the frozen top and previously underflowed the denominator to ~2^64.
+func TestClampProgress(t *testing.T) {
+	cases := []struct {
+		name                     string
+		highest, floor, current  uint64
+		wantProcessed, wantTotal uint64
+	}{
+		{"normal", 100, 20, 60, 40, 80},
+		{"floor above top", 100, 150, 60, 40, 40},
+		{"current above top", 100, 20, 200, 0, 80},
+		{"current below floor grows total", 100, 20, 5, 95, 95},
+		{"el head past frozen tip", 23_000_000, 23_123_953, 22_983_559, 16_441, 16_441},
+	}
+	for _, tc := range cases {
+		t.Run(tc.name, func(t *testing.T) {
+			processed, total := clampProgress(tc.highest, tc.floor, tc.current)
+			if processed != tc.wantProcessed || total != tc.wantTotal {
+				t.Fatalf("clampProgress(%d,%d,%d) = (%d,%d), want (%d,%d)",
+					tc.highest, tc.floor, tc.current, processed, total, tc.wantProcessed, tc.wantTotal)
+			}
+			if processed > total {
+				t.Fatalf("processed (%d) exceeds total (%d)", processed, total)
+			}
+		})
+	}
+}
+
 // Post-merge the EL block number exceeds the beacon slot, so a snapshot-gap
 // floor must be compared against EL block progress, not the slot.
 func TestELBackfillFinished_GapUsesBlockNotSlot(t *testing.T) {
```
