# [?] Merge pull request from GHSA-86h5-xcpx-cfqc

## Summary
Severity: Unknown
Chain: Cosmos
Component: cosmos/cosmos-sdk
Published: 2024-02-27
Source: https://github.com/cosmos/cosmos-sdk/commit/8585d538f10f00d9c4526efb21886dc0336fcf83
Type: security-commit

## Details
Merge pull request from GHSA-86h5-xcpx-cfqc

* check undelegation after redelegation

* add comment

* using app v1

* set up test

* update test

* Update x/staking/keeper/slash.go

Co-authored-by: Aleksandr Bezobchuk <alexanderbez@users.noreply.github.com>

* use switch inside slashing logic

* update slash redelegation test

---------

Co-authored-by: Hieu Vu <72878483+hieuvubk@users.noreply.github.com>
Co-authored-by: Aleksandr Bezobchuk <alexanderbez@users.noreply.github.com>
Co-authored-by: Julien Robert <julien@rbrt.fr>

## Patch
### testutil/sims/app_helpers.go
```diff
@@ -17,11 +17,13 @@ import (
 	banktypes "cosmossdk.io/x/bank/types"
 	stakingtypes "cosmossdk.io/x/staking/types"
 
+	coreheader "cosmossdk.io/core/header"
 	"github.com/cosmos/cosmos-sdk/client/flags"
 	"github.com/cosmos/cosmos-sdk/codec"
 	codectypes "github.com/cosmos/cosmos-sdk/codec/types"
 	cryptocodec "github.com/cosmos/cosmos-sdk/crypto/codec"
 	"github.com/cosmos/cosmos-sdk/crypto/keys/secp256k1"
+
 	"github.com/cosmos/cosmos-sdk/runtime"
 	servertypes "github.com/cosmos/cosmos-sdk/server/types"
 	"github.com/cosmos/cosmos-sdk/testutil/mock"
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
@@ -0,0 +1,165 @@
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
+	bankkeeper "cosmossdk.io/x/bank/keeper"
+	banktestutil "cosmossdk.io/x/bank/testutil"
+	slashingkeeper "cosmossdk.io/x/slashing/keeper"
+	"cosmossdk.io/x/slashing/testutil"
+	stakingkeeper "cosmossdk.io/x/staking/keeper"
+	stakingtypes "cosmossdk.io/x/staking/types"
+
+	distributionkeeper "cosmossdk.io/x/distribution/keeper"
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
+	ctx = ctx.WithBlockHeight(1).WithHeaderInfo(header.Info{Height: 1})
+	// next block, commit height 1, move to height 2
+	// acc 1 and acc 2 delegate to evil val
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
+	// next block, commit height 2, move to height 3
+	// with the new delegations, evil val increases in voting power and commit byzantine behaviour at height 3 consensus
+	// at the same time, acc 1 and acc 2 withdraw delegation from evil val
+	ctx, err = simtestutil.NextBlock(app, ctx, time.Duration(1))
+	require.NoError(t, err)
+
+	evilVal, err := stakingKeeper.GetValidator(ctx, evilValAddr)
+	require.NoError(t, err)
+
+	evilPower := stakingKeeper.TokensToConsensusPower(ctx, evilVal.Tokens)
+	fmt.Println(evilPower)
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
+	// next block, commit height 3, move to height 4
+	// Slash evil val for byzantine behaviour at height 3 consensus,
+	// at which acc 1 and acc 2 still contributed to evil val voting power
+	// even tho they undelegate at block 3, the valset update is applied after commited block 3 when height 3 consensus already passes
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
@@ -332,9 +332,43 @@ func (k Keeper) SlashRedelegation(ctx context.Context, srcValidator types.Valida
 		slashAmount := slashAmountDec.TruncateInt()
 		totalSlashAmount = totalSlashAmount.Add(slashAmount)
 
+		// Handle undelegation after redelegation
+		// Prioritize slashing unbondingDelegation than delegation
+		unbondingDelegation, err := k.UnbondingDelegations.Get(ctx, collections.Join(delegatorAddress, valDstAddr))
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
 		// Unbond from target validator
 		sharesToUnbond := slashFactor.Mul(entry.SharesDst)
-		if sharesToUnbond.IsZero() {
+		if sharesToUnbond.IsZero() || slashAmount.IsZero() {
 			continue
 		}
 
```
