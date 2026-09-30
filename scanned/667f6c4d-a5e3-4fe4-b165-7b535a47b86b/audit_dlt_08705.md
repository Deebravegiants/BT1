# [?] prevent nil deref when reading from queue in data paster

## Summary
Severity: Unknown
Chain: Arbitrum
Component: OffchainLabs/nitro
Published: 2025-08-20
Source: https://github.com/OffchainLabs/nitro/commit/b4bbcb049f46ba9492d0c6cad7f6b8cef2b5ac56
Type: security-commit

## Details
prevent nil deref when reading from queue in data paster

## Patch
### arbnode/dataposter/data_poster.go
```diff
@@ -1213,7 +1213,6 @@ func (p *DataPoster) Start(ctxIn context.Context) {
 			} else {
 				log.Error("Failed to fetch latest confirmed tx from queue", "confirmedNonce", confirmedNonce, "err", err, "confirmedMeta", confirmedMeta)
 			}
-
 		}
 
 		for _, tx := range queueContents {
@@ -1226,9 +1225,14 @@ func (p *DataPoster) Start(ctxIn context.Context) {
 				err := p.sendTx(ctx, tx, tx)
 				p.maybeLogError(err, tx, "failed to re-send transaction")
 			}
-			tx, err = p.queue.Get(ctx, tx.FullTx.Nonce())
+			nonce := tx.FullTx.Nonce()
+			tx, err = p.queue.Get(ctx, nonce)
 			if err != nil {
-				log.Error("Failed to fetch tx from queue to check updated status", "nonce", tx.FullTx.Nonce(), "err", err)
+				log.Error("Failed to fetch tx from queue to check updated status", "nonce", nonce, "err", err)
+				return minWait
+			}
+			if tx == nil {
+				log.Error("Failed to fetch tx from queue to check updated status, got tx == nil", "nonce", nonce)
 				return minWait
 			}
 			if nextCheck.After(tx.NextReplacement) {
```
