# [?] [SharovBot] fix: data race on DelayLoggingEnabled - use atomic.Bool (#23107)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-08-07
Source: https://github.com/erigontech/erigon/commit/ede5bb0853a3cbf0e4f28015875af48aa41bf95a
Type: security-commit

## Details
[SharovBot] fix: data race on DelayLoggingEnabled - use atomic.Bool (#23107)

**[SharovBot]**

## Problem

DATA RACE detected in TestImportClosesChaindataOnInitError (CI run:
https://github.com/erigontech/erigon/actions/runs/31190048942/job/92904328219):

Two goroutines concurrently access the global DelayLoggingEnabled bool
variable:
- Writer: SetupLoggerCtx() sets it from the CLI flag
(node/logging/logging.go:68)
- Reader: UpdateBlockConsumer*Delay() functions read it on every block
event (execution/metrics/block.go:80)

## Fix

Replace the plain bool with sync/atomic.Bool:
- All reads use .Load()
- The single write uses .Store()

No behavior change — atomic.Bool zero-value is false, same as before.

## Testing

- go vet ./execution/metrics/... ./node/logging/... passes
- No test files modified

Co-authored-by: SharovBot <sharovbot@erigon.ci>
Co-authored-by: Giulio Rebuffo <giulio.rebuffo@gmail.com>

## Patch
### execution/metrics/block.go
```diff
@@ -17,6 +17,7 @@
 package metrics
 
 import (
+	"sync/atomic"
 	"time"
 
 	"github.com/erigontech/erigon/common/log/v3"
@@ -26,7 +27,7 @@ import (
 var (
 	delayBuckets = []float64{0.05, 0.125, 0.25, 0.5, 1, 2, 4, 8}
 
-	DelayLoggingEnabled bool
+	DelayLoggingEnabled atomic.Bool
 
 	BlockConsumerHeaderDownloadDelay = diagmetrics.NewSummary(`block_consumer_delay{type="header_download"}`)
 	BlockConsumerBodyDownloadDelay   = diagmetrics.NewSummary(`block_consumer_delay{type="body_download"}`)
@@ -47,7 +48,7 @@ func UpdateBlockConsumerHeaderDownloadDelay(blockTime uint64, blockNumber uint64
 	BlockConsumerHeaderDownloadDelay.ObserveDuration(t)
 	BlockConsumerHeaderDownloadDelayHistogram.ObserveDuration(t)
 
-	if DelayLoggingEnabled {
+	if DelayLoggingEnabled.Load() {
 		log.Info("[consumer-delay] Header", "blockNumber", blockNumber, "delay", time.Since(t))
 	}
 }
@@ -57,7 +58,7 @@ func UpdateBlockConsumerBodyDownloadDelay(blockTime uint64, blockNumber uint64,
 	BlockConsumerBodyDownloadDelay.ObserveDuration(t)
 	BlockConsumerBodyDownloadDelayHistogram.ObserveDuration(t)
 
-	if DelayLoggingEnabled {
+	if DelayLoggingEnabled.Load() {
 		log.Info("[consumer-delay] Body", "blockNumber", blockNumber, "delay", time.Since(t))
 	}
 }
@@ -67,7 +68,7 @@ func UpdateBlockConsumerPreExecutionDelay(blockTime uint64, blockNumber uint64,
 	BlockConsumerPreExecutionDelay.ObserveDuration(t)
 	BlockConsumerPreExecutionDelayHistogram.ObserveDuration(t)
 
-	if DelayLoggingEnabled {
+	if DelayLoggingEnabled.Load() {
 		log.Info("[consumer-delay] Pre-execution", "blockNumber", blockNumber, "delay", time.Since(t))
 	}
 }
@@ -77,7 +78,7 @@ func UpdateBlockConsumerPostExecutionDelay(blockTime uint64, blockNumber uint64,
 	BlockConsumerPostExecutionDelay.ObserveDuration(t)
 	BlockConsumerPostExecutionDelayHistogram.ObserveDuration(t)
 
-	if DelayLoggingEnabled {
+	if DelayLoggingEnabled.Load() {
 		log.Info("[consumer-delay] Post-execution", "blockNumber", blockNumber, "delay", time.Since(t))
 	}
 }
@@ -86,7 +87,7 @@ func UpdateBlockProducerProductionDelay(parentBlockTime uint64, producedBlockNum
 	t := time.Unix(int64(parentBlockTime), 0)
 	BlockProducerProductionDelay.ObserveDuration(t)
 
-	if DelayLoggingEnabled {
+	if DelayLoggingEnabled.Load() {
 		log.Info("[producer-delay] Production", "blockNumber", producedBlockNum, "delay", time.Since(t))
 	}
 }
```

### node/logging/logging.go
```diff
@@ -65,7 +65,7 @@ func SetupLoggerCtx(
 	var consoleJson = ctx.Bool(LogJsonFlag.Name) || ctx.Bool(LogConsoleJsonFlag.Name)
 	var dirJson = ctx.Bool(LogDirJsonFlag.Name)
 
-	metrics.DelayLoggingEnabled = ctx.Bool(LogBlockDelayFlag.Name)
+	metrics.DelayLoggingEnabled.Store(ctx.Bool(LogBlockDelayFlag.Name))
 
 	consoleLevel := consoleDefaultLevel
 
```
