# [?] Fix potential overflow in blockchain.DoEstimateGas

## Summary
Severity: Unknown
Chain: Kaia
Component: kaiachain/kaia
Published: 2025-07-31
Source: https://github.com/kaiachain/kaia/commit/d27c9ccca2585c6df5314e91ae73f6c5d73e5ae8
Type: security-commit

## Details
Fix potential overflow in blockchain.DoEstimateGas

## Patch
### blockchain/evm.go
```diff
@@ -194,7 +194,7 @@ func DoEstimateGas(ctx context.Context, gasLimit, rpcGasCap uint64, txValue, gas
 
 	// Execute the binary search and hone in on an executable gas limit
 	for lo+1 < hi {
-		mid := (hi + lo) / 2
+		mid := lo + (hi-lo)/2
 		failed, _, err := test(mid)
 		if err != nil {
 			return 0, err
```
