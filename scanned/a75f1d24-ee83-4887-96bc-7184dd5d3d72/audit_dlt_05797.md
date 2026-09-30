# [?] fix: avoid panic when migrate param for newly added host (#6167)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cosmos/ibc-go
Published: 2024-04-22
Source: https://github.com/cosmos/ibc-go/commit/c4413c5877f9ef883494da1721cb18caaba7f7f5
Type: security-commit

## Details
fix: avoid panic when migrate param for newly added host (#6167)

* fix: avoid panic when migrate param for newly added host

* keep default params

* Apply suggestions from code review

* allow use default params when set nil legacySubspace

* Update CHANGELOG.md

Co-authored-by: coderabbitai[bot] <136622811+coderabbitai[bot]@users.noreply.github.com>

* Update CHANGELOG.md

* cleanup

* refactor: rm setter in icahost migrator and adjust test case

* chore: update changelog

* Apply suggestions from code review

* Apply suggestions from code review

* Apply suggestions from code review

---------

Co-authored-by: Carlos Rodriguez <carlos@interchain.io>
Co-authored-by: coderabbitai[bot] <136622811+coderabbitai[bot]@users.noreply.github.com>
Co-authored-by: Damian Nolan <damiannolan@gmail.com>

## Patch
### CHANGELOG.md
```diff
@@ -60,6 +60,8 @@ Ref: https://keepachangelog.com/en/1.0.0/
 
 ### Bug Fixes
 
+* (apps/27-interchain-accounts) [\#6167](https://github.com/cosmos/ibc-go/pull/6167) Fixed an edge case bug where migrating params for a pre-existing ica module which implemented controller functionality only could panic when migrating params for newly added host, and align controller param migration with host.
+
 ## [v8.2.0](https://github.com/cosmos/ibc-go/releases/tag/v8.2.0) - 2024-04-05
 
 ### Dependencies
```

### modules/apps/27-interchain-accounts/controller/keeper/migrations.go
```diff
@@ -55,9 +55,10 @@ func (m Migrator) AssertChannelCapabilityMigrations(ctx sdk.Context) error {
 // MigrateParams migrates the controller submodule's parameters from the x/params to self store.
 func (m Migrator) MigrateParams(ctx sdk.Context) error {
 	if m.keeper != nil {
-		var params controllertypes.Params
-		m.keeper.legacySubspace.GetParamSet(ctx, &params)
-
+		params := controllertypes.DefaultParams()
+		if m.keeper.legacySubspace != nil {
+			m.keeper.legacySubspace.GetParamSetIfExists(ctx, &params)
+		}
 		m.keeper.SetParams(ctx, params)
 		m.keeper.Logger(ctx).Info("successfully migrated ica/controller submodule to self-manage params")
 	}
```

### modules/apps/27-interchain-accounts/controller/keeper/migrations_test.go
```diff
@@ -92,6 +92,23 @@ func (suite *KeeperTestSuite) TestMigratorMigrateParams() {
 			},
 			icacontrollertypes.DefaultParams(),
 		},
+		{
+			"success: no legacy params pre-migration",
+			func() {
+				suite.chainA.GetSimApp().ICAControllerKeeper = icacontrollerkeeper.NewKeeper(
+					suite.chainA.Codec,
+					suite.chainA.GetSimApp().GetKey(icacontrollertypes.StoreKey),
+					nil, // assign a nil legacy param subspace
+					suite.chainA.GetSimApp().IBCKeeper.ChannelKeeper,
+					suite.chainA.GetSimApp().IBCKeeper.ChannelKeeper,
+					suite.chainA.GetSimApp().IBCKeeper.PortKeeper,
+					suite.chainA.GetSimApp().ScopedICAControllerKeeper,
+					suite.chainA.GetSimApp().MsgServiceRouter(),
+					suite.chainA.GetSimApp().ICAControllerKeeper.GetAuthority(),
+				)
+			},
+			icacontrollertypes.DefaultParams(),
+		},
 	}
 
 	for _, tc := range testCases {
```

### modules/apps/27-interchain-accounts/host/keeper/migrations.go
```diff
@@ -21,9 +21,10 @@ func NewMigrator(k *Keeper) Migrator {
 // MigrateParams migrates the host submodule's parameters from the x/params to self store.
 func (m Migrator) MigrateParams(ctx sdk.Context) error {
 	if m.keeper != nil {
-		var params types.Params
-		m.keeper.legacySubspace.GetParamSet(ctx, &params)
-
+		params := types.DefaultParams()
+		if m.keeper.legacySubspace != nil {
+			m.keeper.legacySubspace.GetParamSetIfExists(ctx, &params)
+		}
 		if err := params.Validate(); err != nil {
 			return err
 		}
```

### modules/apps/27-interchain-accounts/host/keeper/migrations_test.go
```diff
@@ -3,6 +3,9 @@ package keeper_test
 import (
 	"fmt"
 
+	authtypes "github.com/cosmos/cosmos-sdk/x/auth/types"
+	govtypes "github.com/cosmos/cosmos-sdk/x/gov/types"
+
 	icahostkeeper "github.com/cosmos/ibc-go/v8/modules/apps/27-interchain-accounts/host/keeper"
 	icahosttypes "github.com/cosmos/ibc-go/v8/modules/apps/27-interchain-accounts/host/types"
 )
@@ -22,6 +25,25 @@ func (suite *KeeperTestSuite) TestMigratorMigrateParams() {
 			},
 			icahosttypes.DefaultParams(),
 		},
+		{
+			"success: no legacy params pre-migration",
+			func() {
+				suite.chainA.GetSimApp().ICAHostKeeper = icahostkeeper.NewKeeper(
+					suite.chainA.Codec,
+					suite.chainA.GetSimApp().GetKey(icahosttypes.StoreKey),
+					nil, // assign a nil legacy param subspace
+					suite.chainA.GetSimApp().IBCFeeKeeper,
+					suite.chainA.GetSimApp().IBCKeeper.ChannelKeeper,
+					suite.chainA.GetSimApp().IBCKeeper.PortKeeper,
+					suite.chainA.GetSimApp().AccountKeeper,
+					suite.chainA.GetSimApp().ScopedICAHostKeeper,
+					suite.chainA.GetSimApp().MsgServiceRouter(),
+					suite.chainA.GetSimApp().GRPCQueryRouter(),
+					authtypes.NewModuleAddress(govtypes.ModuleName).String(),
+				)
+			},
+			icahosttypes.DefaultParams(),
+		},
 	}
 
 	for _, tc := range testCases {
```

### modules/apps/27-interchain-accounts/types/expected_keepers.go
```diff
@@ -37,4 +37,5 @@ type PortKeeper interface {
 // ParamSubspace defines the expected Subspace interface for module parameters.
 type ParamSubspace interface {
 	GetParamSet(ctx sdk.Context, ps paramtypes.ParamSet)
+	GetParamSetIfExists(ctx sdk.Context, ps paramtypes.ParamSet)
 }
```
