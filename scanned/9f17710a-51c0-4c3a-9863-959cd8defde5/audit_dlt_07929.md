# [?] fix: crash on nil access when TxPool shutdown (#1353) (#1356)

## Summary
Severity: Unknown
Chain: BNB Chain
Component: bnb-chain/bsc
Published: 2023-03-15
Source: https://github.com/bnb-chain/bsc/commit/fc4303c6c601a697bc1d1f9da17e11c556c6dba1
Type: security-commit

## Details
fix: crash on nil access when TxPool shutdown (#1353) (#1356)

## Patch
### miner/worker.go
```diff
@@ -1126,7 +1126,12 @@ LOOP:
 		// subscribe before fillTransactions
 		txsCh := make(chan core.NewTxsEvent, txChanSize)
 		sub := w.eth.TxPool().SubscribeNewTxsEvent(txsCh)
-		defer sub.Unsubscribe()
+		// if TxPool has been stopped, `sub` would be nil, it could happen on shutdown.
+		if sub == nil {
+			log.Info("commitWork SubscribeNewTxsEvent return nil")
+		} else {
+			defer sub.Unsubscribe()
+		}
 
 		// Fill pending transactions from the txpool
 		fillStart := time.Now()
@@ -1196,7 +1201,9 @@ LOOP:
 		}
 		// if sub's channel if full, it will block other NewTxsEvent subscribers,
 		// so unsubscribe ASAP and Unsubscribe() is re-enterable, safe to call several time.
-		sub.Unsubscribe()
+		if sub != nil {
+			sub.Unsubscribe()
+		}
 	}
 	// get the most profitable work
 	bestWork := workList[0]
```
