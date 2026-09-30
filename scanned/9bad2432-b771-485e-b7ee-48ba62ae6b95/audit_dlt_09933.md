# [?] fix handler crash

## Summary
Severity: Unknown
Chain: Kaia
Component: kaiachain/kaia
Published: 2023-07-05
Source: https://github.com/kaiachain/kaia/commit/f0a78a9a909a3245638202993e65d7b92651af05
Type: security-commit

## Details
fix handler crash

## Patch
### api/api_public_transaction_pool.go
```diff
@@ -192,7 +192,7 @@ func (s *PublicTransactionPoolAPI) GetRawTransactionByHash(ctx context.Context,
 	if tx, _, _, _ = s.b.ChainDB().ReadTxAndLookupInfo(hash); tx == nil {
 		if tx = s.b.GetPoolTransaction(hash); tx == nil {
 			// Transaction not found anywhere, abort
-			return nil, nil
+			return nil, fmt.Errorf("the transaction does not exist (tx hash: %s)", hash.String())
 		}
 	}
 
```
