# [?] Fix a deadlock when sync shutdown and restart happens at the same time

## Summary
Severity: Unknown
Chain: Starknet
Component: NethermindEth/juno
Published: 2023-02-21
Source: https://github.com/NethermindEth/juno/commit/2ead1387daf95f79d02f741ffe3ec303506569fd
Type: security-commit

## Details
Fix a deadlock when sync shutdown and restart happens at the same time

## Patch
### sync/sync.go
```diff
@@ -74,14 +74,20 @@ func (s *Synchronizer) verifierTask(ctx context.Context, block *core.Block, stat
 		default:
 			if err != nil {
 				s.log.Warnw("Sanity checks failed", "number", block.Number, "hash", block.Hash.Text(16))
-				errChan <- ErrSyncFailed{block.Number, err}
+				select {
+				case <-ctx.Done():
+				case errChan <- ErrSyncFailed{block.Number, err}:
+				}
 				return
 			}
 			err = s.Blockchain.Store(block, stateUpdate)
 			if err != nil {
 				s.log.Warnw("Failed storing Block", "number", block.Number, "hash", block.Hash.Text(16),
 					"err", err.Error())
-				errChan <- ErrSyncFailed{block.Number, err}
+				select {
+				case <-ctx.Done():
+				case errChan <- ErrSyncFailed{block.Number, err}:
+				}
 				return
 			}
 
```
