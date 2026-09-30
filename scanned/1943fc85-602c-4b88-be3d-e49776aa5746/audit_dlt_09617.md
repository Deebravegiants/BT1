# [?] fix: panic on export zero-height because validator addr length parsing (#1015)

## Summary
Severity: Unknown
Chain: Cosmos Hub
Component: cosmos/gaia
Published: 2021-10-13
Source: https://github.com/cosmos/gaia/commit/f2183e1774a155b5eea3e9d107c087c3f94f041b
Type: security-commit

## Details
fix: panic on export zero-height because validator addr length parsing (#1015)

## Patch
### app/export.go
```diff
@@ -157,7 +157,7 @@ func (app *GaiaApp) prepForZeroHeightGenesis(ctx sdk.Context, jailAllowedAddrs [
 	counter := int16(0)
 
 	for ; iter.Valid(); iter.Next() {
-		addr := sdk.ValAddress(iter.Key()[1:])
+		addr := sdk.ValAddress(stakingtypes.AddressFromValidatorsKey(iter.Key()))
 		validator, found := app.StakingKeeper.GetValidator(ctx, addr)
 		if !found {
 			panic("expected validator, not found")
```
