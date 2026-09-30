# [?] Improve double spend error strings.

## Summary
Severity: Unknown
Chain: Bitcoin
Component: btcsuite/btcd
Published: 2015-01-07
Source: https://github.com/btcsuite/btcd/commit/8945620a8494f69764777638c314291a02b9ecfa
Type: security-commit

## Details
Improve double spend error strings.

The error message now includes both the previous tx hash and output
index, rather than simply the transaction with the already spent
output.

## Patch
### validate.go
```diff
@@ -701,8 +701,7 @@ func CheckTransactionInputs(tx *btcutil.Tx, txHeight int64, txStore TxStore) (in
 		}
 		if originTx.Spent[originTxIndex] {
 			str := fmt.Sprintf("transaction %v tried to double "+
-				"spend coins from transaction %v", txHash,
-				txInHash)
+				"spend output %v", txHash, txIn.PreviousOutPoint)
 			return 0, ruleError(ErrDoubleSpend, str)
 		}
 
```
