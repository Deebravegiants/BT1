# [?] fix race condition

## Summary
Severity: Unknown
Chain: Arbitrum
Component: OffchainLabs/nitro
Published: 2025-02-27
Source: https://github.com/OffchainLabs/nitro/commit/2dfaa9257202f1f2c9370bcb09537ca005519ccf
Type: security-commit

## Details
fix race condition

## Patch
### staker/block_validator.go
```diff
@@ -96,7 +96,8 @@ type BlockValidator struct {
 	pendingWasmModuleRoot common.Hash
 
 	// for testing only
-	testingProgressMadeChan chan struct{}
+	testingProgressMadeChan  chan struct{}
+	testingProgressMadeMutex sync.Mutex
 
 	// For troubleshooting failed validations
 	validationInputsWriter *inputs.Writer
@@ -862,9 +863,12 @@ validationsLoop:
 			v.validations.Delete(pos)
 			nonBlockingTrigger(v.createNodesChan)
 			nonBlockingTrigger(v.sendRecordChan)
+			v.testingProgressMadeMutex.Lock()
 			if v.testingProgressMadeChan != nil {
 				nonBlockingTrigger(v.testingProgressMadeChan)
 			}
+			v.testingProgressMadeMutex.Unlock()
+
 			log.Trace("result validated", "count", v.validated(), "blockHash", v.lastValidGS.BlockHash)
 			continue
 		}
@@ -1374,7 +1378,9 @@ func (v *BlockValidator) StopAndWait() {
 // WaitForPos can only be used from One thread
 func (v *BlockValidator) WaitForPos(t *testing.T, ctx context.Context, pos arbutil.MessageIndex, timeout time.Duration) bool {
 	triggerchan := make(chan struct{})
+	v.testingProgressMadeMutex.Lock()
 	v.testingProgressMadeChan = triggerchan
+	v.testingProgressMadeMutex.Unlock()
 	timer := time.NewTimer(timeout)
 	defer timer.Stop()
 	lastLoop := false
```
