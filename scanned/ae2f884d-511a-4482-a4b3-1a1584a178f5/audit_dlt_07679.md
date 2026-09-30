# [?] Fix crash when last receipt is not available (#14247)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2025-03-21
Source: https://github.com/erigontech/erigon/commit/09bba77c9b5f1533788e652eb62a91442f22942d
Type: security-commit

## Details
Fix crash when last receipt is not available (#14247)

Fixes #14234

This fixes the crash, pending investigation on why the last receipt was
unavailable.

## Patch
### eth/stagedsync/exec3_serial.go
```diff
@@ -115,6 +115,7 @@ func (se *serialExecutor) execute(ctx context.Context, tasks []*state.TxTask) (c
 		if !txTask.Final {
 			var receipt *types.Receipt
 			if txTask.TxIndex >= 0 {
+				log.Info("writing log for txIndex %d", txTask.TxIndex)
 				receipt = txTask.BlockReceipts[txTask.TxIndex]
 			}
 			if err := rawtemporaldb.AppendReceipt(se.doms, receipt, se.blobGasUsed); err != nil {
@@ -124,6 +125,9 @@ func (se *serialExecutor) execute(ctx context.Context, tasks []*state.TxTask) (c
 			if se.cfg.chainConfig.Bor != nil && txTask.TxIndex >= 1 {
 				// get last receipt and store the last log index + 1
 				lastReceipt := txTask.BlockReceipts[txTask.TxIndex-1]
+				if lastReceipt == nil {
+					return false, fmt.Errorf("receipt is nil but should be populated, txIndex=%d, block=%d", txTask.TxIndex-1, txTask.BlockNum)
+				}
 				if len(lastReceipt.Logs) > 0 {
 					firstIndex := lastReceipt.Logs[len(lastReceipt.Logs)-1].Index + 1
 					receipt := types.Receipt{
```

### eth/stagedsync/stage_custom_trace.go
```diff
@@ -297,6 +297,9 @@ func customTraceBatch(ctx context.Context, cfg *exec3.ExecArgs, tx kv.TemporalRw
 				if cfg.ChainConfig.Bor != nil && txTask.TxIndex >= 1 {
 					// get last receipt and store the last log index + 1
 					lastReceipt := txTask.BlockReceipts[txTask.TxIndex-1]
+					if lastReceipt == nil {
+						return fmt.Errorf("receipt is nil but should be populated, txIndex=%d, block=%d", txTask.TxIndex-1, txTask.BlockNum)
+					}
 					if len(lastReceipt.Logs) > 0 {
 						firstIndex := lastReceipt.Logs[len(lastReceipt.Logs)-1].Index + 1
 						receipt := types.Receipt{
```
