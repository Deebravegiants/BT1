# [?] fix: bump pfm to address security advisory (#488)

## Summary
Severity: Unknown
Chain: Noble
Component: noble-assets/noble
Published: 2025-02-18
Source: https://github.com/noble-assets/noble/commit/9d27f57199bcc57e64cd3749319139aee9f214fe
Type: security-commit

## Details
fix: bump pfm to address security advisory (#488)

## Patch
### .changelog/unreleased/dependencies/488-bump-pfm.md
```diff
@@ -0,0 +1 @@
+- Bump Packet Forward Middleware to [`v8.1.1`](https://github.com/cosmos/ibc-apps/releases/tag/middleware%2Fpacket-forward-middleware%2Fv8.1.1) to resolve [GHSA-6fgm-x6ff-w78f](https://github.com/cosmos/ibc-apps/security/advisories/GHSA-6fgm-x6ff-w78f) security advisory. ([#488](https://github.com/noble-assets/noble/pull/488))
```

### go.mod
```diff
@@ -21,7 +21,7 @@ require (
 	github.com/cometbft/cometbft v0.38.17
 	github.com/cosmos/cosmos-db v1.1.0
 	github.com/cosmos/cosmos-sdk v0.50.11
-	github.com/cosmos/ibc-apps/middleware/packet-forward-middleware/v8 v8.0.2
+	github.com/cosmos/ibc-apps/middleware/packet-forward-middleware/v8 v8.1.1
 	github.com/cosmos/ibc-go/modules/capability v1.0.1
 	github.com/cosmos/ibc-go/v8 v8.5.2
 	github.com/golangci/golangci-lint v1.61.0
```

### go.sum
```diff
@@ -463,8 +463,8 @@ github.com/cosmos/gogoproto v1.7.0 h1:79USr0oyXAbxg3rspGh/m4SWNyoz/GLaAh0QlCe2fr
 github.com/cosmos/gogoproto v1.7.0/go.mod h1:yWChEv5IUEYURQasfyBW5ffkMHR/90hiHgbNgrtp4j0=
 github.com/cosmos/iavl v1.2.2 h1:qHhKW3I70w+04g5KdsdVSHRbFLgt3yY3qTMd4Xa4rC8=
 github.com/cosmos/iavl v1.2.2/go.mod h1:GiM43q0pB+uG53mLxLDzimxM9l/5N9UuSY3/D0huuVw=
-github.com/cosmos/ibc-apps/middleware/packet-forward-middleware/v8 v8.0.2 h1:dyLNlDElY6+5zW/BT/dO/3Ad9FpQblfh+9dQpYQodbA=
-github.com/cosmos/ibc-apps/middleware/packet-forward-middleware/v8 v8.0.2/go.mod h1:82hPO/tRawbuFad2gPwChvpZ0JEIoNi91LwVneAYCeM=
+github.com/cosmos/ibc-apps/middleware/packet-forward-middleware/v8 v8.1.1 h1:+EGYrTsQ2hu8pBwCWAgqc0g/zSklvBFehda9URLfvOU=
+github.com/cosmos/ibc-apps/middleware/packet-forward-middleware/v8 v8.1.1/go.mod h1:8sbOclBgOCgBPesufd3ZlLRHvJ3dOeN9+dXhn3KbKOc=
 github.com/cosmos/ibc-go/modules/capability v1.0.1 h1:ibwhrpJ3SftEEZRxCRkH0fQZ9svjthrX2+oXdZvzgGI=
 github.com/cosmos/ibc-go/modules/capability v1.0.1/go.mod h1:rquyOV262nGJplkumH+/LeYs04P3eV8oB7ZM4Ygqk4E=
 github.com/cosmos/ibc-go/v8 v8.5.2 h1:27s9oeD2AxLQF3e9BQsYt9doONyZ7FwZi/qkBv6Sdks=
```

### legacy.go
```diff
@@ -60,7 +60,6 @@ func (app *App) RegisterLegacyModules() error {
 
 	app.ParamsKeeper.Subspace(ibcexported.ModuleName).WithKeyTable(clienttypes.ParamKeyTable().RegisterParamSet(&connectiontypes.Params{}))
 	app.ParamsKeeper.Subspace(icahosttypes.SubModuleName).WithKeyTable(icahosttypes.ParamKeyTable())
-	app.ParamsKeeper.Subspace(pfmtypes.ModuleName).WithKeyTable(pfmtypes.ParamKeyTable())
 	app.ParamsKeeper.Subspace(transfertypes.ModuleName).WithKeyTable(transfertypes.ParamKeyTable())
 
 	app.CapabilityKeeper = capabilitykeeper.NewKeeper(
@@ -116,7 +115,6 @@ func (app *App) RegisterLegacyModules() error {
 		app.GetKey(pfmtypes.StoreKey),
 		app.TransferKeeper,
 		app.IBCKeeper.ChannelKeeper,
-		nil,
 		app.BankKeeper,
 		app.IBCKeeper.ChannelKeeper,
 		authoritytypes.ModuleAddress.String(),
@@ -130,7 +128,6 @@ func (app *App) RegisterLegacyModules() error {
 		app.PFMKeeper,
 		0,
 		pfmkeeper.DefaultForwardTransferPacketTimeoutTimestamp,
-		pfmkeeper.DefaultRefundTransferPacketTimeoutTimestamp,
 	)
 	transferStack = blockibc.NewIBCMiddleware(transferStack, app.FTFKeeper)
 
```
