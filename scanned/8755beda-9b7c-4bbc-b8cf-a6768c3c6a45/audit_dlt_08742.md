# [?] fix GetTransactionReceipt crash when BaseFee is missing (#224)

## Summary
Severity: Unknown
Chain: Scroll
Component: scroll-tech/go-ethereum
Published: 2023-02-21
Source: https://github.com/scroll-tech/go-ethereum/commit/3fcd77955e9a5caff56a27285febe22ac2f4ee77
Type: security-commit

## Details
fix GetTransactionReceipt crash when BaseFee is missing (#224)

## Patch
### internal/ethapi/api.go
```diff
@@ -1588,7 +1588,13 @@ func (s *PublicTransactionPoolAPI) GetTransactionReceipt(ctx context.Context, ha
 		if err != nil {
 			return nil, err
 		}
-		gasPrice := new(big.Int).Add(header.BaseFee, tx.EffectiveGasTipValue(header.BaseFee))
+
+		baseFee := header.BaseFee
+		if baseFee == nil {
+			baseFee = big.NewInt(0)
+		}
+
+		gasPrice := new(big.Int).Add(baseFee, tx.EffectiveGasTipValue(header.BaseFee))
 		fields["effectiveGasPrice"] = hexutil.Uint64(gasPrice.Uint64())
 	}
 	// Assign receipt status or post state.
```
