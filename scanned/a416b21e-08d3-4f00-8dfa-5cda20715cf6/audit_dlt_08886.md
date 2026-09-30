# [?] Fix panic when feeder returns mismatched number of txns and receipts

## Summary
Severity: Unknown
Chain: Starknet
Component: NethermindEth/juno
Published: 2023-09-28
Source: https://github.com/NethermindEth/juno/commit/8a6218e05f6a613a648f26add8ae904ce2246407
Type: security-commit

## Details
Fix panic when feeder returns mismatched number of txns and receipts

## Patch
### adapters/feeder2core/feeder2core.go
```diff
@@ -19,16 +19,19 @@ func AdaptBlock(response *feeder.Block, sig *feeder.Signature) (*core.Block, err
 	}
 
 	txns := make([]core.Transaction, len(response.Transactions))
-	receipts := make([]*core.TransactionReceipt, len(response.Receipts))
-	eventCount := uint64(0)
 	for i, txn := range response.Transactions {
 		var err error
 		txns[i], err = AdaptTransaction(txn)
 		if err != nil {
 			return nil, err
 		}
-		receipts[i] = AdaptTransactionReceipt(response.Receipts[i])
-		eventCount += uint64(len(response.Receipts[i].Events))
+	}
+
+	receipts := make([]*core.TransactionReceipt, len(response.Receipts))
+	eventCount := uint64(0)
+	for i, receipt := range response.Receipts {
+		receipts[i] = AdaptTransactionReceipt(receipt)
+		eventCount += uint64(len(receipt.Events))
 	}
 
 	sigs := [][]*felt.Felt{}
```
