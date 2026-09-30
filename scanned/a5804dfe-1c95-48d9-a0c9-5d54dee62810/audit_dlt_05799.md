# [?] Fix panic edge case in superfluid AfterEpochEnd hook by surrounding CL multipler update with ApplyFuncIfNoError (#6231)

## Summary
Severity: Unknown
Chain: Osmosis
Component: osmosis-labs/osmosis
Published: 2023-08-29
Source: https://github.com/osmosis-labs/osmosis/commit/32cdadfaea4a160ac5a78d4127e6dd5f0f9764d1
Type: security-commit

## Details
Fix panic edge case in superfluid AfterEpochEnd hook by surrounding CL multipler update with ApplyFuncIfNoError (#6231)

* Fix panic edge case in superfluid AfterEpochEnd hook by surrounding CL multipler update with ApplyFuncIfNoError

* fix tests

* updates

* updates

## Patch
### CHANGELOG.md
```diff
@@ -47,6 +47,8 @@ and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0
 ### Bug Fixes
 * [#6190](https://github.com/osmosis-labs/osmosis/pull/6190) v19 upgrade handler superfluid fix
 * [#6195](https://github.com/osmosis-labs/osmosis/pull/6195) (x/tokenfactory) Fix events for `mintTo` and `burnFrom`
+* [#6195](https://github.com/osmosis-labs/osmosis/pull/6195) Fix panic edge case in superfluid AfterEpochEnd hook by surrounding CL multipler update with ApplyFuncIfNoError
+
 ### Misc Improvements
 
 ### Minor improvements & Bug Fixes
```

### x/incentives/keeper/distribute.go
```diff
@@ -327,7 +327,6 @@ func (k Keeper) calcSplitPolicyCoins(ctx sdk.Context, policy types.SplittingPoli
 	} else {
 		return nil, nil, fmt.Errorf("GroupGauge id %d doesnot have enought coins to distribute.", &groupGauge.Id)
 	}
-
 }
 
 // distributeInternal runs the distribution logic for a gauge, and adds the sends to
@@ -528,7 +527,7 @@ func (k Keeper) Distribute(ctx sdk.Context, gauges []types.Gauge) (sdk.Coins, er
 			ctx.Logger().Debug("distributeSyntheticInternal, gauge id %d, %d", "module", types.ModuleName, "gaugeId", gauge.Id, "height", ctx.BlockHeight())
 			gaugeDistributedCoins, err = k.distributeSyntheticInternal(ctx, gauge, filteredLocks, &distrInfo)
 		} else {
-			// Do not distribue if LockQueryType = Group, because if we distribute here we will be double distributing.
+			// Do not distribute if LockQueryType = Group, because if we distribute here we will be double distributing.
 			if gauge.DistributeTo.LockQueryType == lockuptypes.ByGroup {
 				continue
 			}
```

### x/incentives/types/keys.go
```diff
@@ -71,5 +71,4 @@ func NoLockInternalGaugeDenom(poolId uint64) string {
 // KeyGroupGaugeForId returns key for a given groupGaugeId.
 func KeyGroupGaugeForId(groupGaugeId uint64) []byte {
 	return []byte(fmt.Sprintf("%s%s%d%s", GroupGaugePrefix, "|", groupGaugeId, "|"))
-
 }
```

### x/superfluid/keeper/epoch.go
```diff
@@ -45,10 +45,10 @@ func (k Keeper) AfterEpochStartBeginBlock(ctx sdk.Context) {
 	for _, asset := range k.GetAllSuperfluidAssets(ctx) {
 		err := k.UpdateOsmoEquivalentMultipliers(ctx, asset, curEpoch)
 		if err != nil {
-			// TODO: Revisit what we do here. (halt all distr, only skip this asset)
-			// Since at MVP of feature, we only have one pool of superfluid staking,
-			// we can punt this question.
-			// each of the errors feels like significant misconfig
+			// UPDATE: balancer pools are expected to be skipped only on error due to being
+			// already well tested in production.
+			//
+			// CL pools are surrounded by ApplyFuncIfNoError, so they are silently skipped on error or panic.
 			return
 		}
 	}
@@ -138,57 +138,66 @@ func (k Keeper) UpdateOsmoEquivalentMultipliers(ctx sdk.Context, asset types.Sup
 		multiplier := k.calculateOsmoBackingPerShare(pool, osmoPoolAsset)
 		k.SetOsmoEquivalentMultiplier(ctx, newEpochNumber, asset.Denom, multiplier)
 	} else if asset.AssetType == types.SuperfluidAssetTypeConcentratedShare {
-		// LP_token_Osmo_equivalent = OSMO_amount_on_pool / LP_token_supply
-		poolId := cltypes.MustGetPoolIdFromShareDenom(asset.Denom)
-		pool, err := k.clk.GetConcentratedPoolById(ctx, poolId)
-		if err != nil {
-			k.Logger(ctx).Error(err.Error())
-			// Pool has unexpectedly removed Osmo from its assets.
-			k.BeginUnwindSuperfluidAsset(ctx, 0, asset)
-			return err
-		}
-
-		// get underlying assets from all liquidity in a full range position
-		// note: this is not the same as the total liquidity in the pool, as this includes positions not in the full range
-		bondDenom := k.sk.BondDenom(ctx)
-		fullRangeLiquidity, err := k.clk.GetFullRangeLiquidityInPool(ctx, poolId)
-		if err != nil {
-			k.Logger(ctx).Error(err.Error())
-			k.BeginUnwindSuperfluidAsset(ctx, 0, asset)
-			return fmt.Errorf("failed to retrieve full range liquidity from pool (%d): %w", poolId, err)
-		}
-
-		position := model.Position{
-			LowerTick: cltypes.MinInitializedTick,
-			UpperTick: cltypes.MaxTick,
-			Liquidity: fullRangeLiquidity,
-		}
-		// Note that the returned amounts are rounded up. This should be fine as they both are used for calculating the multiplier.
-		asset0, asset1, err := cl.CalculateUnderlyingAssetsFromPosition(ctx, position, pool)
-		if err != nil {
-			k.Logger(ctx).Error(err.Error())
-			k.BeginUnwindSuperfluidAsset(ctx, 0, asset)
-			return err
-		}
-		assets := sdk.NewCoins(asset0, asset1)
-
-		// get OSMO amount from underlying assets
-		osmoPoolAsset := assets.AmountOf(bondDenom)
-		if osmoPoolAsset.IsZero() {
-			// Pool has unexpectedly removed OSMO from its assets.
-			err := errors.New("pool has unexpectedly removed OSMO as one of its underlying assets")
-			k.Logger(ctx).Error(err.Error())
-			k.BeginUnwindSuperfluidAsset(ctx, 0, asset)
-			return err
-		}
-
-		// calculate multiplier and set it
-		multiplier := osmoPoolAsset.ToDec().Quo(fullRangeLiquidity)
-		k.SetOsmoEquivalentMultiplier(ctx, newEpochNumber, asset.Denom, multiplier)
+		// https://github.com/osmosis-labs/osmosis/issues/6229
+		osmoutils.ApplyFuncIfNoError(ctx, func(cacheCtx sdk.Context) error {
+			return k.updateConcentratedOsmoEquivalentMultiplier(cacheCtx, asset, newEpochNumber)
+		})
 	} else if asset.AssetType == types.SuperfluidAssetTypeNative {
 		// TODO: Consider deleting superfluid asset type native
 		k.Logger(ctx).Error("unsupported superfluid asset type")
 		return errors.New("SuperfluidAssetTypeNative is unsupported")
 	}
 	return nil
 }
+
+// updateConcentratedOsmoEquivalentMultiplier runs the logic for updating the OSMO equivalent multiplier for a concentrated liquidity pool.
+func (k Keeper) updateConcentratedOsmoEquivalentMultiplier(ctx sdk.Context, asset types.SuperfluidAsset, newEpochNumber int64) error {
+	// LP_token_Osmo_equivalent = OSMO_amount_on_pool / LP_token_supply
+	poolId := cltypes.MustGetPoolIdFromShareDenom(asset.Denom)
+	pool, err := k.clk.GetConcentratedPoolById(ctx, poolId)
+	if err != nil {
+		k.Logger(ctx).Error(err.Error())
+		// Pool has unexpectedly removed Osmo from its assets.
+		k.BeginUnwindSuperfluidAsset(ctx, 0, asset)
+		return err
+	}
+
+	// get underlying assets from all liquidity in a full range position
+	// note: this is not the same as the total liquidity in the pool, as this includes positions not in the full range
+	bondDenom := k.sk.BondDenom(ctx)
+	fullRangeLiquidity, err := k.clk.GetFullRangeLiquidityInPool(ctx, poolId)
+	if err != nil {
+		k.Logger(ctx).Error(err.Error())
+		return fmt.Errorf("failed to retrieve full range liquidity from pool (%d): %w", poolId, err)
+	}
+
+	position := model.Position{
+		LowerTick: cltypes.MinInitializedTick,
+		UpperTick: cltypes.MaxTick,
+		Liquidity: fullRangeLiquidity,
+	}
+	// Note that the returned amounts are rounded up. This should be fine as they both are used for calculating the multiplier.
+	asset0, asset1, err := cl.CalculateUnderlyingAssetsFromPosition(ctx, position, pool)
+	if err != nil {
+		k.Logger(ctx).Error(err.Error())
+		k.BeginUnwindSuperfluidAsset(ctx, 0, asset)
+		return err
+	}
+	assets := sdk.NewCoins(asset0, asset1)
+
+	// get OSMO amount from underlying assets
+	osmoPoolAsset := assets.AmountOf(bondDenom)
+	if osmoPoolAsset.IsZero() {
+		// Pool has unexpectedly removed OSMO from its assets.
+		err := errors.New("pool has unexpectedly removed OSMO as one of its underlying assets")
+		k.Logger(ctx).Error(err.Error())
+		k.BeginUnwindSuperfluidAsset(ctx, 0, asset)
+		return err
+	}
+
+	// calculate multiplier and set it
+	multiplier := osmoPoolAsset.ToDec().Quo(fullRangeLiquidity)
+	k.SetOsmoEquivalentMultiplier(ctx, newEpochNumber, asset.Denom, multiplier)
+
+	return nil
+}
```

### x/superfluid/keeper/epoch_test.go
```diff
@@ -17,12 +17,13 @@ import (
 
 func (s *KeeperTestSuite) TestUpdateOsmoEquivalentMultipliers() {
 	testCases := []struct {
-		name               string
-		asset              types.SuperfluidAsset
-		expectedMultiplier sdk.Dec
-		removeStakingAsset bool
-		poolDoesNotExist   bool
-		expectedError      error
+		name                  string
+		asset                 types.SuperfluidAsset
+		expectedMultiplier    sdk.Dec
+		removeStakingAsset    bool
+		poolDoesNotExist      bool
+		expectedError         error
+		expectedZeroMultipler bool
 	}{
 		{
 			name:               "update LP token Osmo equivalent successfully",
@@ -50,13 +51,15 @@ func (s *KeeperTestSuite) TestUpdateOsmoEquivalentMultipliers() {
 			name:             "update concentrated share Osmo equivalent with pool unexpectedly deleted",
 			asset:            types.SuperfluidAsset{Denom: cltypes.GetConcentratedLockupDenomFromPoolId(1), AssetType: types.SuperfluidAssetTypeConcentratedShare},
 			poolDoesNotExist: true,
-			expectedError:    cltypes.PoolNotFoundError{PoolId: 1},
+			// Note: this does not error since CL errors are surrounded in `ApplyFuncIfNoError`
+			expectedZeroMultipler: true,
 		},
 		{
 			name:               "update concentrated share Osmo equivalent with pool unexpectedly removed Osmo",
 			asset:              types.SuperfluidAsset{Denom: cltypes.GetConcentratedLockupDenomFromPoolId(1), AssetType: types.SuperfluidAssetTypeConcentratedShare},
 			removeStakingAsset: true,
-			expectedError:      errors.New("pool has unexpectedly removed OSMO as one of its underlying assets"),
+			// Note: this does not error since CL errors are surrounded in `ApplyFuncIfNoError`
+			expectedZeroMultipler: true,
 		},
 	}
 
@@ -106,7 +109,13 @@ func (s *KeeperTestSuite) TestUpdateOsmoEquivalentMultipliers() {
 
 				// Check that multiplier was set correctly
 				multiplier := superfluidKeeper.GetOsmoEquivalentMultiplier(ctx, tc.asset.Denom)
-				s.Require().NotEqual(multiplier, sdk.ZeroDec())
+
+				if !tc.expectedZeroMultipler {
+					s.Require().NotEqual(multiplier, sdk.ZeroDec())
+				} else {
+					// Zero on success is expected on CL errors since those are surrounded with `ApplyFuncIfNoError`
+					s.Require().Equal(multiplier, sdk.ZeroDec())
+				}
 			}
 		})
 	}
```
