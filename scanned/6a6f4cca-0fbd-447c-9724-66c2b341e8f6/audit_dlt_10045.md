# [?] add new test case and fix race condition

## Summary
Severity: Unknown
Chain: MultiversX
Component: multiversx/mx-chain-go
Published: 2026-02-24
Source: https://github.com/multiversx/mx-chain-go/commit/0cbe5a458c9764b5a3de7b349b71e8913cb450dc
Type: security-commit

## Details
add new test case and fix race condition

## Patch
### process/block/baseProcess.go
```diff
@@ -2262,7 +2262,7 @@ func (bp *baseProcessor) getPruningHandler(finalHeaderNonce uint64) state.Prunin
 		return state.NewPruningHandler(state.DisableDataRemoval)
 	}
 
-	if bp.closingNodeStarted.Load() == true {
+	if bp.closingNodeStarted.Load() {
 		log.Debug("will skip pruning as closing node already started",
 			"finalHeaderNonce", finalHeaderNonce,
 		)
```

### process/block/baseProcess_test.go
```diff
@@ -3484,6 +3484,10 @@ func TestBaseProcessor_getPruningHandler(t *testing.T) {
 	bp.SetLastRestartNonce(1)
 	ph = bp.GetPruningHandler(14)
 	assert.True(t, ph.IsPruningEnabled())
+
+	bp.SetClosingNodeStarted(true)
+	ph = bp.GetPruningHandler(14)
+	assert.False(t, ph.IsPruningEnabled())
 }
 
 func TestBaseProcessor_getPruningHandlerSetsDefaulPruningDelay(t *testing.T) {
```

### process/block/export_test.go
```diff
@@ -94,6 +94,11 @@ func (bp *baseProcessor) GetPruningHandler(finalHeaderNonce uint64) state.Prunin
 	return bp.getPruningHandler(finalHeaderNonce)
 }
 
+// SetClosingNodeStarted -
+func (bp *baseProcessor) SetClosingNodeStarted(val bool) {
+	bp.closingNodeStarted.Store(val)
+}
+
 // SetLastRestartNonce -
 func (bp *baseProcessor) SetLastRestartNonce(lastRestartNonce uint64) {
 	bp.lastRestartNonce = lastRestartNonce
```

### process/mock/coreComponentsMock.go
```diff
@@ -1,6 +1,7 @@
 package mock
 
 import (
+	"sync"
 	"sync/atomic"
 
 	"github.com/multiversx/mx-chain-core-go/core"
@@ -52,6 +53,7 @@ type CoreComponentsMock struct {
 	CommonConfigsHandlerField          common.CommonConfigsHandler
 	SyncTimerField                     ntp.SyncTimer
 	AntifloodConfigsHandlerField       common.AntifloodConfigsHandler
+	mut                                sync.RWMutex
 	ClosingNodeStartedField            *atomic.Bool
 }
 
@@ -234,6 +236,9 @@ func (ccm *CoreComponentsMock) AntifloodConfigsHandler() common.AntifloodConfigs
 
 // ClosingNodeStarted -
 func (ccm *CoreComponentsMock) ClosingNodeStarted() *atomic.Bool {
+	ccm.mut.Lock()
+	defer ccm.mut.Unlock()
+
 	if ccm.ClosingNodeStartedField == nil {
 		ccm.ClosingNodeStartedField = &atomic.Bool{}
 	}
```
