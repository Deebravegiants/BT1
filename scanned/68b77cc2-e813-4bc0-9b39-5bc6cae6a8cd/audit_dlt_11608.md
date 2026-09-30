# [?] Fix vulnerability when processing bls sig transactions (#287)

## Summary
Severity: Unknown
Chain: Babylon
Component: babylonlabs-io/babylon
Published: 2023-01-19
Source: https://github.com/babylonlabs-io/babylon/commit/947918885d4e5b39d4a2a2ebd950d23f07af25c2
Type: security-commit

## Details
Fix vulnerability when processing bls sig transactions (#287)

## Patch
### app/test_helpers.go
```diff
@@ -95,7 +95,6 @@ func setup(withGenesis bool, invCheckPeriod uint) (*BabylonApp, GenesisState) {
 // one validator in validator set during InitGenesis abci call - https://github.com/cosmos/cosmos-sdk/pull/9697
 func NewBabyblonAppWithCustomOptions(t *testing.T, isCheckTx bool, privSigner *PrivSigner, options SetupOptions) *BabylonApp {
 	t.Helper()
-
 	privVal := datagen.NewPV()
 	pubKey, err := privVal.GetPubKey()
 	require.NoError(t, err)
```

### x/checkpointing/keeper/bls_signer.go
```diff
@@ -2,9 +2,10 @@ package keeper
 
 import (
 	"fmt"
-	epochingtypes "github.com/babylonchain/babylon/x/epoching/types"
 	"time"
 
+	epochingtypes "github.com/babylonchain/babylon/x/epoching/types"
+
 	"github.com/babylonchain/babylon/client/tx"
 	"github.com/babylonchain/babylon/crypto/bls12381"
 	"github.com/babylonchain/babylon/types/retry"
```

### x/checkpointing/keeper/keeper.go
```diff
@@ -87,6 +87,11 @@ func (k Keeper) addBlsSig(ctx sdk.Context, sig *types.BlsSig) error {
 		return nil
 	}
 
+	if !sig.LastCommitHash.Equal(*ckptWithMeta.Ckpt.LastCommitHash) {
+		// processed BlsSig message is for invalid last commit hash
+		return types.ErrInvalidLastCommitHash
+	}
+
 	// get signer's address
 	signerAddr, err := sdk.ValAddressFromBech32(sig.SignerAddress)
 	if err != nil {
```

### x/checkpointing/keeper/msg_server_test.go
```diff
@@ -163,6 +163,31 @@ func FuzzWrappedCreateValidator(f *testing.F) {
 	})
 }
 
+func TestInvalidLastCommitHash(t *testing.T) {
+	helper := testepoching.NewHelperWithValSet(t)
+	ck := helper.App.CheckpointingKeeper
+	msgServer := checkpointingkeeper.NewMsgServerImpl(ck)
+	// needed to init total voting power
+	helper.BeginBlock()
+
+	epoch := uint64(1)
+	validLch := datagen.GenRandomByteArray(32)
+	// correct checkpoint for epoch 1
+	_, err := ck.BuildRawCheckpoint(helper.Ctx, epoch, validLch)
+	require.NoError(t, err)
+
+	// Malicious validator created message with valid bls signature but for invalid
+	// commit hash
+	invalidLch := datagen.GenRandomByteArray(32)
+	val0Info := helper.ValBlsPrivKeys[0]
+	signBytes := append(sdk.Uint64ToBigEndian(epoch), invalidLch...)
+	sig := bls12381.Sign(val0Info.BlsKey, signBytes)
+	msg := types.NewMsgAddBlsSig(epoch, invalidLch, sig, val0Info.Address)
+
+	_, err = msgServer.AddBlsSig(helper.Ctx, msg)
+	require.ErrorIs(t, err, types.ErrInvalidLastCommitHash)
+}
+
 func buildMsgWrappedCreateValidator(addr sdk.AccAddress) (*types.MsgWrappedCreateValidator, error) {
 	tmValPrivkey := ed25519.GenPrivKey()
 	bondTokens := sdk.TokensFromConsensusPower(10, sdk.DefaultPowerReduction)
```

### x/checkpointing/types/errors.go
```diff
@@ -16,4 +16,5 @@ var (
 	ErrBlsKeyAlreadyExist     = sdkerrors.Register(ModuleName, 1210, "BLS public key already exists")
 	ErrBlsPrivKeyDoesNotExist = sdkerrors.Register(ModuleName, 1211, "BLS private key does not exist")
 	ErrConflictingCheckpoint  = sdkerrors.Register(ModuleName, 1212, "Conflicting checkpoint is found")
+	ErrInvalidLastCommitHash  = sdkerrors.Register(ModuleName, 1213, "Provided last commit hash is Invalid")
 )
```

### x/epoching/testepoching/helper.go
```diff
@@ -8,7 +8,6 @@ import (
 
 	"cosmossdk.io/math"
 	appparams "github.com/babylonchain/babylon/app/params"
-
 	"github.com/stretchr/testify/require"
 
 	"github.com/babylonchain/babylon/app"
@@ -26,6 +25,11 @@ import (
 	tmproto "github.com/tendermint/tendermint/proto/tendermint/types"
 )
 
+type ValidatorInfo struct {
+	BlsKey  bls12381.PrivateKey
+	Address sdk.ValAddress
+}
+
 // Helper is a structure which wraps the entire app and exposes functionalities for testing the epoching module
 type Helper struct {
 	t *testing.T
@@ -37,7 +41,8 @@ type Helper struct {
 	QueryClient    types.QueryClient
 	StakingKeeper  *stakingkeeper.Keeper
 
-	GenAccs []authtypes.GenesisAccount
+	GenAccs        []authtypes.GenesisAccount
+	ValBlsPrivKeys []ValidatorInfo
 }
 
 // NewHelper creates the helper for testing the epoching module
@@ -51,7 +56,8 @@ func NewHelper(t *testing.T) *Helper {
 	valSet := epochingKeeper.GetValidatorSet(ctx, 0)
 	require.Len(t, valSet, 1)
 	genesisVal := valSet[0]
-	genesisBLSPubkey := bls12381.GenPrivKey().PubKey()
+	blsPrivKey := bls12381.GenPrivKey()
+	genesisBLSPubkey := blsPrivKey.PubKey()
 	err := app.CheckpointingKeeper.CreateRegistration(ctx, genesisBLSPubkey, genesisVal.Addr)
 	require.NoError(t, err)
 
@@ -61,7 +67,20 @@ func NewHelper(t *testing.T) *Helper {
 	queryClient := types.NewQueryClient(queryHelper)
 	msgSrvr := keeper.NewMsgServerImpl(epochingKeeper)
 
-	return &Helper{t, ctx, app, &epochingKeeper, msgSrvr, queryClient, &app.StakingKeeper, nil}
+	return &Helper{
+		t,
+		ctx,
+		app,
+		&epochingKeeper,
+		msgSrvr,
+		queryClient,
+		&app.StakingKeeper,
+		nil,
+		[]ValidatorInfo{ValidatorInfo{
+			blsPrivKey,
+			genesisVal.Addr,
+		}},
+	}
 }
 
 // NewHelperWithValSet is same as NewHelper, except that it creates a set of validators
@@ -86,22 +105,23 @@ func NewHelperWithValSet(t *testing.T) *Helper {
 
 	// get necessary subsets of the app/keeper
 	epochingKeeper := app.EpochingKeeper
-
+	valInfos := []ValidatorInfo{}
 	// add BLS pubkey to the genesis validator
 	valSet := epochingKeeper.GetValidatorSet(ctx, 0)
 	for _, val := range valSet {
-		blsPubkey := bls12381.GenPrivKey().PubKey()
+		blsPrivKey := bls12381.GenPrivKey()
+		valInfos = append(valInfos, ValidatorInfo{blsPrivKey, val.Addr})
+		blsPubkey := blsPrivKey.PubKey()
 		err = app.CheckpointingKeeper.CreateRegistration(ctx, blsPubkey, val.Addr)
 		require.NoError(t, err)
 	}
-
 	querier := keeper.Querier{Keeper: epochingKeeper}
 	queryHelper := baseapp.NewQueryServerTestHelper(ctx, app.InterfaceRegistry())
 	types.RegisterQueryServer(queryHelper, querier)
 	queryClient := types.NewQueryClient(queryHelper)
 	msgSrvr := keeper.NewMsgServerImpl(epochingKeeper)
 
-	return &Helper{t, ctx, app, &epochingKeeper, msgSrvr, queryClient, &app.StakingKeeper, GenAccs}
+	return &Helper{t, ctx, app, &epochingKeeper, msgSrvr, queryClient, &app.StakingKeeper, GenAccs, valInfos}
 }
 
 // GenAndApplyEmptyBlock generates a new empty block and appends it to the current blockchain
```
