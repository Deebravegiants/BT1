# [?] fix: Non-determinism while jailing (#342)

## Summary
Severity: Unknown
Chain: Babylon
Component: babylonlabs-io/babylon
Published: 2024-12-13
Source: https://github.com/babylonlabs-io/babylon/commit/ccc00b7353b6e50985e4d3406604ff57391e6526
Type: security-commit

## Details
fix: Non-determinism while jailing (#342)

The voting power table is a map which causes random order of processing
jailing events. If more than one fps jailed at one block,
non-determinism could happen. The PR fixed this by introducing ordered
voting power table which retains the order from interating the
`votingPowerBbnBlockHeightStore`

## Patch
### CHANGELOG.md
```diff
@@ -42,11 +42,9 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
 - [#338](https://github.com/babylonlabs-io/babylon/pull/338) Add print BIP-340 in
 `debug pubkey-raw` subcommand
 - [#316](https://github.com/babylonlabs-io/babylon/pull/316) Add testnet upgrade data
-
 - [#326](https://github.com/babylonlabs-io/babylon/pull/326) docs: btcstaking:
 Update btcstaking module docs to include EOI
 
-
 ### Bug fixes
 
 - [#324](https://github.com/babylonlabs-io/babylon/pull/324) Fix decrementing
@@ -56,6 +54,7 @@ jailed fp counter
 
 - [#341](https://github.com/babylonlabs-io/babylon/pull/341) Select parameters
 for pre-approval flow based on BTC LC tip height
+- [#342](https://github.com/babylonlabs-io/babylon/pull/342) Fix non-determinism while jailing
 
 ## v0.18.1
 
```

### testutil/btcstaking-helper/keeper.go
```diff
@@ -583,3 +583,14 @@ func (h *Helper) CommitPubRandList(
 
 	return randListInfo
 }
+
+func (h *Helper) AddFinalityProvider(fp *types.FinalityProvider) {
+	err := h.BTCStakingKeeper.AddFinalityProvider(h.Ctx, &types.MsgCreateFinalityProvider{
+		Addr:        fp.Addr,
+		Description: fp.Description,
+		Commission:  fp.Commission,
+		BtcPk:       fp.BtcPk,
+		Pop:         fp.Pop,
+	})
+	h.NoError(err)
+}
```

### x/finality/keeper/liveness.go
```diff
@@ -14,23 +14,20 @@ import (
 // including jailing sluggish finality providers and applying punishment (TBD)
 func (k Keeper) HandleLiveness(ctx context.Context, height int64) {
 	// get all the active finality providers for the height
-	fpSet := k.GetVotingPowerTable(ctx, uint64(height))
+	vpTableOrdered := k.GetVotingPowerTableOrdered(ctx, uint64(height))
 	// get all the voters for the height
 	voterBTCPKs := k.GetVoters(ctx, uint64(height))
 
 	// Iterate over all the finality providers which *should* have signed this block
 	// store whether or not they have actually signed it, identify sluggish
 	// ones, and apply punishment (TBD)
-	for fpPkHex := range fpSet {
-		fpPk, err := types.NewBIP340PubKeyFromHex(fpPkHex)
-		if err != nil {
-			panic(fmt.Errorf("invalid finality provider public key %s: %w", fpPkHex, err))
-		}
-
+	// Iterate over all the finality providers in sorted order by the voting power
+	for _, fpWithVp := range vpTableOrdered {
+		fpPkHex := fpWithVp.FpPk.MarshalHex()
 		_, ok := voterBTCPKs[fpPkHex]
 		missed := !ok
 
-		err = k.HandleFinalityProviderLiveness(ctx, fpPk, missed, height)
+		err := k.HandleFinalityProviderLiveness(ctx, fpWithVp.FpPk, missed, height)
 		if err != nil {
 			panic(fmt.Errorf("failed to handle liveness of finality provider %s: %w", fpPkHex, err))
 		}
```

### x/finality/keeper/liveness_test.go
```diff
@@ -9,8 +9,10 @@ import (
 	"github.com/golang/mock/gomock"
 	"github.com/stretchr/testify/require"
 
+	testutil "github.com/babylonlabs-io/babylon/testutil/btcstaking-helper"
 	"github.com/babylonlabs-io/babylon/testutil/datagen"
 	keepertest "github.com/babylonlabs-io/babylon/testutil/keeper"
+	btclctypes "github.com/babylonlabs-io/babylon/x/btclightclient/types"
 	bstypes "github.com/babylonlabs-io/babylon/x/btcstaking/types"
 	"github.com/babylonlabs-io/babylon/x/finality/types"
 )
@@ -78,3 +80,131 @@ func FuzzHandleLiveness(f *testing.F) {
 		require.Equal(t, int64(0), signingInfo.MissedBlocksCounter)
 	})
 }
+
+// FuzzHandleLivenessDeterminism tests the property of determinism of
+// HandleLiveness by creating two helpers with the same steps to jailing
+// and asserting the jailing events should be with the same order
+func FuzzHandleLivenessDeterminism(f *testing.F) {
+	datagen.AddRandomSeedsToFuzzer(f, 10)
+
+	f.Fuzz(func(t *testing.T, seed int64) {
+		r := rand.New(rand.NewSource(seed))
+		ctrl := gomock.NewController(t)
+		defer ctrl.Finish()
+
+		// mock BTC light client and BTC checkpoint modules
+		btclcKeeper := bstypes.NewMockBTCLightClientKeeper(ctrl)
+		btccKeeper := bstypes.NewMockBtcCheckpointKeeper(ctrl)
+		h1 := testutil.NewHelper(t, btclcKeeper, btccKeeper)
+		h2 := testutil.NewHelper(t, btclcKeeper, btccKeeper)
+
+		// set all parameters
+		covenantSKs, _ := h1.GenAndApplyParams(r)
+		params := h1.BTCStakingKeeper.GetParams(h1.Ctx)
+		err := h2.BTCStakingKeeper.SetParams(h2.Ctx, params)
+		require.NoError(t, err)
+		changeAddress, err := datagen.GenRandomBTCAddress(r, h1.Net)
+		require.NoError(t, err)
+
+		// Generate multiple finality providers
+		numFPs := 5 // Can be adjusted or randomized
+		fps := make([]*bstypes.FinalityProvider, numFPs)
+		for i := 0; i < numFPs; i++ {
+			fpSK, fpPK, fp := h1.CreateFinalityProvider(r)
+			require.NoError(t, err)
+			h2.AddFinalityProvider(fp)
+			h1.CommitPubRandList(r, fpSK, fp, 1, 1000, true)
+			h2.CommitPubRandList(r, fpSK, fp, 1, 1000, true)
+			fps[i] = fp
+
+			// Create delegation for each FP
+			stakingValue := int64(2 * 10e8)
+			delSK, _, err := datagen.GenRandomBTCKeyPair(r)
+			require.NoError(t, err)
+			stakingTxHash, msgCreateBTCDel, actualDel, btcHeaderInfo, inclusionProof, _, err := h1.CreateDelegationWithBtcBlockHeight(
+				r,
+				delSK,
+				fpPK,
+				changeAddress.EncodeAddress(),
+				stakingValue,
+				1000,
+				0,
+				0,
+				true,
+				false,
+				10,
+				10,
+			)
+			require.NoError(t, err)
+			stakingTxHash2, msgCreateBTCDel2, actualDel2, btcHeaderInfo2, inclusionProof2, _, err := h2.CreateDelegationWithBtcBlockHeight(
+				r,
+				delSK,
+				fpPK,
+				changeAddress.EncodeAddress(),
+				stakingValue,
+				1000,
+				0,
+				0,
+				true,
+				false,
+				10,
+				10,
+			)
+			require.NoError(t, err)
+			// generate and insert new covenant signatures
+			h1.CreateCovenantSigs(r, covenantSKs, msgCreateBTCDel, actualDel, 10)
+			h2.CreateCovenantSigs(r, covenantSKs, msgCreateBTCDel2, actualDel2, 10)
+			// activate BTC delegation
+			// after that, all BTC delegations will have voting power
+			h1.AddInclusionProof(stakingTxHash, btcHeaderInfo, inclusionProof, 30)
+			h2.AddInclusionProof(stakingTxHash2, btcHeaderInfo2, inclusionProof2, 30)
+		}
+
+		fParams := h1.FinalityKeeper.GetParams(h1.Ctx)
+		minSignedPerWindow := fParams.MinSignedPerWindowInt()
+		maxMissed := fParams.SignedBlocksWindow - minSignedPerWindow
+
+		nextHeight := datagen.RandomInt(r, 10) + 2 + uint64(minSignedPerWindow)
+
+		btcTip := &btclctypes.BTCHeaderInfo{Height: 30}
+		// for blocks up to the inactivity boundary, mark the finality provider as having not signed
+		sluggishDetectedHeight := nextHeight + uint64(maxMissed)
+		for ; nextHeight < sluggishDetectedHeight; nextHeight++ {
+			h1.SetCtxHeight(nextHeight)
+			h1.BTCLightClientKeeper.EXPECT().GetTipInfo(gomock.Eq(h1.Ctx)).Return(btcTip).AnyTimes()
+			h1.BeginBlocker()
+			h1.FinalityKeeper.HandleLiveness(h1.Ctx, int64(nextHeight))
+
+			h2.SetCtxHeight(nextHeight)
+			h2.BTCLightClientKeeper.EXPECT().GetTipInfo(gomock.Eq(h2.Ctx)).Return(btcTip).AnyTimes()
+			h2.BeginBlocker()
+			h2.FinalityKeeper.HandleLiveness(h2.Ctx, int64(nextHeight))
+		}
+
+		// after next height, the fp will be jailed
+		h1.SetCtxHeight(nextHeight)
+		h1.BTCLightClientKeeper.EXPECT().GetTipInfo(gomock.Eq(h1.Ctx)).Return(btcTip).AnyTimes()
+		h1.BeginBlocker()
+
+		h1.FinalityKeeper.HandleLiveness(h1.Ctx, int64(nextHeight))
+		events := h1.BTCStakingKeeper.GetAllPowerDistUpdateEvents(h1.Ctx, btcTip.Height, btcTip.Height)
+		require.Equal(t, numFPs, len(events))
+
+		h2.SetCtxHeight(nextHeight)
+		h2.BTCLightClientKeeper.EXPECT().GetTipInfo(gomock.Eq(h2.Ctx)).Return(btcTip).AnyTimes()
+		h2.BeginBlocker()
+
+		h2.FinalityKeeper.HandleLiveness(h2.Ctx, int64(nextHeight))
+		events2 := h2.BTCStakingKeeper.GetAllPowerDistUpdateEvents(h2.Ctx, btcTip.Height, btcTip.Height)
+		require.Equal(t, numFPs, len(events))
+
+		// ensure the jailing events are in the same order in two different runs
+		for i, e := range events {
+			e1, ok := e.Ev.(*bstypes.EventPowerDistUpdate_JailedFp)
+			require.True(t, ok)
+			e2, ok := events2[i].Ev.(*bstypes.EventPowerDistUpdate_JailedFp)
+			require.True(t, ok)
+			require.Equal(t, e1.JailedFp.Pk.MarshalHex(), e2.JailedFp.Pk.MarshalHex())
+		}
+	})
+}
```

### x/finality/keeper/power_table.go
```diff
@@ -4,14 +4,19 @@ import (
 	"context"
 	"fmt"
 
+	"cosmossdk.io/store/prefix"
 	"github.com/cosmos/cosmos-sdk/runtime"
+	sdk "github.com/cosmos/cosmos-sdk/types"
 
-	"cosmossdk.io/store/prefix"
 	bbn "github.com/babylonlabs-io/babylon/types"
 	"github.com/babylonlabs-io/babylon/x/finality/types"
-	sdk "github.com/cosmos/cosmos-sdk/types"
 )
 
+type FpWithVotingPower struct {
+	FpPk        *bbn.BIP340PubKey
+	VotingPower uint64
+}
+
 func (k Keeper) SetVotingPower(ctx context.Context, fpBTCPK []byte, height uint64, power uint64) {
 	store := k.votingPowerBbnBlockHeightStore(ctx, height)
 	store.Set(fpBTCPK, sdk.Uint64ToBigEndian(power))
@@ -93,6 +98,35 @@ func (k Keeper) GetVotingPowerTable(ctx context.Context, height uint64) map[stri
 	return fpSet
 }
 
+// GetVotingPowerTableOrdered gets the voting power table ordered by the voting power
+func (k Keeper) GetVotingPowerTableOrdered(ctx context.Context, height uint64) []*FpWithVotingPower {
+	store := k.votingPowerBbnBlockHeightStore(ctx, height)
+	iter := store.Iterator(nil, nil)
+	defer iter.Close()
+
+	// if no finality provider at this height, return nil
+	if !iter.Valid() {
+		return nil
+	}
+
+	// get all finality providers at this height assuming the fps
+	// are already ordered by the voting power
+	fps := make([]*FpWithVotingPower, 0, k.GetParams(ctx).MaxActiveFinalityProviders)
+	for ; iter.Valid(); iter.Next() {
+		fpBTCPK, err := bbn.NewBIP340PubKey(iter.Key())
+		if err != nil {
+			// failing to unmarshal finality provider BTC PK in KVStore is a programming error
+			panic(fmt.Errorf("%w: %w", bbn.ErrUnmarshal, err))
+		}
+		fps = append(fps, &FpWithVotingPower{
+			FpPk:        fpBTCPK,
+			VotingPower: sdk.BigEndianToUint64(iter.Value()),
+		})
+	}
+
+	return fps
+}
+
 // GetBTCStakingActivatedHeight returns the height when the BTC staking protocol is activated
 // i.e., the first height where a finality provider has voting power
 // Before the BTC staking protocol is activated, we don't index or tally any block
```
