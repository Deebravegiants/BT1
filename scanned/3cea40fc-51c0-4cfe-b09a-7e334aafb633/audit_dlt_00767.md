# [?] fix(pbts): hardening tests for overflows in `SynchronyParams` (#4816)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cometbft/cometbft
Published: 2025-01-30
Source: https://github.com/cometbft/cometbft/commit/972fa8038b57cc2152cb67144869ccd604526550
Type: security-commit

## Details
fix(pbts): hardening tests for overflows in `SynchronyParams` (#4816)

Closes #4815.

The added test units allowed us to catch overflow scenarios in some
architectures, in particular `linux/amd64`. The same is not observed in
the `arm64` architecture. Sanity checks were added to prevent this from
happening.

Further more, `MessageDelay` is now capped at 24hrs, `Precision` - 30
sec.

---------

Co-authored-by: Anton Kaliaev <anton.kalyaev@gmail.com>
Co-authored-by: mergify[bot] <37929162+mergify[bot]@users.noreply.github.com>

## Patch
### .changelog/unreleased/bug-fixes/4815-overflow-in-synchrony-params.md
```diff
@@ -0,0 +1,4 @@
+- `[consensus]` Fix overflow in synchrony parameters in `linux/amd64` architecture.
+  Cap `SynchronyParams.MessageDelay` to 24hrs.
+  Cap `SynchronyParams.Precision` to 30 sec.
+  ([\#4815](https://github.com/cometbft/cometbft/issues/4815))
```

### internal/consensus/pbts_test.go
```diff
@@ -529,6 +529,31 @@ func TestPBTSTooFarInTheFutureProposal(t *testing.T) {
 	require.Nil(t, results.height2.prevote.BlockID.Hash)
 }
 
+func TestPBTSTooFarInTheFutureProposalOverflow(t *testing.T) {
+	ctx, cancel := context.WithCancel(context.Background())
+	defer cancel()
+
+	// On purpose use a MessageDelay that has an overflow, i.e. infinite
+	// Emulates the logic for adaptive MessageDelay over rounds.
+	synchronyParams := types.DefaultSynchronyParams().InRound(256)
+	synchronyParams.Precision = 1 * time.Millisecond
+
+	// localtime < proposedBlockTime - Precision
+	cfg := pbtsTestConfiguration{
+		synchronyParams:                   synchronyParams,
+		timeoutPropose:                    50 * time.Millisecond,
+		height2ProposedBlockOffset:        100 * time.Millisecond,
+		height2ProposalTimeDeliveryOffset: 10 * time.Millisecond,
+		height4ProposedBlockOffset:        150 * time.Millisecond,
+	}
+
+	pbtsTest := newPBTSTestHarness(ctx, t, cfg)
+	results := pbtsTest.run(ctx, t)
+
+	// The proposal
+	require.Nil(t, results.height2.prevote.BlockID.Hash)
+}
+
 // TestPBTSEnableHeight tests the transition between BFT Time and PBTS.
 // The test runs multiple heights. BFT Time is used until the configured
 // PbtsEnableHeight. During some of these heights, the timestamp of votes
```

### types/params.go
```diff
@@ -31,6 +31,17 @@ const (
 	ABCIPubKeyTypeSecp256k1    = secp256k1.KeyType
 	ABCIPubKeyTypeBls12381     = bls12381.KeyType
 	ABCIPubKeyTypeSecp256k1Eth = secp256k1eth.KeyType
+
+	// MaxMessageDelay is the maximum allowed value for SynchronyParams.MessageDelay.
+	//
+	// It ensures that the SynchronyParams.MessageDelay does not overflow int64.
+	// The 24hr value was chosen based on common sense.
+	MaxMessageDelay = 24 * time.Hour
+	// MaxPrecision is the maximum allowed value for SynchronyParams.Precision.
+	//
+	// It ensures that the SynchronyParams.Precision does not overflow int64. The
+	// 30s value was chosen based on common sense.
+	MaxPrecision = 30 * time.Second
 )
 
 var ABCIPubKeyTypesToNames = map[string]string{
@@ -124,9 +135,11 @@ func featureEnabled(enableHeight int64, currentHeight int64, f string) bool {
 // These parameters are part of the Proposer-Based Timestamps (PBTS) algorithm.
 // For more information on the relationship of the synchrony parameters to
 // block timestamps validity, refer to the PBTS specification:
-// // https://github.com/cometbft/cometbft/tree/main/spec/consensus/proposer-based-timestamp
+// https://github.com/cometbft/cometbft/tree/main/spec/consensus/proposer-based-timestamp
 type SynchronyParams struct {
-	Precision    time.Duration `json:"precision,string"`
+	// Maximum allowed value: MaxPrecision.
+	Precision time.Duration `json:"precision,string"`
+	// Maximum allowed value: MaxMessageDelay.
 	MessageDelay time.Duration `json:"message_delay,string"`
 }
 
@@ -141,10 +154,20 @@ type SynchronyParams struct {
 // The goal is facilitate the progression of consensus when improper synchrony
 // parameters are set or become insufficient to preserve liveness. Refer to
 // https://github.com/cometbft/cometbft/issues/2184 for more details.
+//
+// There's a cap (MaxMessageDelay) on the MessageDelay to prevent overflow.
 func (sp SynchronyParams) InRound(round int32) SynchronyParams {
+	if round <= 0 {
+		return sp
+	}
+
+	d := time.Duration(math.Min(
+		float64(MaxMessageDelay),
+		math.Pow(1.1, float64(round))*float64(sp.MessageDelay),
+	))
 	return SynchronyParams{
 		Precision:    sp.Precision,
-		MessageDelay: time.Duration(math.Pow(1.1, float64(round)) * float64(sp.MessageDelay)),
+		MessageDelay: d,
 	}
 }
 
@@ -283,6 +306,12 @@ func (params ConsensusParams) ValidateBasic() error {
 			return fmt.Errorf("synchrony.Precision must be greater than 0. Got: %d",
 				params.Synchrony.Precision)
 		}
+		if params.Synchrony.MessageDelay > MaxMessageDelay {
+			return fmt.Errorf("synchrony.MessageDelay is too big, must be less than or equal to %v", MaxMessageDelay)
+		}
+		if params.Synchrony.Precision > MaxPrecision {
+			return fmt.Errorf("synchrony.Precision is too big, must be less than or equal to %v", MaxPrecision)
+		}
 	}
 
 	if len(params.Validator.PubKeyTypes) == 0 {
```

### types/params_test.go
```diff
@@ -2,6 +2,7 @@ package types
 
 import (
 	"bytes"
+	"math"
 	"sort"
 	"testing"
 	"time"
@@ -282,6 +283,28 @@ func TestConsensusParamsValidation(t *testing.T) {
 			}),
 			valid: false,
 		},
+		{
+			name: "messageDelay too big",
+			params: makeParams(makeParamsArgs{
+				blockBytes:   1,
+				evidenceAge:  2,
+				precision:    1 * time.Second,
+				messageDelay: time.Duration(math.MaxInt64),
+				pbtsHeight:   1,
+			}),
+			valid: false,
+		},
+		{
+			name: "precision too big",
+			params: makeParams(makeParamsArgs{
+				blockBytes:   1,
+				evidenceAge:  2,
+				precision:    time.Duration(math.MaxInt64),
+				messageDelay: 1 * time.Second,
+				pbtsHeight:   1,
+			}),
+			valid: false,
+		},
 		{
 			name: "precision 0",
 			params: makeParams(makeParamsArgs{
@@ -741,13 +764,18 @@ func durationPtr(t time.Duration) *time.Duration {
 	return &t
 }
 
+// MessageDelay should increase over rounds, while Precision remains unchanged.
+// After 10 rounds, we expect MessageDelay to increase by at least 2x and by at
+// most 10x, up to maxMessageDelay. See: https://github.com/cometbft/cometbft/issues/2184.
 func TestParamsAdaptiveSynchronyParams(t *testing.T) {
 	originalSP := DefaultSynchronyParams()
 	assert.Equal(t, originalSP, originalSP.InRound(0),
 		"SynchronyParams(0) must be equal to SynchronyParams")
 
 	lastSP := originalSP
 	for round := int32(1); round <= 10; round++ {
+		t.Logf("Round %d: %v", round, lastSP)
+
 		adaptedSP := originalSP.InRound(round)
 		assert.NotEqual(t, adaptedSP, lastSP)
 		assert.Equal(t, adaptedSP.Precision, lastSP.Precision,
@@ -756,7 +784,13 @@ func TestParamsAdaptiveSynchronyParams(t *testing.T) {
 			"MessageDelay must increase over rounds")
 
 		// It should not increase a lot per round, say more than 25%
-		maxMessageDelay := lastSP.MessageDelay + lastSP.MessageDelay*25/100
+		// Safely increase message delay, accounting for overflows.
+		var maxMessageDelay time.Duration
+		if lastSP.MessageDelay > MaxMessageDelay {
+			maxMessageDelay = MaxMessageDelay
+		} else {
+			maxMessageDelay = lastSP.MessageDelay + lastSP.MessageDelay/4
+		}
 		assert.LessOrEqual(t, adaptedSP.MessageDelay, maxMessageDelay,
 			"MessageDelay should not increase by more than 25% per round")
 
@@ -768,3 +802,50 @@ func TestParamsAdaptiveSynchronyParams(t *testing.T) {
 	assert.LessOrEqual(t, lastSP.MessageDelay, originalSP.MessageDelay*10,
 		"MessageDelay must not increase by more than 10 times after 10 rounds")
 }
+
+func TestParamsAdaptiveSynchronyParamsReachesMaximum(t *testing.T) {
+	sp := DefaultSynchronyParams()
+	lastSP := sp
+	var overflowRound int32
+	var overflowMessageDelay time.Duration
+	// Exponentially increase rounds to find when it reached max
+	for round := int32(1); round > 0; round *= 2 {
+		adaptedSP := sp.InRound(round)
+		assert.Equal(t, adaptedSP.Precision, lastSP.Precision,
+			"Precision must not change over rounds")
+
+		if adaptedSP.MessageDelay == lastSP.MessageDelay { // reached max
+			if overflowRound == 0 {
+				overflowRound = round / 2
+				overflowMessageDelay = adaptedSP.MessageDelay
+			}
+		} else if adaptedSP.MessageDelay < lastSP.MessageDelay {
+			t.Fatalf("MessageDelay should not decrease over rounds:"+
+				"it was %v (%d), not it is %v (%d)",
+				lastSP.MessageDelay, round/2,
+				adaptedSP.MessageDelay, round)
+		}
+		lastSP = adaptedSP
+	}
+
+	// Linearly search for the exact round when it reached max
+	for round := overflowRound / 2; round <= overflowRound; round++ {
+		adaptedSP := sp.InRound(round)
+		if adaptedSP.MessageDelay == overflowMessageDelay {
+			overflowRound = round
+			break
+		}
+	}
+
+	preOverflowSP := sp.InRound(overflowRound - 1)
+	overflowSP := sp.InRound(overflowRound)
+	assert.Equal(t, preOverflowSP.Precision, overflowSP.Precision,
+		"Precision must not change over rounds")
+	assert.Greater(t, overflowSP.MessageDelay, preOverflowSP.MessageDelay,
+		"MessageDelay must increase over rounds")
+
+	t.Log("Pre-max round", overflowRound-1, "MessageDelay",
+		preOverflowSP.MessageDelay)
+	t.Log("Max round", overflowRound, "MessageDelay",
+		overflowSP.MessageDelay)
+}
```

### types/proposal_test.go
```diff
@@ -223,11 +223,11 @@ func TestProposalProtoBuf(t *testing.T) {
 
 func TestProposalIsTimely(t *testing.T) {
 	timestamp, err := time.Parse(time.RFC3339, "2019-03-13T23:00:00Z")
+	require.NoError(t, err)
 	sp := SynchronyParams{
 		Precision:    time.Nanosecond,
 		MessageDelay: 2 * time.Nanosecond,
 	}
-	require.NoError(t, err)
 	testCases := []struct {
 		name                string
 		proposalHeight      int64
@@ -286,3 +286,63 @@ func TestProposalIsTimely(t *testing.T) {
 		})
 	}
 }
+
+func TestProposalIsTimelyOverflow(t *testing.T) {
+	sp := DefaultSynchronyParams()
+	lastSP := sp
+	var overflowRound int32
+	var overflowMessageDelay time.Duration
+	// Exponentially increase rounds to find when it overflows
+	for round := int32(1); round > 0; /* no overflow */ round *= 2 {
+		adaptedSP := sp.InRound(round)
+		if adaptedSP.MessageDelay == lastSP.MessageDelay { // overflow
+			overflowRound = round / 2
+			overflowMessageDelay = lastSP.MessageDelay
+			break
+		}
+		lastSP = adaptedSP
+	}
+
+	// Linearly search for the exact overflow round
+	for round := overflowRound / 2; round <= overflowRound; round++ {
+		adaptedSP := sp.InRound(round)
+		if adaptedSP.MessageDelay == overflowMessageDelay {
+			overflowRound = round
+			break
+		}
+	}
+
+	sp = sp.InRound(overflowRound)
+	t.Log("Overflow round", overflowRound, "MessageDelay", sp.MessageDelay)
+
+	timestamp, err := time.Parse(time.RFC3339, "2019-03-13T23:00:00Z")
+	require.NoError(t, err)
+
+	p := Proposal{
+		Type:      ProposalType,
+		Height:    2,
+		Timestamp: timestamp,
+		Round:     0,
+		POLRound:  -1,
+		BlockID:   testBlockID,
+		Signature: []byte{1},
+	}
+	require.NoError(t, p.ValidateBasic())
+
+	// Timestamp a bit in the future
+	proposalReceiveTime := timestamp.Add(-sp.Precision)
+	assert.True(t, p.IsTimely(proposalReceiveTime, sp))
+
+	// Timestamp far in the future is still rejected
+	proposalReceiveTime = timestamp.Add(-sp.Precision).Add(-1)
+	assert.False(t, p.IsTimely(proposalReceiveTime, sp))
+
+	// Receive time as in the future as it can get
+	proposalReceiveTime = timestamp.Add(sp.MessageDelay).Add(sp.Precision)
+	assert.True(t, p.IsTimely(proposalReceiveTime, sp))
+
+	// Timestamp as in the past as it can get
+	proposalReceiveTime = timestamp
+	p.Timestamp = timestamp.Add(-sp.MessageDelay).Add(-sp.Precision)
+	assert.True(t, p.IsTimely(proposalReceiveTime, sp))
+}
```

### types/validator_set_test.go
```diff
@@ -16,7 +16,6 @@ import (
 	"github.com/cometbft/cometbft/crypto"
 	"github.com/cometbft/cometbft/crypto/ed25519"
 	"github.com/cometbft/cometbft/crypto/secp256k1"
-	"github.com/cometbft/cometbft/crypto/secp256k1eth"
 	cmtrand "github.com/cometbft/cometbft/internal/rand"
 	cmtmath "github.com/cometbft/cometbft/libs/math"
 )
@@ -1717,7 +1716,7 @@ func TestValidatorSet_AllKeysHaveSameType(t *testing.T) {
 			sameType: false,
 		},
 		{
-			vals:     NewValidatorSet([]*Validator{NewValidator(secp256k1eth.GenPrivKey().PubKey(), 200), NewValidator(secp256k1.GenPrivKey().PubKey(), 200)}),
+			vals:     NewValidatorSet([]*Validator{NewValidator(ed25519.GenPrivKey().PubKey(), 200), NewValidator(secp256k1.GenPrivKey().PubKey(), 200)}),
 			sameType: false,
 		},
 	}
```
