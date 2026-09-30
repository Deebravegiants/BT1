# [?] [release/v1.x] fix: Panic can be triggered in handling liveness (#584) (#586)

## Summary
Severity: Unknown
Chain: Babylon
Component: babylonlabs-io/babylon
Published: 2025-02-27
Source: https://github.com/babylonlabs-io/babylon/commit/bda450778a3852bd351fd9659a79bc5b9169c2b1
Type: security-commit

## Details
[release/v1.x] fix: Panic can be triggered in handling liveness (#584) (#586)

# Backport

This will backport the following commits from `main` to `release/v1.x`:
- [fix: Panic can be triggered in handling liveness
(#584)](https://github.com/babylonlabs-io/babylon/pull/584)

<!--- Backport version: 9.5.1 -->

### Questions ?
Please refer to the [Backport tool
documentation](https://github.com/sorenlouv/backport)

Co-authored-by: Cirrus Gai <greferry@gmail.com>

## Patch
### CHANGELOG.md
```diff
@@ -55,6 +55,7 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
 - [#539](https://github.com/babylonlabs-io/babylon/pull/539) fix: add missing `x/checkpointing` hooks
 invocation
 - [#563](https://github.com/babylonlabs-io/babylon/pull/563) reject coinbase staking transactions
+- [#584](https://github.com/babylonlabs-io/babylon/pull/584) fix: Panic can be triggered in handling liveness
 
 ## v1.0.0-rc6
 
```

### x/finality/keeper/liveness.go
```diff
@@ -139,9 +139,15 @@ func (k Keeper) updateSigningInfo(
 	// A genesis finality provider will start at index 0, whereas a non-genesis finality provider's
 	// startHeight will be the block they become active for, but the first block they vote on will be
 	// one later. (And thus their first vote is at index 1)
+	//
+	// NOTE: due to the introduction of the parameter `FinalitySigTimeout`, if there are `x`
+	// consecutive blocks for which a fp is non-active in the middle of the fp being active
+	// where `x` < FinalitySigTimeout, it is possible that `signInfo.StartHeight > height`
+	// in this case, it should return directly because it indicates that the fp does not
+	// need to vote for the height we are examining. This ensures the index calculated
+	// below will not be negative
 	if signInfo.StartHeight > height {
-		return false, nil, fmt.Errorf("invalid state, the finality provider signing info has start height %d, which is greater than the current height %d",
-			signInfo.StartHeight, height)
+		return false, &signInfo, nil
 	}
 	index := (height - signInfo.StartHeight) % signedBlocksWindow
 
```

### x/finality/keeper/power_dist_change_test.go
```diff
@@ -5,15 +5,26 @@ import (
 	"testing"
 	"time"
 
+	sdkmath "cosmossdk.io/math"
 	"github.com/btcsuite/btcd/btcec/v2"
+	"github.com/btcsuite/btcd/chaincfg"
+	"github.com/btcsuite/btcd/txscript"
+	"github.com/btcsuite/btcd/wire"
+	sdk "github.com/cosmos/cosmos-sdk/types"
 	"github.com/decred/dcrd/dcrec/secp256k1/v4"
 	"github.com/golang/mock/gomock"
 	"github.com/stretchr/testify/require"
 
+	babylonApp "github.com/babylonlabs-io/babylon/app"
 	testutil "github.com/babylonlabs-io/babylon/testutil/btcstaking-helper"
 	"github.com/babylonlabs-io/babylon/testutil/datagen"
+	bbn "github.com/babylonlabs-io/babylon/types"
+	btcctypes "github.com/babylonlabs-io/babylon/x/btccheckpoint/types"
+	btclckeeper "github.com/babylonlabs-io/babylon/x/btclightclient/keeper"
 	btclctypes "github.com/babylonlabs-io/babylon/x/btclightclient/types"
+	btcstakingkeeper "github.com/babylonlabs-io/babylon/x/btcstaking/keeper"
 	"github.com/babylonlabs-io/babylon/x/btcstaking/types"
+	finalitykeeper "github.com/babylonlabs-io/babylon/x/finality/keeper"
 	ftypes "github.com/babylonlabs-io/babylon/x/finality/types"
 )
 
@@ -949,3 +960,352 @@ func TestDoNotGenerateDuplicateEventsAfterHavingCovenantQuorum(t *testing.T) {
 	require.Equal(t, expectedStakingTxHash, btcDelStateUpdate.StakingTxHash)
 	require.Equal(t, types.BTCDelegationStatus_ACTIVE, btcDelStateUpdate.NewState)
 }
+
+// TestHandleLivenessPanic is to test whether the handle liveness will panic
+// in the case where an fp becomes active -> non-active -> active quickly
+func TestHandleLivenessPanic(t *testing.T) {
+	// Initial setup
+	r := rand.New(rand.NewSource(12312312312))
+	app := babylonApp.Setup(t, false)
+	ctx := app.BaseApp.NewContext(false)
+
+	defaultStakingKeeper := app.StakingKeeper
+	btcStakingKeeper := app.BTCStakingKeeper
+	btcStakingMsgServer := btcstakingkeeper.NewMsgServerImpl(btcStakingKeeper)
+	btcLcKeeper := app.BTCLightClientKeeper
+	btcLcMsgServer := btclckeeper.NewMsgServerImpl(btcLcKeeper)
+
+	btcCcKeeper := app.BtcCheckpointKeeper
+	epochingKeeper := app.EpochingKeeper
+	checkpointingKeeper := app.CheckpointingKeeper
+
+	finalityKeeper := app.FinalityKeeper
+	finalityMsgServer := finalitykeeper.NewMsgServerImpl(finalityKeeper)
+	finalityParams := ftypes.DefaultParams()
+	finalityParams.MaxActiveFinalityProviders = 5
+	_ = finalityKeeper.SetParams(ctx, finalityParams)
+
+	epochingKeeper.InitEpoch(ctx)
+	initHeader := ctx.HeaderInfo()
+	initHeader.Height = int64(1)
+	ctx = ctx.WithHeaderInfo(initHeader)
+
+	// Generate Covenant related keys
+	covenantSKs, covenantPKs, err := datagen.GenRandomBTCKeyPairs(r, 1)
+	require.NoError(t, err)
+	slashingAddress, err := datagen.GenRandomBTCAddress(r, &chaincfg.SimNetParams)
+	require.NoError(t, err)
+	slashingPkScript, err := txscript.PayToAddrScript(slashingAddress)
+	require.NoError(t, err)
+
+	CcParams := btcCcKeeper.GetParams(ctx)
+	CcParams.BtcConfirmationDepth = 1 // for simulation
+	err = btcCcKeeper.SetParams(ctx, CcParams)
+	require.NoError(t, err)
+
+	// 0. BTCStakingKeeper parameter setting
+	err = btcStakingKeeper.SetParams(ctx, types.Params{
+		CovenantPks:               bbn.NewBIP340PKsFromBTCPKs(covenantPKs),
+		CovenantQuorum:            1,
+		MinStakingValueSat:        10000,
+		MaxStakingValueSat:        int64(4000 * 10e8),
+		MinStakingTimeBlocks:      400,
+		MaxStakingTimeBlocks:      10000,
+		SlashingPkScript:          slashingPkScript,
+		MinSlashingTxFeeSat:       100,
+		MinCommissionRate:         sdkmath.LegacyMustNewDecFromStr("0.01"),
+		SlashingRate:              sdkmath.LegacyNewDecWithPrec(int64(datagen.RandomInt(r, 41)+10), 2),
+		UnbondingTimeBlocks:       100,
+		UnbondingFeeSat:           1000,
+		AllowListExpirationHeight: 0,
+		BtcActivationHeight:       1,
+	})
+	require.NoError(t, err)
+
+	valset, err := defaultStakingKeeper.GetAllValidators(ctx)
+	require.NoError(t, err)
+	t.Logf("[+] initial validator set length : %d\n", len(valset))
+
+	header := ctx.HeaderInfo()
+	maximumSimulateBlocks := 5
+
+	// Epoch and checkpoint setting
+	t.Logf("Current Epoch Number : %d\n", epochingKeeper.GetEpoch(ctx).GetEpochNumber())
+	checkpointingKeeper.SetLastFinalizedEpoch(ctx, 1)
+
+	// Among externally created FPs, save the FP where i==5
+	var targetFp *types.FinalityProvider
+	var targetFpSK *btcec.PrivateKey
+
+	fpNum := 6
+	for i := 0; i < fpNum; i++ {
+		// Create FP externally and pass it when called
+		fpSK, _, err := datagen.GenRandomBTCKeyPair(r)
+		require.NoError(t, err)
+		fp, err := datagen.GenRandomFinalityProviderWithBTCSK(r, fpSK, "")
+		require.NoError(t, err)
+		// Save when i is 5
+		if i == 1 {
+			targetFp = fp
+			targetFpSK = fpSK
+		}
+		createDelegationWithFinalityProvider(
+			t, ctx, r, i,
+			fp, fpSK, // Pass already created FP info
+			btcStakingMsgServer, btcLcMsgServer, finalityMsgServer,
+			btcStakingKeeper, btcLcKeeper,
+			covenantSKs, covenantPKs, false,
+		)
+	}
+
+	// Block simulation
+	for i := 0; i < maximumSimulateBlocks; i++ {
+		ctx = ctx.WithHeaderInfo(header)
+		ctx = ctx.WithBlockHeight(header.Height)
+
+		t.Logf("-------- BeginBlock : %d ---------\n", header.Height)
+		_, err := app.BeginBlocker(ctx)
+		require.NoError(t, err)
+
+		dc := finalityKeeper.GetVotingPowerDistCache(ctx, uint64(header.Height))
+		activeFps := dc.GetActiveFinalityProviderSet()
+		var fpsList []*ftypes.FinalityProviderDistInfo
+		for _, v := range activeFps {
+			fpsList = append(fpsList, v)
+		}
+		ftypes.SortFinalityProvidersWithZeroedVotingPower(fpsList)
+
+		t.Logf("block height : %d, activeFps length : %d\n", ctx.HeaderInfo().Height, len(fpsList))
+		for fpIndex, fp := range fpsList {
+			t.Logf("fpIndex : %d, active fp address : %v, voting power : %d\n",
+				fpIndex, fp.BtcPk.MarshalHex(), fp.TotalBondedSat)
+		}
+
+		// Example: At block height 3, create additional delegation using FP (targetFp) created at i==5
+		if i == 2 {
+			// targetFp and targetFpSK must be non-nil
+			// Create FP externally and pass it when called
+			newfpSK, _, err := datagen.GenRandomBTCKeyPair(r)
+			require.NoError(t, err)
+			newfp, err := datagen.GenRandomFinalityProviderWithBTCSK(r, newfpSK, "")
+			require.NoError(t, err)
+
+			createDelegationWithFinalityProvider(
+				t, ctx, r, fpNum,
+				newfp, newfpSK, // Use i==5 FP info
+				btcStakingMsgServer, btcLcMsgServer, finalityMsgServer,
+				btcStakingKeeper, btcLcKeeper,
+				covenantSKs, covenantPKs, false,
+			)
+		}
+
+		if i == 3 {
+			// targetFp and targetFpSK must be non-nil
+			require.NotNil(t, targetFp)
+			require.NotNil(t, targetFpSK)
+			createDelegationWithFinalityProvider(
+				t, ctx, r, 5,
+				targetFp, targetFpSK, // Use i==5 FP info
+				btcStakingMsgServer, btcLcMsgServer, finalityMsgServer,
+				btcStakingKeeper, btcLcKeeper,
+				covenantSKs, covenantPKs, true,
+			)
+		}
+
+		_, err = app.EndBlocker(ctx)
+		t.Logf("-------- EndBlock height : %d---------\n", header.Height)
+		require.NoError(t, err)
+		header.Height++
+	}
+}
+
+func createDelegationWithFinalityProvider(
+	t *testing.T,
+	ctx sdk.Context,
+	r *rand.Rand,
+	fpIndex int,
+	fpInfo *types.FinalityProvider, // Must be non-nil
+	fpSK *btcec.PrivateKey, // Must be non-nil
+	btcStakingMsgServer types.MsgServer,
+	btcLcMsgServer btclctypes.MsgServer,
+	finalityMsgServer ftypes.MsgServer, // Use finality related MsgServer type
+	btcStakingKeeper btcstakingkeeper.Keeper, // keeper (passed by value)
+	btcLcKeeper btclckeeper.Keeper,
+	covenantSKs []*btcec.PrivateKey,
+	covenantPKs []*btcec.PublicKey,
+	createFinalityProviderSkip bool,
+) {
+	require.NotNil(t, fpInfo, "fpInfo must be provided")
+	require.NotNil(t, fpSK, "fpSK must be provided")
+	finalityFP := fpInfo
+	finalityPriv := fpSK
+
+	// 1. Create and Commit FinalityProvider (call separate function)
+	if createFinalityProviderSkip == false {
+		createAndCommitFinalityProvider(t, ctx, r, finalityFP, finalityPriv, btcStakingMsgServer, finalityMsgServer)
+	}
+
+	// 2. Prepare delegation creation
+	bsParams := btcStakingKeeper.GetParams(ctx)
+	covPKs, err := bbn.NewBTCPKsFromBIP340PKs(bsParams.CovenantPks)
+	require.NoError(t, err)
+	stakingValue := int64((fpIndex + 1) * 10e8)
+	unbondingTime := bsParams.UnbondingTimeBlocks
+
+	// Generate delegator keys and create Staking info
+	delSK, _, err := datagen.GenRandomBTCKeyPair(r)
+	require.NoError(t, err)
+	stakingTime := 1000
+
+	testStakingInfo := datagen.GenBTCStakingSlashingInfo(
+		r, t, &chaincfg.SimNetParams,
+		delSK, []*btcec.PublicKey{finalityFP.BtcPk.MustToBTCPK()},
+		covPKs, bsParams.CovenantQuorum,
+		uint16(stakingTime), stakingValue,
+		bsParams.SlashingPkScript, bsParams.SlashingRate,
+		uint16(unbondingTime),
+	)
+
+	stakingMsgTx := testStakingInfo.StakingTx
+	serializedStakingTx, err := bbn.SerializeBTCTx(stakingMsgTx)
+	require.NoError(t, err)
+
+	// Delegator account and PoP creation
+	acc := datagen.GenRandomAccount()
+	stakerAddr := sdk.MustAccAddressFromBech32(acc.Address)
+	pop, err := datagen.NewPoPBTC(stakerAddr, delSK)
+	require.NoError(t, err)
+
+	// Tx inclusion proof for Tx
+	prevBlockHeader := btcLcKeeper.GetTipInfo(ctx).Header.ToBlockHeader()
+	btcHeaderWithProof := datagen.CreateBlockWithTransaction(r, prevBlockHeader, stakingMsgTx)
+	btcHeader := btcHeaderWithProof.HeaderBytes
+
+	dummy1Tx := datagen.CreateDummyTx()
+	dummy1HeaderWithProof := datagen.CreateBlockWithTransaction(r, btcHeader.ToBlockHeader(), dummy1Tx)
+	dummy1Header := dummy1HeaderWithProof.HeaderBytes
+
+	txInclusionProof := types.NewInclusionProof(
+		&btcctypes.TransactionKey{Index: 1, Hash: btcHeader.Hash()},
+		btcHeaderWithProof.SpvProof.MerkleNodes,
+	)
+	headers := []bbn.BTCHeaderBytes{btcHeader, dummy1Header}
+	insertHeaderMsg := &btclctypes.MsgInsertHeaders{
+		Signer:  stakerAddr.String(),
+		Headers: headers,
+	}
+	_, err = btcLcMsgServer.InsertHeaders(ctx, insertHeaderMsg)
+	require.NoError(t, err)
+
+	// Delegator signature creation
+	slashingPathInfo, err := testStakingInfo.StakingInfo.SlashingPathSpendInfo()
+	require.NoError(t, err)
+	delegatorSig, err := testStakingInfo.SlashingTx.Sign(
+		stakingMsgTx, 0, slashingPathInfo.GetPkScriptPath(), delSK,
+	)
+	require.NoError(t, err)
+
+	// 3. Unbonding related info creation
+	stkTxHash := testStakingInfo.StakingTx.TxHash()
+	unbondingValue := stakingValue - datagen.UnbondingTxFee
+	testUnbondingInfo := datagen.GenBTCUnbondingSlashingInfo(
+		r, t, &chaincfg.SimNetParams,
+		delSK, []*btcec.PublicKey{finalityFP.BtcPk.MustToBTCPK()},
+		covenantPKs, bsParams.CovenantQuorum,
+		wire.NewOutPoint(&stkTxHash, datagen.StakingOutIdx),
+		uint16(unbondingTime), unbondingValue,
+		bsParams.SlashingPkScript, bsParams.SlashingRate,
+		uint16(unbondingTime),
+	)
+	unbondingTx, err := bbn.SerializeBTCTx(testUnbondingInfo.UnbondingTx)
+	require.NoError(t, err)
+	delUnbondingSlashingSig, err := testUnbondingInfo.GenDelSlashingTxSig(delSK)
+	require.NoError(t, err)
+
+	// 4. Delegation creation message sending
+	msgCreateBTCDel := &types.MsgCreateBTCDelegation{
+		StakerAddr:                    stakerAddr.String(),
+		FpBtcPkList:                   []bbn.BIP340PubKey{*finalityFP.BtcPk},
+		BtcPk:                         bbn.NewBIP340PubKeyFromBTCPK(delSK.PubKey()),
+		Pop:                           pop,
+		StakingTime:                   uint32(stakingTime),
+		StakingValue:                  stakingValue,
+		StakingTx:                     serializedStakingTx,
+		StakingTxInclusionProof:       txInclusionProof,
+		SlashingTx:                    testStakingInfo.SlashingTx,
+		DelegatorSlashingSig:          delegatorSig,
+		UnbondingTx:                   unbondingTx,
+		UnbondingTime:                 unbondingTime,
+		UnbondingValue:                unbondingValue,
+		UnbondingSlashingTx:           testUnbondingInfo.SlashingTx,
+		DelegatorUnbondingSlashingSig: delUnbondingSlashingSig,
+	}
+	_, err = btcStakingMsgServer.CreateBTCDelegation(ctx, msgCreateBTCDel)
+	require.NoError(t, err)
+
+	// 5. Covenant Signature addition
+	stakingTxHash := testStakingInfo.StakingTx.TxHash()
+	vPKs, err := bbn.NewBTCPKsFromBIP340PKs(msgCreateBTCDel.FpBtcPkList)
+	require.NoError(t, err)
+
+	covenantSlashingTxSigs, err := datagen.GenCovenantAdaptorSigs(
+		covenantSKs, vPKs,
+		testStakingInfo.StakingTx, slashingPathInfo.GetPkScriptPath(),
+		msgCreateBTCDel.SlashingTx,
+	)
+	require.NoError(t, err)
+
+	unbondingSlashingPathInfo, err := testUnbondingInfo.UnbondingInfo.SlashingPathSpendInfo()
+	require.NoError(t, err)
+	covenantUnbondingSlashingTxSigs, err := datagen.GenCovenantAdaptorSigs(
+		covenantSKs, vPKs,
+		testUnbondingInfo.UnbondingTx, unbondingSlashingPathInfo.GetPkScriptPath(),
+		testUnbondingInfo.SlashingTx,
+	)
+	require.NoError(t, err)
+
+	unbondingPathInfo, err := testStakingInfo.StakingInfo.UnbondingPathSpendInfo()
+	require.NoError(t, err)
+	covUnbondingSigs, err := datagen.GenCovenantUnbondingSigs(
+		covenantSKs, testStakingInfo.StakingTx,
+		0, unbondingPathInfo.GetPkScriptPath(),
+		testUnbondingInfo.UnbondingTx,
+	)
+	require.NoError(t, err)
+
+	msgAddCovenantSig := &types.MsgAddCovenantSigs{
+		Signer:                  msgCreateBTCDel.StakerAddr,
+		Pk:                      covenantSlashingTxSigs[0].CovPk,
+		StakingTxHash:           stakingTxHash.String(),
+		SlashingTxSigs:          covenantSlashingTxSigs[0].AdaptorSigs,
+		UnbondingTxSig:          bbn.NewBIP340SignatureFromBTCSig(covUnbondingSigs[0]),
+		SlashingUnbondingTxSigs: covenantUnbondingSlashingTxSigs[0].AdaptorSigs,
+	}
+	_, err = btcStakingMsgServer.AddCovenantSigs(ctx, msgAddCovenantSig)
+	require.NoError(t, err)
+}
+
+func createAndCommitFinalityProvider(
+	t *testing.T,
+	ctx sdk.Context,
+	r *rand.Rand,
+	fp *types.FinalityProvider,
+	fpSK *btcec.PrivateKey,
+	btcStakingMsgServer types.MsgServer,
+	finalityMsgServer ftypes.MsgServer,
+) {
+	fpMsg := &types.MsgCreateFinalityProvider{
+		Addr:        fp.Addr,
+		Description: fp.Description,
+		Commission:  types.NewCommissionRates(*fp.Commission, fp.CommissionInfo.MaxRate, fp.CommissionInfo.MaxChangeRate),
+		BtcPk:       fp.BtcPk,
+		Pop:         fp.Pop,
+	}
+	_, err := btcStakingMsgServer.CreateFinalityProvider(ctx, fpMsg)
+	require.NoError(t, err)
+
+	_, msgCommitPubRandList, err := datagen.GenRandomMsgCommitPubRandList(r, fpSK, 1, 300)
+	require.NoError(t, err)
+	_, err = finalityMsgServer.CommitPubRandList(ctx, msgCommitPubRandList)
+	require.NoError(t, err)
+}
```
