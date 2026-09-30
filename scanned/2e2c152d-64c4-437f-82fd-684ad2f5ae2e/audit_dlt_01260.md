# [?] execution: fix potential limitedBigJump calc uint underflow in updateForkChoice (#15746)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2025-06-25
Source: https://github.com/erigontech/erigon/commit/29378d42dfb874d88bf91ce84b924b47253ff13e
Type: security-commit

## Details
execution: fix potential limitedBigJump calc uint underflow in updateForkChoice (#15746)

protects the `limitedBigJump` calculation from a uint64 underflow 

e.g. there can be cases (for example on chains like bor) where the ufc
header number is a few blocks less than the previous exec progress from
the last ufc - if we are on block 10 on fork A but then block 9 on fork
B appears with higher difficulty

such an underflow can cause limitedBigJump to be set to `true` which
then sets `IsInitialCycle=true` potentially causing furious/aggressive
prunes on chain tip

## Patch
### execution/eth1/forkchoice.go
```diff
@@ -277,13 +277,16 @@ func (e *EthereumExecutionModule) updateForkChoice(ctx context.Context, original
 	metrics.UpdateBlockConsumerPreExecutionDelay(fcuHeader.Time, fcuHeader.Number.Uint64(), e.logger)
 	defer metrics.UpdateBlockConsumerPostExecutionDelay(fcuHeader.Time, fcuHeader.Number.Uint64(), e.logger)
 
-	limitedBigJump := e.syncCfg.LoopBlockLimit > 0 && finishProgressBefore > 0 && fcuHeader.Number.Uint64()-finishProgressBefore > uint64(e.syncCfg.LoopBlockLimit-2)
-	isSynced := finishProgressBefore > 0 && finishProgressBefore > e.blockReader.FrozenBlocks() && finishProgressBefore == headersProgressBefore
-	if limitedBigJump {
-		isSynced = false
-		log.Info("[sync] limited big jump", "from", finishProgressBefore, "amount", uint64(e.syncCfg.LoopBlockLimit))
+	var limitedBigJump bool
+	if e.syncCfg.LoopBlockLimit > 0 && finishProgressBefore > 0 && fcuHeader.Number.Uint64() > finishProgressBefore {
+		// note fcuHeader.Number.Uint64() may be < finishProgressBefore - protect from underflow by checking it is >
+		extraPadding := uint64(2)
+		limitedBigJump = (fcuHeader.Number.Uint64()-finishProgressBefore)+extraPadding > uint64(e.syncCfg.LoopBlockLimit)
+		e.logger.Info("[sync] limited big jump", "from", finishProgressBefore, "to", fcuHeader.Number.Uint64(), "amount", uint64(e.syncCfg.LoopBlockLimit), "padding", extraPadding)
 	}
 
+	isSynced := !limitedBigJump && finishProgressBefore > 0 && finishProgressBefore > e.blockReader.FrozenBlocks() && finishProgressBefore == headersProgressBefore
+
 	canonicalHash, err := e.canonicalHash(ctx, tx, fcuHeader.Number.Uint64())
 	if err != nil {
 		sendForkchoiceErrorWithoutWaiting(e.logger, outcomeCh, err, false)
```
