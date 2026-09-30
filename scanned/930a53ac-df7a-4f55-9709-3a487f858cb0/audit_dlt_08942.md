# [?] fix(tss): nil pointer dereference at tss query signature when the signature does not exist yet (#774)

## Summary
Severity: Unknown
Chain: Axelar
Component: axelarnetwork/axelar-core
Published: 2021-09-02
Source: https://github.com/axelarnetwork/axelar-core/commit/da77bbff05549f44037ddc481c7776aed312c2a6
Type: security-commit

## Details
fix(tss): nil pointer dereference at tss query signature when the signature does not exist yet (#774)

## Patch
### docs/proto/proto-docs.md
```diff
@@ -232,8 +232,8 @@
     - [QueryKeyShareResponse](#tss.v1beta1.QueryKeyShareResponse)
     - [QueryKeyShareResponse.ShareInfo](#tss.v1beta1.QueryKeyShareResponse.ShareInfo)
     - [QueryRecoveryResponse](#tss.v1beta1.QueryRecoveryResponse)
-    - [QuerySigResponse](#tss.v1beta1.QuerySigResponse)
-    - [Signature](#tss.v1beta1.Signature)
+    - [QuerySignatureResponse](#tss.v1beta1.QuerySignatureResponse)
+    - [QuerySignatureResponse.Signature](#tss.v1beta1.QuerySignatureResponse.Signature)
   
     - [VoteStatus](#tss.v1beta1.VoteStatus)
   
@@ -3277,32 +3277,32 @@ Params is the parameter set for this module
 
 
 
-<a name="tss.v1beta1.QuerySigResponse"></a>
+<a name="tss.v1beta1.QuerySignatureResponse"></a>
 
-### QuerySigResponse
+### QuerySignatureResponse
 
 
 
 | Field | Type | Label | Description |
 | ----- | ---- | ----- | ----------- |
 | `vote_status` | [VoteStatus](#tss.v1beta1.VoteStatus) |  |  |
-| `signature` | [Signature](#tss.v1beta1.Signature) |  |  |
+| `signature` | [QuerySignatureResponse.Signature](#tss.v1beta1.QuerySignatureResponse.Signature) |  |  |
 
 
 
 
 
 
-<a name="tss.v1beta1.Signature"></a>
+<a name="tss.v1beta1.QuerySignatureResponse.Signature"></a>
 
-### Signature
+### QuerySignatureResponse.Signature
 
 
 
 | Field | Type | Label | Description |
 | ----- | ---- | ----- | ----------- |
-| `r` | [bytes](#bytes) |  |  |
-| `s` | [bytes](#bytes) |  |  |
+| `r` | [string](#string) |  |  |
+| `s` | [string](#string) |  |  |
 
 
 
@@ -3319,8 +3319,9 @@ Params is the parameter set for this module
 | Name | Number | Description |
 | ---- | ------ | ----------- |
 | VOTE_STATUS_UNSPECIFIED | 0 |  |
-| VOTE_STATUS_PENDING | 1 |  |
-| VOTE_STATUS_DECIDED | 2 |  |
+| VOTE_STATUS_NOT_FOUND | 1 |  |
+| VOTE_STATUS_PENDING | 2 |  |
+| VOTE_STATUS_DECIDED | 3 |  |
 
 
  <!-- end enums -->
```

### proto/tss/v1beta1/query.proto
```diff
@@ -8,29 +8,30 @@ import "tss/exported/v1beta1/types.proto";
 
 option (gogoproto.goproto_getters_all) = false;
 
-message QuerySigResponse {
+message QuerySignatureResponse {
+  message Signature {
+    string r = 1;
+    string s = 2;
+  }
+
   VoteStatus vote_status = 1;
   Signature signature = 2;
 }
 
-message Signature {
-  bytes r = 2;
-  bytes s = 3;
-}
-
 message QueryKeyResponse {
   VoteStatus vote_status = 1;
   tss.exported.v1beta1.KeyRole role = 2;
 }
 
 enum VoteStatus {
-  option (gogoproto.goproto_enum_prefix) = true;
+  option (gogoproto.goproto_enum_prefix) = false;
   option (gogoproto.goproto_enum_stringer) = true;
 
   VOTE_STATUS_UNSPECIFIED = 0
       [ (gogoproto.enumvalue_customname) = "Unspecified" ];
-  VOTE_STATUS_PENDING = 1 [ (gogoproto.enumvalue_customname) = "Pending" ];
-  VOTE_STATUS_DECIDED = 2 [ (gogoproto.enumvalue_customname) = "Decided" ];
+  VOTE_STATUS_NOT_FOUND = 1 [ (gogoproto.enumvalue_customname) = "NotFound" ];
+  VOTE_STATUS_PENDING = 2 [ (gogoproto.enumvalue_customname) = "Pending" ];
+  VOTE_STATUS_DECIDED = 3 [ (gogoproto.enumvalue_customname) = "Decided" ];
 }
 
 message QueryRecoveryResponse {
```

### x/tss/client/cli/query.go
```diff
@@ -53,19 +53,17 @@ func GetCmdGetSig(queryRoute string) *cobra.Command {
 			}
 
 			sigID := args[0]
-			res, _, err := cliCtx.QueryWithData(fmt.Sprintf("custom/%s/%s/%s", queryRoute, keeper.QuerySigStatus, sigID), nil)
+			bz, _, err := cliCtx.Query(fmt.Sprintf("custom/%s/%s/%s", queryRoute, keeper.QuerySignature, sigID))
 			if err != nil {
 				return sdkerrors.Wrapf(err, "failed to get signature")
 			}
 
-			var sigResponse types.QuerySigResponse
-			err = sigResponse.Unmarshal(res)
-			if err != nil {
+			var res types.QuerySignatureResponse
+			if err := types.ModuleCdc.UnmarshalBinaryLengthPrefixed(bz, &res); err != nil {
 				return sdkerrors.Wrapf(err, "failed to get signature")
 			}
 
-			hexSig := types.NewHexSignatureFromQuerySigResponse(&sigResponse)
-			return cliCtx.PrintObjectLegacy(hexSig)
+			return cliCtx.PrintProto(&res)
 		},
 	}
 
@@ -86,18 +84,17 @@ func GetCmdGetKey(queryRoute string) *cobra.Command {
 			}
 
 			keyID := args[0]
-			res, _, err := cliCtx.QueryWithData(fmt.Sprintf("custom/%s/%s/%s", queryRoute, keeper.QueryKeyStatus, keyID), nil)
+			bz, _, err := cliCtx.Query(fmt.Sprintf("custom/%s/%s/%s", queryRoute, keeper.QueryKey, keyID))
 			if err != nil {
 				return sdkerrors.Wrapf(err, "failed to get key")
 			}
 
-			var keyResponse types.QueryKeyResponse
-			err = keyResponse.Unmarshal(res)
-			if err != nil {
+			var res types.QueryKeyResponse
+			if err := types.ModuleCdc.UnmarshalBinaryLengthPrefixed(bz, &res); err != nil {
 				return sdkerrors.Wrapf(err, "failed to get key")
 			}
 
-			return cliCtx.PrintObjectLegacy(keyResponse)
+			return cliCtx.PrintProto(&res)
 		},
 	}
 
```

### x/tss/client/rest/query.go
```diff
@@ -35,20 +35,19 @@ func QueryHandlerSigStatus(cliCtx client.Context) http.HandlerFunc {
 		}
 
 		sigID := mux.Vars(r)[utils.PathVarSigID]
-		res, _, err := cliCtx.QueryWithData(fmt.Sprintf("custom/%s/%s/%s", types.QuerierRoute, keeper.QuerySigStatus, sigID), nil)
+		bz, _, err := cliCtx.Query(fmt.Sprintf("custom/%s/%s/%s", types.QuerierRoute, keeper.QuerySignature, sigID))
 		if err != nil {
 			rest.WriteErrorResponse(w, http.StatusBadRequest, err.Error())
 			return
 		}
 
-		var sigResponse types.QuerySigResponse
-		err = sigResponse.Unmarshal(res)
-		if err != nil {
+		var res types.QuerySignatureResponse
+		if err := types.ModuleCdc.UnmarshalBinaryLengthPrefixed(bz, &res); err != nil {
 			rest.WriteErrorResponse(w, http.StatusBadRequest, sdkerrors.Wrapf(err, "failed to get sig status").Error())
 			return
 		}
 
-		rest.PostProcessResponse(w, cliCtx, sigResponse)
+		rest.PostProcessResponse(w, cliCtx, res)
 	}
 }
 
@@ -62,20 +61,19 @@ func QueryHandlerKeyStatus(cliCtx client.Context) http.HandlerFunc {
 		}
 
 		keyID := mux.Vars(r)[utils.PathVarKeyID]
-		res, _, err := cliCtx.QueryWithData(fmt.Sprintf("custom/%s/%s/%s", types.QuerierRoute, keeper.QueryKeyStatus, keyID), nil)
+		bz, _, err := cliCtx.Query(fmt.Sprintf("custom/%s/%s/%s", types.QuerierRoute, keeper.QueryKey, keyID))
 		if err != nil {
 			rest.WriteErrorResponse(w, http.StatusBadRequest, err.Error())
 			return
 		}
 
-		var keyResponse types.QueryKeyResponse
-		err = keyResponse.Unmarshal(res)
-		if err != nil {
+		var res types.QueryKeyResponse
+		if err := types.ModuleCdc.UnmarshalBinaryLengthPrefixed(bz, &res); err != nil {
 			rest.WriteErrorResponse(w, http.StatusBadRequest, sdkerrors.Wrapf(err, "failed to get key status").Error())
 			return
 		}
 
-		rest.PostProcessResponse(w, cliCtx, keyResponse)
+		rest.PostProcessResponse(w, cliCtx, res)
 	}
 }
 
```

### x/tss/client/rest/tx.go
```diff
@@ -21,8 +21,8 @@ const (
 	TxKeygenStart     = "start"
 	TxMasterKeyRotate = "rotate"
 
-	QuerySigStatus            = keeper.QuerySigStatus
-	QueryKeyStatus            = keeper.QueryKeyStatus
+	QuerySignature            = keeper.QuerySignature
+	QueryKey                  = keeper.QueryKey
 	QueryRecovery             = keeper.QueryRecovery
 	QueryKeyID                = keeper.QueryKeyID
 	QueryKeySharesByKeyID     = keeper.QueryKeySharesByKeyID
@@ -52,8 +52,8 @@ func RegisterRoutes(cliCtx client.Context, r *mux.Router) {
 	registerTx(GetHandlerKeyRotate(cliCtx), TxMasterKeyRotate, clientUtils.PathVarChain)
 
 	registerQuery := clientUtils.RegisterQueryHandlerFn(r, types.RestRoute)
-	registerQuery(QueryHandlerSigStatus(cliCtx), QuerySigStatus, clientUtils.PathVarSigID)
-	registerQuery(QueryHandlerKeyStatus(cliCtx), QueryKeyStatus, clientUtils.PathVarKeyID)
+	registerQuery(QueryHandlerSigStatus(cliCtx), QuerySignature, clientUtils.PathVarSigID)
+	registerQuery(QueryHandlerKeyStatus(cliCtx), QueryKey, clientUtils.PathVarKeyID)
 	registerQuery(QueryHandlerRecovery(cliCtx), QueryRecovery)
 	registerQuery(QueryHandlerKeyID(cliCtx), QueryKeyID, clientUtils.PathVarChain, clientUtils.PathVarKeyRole)
 	registerQuery(QueryHandlerKeySharesByKeyID(cliCtx), QueryKeySharesByKeyID, clientUtils.PathVarKeyID)
```

### x/tss/keeper/querier.go
```diff
@@ -1,24 +1,23 @@
 package keeper
 
 import (
+	"encoding/hex"
 	"fmt"
 
 	sdk "github.com/cosmos/cosmos-sdk/types"
-	stakingtypes "github.com/cosmos/cosmos-sdk/x/staking/types"
 	sdkerrors "github.com/cosmos/cosmos-sdk/types/errors"
+	stakingtypes "github.com/cosmos/cosmos-sdk/x/staking/types"
 	abci "github.com/tendermint/tendermint/abci/types"
 
 	"github.com/axelarnetwork/axelar-core/x/tss/exported"
+	"github.com/axelarnetwork/axelar-core/x/tss/types"
 	voting "github.com/axelarnetwork/axelar-core/x/vote/exported"
-	tssTypes "github.com/axelarnetwork/axelar-core/x/tss/types"
-
-	"github.com/axelarnetwork/axelar-core/x/bitcoin/types"
 )
 
 // Query paths
 const (
-	QuerySigStatus            = "sig-status"
-	QueryKeyStatus            = "key-status"
+	QuerySignature            = "signature"
+	QueryKey                  = "key"
 	QueryRecovery             = "recovery"
 	QueryKeyID                = "key-id"
 	QueryKeySharesByKeyID     = "key-share-id"
@@ -27,15 +26,15 @@ const (
 )
 
 // NewQuerier returns a new querier for the TSS module
-func NewQuerier(k tssTypes.TSSKeeper, v tssTypes.Voter, s tssTypes.Snapshotter, staking tssTypes.StakingKeeper, n tssTypes.Nexus) sdk.Querier {
+func NewQuerier(k types.TSSKeeper, v types.Voter, s types.Snapshotter, staking types.StakingKeeper, n types.Nexus) sdk.Querier {
 	return func(ctx sdk.Context, path []string, req abci.RequestQuery) ([]byte, error) {
 		var res []byte
 		var err error
 		switch path[0] {
-		case QuerySigStatus:
-			res, err = querySigStatus(ctx, k, v, path[1])
-		case QueryKeyStatus:
-			res, err = queryKeygenStatus(ctx, k, v, path[1])
+		case QuerySignature:
+			res, err = querySignatureStatus(ctx, k, v, path[1])
+		case QueryKey:
+			res, err = queryKey(ctx, k, v, path[1])
 		case QueryRecovery:
 			res, err = queryRecovery(ctx, k, s, path[1])
 		case QueryKeyID:
@@ -51,13 +50,13 @@ func NewQuerier(k tssTypes.TSSKeeper, v tssTypes.Voter, s tssTypes.Snapshotter,
 		}
 
 		if err != nil {
-			return nil, sdkerrors.Wrap(types.ErrBitcoin, err.Error())
+			return nil, sdkerrors.Wrap(types.ErrTss, err.Error())
 		}
 		return res, nil
 	}
 }
 
-func queryRecovery(ctx sdk.Context, k tssTypes.TSSKeeper, s tssTypes.Snapshotter, keyID string) ([]byte, error) {
+func queryRecovery(ctx sdk.Context, k types.TSSKeeper, s types.Snapshotter, keyID string) ([]byte, error) {
 	counter, ok := k.GetSnapshotCounterForKeyID(ctx, keyID)
 	if !ok {
 		return nil, fmt.Errorf("could not obtain snapshot counter for key ID %s", keyID)
@@ -77,7 +76,7 @@ func queryRecovery(ctx sdk.Context, k tssTypes.TSSKeeper, s tssTypes.Snapshotter
 
 	infos := k.GetAllRecoveryInfos(ctx, keyID)
 
-	resp := tssTypes.QueryRecoveryResponse{
+	resp := types.QueryRecoveryResponse{
 		Threshold:          int32(snapshot.CorruptionThreshold),
 		PartyUids:          participants,
 		PartyShareCounts:   participantShareCounts,
@@ -87,62 +86,57 @@ func queryRecovery(ctx sdk.Context, k tssTypes.TSSKeeper, s tssTypes.Snapshotter
 	return resp.Marshal()
 }
 
-func querySigStatus(ctx sdk.Context, k tssTypes.TSSKeeper, v tssTypes.Voter, sigID string) ([]byte, error) {
-	var resp tssTypes.QuerySigResponse
+func querySignatureStatus(ctx sdk.Context, k types.TSSKeeper, v types.Voter, sigID string) ([]byte, error) {
 	if sig, status := k.GetSig(ctx, sigID); status == exported.SigStatus_Signed {
 		// poll was successful
-		resp := tssTypes.QuerySigResponse{
-			VoteStatus: tssTypes.VoteStatus_Decided,
-			Signature: &tssTypes.Signature{
-				R: sig.R.Bytes(),
-				S: sig.S.Bytes(),
+		res := types.QuerySignatureResponse{
+			VoteStatus: types.Decided,
+			Signature: &types.QuerySignatureResponse_Signature{
+				R: hex.EncodeToString(sig.R.Bytes()),
+				S: hex.EncodeToString(sig.S.Bytes()),
 			},
 		}
-		return resp.Marshal()
+
+		return types.ModuleCdc.MarshalBinaryLengthPrefixed(&res)
 	}
 
-	pollMeta := voting.NewPollKey(tssTypes.ModuleName, sigID)
-	poll := v.GetPoll(ctx, pollMeta)
+	var res types.QuerySignatureResponse
+	pollMeta := voting.NewPollKey(types.ModuleName, sigID)
 
-	if poll == nil {
-		// poll either never existed or has been closed
-		resp.VoteStatus = tssTypes.VoteStatus_Unspecified
+	if poll := v.GetPoll(ctx, pollMeta); poll.Is(voting.NonExistent) {
+		res.VoteStatus = types.NotFound
 	} else {
-		// poll still open, pending a decision
-		resp.VoteStatus = tssTypes.VoteStatus_Pending
+		res.VoteStatus = types.Pending
 	}
 
-	return resp.Marshal()
+	return types.ModuleCdc.MarshalBinaryLengthPrefixed(&res)
 }
 
-func queryKeygenStatus(ctx sdk.Context, k tssTypes.TSSKeeper, v tssTypes.Voter, keyID string) ([]byte, error) {
-	var resp tssTypes.QueryKeyResponse
-
+func queryKey(ctx sdk.Context, k types.TSSKeeper, v types.Voter, keyID string) ([]byte, error) {
 	if key, ok := k.GetKey(ctx, keyID); ok {
 		// poll was successful
-		resp = tssTypes.QueryKeyResponse{
-			VoteStatus: tssTypes.VoteStatus_Decided,
+		res := types.QueryKeyResponse{
+			VoteStatus: types.Decided,
 			Role:       key.Role,
 		}
 
-		return resp.Marshal()
+		return types.ModuleCdc.MarshalBinaryLengthPrefixed(&res)
 	}
 
-	pollMeta := voting.NewPollKey(tssTypes.ModuleName, keyID)
-	poll := v.GetPoll(ctx, pollMeta)
-	if poll == nil {
-		// poll either never existed or has been closed
-		resp.VoteStatus = tssTypes.VoteStatus_Unspecified
+	var res types.QueryKeyResponse
+	pollMeta := voting.NewPollKey(types.ModuleName, keyID)
+
+	if poll := v.GetPoll(ctx, pollMeta); poll.Is(voting.NonExistent) {
+		res.VoteStatus = types.NotFound
 	} else {
-		// poll still open, pending a decision
-		resp.VoteStatus = tssTypes.VoteStatus_Pending
+		res.VoteStatus = types.Pending
 	}
 
-	return resp.Marshal()
+	return types.ModuleCdc.MarshalBinaryLengthPrefixed(&res)
 }
 
 // queryKeyID returns the keyID of the most recent key for a provided keyChain and keyRole
-func queryKeyID(ctx sdk.Context, k tssTypes.TSSKeeper, n tssTypes.Nexus, keyChainStr string, keyRoleStr string) ([]byte, error) {
+func queryKeyID(ctx sdk.Context, k types.TSSKeeper, n types.Nexus, keyChainStr string, keyRoleStr string) ([]byte, error) {
 	keyChain, ok := n.GetChain(ctx, keyChainStr)
 	if !ok {
 		return nil, fmt.Errorf("%s is not a registered chain", keyChainStr)
@@ -165,7 +159,7 @@ func queryKeyID(ctx sdk.Context, k tssTypes.TSSKeeper, n tssTypes.Nexus, keyChai
 	return []byte(keyID), nil
 }
 
-func queryKeySharesByKeyID(ctx sdk.Context, k tssTypes.TSSKeeper, s tssTypes.Snapshotter, keyID string) ([]byte, error) {
+func queryKeySharesByKeyID(ctx sdk.Context, k types.TSSKeeper, s types.Snapshotter, keyID string) ([]byte, error) {
 
 	counter, ok := k.GetSnapshotCounterForKeyID(ctx, keyID)
 	if !ok {
@@ -177,10 +171,10 @@ func queryKeySharesByKeyID(ctx sdk.Context, k tssTypes.TSSKeeper, s tssTypes.Sna
 		return nil, fmt.Errorf("no snapshot found for counter number %d", counter)
 	}
 
-	var allShareInfos []tssTypes.QueryKeyShareResponse_ShareInfo
+	var allShareInfos []types.QueryKeyShareResponse_ShareInfo
 	for _, validator := range snapshot.Validators {
 
-		thisShareInfo := tssTypes.QueryKeyShareResponse_ShareInfo{
+		thisShareInfo := types.QueryKeyShareResponse_ShareInfo{
 			KeyID:               keyID,
 			SnapshotBlockNumber: snapshot.Height,
 			ValidatorAddress:    validator.GetSDKValidator().GetOperator().String(),
@@ -191,16 +185,16 @@ func queryKeySharesByKeyID(ctx sdk.Context, k tssTypes.TSSKeeper, s tssTypes.Sna
 		allShareInfos = append(allShareInfos, thisShareInfo)
 	}
 
-	keyShareInfos := tssTypes.QueryKeyShareResponse{
+	keyShareInfos := types.QueryKeyShareResponse{
 		ShareInfos: allShareInfos,
 	}
 
 	return keyShareInfos.Marshal()
 }
 
-func queryKeySharesByValidator(ctx sdk.Context, k tssTypes.TSSKeeper, n tssTypes.Nexus, s tssTypes.Snapshotter, targetValidatorAddr string) ([]byte, error) {
+func queryKeySharesByValidator(ctx sdk.Context, k types.TSSKeeper, n types.Nexus, s types.Snapshotter, targetValidatorAddr string) ([]byte, error) {
 
-	var allShareInfos []tssTypes.QueryKeyShareResponse_ShareInfo
+	var allShareInfos []types.QueryKeyShareResponse_ShareInfo
 
 	for _, chain := range n.GetChains(ctx) {
 		for _, keyRole := range exported.GetKeyRoles() {
@@ -226,7 +220,7 @@ func queryKeySharesByValidator(ctx sdk.Context, k tssTypes.TSSKeeper, n tssTypes
 				validatorAddr := validator.GetSDKValidator().GetOperator().String()
 				if validatorAddr == targetValidatorAddr {
 
-					thisShareInfo := tssTypes.QueryKeyShareResponse_ShareInfo{
+					thisShareInfo := types.QueryKeyShareResponse_ShareInfo{
 						KeyID:               keyID,
 						KeyChain:            chain.Name,
 						KeyRole:             keyRole.String(),
@@ -242,14 +236,14 @@ func queryKeySharesByValidator(ctx sdk.Context, k tssTypes.TSSKeeper, n tssTypes
 		}
 	}
 
-	keyShareInfos := tssTypes.QueryKeyShareResponse{
+	keyShareInfos := types.QueryKeyShareResponse{
 		ShareInfos: allShareInfos,
 	}
 
 	return keyShareInfos.Marshal()
 }
 
-func queryDeactivatedOperator(ctx sdk.Context, k tssTypes.TSSKeeper, s tssTypes.Snapshotter, staking tssTypes.StakingKeeper) ([]byte, error) {
+func queryDeactivatedOperator(ctx sdk.Context, k types.TSSKeeper, s types.Snapshotter, staking types.StakingKeeper) ([]byte, error) {
 
 	var deactivatedValidators []string
 	validatorIter := func(_ int64, validator stakingtypes.ValidatorI) (stop bool) {
@@ -272,7 +266,7 @@ func queryDeactivatedOperator(ctx sdk.Context, k tssTypes.TSSKeeper, s tssTypes.
 	// IterateBondedValidatorsByPower(https://github.com/cosmos/cosmos-sdk/blob/7fc7b3f6ff82eb5ede52881778114f6b38bd7dfa/x/staking/keeper/alias_functions.go#L33) iterates validators by power in descending order
 	staking.IterateBondedValidatorsByPower(ctx, validatorIter)
 
-	resp := tssTypes.QueryDeactivatedOperatorsResponse{
+	resp := types.QueryDeactivatedOperatorsResponse{
 		OperatorAddresses: deactivatedValidators,
 	}
 
```

### x/tss/types/query.pb.go
```diff
@@ -27,21 +27,24 @@ const _ = proto.GoGoProtoPackageIsVersion3 // please upgrade the proto package
 type VoteStatus int32
 
 const (
-	VoteStatus_Unspecified VoteStatus = 0
-	VoteStatus_Pending     VoteStatus = 1
-	VoteStatus_Decided     VoteStatus = 2
+	Unspecified VoteStatus = 0
+	NotFound    VoteStatus = 1
+	Pending     VoteStatus = 2
+	Decided     VoteStatus = 3
 )
 
 var VoteStatus_name = map[int32]string{
 	0: "VOTE_STATUS_UNSPECIFIED",
-	1: "VOTE_STATUS_PENDING",
-	2: "VOTE_STATUS_DECIDED",
+	1: "VOTE_STATUS_NOT_FOUND",
+	2: "VOTE_STATUS_PENDING",
+	3: "VOTE_STATUS_DECIDED",
 }
 
 var VoteStatus_value = map[string]int32{
 	"VOTE_STATUS_UNSPECIFIED": 0,
-	"VOTE_STATUS_PENDING":     1,
-	"VOTE_STATUS_DECIDED":     2,
+	"VOTE_STATUS_NOT_FOUND":   1,
+	"VOTE_STATUS_PENDING":     2,
+	"VOTE_STATUS_DECIDED":     3,
 }
 
 func (x VoteStatus) String() string {
@@ -52,23 +55,23 @@ func (VoteStatus) EnumDescriptor() ([]byte, []int) {
 	return fileDescriptor_b9e98857940a4a89, []int{0}
 }
 
-type QuerySigResponse struct {
-	VoteStatus VoteStatus `protobuf:"varint,1,opt,name=vote_status,json=voteStatus,proto3,enum=tss.v1beta1.VoteStatus" json:"vote_status,omitempty"`
-	Signature  *Signature `protobuf:"bytes,2,opt,name=signature,proto3" json:"signature,omitempty"`
+type QuerySignatureResponse struct {
+	VoteStatus VoteStatus                        `protobuf:"varint,1,opt,name=vote_status,json=voteStatus,proto3,enum=tss.v1beta1.VoteStatus" json:"vote_status,omitempty"`
+	Signature  *QuerySignatureResponse_Signature `protobuf:"bytes,2,opt,name=signature,proto3" json:"signature,omitempty"`
 }
 
-func (m *QuerySigResponse) Reset()         { *m = QuerySigResponse{} }
-func (m *QuerySigResponse) String() string { return proto.CompactTextString(m) }
-func (*QuerySigResponse) ProtoMessage()    {}
-func (*QuerySigResponse) Descriptor() ([]byte, []int) {
+func (m *QuerySignatureResponse) Reset()         { *m = QuerySignatureResponse{} }
+func (m *QuerySignatureResponse) String() string { return proto.CompactTextString(m) }
+func (*QuerySignatureResponse) ProtoMessage()    {}
+func (*QuerySignatureResponse) Descriptor() ([]byte, []int) {
 	return fileDescriptor_b9e98857940a4a89, []int{0}
 }
-func (m *QuerySigResponse) XXX_Unmarshal(b []byte) error {
+func (m *QuerySignatureResponse) XXX_Unmarshal(b []byte) error {
 	return m.Unmarshal(b)
 }
-func (m *QuerySigResponse) XXX_Marshal(b []byte, deterministic bool) ([]byte, error) {
+func (m *QuerySignatureResponse) XXX_Marshal(b []byte, deterministic bool) ([]byte, error) {
 	if deterministic {
-		return xxx_messageInfo_QuerySigResponse.Marshal(b, m, deterministic)
+		return xxx_messageInfo_QuerySignatureResponse.Marshal(b, m, deterministic)
 	} else {
 		b = b[:cap(b)]
 		n, err := m.MarshalToSizedBuffer(b)
@@ -78,35 +81,35 @@ func (m *QuerySigResponse) XXX_Marshal(b []byte, deterministic bool) ([]byte, er
 		return b[:n], nil
 	}
 }
-func (m *QuerySigResponse) XXX_Merge(src proto.Message) {
-	xxx_messageInfo_QuerySigResponse.Merge(m, src)
+func (m *QuerySignatureResponse) XXX_Merge(src proto.Message) {
+	xxx_messageInfo_QuerySignatureResponse.Merge(m, src)
 }
-func (m *QuerySigResponse) XXX_Size() int {
+func (m *QuerySignatureResponse) XXX_Size() int {
 	return m.Size()
 }
-func (m *QuerySigResponse) XXX_DiscardUnknown() {
-	xxx_messageInfo_QuerySigResponse.DiscardUnknown(m)
+func (m *QuerySignatureResponse) XXX_DiscardUnknown() {
+	xxx_messageInfo_QuerySignatureResponse.DiscardUnknown(m)
 }
 
-var xxx_messageInfo_QuerySigResponse proto.InternalMessageInfo
+var xxx_messageInfo_QuerySignatureResponse proto.InternalMessageInfo
 
-type Signature struct {
-	R []byte `protobuf:"bytes,2,opt,name=r,proto3" json:"r,omitempty"`
-	S []byte `protobuf:"bytes,3,opt,name=s,proto3" json:"s,omitempty"`
+type QuerySignatureResponse_Signature struct {
+	R string `protobuf:"bytes,1,opt,name=r,proto3" json:"r,omitempty"`
+	S string `protobuf:"bytes,2,opt,name=s,proto3" json:"s,omitempty"`
 }
 
-func (m *Signature) Reset()         { *m = Signature{} }
-func (m *Signature) String() string { return proto.CompactTextString(m) }
-func (*Signature) ProtoMessage()    {}
-func (*Signature) Descriptor() ([]byte, []int) {
-	return fileDescriptor_b9e98857940a4a89, []int{1}
+func (m *QuerySignatureResponse_Signature) Reset()         { *m = QuerySignatureResponse_Signature{} }
+func (m *QuerySignatureResponse_Signature) String() string { return proto.CompactTextString(m) }
+func (*QuerySignatureResponse_Signature) ProtoMessage()    {}
+func (*QuerySignatureResponse_Signature) Descriptor() ([]byte, []int) {
+	return fileDescriptor_b9e98857940a4a89, []int{0, 0}
 }
-func (m *Signature) XXX_Unmarshal(b []byte) error {
+func (m *QuerySignatureResponse_Signature) XXX_Unmarshal(b []byte) error {
 	return m.Unmarshal(b)
 }
-func (m *Signature) XXX_Marshal(b []byte, deterministic bool) ([]byte, error) {
+func (m *QuerySignatureResponse_Signature) XXX_Marshal(b []byte, deterministic bool) ([]byte, error) {
 	if deterministic {
-		return xxx_messageInfo_Signature.Marshal(b, m, deterministic)
+		return xxx_messageInfo_QuerySignatureResponse_Signature.Marshal(b, m, deterministic)
 	} else {
 		b = b[:cap(b)]
 		n, err := m.MarshalToSizedBuffer(b)
@@ -116,17 +119,17 @@ func (m *Signature) XXX_Marshal(b []byte, deterministic bool) ([]byte, error) {
 		return b[:n], nil
 	}
 }
-func (m *Signature) XXX_Merge(src proto.Message) {
-	xxx_messageInfo_Signature.Merge(m, src)
+func (m *QuerySignatureResponse_Signature) XXX_Merge(src proto.Message) {
+	xxx_messageInfo_QuerySignatureResponse_Signature.Merge(m, src)
 }
-func (m *Signature) XXX_Size() int {
+func (m *QuerySignatureResponse_Signature) XXX_Size() int {
 	return m.Size()
 }
-func (m *Signature) XXX_DiscardUnknown() {
-	xxx_messageInfo_Signature.DiscardUnknown(m)
+func (m *QuerySignatureResponse_Signature) XXX_DiscardUnknown() {
+	xxx_messageInfo_QuerySignatureResponse_Signature.DiscardUnknown(m)
 }
 
-var xxx_messageInfo_Signature proto.InternalMessageInfo
+var xxx_messageInfo_QuerySignatureResponse_Signature proto.InternalMessageInfo
 
 type QueryKeyResponse struct {
 	VoteStatus VoteStatus       `protobuf:"varint,1,opt,name=vote_status,json=voteStatus,proto3,enum=tss.v1beta1.VoteStatus" json:"vote_status,omitempty"`
@@ -137,7 +140,7 @@ func (m *QueryKeyResponse) Reset()         { *m = QueryKeyResponse{} }
 func (m *QueryKeyResponse) String() string { return proto.CompactTextString(m) }
 func (*QueryKeyResponse) ProtoMessage()    {}
 func (*QueryKeyResponse) Descriptor() ([]byte, []int) {
-	return fileDescriptor_b9e98857940a4a89, []int{2}
+	return fileDescriptor_b9e98857940a4a89, []int{1}
 }
 func (m *QueryKeyResponse) XXX_Unmarshal(b []byte) error {
 	return m.Unmarshal(b)
@@ -177,7 +180,7 @@ func (m *QueryRecoveryResponse) Reset()         { *m = QueryRecoveryResponse{} }
 func (m *QueryRecoveryResponse) String() string { return proto.CompactTextString(m) }
 func (*QueryRecoveryResponse) ProtoMessage()    {}
 func (*QueryRecoveryResponse) Descriptor() ([]byte, []int) {
-	return fileDescriptor_b9e98857940a4a89, []int{3}
+	return fileDescriptor_b9e98857940a4a89, []int{2}
 }
 func (m *QueryRecoveryResponse) XXX_Unmarshal(b []byte) error {
 	return m.Unmarshal(b)
@@ -214,7 +217,7 @@ func (m *QueryKeyShareResponse) Reset()         { *m = QueryKeyShareResponse{} }
 func (m *QueryKeyShareResponse) String() string { return proto.CompactTextString(m) }
 func (*QueryKeyShareResponse) ProtoMessage()    {}
 func (*QueryKeyShareResponse) Descriptor() ([]byte, []int) {
-	return fileDescriptor_b9e98857940a4a89, []int{4}
+	return fileDescriptor_b9e98857940a4a89, []int{3}
 }
 func (m *QueryKeyShareResponse) XXX_Unmarshal(b []byte) error {
 	return m.Unmarshal(b)
@@ -257,7 +260,7 @@ func (m *QueryKeyShareResponse_ShareInfo) Reset()         { *m = QueryKeyShareRe
 func (m *QueryKeyShareResponse_ShareInfo) String() string { return proto.CompactTextString(m) }
 func (*QueryKeyShareResponse_ShareInfo) ProtoMessage()    {}
 func (*QueryKeyShareResponse_ShareInfo) Descriptor() ([]byte, []int) {
-	return fileDescriptor_b9e98857940a4a89, []int{4, 0}
+	return fileDescriptor_b9e98857940a4a89, []int{3, 0}
 }
 func (m *QueryKeyShareResponse_ShareInfo) XXX_Unmarshal(b []byte) error {
 	return m.Unmarshal(b)
@@ -294,7 +297,7 @@ func (m *QueryDeactivatedOperatorsResponse) Reset()         { *m = QueryDeactiva
 func (m *QueryDeactivatedOperatorsResponse) String() string { return proto.CompactTextString(m) }
 func (*QueryDeactivatedOperatorsResponse) ProtoMessage()    {}
 func (*QueryDeactivatedOperatorsResponse) Descriptor() ([]byte, []int) {
-	return fileDescriptor_b9e98857940a4a89, []int{5}
+	return fileDescriptor_b9e98857940a4a89, []int{4}
 }
 func (m *QueryDeactivatedOperatorsResponse) XXX_Unmarshal(b []byte) error {
 	return m.Unmarshal(b)
@@ -325,8 +328,8 @@ var xxx_messageInfo_QueryDeactivatedOperatorsResponse proto.InternalMessageInfo
 
 func init() {
 	proto.RegisterEnum("tss.v1beta1.VoteStatus", VoteStatus_name, VoteStatus_value)
-	proto.RegisterType((*QuerySigResponse)(nil), "tss.v1beta1.QuerySigResponse")
-	proto.RegisterType((*Signature)(nil), "tss.v1beta1.Signature")
+	proto.RegisterType((*QuerySignatureResponse)(nil), "tss.v1beta1.QuerySignatureResponse")
+	proto.RegisterType((*QuerySignatureResponse_Signature)(nil), "tss.v1beta1.QuerySignatureResponse.Signature")
 	proto.RegisterType((*QueryKeyResponse)(nil), "tss.v1beta1.QueryKeyResponse")
 	proto.RegisterType((*QueryRecoveryResponse)(nil), "tss.v1beta1.QueryRecoveryResponse")
 	proto.RegisterType((*QueryKeyShareResponse)(nil), "tss.v1beta1.QueryKeyShareResponse")
@@ -337,59 +340,61 @@ func init() {
 func init() { proto.RegisterFile("tss/v1beta1/query.proto", fileDescriptor_b9e98857940a4a89) }
 
 var fileDescriptor_b9e98857940a4a89 = []byte{
-	// 772 bytes of a gzipped FileDescriptorProto
-	0x1f, 0x8b, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02, 0xff, 0xac, 0x54, 0x4f, 0x6f, 0xe3, 0x44,
-	0x1c, 0x8d, 0xf3, 0xa7, 0x5d, 0x4f, 0x4a, 0xc9, 0xce, 0xee, 0x52, 0x13, 0x58, 0xaf, 0x89, 0x90,
-	0x88, 0xa0, 0x9b, 0x6c, 0x03, 0x07, 0xae, 0x4d, 0x1c, 0x50, 0x54, 0x29, 0x5b, 0xec, 0xa4, 0x07,
-	0x2e, 0x96, 0x63, 0xff, 0x9a, 0x58, 0x49, 0x3c, 0x66, 0x66, 0x1c, 0xea, 0x13, 0x12, 0x27, 0xd4,
-	0x53, 0xf9, 0x00, 0xbd, 0x00, 0x07, 0x3e, 0x00, 0x1f, 0xa2, 0xc7, 0x1e, 0x39, 0x55, 0x90, 0x7e,
-	0x11, 0x34, 0xe3, 0xd8, 0x69, 0x11, 0x47, 0x4e, 0x9e, 0xdf, 0x7b, 0xef, 0xf7, 0xe6, 0xcd, 0xfc,
-	0xac, 0x41, 0x07, 0x9c, 0xb1, 0xf6, 0xea, 0x68, 0x02, 0xdc, 0x3d, 0x6a, 0x7f, 0x17, 0x03, 0x4d,
-	0x5a, 0x11, 0x25, 0x9c, 0xe0, 0x2a, 0x67, 0xac, 0xb5, 0x21, 0xea, 0xcf, 0xa7, 0x64, 0x4a, 0x24,
-	0xde, 0x16, 0xab, 0x54, 0x52, 0x37, 0x44, 0x2f, 0x5c, 0x44, 0x84, 0x72, 0xf0, 0x73, 0x13, 0x9e,
-	0x44, 0xc0, 0x52, 0x45, 0xe3, 0x47, 0x05, 0xd5, 0xbe, 0x11, 0xa6, 0x76, 0x30, 0xb5, 0x80, 0x45,
-	0x24, 0x64, 0x80, 0xbf, 0x44, 0xd5, 0x15, 0xe1, 0xe0, 0x30, 0xee, 0xf2, 0x98, 0x69, 0x8a, 0xa1,
-	0x34, 0xf7, 0x3b, 0x07, 0xad, 0x07, 0xfb, 0xb5, 0xce, 0x08, 0x07, 0x5b, 0xd2, 0x16, 0x5a, 0xe5,
-	0x6b, 0xfc, 0x05, 0x52, 0x59, 0x30, 0x0d, 0x5d, 0x1e, 0x53, 0xd0, 0x8a, 0x86, 0xd2, 0xac, 0x76,
-	0xde, 0x7b, 0xd4, 0x67, 0x67, 0xac, 0xb5, 0x15, 0x36, 0x3e, 0x41, 0x6a, 0x8e, 0xe3, 0x3d, 0xa4,
-	0x50, 0xd9, 0xba, 0x67, 0x29, 0x54, 0x54, 0x4c, 0x2b, 0xa5, 0x15, 0x6b, 0xfc, 0xb0, 0x09, 0x7b,
-	0x02, 0xc9, 0xff, 0x10, 0xf6, 0x08, 0x95, 0x29, 0x59, 0xa4, 0x39, 0xf7, 0x3b, 0x2f, 0x65, 0x4b,
-	0x76, 0x59, 0x79, 0xaf, 0xd8, 0x8a, 0x2c, 0xc0, 0x92, 0xd2, 0xc6, 0x1f, 0x0a, 0x7a, 0x21, 0x13,
-	0x58, 0xe0, 0x91, 0x95, 0xfc, 0x6e, 0x62, 0xbc, 0x44, 0x28, 0x72, 0x29, 0x4f, 0x9c, 0x38, 0xf0,
-	0x45, 0x8a, 0x52, 0x53, 0xb5, 0x54, 0x89, 0x8c, 0x03, 0x9f, 0xe1, 0x43, 0x84, 0x53, 0x9a, 0xcd,
-	0x5c, 0x0a, 0x8e, 0x47, 0xe2, 0x90, 0x33, 0xad, 0x68, 0x94, 0x9a, 0xef, 0x58, 0x35, 0xc9, 0xd8,
-	0x82, 0xe8, 0x49, 0x1c, 0x7f, 0x88, 0x54, 0x3e, 0xa3, 0xc0, 0x66, 0x64, 0xe1, 0xcb, 0xd3, 0x57,
-	0xac, 0x2d, 0x80, 0xdf, 0xa0, 0xe7, 0xa9, 0x0b, 0xdd, 0x84, 0x70, 0x82, 0xf0, 0x9c, 0x30, 0xad,
-	0x6c, 0x94, 0x9a, 0x7b, 0x16, 0x96, 0x5c, 0x96, 0x6f, 0x20, 0x98, 0xc6, 0xcf, 0xa5, 0x4d, 0xec,
-	0x13, 0x48, 0xf7, 0xc9, 0x63, 0xdb, 0xa8, 0x9a, 0x7a, 0xa5, 0x16, 0x22, 0x77, 0xb5, 0x73, 0xf8,
-	0xe8, 0xf6, 0xfe, 0xb3, 0xb1, 0x25, 0x2b, 0xe1, 0xde, 0x2d, 0xdf, 0xdc, 0xbd, 0x2a, 0x58, 0x88,
-	0x65, 0x00, 0xab, 0xff, 0x52, 0x44, 0x6a, 0xce, 0x63, 0x03, 0xed, 0xcc, 0x21, 0x71, 0x02, 0x5f,
-	0xce, 0x46, 0xed, 0xaa, 0xeb, 0xbb, 0x57, 0x95, 0x13, 0x48, 0x06, 0xa6, 0x55, 0x99, 0x43, 0x32,
-	0xf0, 0xf1, 0x07, 0x48, 0x15, 0x0a, 0x6f, 0xe6, 0x06, 0xa1, 0x9c, 0x86, 0x6a, 0x3d, 0x99, 0x43,
-	0xd2, 0x13, 0x35, 0x7e, 0x1f, 0x89, 0xb5, 0x23, 0x27, 0x55, 0x92, 0xdc, 0xee, 0x3c, 0x9d, 0x09,
-	0xee, 0xa0, 0x17, 0x2c, 0x74, 0x23, 0x36, 0x23, 0xdc, 0x99, 0x2c, 0x88, 0x37, 0x77, 0xc2, 0x78,
-	0x39, 0x01, 0xaa, 0x95, 0x0d, 0xa5, 0x59, 0xb2, 0x9e, 0x65, 0x64, 0x57, 0x70, 0x43, 0x49, 0xe1,
-	0xcf, 0xd0, 0xd3, 0x95, 0xbb, 0x08, 0x7c, 0x97, 0x13, 0xea, 0xb8, 0xbe, 0x4f, 0x81, 0x31, 0xad,
-	0x22, 0x7d, 0x6b, 0x39, 0x71, 0x9c, 0xe2, 0xe2, 0xa6, 0xc3, 0x78, 0xe9, 0x6c, 0x1b, 0xe4, 0x21,
-	0x99, 0xb6, 0x23, 0xfd, 0x71, 0x18, 0x2f, 0xcf, 0x32, 0x4a, 0x9e, 0x97, 0xe1, 0x26, 0xaa, 0x89,
-	0x0e, 0x4e, 0xb8, 0xbb, 0xc8, 0xd4, 0xbb, 0x52, 0xbd, 0x1f, 0xc6, 0xcb, 0x91, 0x80, 0x53, 0x65,
-	0xc3, 0x42, 0x1f, 0xc9, 0x9b, 0x35, 0xc1, 0xf5, 0x78, 0xb0, 0x72, 0x39, 0xf8, 0x6f, 0x23, 0xa0,
-	0xc2, 0x8b, 0xe5, 0xe3, 0x79, 0x8d, 0x30, 0xd9, 0x80, 0x59, 0x58, 0xc8, 0xfe, 0xae, 0xa7, 0x19,
-	0x73, 0x9c, 0x11, 0x9f, 0x5e, 0x29, 0x08, 0x6d, 0x7f, 0x76, 0x7c, 0x88, 0x0e, 0xce, 0xde, 0x8e,
-	0xfa, 0x8e, 0x3d, 0x3a, 0x1e, 0x8d, 0x6d, 0x67, 0x3c, 0xb4, 0x4f, 0xfb, 0xbd, 0xc1, 0x57, 0x83,
-	0xbe, 0x59, 0x2b, 0xd4, 0xdf, 0xbd, 0xbc, 0x36, 0xaa, 0xe3, 0x90, 0x45, 0xe0, 0x05, 0xe7, 0x01,
-	0xf8, 0xf8, 0x63, 0xf4, 0xec, 0xa1, 0xfa, 0xb4, 0x3f, 0x34, 0x07, 0xc3, 0xaf, 0x6b, 0x4a, 0xbd,
-	0x7a, 0x79, 0x6d, 0xec, 0x9e, 0x42, 0xe8, 0x07, 0xe1, 0xf4, 0xdf, 0x2a, 0xb3, 0xdf, 0x1b, 0x98,
-	0x7d, 0xb3, 0x56, 0x4c, 0x55, 0x26, 0x78, 0x81, 0x0f, 0x7e, 0xfd, 0xc9, 0x4f, 0xbf, 0xea, 0xca,
-	0xef, 0xbf, 0xe9, 0x4a, 0x77, 0x78, 0xf3, 0xb7, 0x5e, 0xb8, 0x59, 0xeb, 0xca, 0xed, 0x5a, 0x57,
-	0xfe, 0x5a, 0xeb, 0xca, 0xd5, 0xbd, 0x5e, 0xb8, 0xbd, 0xd7, 0x0b, 0x7f, 0xde, 0xeb, 0x85, 0x6f,
-	0xdf, 0x4c, 0x03, 0x3e, 0x8b, 0x27, 0x2d, 0x8f, 0x2c, 0xdb, 0xee, 0x05, 0x2c, 0x5c, 0x1a, 0x02,
-	0xff, 0x9e, 0xd0, 0xf9, 0xa6, 0x7a, 0xed, 0x11, 0x0a, 0xed, 0x8b, 0xb6, 0x78, 0xc7, 0xe4, 0xb3,
-	0x35, 0xd9, 0x91, 0xef, 0xd6, 0xe7, 0xff, 0x04, 0x00, 0x00, 0xff, 0xff, 0x59, 0x43, 0x2f, 0xde,
-	0x17, 0x05, 0x00, 0x00,
-}
-
-func (m *QuerySigResponse) Marshal() (dAtA []byte, err error) {
+	// 802 bytes of a gzipped FileDescriptorProto
+	0x1f, 0x8b, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02, 0xff, 0xac, 0x54, 0x3f, 0x73, 0xe3, 0x44,
+	0x1c, 0xf5, 0xc6, 0xf9, 0xa7, 0x75, 0x08, 0xbe, 0xbd, 0x0b, 0x31, 0x86, 0xd3, 0x09, 0x0f, 0x33,
+	0xa7, 0x81, 0xc4, 0xbe, 0x98, 0x86, 0x36, 0x89, 0x1c, 0xc6, 0x93, 0x19, 0x25, 0xc8, 0x76, 0x0a,
+	0x1a, 0x8d, 0x2c, 0xfd, 0xce, 0xd6, 0xd8, 0xd6, 0x8a, 0xdd, 0x95, 0x89, 0x2a, 0x5a, 0x26, 0x15,
+	0x7c, 0x80, 0x34, 0x40, 0xc1, 0x07, 0xa0, 0xe1, 0x1b, 0xa4, 0xbc, 0x92, 0xea, 0x06, 0x9c, 0x2f,
+	0xc2, 0xec, 0xca, 0x92, 0x43, 0xa0, 0xbc, 0x4a, 0xbb, 0xef, 0xbd, 0xdf, 0xdb, 0xf7, 0xdb, 0x9f,
+	0x66, 0xf1, 0xbe, 0xe0, 0xbc, 0x35, 0x3f, 0x1a, 0x82, 0xf0, 0x8e, 0x5a, 0xdf, 0x26, 0xc0, 0xd2,
+	0x66, 0xcc, 0xa8, 0xa0, 0xa4, 0x22, 0x38, 0x6f, 0x2e, 0x89, 0xfa, 0xb3, 0x11, 0x1d, 0x51, 0x85,
+	0xb7, 0xe4, 0x2a, 0x93, 0xd4, 0x0d, 0x59, 0x0b, 0xd7, 0x31, 0x65, 0x02, 0x82, 0xc2, 0x44, 0xa4,
+	0x31, 0xf0, 0x4c, 0xd1, 0xb8, 0x43, 0xf8, 0x83, 0xaf, 0xa5, 0x69, 0x2f, 0x1c, 0x45, 0x9e, 0x48,
+	0x18, 0x38, 0xc0, 0x63, 0x1a, 0x71, 0x20, 0x5f, 0xe2, 0xca, 0x9c, 0x0a, 0x70, 0xb9, 0xf0, 0x44,
+	0xc2, 0x6b, 0xc8, 0x40, 0xe6, 0x6e, 0x7b, 0xbf, 0xf9, 0xe0, 0xd4, 0xe6, 0x15, 0x15, 0xd0, 0x53,
+	0xb4, 0x83, 0xe7, 0xc5, 0x9a, 0x9c, 0x63, 0x8d, 0xe7, 0x76, 0xb5, 0x35, 0x03, 0x99, 0x95, 0xf6,
+	0xe1, 0xbf, 0xea, 0xfe, 0xff, 0xc4, 0xe6, 0x0a, 0x59, 0xd5, 0xd7, 0x5f, 0x62, 0xad, 0xc0, 0xc9,
+	0x0e, 0x46, 0x4c, 0x25, 0xd1, 0x1c, 0xc4, 0xe4, 0x8e, 0x2b, 0x7f, 0xcd, 0x41, 0xbc, 0xf1, 0x3d,
+	0xae, 0x2a, 0xdf, 0x73, 0x48, 0xdf, 0x41, 0x0f, 0x47, 0x78, 0x9d, 0xd1, 0x69, 0x16, 0x7f, 0xb7,
+	0xfd, 0x5c, 0x95, 0xe4, 0x37, 0x59, 0xd4, 0xca, 0xa3, 0xe8, 0x14, 0x1c, 0x25, 0x6d, 0xfc, 0x8e,
+	0xf0, 0x9e, 0x4a, 0xe0, 0x80, 0x4f, 0xe7, 0xea, 0xbb, 0x8c, 0xf1, 0x1c, 0xe3, 0xd8, 0x63, 0x22,
+	0x75, 0x93, 0x30, 0x90, 0x29, 0xca, 0xa6, 0xe6, 0x68, 0x0a, 0x19, 0x84, 0x01, 0x27, 0x07, 0x98,
+	0x64, 0x34, 0x1f, 0x7b, 0x0c, 0x5c, 0x9f, 0x26, 0x91, 0x90, 0x8d, 0x95, 0xcd, 0xf7, 0x9c, 0xaa,
+	0x62, 0x7a, 0x92, 0x38, 0x55, 0x38, 0xf9, 0x18, 0x6b, 0x62, 0xcc, 0x80, 0x8f, 0xe9, 0x34, 0xa8,
+	0x95, 0x0d, 0x64, 0x6e, 0x38, 0x2b, 0x80, 0xbc, 0xc2, 0xcf, 0x32, 0x17, 0xb6, 0x0c, 0xe1, 0x86,
+	0xd1, 0x6b, 0xca, 0x6b, 0xeb, 0x46, 0xd9, 0xdc, 0x71, 0x88, 0xe2, 0xf2, 0x7c, 0x5d, 0xc9, 0x34,
+	0x7e, 0x2a, 0x2f, 0x63, 0x9f, 0x43, 0x76, 0x4e, 0x11, 0xbb, 0x87, 0x2b, 0x99, 0x57, 0x66, 0x21,
+	0x73, 0x57, 0xda, 0x07, 0xff, 0x9d, 0xe4, 0xe3, 0xc2, 0xa6, 0xda, 0x49, 0xf7, 0x93, 0xf5, 0xbb,
+	0xb7, 0x2f, 0x4a, 0x0e, 0xe6, 0x39, 0xc0, 0xeb, 0x3f, 0xaf, 0x61, 0xad, 0xe0, 0x89, 0x81, 0x37,
+	0x27, 0x90, 0xba, 0x61, 0x90, 0x4d, 0xf5, 0x44, 0x5b, 0xbc, 0x7d, 0xb1, 0x71, 0x0e, 0x69, 0xd7,
+	0x72, 0x36, 0x26, 0x90, 0x76, 0x03, 0xf2, 0x11, 0xd6, 0xa4, 0xc2, 0x1f, 0x7b, 0x61, 0xb4, 0x1c,
+	0xf6, 0xf6, 0x04, 0xd2, 0x53, 0xb9, 0x27, 0x1f, 0x62, 0xb9, 0x76, 0xd5, 0xa4, 0xca, 0x8a, 0xdb,
+	0x9a, 0x64, 0x33, 0x21, 0x6d, 0xbc, 0xc7, 0x23, 0x2f, 0xe6, 0x63, 0x2a, 0xdc, 0xe1, 0x94, 0xfa,
+	0x13, 0x37, 0x4a, 0x66, 0x43, 0x60, 0xb5, 0x75, 0x03, 0x99, 0x65, 0xe7, 0x69, 0x4e, 0x9e, 0x48,
+	0xce, 0x56, 0x14, 0xf9, 0x1c, 0x3f, 0x99, 0x7b, 0xd3, 0x30, 0xf0, 0x04, 0x65, 0xae, 0x17, 0x04,
+	0x0c, 0x38, 0xaf, 0x6d, 0x28, 0xdf, 0x6a, 0x41, 0x1c, 0x67, 0xb8, 0xbc, 0xe9, 0x28, 0x99, 0xb9,
+	0xab, 0x02, 0xd5, 0x24, 0xaf, 0x6d, 0x2a, 0x7f, 0x12, 0x25, 0xb3, 0xab, 0x9c, 0x52, 0xfd, 0x72,
+	0x62, 0xe2, 0xaa, 0xac, 0x10, 0x54, 0x78, 0xd3, 0x5c, 0xbd, 0xa5, 0xd4, 0xbb, 0x51, 0x32, 0xeb,
+	0x4b, 0x38, 0x53, 0x36, 0x1c, 0xfc, 0x89, 0xba, 0x59, 0x0b, 0x3c, 0x5f, 0x84, 0x73, 0x4f, 0x40,
+	0x70, 0x11, 0x03, 0x93, 0x5e, 0xbc, 0x18, 0xcf, 0x21, 0x26, 0x74, 0x09, 0xe6, 0x61, 0x21, 0xff,
+	0xbb, 0x9e, 0xe4, 0xcc, 0x71, 0x4e, 0x7c, 0xf6, 0x07, 0xc2, 0x78, 0xf5, 0xb3, 0x93, 0x03, 0xbc,
+	0x7f, 0x75, 0xd1, 0xef, 0xb8, 0xbd, 0xfe, 0x71, 0x7f, 0xd0, 0x73, 0x07, 0x76, 0xef, 0xb2, 0x73,
+	0xda, 0x3d, 0xeb, 0x76, 0xac, 0x6a, 0xa9, 0xfe, 0xfe, 0xcd, 0xad, 0x51, 0x19, 0x44, 0x3c, 0x06,
+	0x3f, 0x7c, 0x1d, 0x42, 0x40, 0x5e, 0xe2, 0xbd, 0x87, 0x6a, 0xfb, 0xa2, 0xef, 0x9e, 0x5d, 0x0c,
+	0x6c, 0xab, 0x8a, 0xea, 0x3b, 0x37, 0xb7, 0xc6, 0xb6, 0x4d, 0xc5, 0x19, 0x4d, 0xa2, 0x80, 0x7c,
+	0x8a, 0x9f, 0x3e, 0x14, 0x5e, 0x76, 0x6c, 0xab, 0x6b, 0x7f, 0x55, 0x5d, 0xab, 0x57, 0x6e, 0x6e,
+	0x8d, 0xad, 0x4b, 0x88, 0x82, 0x30, 0x1a, 0x3d, 0x56, 0x59, 0x9d, 0xd3, 0xae, 0xd5, 0xb1, 0xaa,
+	0xe5, 0x4c, 0x65, 0x81, 0x1f, 0x06, 0x10, 0xd4, 0xb7, 0x7f, 0xf8, 0x45, 0x2f, 0xfd, 0xf6, 0xab,
+	0x8e, 0x4e, 0xec, 0xbb, 0xbf, 0xf5, 0xd2, 0xdd, 0x42, 0x47, 0x6f, 0x16, 0x3a, 0xfa, 0x6b, 0xa1,
+	0xa3, 0x1f, 0xef, 0xf5, 0xd2, 0x9b, 0x7b, 0xbd, 0xf4, 0xe7, 0xbd, 0x5e, 0xfa, 0xe6, 0xd5, 0x28,
+	0x14, 0xe3, 0x64, 0xd8, 0xf4, 0xe9, 0xac, 0xe5, 0x5d, 0xc3, 0xd4, 0x63, 0x11, 0x88, 0xef, 0x28,
+	0x9b, 0x2c, 0x77, 0x87, 0x3e, 0x65, 0xd0, 0xba, 0x6e, 0xc9, 0xd7, 0x50, 0x3d, 0x7e, 0xc3, 0x4d,
+	0xf5, 0xfa, 0x7d, 0xf1, 0x4f, 0x00, 0x00, 0x00, 0xff, 0xff, 0xbf, 0x50, 0x52, 0xd8, 0x5d, 0x05,
+	0x00, 0x00,
+}
+
+func (m *QuerySignatureResponse) Marshal() (dAtA []byte, err error) {
 	size := m.Size()
 	dAtA = make([]byte, size)
 	n, err := m.MarshalToSizedBuffer(dAtA[:size])
@@ -399,12 +404,12 @@ func (m *QuerySigResponse) Marshal() (dAtA []byte, err error) {
 	return dAtA[:n], nil
 }
 
-func (m *QuerySigResponse) MarshalTo(dAtA []byte) (int, error) {
+func (m *QuerySignatureResponse) MarshalTo(dAtA []byte) (int, error) {
 	size := m.Size()
 	return m.MarshalToSizedBuffer(dAtA[:size])
 }
 
-func (m *QuerySigResponse) MarshalToSizedBuffer(dAtA []byte) (int, error) {
+func (m *QuerySignatureResponse) MarshalToSizedBuffer(dAtA []byte) (int, error) {
 	i := len(dAtA)
 	_ = i
 	var l int
@@ -429,7 +434,7 @@ func (m *QuerySigResponse) MarshalToSizedBuffer(dAtA []byte) (int, error) {
 	return len(dAtA) - i, nil
 }
 
-func (m *Signature) Marshal() (dAtA []byte, err error) {
+func (m *QuerySignatureResponse_Signature) Marshal() (dAtA []byte, err error) {
 	size := m.Size()
 	dAtA = make([]byte, size)
 	n, err := m.MarshalToSizedBuffer(dAtA[:size])
@@ -439,12 +444,12 @@ func (m *Signature) Marshal() (dAtA []byte, err error) {
 	return dAtA[:n], nil
 }
 
-func (m *Signature) MarshalTo(dAtA []byte) (int, error) {
+func (m *QuerySignatureResponse_Signature) MarshalTo(dAtA []byte) (int, error) {
 	size := m.Size()
 	return m.MarshalToSizedBuffer(dAtA[:size])
 }
 
-func (m *Signature) MarshalToSizedBuffer(dAtA []byte) (int, error) {
+func (m *QuerySignatureResponse_Signature) MarshalToSizedBuffer(dAtA []byte) (int, error) {
 	i := len(dAtA)
 	_ = i
 	var l int
@@ -454,14 +459,14 @@ func (m *Signature) MarshalToSizedBuffer(dAtA []byte) (int, error) {
 		copy(dAtA[i:], m.S)
 		i = encodeVarintQuery(dAtA, i, uint64(len(m.S)))
 		i--
-		dAtA[i] = 0x1a
+		dAtA[i] = 0x12
 	}
 	if len(m.R) > 0 {
 		i -= len(m.R)
 		copy(dAtA[i:], m.R)
 		i = encodeVarintQuery(dAtA, i, uint64(len(m.R)))
 		i--
-		dAtA[i] = 0x12
+		dAtA[i] = 0xa
 	}
 	return len(dAtA) - i, nil
 }
@@ -709,7 +714,7 @@ func encodeVarintQuery(dAtA []byte, offset int, v uint64) int {
 	dAtA[offset] = uint8(v)
 	return base
 }
-func (m *QuerySigResponse) Size() (n int) {
+func (m *QuerySignatureResponse) Size() (n int) {
 	if m == nil {
 		return 0
 	}
@@ -725,7 +730,7 @@ func (m *QuerySigResponse) Size() (n int) {
 	return n
 }
 
-func (m *Signature) Size() (n int) {
+func (m *QuerySignatureResponse_Signature) Size() (n int) {
 	if m == nil {
 		return 0
 	}
@@ -858,7 +863,7 @@ func sovQuery(x uint64) (n int) {
 func sozQuery(x uint64) (n int) {
 	return sovQuery(uint64((x << 1) ^ uint64((int64(x) >> 63))))
 }
-func (m *QuerySigResponse) Unmarshal(dAtA []byte) error {
+func (m *QuerySignatureResponse) Unmarshal(dAtA []byte) error {
 	l := len(dAtA)
 	iNdEx := 0
 	for iNdEx < l {
@@ -881,10 +886,10 @@ func (m *QuerySigResponse) Unmarshal(dAtA []byte) error {
 		fieldNum := int32(wire >> 3)
 		wireType := int(wire & 0x7)
 		if wireType == 4 {
-			return fmt.Errorf("proto: QuerySigResponse: wiretype end group for non-group")
+			return fmt.Errorf("proto: QuerySignatureResponse: wiretype end group for non-group")
 		}
 		if fieldNum <= 0 {
-			return fmt.Errorf("proto: QuerySigResponse: illegal tag %d (wire type %d)", fieldNum, wire)
+			return fmt.Errorf("proto: QuerySignatureResponse: illegal tag %d (wire type %d)", fieldNum, wire)
 		}
 		switch fieldNum {
 		case 1:
@@ -936,7 +941,7 @@ func (m *QuerySigResponse) Unmarshal(dAtA []byte) error {
 				return io.ErrUnexpectedEOF
 			}
 			if m.Signature == nil {
-				m.Signature = &Signature{}
+				m.Signature = &QuerySignatureResponse_Signature{}
 			}
 			if err := m.Signature.Unmarshal(dAtA[iNdEx:postIndex]); err != nil {
 				return err
@@ -963,7 +968,7 @@ func (m *QuerySigResponse) Unmarshal(dAtA []byte) error {
 	}
 	return nil
 }
-func (m *Signature) Unmarshal(dAtA []byte) error {
+func (m *QuerySignatureResponse_Signature) Unmarshal(dAtA []byte) error {
 	l := len(dAtA)
 	iNdEx := 0
 	for iNdEx < l {
@@ -992,11 +997,11 @@ func (m *Signature) Unmarshal(dAtA []byte) error {
 			return fmt.Errorf("proto: Signature: illegal tag %d (wire type %d)", fieldNum, wire)
 		}
 		switch fieldNum {
-		case 2:
+		case 1:
 			if wireType != 2 {
 				return fmt.Errorf("proto: wrong wireType = %d for field R", wireType)
 			}
-			var byteLen int
+			var stringLen uint64
 			for shift := uint(0); ; shift += 7 {
 				if shift >= 64 {
 					return ErrIntOverflowQuery
@@ -1006,31 +1011,29 @@ func (m *Signature) Unmarshal(dAtA []byte) error {
 				}
 				b := dAtA[iNdEx]
 				iNdEx++
-				byteLen |= int(b&0x7F) << shift
+				stringLen |= uint64(b&0x7F) << shift
 				if b < 0x80 {
 					break
 				}
 			}
-			if byteLen < 0 {
+			intStringLen := int(stringLen)
+			if intStringLen < 0 {
 				return ErrInvalidLengthQuery
 			}
-			postIndex := iNdEx + byteLen
+			postIndex := iNdEx + intStringLen
 			if postIndex < 0 {
 				return ErrInvalidLengthQuery
 			}
 			if postIndex > l {
 				return io.ErrUnexpectedEOF
 			}
-			m.R = append(m.R[:0], dAtA[iNdEx:postIndex]...)
-			if m.R == nil {
-				m.R = []byte{}
-			}
+			m.R = string(dAtA[iNdEx:postIndex])
 			iNdEx = postIndex
-		case 3:
+		case 2:
 			if wireType != 2 {
 				return fmt.Errorf("proto: wrong wireType = %d for field S", wireType)
 			}
-			var byteLen int
+			var stringLen uint64
 			for shift := uint(0); ; shift += 7 {
 				if shift >= 64 {
 					return ErrIntOverflowQuery
@@ -1040,25 +1043,23 @@ func (m *Signature) Unmarshal(dAtA []byte) error {
 				}
 				b := dAtA[iNdEx]
 				iNdEx++
-				byteLen |= int(b&0x7F) << shift
+				stringLen |= uint64(b&0x7F) << shift
 				if b < 0x80 {
 					break
 				}
 			}
-			if byteLen < 0 {
+			intStringLen := int(stringLen)
+			if intStringLen < 0 {
 				return ErrInvalidLengthQuery
 			}
-			postIndex := iNdEx + byteLen
+			postIndex := iNdEx + intStringLen
 			if postIndex < 0 {
 				return ErrInvalidLengthQuery
 			}
 			if postIndex > l {
 				return io.ErrUnexpectedEOF
 			}
-			m.S = append(m.S[:0], dAtA[iNdEx:postIndex]...)
-			if m.S == nil {
-				m.S = []byte{}
-			}
+			m.S = string(dAtA[iNdEx:postIndex])
 			iNdEx = postIndex
 		default:
 			iNdEx = preIndex
```

### x/tss/types/types.go
```diff
@@ -1,19 +0,0 @@
-package types
-
-import (
-	"github.com/ethereum/go-ethereum/common/hexutil"
-)
-
-// HexSignature represents a tss signature as hex encoded bytes for use in responses from the query client.
-type HexSignature struct {
-	R string `json:"r"`
-	S string `json:"s"`
-}
-
-// NewHexSignatureFromQuerySigResponse converts a QuerySigResponse to a HexSignature
-func NewHexSignatureFromQuerySigResponse(sigResp *QuerySigResponse) HexSignature {
-	return HexSignature{
-		R: hexutil.Encode(sigResp.Signature.R),
-		S: hexutil.Encode(sigResp.Signature.S),
-	}
-}
```
