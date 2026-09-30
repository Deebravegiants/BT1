# [?] fix(execution/builder): add panic recovery in block builder goroutine (#18417)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2025-12-23
Source: https://github.com/erigontech/erigon/commit/6f61c351ed37ee7de4b0e8fbe5da318344f4ed22
Type: security-commit

## Details
fix(execution/builder): add panic recovery in block builder goroutine (#18417)

Add panic recovery to prevent infinite deadlock in Stop() when build
function panics. Without this fix, a panic in build() leaves result and
err unset, causing Stop() to wait indefinitely in sync.Cond.Wait().

The fix converts panics to errors and ensures result/err are always set,
following Erigon's standard panic handling pattern.

## Patch
### execution/builder/block_builder.go
```diff
@@ -17,10 +17,12 @@
 package builder
 
 import (
+	"fmt"
 	"sync"
 	"sync/atomic"
 	"time"
 
+	"github.com/erigontech/erigon/common/dbg"
 	"github.com/erigontech/erigon/common/log/v3"
 	"github.com/erigontech/erigon/execution/types"
 )
@@ -42,21 +44,32 @@ func NewBlockBuilder(build BlockBuilderFunc, param *Parameters, maxBuildTimeSecs
 
 	go func() {
 		defer close(terminated)
+		var result *types.BlockWithReceipts
+		var err error
+
+		defer func() {
+			if rec := recover(); rec != nil {
+				err = fmt.Errorf("block builder panic: %+v, trace: %s", rec, dbg.Stack())
+				log.Warn("Block builder panicked", "err", err)
+				result = nil
+			}
+
+			builder.syncCond.L.Lock()
+			defer builder.syncCond.L.Unlock()
+			builder.result = result
+			builder.err = err
+			builder.syncCond.Broadcast()
+		}()
+
 		log.Info("Building block...")
 		t := time.Now()
-		result, err := build(param, &builder.interrupt)
+		result, err = build(param, &builder.interrupt)
 		if err != nil {
 			log.Warn("Failed to build a block", "err", err)
 		} else {
 			block := result.Block
 			log.Info("Built block", "hash", block.Hash(), "height", block.NumberU64(), "txs", len(block.Transactions()), "executionRequests", len(result.Requests), "gas used %", 100*float64(block.GasUsed())/float64(block.GasLimit()), "time", time.Since(t))
 		}
-
-		builder.syncCond.L.Lock()
-		defer builder.syncCond.L.Unlock()
-		builder.result = result
-		builder.err = err
-		builder.syncCond.Broadcast()
 	}()
 
 	go func() {
```
