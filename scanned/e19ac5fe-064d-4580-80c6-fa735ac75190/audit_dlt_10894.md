# [?] fix(node): panic in txStashLoop

## Summary
Severity: Unknown
Chain: VeChain
Component: vechain/thor
Published: 2018-07-09
Source: https://github.com/vechain/thor/commit/971ff483917a91bea2cd32733fd2dddd818531f3
Type: security-commit

## Details
fix(node): panic in txStashLoop

## Patch
### cmd/thor/node/node.go
```diff
@@ -219,10 +219,11 @@ func (n *Node) txStashLoop(ctx context.Context) {
 		case <-ctx.Done():
 			return
 		case txEv := <-txCh:
-			// only stash non-executable txs
-			if txEv.Executable != nil || *txEv.Executable {
+			// skip executables
+			if txEv.Executable != nil && *txEv.Executable {
 				continue
 			}
+			// only stash non-executable txs
 			if err := stash.Save(txEv.Tx); err != nil {
 				log.Warn("stash tx", "id", txEv.Tx.ID(), "err", err)
 			} else {
```
