# [?] added nil pointer check for args.Value to avoid a panic in estimate gas call (#989)

## Summary
Severity: Unknown
Chain: Quorum
Component: Consensys-inc-archive/quorum
Published: 2020-05-09
Source: https://github.com/Consensys-inc-archive/quorum/commit/80564d5f26d464e9e5c99e74338d1cf0a8428493
Type: security-commit

## Details
added nil pointer check for args.Value to avoid a panic in estimate gas call (#989)

## Patch
### internal/ethapi/api.go
```diff
@@ -972,7 +972,7 @@ func DoEstimateGas(ctx context.Context, b Backend, args CallArgs, blockNrOrHash
 	//This makes the return value a potential over-estimate of gas, rather than the exact cost to run right now
 
 	//if the transaction has a value then it cannot be private, so we can skip this check
-	if args.Value.ToInt().Cmp(big.NewInt(0)) == 0 {
+	if args.Value != nil && args.Value.ToInt().Cmp(big.NewInt(0)) == 0 {
 		homestead := b.ChainConfig().IsHomestead(new(big.Int).SetInt64(int64(rpc.PendingBlockNumber)))
 		istanbul := b.ChainConfig().IsIstanbul(new(big.Int).SetInt64(int64(rpc.PendingBlockNumber)))
 		var data []byte
```
