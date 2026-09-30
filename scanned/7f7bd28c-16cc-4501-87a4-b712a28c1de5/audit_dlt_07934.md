# [?] [R4R]fix:Shift panic for zero length of heads (#870)

## Summary
Severity: Unknown
Chain: BNB Chain
Component: bnb-chain/bsc
Published: 2022-04-25
Source: https://github.com/bnb-chain/bsc/commit/0f5a4c87dbb5a7223d21fa6cc9d7020f676dfa05
Type: security-commit

## Details
[R4R]fix:Shift panic for zero length of heads (#870)

* fix:Shift panic for zero length of heads

* fix: make sure peek before shift

* refactor and update ut

* refactor

## Patch
### core/state_prefetcher.go
```diff
@@ -127,23 +127,21 @@ func (p *statePrefetcher) PrefetchMining(txs *types.TransactionsByPriceAndNonce,
 	go func(txset *types.TransactionsByPriceAndNonce) {
 		count := 0
 		for {
-			tx := txset.Peek()
-			if tx == nil {
-				return
-			}
 			select {
 			case <-interruptCh:
 				return
 			default:
-			}
-			if count++; count%checkInterval == 0 {
-				if *txCurr == nil {
+				if count++; count%checkInterval == 0 {
+					txset.Forward(*txCurr)
+				}
+				tx := txset.Peek()
+				if tx == nil {
 					return
 				}
-				txset.Forward(*txCurr)
+				txCh <- tx
+				txset.Shift()
+
 			}
-			txCh <- tx
-			txset.Shift()
 		}
 	}(txs)
 }
```

### core/types/transaction.go
```diff
@@ -506,7 +506,9 @@ func (t *TransactionsByPriceAndNonce) CurrentSize() int {
 //Forward moves current transaction to be the one which is one index after tx
 func (t *TransactionsByPriceAndNonce) Forward(tx *Transaction) {
 	if tx == nil {
-		t.heads = t.heads[0:0]
+		if len(t.heads) > 0 {
+			t.heads = t.heads[0:0]
+		}
 		return
 	}
 	//check whether target tx exists in t.heads
```

### core/types/transaction_test.go
```diff
@@ -392,14 +392,17 @@ func TestTransactionForward(t *testing.T) {
 	}
 
 	tmp := txset.Copy()
-	for j := 0; j < 10; j++ {
+	for j := 0; j < 11; j++ {
 		txset = tmp.Copy()
 		txsetCpy = tmp.Copy()
 		i := 0
 		for ; i < j; i++ {
 			txset.Shift()
 		}
 		tx := txset.Peek()
+		if tx == nil {
+			continue
+		}
 		txsetCpy.Forward(tx)
 		txCpy := txsetCpy.Peek()
 		if txCpy == nil {
```
