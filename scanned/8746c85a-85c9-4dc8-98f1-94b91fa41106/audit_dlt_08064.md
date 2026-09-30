# [?] Merge pull request #16843 from karalabe/txpool-fix-deadlock

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2018-05-30
Source: https://github.com/celo-org/celo-blockchain/commit/ca34e8230e52805401cff05ca874bc3bc90296e8
Type: security-commit

## Details
Merge pull request #16843 from karalabe/txpool-fix-deadlock

core: fix transaction event asynchronicity

## Patch
### core/tx_pool.go
```diff
@@ -962,7 +962,7 @@ func (pool *TxPool) promoteExecutables(accounts []common.Address) {
 	}
 	// Notify subsystem for new promoted transactions.
 	if len(promoted) > 0 {
-		pool.txFeed.Send(NewTxsEvent{promoted})
+		go pool.txFeed.Send(NewTxsEvent{promoted})
 	}
 	// If the pending limit is overflown, start equalizing allowances
 	pending := uint64(0)
```
