# [?] fix: guard burned-fee tracker mint against overflow (#2371, private:#73)

## Summary
Severity: Unknown
Chain: Axelar
Component: axelarnetwork/axelar-core
Published: 2026-08-27
Source: https://github.com/axelarnetwork/axelar-core/commit/3ea7f4a29d8f01c6d59ed07a25c7c1453982af40
Type: security-commit

## Details
fix: guard burned-fee tracker mint against overflow (#2371, private:#73)

## Patch
### x/distribution/keeper/keeper.go
```diff
@@ -3,16 +3,17 @@ package keeper
 import (
 	"context"
 
+	"cosmossdk.io/log"
 	abci "github.com/cometbft/cometbft/abci/types"
 	"github.com/cosmos/cosmos-sdk/telemetry"
 	sdk "github.com/cosmos/cosmos-sdk/types"
 	distribution "github.com/cosmos/cosmos-sdk/x/distribution/keeper"
 	distributionTypes "github.com/cosmos/cosmos-sdk/x/distribution/types"
 
+	"github.com/axelarnetwork/axelar-core/utils"
 	"github.com/axelarnetwork/axelar-core/utils/events"
 	"github.com/axelarnetwork/axelar-core/x/distribution/types"
 	"github.com/axelarnetwork/utils/funcs"
-	"github.com/axelarnetwork/utils/slices"
 )
 
 // Keeper wraps the distribution keeper to customize fee allocation mechanism
@@ -38,6 +39,11 @@ func NewKeeper(
 	}
 }
 
+// Logger returns a module-specific logger.
+func (k Keeper) Logger(ctx sdk.Context) log.Logger {
+	return ctx.Logger().With("module", "x/"+distributionTypes.ModuleName)
+}
+
 // AllocateTokens modifies the fee distribution by:
 // - Allocating the community tax portion to the community pool
 // - Burning all remaining tokens instead of distributing to validators
@@ -86,14 +92,29 @@ func (k Keeper) AllocateTokens(ctx context.Context, _ int64, _ []abci.VoteInfo)
 		Coins: feesToBurn,
 	})
 
-	// track cumulative burned fees
-	feesBurned := slices.Map(feesToBurn, types.WithBurnedPrefix)
-	err = k.bankKeeper.MintCoins(ctx, distributionTypes.ModuleName, feesBurned)
-	if err != nil {
-		return err
+	// Track cumulative burned fees
+	for _, coin := range feesToBurn {
+		success := utils.RunCached(sdkCtx, k, func(ctx sdk.Context) (bool, error) {
+			feesBurned := sdk.NewCoins(types.WithBurnedPrefix(coin))
+			if err := k.bankKeeper.MintCoins(ctx, distributionTypes.ModuleName, feesBurned); err != nil {
+				return false, err
+			}
+			if err := k.bankKeeper.SendCoinsFromModuleToAccount(ctx, distributionTypes.ModuleName, types.ZeroAddress, feesBurned); err != nil {
+				return false, err
+			}
+
+			return true, nil
+		})
+
+		if !success {
+			k.Logger(sdkCtx).Error("burned-fee tracker update rolled back; fees are still burned",
+				"denom", coin.Denom,
+				"amount", coin.Amount.String(),
+			)
+		}
 	}
 
-	return k.bankKeeper.SendCoinsFromModuleToAccount(ctx, distributionTypes.ModuleName, types.ZeroAddress, feesBurned)
+	return nil
 }
 
 // BeginBlocker mirrors the cosmos-sdk distribution keeper's BeginBlocker
```

### x/distribution/keeper/keeper_test.go
```diff
@@ -2,6 +2,7 @@ package keeper_test
 
 import (
 	"context"
+	"math/big"
 	"testing"
 
 	"cosmossdk.io/log"
@@ -225,3 +226,115 @@ func expectedBurnAndTax(ctx sdk.Context, k keeper.Keeper, fee sdk.Coins) (sdk.Co
 
 	return burnAmt, tax.Add(remainder...)
 }
+
+// buildDistrKeeper wires an axelar distribution keeper backed by the given
+// mutable balance map, mirroring the setup in TestAllocateTokens.
+func buildDistrKeeper(t *testing.T, ctx sdk.Context, accBalances map[string]sdk.Coins) (keeper.Keeper, *mock.BankKeeperMock) {
+	encCfg := params.MakeEncodingConfig()
+	ak := &mock.AccountKeeperMock{
+		GetModuleAccountFunc: func(_ context.Context, name string) sdk.ModuleAccountI {
+			return authtypes.NewEmptyModuleAccount(name)
+		},
+		GetModuleAddressFunc: func(name string) sdk.AccAddress { return authtypes.NewModuleAddress(name) },
+	}
+	bk := &mock.BankKeeperMock{
+		GetAllBalancesFunc: func(_ context.Context, addr sdk.AccAddress) sdk.Coins { return accBalances[addr.String()] },
+		SendCoinsFromModuleToModuleFunc: func(_ context.Context, s, r string, amt sdk.Coins) error {
+			s, r = authtypes.NewModuleAddress(s).String(), authtypes.NewModuleAddress(r).String()
+			accBalances[s], accBalances[r] = accBalances[s].Sub(amt...), accBalances[r].Add(amt...)
+			return nil
+		},
+		SendCoinsFromModuleToAccountFunc: func(_ context.Context, s string, r sdk.AccAddress, amt sdk.Coins) error {
+			s = authtypes.NewModuleAddress(s).String()
+			accBalances[s], accBalances[r.String()] = accBalances[s].Sub(amt...), accBalances[r.String()].Add(amt...)
+			return nil
+		},
+		BurnCoinsFunc: func(_ context.Context, name string, amt sdk.Coins) error {
+			a := authtypes.NewModuleAddress(name).String()
+			accBalances[a] = accBalances[a].Sub(amt...)
+			return nil
+		},
+		MintCoinsFunc: func(_ context.Context, name string, amt sdk.Coins) error {
+			a := authtypes.NewModuleAddress(name).String()
+			accBalances[a] = accBalances[a].Add(amt...)
+			return nil
+		},
+	}
+	sk := &mock.StakingKeeperMock{}
+
+	distriK := distribution.NewKeeper(encCfg.Codec, runtime.NewKVStoreService(store.NewKVStoreKey(distributiontypes.StoreKey)), ak, bk, sk, authtypes.FeeCollectorName, "")
+	k := keeper.NewKeeper(distriK, ak, bk, sk, authtypes.FeeCollectorName)
+	funcs.MustNoErr(k.FeePool.Set(ctx, distributiontypes.FeePool{CommunityPool: sdk.DecCoins{}}))
+	funcs.MustNoErr(k.Params.Set(ctx, distributiontypes.DefaultParams()))
+
+	return k, bk
+}
+
+func maxInt() math.Int {
+	return math.NewIntFromBigInt(new(big.Int).Sub(new(big.Int).Lsh(big.NewInt(1), 256), big.NewInt(1)))
+}
+
+func TestAllocateTokensBurnsButRollsBackOverflowingTracker(t *testing.T) {
+	const denom = "ibc/OVERFLOW"
+	feeCollector := authtypes.NewModuleAddress(authtypes.FeeCollectorName).String()
+	burnedDenom := types.WithBurnedPrefix(sdk.NewCoin(denom, math.OneInt())).Denom
+	fee := math.NewInt(1_000_000)
+
+	ctx := sdk.NewContext(fake.NewMultiStore(), tmproto.Header{}, false, log.NewTestLogger(t))
+	accBalances := map[string]sdk.Coins{
+		feeCollector: sdk.NewCoins(sdk.NewCoin(denom, fee)),
+		// the cumulative burned-<denom> tracker is already at the 256-bit max, so
+		// minting more of it would overflow
+		types.ZeroAddress.String(): sdk.NewCoins(sdk.NewCoin(burnedDenom, maxInt())),
+	}
+
+	k, bk := buildDistrKeeper(t, ctx, accBalances)
+
+	// AllocateTokens must not panic ...
+	assert.NotPanics(t, func() { funcs.MustNoErr(k.AllocateTokens(ctx, 0, nil)) })
+
+	// ... the fee is processed out of the fee collector (not left stuck) ...
+	assert.True(t, accBalances[feeCollector].AmountOf(denom).IsZero())
+
+	// ... it is still burned ...
+	assert.NotEmpty(t, bk.BurnCoinsCalls())
+	if len(bk.BurnCoinsCalls()) > 0 {
+		assert.True(t, bk.BurnCoinsCalls()[0].Amt.AmountOf(denom).IsPositive())
+	}
+
+	// ... but the burned-<denom> tracker was not grown (update rolled back).
+	assert.Equal(t, maxInt(), accBalances[types.ZeroAddress.String()].AmountOf(burnedDenom))
+}
+
+func TestAllocateTokensTracksHealthyDenomsWhenAnotherOverflows(t *testing.T) {
+	const overflowDenom = "ibc/OVERFLOW"
+	const healthyDenom = "uaxl"
+	feeCollector := authtypes.NewModuleAddress(authtypes.FeeCollectorName).String()
+	burnedOverflow := types.WithBurnedPrefix(sdk.NewCoin(overflowDenom, math.OneInt())).Denom
+	burnedHealthy := types.WithBurnedPrefix(sdk.NewCoin(healthyDenom, math.OneInt())).Denom
+
+	ctx := sdk.NewContext(fake.NewMultiStore(), tmproto.Header{}, false, log.NewTestLogger(t))
+	accBalances := map[string]sdk.Coins{
+		feeCollector: sdk.NewCoins(
+			sdk.NewCoin(overflowDenom, math.NewInt(1_000_000)),
+			sdk.NewCoin(healthyDenom, math.NewInt(1_000_000)),
+		),
+		// only the overflow denom's tracker is maxed out
+		types.ZeroAddress.String(): sdk.NewCoins(sdk.NewCoin(burnedOverflow, maxInt())),
+	}
+
+	k, bk := buildDistrKeeper(t, ctx, accBalances)
+
+	assert.NotPanics(t, func() { funcs.MustNoErr(k.AllocateTokens(ctx, 0, nil)) })
+
+	// both denoms are drained from the fee collector and burned
+	assert.True(t, accBalances[feeCollector].IsZero())
+	assert.Len(t, bk.BurnCoinsCalls(), 1)
+	assert.True(t, bk.BurnCoinsCalls()[0].Amt.AmountOf(overflowDenom).IsPositive())
+	assert.True(t, bk.BurnCoinsCalls()[0].Amt.AmountOf(healthyDenom).IsPositive())
+
+	// the overflowing denom's tracker is left untouched ...
+	assert.Equal(t, maxInt(), accBalances[types.ZeroAddress.String()].AmountOf(burnedOverflow))
+	// ... but the healthy denom is still tracked
+	assert.True(t, accBalances[types.ZeroAddress.String()].AmountOf(burnedHealthy).IsPositive())
+}
```
