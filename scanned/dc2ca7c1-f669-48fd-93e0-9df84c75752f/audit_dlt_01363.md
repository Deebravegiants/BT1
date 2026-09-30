# [?] miner: fix deadlock and panic issues in block production (#1639)

## Summary
Severity: Unknown
Chain: Polygon
Component: maticnetwork/bor
Published: 2025-07-16
Source: https://github.com/0xPolygon/bor/commit/95d00c9b182f76011f59adc77924e94a53a7b99f
Type: security-commit

## Details
miner: fix deadlock and panic issues in block production (#1639)

- Skip stale sealed blocks that are behind current chain head to prevent
    resultLoop from attempting to write outdated blocks after reorgs
  - Add 1-second timeout to chDeps channel send to prevent indefinite
    blocking when receiver is dead or channel is full
  - Return error when transaction count exceeds dependency list length
    to prevent array index out of bounds panic

  These fixes address production issues where mining nodes would deadlock
  for hours after milestone-triggered reorgs, unable to
  process new blocks or respond to chain updates.

## Patch
### miner/worker.go
```diff
@@ -752,6 +752,13 @@ func (w *worker) resultLoop() {
 				continue
 			}
 
+			// Skip if the sealed block is behind current head (stale block from before reorg)
+			currentBlock := w.chain.CurrentBlock()
+			if currentBlock != nil && block.NumberU64() <= currentBlock.Number.Uint64() {
+				log.Info("Skipping stale sealed block", "sealed", block.NumberU64(), "current", currentBlock.Number.Uint64())
+				continue
+			}
+
 			oldBlock := w.chain.GetBlockByNumber(block.NumberU64())
 			if oldBlock != nil {
 				oldBlockAuthor, _ := w.chain.Engine().Author(oldBlock.Header())
@@ -1084,6 +1091,7 @@ mainloop:
 
 				if env.tcount > len(env.depsMVFullWriteList) {
 					log.Warn("blockstm - env.tcount > len(env.depsMVFullWriteList)", "env.tcount", env.tcount, "len(depsMVFullWriteList)", len(env.depsMVFullWriteList))
+					return errors.New("transaction count exceeds dependency list length")
 				}
 
 				temp := blockstm.TxDep{
@@ -1092,7 +1100,20 @@ mainloop:
 					FullWriteList: env.depsMVFullWriteList,
 				}
 
-				chDeps <- temp
+				// Send with timeout to prevent deadlock
+				select {
+				case chDeps <- temp:
+					// Successfully sent
+				case <-time.After(1 * time.Second):
+					// Timeout after 1 second - channel is blocked
+					log.Error("Transaction dependency channel blocked, aborting block building",
+						"txIndex", env.tcount-1,
+						"blockNumber", env.header.Number.Uint64())
+					once.Do(func() {
+						close(chDeps)
+					})
+					return errors.New("dependency channel timeout")
+				}
 			}
 
 			txs.Shift()
```
