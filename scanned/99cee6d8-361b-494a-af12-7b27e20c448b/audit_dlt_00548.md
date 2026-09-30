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

Extract `forwardSyncProgress` (clamps both slot differences) and
`boundedDuration` (saturates instead of overflowing the
`time.Duration`), and drop the now-unnecessary `< 0` guard.

## Tests

`forward_sync_test.go` covers the overshoot, the
reorg-below-prev-progress case, a normal case, and the duration
saturation. The overshoot/reorg tests fail on the old code.

## Backport

Will cherry-pick to `release/3.5`.

---------

Co-authored-by: Alex Sharov <AskAlexSharov@gmail.com>

### cl/phase1/stages/forward_sync.go
```diff
@@ -19,6 +19,7 @@ import (
 	"github.com/erigontech/erigon/cl/phase1/execution_client"
 	"github.com/erigontech/erigon/cl/phase1/forkchoice"
 	network2 "github.com/erigontech/erigon/cl/phase1/network"
+	"github.com/erigontech/erigon/cl/utils"
 	"github.com/erigontech/erigon/cl/utils/bls"
 	"github.com/erigontech/erigon/common"
 	"github.com/erigontech/erigon/common/hexutil"
@@ -265,6 +266,20 @@ func processDownloadedBlockBatches(ctx context.Context, logger log.Logger, cfg *
 	return
 }
 
+// forwardSyncProgress returns the slots still to sync and the observed sync rate
+// in slots/sec. currentSlot can overshoot chainTipSlot and dip below prevProgress
+// on reorgs, so both differences are clamped to keep the unsigned math from
+// underflowing.
+func forwardSyncProgress(chainTipSlot, currentSlot, prevProgress uint64, secsPerLog int) (slotsRemaining uint64, ratePerSec float64) {
+	if chainTipSlot > currentSlot {
+		slotsRemaining = chainTipSlot - currentSlot
+	}
+	if currentSlot > prevProgress && secsPerLog > 0 {
+		ratePerSec = float64(currentSlot-prevProgress) / float64(secsPerLog)
+	}
+	return
+}
+
 // forwardSync (MAIN ROUTINE FOR ForwardSync) performs the forward synchronization of beacon blocks.
 func forwardSync(ctx context.Context, logger log.Logger, cfg *Cfg, args Args) error {
 	var (
@@ -370,18 +385,15 @@ func forwardSync(ctx context.Context, logger log.Logger, cfg *Cfg, args Args) er
 			return ctx.Err()
 		case <-logTicker.C:
 			// Log progress at regular intervals
-			progressMade := chainTipSlot - currentSlot.Load()
-			distFromChainTip := time.Duration(progressMade*cfg.beaconCfg.SecondsPerSlot) * time.Second
-			timeProgress := currentSlot.Load() - prevProgress
-			estimatedTimeRemaining := 999 * time.Hour
-			if timeProgress > 0 {
-				estimatedTimeRemaining = time.Duration(float64(progressMade)/(float64(currentSlot.Load()-prevProgress)/float64(secsPerLog))) * time.Second
-			}
-			if distFromChainTip < 0 || estimatedTimeRemaining < 0 {
-				continue
-			}
-			prevProgress = currentSlot.Load()
-			logger.Info("[Caplin] Forward Sync", "progress", currentSlot.Load(), "distance-from-chain-tip", distFromChainTip, "estimated-time-remaining", estimatedTimeRemaining)
+			cur := currentSlot.Load()
+			slotsRemaining, ratePerSec := forwardSyncProgress(chainTipSlot, cur, prevProgress, secsPerLog)
+			prevProgress = cur
+			// distance-from-chain-tip is the ETA at the chain's own production rate
+			// (one slot per SecondsPerSlot), which also saturates instead of overflowing.
+			chainRatePerSec := 1.0 / float64(cfg.beaconCfg.SecondsPerSlot)
+			logger.Info("[Caplin] Forward Sync", "progress", cur,
+				"distance-from-chain-tip", utils.ETA(slotsRemaining, chainRatePerSec),
+				"estimated-time-remaining", utils.ETA(slotsRemaining, ratePerSec))
 		default:
 		}
 	}
```

### cl/phase1/stages/forward_sync_test.go
```diff
@@ -0,0 +1,56 @@
+// Copyright 2024 The Erigon Authors
+// This file is part of Erigon.
+//
+// Erigon is free software: you can redistribute it and/or modify
+// it under the terms of the GNU Lesser General Public License as published by
+// the Free Software Foundation, either version 3 of the License, or
+// (at your option) any later version.
+//
+// Erigon is distributed in the hope that it will be useful,
+// but WITHOUT ANY WARRANTY; without even the implied warranty of
+// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
+// GNU Lesser General Public License for more details.
+//
+// You should have received a copy of the GNU Lesser General Public License
+// along with Erigon. If not, see <http://www.gnu.org/licenses/>.
+
+package stages
+
+import (
+	"testing"
+)
+
+// currentSlot can overshoot the captured chainTipSlot; slotsRemaining must clamp
+// to 0 rather than underflow into a ~2^64 slot count.
+func TestForwardSyncProgress_CurrentSlotPastChainTip(t *testing.T) {
+	slotsRemaining, ratePerSec := forwardSyncProgress(1_000_000, 1_000_050, 999_900, 30)
+	if slotsRemaining != 0 {
+		t.Fatalf("slotsRemaining = %d, want 0 when current slot is past the tip", slotsRemaining)
+	}
+	if ratePerSec < 0 {
+		t.Fatalf("ratePerSec must not be negative, got %g", ratePerSec)
+	}
+}
+
+// A reorg can drop currentSlot below prevProgress; the rate must clamp to 0
+// rather than underflow the slots-processed denominator.
+func TestForwardSyncProgress_ReorgBelowPrevProgress(t *testing.T) {
+	slotsRemaining, ratePerSec := forwardSyncProgress(1_000_000, 900_000, 950_000, 30)
+	if slotsRemaining != 100_000 {
+		t.Fatalf("slotsRemaining = %d, want 100000", slotsRemaining)
+	}
+	if ratePerSec != 0 {
+		t.Fatalf("ratePerSec = %g, want 0 when current slot is below prev progress", ratePerSec)
+	}
+}
+
+// Normal case: slotsRemaining is the tip gap, rate is slots processed per second.
+func TestForwardSyncProgress_Normal(t *testing.T) {
+	slotsRemaining, ratePerSec := forwardSyncProgress(1_000_000, 900_000, 899_700, 30)
+	if slotsRemaining != 100_000 {
+		t.Fatalf("slotsRemaining = %d, want 100000", slotsRemaining)
+	}
+	if ratePerSec != 10 { // (900000-899700)/30
+		t.Fatalf("ratePerSec = %g, want 10", ratePerSec)
+	}
+}
```
