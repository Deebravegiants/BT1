# [?] Prevent integer overflow

## Summary
Severity: Unknown
Chain: Cosmos
Component: CosmWasm/wasmd
Published: 2020-10-06
Source: https://github.com/CosmWasm/wasmd/commit/fd9130d7df9957880579be6ed44f99ee05b4f17a
Type: security-commit

## Details
Prevent integer overflow

## Patch
### x/wasm/internal/keeper/keeper.go
```diff
@@ -566,6 +566,10 @@ func (k Keeper) dispatchMessages(ctx sdk.Context, contractAddr sdk.AccAddress, m
 
 func gasForContract(ctx sdk.Context) uint64 {
 	meter := ctx.GasMeter()
+	// avoid integer overflow
+	if meter.IsOutOfGas() {
+		return 0
+	}
 	remaining := (meter.Limit() - meter.GasConsumed()) * GasMultiplier
 	if remaining > MaxGas {
 		return MaxGas
```
