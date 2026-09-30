# [?] fix wasm panic

## Summary
Severity: Unknown
Chain: Neutron
Component: neutron-org/neutron
Published: 2023-09-15
Source: https://github.com/neutron-org/neutron/commit/13b5273f5e4db63522ac9028e8e016a19a68a4bb
Type: security-commit

## Details
fix wasm panic

## Patch
### app/app.go
```diff
@@ -440,7 +440,7 @@ func New(
 		appCodec,
 		keys[crisistypes.StoreKey],
 		invCheckPeriod,
-		app.BankKeeper,
+		&app.BankKeeper,
 		authtypes.FeeCollectorName,
 		authtypes.NewModuleAddress(adminmoduletypes.ModuleName).String(),
 	)
@@ -501,7 +501,7 @@ func New(
 		keys[feeburnertypes.StoreKey],
 		keys[feeburnertypes.MemStoreKey],
 		app.AccountKeeper,
-		app.BankKeeper,
+		&app.BankKeeper,
 		authtypes.NewModuleAddress(adminmoduletypes.ModuleName).String(),
 	)
 	feeBurnerModule := feeburner.NewAppModule(appCodec, *app.FeeBurnerKeeper)
@@ -514,7 +514,7 @@ func New(
 		app.TransferKeeper.Keeper,
 		app.IBCKeeper.ChannelKeeper,
 		app.FeeBurnerKeeper,
-		app.BankKeeper,
+		&app.BankKeeper,
 		app.IBCKeeper.ChannelKeeper,
 	)
 	wasmHooks := ibchooks.NewWasmHooks(nil, sdk.GetConfig().GetBech32AccountAddrPrefix()) // The contract keeper needs to be set later
@@ -533,7 +533,7 @@ func New(
 		app.IBCKeeper.ChannelKeeper,
 		&app.IBCKeeper.PortKeeper,
 		app.AccountKeeper,
-		app.BankKeeper,
+		&app.BankKeeper,
 		scopedTransferKeeper,
 		app.FeeKeeper,
 		app.ContractManagerKeeper,
@@ -560,7 +560,7 @@ func New(
 		app.IBCKeeper.ConnectionKeeper,
 		app.IBCKeeper.ClientKeeper,
 		app.SlashingKeeper,
-		app.BankKeeper,
+		&app.BankKeeper,
 		app.AccountKeeper,
 		app.TransferKeeper.Keeper, // we cant use our transfer wrapper type here because of interface incompatibility, it looks safe to use underlying transfer keeper.
 		// Since the keeper is only used to send reward to provider chain
@@ -575,7 +575,7 @@ func New(
 		app.keys[tokenfactorytypes.StoreKey],
 		app.AccountKeeper,
 		app.BankKeeper.WithMintCoinsRestriction(tokenfactorytypes.NewTokenFactoryDenomMintCoinsRestriction()),
-		app.WasmKeeper,
+		&app.WasmKeeper,
 		authtypes.NewModuleAddress(adminmoduletypes.ModuleName).String(),
 	)
 	app.TokenFactoryKeeper = &tokenFactoryKeeper
@@ -589,7 +589,7 @@ func New(
 		appCodec,
 		keys[buildertypes.StoreKey],
 		app.AccountKeeper,
-		app.BankKeeper,
+		&app.BankKeeper,
 		// 25% of rewards should be sent to the redistribute address
 		rewardsaddressprovider.NewFixedAddressRewardsAddressProvider(app.AccountKeeper.GetModuleAddress(ccvconsumertypes.ConsumerRedistributeName)),
 		authtypes.NewModuleAddress(adminmoduletypes.ModuleName).String(),
@@ -631,7 +631,7 @@ func New(
 		keys[interchainqueriesmoduletypes.StoreKey],
 		keys[interchainqueriesmoduletypes.MemStoreKey],
 		app.IBCKeeper,
-		app.BankKeeper,
+		&app.BankKeeper,
 		app.ContractManagerKeeper,
 		interchainqueriesmodulekeeper.Verifier{},
 		interchainqueriesmodulekeeper.TransactionVerifier{},
@@ -659,7 +659,7 @@ func New(
 		appCodec,
 		keys[wasm.StoreKey],
 		app.AccountKeeper,
-		app.BankKeeper,
+		&app.BankKeeper,
 		nil,
 		nil,
 		app.IBCKeeper.ChannelKeeper, // may be replaced with middleware such as ics29 feerefunder
```
