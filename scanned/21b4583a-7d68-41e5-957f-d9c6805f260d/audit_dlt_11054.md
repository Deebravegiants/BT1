# [?] Avoid overflow when adding additional gas

## Summary
Severity: Unknown
Chain: Arbitrum
Component: OffchainLabs/go-ethereum
Published: 2025-04-30
Source: https://github.com/OffchainLabs/go-ethereum/commit/25fc5f0842584e72455e4d60a61f035623b1aba0
Type: security-commit

## Details
Avoid overflow when adding additional gas

## Patch
### internal/ethapi/api.go
```diff
@@ -721,7 +721,9 @@ func applyMessage(ctx context.Context, b Backend, args TransactionArgs, state *s
 		if err != nil {
 			return nil, err
 		}
-		gp.AddGas(postingGas)
+		if gp.Gas() < gomath.MaxUint64-postingGas {
+			gp.AddGas(postingGas)
+		}
 	}
 	if msg.GasLimit > gp.Gas() {
 		gp.SetGas(msg.GasLimit)
```
