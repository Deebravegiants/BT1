# [?] fix: fix non-determinism in voting power rotation (#597)

## Summary
Severity: Unknown
Chain: Babylon
Component: babylonlabs-io/babylon
Published: 2024-03-27
Source: https://github.com/babylonlabs-io/babylon/commit/8d76979ef05742206a74166c480c69b44b082798
Type: security-commit

## Details
fix: fix non-determinism in voting power rotation (#597)

## Patch
### x/btcstaking/keeper/power_dist_change.go
```diff
@@ -2,6 +2,7 @@ package keeper
 
 import (
 	"context"
+	"sort"
 
 	"cosmossdk.io/store/prefix"
 	bbn "github.com/babylonchain/babylon/types"
@@ -51,7 +52,7 @@ func (k Keeper) UpdatePowerDist(ctx context.Context) {
 
 	// reconcile old voting power distribution cache and new events
 	// to construct the new distribution
-	newDc := k.processAllPowerDistUpdateEvents(ctx, dc, events, maxActiveFps)
+	newDc := k.ProcessAllPowerDistUpdateEvents(ctx, dc, events, maxActiveFps)
 
 	// record voting power and cache for this height
 	k.recordVotingPowerAndCache(ctx, newDc, maxActiveFps)
@@ -90,13 +91,13 @@ func (k Keeper) recordMetrics(dc *types.VotingPowerDistCache, maxActiveFps uint3
 	// TODO: record number of BTC delegations under different status
 }
 
-// processAllPowerDistUpdateEvents processes all events that affect
+// ProcessAllPowerDistUpdateEvents processes all events that affect
 // voting power distribution and returns a new distribution cache.
 // The following events will affect the voting power distribution:
 // - newly active BTC delegations
 // - newly unbonded BTC delegations
 // - slashed finality providers
-func (k Keeper) processAllPowerDistUpdateEvents(
+func (k Keeper) ProcessAllPowerDistUpdateEvents(
 	ctx context.Context,
 	dc *types.VotingPowerDistCache,
 	events []*types.EventPowerDistUpdate,
@@ -192,7 +193,16 @@ func (k Keeper) processAllPowerDistUpdateEvents(
 	/*
 		process new BTC delegations under new finality providers in activeBTCDels
 	*/
-	for fpBTCPKHex, fpActiveBTCDels := range activeBTCDels {
+	// sort new finality providers in activeBTCDels to ensure determinism
+	fpBTCPKHexList := make([]string, 0, len(activeBTCDels))
+	for fpBTCPKHex := range activeBTCDels {
+		fpBTCPKHexList = append(fpBTCPKHexList, fpBTCPKHex)
+	}
+	sort.SliceStable(fpBTCPKHexList, func(i, j int) bool {
+		return fpBTCPKHexList[i] < fpBTCPKHexList[j]
+	})
+	// for each new finality provider, apply the new BTC delegations to the new dist cache
+	for _, fpBTCPKHex := range fpBTCPKHexList {
 		// get the finality provider and initialise its dist info
 		fpBTCPK, err := bbn.NewBIP340PubKeyFromHex(fpBTCPKHex)
 		if err != nil {
@@ -205,6 +215,7 @@ func (k Keeper) processAllPowerDistUpdateEvents(
 		fpDistInfo := types.NewFinalityProviderDistInfo(newFP)
 
 		// add each BTC delegation
+		fpActiveBTCDels := activeBTCDels[fpBTCPKHex]
 		for _, d := range fpActiveBTCDels {
 			fpDistInfo.AddBTCDel(d)
 		}
```

### x/btcstaking/keeper/power_dist_change_test.go
```diff
@@ -7,10 +7,62 @@ import (
 	"github.com/babylonchain/babylon/testutil/datagen"
 	btclctypes "github.com/babylonchain/babylon/x/btclightclient/types"
 	"github.com/babylonchain/babylon/x/btcstaking/types"
+	"github.com/btcsuite/btcd/btcec/v2"
 	"github.com/golang/mock/gomock"
 	"github.com/stretchr/testify/require"
 )
 
+func FuzzProcessAllPowerDistUpdateEvents_Determinism(f *testing.F) {
+	datagen.AddRandomSeedsToFuzzer(f, 10)
+
+	f.Fuzz(func(t *testing.T, seed int64) {
+		r := rand.New(rand.NewSource(seed))
+		ctrl := gomock.NewController(t)
+		defer ctrl.Finish()
+
+		// mock BTC light client and BTC checkpoint modules
+		btclcKeeper := types.NewMockBTCLightClientKeeper(ctrl)
+		btccKeeper := types.NewMockBtcCheckpointKeeper(ctrl)
+		h := NewHelper(t, btclcKeeper, btccKeeper)
+
+		// set all parameters
+		h.GenAndApplyParams(r)
+		changeAddress, err := datagen.GenRandomBTCAddress(r, h.Net)
+		require.NoError(t, err)
+
+		// generate and insert a number of new finality providers
+		fpPKs := []*btcec.PublicKey{}
+		for i := 0; i < 5; i++ {
+			_, fpPK, _ := h.CreateFinalityProvider(r)
+			fpPKs = append(fpPKs, fpPK)
+		}
+
+		// empty dist cache
+		dc := types.NewVotingPowerDistCache()
+
+		stakingValue := int64(2 * 10e8)
+
+		// generate many new BTC delegations under each finality provider, and their corresponding events
+		events := []*types.EventPowerDistUpdate{}
+		for _, fpPK := range fpPKs {
+			for i := 0; i < 5; i++ {
+				_, _, _, _, del := h.CreateDelegation(r, fpPK, changeAddress.EncodeAddress(), stakingValue, 1000)
+				event := types.NewEventPowerDistUpdateWithBTCDel(&types.EventBTCDelegationStateUpdate{
+					StakingTxHash: del.MustGetStakingTxHash().String(),
+					NewState:      types.BTCDelegationStatus_ACTIVE,
+				})
+				events = append(events, event)
+			}
+		}
+
+		newDc := h.BTCStakingKeeper.ProcessAllPowerDistUpdateEvents(h.Ctx, dc, events, 100)
+		for i := 0; i < 10; i++ {
+			newDc2 := h.BTCStakingKeeper.ProcessAllPowerDistUpdateEvents(h.Ctx, dc, events, 100)
+			require.Equal(t, newDc, newDc2)
+		}
+	})
+}
+
 func FuzzFinalityProviderEvents(f *testing.F) {
 	datagen.AddRandomSeedsToFuzzer(f, 10)
 
```
