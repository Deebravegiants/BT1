# [?] fix: remove panic in contracts and add guards for ica and ibc logic  (#1941)

## Summary
Severity: Unknown
Chain: Cronos
Component: crypto-org-chain/cronos
Published: 2025-12-17
Source: https://github.com/crypto-org-chain/cronos/commit/5cabab487a660e6fbb66c4f9bd5c6eb8228f2b7a
Type: security-commit

## Details
fix: remove panic in contracts and add guards for ica and ibc logic  (#1941)

* return calculated gas instead of panic for RelayerContract, add guards for ica precompile and ibc getSourceChannelId

* add guard for Run method for IcaContract

* remove unnecessary else

* minor change

* update to use DefaultGasRequired

## Patch
### CHANGELOG.md
```diff
@@ -7,6 +7,7 @@
 * [#1882](https://github.com/crypto-org-chain/cronos/pull/1882) Support for eip2935
 * [#1880](https://github.com/crypto-org-chain/cronos/pull/1880) Move module from v2 to v1 to follow semver convention
 * [#1933](https://github.com/crypto-org-chain/cronos/pull/1933) Chore: add validation for HeaderHashNum and HistoryServeWindow in evm params
+* [#1941](https://github.com/crypto-org-chain/cronos/pull/1941) fix: return calculated gas instead of panic for RelayerContract, add guards for ica precompile and ibc getSourceChannelId
 
 *Dec 4, 2025*
 
```

### x/cronos/keeper/mock/ibckeeper_mock.go
```diff
@@ -9,6 +9,11 @@ import (
 	sdk "github.com/cosmos/cosmos-sdk/types"
 )
 
+const (
+	emptyTraceIbcDenomHash = "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB"
+	EmptyTraceIbcDenom     = "ibc/" + emptyTraceIbcDenomHash
+)
+
 type IbcKeeperMock struct{}
 
 func (i IbcKeeperMock) Transfer(goCtx context.Context, msg *types.MsgTransfer) (*types.MsgTransferResponse, error) {
@@ -32,5 +37,12 @@ func (i IbcKeeperMock) GetDenom(ctx sdk.Context, denomTraceHash tmbytes.HexBytes
 			Base: "correctIBCToken",
 		}, true
 	}
+
+	if denomTraceHash.String() == emptyTraceIbcDenomHash {
+		return types.Denom{
+			Trace: []types.Hop{},
+			Base:  "emptyTraceToken",
+		}, true
+	}
 	return types.Denom{}, false
 }
```

### x/cronos/keeper/params.go
```diff
@@ -57,7 +57,9 @@ func (k Keeper) GetSourceChannelID(ctx sdk.Context, ibcVoucherDenom string) (cha
 	if !exists {
 		return "", errors.Wrapf(types.ErrIbcCroDenomInvalid, "%s is invalid", ibcVoucherDenom)
 	}
-
+	if len(denomTrace.Trace) == 0 {
+		return "", errors.Wrapf(types.ErrIbcCroDenomInvalid, "%s has empty denom trace", ibcVoucherDenom)
+	}
 	// the path has for format port/channelId
 	return denomTrace.Trace[0].ChannelId, nil
 }
```

### x/cronos/keeper/params_test.go
```diff
@@ -2,6 +2,7 @@ package keeper_test
 
 import (
 	"errors"
+	"fmt"
 
 	cronosmodulekeeper "github.com/crypto-org-chain/cronos/x/cronos/keeper"
 	keepertest "github.com/crypto-org-chain/cronos/x/cronos/keeper/mock"
@@ -32,6 +33,12 @@ func (suite *KeeperTestSuite) TestGetSourceChannelID() {
 				suite.Require().Equal(channelID, "channel-0")
 			},
 		},
+		{
+			"empty denom trace",
+			keepertest.EmptyTraceIbcDenom,
+			fmt.Errorf("%s has empty denom trace: ibc cro denom is invalid", keepertest.EmptyTraceIbcDenom),
+			func(channelID string) {},
+		},
 	}
 
 	for _, tc := range testCases {
```

### x/cronos/keeper/precompiles/ica.go
```diff
@@ -103,6 +103,9 @@ func (ic *IcaContract) RequiredGas(input []byte) uint64 {
 	// base cost to prevent large input size
 	baseCost := uint64(len(input)) * ic.kvGasConfig.WriteCostPerByte
 	var methodID [4]byte
+	if len(input) < 4 {
+		return baseCost
+	}
 	copy(methodID[:], input[:4])
 	requiredGas, ok := icaGasRequiredByMethod[methodID]
 	if icaMethodNamesByID[methodID] == SubmitMsgsMethodName {
@@ -116,6 +119,9 @@ func (ic *IcaContract) RequiredGas(input []byte) uint64 {
 
 func (ic *IcaContract) Run(evm *vm.EVM, contract *vm.Contract, readonly bool) ([]byte, error) {
 	// parse input
+	if len(contract.Input) < 4 {
+		return nil, errors.New("input too short")
+	}
 	methodID := contract.Input[:4]
 	method, err := icaABI.MethodById(methodID)
 	if err != nil {
```

### x/cronos/keeper/precompiles/relayer.go
```diff
@@ -51,6 +51,7 @@ const (
 	RegisterCounterpartyPayee       = "registerCounterpartyPayee"
 	GasWhenReceiverChainIsSource    = 51705
 	GasWhenReceiverChainIsNotSource = 144025
+	DefaultGasRequired              = 100000
 )
 
 func init() {
@@ -96,7 +97,7 @@ func init() {
 		case RegisterCounterpartyPayee:
 			relayerGasRequiredByMethod[methodID] = 37000
 		default:
-			relayerGasRequiredByMethod[methodID] = 100000
+			relayerGasRequiredByMethod[methodID] = DefaultGasRequired
 		}
 		relayerMethodNamedByMethod[methodID] = methodName
 	}
@@ -132,44 +133,59 @@ func (bc *RelayerContract) Address() common.Address {
 // RequiredGas calculates the contract gas use
 // `max(0, len(input) * DefaultTxSizeCostPerByte + requiredGasTable[methodPrefix] - intrinsicGas)`
 func (bc *RelayerContract) RequiredGas(input []byte) (gas uint64) {
+	intrinsicGas, _ := core.IntrinsicGas(input, nil, nil, false, bc.isHomestead, bc.isIstanbul, bc.isShanghai)
 	// base cost to prevent large input size
 	inputLen := len(input)
 	baseCost := uint64(inputLen) * authtypes.DefaultTxSizeCostPerByte
 	var methodID [4]byte
+	if inputLen < 4 {
+		bc.logger.Error("invalid input length", "input", input)
+		return getRequiredGas(DefaultGasRequired, baseCost, intrinsicGas)
+	}
+	defer func() {
+		methodName := relayerMethodNamedByMethod[methodID]
+		bc.logger.Debug("required", "gas", gas, "method", methodName, "len", inputLen, "intrinsic", intrinsicGas)
+	}()
 	copy(methodID[:], input[:4])
-	requiredGas, ok := relayerGasRequiredByMethod[methodID]
+	gasRequiredByMethod, ok := relayerGasRequiredByMethod[methodID]
+	if !ok {
+		bc.logger.Error("unknown method", "method", methodID)
+		return getRequiredGas(DefaultGasRequired, baseCost, intrinsicGas)
+	}
+
 	method, err := irelayerABI.MethodById(methodID[:])
 	if err != nil {
-		panic(err)
+		bc.logger.Error("failed to get method by id", "error", err)
+		return getRequiredGas(gasRequiredByMethod, baseCost, intrinsicGas)
 	}
 	if method.Name == RecvPacket {
 		args, err := method.Inputs.Unpack(input[4:])
 		if err != nil {
-			panic(err)
+			bc.logger.Error("failed to unpack input arguments", "error", err)
+			return getRequiredGas(gasRequiredByMethod, baseCost, intrinsicGas)
 		}
 		i := args[0].([]byte)
 		var msg channeltypes.MsgRecvPacket
 		if err = bc.cdc.Unmarshal(i, &msg); err != nil {
-			panic(err)
+			bc.logger.Error("failed to unmarshal MsgRecvPacket", "error", err)
+			return getRequiredGas(gasRequiredByMethod, baseCost, intrinsicGas)
 		}
 		var data ibctransfertypes.FungibleTokenPacketData
 		if err = ibctransfertypes.ModuleCdc.UnmarshalJSON(msg.Packet.GetData(), &data); err != nil {
-			panic(err)
+			bc.logger.Error("failed to unmarshal FungibleTokenPacketData", "error", err)
+			return getRequiredGas(gasRequiredByMethod, baseCost, intrinsicGas)
 		}
 		denom := ibctransfertypes.ExtractDenomFromPath(data.Denom)
 		if denom.HasPrefix(msg.Packet.GetSourcePort(), msg.Packet.GetSourceChannel()) {
-			requiredGas = GasWhenReceiverChainIsSource
+			gasRequiredByMethod = GasWhenReceiverChainIsSource
 		}
 	}
-	intrinsicGas, _ := core.IntrinsicGas(input, nil, nil, false, bc.isHomestead, bc.isIstanbul, bc.isShanghai)
-	defer func() {
-		methodName := relayerMethodNamedByMethod[methodID]
-		bc.logger.Debug("required", "gas", gas, "method", methodName, "len", inputLen, "intrinsic", intrinsicGas)
-	}()
-	if !ok {
-		requiredGas = 0
-	}
-	total := requiredGas + baseCost
+
+	return getRequiredGas(gasRequiredByMethod, baseCost, intrinsicGas)
+}
+
+func getRequiredGas(gasRequiredByMethod, baseCost, intrinsicGas uint64) uint64 {
+	total := gasRequiredByMethod + baseCost
 	if total < intrinsicGas {
 		return 0
 	}
```
