# [?] Merge pull request from GHSA-2vxv-63gj-7pmq

## Summary
Severity: Unknown
Chain: Cosmos Hub
Component: cosmos/gaia
Published: 2021-03-10
Source: https://github.com/cosmos/gaia/commit/80d55aa032e513d57b93b8584b271af6f25a9f9c
Type: security-commit

## Details
Merge pull request from GHSA-2vxv-63gj-7pmq

## Patch
### app/app.go
```diff
@@ -131,11 +131,6 @@ var (
 		govtypes.ModuleName:            {authtypes.Burner},
 		ibctransfertypes.ModuleName:    {authtypes.Minter, authtypes.Burner},
 	}
-
-	// module accounts that are allowed to receive tokens
-	allowedReceivingModAcc = map[string]bool{
-		distrtypes.ModuleName: true,
-	}
 )
 
 var (
@@ -244,7 +239,7 @@ func NewGaiaApp(
 		appCodec, keys[authtypes.StoreKey], app.GetSubspace(authtypes.ModuleName), authtypes.ProtoBaseAccount, maccPerms,
 	)
 	app.BankKeeper = bankkeeper.NewBaseKeeper(
-		appCodec, keys[banktypes.StoreKey], app.AccountKeeper, app.GetSubspace(banktypes.ModuleName), app.BlockedAddrs(),
+		appCodec, keys[banktypes.StoreKey], app.AccountKeeper, app.GetSubspace(banktypes.ModuleName), app.ModuleAccountAddrs(),
 	)
 	stakingKeeper := stakingkeeper.NewKeeper(
 		appCodec, keys[stakingtypes.StoreKey], app.AccountKeeper, app.BankKeeper, app.GetSubspace(stakingtypes.ModuleName),
@@ -471,17 +466,6 @@ func (app *GaiaApp) ModuleAccountAddrs() map[string]bool {
 	return modAccAddrs
 }
 
-// BlockedAddrs returns all the app's module account addresses that are not
-// allowed to receive external tokens.
-func (app *GaiaApp) BlockedAddrs() map[string]bool {
-	blockedAddrs := make(map[string]bool)
-	for acc := range maccPerms {
-		blockedAddrs[authtypes.NewModuleAddress(acc).String()] = !allowedReceivingModAcc[acc]
-	}
-
-	return blockedAddrs
-}
-
 // LegacyAmino returns GaiaApp's amino codec.
 //
 // NOTE: This is solely to be used for testing purposes as it may be desirable
```
