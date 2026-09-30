# [?] imp(staking): detect the length of the ed25519 pubkey in CreateValidator to prevent panic (#18506)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cosmos/cosmos-sdk
Published: 2023-11-27
Source: https://github.com/cosmos/cosmos-sdk/commit/d3e662da1f1ffe2aedd891c6b62b7d28ea726160
Type: security-commit

## Details
imp(staking): detect the length of the ed25519 pubkey in CreateValidator to prevent panic (#18506)

## Patch
### CHANGELOG.md
```diff
@@ -65,6 +65,7 @@ Ref: https://keepachangelog.com/en/1.0.0/
 * [#17733](https://github.com/cosmos/cosmos-sdk/pull/17733) Ensure `buf export` exports all proto dependencies
 * (version) [#18063](https://github.com/cosmos/cosmos-sdk/pull/18063) Include additional information in the Info struct. This change enhances the Info struct by adding support for additional information through the ExtraInfo field
 * (crypto | x/auth) [#14372](https://github.com/cosmos/cosmos-sdk/pull/18194) Key checks on signatures antehandle.
+* (staking) [#18506](https://github.com/cosmos/cosmos-sdk/pull/18506) Detect the length of the ed25519 pubkey in CreateValidator to prevent panic.
 
 ### Bug Fixes
 
```

### types/staking.go
```diff
@@ -22,6 +22,9 @@ var (
 
 	// DefaultPowerReduction is the default amount of staking tokens required for 1 unit of consensus-engine power
 	DefaultPowerReduction = sdkmath.NewIntFromUint64(1000000)
+
+	// PubKeyEd25519Type is ed25519 for type the consensus params validator pub_key_types params
+	PubKeyEd25519Type = "ed25519"
 )
 
 // TokensToConsensusPower - convert input tokens to potential consensus-engine power
```

### x/staking/keeper/msg_server.go
```diff
@@ -3,6 +3,7 @@ package keeper
 import (
 	"context"
 	"errors"
+	"slices"
 	"strconv"
 	"time"
 
@@ -15,6 +16,7 @@ import (
 	"cosmossdk.io/math"
 	"cosmossdk.io/x/staking/types"
 
+	"github.com/cosmos/cosmos-sdk/crypto/keys/ed25519"
 	cryptotypes "github.com/cosmos/cosmos-sdk/crypto/types"
 	"github.com/cosmos/cosmos-sdk/telemetry"
 	sdk "github.com/cosmos/cosmos-sdk/types"
@@ -60,7 +62,26 @@ func (k msgServer) CreateValidator(ctx context.Context, msg *types.MsgCreateVali
 
 	pk, ok := msg.Pubkey.GetCachedValue().(cryptotypes.PubKey)
 	if !ok {
-		return nil, errorsmod.Wrapf(sdkerrors.ErrInvalidType, "Expecting cryptotypes.PubKey, got %T", pk)
+		return nil, errorsmod.Wrapf(sdkerrors.ErrInvalidType, "Expecting cryptotypes.PubKey, got %T", msg.Pubkey.GetCachedValue())
+	}
+
+	sdkCtx := sdk.UnwrapSDKContext(ctx)
+	cp := sdkCtx.ConsensusParams()
+	if cp.Validator != nil {
+		pkType := pk.Type()
+		if !slices.Contains(cp.Validator.PubKeyTypes, pkType) {
+			return nil, errorsmod.Wrapf(
+				types.ErrValidatorPubKeyTypeNotSupported,
+				"got: %s, expected: %s", pk.Type(), cp.Validator.PubKeyTypes,
+			)
+		}
+
+		if pkType == sdk.PubKeyEd25519Type && len(pk.Bytes()) != ed25519.PubKeySize {
+			return nil, errorsmod.Wrapf(
+				types.ErrConsensusPubKeyLenInvalid,
+				"got: %d, expected: %d", len(pk.Bytes()), ed25519.PubKeySize,
+			)
+		}
 	}
 
 	if _, err := k.GetValidatorByConsAddr(ctx, sdk.GetConsAddress(pk)); err == nil {
@@ -82,25 +103,6 @@ func (k msgServer) CreateValidator(ctx context.Context, msg *types.MsgCreateVali
 		return nil, err
 	}
 
-	sdkCtx := sdk.UnwrapSDKContext(ctx)
-	cp := sdkCtx.ConsensusParams()
-	if cp.Validator != nil {
-		pkType := pk.Type()
-		hasKeyType := false
-		for _, keyType := range cp.Validator.PubKeyTypes {
-			if pkType == keyType {
-				hasKeyType = true
-				break
-			}
-		}
-		if !hasKeyType {
-			return nil, errorsmod.Wrapf(
-				types.ErrValidatorPubKeyTypeNotSupported,
-				"got: %s, expected: %s", pk.Type(), cp.Validator.PubKeyTypes,
-			)
-		}
-	}
-
 	validator, err := types.NewValidator(msg.ValidatorAddress, pk, msg.Description)
 	if err != nil {
 		return nil, err
```

### x/staking/keeper/msg_server_test.go
```diff
@@ -4,6 +4,7 @@ import (
 	"testing"
 	"time"
 
+	cmtproto "github.com/cometbft/cometbft/proto/tendermint/types"
 	"github.com/golang/mock/gomock"
 
 	"cosmossdk.io/collections"
@@ -14,6 +15,7 @@ import (
 	"github.com/cosmos/cosmos-sdk/codec/address"
 	codectypes "github.com/cosmos/cosmos-sdk/codec/types"
 	"github.com/cosmos/cosmos-sdk/crypto/keys/ed25519"
+	cryptotypes "github.com/cosmos/cosmos-sdk/crypto/types"
 	simtestutil "github.com/cosmos/cosmos-sdk/testutil/sims"
 	sdk "github.com/cosmos/cosmos-sdk/types"
 )
@@ -40,6 +42,16 @@ func (s *KeeperTestSuite) TestMsgCreateValidator() {
 	pubkey, err := codectypes.NewAnyWithValue(pk1)
 	require.NoError(err)
 
+	var ed25519pk cryptotypes.PubKey = &ed25519.PubKey{Key: []byte{1, 2, 3, 4, 5, 6}}
+	pubkeyInvalidLen, err := codectypes.NewAnyWithValue(ed25519pk)
+	require.NoError(err)
+
+	ctx = ctx.WithConsensusParams(cmtproto.ConsensusParams{
+		Validator: &cmtproto.ValidatorParams{
+			PubKeyTypes: []string{sdk.PubKeyEd25519Type},
+		},
+	})
+
 	testCases := []struct {
 		name      string
 		input     *stakingtypes.MsgCreateValidator
@@ -59,7 +71,7 @@ func (s *KeeperTestSuite) TestMsgCreateValidator() {
 				DelegatorAddress:  Addr.String(),
 				ValidatorAddress:  ValAddr.String(),
 				Pubkey:            pubkey,
-				Value:             sdk.NewInt64Coin("stake", 10000),
+				Value:             sdk.NewInt64Coin(sdk.DefaultBondDenom, 10000),
 			},
 			expErr:    true,
 			expErrMsg: "empty description",
@@ -79,7 +91,7 @@ func (s *KeeperTestSuite) TestMsgCreateValidator() {
 				DelegatorAddress:  Addr.String(),
 				ValidatorAddress:  sdk.AccAddress([]byte("invalid")).String(),
 				Pubkey:            pubkey,
-				Value:             sdk.NewInt64Coin("stake", 10000),
+				Value:             sdk.NewInt64Coin(sdk.DefaultBondDenom, 10000),
 			},
 			expErr:    true,
 			expErrMsg: "invalid validator address",
@@ -99,11 +111,31 @@ func (s *KeeperTestSuite) TestMsgCreateValidator() {
 				DelegatorAddress:  Addr.String(),
 				ValidatorAddress:  ValAddr.String(),
 				Pubkey:            nil,
-				Value:             sdk.NewInt64Coin("stake", 10000),
+				Value:             sdk.NewInt64Coin(sdk.DefaultBondDenom, 10000),
 			},
 			expErr:    true,
 			expErrMsg: "empty validator public key",
 		},
+		{
+			name: "validator pubkey len is invalid",
+			input: &stakingtypes.MsgCreateValidator{
+				Description: stakingtypes.Description{
+					Moniker: "NewValidator",
+				},
+				Commission: stakingtypes.CommissionRates{
+					Rate:          math.LegacyNewDecWithPrec(5, 1),
+					MaxRate:       math.LegacyNewDecWithPrec(5, 1),
+					MaxChangeRate: math.LegacyNewDec(0),
+				},
+				MinSelfDelegation: math.NewInt(1),
+				DelegatorAddress:  Addr.String(),
+				ValidatorAddress:  ValAddr.String(),
+				Pubkey:            pubkeyInvalidLen,
+				Value:             sdk.NewInt64Coin(sdk.DefaultBondDenom, 10000),
+			},
+			expErr:    true,
+			expErrMsg: "consensus pubkey len is invalid",
+		},
 		{
 			name: "empty delegation amount",
 			input: &stakingtypes.MsgCreateValidator{
@@ -119,7 +151,7 @@ func (s *KeeperTestSuite) TestMsgCreateValidator() {
 				DelegatorAddress:  Addr.String(),
 				ValidatorAddress:  ValAddr.String(),
 				Pubkey:            pubkey,
-				Value:             sdk.NewInt64Coin("stake", 0),
+				Value:             sdk.NewInt64Coin(sdk.DefaultBondDenom, 0),
 			},
 			expErr:    true,
 			expErrMsg: "invalid delegation amount",
@@ -159,7 +191,7 @@ func (s *KeeperTestSuite) TestMsgCreateValidator() {
 				DelegatorAddress:  Addr.String(),
 				ValidatorAddress:  ValAddr.String(),
 				Pubkey:            pubkey,
-				Value:             sdk.NewInt64Coin("stake", 10000),
+				Value:             sdk.NewInt64Coin(sdk.DefaultBondDenom, 10000),
 			},
 			expErr:    true,
 			expErrMsg: "minimum self delegation must be a positive integer",
@@ -179,7 +211,7 @@ func (s *KeeperTestSuite) TestMsgCreateValidator() {
 				DelegatorAddress:  Addr.String(),
 				ValidatorAddress:  ValAddr.String(),
 				Pubkey:            pubkey,
-				Value:             sdk.NewInt64Coin("stake", 10000),
+				Value:             sdk.NewInt64Coin(sdk.DefaultBondDenom, 10000),
 			},
 			expErr:    true,
 			expErrMsg: "minimum self delegation must be a positive integer",
@@ -199,7 +231,7 @@ func (s *KeeperTestSuite) TestMsgCreateValidator() {
 				DelegatorAddress:  Addr.String(),
 				ValidatorAddress:  ValAddr.String(),
 				Pubkey:            pubkey,
-				Value:             sdk.NewInt64Coin("stake", 10),
+				Value:             sdk.NewInt64Coin(sdk.DefaultBondDenom, 10),
 			},
 			expErr:    true,
 			expErrMsg: "validator's self delegation must be greater than their minimum self delegation",
@@ -223,7 +255,7 @@ func (s *KeeperTestSuite) TestMsgCreateValidator() {
 				DelegatorAddress:  Addr.String(),
 				ValidatorAddress:  ValAddr.String(),
 				Pubkey:            pubkey,
-				Value:             sdk.NewInt64Coin("stake", 10000),
+				Value:             sdk.NewInt64Coin(sdk.DefaultBondDenom, 10000),
 			},
 			expErr: false,
 		},
@@ -253,7 +285,7 @@ func (s *KeeperTestSuite) TestMsgEditValidator() {
 	require.NotNil(pk)
 
 	comm := stakingtypes.NewCommissionRates(math.LegacyNewDec(0), math.LegacyNewDec(0), math.LegacyNewDec(0))
-	msg, err := stakingtypes.NewMsgCreateValidator(ValAddr.String(), pk, sdk.NewCoin("stake", math.NewInt(10)), stakingtypes.Description{Moniker: "NewVal"}, comm, math.OneInt())
+	msg, err := stakingtypes.NewMsgCreateValidator(ValAddr.String(), pk, sdk.NewCoin(sdk.DefaultBondDenom, math.NewInt(10)), stakingtypes.Description{Moniker: "NewVal"}, comm, math.OneInt())
 	require.NoError(err)
 
 	res, err := msgServer.CreateValidator(ctx, msg)
@@ -427,7 +459,7 @@ func (s *KeeperTestSuite) TestMsgDelegate() {
 
 	comm := stakingtypes.NewCommissionRates(math.LegacyNewDec(0), math.LegacyNewDec(0), math.LegacyNewDec(0))
 
-	msg, err := stakingtypes.NewMsgCreateValidator(ValAddr.String(), pk, sdk.NewCoin("stake", math.NewInt(10)), stakingtypes.Description{Moniker: "NewVal"}, comm, math.OneInt())
+	msg, err := stakingtypes.NewMsgCreateValidator(ValAddr.String(), pk, sdk.NewCoin(sdk.DefaultBondDenom, math.NewInt(10)), stakingtypes.Description{Moniker: "NewVal"}, comm, math.OneInt())
 	require.NoError(err)
 
 	res, err := msgServer.CreateValidator(ctx, msg)
```

### x/staking/types/errors.go
```diff
@@ -51,4 +51,5 @@ var (
 	// consensus key errors
 	ErrConsensusPubKeyAlreadyUsedForValidator = errors.Register(ModuleName, 46, "consensus pubkey is already used for a validator")
 	ErrExceedingMaxConsPubKeyRotations        = errors.Register(ModuleName, 47, "exceeding maximum consensus pubkey rotations within unbonding period")
+	ErrConsensusPubKeyLenInvalid              = errors.Register(ModuleName, 48, "consensus pubkey len is invalid")
 )
```
