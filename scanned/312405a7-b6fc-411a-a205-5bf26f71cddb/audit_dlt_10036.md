# [?] fix a possible underflow on getPruningHandler

## Summary
Severity: Unknown
Chain: MultiversX
Component: multiversx/mx-chain-go
Published: 2026-07-13
Source: https://github.com/multiversx/mx-chain-go/commit/222d301f5873d4e0f263da68be423ff1d2a28a35
Type: security-commit

## Details
fix a possible underflow on getPruningHandler

## Patch
### process/block/baseProcess.go
```diff
@@ -2449,7 +2449,7 @@ func (bp *baseProcessor) PruneStateOnRollback(currHeader data.HeaderHandler, cur
 }
 
 func (bp *baseProcessor) getPruningHandler(finalHeaderNonce uint64) state.PruningHandler {
-	if finalHeaderNonce-bp.lastRestartNonce <= uint64(bp.pruningDelay) {
+	if finalHeaderNonce < bp.lastRestartNonce || finalHeaderNonce-bp.lastRestartNonce <= uint64(bp.pruningDelay) {
 		log.Debug("will skip pruning",
 			"finalHeaderNonce", finalHeaderNonce,
 			"last restart nonce", bp.lastRestartNonce,
```

### process/block/baseProcess_test.go
```diff
@@ -3810,6 +3810,10 @@ func TestBaseProcessor_getPruningHandler(t *testing.T) {
 	ph = bp.GetPruningHandler(14)
 	assert.True(t, ph.IsPruningEnabled())
 
+	bp.SetLastRestartNonce(15)
+	ph = bp.GetPruningHandler(14)
+	assert.False(t, ph.IsPruningEnabled())
+
 	bp.SetClosingNodeStarted(true)
 	ph = bp.GetPruningHandler(14)
 	assert.False(t, ph.IsPruningEnabled())
```
