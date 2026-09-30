# [?] Merge pull request from GHSA-86h5-xcpx-cfqc

## Summary
Severity: Unknown
Chain: Cosmos
Component: cosmos/cosmos-sdk
Published: 2024-02-27
Source: https://github.com/cosmos/cosmos-sdk/commit/c21c8249c853da334f56fc84846abf371f41ff6d
Type: security-commit

## Details
Merge pull request from GHSA-86h5-xcpx-cfqc

* fix slashing hole with test

* release notes + changelog

* word

* date

* updates

---------

Co-authored-by: Julien Robert <julien@rbrt.fr>

## Patch
### CHANGELOG.md
```diff
@@ -38,11 +38,14 @@ Ref: https://keepachangelog.com/en/1.0.0/
 
 ## [Unreleased]
 
+## [v0.50.5](https://github.com/cosmos/cosmos-sdk/releases/tag/v0.50.5) - 2024-XX-XX
+
 ### Bug Fixes
 
 * (x/auth) [#19549](https://github.com/cosmos/cosmos-sdk/pull/19549) Accept custom get signers when injecting `x/auth/tx`.
+* (x/staking) Fix a possible bypass of delagator slashing: [GHSA-86h5-xcpx-cfqc](https://github.com/cosmos/cosmos-sdk/security/advisories/GHSA-86h5-xcpx-cfqc)
 
-## [v0.50.4](https://github.com/cosmos/cosmos-sdk/releases/tag/v0.50.4) - 2023-02-19
+## [v0.50.4](https://github.com/cosmos/cosmos-sdk/releases/tag/v0.50.4) - 2024-02-19
 
 ### Features
 
@@ -62,7 +65,7 @@ Ref: https://keepachangelog.com/en/1.0.0/
 * (baseapp) [#19177](https://github.com/cosmos/cosmos-sdk/pull/19177) Fix baseapp `DefaultProposalHandler` same-sender non-sequential sequence.
 * (crypto) [#19371](https://github.com/cosmos/cosmos-sdk/pull/19371) Avoid CLI redundant log in stdout, log to stderr instead.
 
-## [v0.50.3](https://github.com/cosmos/cosmos-sdk/releases/tag/v0.50.3) - 2023-01-15
+## [v0.50.3](https://github.com/cosmos/cosmos-sdk/releases/tag/v0.50.3) - 2024-01-15
 
 ### Features
 
```

### RELEASE_NOTES.md
```diff
@@ -1,24 +1,20 @@
-# Cosmos SDK v0.50.4 Release Notes
+# Cosmos SDK v0.50.5 Release Notes
 
 💬 [**Release Discussion**](https://github.com/orgs/cosmos/discussions/58)
 
 ## 🚀 Highlights
 
-Some months ago Cosmos SDK Eden was released. Missed the announcement? Read it [here](https://github.com/cosmos/cosmos-sdk/releases/tag/v0.50.1).
-For this month patch release of the v0.50.x line, a few features and improvements were added to the SDK.
+While early in our monthly release cadence, this release includes a few notable fixes:
 
-Notably, we added and fixed the following:
-
-* Adds in-place testnet CLI command for creating testnets from local state (kudos to @czarcas7ic)
-* Multiple fixes in baseapp, with fixes in `DefaultProposalHandler` and vote extensions
-* Add a missed check in `x/auth/vesting`: [GHSA-4j93-fm92-rp4m](https://github.com/cosmos/cosmos-sdk/security/advisories/GHSA-4j93-fm92-rp4m)
+* Fix a bypass delagator slashing: [GHSA-86h5-xcpx-cfqc](https://github.com/cosmos/cosmos-sdk/security/advisories/GHSA-86h5-xcpx-cfqc)
+* Allow to provide custom signers for `x/auth/tx` using depinject
 
 We recommended to upgrade to this patch release as soon as possible.  
 When upgrading from <= v0.50.3, please ensure that 2/3 of the validator power upgrade to v0.50.4.
 
 ## 📝 Changelog
 
-Check out the [changelog](https://github.com/cosmos/cosmos-sdk/blob/v0.50.4/CHANGELOG.md) for an exhaustive list of changes, or [compare changes](https://github.com/cosmos/cosmos-sdk/compare/release/v0.50.3...v0.50.4) from the last release.
+Check out the [changelog](https://github.com/cosmos/cosmos-sdk/blob/v0.50.5/CHANGELOG.md) for an exhaustive list of changes, or [compare changes](https://github.com/cosmos/cosmos-sdk/compare/release/v0.50.4...v0.50.5) from the last release.
 
 Refer to the [upgrading guide](https://github.com/cosmos/cosmos-sdk/blob/release/v0.50.x/UPGRADING.md) when migrating from `v0.47.x` to `v0.50.1`.
 Note, that the next SDK release, v0.51.0, will not include `x/params` migration, when migrating from < v0.47, v0.50.x **or** v0.47.x, is a mandatory migration.
```

### testutil/sims/app_helpers.go
```diff
@@ -11,6 +11,8 @@ import (
 	cmttypes "github.com/cometbft/cometbft/types"
 	dbm "github.com/cosmos/cosmos-db"
 
+	coreheader "cosmossdk.io/core/header"
+
 	"cosmossdk.io/depinject"
 	sdkmath "cosmossdk.io/math"
 
@@ -107,6 +109,35 @@ func SetupAtGenesis(appConfig depinject.Config, extraOutputs ...interface{}) (*r
 	return SetupWithConfiguration(appConfig, cfg, extraOutputs...)
 }
 
+// NextBlock starts a new block.
+func NextBlock(app *runtime.App, ctx sdk.Context, jumpTime time.Duration) (sdk.Context, error) {
+	_, err := app.FinalizeBlock(&abci.RequestFinalizeBlock{Height: ctx.BlockHeight(), Time: ctx.BlockTime()})
+	if err != nil {
+		return sdk.Context{}, err
+	}
+	_, err = app.Commit()
+	if err != nil {
+		return sdk.Context{}, err
+	}
+
+	newBlockTime := ctx.BlockTime().Add(jumpTime)
+
+	header := ctx.BlockHeader()
+	header.Time = newBlockTime
+	header.Height = header.Height + 1
+
+	newCtx := app.BaseApp.NewUncachedContext(false, header).WithHeaderInfo(coreheader.Info{
+		Height: header.Height,
+		Time:   header.Time,
+	})
+
+	if err != nil {
+		return sdk.Context{}, err
+	}
+
+	return newCtx, err
+}
+
 // SetupWithConfiguration initializes a new runtime.App. A Nop logger is set in runtime.App.
 // appConfig defines the application configuration (f.e. app_config.go).
 // extraOutputs defines the extra outputs to be assigned by the dependency injector (depinject).
```

### x/slashing/keeper/slash_redelegation_test.go
```diff
@@ -0,0 +1,166 @@
+package keeper_test
+
+import (
+	"fmt"
+	"testing"
+	"time"
+
+	"cosmossdk.io/core/header"
+	"cosmossdk.io/depinject"
+	"cosmossdk.io/log"
+	"cosmossdk.io/math"
+	bankkeeper "github.com/cosmos/cosmos-sdk/x/bank/keeper"
+	banktestutil "github.com/cosmos/cosmos-sdk/x/bank/testutil"
+	slashingkeeper "github.com/cosmos/cosmos-sdk/x/slashing/keeper"
+	"github.com/cosmos/cosmos-sdk/x/slashing/testutil"
+	stakingkeeper "github.com/cosmos/cosmos-sdk/x/staking/keeper"
+	stakingtypes "github.com/cosmos/cosmos-sdk/x/staking/types"
+
+	distributionkeeper "github.com/cosmos/cosmos-sdk/x/distribution/keeper"
+
+	"github.com/cosmos/cosmos-sdk/crypto/keys/secp256k1"
+	sdk "github.com/cosmos/cosmos-sdk/types"
+	"github.com/stretchr/testify/require"
+
+	simtestutil "github.com/cosmos/cosmos-sdk/testutil/sims"
+)
+
+func TestSlashRedelegation(t *testing.T) {
+	// setting up
+	var stakingKeeper *stakingkeeper.Keeper
+	var bankKeeper bankkeeper.Keeper
+	var slashKeeper slashingkeeper.Keeper
+	var distrKeeper distributionkeeper.Keeper
+
+	app, err := simtestutil.Setup(depinject.Configs(
+		depinject.Supply(log.NewNopLogger()),
+		testutil.AppConfig,
+	), &stakingKeeper, &bankKeeper, &slashKeeper, &distrKeeper)
+	require.NoError(t, err)
+
+	// get sdk context, staking msg server and bond denom
+	ctx := app.BaseApp.NewContext(false)
+	stakingMsgServer := stakingkeeper.NewMsgServerImpl(stakingKeeper)
+	bondDenom, err := stakingKeeper.BondDenom(ctx)
+	require.NoError(t, err)
+
+	// evilVal will be slashed, goodVal won't be slashed
+	evilValPubKey := secp256k1.GenPrivKey().PubKey()
+	goodValPubKey := secp256k1.GenPrivKey().PubKey()
+
+	// both test acc 1 and 2 delegated to evil val, both acc should be slashed when evil val is slashed
+	// test acc 1 use the "undelegation after redelegation" trick (redelegate to good val and then undelegate) to avoid slashing
+	// test acc 2 only undelegate from evil val
+	testAcc1 := sdk.AccAddress([]byte("addr1_______________"))
+	testAcc2 := sdk.AccAddress([]byte("addr2_______________"))
+
+	// fund acc 1 and acc 2
+	testCoins := sdk.NewCoins(sdk.NewCoin(bondDenom, stakingKeeper.TokensFromConsensusPower(ctx, 10)))
+	banktestutil.FundAccount(ctx, bankKeeper, testAcc1, testCoins)
+	banktestutil.FundAccount(ctx, bankKeeper, testAcc2, testCoins)
+
+	balance1Before := bankKeeper.GetBalance(ctx, testAcc1, bondDenom)
+	balance2Before := bankKeeper.GetBalance(ctx, testAcc2, bondDenom)
+
+	// assert acc 1 and acc 2 balance
+	require.Equal(t, balance1Before.Amount.String(), testCoins[0].Amount.String())
+	require.Equal(t, balance2Before.Amount.String(), testCoins[0].Amount.String())
+
+	// creating evil val
+	evilValAddr := sdk.ValAddress(evilValPubKey.Address())
+	banktestutil.FundAccount(ctx, bankKeeper, sdk.AccAddress(evilValAddr), testCoins)
+	createValMsg1, _ := stakingtypes.NewMsgCreateValidator(
+		evilValAddr.String(), evilValPubKey, testCoins[0], stakingtypes.Description{Details: "test"}, stakingtypes.NewCommissionRates(math.LegacyNewDecWithPrec(5, 1), math.LegacyNewDecWithPrec(5, 1), math.LegacyNewDec(0)), math.OneInt())
+	_, err = stakingMsgServer.CreateValidator(ctx, createValMsg1)
+	require.NoError(t, err)
+
+	// creating good val
+	goodValAddr := sdk.ValAddress(goodValPubKey.Address())
+	banktestutil.FundAccount(ctx, bankKeeper, sdk.AccAddress(goodValAddr), testCoins)
+	createValMsg2, _ := stakingtypes.NewMsgCreateValidator(
+		goodValAddr.String(), goodValPubKey, testCoins[0], stakingtypes.Description{Details: "test"}, stakingtypes.NewCommissionRates(math.LegacyNewDecWithPrec(5, 1), math.LegacyNewDecWithPrec(5, 1), math.LegacyNewDec(0)), math.OneInt())
+	_, err = stakingMsgServer.CreateValidator(ctx, createValMsg2)
+	require.NoError(t, err)
+
+	// next block, commit height 2, move to height 3
+	// acc 1 and acc 2 delegate to evil val
+	ctx = ctx.WithBlockHeight(app.LastBlockHeight() + 1).WithHeaderInfo(header.Info{Height: app.LastBlockHeight() + 1})
+	fmt.Println()
+	ctx, err = simtestutil.NextBlock(app, ctx, time.Duration(1))
+	require.NoError(t, err)
+
+	// Acc 2 delegate
+	delMsg := stakingtypes.NewMsgDelegate(testAcc2.String(), evilValAddr.String(), testCoins[0])
+	_, err = stakingMsgServer.Delegate(ctx, delMsg)
+	require.NoError(t, err)
+
+	// Acc 1 delegate
+	delMsg = stakingtypes.NewMsgDelegate(testAcc1.String(), evilValAddr.String(), testCoins[0])
+	_, err = stakingMsgServer.Delegate(ctx, delMsg)
+	require.NoError(t, err)
+
+	// next block, commit height 3, move to height 4
+	// with the new delegations, evil val increases in voting power and commit byzantine behaviour at height 4 consensus
+	// at the same time, acc 1 and acc 2 withdraw delegation from evil val
+	ctx, err = simtestutil.NextBlock(app, ctx, time.Duration(1))
+	require.NoError(t, err)
+
+	evilVal, err := stakingKeeper.GetValidator(ctx, evilValAddr)
+	require.NoError(t, err)
+
+	evilPower := stakingKeeper.TokensToConsensusPower(ctx, evilVal.Tokens)
+
+	// Acc 1 redelegate from evil val to good val
+	redelMsg := stakingtypes.NewMsgBeginRedelegate(testAcc1.String(), evilValAddr.String(), goodValAddr.String(), testCoins[0])
+	_, err = stakingMsgServer.BeginRedelegate(ctx, redelMsg)
+	require.NoError(t, err)
+
+	// Acc 1 undelegate from good val
+	undelMsg := stakingtypes.NewMsgUndelegate(testAcc1.String(), goodValAddr.String(), testCoins[0])
+	_, err = stakingMsgServer.Undelegate(ctx, undelMsg)
+	require.NoError(t, err)
+
+	// Acc 2 undelegate from evil val
+	undelMsg = stakingtypes.NewMsgUndelegate(testAcc2.String(), evilValAddr.String(), testCoins[0])
+	_, err = stakingMsgServer.Undelegate(ctx, undelMsg)
+	require.NoError(t, err)
+
+	// next block, commit height 4, move to height 5
+	// Slash evil val for byzantine behaviour at height 4 consensus,
+	// at which acc 1 and acc 2 still contributed to evil val voting power
+	// even tho they undelegate at block 4, the valset update is applied after commited block 4 when height 4 consensus already passes
+	ctx, err = simtestutil.NextBlock(app, ctx, time.Duration(1))
+	require.NoError(t, err)
+
+	// slash evil val with slash factor = 0.9, leaving only 10% of stake after slashing
+	evilVal, _ = stakingKeeper.GetValidator(ctx, evilValAddr)
+	evilValConsAddr, err := evilVal.GetConsAddr()
+	require.NoError(t, err)
+
+	err = slashKeeper.Slash(ctx, evilValConsAddr, math.LegacyMustNewDecFromStr("0.9"), evilPower, 3)
+	require.NoError(t, err)
+
+	// assert invariant to make sure we conduct slashing correctly
+	_, stop := stakingkeeper.AllInvariants(stakingKeeper)(ctx)
+	require.False(t, stop)
+
+	_, stop = bankkeeper.AllInvariants(bankKeeper)(ctx)
+	require.False(t, stop)
+
+	_, stop = distributionkeeper.AllInvariants(distrKeeper)(ctx)
+	require.False(t, stop)
+
+	// one eternity later
+	ctx, err = simtestutil.NextBlock(app, ctx, time.Duration(1000000000000000000))
+	require.NoError(t, err)
+
+	ctx, err = simtestutil.NextBlock(app, ctx, time.Duration(1))
+	require.NoError(t, err)
+
+	// confirm that account 1 and account 2 has been slashed, and the slash amount is correct
+	balance1AfterSlashing := bankKeeper.GetBalance(ctx, testAcc1, bondDenom)
+	balance2AfterSlashing := bankKeeper.GetBalance(ctx, testAcc2, bondDenom)
+
+	require.Equal(t, balance1AfterSlashing.Amount.Mul(math.NewIntFromUint64(10)).String(), balance1Before.Amount.String())
+	require.Equal(t, balance2AfterSlashing.Amount.Mul(math.NewIntFromUint64(10)).String(), balance2Before.Amount.String())
+}
```

### x/staking/keeper/slash.go
```diff
@@ -326,9 +326,48 @@ func (k Keeper) SlashRedelegation(ctx context.Context, srcValidator types.Valida
 		slashAmount := slashAmountDec.TruncateInt()
 		totalSlashAmount = totalSlashAmount.Add(slashAmount)
 
+		validatorDstAddress, err := sdk.ValAddressFromBech32(redelegation.ValidatorDstAddress)
+		if err != nil {
+			panic(err)
+		}
+		// Handle undelegation after redelegation
+		// Prioritize slashing unbondingDelegation than delegation
+		unbondingDelegation, err := k.GetUnbondingDelegation(ctx, sdk.MustAccAddressFromBech32(redelegation.DelegatorAddress), validatorDstAddress)
+		if err == nil {
+			for i, entry := range unbondingDelegation.Entries {
+				// slash with the amount of `slashAmount` if possible, else slash all unbonding token
+				unbondingSlashAmount := math.MinInt(slashAmount, entry.Balance)
+
+				switch {
+				// There's no token to slash
+				case unbondingSlashAmount.IsZero():
+					continue
+				// If unbonding started before this height, stake didn't contribute to infraction
+				case entry.CreationHeight < infractionHeight:
+					continue
+				// Unbonding delegation no longer eligible for slashing, skip it
+				case entry.IsMature(now) && !entry.OnHold():
+					continue
+				// Slash the unbonding delegation
+				default:
+					// update remaining slashAmount
+					slashAmount = slashAmount.Sub(unbondingSlashAmount)
+
+					notBondedBurnedAmount = notBondedBurnedAmount.Add(unbondingSlashAmount)
+					entry.Balance = entry.Balance.Sub(unbondingSlashAmount)
+					unbondingDelegation.Entries[i] = entry
+					if err = k.SetUnbondingDelegation(ctx, unbondingDelegation); err != nil {
+						return math.ZeroInt(), err
+					}
+				}
+			}
+		}
+
+		// Slash the moved delegation
+
 		// Unbond from target validator
 		sharesToUnbond := slashFactor.Mul(entry.SharesDst)
-		if sharesToUnbond.IsZero() {
+		if sharesToUnbond.IsZero() || slashAmount.IsZero() {
 			continue
 		}
 
```
