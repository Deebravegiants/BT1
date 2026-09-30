# [?] Merge pull request #250 from uprendis/feature/fix-receipt-api-crash

## Summary
Severity: Unknown
Chain: Sonic
Component: 0xsoniclabs/sonic
Published: 2022-02-11
Source: https://github.com/0xsoniclabs/sonic/commit/7be62dbe72cad65c102653746c210636b16f96f9
Type: security-commit

## Details
Merge pull request #250 from uprendis/feature/fix-receipt-api-crash

Fix nil pointer dereference in GetTransactionReceipt

## Patch
### ethapi/api.go
```diff
@@ -1623,13 +1623,9 @@ func (s *PublicTransactionPoolAPI) GetTransactionReceipt(ctx context.Context, ha
 		"type":              hexutil.Uint(tx.Type()),
 	}
 	// Assign the effective gas price paid
-	if !s.b.ChainConfig().IsLondon(bigblock) {
+	if header.BaseFee == nil {
 		fields["effectiveGasPrice"] = hexutil.Uint64(tx.GasPrice().Uint64())
 	} else {
-		header, err := s.b.HeaderByHash(ctx, header.Hash)
-		if err != nil {
-			return nil, err
-		}
 		gasPrice := new(big.Int).Add(header.BaseFee, tx.EffectiveGasTipValue(header.BaseFee))
 		fields["effectiveGasPrice"] = hexutil.Uint64(gasPrice.Uint64())
 	}
```
