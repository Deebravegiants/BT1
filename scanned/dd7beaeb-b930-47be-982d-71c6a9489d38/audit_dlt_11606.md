# [?] fix non determinism in `BeginBlock` (#453)

## Summary
Severity: Unknown
Chain: Babylon
Component: babylonlabs-io/babylon
Published: 2024-02-06
Source: https://github.com/babylonlabs-io/babylon/commit/396a712297f97cd8ca225bcea81ee9b02dada991
Type: security-commit

## Details
fix non determinism in `BeginBlock` (#453)

## Patch
### x/btcstaking/keeper/btc_delegators.go
```diff
@@ -54,6 +54,29 @@ func (k Keeper) AddBTCDelegation(ctx context.Context, btcDel *types.BTCDelegatio
 	return nil
 }
 
+// IterateBTCDelegations iterates all BTC delegations under a given finality provider
+func (k Keeper) IterateBTCDelegations(ctx context.Context, fpBTCPK *bbn.BIP340PubKey, handler func(btcDel *types.BTCDelegation) bool) {
+	btcDelIter := k.btcDelegatorStore(ctx, fpBTCPK).Iterator(nil, nil)
+	defer btcDelIter.Close()
+	for ; btcDelIter.Valid(); btcDelIter.Next() {
+		// unmarshal delegator's delegation index
+		var btcDelIndex types.BTCDelegatorDelegationIndex
+		k.cdc.MustUnmarshal(btcDelIter.Value(), &btcDelIndex)
+		// retrieve and process each of the BTC delegation
+		for _, stakingTxHashBytes := range btcDelIndex.StakingTxHashList {
+			stakingTxHash, err := chainhash.NewHash(stakingTxHashBytes)
+			if err != nil {
+				panic(err) // only programming error is possible
+			}
+			btcDel := k.getBTCDelegation(ctx, *stakingTxHash)
+			shouldContinue := handler(btcDel)
+			if !shouldContinue {
+				return
+			}
+		}
+	}
+}
+
 // hasBTCDelegatorDelegations checks if the given BTC delegator has any BTC delegations under a given finality provider
 func (k Keeper) hasBTCDelegatorDelegations(ctx context.Context, fpBTCPK *bbn.BIP340PubKey, delBTCPK *bbn.BIP340PubKey) bool {
 	fpBTCPKBytes := fpBTCPK.MustMarshal()
```

### x/btcstaking/keeper/keeper.go
```diff
@@ -71,51 +71,49 @@ func (k Keeper) BeginBlocker(ctx context.Context) error {
 	wValue := k.btccKeeper.GetParams(ctx).CheckpointFinalizationTimeout
 
 	// prepare for recording finality providers with positive voting power
-	// key is the finality provider's FP BTC PK hex, and value is the
-	// voting power
-	fpPowerMap := map[string]uint64{}
+	activeFps := []*types.FinalityProviderWithMeta{}
 	// prepare for recording finality providers and their BTC delegations
 	// for rewards
-	fpDistMap := map[string]*types.FinalityProviderDistInfo{}
+	rdc := types.NewRewardDistCache()
 
-	k.IterateActiveFPsAndBTCDelegations(
+	// iterate over all finality providers to find out non-slashed ones that have
+	// positive voting power
+	k.IterateActiveFPs(
 		ctx,
-		func(fp *types.FinalityProvider, btcDel *types.BTCDelegation) bool {
-			fpBTCPKHex := fp.BtcPk.MarshalHex()
-
-			// record active finality providers
-			power := btcDel.VotingPower(btcTipHeight, wValue, covenantQuorum)
-			if power == 0 {
-				return true // skip if no voting power
+		func(fp *types.FinalityProvider) bool {
+			fpDistInfo := types.NewFinalityProviderDistInfo(fp)
+
+			// iterate over all BTC delegations under the finality provider
+			// in order to accumulate voting power and reward dist info for it
+			k.IterateBTCDelegations(ctx, fp.BtcPk, func(btcDel *types.BTCDelegation) bool {
+				// accumulate voting power and reward distribution cache
+				fpDistInfo.AddBTCDel(btcDel, btcTipHeight, wValue, covenantQuorum)
+				return true
+			})
+
+			if fpDistInfo.TotalVotingPower > 0 {
+				activeFP := &types.FinalityProviderWithMeta{
+					BtcPk:       fp.BtcPk,
+					VotingPower: fpDistInfo.TotalVotingPower,
+				}
+				activeFps = append(activeFps, activeFP)
+				rdc.AddFinalityProviderDistInfo(fpDistInfo)
 			}
-			fpPowerMap[fpBTCPKHex] += power
 
-			// create fp dist info if not exist
-			if _, ok := fpDistMap[fpBTCPKHex]; !ok {
-				fpDistMap[fpBTCPKHex] = types.NewFinalityProviderDistInfo(fp)
-			}
-			// append BTC delegation
-			fpDistMap[fpBTCPKHex].AddBTCDel(btcDel, btcTipHeight, wValue, covenantQuorum)
 			return true
 		},
 	)
 
-	// return directly if there is no active finality provider
-	if len(fpPowerMap) == 0 {
-		return nil
-	}
-
-	// get top N finality providers and set their voting power to KV store
-	k.setCurrentTopNVotingPower(ctx, fpPowerMap)
-
-	// create reward distribution cache
-	rdc := types.NewRewardDistCache()
-	for fpBTCPKHex := range fpDistMap {
-		// try to add this finality provider distribution info to reward distribution cache
-		rdc.AddFinalityProviderDistInfo(fpDistMap[fpBTCPKHex])
+	// filter out top `MaxActiveFinalityProviders` active finality providers in terms of voting power
+	activeFps = types.FilterTopNFinalityProviders(activeFps, k.GetParams(ctx).MaxActiveFinalityProviders)
+	// set voting power table
+	babylonTipHeight := uint64(sdk.UnwrapSDKContext(ctx).HeaderInfo().Height)
+	for _, fp := range activeFps {
+		k.SetVotingPower(ctx, fp.BtcPk.MustMarshal(), babylonTipHeight, fp.VotingPower)
 	}
 
-	// all good, set the reward distribution cache of the current height
+	// set the reward distribution cache of the current height
+	// TODO: only give rewards to top N finality providers and their BTC delegations
 	k.setRewardDistCache(ctx, uint64(sdk.UnwrapSDKContext(ctx).HeaderInfo().Height), rdc)
 
 	return nil
```

### x/btcstaking/keeper/voting_power_table.go
```diff
@@ -4,7 +4,6 @@ import (
 	"context"
 	"fmt"
 
-	"github.com/btcsuite/btcd/chaincfg/chainhash"
 	"github.com/cosmos/cosmos-sdk/runtime"
 
 	"cosmossdk.io/store/prefix"
@@ -13,77 +12,23 @@ import (
 	sdk "github.com/cosmos/cosmos-sdk/types"
 )
 
-// IterateActiveFPsAndBTCDelegations iterates over all finality providers that are not slashed,
-// and their BTC delegations
-func (k Keeper) IterateActiveFPsAndBTCDelegations(ctx context.Context, handler func(fp *types.FinalityProvider, btcDel *types.BTCDelegation) bool) {
+// IterateActiveFPs iterates over all finality providers that are not slashed
+func (k Keeper) IterateActiveFPs(ctx context.Context, handler func(fp *types.FinalityProvider) bool) {
 	// filter out all finality providers with positive voting power
 	fpIter := k.finalityProviderStore(ctx).Iterator(nil, nil)
 	defer fpIter.Close()
 	for ; fpIter.Valid(); fpIter.Next() {
-		fpBTCPKBytes := fpIter.Key()
-		fpBTCPK, err := bbn.NewBIP340PubKey(fpBTCPKBytes)
-		if err != nil {
-			// failed to unmarshal finality provider PK in KVStore is a programming error
-			panic(err)
-		}
-		fp, err := k.GetFinalityProvider(ctx, fpBTCPKBytes)
-		if err != nil {
-			// failed to get a finality provider with voting power is a programming error
-			panic(err)
-		}
+		var fp types.FinalityProvider
+		k.cdc.MustUnmarshal(fpIter.Value(), &fp)
 		if fp.IsSlashed() {
 			// slashed finality provider is removed from finality provider set
 			continue
 		}
 
-		// iterate all BTC delegations under this finality provider
-		// to calculate this finality provider's total voting power
-		// wrapped in a function to close btcDelIter as soon as the function
-		// returned, see https://stackoverflow.com/questions/45617758/proper-way-to-release-resources-with-defer-in-a-loop/45620423
-		func() {
-			btcDelIter := k.btcDelegatorStore(ctx, fpBTCPK).Iterator(nil, nil)
-			defer btcDelIter.Close()
-			for ; btcDelIter.Valid(); btcDelIter.Next() {
-
-				// unmarshal delegator's delegation index
-				var btcDelIndex types.BTCDelegatorDelegationIndex
-				k.cdc.MustUnmarshal(btcDelIter.Value(), &btcDelIndex)
-
-				// retrieve and process each of the BTC delegation
-				for _, stakingTxHashBytes := range btcDelIndex.StakingTxHashList {
-					stakingTxHash, err := chainhash.NewHash(stakingTxHashBytes)
-					if err != nil {
-						panic(err) // only programming error is possible
-					}
-					btcDel := k.getBTCDelegation(ctx, *stakingTxHash)
-					shouldContinue := handler(fp, btcDel)
-					if !shouldContinue {
-						break
-					}
-				}
-			}
-		}()
-	}
-}
-
-// setCurrentTopNVotingPower gets top N finality providers and set their current voting power to KV store
-func (k Keeper) setCurrentTopNVotingPower(ctx context.Context, fpPowerMap map[string]uint64) {
-	// filter out top `MaxActiveFinalityProviders` active finality providers in terms of voting power
-	activeFps := []*types.FinalityProviderWithMeta{}
-	for btcPKHex, power := range fpPowerMap {
-		btcPK, err := bbn.NewBIP340PubKeyFromHex(btcPKHex)
-		if err != nil {
-			panic(err) // only programming error
+		shouldContinue := handler(&fp)
+		if !shouldContinue {
+			return
 		}
-		activeFps = append(activeFps, &types.FinalityProviderWithMeta{BtcPk: btcPK, VotingPower: power})
-	}
-	activeFps = types.FilterTopNFinalityProviders(activeFps, k.GetParams(ctx).MaxActiveFinalityProviders)
-
-	// get current Babylon height
-	babylonTipHeight := uint64(sdk.UnwrapSDKContext(ctx).HeaderInfo().Height)
-	// set voting power for each active finality providers
-	for _, fp := range activeFps {
-		k.SetVotingPower(ctx, fp.BtcPk.MustMarshal(), babylonTipHeight, fp.VotingPower)
 	}
 }
 
```
