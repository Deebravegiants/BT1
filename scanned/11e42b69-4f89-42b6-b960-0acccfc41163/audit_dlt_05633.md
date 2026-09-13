# [?] cl: GLOAS audit fixes — clone aliasing, PTC consistency, memory leaks, nil panics (#21248)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-05-21
Source: https://github.com/erigontech/erigon/commit/93480e4c0f2d3060efff4ca18ece948f860e3804
Type: security-commit

## Details
cl: GLOAS audit fixes — clone aliasing, PTC consistency, memory leaks, nil panics (#21248)

## Summary

- **Fix PTC consistency bug in `notifyPtcMessages`**: old code used two
different states (`s` vs `blockState`) for PTC computation, causing
validators to be mapped to wrong PTC positions. Now uses
`blockState.GetPTCFromWindow` consistently and iterates aggregation bits
directly, eliminating the intermediate `GetIndexedPayloadAttestation`
allocation and sort.
- **Fix `ExecutionPayloadEnvelope.Clone()` shallow copy**: old Clone
shared `Payload` and `ExecutionRequests` pointers (aliasing). Now
deep-copies via SSZ roundtrip. Also fixes `NewExecutionPayloadEnvelope`
to use `GloasVersion` instead of `BellatrixVersion`.
- **Add nil-panic guards** in `ProcessExecutionPayloadBid`,
`verifyExecutionPayloadBidSignature`, and
`ProcessExecutionPayloadEnvelope` for malformed SSZ inputs.
- **Cap `pendingELPayloads` at 1024** to prevent unbounded growth;
`DrainPendingELPayloads` now reuses backing array when small, releases
to GC when large.
- **Clean up `blockTimeliness` sync.Map** in `onNewFinalized` (was
growing without bound).
- **Switch gossip topic scoring from `strings.Contains` to exact `==`
match**, removing fragile ordering dependency between
`execution_payload` and `execution_payload_bid`.

No pre-GLOAS behavior changes — all fixes are in GLOAS-specific code
paths or produce identical results for pre-GLOAS topics.

## Test plan

- [x] `TestSignedExecutionPayloadEnvelopeCloneNilMessage` — nil Message
Clone
- [x] `TestGetPTCFromWindow` /
`TestGetPTCFromWindowRejectsSlotOutsideWindow` — PTC window accessor
- [x] `TestPendingELPayloadsDropOldestAtCap` /
`TestDrainPendingELPayloadsReleasesLargeBackingArray` — cap limit and
drain
- [x] `TestTopicScoreParamsExactTopicMatching` — exact topic match,
rejects suffixed names
- [x] `TestProcessExecutionPayloadEnvelopeRejectsNilEnvelope` — nil
envelope rejection
- [ ] `make lint` passes
- [ ] Existing CL tests pass (`make test-short`)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

---------

Co-authored-by: Claude Opus 4.6 <noreply@anthropic.com>

### cl/cltypes/epbs_payload.go
```diff
@@ -24,6 +24,7 @@ import (
 	"github.com/erigontech/erigon/common"
 	"github.com/erigontech/erigon/common/clonable"
 	"github.com/erigontech/erigon/common/length"
+	log "github.com/erigontech/erigon/common/log/v3"
 	"github.com/erigontech/erigon/common/ssz"
 )
 
@@ -412,7 +413,7 @@ type ExecutionPayloadEnvelope struct {
 
 func NewExecutionPayloadEnvelope(cfg *clparams.BeaconChainConfig) *ExecutionPayloadEnvelope {
 	return &ExecutionPayloadEnvelope{
-		Payload:               NewEth1Block(clparams.BellatrixVersion, cfg),
+		Payload:               NewEth1Block(clparams.GloasVersion, cfg),
 		ExecutionRequests:     NewExecutionRequests(cfg),
 		BuilderIndex:          0,
 		BeaconBlockRoot:       common.Hash{},
@@ -468,14 +469,20 @@ func (e *ExecutionPayloadEnvelope) EncodingSizeSSZ() int {
 }
 
 func (e *ExecutionPayloadEnvelope) Clone() clonable.Clonable {
-	return &ExecutionPayloadEnvelope{
-		Payload:               e.Payload,
-		ExecutionRequests:     e.ExecutionRequests,
-		BuilderIndex:          e.BuilderIndex,
-		BeaconBlockRoot:       e.BeaconBlockRoot,
-		ParentBeaconBlockRoot: e.ParentBeaconBlockRoot,
-		beaconCfg:             e.beaconCfg,
+	cloned := NewExecutionPayloadEnvelope(e.beaconCfg)
+	if e.Payload == nil {
+		return cloned
 	}
+	encoded, err := e.EncodeSSZ(nil)
+	if err != nil {
+		log.Error("ExecutionPayloadEnvelope.Clone: EncodeSSZ failed", "err", err)
+		return cloned
+	}
+	if err := cloned.DecodeSSZ(encoded, int(e.Payload.Version())); err != nil {
+		log.Error("ExecutionPayloadEnvelope.Clone: DecodeSSZ failed", "err", err)
+		return cloned
+	}
+	return cloned
 }
 
 // SignedExecutionPayloadEnvelope represents a signed execution payload envelope.
@@ -510,8 +517,12 @@ func (s *SignedExecutionPayloadEnvelope) EncodingSizeSSZ() int {
 }
 
 func (s *SignedExecutionPayloadEnvelope) Clone() clonable.Clonable {
+	var message *ExecutionPayloadEnvelope
+	if s.Message != nil {
+		message = s.Message.Clone().(*ExecutionPayloadEnvelope)
+	}
 	return &SignedExecutionPayloadEnvelope{
-		Message:   s.Message.Clone().(*ExecutionPayloadEnvelope),
+		Message:   message,
 		Signature: s.Signature,
 		beaconCfg: s.beaconCfg,
 	}
```

### cl/cltypes/epbs_payload_test.go
```diff
@@ -0,0 +1,18 @@
+package cltypes
+
+import (
+	"testing"
+
+	"github.com/erigontech/erigon/common"
+	"github.com/stretchr/testify/require"
+)
+
+func TestSignedExecutionPayloadEnvelopeCloneNilMessage(t *testing.T) {
+	envelope := &SignedExecutionPayloadEnvelope{
+		Signature: common.Bytes96{1, 2, 3},
+	}
+
+	cloned := envelope.Clone().(*SignedExecutionPayloadEnvelope)
+	require.Nil(t, cloned.Message)
+	require.Equal(t, envelope.Signature, cloned.Signature)
+}
```

### cl/phase1/core/state/cache_accessors.go
```diff
@@ -517,7 +517,7 @@ func (b *CachingBeaconState) GetValidatorActivationChurnLimit() uint64 {
 // ptcWindow's 3-epoch range (e.g. state advanced far past the parent).
 func (b *CachingBeaconState) GetPTC(slot uint64) ([]uint64, error) {
 	if b.Version() >= clparams.GloasVersion {
-		ptc, err := b.getPTCFromWindow(slot)
+		ptc, err := b.GetPTCFromWindow(slot)
 		if err == nil {
 			return ptc, nil
 		}
@@ -526,14 +526,14 @@ func (b *CachingBeaconState) GetPTC(slot uint64) ([]uint64, error) {
 	return b.ComputePTC(slot)
 }
 
-// getPTCFromWindow reads the PTC for a given slot from the ptc_window state field.
+// GetPTCFromWindow reads the PTC for a given slot from the ptc_window state field.
 // Index calculation follows the spec's get_ptc:
 //   - previous epoch: index = slot % SLOTS_PER_EPOCH
 //   - current/lookahead: index = (epoch - state_epoch + 1) * SLOTS_PER_EPOCH + slot % SLOTS_PER_EPOCH
 //
 // The ptc_window only covers [stateEpoch-1, stateEpoch, stateEpoch+1]. Slots
 // outside this range return an error.
-func (b *CachingBeaconState) getPTCFromWindow(slot uint64) ([]uint64, error) {
+func (b *CachingBeaconState) GetPTCFromWindow(slot uint64) ([]uint64, error) {
 	cfg := b.BeaconConfig()
 	epoch := GetEpochAtSlot(cfg, slot)
 	stateEpoch := b.Slot() / cfg.SlotsPerEpoch
@@ -557,8 +557,11 @@ func (b *CachingBeaconState) getPTCFromWindow(slot uint64) ([]uint64, error) {
 	}
 
 	ptcWindow := b.GetPtcWindow()
+	if ptcWindow == nil {
+		return nil, errors.New("GetPTCFromWindow: ptcWindow is nil")
+	}
 	if index >= uint64(ptcWindow.Length()) {
-		return nil, fmt.Errorf("getPTCFromWindow: index %d out of range (window size %d)", index, ptcWindow.Length())
+		return nil, fmt.Errorf("GetPTCFromWindow: index %d out of range (window size %d)", index, ptcWindow.Length())
 	}
 
 	vec := ptcWindow.Get(int(index))
```

### cl/phase1/forkchoice/forkchoice.go
```diff
@@ -22,6 +22,8 @@ import (
 	"sync"
 	"sync/atomic"
 
+	"github.com/erigontech/erigon/common/log/v3"
+
 	"github.com/erigontech/erigon/cl/beacon/beaconevents"
 	"github.com/erigontech/erigon/cl/beacon/synced_data"
 	"github.com/erigontech/erigon/cl/clparams"
@@ -58,9 +60,11 @@ type ForkNode struct {
 }
 
 const (
-	checkpointsPerCache = 1024
-	allowedCachedStates = 8
-	queueCacheSize      = 128
+	checkpointsPerCache        = 1024
+	allowedCachedStates        = 8
+	queueCacheSize             = 128
+	pendingELPayloadsShrinkCap = 256 // drain releases the backing array when cap exceeds this
+	maxPendingELPayloads       = 1024
 )
 
 type randaoDelta struct {
@@ -951,6 +955,12 @@ func (f *ForkChoiceStore) GetProposerLookahead(slot uint64) (solid.Uint64VectorS
 func (f *ForkChoiceStore) addPendingELPayload(block *cltypes.SignedBeaconBlock, envelope *cltypes.SignedExecutionPayloadEnvelope) {
 	f.pendingELPayloadsMu.Lock()
 	defer f.pendingELPayloadsMu.Unlock()
+	if len(f.pendingELPayloads) >= maxPendingELPayloads {
+		log.Warn("addPendingELPayload: dropping oldest pending EL payload", "queueLen", len(f.pendingELPayloads))
+		copy(f.pendingELPayloads, f.pendingELPayloads[1:])
+		f.pendingELPayloads[len(f.pendingELPayloads)-1] = PendingELPayload{}
+		f.pendingELPayloads = f.pendingELPayloads[:len(f.pendingELPayloads)-1]
+	}
 	f.pendingELPayloads = append(f.pendingELPayloads, PendingELPayload{
 		Block:    block,
 		Envelope: envelope,
@@ -962,7 +972,17 @@ func (f *ForkChoiceStore) addPendingELPayload(block *cltypes.SignedBeaconBlock,
 func (f *ForkChoiceStore) DrainPendingELPayloads() []PendingELPayload {
 	f.pendingELPayloadsMu.Lock()
 	defer f.pendingELPayloadsMu.Unlock()
-	payloads := f.pendingELPayloads
-	f.pendingELPayloads = nil
-	return payloads
+	if len(f.pendingELPayloads) == 0 {
+		return nil
+	}
+	if cap(f.pendingELPayloads) > pendingELPayloadsShrinkCap {
+		result := f.pendingELPayloads
+		f.pendingELPayloads = nil
+		return result
+	}
+	result := make([]PendingELPayload, len(f.pendingELPayloads))
+	copy(result, f.pendingELPayloads)
+	clear(f.pendingELPayloads)
+	f.pendingELPayloads = f.pendingELPayloads[:0]
+	return result
 }
```

### cl/phase1/forkchoice/payload_vote.go
```diff
@@ -48,11 +48,10 @@ func (f *ForkChoiceStore) notifyPtcMessages(
 		return
 	}
 
-	// Pre-compute state and PTC per unique blockRoot to avoid redundant GetState + GetPTC
-	// calls for every attesting validator (PtcSize can be 512).
+	// Pre-compute PTC per unique blockRoot to avoid redundant state lookups
+	// for every attesting validator (PtcSize can be 512).
 	type cachedPTC struct {
-		state *state.CachingBeaconState
-		ptc   []uint64
+		ptc []uint64
 	}
 	ptcCache := make(map[common.Hash]*cachedPTC)
 
@@ -70,50 +69,36 @@ func (f *ForkChoiceStore) notifyPtcMessages(
 			if err != nil || blockState == nil {
 				continue
 			}
-			ptc, err := blockState.GetPTC(data.Slot)
-			if err != nil {
+			if data.Slot != blockState.Slot() {
 				continue
 			}
-			if data.Slot != blockState.Slot() {
+			ptc, err := blockState.GetPTCFromWindow(data.Slot)
+			if err != nil {
 				continue
 			}
-			cached = &cachedPTC{state: blockState, ptc: ptc}
+			cached = &cachedPTC{ptc: ptc}
 			ptcCache[blockRoot] = cached
 		}
 
-		indexedPayloadAttestation, err := s.GetIndexedPayloadAttestation(payloadAttestation)
-		if err != nil {
+		if payloadAttestation.AggregationBits == nil {
 			continue
 		}
 
-		attestingIndices := indexedPayloadAttestation.AttestingIndices
-		for j := 0; j < attestingIndices.Length(); j++ {
-			idx := attestingIndices.Get(j)
-			f.applyPayloadAttestationVote(idx, data, blockRoot, cached.ptc)
+		for j := range cached.ptc {
+			if payloadAttestation.AggregationBits.GetBitAt(j) {
+				f.applyPayloadAttestationVote(j, data, blockRoot)
+			}
 		}
 	}
 }
 
-// applyPayloadAttestationVote updates PTC vote tracking for a single validator.
-// Used by notifyPtcMessages with pre-computed PTC to avoid redundant GetState/GetPTC calls.
+// applyPayloadAttestationVote updates PTC vote tracking for a single PTC position.
+// ptcIndex is the position in the PTC (the aggregation bit index).
 func (f *ForkChoiceStore) applyPayloadAttestationVote(
-	validatorIndex uint64,
+	ptcIndex int,
 	data *cltypes.PayloadAttestationData,
 	blockRoot common.Hash,
-	ptc []uint64,
 ) {
-	// Find the validator's position in the PTC
-	ptcIndex := -1
-	for i, idx := range ptc {
-		if idx == validatorIndex {
-			ptcIndex = i
-			break
-		}
-	}
-	if ptcIndex == -1 {
-		return
-	}
-
 	// Atomically update PTC vote arrays under mutex to prevent concurrent
 	// Load→modify→Store from losing votes. See also OnPayloadAttestationMessage.
 	f.ptcVoteMu.Lock()
```

### cl/phase1/forkchoice/payload_vote_test.go
```diff
@@ -0,0 +1,46 @@
+package forkchoice
+
+import (
+	"testing"
+
+	"github.com/erigontech/erigon/cl/clparams"
+	"github.com/erigontech/erigon/cl/cltypes/solid"
+	state2 "github.com/erigontech/erigon/cl/phase1/core/state"
+	"github.com/stretchr/testify/require"
+)
+
+func TestGetPTCFromWindow(t *testing.T) {
+	cfg := &clparams.MainnetBeaconConfig
+	s := state2.New(cfg)
+	s.SetVersion(clparams.GloasVersion)
+
+	slotsPerEpoch := cfg.SlotsPerEpoch
+	slot := 2*slotsPerEpoch + 5
+	s.SetSlot(slot)
+
+	ptcWindow := solid.NewUint64VectorOfVectors(int(3*slotsPerEpoch), 4)
+	windowIndex := slotsPerEpoch + slot%slotsPerEpoch
+	vec := ptcWindow.Get(int(windowIndex))
+	for i := 0; i < vec.Length(); i++ {
+		vec.Set(i, uint64(10+i))
+	}
+	s.SetPtcWindow(ptcWindow)
+
+	ptc, err := s.GetPTCFromWindow(slot)
+	require.NoError(t, err)
+	require.Equal(t, []uint64{10, 11, 12, 13}, ptc)
+
+	ptc[0] = 99
+	require.Equal(t, uint64(10), ptcWindow.Get(int(windowIndex)).Get(0))
+}
+
+func TestGetPTCFromWindowRejectsSlotOutsideWindow(t *testing.T) {
+	cfg := &clparams.MainnetBeaconConfig
+	s := state2.New(cfg)
+	s.SetVersion(clparams.GloasVersion)
+	s.SetSlot(2*cfg.SlotsPerEpoch + 5)
+	s.SetPtcWindow(solid.NewUint64VectorOfVectors(int(3*cfg.SlotsPerEpoch), 4))
+
+	_, err := s.GetPTCFromWindow(0)
+	require.Error(t, err)
+}
```

### cl/phase1/forkchoice/pending_el_payload_test.go
```diff
@@ -0,0 +1,35 @@
+package forkchoice
+
+import (
+	"testing"
+
+	"github.com/erigontech/erigon/cl/cltypes"
+	"github.com/stretchr/testify/require"
+)
+
+func TestPendingELPayloadsDropOldestAtCap(t *testing.T) {
+	f := &ForkChoiceStore{}
+
+	for i := 0; i < maxPendingELPayloads+1; i++ {
+		f.addPendingELPayload(&cltypes.SignedBeaconBlock{
+			Block: &cltypes.BeaconBlock{Slot: uint64(i)},
+		}, nil)
+	}
+
+	payloads := f.DrainPendingELPayloads()
+	require.Len(t, payloads, maxPendingELPayloads)
+	require.Equal(t, uint64(1), payloads[0].Block.Block.Slot)
+	require.Equal(t, uint64(maxPendingELPayloads), payloads[len(payloads)-1].Block.Block.Slot)
+}
+
+func TestDrainPendingELPayloadsReleasesLargeBackingArray(t *testing.T) {
+	f := &ForkChoiceStore{}
+
+	for i := 0; i < pendingELPayloadsShrinkCap+1; i++ {
+		f.addPendingELPayload(&cltypes.SignedBeaconBlock{}, nil)
+	}
+
+	payloads := f.DrainPendingELPayloads()
+	require.Len(t, payloads, pendingELPayloadsShrinkCap+1)
+	require.Nil(t, f.pendingELPayloads)
+}
```

### cl/phase1/forkchoice/utils.go
```diff
@@ -96,6 +96,15 @@ func (f *ForkChoiceStore) onNewFinalized(newFinalized solid.Checkpoint) {
 		}
 		return true
 	})
+	// Clean up block timeliness entries for finalized blocks.
+	f.blockTimeliness.Range(func(k, v any) bool {
+		blockRoot := k.(common.Hash)
+		header, has := f.forkGraph.GetHeader(blockRoot)
+		if !has || header.Slot <= finalizedSlot {
+			f.blockTimeliness.Delete(k)
+		}
+		return true
+	})
 	// Clean up GLOAS-specific payload votes for finalized blocks.
 	// Note: envelope files are cleaned up in forkGraph.Prune().
 	if newFinalized.Epoch >= f.beaconCfg.GloasForkEpoch {
```

### cl/phase1/network/gossip/score.go
```diff
@@ -3,7 +3,6 @@ package gossip
 import (
 	"fmt"
 	"math"
-	"strings"
 	"time"
 
 	"github.com/erigontech/erigon/cl/gossip"
@@ -63,24 +62,22 @@ const (
 
 func (g *GossipManager) topicScoreParams(topic string) *pubsub.TopicScoreParams {
 	switch {
-	case strings.Contains(topic, gossip.TopicNameBeaconBlock) || gossip.IsTopicBlobSidecar(topic):
+	case topic == gossip.TopicNameBeaconBlock || gossip.IsTopicBlobSidecar(topic):
 		return g.defaultBlockTopicParams()
-	// execution_payload_bid must be checked before execution_payload (substring match).
-	case strings.Contains(topic, gossip.TopicNameExecutionPayloadBid):
-		return g.defaultExecutionPayloadBidTopicParams()
-	case strings.Contains(topic, gossip.TopicNameExecutionPayload):
+	case topic == gossip.TopicNameExecutionPayload:
 		return g.defaultExecutionPayloadTopicParams()
-	case strings.Contains(topic, gossip.TopicNamePayloadAttestation):
+	case topic == gossip.TopicNameExecutionPayloadBid:
+		return g.defaultExecutionPayloadBidTopicParams()
+	case topic == gossip.TopicNamePayloadAttestation:
 		return g.defaultPayloadAttestationTopicParams()
-	case strings.Contains(topic, gossip.TopicNameProposerPreferences):
+	case topic == gossip.TopicNameProposerPreferences:
 		return g.defaultProposerPreferencesTopicParams()
-	case strings.Contains(topic, gossip.TopicNameVoluntaryExit):
+	case topic == gossip.TopicNameVoluntaryExit:
 		return g.defaultVoluntaryExitTopicParams()
 	case gossip.IsTopicBeaconAttestation(topic):
 		return g.defaultAggregateSubnetTopicParams()
 	case gossip.IsTopicSyncCommittee(topic):
 		return g.defaultSyncSubnetTopicParams(g.activeIndicies)
-
 	default:
 		return nil
 	}
```

### cl/phase1/network/gossip/score_test.go
```diff
@@ -0,0 +1,23 @@
+package gossip
+
+import (
+	"testing"
+
+	"github.com/erigontech/erigon/cl/clparams"
+	gossipnames "github.com/erigontech/erigon/cl/gossip"
+	"github.com/stretchr/testify/require"
+)
+
+func TestTopicScoreParamsExactTopicMatching(t *testing.T) {
+	g := &GossipManager{
+		beaconConfig: &clparams.BeaconChainConfig{
+			SlotsPerEpoch:  32,
+			SecondsPerSlot: 12,
+		},
+	}
+
+	require.Equal(t, executionPayloadWeight, g.topicScoreParams(gossipnames.TopicNameExecutionPayload).TopicWeight)
+	require.Equal(t, executionPayloadBidWeight, g.topicScoreParams(gossipnames.TopicNameExecutionPayloadBid).TopicWeight)
+	require.Nil(t, g.topicScoreParams(gossipnames.TopicNameExecutionPayload+"_extra"))
+	require.Nil(t, g.topicScoreParams(gossipnames.TopicNameBeaconBlock+"_extra"))
+}
```

### cl/transition/impl/eth2/operations.go
```diff
@@ -513,6 +513,9 @@ func updateNextWithdrawalBuilderIndex(s abstract.BeaconState, processedBuildersS
 // [New in Gloas:EIP7732]
 func (I *impl) ProcessExecutionPayloadBid(s abstract.BeaconState, block cltypes.GenericBeaconBlock) error {
 	signedBid := block.GetBody().GetSignedExecutionPayloadBid()
+	if signedBid == nil || signedBid.Message == nil {
+		return errors.New("processExecutionPayloadBid: signed bid or bid message is nil")
+	}
 	bid := signedBid.Message
 	builderIndex := bid.BuilderIndex
 	amount := bid.Value
@@ -727,6 +730,9 @@ func (I *impl) ProcessParentExecutionPayload(s abstract.BeaconState, block cltyp
 // [New in Gloas:EIP7732]
 func verifyExecutionPayloadBidSignature(s abstract.BeaconState, signedBid *cltypes.SignedExecutionPayloadBid) (bool, error) {
 	builders := s.GetBuilders()
+	if builders == nil || signedBid.Message.BuilderIndex >= uint64(builders.Len()) {
+		return false, fmt.Errorf("builder index %d out of range", signedBid.Message.BuilderIndex)
+	}
 	builder := builders.Get(int(signedBid.Message.BuilderIndex))
 
 	domain, err := s.GetDomain(s.BeaconConfig().DomainBeaconBuilder, state.Epoch(s))
@@ -746,8 +752,14 @@ func verifyExecutionPayloadBidSignature(s abstract.BeaconState, signedBid *cltyp
 // ProcessExecutionPayloadEnvelope processes the execution payload envelope for the Gloas fork.
 // [New in Gloas:EIP7732]
 func (I *impl) ProcessExecutionPayloadEnvelope(s abstract.BeaconState, signedEnvelope *cltypes.SignedExecutionPayloadEnvelope) error {
+	if signedEnvelope == nil || signedEnvelope.Message == nil {
+		return errors.New("ProcessExecutionPayloadEnvelope: signed envelope or envelope message is nil")
+	}
 	envelope := signedEnvelope.Message
 	payload := envelope.Payload
+	if payload == nil {
+		return errors.New("ProcessExecutionPayloadEnvelope: envelope has nil payload")
+	}
 
 	// Verify signature
 	if I.FullValidation {
@@ -801,6 +813,9 @@ func (I *impl) ProcessExecutionPayloadEnvelope(s abstract.BeaconState, signedEnv
 
 	// Verify consistency with the committed bid
 	committedBid := s.GetLatestExecutionPayloadBid()
+	if committedBid == nil {
+		return errors.New("ProcessExecutionPayloadEnvelope: state has no latest execution payload bid")
+	}
 	if envelope.BuilderIndex != committedBid.BuilderIndex {
 		return fmt.Errorf("ProcessExecutionPayloadEnvelope: builder_index %d != committed bid builder_index %d", envelope.BuilderIndex, committedBid.BuilderIndex)
 	}
@@ -842,7 +857,13 @@ func (I *impl) ProcessExecutionPayloadEnvelope(s abstract.BeaconState, signedEnv
 
 	// Verify consistency with expected withdrawals
 	payloadWithdrawals := payload.Withdrawals
+	if payloadWithdrawals == nil {
+		return errors.New("ProcessExecutionPayloadEnvelope: payload has nil withdrawals")
+	}
 	expectedWithdrawals := s.GetPayloadExpectedWithdrawals()
+	if expectedWithdrawals == nil {
+		return errors.New("ProcessExecutionPayloadEnvelope: state has nil expected withdrawals")
+	}
 	payloadWithdrawalsRoot, err := payloadWithdrawals.HashSSZ()
 	if err != nil {
 		return fmt.Errorf("ProcessExecutionPayloadEnvelope: failed to hash payload withdrawals: %w", err)
```

### cl/transition/impl/eth2/operations_gloas_test.go
```diff
@@ -0,0 +1,22 @@
+package eth2_test
+
+import (
+	"testing"
+
+	"github.com/erigontech/erigon/cl/clparams"
+	"github.com/erigontech/erigon/cl/cltypes"
+	"github.com/erigontech/erigon/cl/phase1/core/state"
+	"github.com/erigontech/erigon/cl/transition/impl/eth2"
+	"github.com/stretchr/testify/require"
+)
+
+func TestProcessExecutionPayloadEnvelopeRejectsNilEnvelope(t *testing.T) {
+	s := state.New(&clparams.MainnetBeaconConfig)
+	machine := &eth2.Impl{}
+
+	require.Error(t, machine.ProcessExecutionPayloadEnvelope(s, nil))
+	require.Error(t, machine.ProcessExecutionPayloadEnvelope(s, &cltypes.SignedExecutionPayloadEnvelope{}))
+	require.Error(t, machine.ProcessExecutionPayloadEnvelope(s, &cltypes.SignedExecutionPayloadEnvelope{
+		Message: &cltypes.ExecutionPayloadEnvelope{},
+	}))
+}
```
