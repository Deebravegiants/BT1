# [?] fix state sync eta overflow (#565)

## Summary
Severity: Unknown
Chain: Avalanche
Component: ava-labs/avalanchego
Published: 2024-05-30
Source: https://github.com/ava-labs/avalanchego/commit/dbc0b27d15f35350f26859fd6c38c72fa7a96b5a
Type: security-commit

## Details
fix state sync eta overflow (#565)

* add UT

* use max

* fix test

* use EstimateETA

## Patch
### sync/statesync/trie_sync_stats.go
```diff
@@ -9,6 +9,7 @@ import (
 	"time"
 
 	utils_math "github.com/ava-labs/avalanchego/utils/math"
+	"github.com/ava-labs/avalanchego/utils/timer"
 	"github.com/ava-labs/coreth/metrics"
 	"github.com/ethereum/go-ethereum/common"
 	"github.com/ethereum/go-ethereum/log"
@@ -114,7 +115,7 @@ func (t *trieSyncStats) trieDone(root common.Hash) {
 // updateETA calculates and logs and ETA based on the number of leafs
 // currently in progress and the number of tries remaining.
 // assumes lock is held.
-func (t *trieSyncStats) updateETA(sinceUpdate time.Duration, now time.Time) {
+func (t *trieSyncStats) updateETA(sinceUpdate time.Duration, now time.Time) time.Duration {
 	leafsRate := float64(t.leafsSinceUpdate) / sinceUpdate.Seconds()
 	if t.leafsRate == nil {
 		t.leafsRate = utils_math.NewAverager(leafsRate, leafRateHalfLife, now)
@@ -128,15 +129,17 @@ func (t *trieSyncStats) updateETA(sinceUpdate time.Duration, now time.Time) {
 		// provide a separate ETA for the account trie syncing step since we
 		// don't know the total number of storage tries yet.
 		log.Info("state sync: syncing account trie", "ETA", roundETA(leafsTime))
-		return
+		return leafsTime
 	}
 
-	triesTime := now.Sub(t.triesStartTime) * time.Duration(t.triesRemaining) / time.Duration(t.triesSynced)
+	triesTime := timer.EstimateETA(t.triesStartTime, uint64(t.triesSynced), uint64(t.triesSynced+t.triesRemaining))
+	eta := max(leafsTime, triesTime)
 	log.Info(
 		"state sync: syncing storage tries",
 		"triesRemaining", t.triesRemaining,
-		"ETA", roundETA(leafsTime+triesTime), // TODO: should we use max instead of sum?
+		"ETA", roundETA(eta),
 	)
+	return eta
 }
 
 func (t *trieSyncStats) setTriesRemaining(triesRemaining int) {
```

### sync/statesync/trie_sync_stats_test.go
```diff
@@ -0,0 +1,26 @@
+// (c) 2024, Ava Labs, Inc. All rights reserved.
+// See the file LICENSE for licensing terms.
+
+package statesync
+
+import (
+	"testing"
+	"time"
+
+	"github.com/ava-labs/coreth/metrics"
+	"github.com/stretchr/testify/require"
+)
+
+func TestETAShouldNotOverflow(t *testing.T) {
+	require := require.New(t)
+	now := time.Now()
+	start := now.Add(-6 * time.Hour)
+
+	stats := &trieSyncStats{
+		triesStartTime: start,
+		triesSynced:    100_000,
+		triesRemaining: 450_000,
+		leafsRateGauge: metrics.NilGauge{},
+	}
+	require.Positive(stats.updateETA(time.Minute, now))
+}
```
