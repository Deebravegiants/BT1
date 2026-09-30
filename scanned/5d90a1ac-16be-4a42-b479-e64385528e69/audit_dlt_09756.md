# [?] Fix possible total validator weight overflow in warp messages

## Summary
Severity: Unknown
Chain: Flare
Component: flare-foundation/go-flare
Published: 2026-05-19
Source: https://github.com/flare-foundation/go-flare/commit/576fec15d8cee91c576069bca482ab6c12a2f754
Type: security-commit

## Details
Fix possible total validator weight overflow in warp messages

## Patch
### avalanchego/network/p2p/validators.go
```diff
@@ -8,6 +8,7 @@ import (
 	"context"
 	"fmt"
 	"math"
+	"math/big"
 	"sync"
 	"time"
 
@@ -48,6 +49,7 @@ func NewValidators(
 		subnetID:                 subnetID,
 		validators:               validators,
 		maxValidatorSetStaleness: maxValidatorSetStaleness,
+		totalWeight:              new(big.Int),
 	}
 }
 
@@ -63,7 +65,7 @@ type Validators struct {
 	connectedValidators set.Set[ids.NodeID]
 	validatorList       []validator
 	validatorSet        set.Set[ids.NodeID]
-	totalWeight         uint64
+	totalWeight         *big.Int
 	lastUpdated         time.Time
 }
 
@@ -120,14 +122,14 @@ func (v *Validators) refresh(ctx context.Context) {
 	// Even though validatorList may be nil, truncating will not panic.
 	v.validatorList = v.validatorList[:0]
 	v.validatorSet.Clear()
-	v.totalWeight = 0
+	v.totalWeight.SetUint64(0)
 	for nodeID, vdr := range validatorSet {
 		v.validatorList = append(v.validatorList, validator{
 			nodeID: nodeID,
 			weight: vdr.Weight,
 		})
 		v.validatorSet.Add(nodeID)
-		v.totalWeight += vdr.Weight
+		v.totalWeight.Add(v.totalWeight, new(big.Int).SetUint64(vdr.Weight))
 	}
 	utils.Sort(v.validatorList)
 
@@ -179,21 +181,33 @@ func (v *Validators) Top(ctx context.Context, percentage float64) []ids.NodeID {
 	var (
 		maxSize      = int(math.Ceil(percentage * float64(len(v.validatorList))))
 		top          = make([]ids.NodeID, 0, maxSize)
-		currentStake uint64
-		targetStake  = uint64(math.Ceil(percentage * float64(v.totalWeight)))
+		currentStake = new(big.Int)
+		targetStake  = ceilStake(v.totalWeight, percentage)
 	)
 
 	for _, vdr := range v.validatorList {
-		if currentStake >= targetStake {
+		if currentStake.Cmp(targetStake) >= 0 {
 			break
 		}
 		top = append(top, vdr.nodeID)
-		currentStake += vdr.weight
+		currentStake.Add(currentStake, new(big.Int).SetUint64(vdr.weight))
 	}
 
 	return top
 }
 
+// ceilStake returns ceil(total * percentage) as a *big.Int. percentage is
+// expected to be in [0, 1].
+func ceilStake(total *big.Int, percentage float64) *big.Int {
+	scaled := new(big.Float).SetInt(total)
+	scaled.Mul(scaled, big.NewFloat(percentage))
+	result, acc := scaled.Int(nil)
+	if acc == big.Below {
+		result.Add(result, big.NewInt(1))
+	}
+	return result
+}
+
 // Has returns if nodeID is a connected validator
 func (v *Validators) Has(ctx context.Context, nodeID ids.NodeID) bool {
 	v.refresh(ctx)
```

### avalanchego/proto/pb/validatorstate/validator_state.pb.go
```diff
@@ -536,7 +536,7 @@ func (x *GetWarpValidatorSetsResponse) GetValidatorSets() []*WarpValidatorSet {
 
 type GetWarpValidatorSetResponse struct {
 	state         protoimpl.MessageState `protogen:"open.v1"`
-	TotalWeight   uint64                 `protobuf:"varint,1,opt,name=total_weight,json=totalWeight,proto3" json:"total_weight,omitempty"`
+	TotalWeight   []byte                 `protobuf:"bytes,1,opt,name=total_weight,json=totalWeight,proto3" json:"total_weight,omitempty"`
 	Validators    []*WarpValidator       `protobuf:"bytes,2,rep,name=validators,proto3" json:"validators,omitempty"`
 	unknownFields protoimpl.UnknownFields
 	sizeCache     protoimpl.SizeCache
@@ -572,11 +572,11 @@ func (*GetWarpValidatorSetResponse) Descriptor() ([]byte, []int) {
 	return file_validatorstate_validator_state_proto_rawDescGZIP(), []int{10}
 }
 
-func (x *GetWarpValidatorSetResponse) GetTotalWeight() uint64 {
+func (x *GetWarpValidatorSetResponse) GetTotalWeight() []byte {
 	if x != nil {
 		return x.TotalWeight
 	}
-	return 0
+	return nil
 }
 
 func (x *GetWarpValidatorSetResponse) GetValidators() []*WarpValidator {
@@ -589,7 +589,7 @@ func (x *GetWarpValidatorSetResponse) GetValidators() []*WarpValidator {
 type WarpValidatorSet struct {
 	state         protoimpl.MessageState `protogen:"open.v1"`
 	SubnetId      []byte                 `protobuf:"bytes,1,opt,name=subnet_id,json=subnetId,proto3" json:"subnet_id,omitempty"`
-	TotalWeight   uint64                 `protobuf:"varint,2,opt,name=total_weight,json=totalWeight,proto3" json:"total_weight,omitempty"`
+	TotalWeight   []byte                 `protobuf:"bytes,2,opt,name=total_weight,json=totalWeight,proto3" json:"total_weight,omitempty"`
 	Validators    []*WarpValidator       `protobuf:"bytes,3,rep,name=validators,proto3" json:"validators,omitempty"`
 	unknownFields protoimpl.UnknownFields
 	sizeCache     protoimpl.SizeCache
@@ -632,11 +632,11 @@ func (x *WarpValidatorSet) GetSubnetId() []byte {
 	return nil
 }
 
-func (x *WarpValidatorSet) GetTotalWeight() uint64 {
+func (x *WarpValidatorSet) GetTotalWeight() []byte {
 	if x != nil {
 		return x.TotalWeight
 	}
-	return 0
+	return nil
 }
 
 func (x *WarpValidatorSet) GetValidators() []*WarpValidator {
@@ -839,13 +839,13 @@ const file_validatorstate_validator_state_proto_rawDesc = "" +
 	"\x1cGetWarpValidatorSetsResponse\x12G\n" +
 	"\x0evalidator_sets\x18\x01 \x03(\v2 .validatorstate.WarpValidatorSetR\rvalidatorSets\"\x7f\n" +
 	"\x1bGetWarpValidatorSetResponse\x12!\n" +
-	"\ftotal_weight\x18\x01 \x01(\x04R\vtotalWeight\x12=\n" +
+	"\ftotal_weight\x18\x01 \x01(\fR\vtotalWeight\x12=\n" +
 	"\n" +
 	"validators\x18\x02 \x03(\v2\x1d.validatorstate.WarpValidatorR\n" +
 	"validators\"\x91\x01\n" +
 	"\x10WarpValidatorSet\x12\x1b\n" +
 	"\tsubnet_id\x18\x01 \x01(\fR\bsubnetId\x12!\n" +
-	"\ftotal_weight\x18\x02 \x01(\x04R\vtotalWeight\x12=\n" +
+	"\ftotal_weight\x18\x02 \x01(\fR\vtotalWeight\x12=\n" +
 	"\n" +
 	"validators\x18\x03 \x03(\v2\x1d.validatorstate.WarpValidatorR\n" +
 	"validators\"a\n" +
```

### avalanchego/proto/validatorstate/validator_state.proto
```diff
@@ -81,13 +81,13 @@ message GetWarpValidatorSetsResponse {
 }
 
 message GetWarpValidatorSetResponse {
-  uint64 total_weight = 1;
+  bytes total_weight = 1;
   repeated WarpValidator validators = 2;
 }
 
 message WarpValidatorSet {
   bytes subnet_id = 1;
-  uint64 total_weight = 2;
+  bytes total_weight = 2;
   repeated WarpValidator validators = 3;
 }
 
```

### avalanchego/snow/validators/gvalidators/validator_state_client.go
```diff
@@ -7,6 +7,7 @@ import (
 	"context"
 	"errors"
 	"fmt"
+	"math/big"
 
 	"google.golang.org/protobuf/types/known/emptypb"
 
@@ -86,7 +87,7 @@ func (c *Client) GetWarpValidatorSets(
 		}
 		validatorSets[subnetID] = validators.WarpSet{
 			Validators:  vdrs,
-			TotalWeight: validatorSet.GetTotalWeight(),
+			TotalWeight: new(big.Int).SetBytes(validatorSet.GetTotalWeight()),
 		}
 	}
 
@@ -119,7 +120,7 @@ func (c *Client) GetWarpValidatorSet(
 	}
 	return validators.WarpSet{
 		Validators:  vdrs,
-		TotalWeight: resp.GetTotalWeight(),
+		TotalWeight: new(big.Int).SetBytes(resp.GetTotalWeight()),
 	}, nil
 }
 
```

### avalanchego/snow/validators/gvalidators/validator_state_server.go
```diff
@@ -5,6 +5,7 @@ package gvalidators
 
 import (
 	"context"
+	"math/big"
 
 	"google.golang.org/protobuf/types/known/emptypb"
 
@@ -58,7 +59,7 @@ func (s *Server) GetWarpValidatorSets(ctx context.Context, req *pb.GetWarpValida
 	for subnetID, vdrs := range validatorSets {
 		proto = append(proto, &pb.WarpValidatorSet{
 			SubnetId:    subnetID[:],
-			TotalWeight: vdrs.TotalWeight,
+			TotalWeight: totalWeightBytes(vdrs.TotalWeight),
 			Validators:  warpValidatorsToProto(vdrs.Validators),
 		})
 	}
@@ -77,11 +78,20 @@ func (s *Server) GetWarpValidatorSet(ctx context.Context, req *pb.GetWarpValidat
 		return nil, err
 	}
 	return &pb.GetWarpValidatorSetResponse{
-		TotalWeight: validatorSet.TotalWeight,
+		TotalWeight: totalWeightBytes(validatorSet.TotalWeight),
 		Validators:  warpValidatorsToProto(validatorSet.Validators),
 	}, nil
 }
 
+// totalWeightBytes encodes a *big.Int total weight for the proto wire,
+// treating nil as zero (empty bytes).
+func totalWeightBytes(w *big.Int) []byte {
+	if w == nil {
+		return nil
+	}
+	return w.Bytes()
+}
+
 func (s *Server) GetValidatorSet(ctx context.Context, req *pb.GetValidatorSetRequest) (*pb.GetValidatorSetResponse, error) {
 	subnetID, err := ids.ToID(req.SubnetId)
 	if err != nil {
```

### avalanchego/snow/validators/gvalidators/validator_state_test.go
```diff
@@ -304,4 +304,24 @@ func TestGetWarpValidatorSet(t *testing.T) {
 		require.NoError(err)
 		require.Equal(expectedVdrSet, vdrSet)
 	})
+
+	t.Run("nil_total_weight", func(t *testing.T) {
+		// A WarpSet with nil TotalWeight must not panic the server; the wire
+		// encoding treats nil as zero bytes and the client decodes to a
+		// zero-valued *big.Int.
+		require := require.New(t)
+
+		subnetID := ids.GenerateTestID()
+		state := &validatorstest.State{
+			GetWarpValidatorSetF: func(_ context.Context, _ uint64, _ ids.ID) (validators.WarpSet, error) {
+				return validators.WarpSet{}, nil
+			},
+		}
+		c := newClient(t, state)
+
+		vdrSet, err := c.GetWarpValidatorSet(t.Context(), height, subnetID)
+		require.NoError(err)
+		require.NotNil(vdrSet.TotalWeight)
+		require.Equal(0, vdrSet.TotalWeight.Sign())
+	})
 }
```

### avalanchego/snow/validators/validatorstest/warp.go
```diff
@@ -4,6 +4,7 @@
 package validatorstest
 
 import (
+	"math/big"
 	"testing"
 
 	"github.com/stretchr/testify/require"
@@ -41,7 +42,7 @@ func NewWarpSet(t testing.TB, n uint64) validators.WarpSet {
 	utils.Sort(vdrs)
 	return validators.WarpSet{
 		Validators:  vdrs,
-		TotalWeight: n,
+		TotalWeight: new(big.Int).SetUint64(n),
 	}
 }
 
```

### avalanchego/snow/validators/warp.go
```diff
@@ -6,14 +6,14 @@ package validators
 import (
 	"bytes"
 	"encoding/json"
+	"math/big"
 
 	"golang.org/x/exp/maps"
 
 	"github.com/ava-labs/avalanchego/ids"
 	"github.com/ava-labs/avalanchego/utils"
 	"github.com/ava-labs/avalanchego/utils/crypto/bls"
 	"github.com/ava-labs/avalanchego/utils/formatting"
-	"github.com/ava-labs/avalanchego/utils/math"
 
 	avajson "github.com/ava-labs/avalanchego/utils/json"
 )
@@ -25,18 +25,22 @@ type WarpSet struct {
 	Validators []*Warp
 	// The total weight of all the validators, including the ones that don't
 	// have a public key.
-	TotalWeight uint64
+	TotalWeight *big.Int
 }
 
 type jsonWarpSet struct {
 	Validators  []*Warp        `json:"validators"`
-	TotalWeight avajson.Uint64 `json:"totalWeight"`
+	TotalWeight avajson.BigInt `json:"totalWeight"`
 }
 
 func (w WarpSet) MarshalJSON() ([]byte, error) {
+	totalWeight := w.TotalWeight
+	if totalWeight == nil {
+		totalWeight = new(big.Int)
+	}
 	return json.Marshal(jsonWarpSet{
 		Validators:  w.Validators,
-		TotalWeight: avajson.Uint64(w.TotalWeight),
+		TotalWeight: avajson.NewBigInt(totalWeight),
 	})
 }
 
@@ -45,7 +49,7 @@ func (w *WarpSet) UnmarshalJSON(b []byte) error {
 	if err := json.Unmarshal(b, &j); err != nil {
 		return err
 	}
-	w.TotalWeight = uint64(j.TotalWeight)
+	w.TotalWeight = j.TotalWeight.ToBigInt()
 	w.Validators = j.Validators
 	return nil
 }
@@ -108,14 +112,10 @@ func (w *Warp) UnmarshalJSON(b []byte) error {
 func FlattenValidatorSet(vdrSet map[ids.NodeID]*GetValidatorOutput) (WarpSet, error) {
 	var (
 		vdrs        = make(map[string]*Warp, len(vdrSet))
-		totalWeight uint64
-		err         error
+		totalWeight = new(big.Int)
 	)
 	for _, vdr := range vdrSet {
-		totalWeight, err = math.Add(totalWeight, vdr.Weight)
-		if err != nil {
-			return WarpSet{}, err
-		}
+		totalWeight.Add(totalWeight, new(big.Int).SetUint64(vdr.Weight))
 
 		if vdr.PublicKey == nil {
 			continue
@@ -131,7 +131,10 @@ func FlattenValidatorSet(vdrSet map[ids.NodeID]*GetValidatorOutput) (WarpSet, er
 			vdrs[string(pkBytes)] = uniqueVdr
 		}
 
-		uniqueVdr.Weight += vdr.Weight // Impossible to overflow here
+		// Individual validator weights fit in uint64. Although BLS keys are not
+		// consensus-enforced unique, validators are expected to use unique keys; a
+		// shared-key aggregate exceeding uint64 is treated as out of scope.
+		uniqueVdr.Weight += vdr.Weight
 		uniqueVdr.NodeIDs = append(uniqueVdr.NodeIDs, vdr.NodeID)
 	}
 
```

### avalanchego/snow/validators/warp_test.go
```diff
@@ -6,7 +6,7 @@ package validators_test
 import (
 	"encoding/hex"
 	"encoding/json"
-	"math"
+	"math/big"
 	"strconv"
 	"testing"
 
@@ -17,8 +17,6 @@ import (
 	"github.com/ava-labs/avalanchego/utils/crypto/bls"
 	"github.com/ava-labs/avalanchego/utils/crypto/bls/signer/localsigner"
 
-	safemath "github.com/ava-labs/avalanchego/utils/math"
-
 	. "github.com/ava-labs/avalanchego/snow/validators"
 )
 
@@ -75,7 +73,7 @@ func TestWarpSetJSON(t *testing.T) {
 				},
 			},
 		},
-		TotalWeight: 54321,
+		TotalWeight: big.NewInt(54321),
 	}
 	wsJSON, err := json.MarshalIndent(ws, "", "\t")
 	require.NoError(t, err)
@@ -100,6 +98,15 @@ func TestWarpSetJSON(t *testing.T) {
 	require.Equal(t, ws, parsedWS)
 }
 
+func TestWarpSetMarshalJSONNilTotalWeight(t *testing.T) {
+	// A zero-value WarpSet (TotalWeight == nil) must not panic on MarshalJSON;
+	// nil is treated as zero.
+	ws := WarpSet{}
+	wsJSON, err := json.Marshal(ws)
+	require.NoError(t, err)
+	require.JSONEq(t, `{"validators":null,"totalWeight":"0"}`, string(wsJSON))
+}
+
 func TestFlattenValidatorSet(t *testing.T) {
 	var (
 		vdrs    = validatorstest.NewWarpSet(t, 3)
@@ -113,18 +120,6 @@ func TestFlattenValidatorSet(t *testing.T) {
 		want       WarpSet
 		wantErr    error
 	}{
-		{
-			name: "overflow",
-			validators: map[ids.NodeID]*GetValidatorOutput{
-				nodeID0: validatorstest.WarpToOutput(vdrs.Validators[0]),
-				nodeID1: {
-					NodeID:    nodeID1,
-					PublicKey: vdrs.Validators[1].PublicKey,
-					Weight:    math.MaxUint64,
-				},
-			},
-			wantErr: safemath.ErrOverflow,
-		},
 		{
 			name: "nil_public_key_skipped",
 			validators: map[ids.NodeID]*GetValidatorOutput{
@@ -137,7 +132,7 @@ func TestFlattenValidatorSet(t *testing.T) {
 			},
 			want: WarpSet{
 				Validators:  []*Warp{vdrs.Validators[0]},
-				TotalWeight: vdrs.Validators[0].Weight + 5,
+				TotalWeight: new(big.Int).SetUint64(vdrs.Validators[0].Weight + 5),
 			},
 		},
 		{
```

### avalanchego/vms/platformvm/validators/manager_test.go
```diff
@@ -6,6 +6,7 @@ package validators_test
 import (
 	"bytes"
 	"math"
+	"math/big"
 	"testing"
 	"time"
 
@@ -245,13 +246,13 @@ func TestGetWarpValidatorSets(t *testing.T) {
 				NodeIDs:        []ids.NodeID{primaryStaker1.NodeID},
 			},
 		},
-		TotalWeight: genesistest.DefaultValidatorWeight*uint64(len(genesistest.DefaultNodeIDs)) + 2,
+		TotalWeight: new(big.Int).SetUint64(genesistest.DefaultValidatorWeight*uint64(len(genesistest.DefaultNodeIDs)) + 2),
 	}
 	expectedValidators := []map[ids.ID]validators.WarpSet{
 		{
 			constants.PrimaryNetworkID: {
 				Validators:  []*validators.Warp{},
-				TotalWeight: genesistest.DefaultValidatorWeight * uint64(len(genesistest.DefaultNodeIDs)),
+				TotalWeight: new(big.Int).SetUint64(genesistest.DefaultValidatorWeight * uint64(len(genesistest.DefaultNodeIDs))),
 			},
 		}, // Subnet didn't exist at genesis
 		{
@@ -264,7 +265,7 @@ func TestGetWarpValidatorSets(t *testing.T) {
 						NodeIDs:        []ids.NodeID{primaryStaker0.NodeID},
 					},
 				},
-				TotalWeight: genesistest.DefaultValidatorWeight*uint64(len(genesistest.DefaultNodeIDs)) + 1,
+				TotalWeight: new(big.Int).SetUint64(genesistest.DefaultValidatorWeight*uint64(len(genesistest.DefaultNodeIDs)) + 1),
 			},
 			subnetID: {
 				Validators: []*validators.Warp{
@@ -275,11 +276,31 @@ func TestGetWarpValidatorSets(t *testing.T) {
 						NodeIDs:        []ids.NodeID{subnetStaker0.NodeID},
 					},
 				},
-				TotalWeight: 1,
+				TotalWeight: big.NewInt(1),
 			},
 		}, // Subnet was added at height 1
 		{
 			constants.PrimaryNetworkID: expectedPrimaryNetworkWithAllValidators,
+			subnetID: {
+				Validators: []*validators.Warp{
+					{
+						PublicKey:      pk0,
+						PublicKeyBytes: pk0Bytes,
+						Weight:         1,
+						NodeIDs:        []ids.NodeID{subnetStaker0.NodeID},
+					},
+					{
+						PublicKey:      pk1,
+						PublicKeyBytes: pk1Bytes,
+						Weight:         math.MaxUint64,
+						NodeIDs:        []ids.NodeID{subnetStaker1.NodeID},
+					},
+				},
+				TotalWeight: new(big.Int).Add(
+					new(big.Int).SetUint64(math.MaxUint64),
+					big.NewInt(1),
+				),
+			},
 		}, // Subnet overflow occurred at height 1
 		{
 			constants.PrimaryNetworkID: expectedPrimaryNetworkWithAllValidators,
@@ -292,7 +313,7 @@ func TestGetWarpValidatorSets(t *testing.T) {
 						NodeIDs:        []ids.NodeID{subnetStaker0.NodeID},
 					},
 				},
-				TotalWeight: 1,
+				TotalWeight: big.NewInt(1),
 			},
 		}, // Subnet overflow was removed at height 2
 		{
@@ -318,6 +339,10 @@ func TestGetWarpValidatorSets(t *testing.T) {
 		if len(actualSubnet.Validators) == 0 {
 			actualSubnet.Validators = nil
 		}
+		// Treat a nil *big.Int and a zero *big.Int as the same
+		if actualSubnet.TotalWeight != nil && actualSubnet.TotalWeight.Sign() == 0 {
+			actualSubnet.TotalWeight = nil
+		}
 		require.Equal(expected[subnetID], actualSubnet)
 	}
 }
```

### avalanchego/vms/platformvm/warp/signature.go
```diff
@@ -91,8 +91,7 @@ func (s *BitSetSignature) Verify(
 		return err
 	}
 
-	// Because [signers] is a subset of [validators.Validators], this can never error.
-	sigWeight, _ := SumWeight(signers)
+	sigWeight := SumWeight(signers)
 
 	// Make sure the signature's weight is sufficient.
 	err = VerifyWeight(
@@ -130,22 +129,28 @@ func (s *BitSetSignature) String() string {
 }
 
 // VerifyWeight returns [nil] if [sigWeight] is at least [quorumNum]/[quorumDen]
-// of [totalWeight].
+// of [totalWeight]. A nil [sigWeight] or [totalWeight] is treated as zero.
 // If [sigWeight >= totalWeight * quorumNum / quorumDen] then return [nil]
 func VerifyWeight(
-	sigWeight uint64,
-	totalWeight uint64,
+	sigWeight *big.Int,
+	totalWeight *big.Int,
 	quorumNum uint64,
 	quorumDen uint64,
 ) error {
+	if totalWeight == nil {
+		totalWeight = new(big.Int)
+	}
+	if sigWeight == nil {
+		sigWeight = new(big.Int)
+	}
 	// Verifies that quorumNum * totalWeight <= quorumDen * sigWeight
-	scaledTotalWeight := new(big.Int).SetUint64(totalWeight)
+	scaledTotalWeight := new(big.Int).Set(totalWeight)
 	scaledTotalWeight.Mul(scaledTotalWeight, new(big.Int).SetUint64(quorumNum))
-	scaledSigWeight := new(big.Int).SetUint64(sigWeight)
+	scaledSigWeight := new(big.Int).Set(sigWeight)
 	scaledSigWeight.Mul(scaledSigWeight, new(big.Int).SetUint64(quorumDen))
 	if scaledTotalWeight.Cmp(scaledSigWeight) == 1 {
 		return fmt.Errorf(
-			"%w: %d*%d > %d*%d",
+			"%w: %d*%s > %d*%s",
 			ErrInsufficientWeight,
 			quorumNum,
 			totalWeight,
```

### avalanchego/vms/platformvm/warp/signature_test.go
```diff
@@ -5,6 +5,7 @@ package warp
 
 import (
 	"errors"
+	"math/big"
 	"strconv"
 	"testing"
 
@@ -173,9 +174,9 @@ func TestSignatureVerification(t *testing.T) {
 					testVdrs[0].vdr,
 					testVdrs[2].vdr,
 				},
-				TotalWeight: testVdrs[0].vdr.Weight +
+				TotalWeight: new(big.Int).SetUint64(testVdrs[0].vdr.Weight +
 					testVdrs[1].vdr.Weight +
-					testVdrs[2].vdr.Weight,
+					testVdrs[2].vdr.Weight),
 			},
 			quorumDen: 2,
 			signature: &BitSetSignature{
@@ -191,9 +192,9 @@ func TestSignatureVerification(t *testing.T) {
 				Validators: []*validators.Warp{
 					testVdrs[0].vdr,
 				},
-				TotalWeight: testVdrs[0].vdr.Weight +
+				TotalWeight: new(big.Int).SetUint64(testVdrs[0].vdr.Weight +
 					testVdrs[1].vdr.Weight +
-					testVdrs[2].vdr.Weight,
+					testVdrs[2].vdr.Weight),
 			},
 			quorumDen: 10000,
 			signature: &BitSetSignature{
@@ -209,9 +210,9 @@ func TestSignatureVerification(t *testing.T) {
 				Validators: []*validators.Warp{
 					testVdrs[0].vdr,
 				},
-				TotalWeight: testVdrs[0].vdr.Weight +
+				TotalWeight: new(big.Int).SetUint64(testVdrs[0].vdr.Weight +
 					testVdrs[1].vdr.Weight +
-					testVdrs[2].vdr.Weight,
+					testVdrs[2].vdr.Weight),
 			},
 			quorumDen: 10000,
 			signature: &BitSetSignature{
@@ -229,9 +230,9 @@ func TestSignatureVerification(t *testing.T) {
 					testVdrs[1].vdr,
 					testVdrs[2].vdr,
 				},
-				TotalWeight: testVdrs[0].vdr.Weight +
+				TotalWeight: new(big.Int).SetUint64(testVdrs[0].vdr.Weight +
 					testVdrs[1].vdr.Weight +
-					testVdrs[2].vdr.Weight,
+					testVdrs[2].vdr.Weight),
 			},
 			quorumDen: 2,
 			signature: &BitSetSignature{
@@ -247,9 +248,9 @@ func TestSignatureVerification(t *testing.T) {
 				Validators: []*validators.Warp{
 					testVdrs[0].vdr,
 				},
-				TotalWeight: testVdrs[0].vdr.Weight +
+				TotalWeight: new(big.Int).SetUint64(testVdrs[0].vdr.Weight +
 					testVdrs[1].vdr.Weight +
-					testVdrs[2].vdr.Weight,
+					testVdrs[2].vdr.Weight),
 			},
 			quorumDen: 2,
 			signature: &BitSetSignature{
@@ -265,9 +266,9 @@ func TestSignatureVerification(t *testing.T) {
 				Validators: []*validators.Warp{
 					testVdrs[0].vdr,
 				},
-				TotalWeight: testVdrs[0].vdr.Weight +
+				TotalWeight: new(big.Int).SetUint64(testVdrs[0].vdr.Weight +
 					testVdrs[1].vdr.Weight +
-					testVdrs[2].vdr.Weight,
+					testVdrs[2].vdr.Weight),
 			},
 			quorumDen: 10000,
 			signature: &BitSetSignature{
@@ -283,9 +284,9 @@ func TestSignatureVerification(t *testing.T) {
 				Validators: []*validators.Warp{
 					testVdrs[0].vdr,
 				},
-				TotalWeight: testVdrs[0].vdr.Weight +
+				TotalWeight: new(big.Int).SetUint64(testVdrs[0].vdr.Weight +
 					testVdrs[1].vdr.Weight +
-					testVdrs[2].vdr.Weight,
+					testVdrs[2].vdr.Weight),
 			},
 			quorumDen: 10000,
 			signature: &BitSetSignature{
@@ -302,9 +303,9 @@ func TestSignatureVerification(t *testing.T) {
 					testVdrs[0].vdr,
 					testVdrs[2].vdr,
 				},
-				TotalWeight: testVdrs[0].vdr.Weight +
+				TotalWeight: new(big.Int).SetUint64(testVdrs[0].vdr.Weight +
 					testVdrs[1].vdr.Weight +
-					testVdrs[2].vdr.Weight,
+					testVdrs[2].vdr.Weight),
 			},
 			quorumDen: 2,
 			signature: &BitSetSignature{
@@ -321,9 +322,9 @@ func TestSignatureVerification(t *testing.T) {
 					testVdrs[1].vdr,
 					testVdrs[2].vdr,
 				},
-				TotalWeight: testVdrs[0].vdr.Weight +
+				TotalWeight: new(big.Int).SetUint64(testVdrs[0].vdr.Weight +
 					testVdrs[1].vdr.Weight +
-					testVdrs[2].vdr.Weight,
+					testVdrs[2].vdr.Weight),
 			},
 			quorumDen: 2,
 			signature: &BitSetSignature{
@@ -346,6 +347,16 @@ func TestSignatureVerification(t *testing.T) {
 	}
 }
 
+func TestVerifyWeightNilArgs(t *testing.T) {
+	require := require.New(t)
+	// Both nil: 0/0 trivially satisfies the threshold (no insufficient weight).
+	require.NoError(VerifyWeight(nil, nil, 1, 1))
+	// Nil totalWeight, non-zero sigWeight: should still be fine (sig over zero total).
+	require.NoError(VerifyWeight(big.NewInt(5), nil, 1, 1))
+	// Nil sigWeight, non-zero totalWeight: insufficient.
+	require.ErrorIs(VerifyWeight(nil, big.NewInt(5), 1, 1), ErrInsufficientWeight)
+}
+
 func BenchmarkSignatureVerification(b *testing.B) {
 	unsignedMsg, err := NewUnsignedMessage(
 		constants.UnitTestID,
```
