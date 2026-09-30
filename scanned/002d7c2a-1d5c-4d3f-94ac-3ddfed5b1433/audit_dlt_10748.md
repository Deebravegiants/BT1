# [?] Merge pull request #1398 from hyunsooda/tx-fix-oob

## Summary
Severity: Unknown
Chain: Kaia
Component: kaiachain/kaia
Published: 2022-06-16
Source: https://github.com/kaiachain/kaia/commit/fcf5e95bb1da115ac6686b2dea6f1710b97950ac
Type: security-commit

## Details
Merge pull request #1398 from hyunsooda/tx-fix-oob

[Transaction] Fixed a potential buffer-over-run

## Patch
### blockchain/types/transaction.go
```diff
@@ -928,6 +928,9 @@ func (t *TransactionsByPriceAndNonce) Peek() *Transaction {
 
 // Shift replaces the current best head with the next one from the same account.
 func (t *TransactionsByPriceAndNonce) Shift() {
+	if len(t.heads) == 0 {
+		return
+	}
 	acc, _ := Sender(t.signer, t.heads[0])
 	if txs, ok := t.txs[acc]; ok && len(txs) > 0 {
 		t.heads[0], t.txs[acc] = txs[0], txs[1:]
```
