# [?] core: maybe fix panic

## Summary
Severity: Unknown
Chain: Ethereum Classic
Component: etclabscore/core-geth
Published: 2022-10-17
Source: https://github.com/etclabscore/core-geth/commit/83fb902128c1d88b745450f4d90cb0d77e90a034
Type: security-commit

## Details
core: maybe fix panic

Date: 2022-10-17 13:55:00-07:00
Signed-off-by: meows <b5c6@protonmail.com>

## Patch
### core/tx_cacher.go
```diff
@@ -60,9 +60,16 @@ func newTxSenderCacher(threads int) *txSenderCacher {
 // cache is an infinite loop, caching transaction senders from various forms of
 // data structures.
 func (cacher *txSenderCacher) cache() {
-	for task := range cacher.tasks {
-		for i := 0; i < len(task.txs); i += task.inc {
-			types.Sender(task.signer, task.txs[i])
+	for {
+		select {
+		case task := <-cacher.tasks:
+			for i := 0; i < len(task.txs); i += task.inc {
+				types.Sender(task.signer, task.txs[i])
+			}
+		default:
+			if cacher.tasks == nil {
+				return
+			}
 		}
 	}
 }
```
