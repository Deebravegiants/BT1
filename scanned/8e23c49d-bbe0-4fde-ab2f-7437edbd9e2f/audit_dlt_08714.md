# [?] Fix panic in sync-till-block option

## Summary
Severity: Unknown
Chain: Arbitrum
Component: OffchainLabs/nitro
Published: 2025-04-09
Source: https://github.com/OffchainLabs/nitro/commit/4843f24f7d14b5084fd0074e6654334539f1f599
Type: security-commit

## Details
Fix panic in sync-till-block option

## Patch
### execution/gethexec/executionengine.go
```diff
@@ -655,7 +655,7 @@ func (s *ExecutionEngine) SequenceDelayedMessage(message *arbostypes.L1IncomingM
 }
 
 func (s *ExecutionEngine) sequenceDelayedMessageWithBlockMutex(message *arbostypes.L1IncomingMessage, delayedMsgIdx uint64) (*types.Block, error) {
-	if s.syncTillBlock > 0 && s.latestBlock.NumberU64() >= s.syncTillBlock {
+	if s.syncTillBlock > 0 && s.latestBlock != nil && s.latestBlock.NumberU64() >= s.syncTillBlock {
 		return nil, ExecutionEngineBlockCreationStopped
 	}
 	currentHeader, err := s.getCurrentHeader()
@@ -1031,7 +1031,7 @@ func (s *ExecutionEngine) Start(ctx_in context.Context) {
 	s.StopWaiter.Start(ctx_in, s)
 	s.LaunchThread(func(ctx context.Context) {
 		for {
-			if s.syncTillBlock > 0 && s.latestBlock.NumberU64() >= s.syncTillBlock {
+			if s.syncTillBlock > 0 && s.latestBlock != nil && s.latestBlock.NumberU64() >= s.syncTillBlock {
 				log.Info("stopping block creation in execution engine", "syncTillBlock", s.syncTillBlock)
 				return
 			}
```
