# [?] [R4R]Fix mining-prefetcher panic for empty transaction initial of txCurr(#843)

## Summary
Severity: Unknown
Chain: BNB Chain
Component: bnb-chain/bsc
Published: 2022-04-06
Source: https://github.com/bnb-chain/bsc/commit/12c5eb00a86c83f775e0284d9ca77ff892563bfd
Type: security-commit

## Details
[R4R]Fix mining-prefetcher panic for empty transaction initial of txCurr(#843)

## Patch
### miner/worker.go
```diff
@@ -782,10 +782,10 @@ func (w *worker) commitTransactions(txs *types.TransactionsByPriceAndNonce, coin
 
 	interruptCh := make(chan struct{})
 	defer close(interruptCh)
-	tx := &types.Transaction{}
-	txCurr := &tx
 	//prefetch txs from all pending txs
 	txsPrefetch := txs.Copy()
+	tx := txsPrefetch.Peek()
+	txCurr := &tx
 	w.prefetcher.PrefetchMining(txsPrefetch, w.current.header, w.current.gasPool.Gas(), w.current.state.Copy(), *w.chain.GetVMConfig(), interruptCh, txCurr)
 
 LOOP:
```
