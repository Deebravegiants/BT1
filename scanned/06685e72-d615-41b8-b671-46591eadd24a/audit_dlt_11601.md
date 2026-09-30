# [?] backport: fix(finality): check for overflow in CommitPubRandList (#567) (#570)

## Summary
Severity: Unknown
Chain: Babylon
Component: babylonlabs-io/babylon
Published: 2025-02-26
Source: https://github.com/babylonlabs-io/babylon/commit/159abe3ee87f78ca12994c0a6afe6ce1c01c016d
Type: security-commit

## Details
backport: fix(finality): check for overflow in CommitPubRandList (#567) (#570)

Closes https://github.com/babylonlabs-io/pm/issues/248

## Patch
### CHANGELOG.md
```diff
@@ -47,6 +47,7 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
 ### State Machine Breaking
 
 - [#530](https://github.com/babylonlabs-io/babylon/pull/530) Add `ConflictingCheckpointReceived` flag in `x/checkpointing` module.
+- [#567](https://github.com/babylonlabs-io/babylon/pull/567) Add check for height overflow in `CommitPubRandList` in `x/finality` module
 
 ### Bug fixes
 
```

### x/finality/keeper/msg_server.go
```diff
@@ -234,6 +234,15 @@ func (ms msgServer) ShouldAcceptSigForHeight(ctx context.Context, block *types.I
 func (ms msgServer) CommitPubRandList(goCtx context.Context, req *types.MsgCommitPubRandList) (*types.MsgCommitPubRandListResponse, error) {
 	defer telemetry.ModuleMeasureSince(types.ModuleName, time.Now(), types.MetricsKeyCommitPubRandList)
 
+	// To avoid public randomness reset,
+	// check for overflow when doing (StartHeight + NumPubRand)
+	if req.StartHeight >= (req.StartHeight + req.NumPubRand) {
+		return nil, types.ErrOverflowInBlockHeight.Wrapf(
+			"public rand commit start block height: %d is equal or higher than (start height + num pub rand) %d",
+			req.StartHeight, req.StartHeight+req.NumPubRand,
+		)
+	}
+
 	ctx := sdk.UnwrapSDKContext(goCtx)
 	activationHeight, errMod := ms.validateActivationHeight(ctx, req.StartHeight)
 	if errMod != nil {
```

### x/finality/keeper/msg_server_test.go
```diff
@@ -3,12 +3,13 @@ package keeper_test
 import (
 	"context"
 	"fmt"
+	"math"
 	"math/rand"
 	"testing"
 	"time"
 
 	"cosmossdk.io/core/header"
-	"cosmossdk.io/math"
+	sdkmath "cosmossdk.io/math"
 	sdk "github.com/cosmos/cosmos-sdk/types"
 	"github.com/golang/mock/gomock"
 	"github.com/stretchr/testify/require"
@@ -106,6 +107,14 @@ func FuzzCommitPubRandList(f *testing.F) {
 		require.NoError(t, err)
 		_, err = ms.CommitPubRandList(ctx, msg)
 		require.NoError(t, err)
+
+		// Case 6: commit a pubrand list that overflows when adding startHeight + numPubRand
+		overflowStartHeight := math.MaxUint64 - datagen.RandomInt(r, 5)
+		_, msg, err = datagen.GenRandomMsgCommitPubRandList(r, btcSK, overflowStartHeight, numPubRand)
+		require.NoError(t, err)
+		_, err = ms.CommitPubRandList(ctx, msg)
+		require.Error(t, err)
+		require.ErrorContains(t, err, types.ErrOverflowInBlockHeight.Error())
 	})
 }
 
@@ -564,12 +573,12 @@ func TestBtcDelegationRewards(t *testing.T) {
 	// if 1500ubbn are added as reward
 	// del1 should receive 1/3 => 500
 	// del2 should receive 2/3 => 1000
-	rwdFp1 := sdk.NewCoins(sdk.NewCoin(appparams.DefaultBondDenom, math.NewInt(1500)))
+	rwdFp1 := sdk.NewCoins(sdk.NewCoin(appparams.DefaultBondDenom, sdkmath.NewInt(1500)))
 	err = h.IncentivesKeeper.AddFinalityProviderRewardsForBtcDelegations(h.Ctx, fp1.Address(), rwdFp1)
 	h.NoError(err)
 
-	rwdFp1Del1 := sdk.NewCoins(sdk.NewCoin(appparams.DefaultBondDenom, math.NewInt(500)))
-	rwdFp1Del2 := sdk.NewCoins(sdk.NewCoin(appparams.DefaultBondDenom, math.NewInt(1000)))
+	rwdFp1Del1 := sdk.NewCoins(sdk.NewCoin(appparams.DefaultBondDenom, sdkmath.NewInt(500)))
+	rwdFp1Del2 := sdk.NewCoins(sdk.NewCoin(appparams.DefaultBondDenom, sdkmath.NewInt(1000)))
 
 	fp1Del1Rwd, err := h.IncentivesKeeper.RewardGauges(h.Ctx, &ictvtypes.QueryRewardGaugesRequest{
 		Address: fp1Del1.Address().String(),
```

### x/finality/types/errors.go
```diff
@@ -23,4 +23,5 @@ var (
 	ErrBTCStakingNotActivated         = errorsmod.Register(ModuleName, 1114, "the BTC staking protocol is not activated yet")
 	ErrFinalityNotActivated           = errorsmod.Register(ModuleName, 1115, "finality is not active yet")
 	ErrSigHeightOutdated              = errorsmod.Register(ModuleName, 1116, "the voting block is already finalized and timestamped")
+	ErrOverflowInBlockHeight          = errorsmod.Register(ModuleName, 1117, "overflow in block height calculation")
 )
```
