# [?] fix: nondeterminism incentives `IterateBTCDelegationSatsUpdated` (#1805)

## Summary
Severity: Unknown
Chain: Babylon
Component: babylonlabs-io/babylon
Published: 2025-10-13
Source: https://github.com/babylonlabs-io/babylon/commit/3eefafe95e25e590a711db5a555f1f2cefad0e58
Type: security-commit

## Details
fix: nondeterminism incentives `IterateBTCDelegationSatsUpdated` (#1805)

Note: I was not able to reproduce it with replay testing only with unit
testing, so it might not be a problem but still think it is worth to
review it

## Patch
### CHANGELOG.md
```diff
@@ -54,8 +54,9 @@ baby ratio where it wasn't increasing the costaker cumulative rewards and neithe
 as the completely removal of an baby delegation doesn't calls `AfterDelegationModified
 - [#1790](https://github.com/babylonlabs-io/babylon/pull/1790) Fix withdraw reward to only error if both `BTC_STAKER` and `COSTAKER` types have zero rewards available.
 - [#1792](https://github.com/babylonlabs-io/babylon/pull/1792) Fix costaking baby bond unbond and bond again for the same delegation pair (del, val) in the same block
-- [#1800](https://github.com/babylonlabs-io/babylon/pull/1800) Handle co-staking edge cases for baby stakers 
+- [#1800](https://github.com/babylonlabs-io/babylon/pull/1800) Handle co-staking edge cases for baby stakers
 - [#1802](https://github.com/babylonlabs-io/babylon/pull/1802) Fix non-determinism in co-staking
+- [#1805](https://github.com/babylonlabs-io/babylon/pull/1805) Fix non-determinism in incentives `IterateBTCDelegationSatsUpdated`
 
 ## v4.0.0-rc.0
 
```

### test/replay/costaking_test.go
```diff
@@ -1295,11 +1295,11 @@ func TestBabyCoStaking(t *testing.T) {
 
 	// Redelegation msg made it to the last epoch block, so it is processed
 	// And the redelegation is slashed, so the tracker should be updated accordingly
-	del6Delegation, err := stkK.GetDelegation(d.Ctx(), del6.Address(), val2ValAddr)
+	_, err = stkK.GetDelegation(d.Ctx(), del6.Address(), val2ValAddr)
 	require.Error(d.t, err)
 	require.ErrorContains(d.t, err, "no delegation")
 
-	del6Delegation, err = stkK.GetDelegation(d.Ctx(), del6.Address(), val1ValAddr)
+	del6Delegation, err := stkK.GetDelegation(d.Ctx(), del6.Address(), val1ValAddr)
 	require.NoError(d.t, err)
 
 	val1, err = stkK.GetValidator(d.Ctx(), val1ValAddr)
@@ -1313,11 +1313,11 @@ func TestBabyCoStaking(t *testing.T) {
 	require.True(t, del6Tracker.ActiveSatoshis.IsZero())
 	require.True(t, del6Tracker.TotalScore.IsZero())
 
-	del7Delegation, err := stkK.GetDelegation(d.Ctx(), del7.Address(), val2ValAddr)
+	_, err = stkK.GetDelegation(d.Ctx(), del7.Address(), val2ValAddr)
 	require.Error(d.t, err)
 	require.ErrorContains(d.t, err, "no delegation")
 
-	del7Delegation, err = stkK.GetDelegation(d.Ctx(), del7.Address(), val6ValAddr)
+	del7Delegation, err := stkK.GetDelegation(d.Ctx(), del7.Address(), val6ValAddr)
 	require.NoError(d.t, err)
 
 	val6, err := stkK.GetValidator(d.Ctx(), val6ValAddr)
```

### test/replay/driver.go
```diff
@@ -896,12 +896,12 @@ func (d *BabylonAppDriver) FinalizeCkptForEpoch(epochNumber uint64) {
 }
 
 func (d *BabylonAppDriver) ProgressTillFirstBlockTheNextEpoch() {
-	currnetEpochNunber := d.GetEpoch().EpochNumber
-	nextEpochNumber := currnetEpochNunber + 1
+	currentEpochNumber := d.GetEpoch().EpochNumber
+	nextEpochNumber := currentEpochNumber + 1
 
-	for currnetEpochNunber < nextEpochNumber {
+	for currentEpochNumber < nextEpochNumber {
 		d.GenerateNewBlock()
-		currnetEpochNunber = d.GetEpoch().EpochNumber
+		currentEpochNumber = d.GetEpoch().EpochNumber
 	}
 }
 
```

### test/replay/scenario_builder.go
```diff
@@ -38,7 +38,6 @@ func (s *StandardScenario) InitScenario(
 	valAddr := sdk.MustValAddressFromBech32(val.OperatorAddress)
 
 	covSender := s.driver.CreateCovenantSender()
-	fps := s.driver.CreateNFinalityProviderAccounts(numFps)
 	// each staker will delegate to same fp
 	stakers := s.driver.CreateNStakerAccounts(numFps)
 
@@ -53,15 +52,7 @@ func (s *StandardScenario) InitScenario(
 	s.driver.ProgressTillFirstBlockTheNextEpoch()
 	s.driver.FinalizeCkptForEpoch(oldEpochNumber)
 
-	for _, fp := range fps {
-		fp.RegisterFinalityProvider()
-	}
-	// register all fps in one block
-	s.driver.GenerateNewBlockAssertExecutionSuccess()
-
-	for _, fp := range fps {
-		fp.CommitRandomness()
-	}
+	fps := s.CreateFpRegisterAndCommitRandomness(numFps)
 
 	currentEpochNumber := s.driver.GetEpoch().EpochNumber
 	s.driver.ProgressTillFirstBlockTheNextEpoch()
@@ -105,6 +96,22 @@ func (s *StandardScenario) InitScenario(
 	s.activationHeight = activationHeight
 }
 
+func (s *StandardScenario) CreateFpRegisterAndCommitRandomness(n int) []*FinalityProvider {
+	fps := s.driver.CreateNFinalityProviderAccounts(n)
+	s.driver.GenerateNewBlockAssertExecutionSuccess()
+	for _, fp := range fps {
+		fp.RegisterFinalityProvider()
+	}
+	// register all fps in one block
+	s.driver.GenerateNewBlockAssertExecutionSuccess()
+
+	for _, fp := range fps {
+		fp.CommitRandomness()
+	}
+
+	return fps
+}
+
 func (s *StandardScenario) CreateActiveBtcDel(fp *FinalityProvider, staker *Staker, totalSat int64) {
 	staker.CreatePreApprovalDelegation(
 		[]*bbn.BIP340PubKey{fp.BTCPublicKey()},
@@ -125,6 +132,11 @@ func (s *StandardScenario) FinalityFinalizeBlocksAllVotes(fromBlockToFinalize, n
 	return s.FinalityFinalizeBlocks(fromBlockToFinalize, numBlocksToFinalize, s.FpMapBtcPkHex())
 }
 
+func (s *StandardScenario) FinalityFinalizeBlocksAllVotesUntilCurrentHeight(fromBlockToFinalize uint64) uint64 {
+	currHeight := uint64(s.driver.Ctx().BlockHeader().Height)
+	return s.FinalityFinalizeBlocks(fromBlockToFinalize, currHeight-fromBlockToFinalize, s.FpMapBtcPkHex())
+}
+
 func (s *StandardScenario) FpMapBtcPkHex() map[string]struct{} {
 	return s.FpMapBtcPkHexQnt(len(s.finalityProviders))
 }
```

### x/incentive/keeper/reward_tracker_store.go
```diff
@@ -3,6 +3,7 @@ package keeper
 import (
 	"context"
 	"errors"
+	"sort"
 
 	"cosmossdk.io/collections"
 	sdkmath "cosmossdk.io/math"
@@ -131,7 +132,15 @@ func (k Keeper) IterateBTCDelegationSatsUpdated(
 	}
 
 	// iterates over the compiled events as some new btc delegation could be activated during the pending events
-	for delStr, sats := range compiledEvents {
+	// Sort the keys to ensure deterministic iteration order
+	delStrs := make([]string, 0, len(compiledEvents))
+	for delStr := range compiledEvents {
+		delStrs = append(delStrs, delStr)
+	}
+	sort.Strings(delStrs)
+
+	for _, delStr := range delStrs {
+		sats := compiledEvents[delStr]
 		delAddr, err := sdk.AccAddressFromBech32(delStr)
 		if err != nil {
 			return err
```

### x/incentive/keeper/reward_tracker_store_test.go
```diff
@@ -802,6 +802,75 @@ func TestIterateBTCDelegationSatsUpdated(t *testing.T) {
 	require.Equal(t, 0, fp3Count, "fp3 with no stored data should have 0 delegations")
 }
 
+func FuzzIterateBTCDelegationSatsUpdatedDeterminism(f *testing.F) {
+	datagen.AddRandomSeedsToFuzzer(f, 10)
+
+	f.Fuzz(func(t *testing.T, seed int64) {
+		r := rand.New(rand.NewSource(seed))
+
+		k, ctx := NewKeeperWithCtx(t)
+
+		fp := datagen.GenRandomAddress()
+		numDelegations := datagen.RandomInt(r, 5) + 5
+		delegators := make([]sdk.AccAddress, numDelegations)
+
+		sdkCtx := sdk.UnwrapSDKContext(ctx)
+		currentHeight := uint64(100)
+		header := sdkCtx.HeaderInfo()
+		header.Height = int64(currentHeight)
+		ctx = sdkCtx.WithHeaderInfo(header)
+
+		startHeight := datagen.RandomInt(r, 50) + 10
+		err := k.SetRewardTrackerEventLastProcessedHeight(ctx, startHeight)
+		require.NoError(t, err)
+
+		for i := uint64(0); i < numDelegations; i++ {
+			delegators[i] = datagen.GenRandomAddress()
+			// add the events to iterate over
+			err := k.AddEventBtcDelegationActivated(ctx, uint64(startHeight+2+i), fp, delegators[i], datagen.RandomInt(r, 1000)+100)
+			require.NoError(t, err)
+		}
+
+		// as the func doesn't delete the events we just iterate over it multiple times and check that all iterations were the same
+		runIteration := func() []string {
+			var order []string
+			err := k.IterateBTCDelegationSatsUpdated(ctx, fp, func(del sdk.AccAddress, activeSats sdkmath.Int) error {
+				order = append(order, del.String())
+				return nil
+			})
+			require.NoError(t, err)
+			return order
+		}
+
+		iterations := 10
+		orders := make([][]string, iterations)
+		for i := 0; i < iterations; i++ {
+			orders[i] = runIteration()
+		}
+
+		// check the first order against all the others
+		firstOrder := orders[0]
+		for i := 1; i < iterations; i++ {
+			require.ElementsMatch(t, firstOrder, orders[i], "all iterations should contain the same delegators")
+
+			if len(firstOrder) != len(orders[i]) {
+				t.Fatalf("iteration %d has different length than first iteration", i)
+			}
+
+			for j := range firstOrder {
+				if firstOrder[j] == orders[i][j] {
+					continue
+				}
+
+				t.Logf("Non-deterministic ordering detected!")
+				t.Logf("First iteration order:  %v", firstOrder)
+				t.Logf("Iteration %d order: %v", i, orders[i])
+				t.Fatalf("IterateBTCDelegationSatsUpdated produced different ordering on iteration %d. - seed %d", i, seed)
+			}
+		}
+	})
+}
+
 func NewKeeperWithCtx(t *testing.T) (*Keeper, sdk.Context) {
 	encConf := appparams.DefaultEncodingConfig()
 	ctx, kvStore := store.NewStoreWithCtx(t, types.ModuleName)
```
