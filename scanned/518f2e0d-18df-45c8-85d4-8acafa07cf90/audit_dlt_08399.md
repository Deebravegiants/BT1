# [?] Merge pull request from GHSA-95rx-m9m5-m94v

## Summary
Severity: Unknown
Chain: Cosmos
Component: cosmos/cosmos-sdk
Published: 2024-03-01
Source: https://github.com/cosmos/cosmos-sdk/commit/7155a1cd5278879dd7a747e39888239959bf9083
Type: security-commit

## Details
Merge pull request from GHSA-95rx-m9m5-m94v

* validate ExtendedCommit against LastCommit

* test cases

* lint

---------

Co-authored-by: Marko <marbar3778@yahoo.com>

## Patch
### baseapp/abci_test.go
```diff
@@ -1804,7 +1804,10 @@ func TestABCI_PrepareProposal_VoteExtensions(t *testing.T) {
 	// set up baseapp
 	prepareOpt := func(bapp *baseapp.BaseApp) {
 		bapp.SetPrepareProposal(func(ctx sdk.Context, req *abci.RequestPrepareProposal) (*abci.ResponsePrepareProposal, error) {
-			err := baseapp.ValidateVoteExtensions(ctx, valStore, req.Height, bapp.ChainID(), req.LocalLastCommit)
+			ctx = ctx.WithBlockHeight(req.Height).WithChainID(bapp.ChainID())
+			_, info := extendedCommitToLastCommit(req.LocalLastCommit)
+			ctx = ctx.WithCometInfo(info)
+			err := baseapp.ValidateVoteExtensions(ctx, valStore, req.LocalLastCommit)
 			if err != nil {
 				return nil, err
 			}
@@ -2111,7 +2114,10 @@ func TestBaseApp_VoteExtensions(t *testing.T) {
 
 		app.SetPrepareProposal(func(ctx sdk.Context, req *abci.RequestPrepareProposal) (*abci.ResponsePrepareProposal, error) {
 			txs := [][]byte{}
-			if err := baseapp.ValidateVoteExtensions(ctx, valStore, req.Height, app.ChainID(), req.LocalLastCommit); err != nil {
+			ctx = ctx.WithBlockHeight(req.Height).WithChainID(app.ChainID())
+			_, info := extendedCommitToLastCommit(req.LocalLastCommit)
+			ctx = ctx.WithCometInfo(info)
+			if err := baseapp.ValidateVoteExtensions(ctx, valStore, req.LocalLastCommit); err != nil {
 				return nil, err
 			}
 			// add all VE as txs (in a real scenario we would need to check signatures too)
```

### baseapp/abci_utils.go
```diff
@@ -4,6 +4,7 @@ import (
 	"bytes"
 	"context"
 	"fmt"
+	"slices"
 
 	"github.com/cockroachdb/errors"
 	abci "github.com/cometbft/cometbft/abci/types"
@@ -14,6 +15,7 @@ import (
 	protoio "github.com/cosmos/gogoproto/io"
 	"github.com/cosmos/gogoproto/proto"
 
+	"cosmossdk.io/core/comet"
 	sdk "github.com/cosmos/cosmos-sdk/types"
 	"github.com/cosmos/cosmos-sdk/types/mempool"
 )
@@ -40,11 +42,19 @@ type (
 func ValidateVoteExtensions(
 	ctx sdk.Context,
 	valStore ValidatorStore,
-	currentHeight int64,
-	chainID string,
 	extCommit abci.ExtendedCommitInfo,
 ) error {
+	// Get values from context
 	cp := ctx.ConsensusParams()
+	currentHeight := ctx.BlockHeight()
+	chainID := ctx.BlockHeader().ChainID
+	commitInfo := ctx.CometInfo().LastCommit
+
+	// Check that both extCommit + commit are ordered in accordance with vp/address.
+	if err := validateExtendedCommitAgainstLastCommit(extCommit, commitInfo); err != nil {
+		return err
+	}
+
 	// Start checking vote extensions only **after** the vote extensions enable
 	// height, because when `currentHeight == VoteExtensionsEnableHeight`
 	// PrepareProposal doesn't get any vote extensions in its request.
@@ -65,7 +75,6 @@ func ValidateVoteExtensions(
 		sumVP int64
 	)
 
-	cache := make(map[string]struct{})
 	for _, vote := range extCommit.Votes {
 		totalVP += vote.Validator.Power
 
@@ -90,12 +99,7 @@ func ValidateVoteExtensions(
 			return fmt.Errorf("vote extensions enabled; received empty vote extension signature at height %d", currentHeight)
 		}
 
-		// Ensure that the validator has not already submitted a vote extension.
 		valConsAddr := sdk.ConsAddress(vote.Validator.Address)
-		if _, ok := cache[valConsAddr.String()]; ok {
-			return fmt.Errorf("duplicate validator; validator %s has already submitted a vote extension", valConsAddr.String())
-		}
-		cache[valConsAddr.String()] = struct{}{}
 
 		pubKeyProto, err := valStore.GetPubKeyByConsAddr(ctx, valConsAddr)
 		if err != nil {
@@ -141,6 +145,51 @@ func ValidateVoteExtensions(
 	return nil
 }
 
+// validateExtendedCommitAgainstLastCommit validates an ExtendedCommitInfo against a LastCommit. Specifically,
+// it checks that the ExtendedCommit + LastCommit (for the same height), are consistent with each other + that
+// they are ordered correctly (by voting power) in accordance with
+// [comet](https://github.com/cometbft/cometbft/blob/4ce0277b35f31985bbf2c25d3806a184a4510010/types/validator_set.go#L784).
+func validateExtendedCommitAgainstLastCommit(ec abci.ExtendedCommitInfo, lc comet.CommitInfo) error {
+	// check that the rounds are the same
+	if ec.Round != lc.Round {
+		return fmt.Errorf("extended commit round %d does not match last commit round %d", ec.Round, lc.Round)
+	}
+
+	// check that the # of votes are the same
+	if len(ec.Votes) != len(lc.Votes) {
+		return fmt.Errorf("extended commit votes length %d does not match last commit votes length %d", len(ec.Votes), len(lc.Votes))
+	}
+
+	// check sort order of extended commit votes
+	if !slices.IsSortedFunc(ec.Votes, func(vote1, vote2 abci.ExtendedVoteInfo) int {
+		if vote1.Validator.Power == vote2.Validator.Power {
+			return bytes.Compare(vote1.Validator.Address, vote2.Validator.Address) // addresses sorted in ascending order (used to break vp conflicts)
+		}
+		return -int(vote1.Validator.Power - vote2.Validator.Power) // vp sorted in descending order
+	}) {
+		return fmt.Errorf("extended commit votes are not sorted by voting power")
+	}
+
+	addressCache := make(map[string]struct{}, len(ec.Votes))
+	// check consistency between LastCommit and ExtendedCommit
+	for i, vote := range ec.Votes {
+		// cache addresses to check for duplicates
+		if _, ok := addressCache[string(vote.Validator.Address)]; ok {
+			return fmt.Errorf("extended commit vote address %X is duplicated", vote.Validator.Address)
+		}
+		addressCache[string(vote.Validator.Address)] = struct{}{}
+
+		if !bytes.Equal(vote.Validator.Address, lc.Votes[i].Validator.Address) {
+			return fmt.Errorf("extended commit vote address %X does not match last commit vote address %X", vote.Validator.Address, lc.Votes[i].Validator.Address)
+		}
+		if vote.Validator.Power != lc.Votes[i].Validator.Power {
+			return fmt.Errorf("extended commit vote power %d does not match last commit vote power %d", vote.Validator.Power, lc.Votes[i].Validator.Power)
+		}
+	}
+
+	return nil
+}
+
 type (
 	// ProposalTxVerifier defines the interface that is implemented by BaseApp,
 	// that any custom ABCI PrepareProposal and ProcessProposal handler can use
```

### baseapp/abci_utils_test.go
```diff
@@ -2,6 +2,7 @@ package baseapp_test
 
 import (
 	"bytes"
+	"sort"
 	"testing"
 
 	abci "github.com/cometbft/cometbft/abci/types"
@@ -19,6 +20,7 @@ import (
 	"cosmossdk.io/log"
 	authtx "cosmossdk.io/x/auth/tx"
 
+	"cosmossdk.io/core/comet"
 	"github.com/cosmos/cosmos-sdk/baseapp"
 	baseapptestutil "github.com/cosmos/cosmos-sdk/baseapp/testutil"
 	"github.com/cosmos/cosmos-sdk/baseapp/testutil/mock"
@@ -64,6 +66,13 @@ func (t testValidator) toValidator(power int64) abci.Validator {
 	}
 }
 
+func (t testValidator) toSDKValidator(power int64) comet.Validator {
+	return comet.Validator{
+		Address: t.consAddr.Bytes(),
+		Power:   power,
+	}
+}
+
 type ABCIUtilsTestSuite struct {
 	suite.Suite
 
@@ -98,7 +107,9 @@ func NewABCIUtilsTestSuite(t *testing.T) *ABCIUtilsTestSuite {
 		Abci: &cmtproto.ABCIParams{
 			VoteExtensionsEnableHeight: 2,
 		},
-	})
+	}).WithBlockHeader(cmtproto.Header{
+		ChainID: chainID,
+	}).WithLogger(log.NewTestLogger(t))
 	return s
 }
 
@@ -128,6 +139,8 @@ func (s *ABCIUtilsTestSuite) TestValidateVoteExtensionsHappyPath() {
 	extSig2, err := s.vals[2].privKey.Sign(bz)
 	s.Require().NoError(err)
 
+	s.ctx = s.ctx.WithBlockHeight(3) // enable vote-extensions
+
 	llc := abci.ExtendedCommitInfo{
 		Round: 0,
 		Votes: []abci.ExtendedVoteInfo{
@@ -151,8 +164,13 @@ func (s *ABCIUtilsTestSuite) TestValidateVoteExtensionsHappyPath() {
 			},
 		},
 	}
+
+	// order + convert to last commit
+	llc, info := extendedCommitToLastCommit(llc)
+	s.ctx = s.ctx.WithCometInfo(info)
+
 	// expect-pass (votes of height 2 are included in next block)
-	s.Require().NoError(baseapp.ValidateVoteExtensions(s.ctx, s.valStore, 3, chainID, llc))
+	s.Require().NoError(baseapp.ValidateVoteExtensions(s.ctx, s.valStore, llc))
 }
 
 // check ValidateVoteExtensions works when a single node has submitted a BlockID_Absent
@@ -174,6 +192,8 @@ func (s *ABCIUtilsTestSuite) TestValidateVoteExtensionsSingleVoteAbsent() {
 	extSig2, err := s.vals[2].privKey.Sign(bz)
 	s.Require().NoError(err)
 
+	s.ctx = s.ctx.WithBlockHeight(3) // vote-extensions are enabled
+
 	llc := abci.ExtendedCommitInfo{
 		Round: 0,
 		Votes: []abci.ExtendedVoteInfo{
@@ -196,8 +216,12 @@ func (s *ABCIUtilsTestSuite) TestValidateVoteExtensionsSingleVoteAbsent() {
 			},
 		},
 	}
+
+	llc, info := extendedCommitToLastCommit(llc)
+	s.ctx = s.ctx.WithCometInfo(info)
+
 	// expect-pass (votes of height 2 are included in next block)
-	s.Require().NoError(baseapp.ValidateVoteExtensions(s.ctx, s.valStore, 3, chainID, llc))
+	s.Require().NoError(baseapp.ValidateVoteExtensions(s.ctx, s.valStore, llc))
 }
 
 // check ValidateVoteExtensions works with duplicate votes
@@ -223,15 +247,27 @@ func (s *ABCIUtilsTestSuite) TestValidateVoteExtensionsDuplicateVotes() {
 		BlockIdFlag:        cmtproto.BlockIDFlagCommit,
 	}
 
+	ve2 := abci.ExtendedVoteInfo{
+		Validator:          s.vals[0].toValidator(334), // use diff voting-power to dupe
+		VoteExtension:      ext,
+		ExtensionSignature: extSig0,
+		BlockIdFlag:        cmtproto.BlockIDFlagCommit,
+	}
+
 	llc := abci.ExtendedCommitInfo{
 		Round: 0,
 		Votes: []abci.ExtendedVoteInfo{
 			ve,
-			ve,
+			ve2,
 		},
 	}
+
+	s.ctx = s.ctx.WithBlockHeight(3) // vote-extensions are enabled
+	llc, info := extendedCommitToLastCommit(llc)
+	s.ctx = s.ctx.WithCometInfo(info)
+
 	// expect fail (duplicate votes)
-	s.Require().Error(baseapp.ValidateVoteExtensions(s.ctx, s.valStore, 3, chainID, llc))
+	s.Require().Error(baseapp.ValidateVoteExtensions(s.ctx, s.valStore, llc))
 }
 
 // check ValidateVoteExtensions works when a single node has submitted a BlockID_Nil
@@ -275,8 +311,15 @@ func (s *ABCIUtilsTestSuite) TestValidateVoteExtensionsSingleVoteNil() {
 			},
 		},
 	}
+
+	s.ctx = s.ctx.WithBlockHeight(3) // vote-extensions are enabled
+
+	// create last commit
+	llc, info := extendedCommitToLastCommit(llc)
+	s.ctx = s.ctx.WithCometInfo(info)
+
 	// expect-pass (votes of height 2 are included in next block)
-	s.Require().NoError(baseapp.ValidateVoteExtensions(s.ctx, s.valStore, 3, chainID, llc))
+	s.Require().NoError(baseapp.ValidateVoteExtensions(s.ctx, s.valStore, llc))
 }
 
 // check ValidateVoteExtensions works when two nodes have submitted a BlockID_Nil / BlockID_Absent
@@ -317,8 +360,115 @@ func (s *ABCIUtilsTestSuite) TestValidateVoteExtensionsTwoVotesNilAbsent() {
 		},
 	}
 
+	s.ctx = s.ctx.WithBlockHeight(3) // vote-extensions are enabled
+
+	// create last commit
+	llc, info := extendedCommitToLastCommit(llc)
+	s.ctx = s.ctx.WithCometInfo(info)
+
 	// expect-pass (votes of height 2 are included in next block)
-	s.Require().Error(baseapp.ValidateVoteExtensions(s.ctx, s.valStore, 3, chainID, llc))
+	s.Require().Error(baseapp.ValidateVoteExtensions(s.ctx, s.valStore, llc))
+}
+
+func (s *ABCIUtilsTestSuite) TestValidateVoteExtensionsIncorrectVotingPower() {
+	ext := []byte("vote-extension")
+	cve := cmtproto.CanonicalVoteExtension{
+		Extension: ext,
+		Height:    2,
+		Round:     int64(0),
+		ChainId:   chainID,
+	}
+
+	bz, err := marshalDelimitedFn(&cve)
+	s.Require().NoError(err)
+
+	extSig0, err := s.vals[0].privKey.Sign(bz)
+	s.Require().NoError(err)
+
+	llc := abci.ExtendedCommitInfo{
+		Round: 0,
+		Votes: []abci.ExtendedVoteInfo{
+			// validator of power >2/3 is missing, so commit-info should not be valid
+			{
+				Validator:          s.vals[0].toValidator(333),
+				BlockIdFlag:        cmtproto.BlockIDFlagCommit,
+				VoteExtension:      ext,
+				ExtensionSignature: extSig0,
+			},
+			{
+				Validator:   s.vals[1].toValidator(333),
+				BlockIdFlag: cmtproto.BlockIDFlagNil,
+			},
+			{
+				Validator:     s.vals[2].toValidator(334),
+				VoteExtension: ext,
+				BlockIdFlag:   cmtproto.BlockIDFlagAbsent,
+			},
+		},
+	}
+
+	s.ctx = s.ctx.WithBlockHeight(3) // vote-extensions are enabled
+
+	// create last commit
+	llc, info := extendedCommitToLastCommit(llc)
+	s.ctx = s.ctx.WithCometInfo(info)
+
+	// modify voting powers to differ from the last-commit
+	llc.Votes[0].Validator.Power = 335
+	llc.Votes[2].Validator.Power = 332
+
+	// expect-pass (votes of height 2 are included in next block)
+	s.Require().Error(baseapp.ValidateVoteExtensions(s.ctx, s.valStore, llc))
+}
+
+func (s *ABCIUtilsTestSuite) TestValidateVoteExtensionsIncorrecOrder() {
+	ext := []byte("vote-extension")
+	cve := cmtproto.CanonicalVoteExtension{
+		Extension: ext,
+		Height:    2,
+		Round:     int64(0),
+		ChainId:   chainID,
+	}
+
+	bz, err := marshalDelimitedFn(&cve)
+	s.Require().NoError(err)
+
+	extSig0, err := s.vals[0].privKey.Sign(bz)
+	s.Require().NoError(err)
+
+	llc := abci.ExtendedCommitInfo{
+		Round: 0,
+		Votes: []abci.ExtendedVoteInfo{
+			// validator of power >2/3 is missing, so commit-info should not be valid
+			{
+				Validator:          s.vals[0].toValidator(333),
+				BlockIdFlag:        cmtproto.BlockIDFlagCommit,
+				VoteExtension:      ext,
+				ExtensionSignature: extSig0,
+			},
+			{
+				Validator:   s.vals[1].toValidator(333),
+				BlockIdFlag: cmtproto.BlockIDFlagNil,
+			},
+			{
+				Validator:     s.vals[2].toValidator(334),
+				VoteExtension: ext,
+				BlockIdFlag:   cmtproto.BlockIDFlagAbsent,
+			},
+		},
+	}
+
+	s.ctx = s.ctx.WithBlockHeight(3) // vote-extensions are enabled
+
+	// create last commit
+	llc, info := extendedCommitToLastCommit(llc)
+	s.ctx = s.ctx.WithCometInfo(info)
+
+	// modify voting powers to differ from the last-commit
+	llc.Votes[0], llc.Votes[2] = llc.Votes[2], llc.Votes[0]
+
+	// expect-pass (votes of height 2 are included in next block)
+	s.Require().Error(baseapp.ValidateVoteExtensions(s.ctx, s.valStore, llc))
 }
 
 func (s *ABCIUtilsTestSuite) TestDefaultProposalHandler_NoOpMempoolTxSelection() {
@@ -603,3 +753,61 @@ func setTxSignatureWithSecret(t *testing.T, builder client.TxBuilder, signatures
 	)
 	require.NoError(t, err)
 }
+
+func extendedCommitToLastCommit(ec abci.ExtendedCommitInfo) (abci.ExtendedCommitInfo, comet.Info) {
+	// sort the extended commit info
+	sort.Sort(extendedVoteInfos(ec.Votes))
+
+	// convert the extended commit info to last commit info
+	lastCommit := comet.CommitInfo{
+		Round: ec.Round,
+		Votes: make([]comet.VoteInfo, len(ec.Votes)),
+	}
+
+	for i, vote := range ec.Votes {
+		lastCommit.Votes[i] = comet.VoteInfo{
+			Validator: comet.Validator{
+				Address: vote.Validator.Address,
+				Power:   vote.Validator.Power,
+			},
+		}
+	}
+
+	return ec, comet.Info{
+		LastCommit: lastCommit,
+	}
+}
+
+type voteInfos []comet.VoteInfo
+
+func (v voteInfos) Len() int {
+	return len(v)
+}
+
+func (v voteInfos) Less(i, j int) bool {
+	if v[i].Validator.Power == v[j].Validator.Power {
+		return bytes.Compare(v[i].Validator.Address, v[j].Validator.Address) == -1
+	}
+	return v[i].Validator.Power > v[j].Validator.Power
+}
+
+func (v voteInfos) Swap(i, j int) {
+	v[i], v[j] = v[j], v[i]
+}
+
+type extendedVoteInfos []abci.ExtendedVoteInfo
+
+func (v extendedVoteInfos) Len() int {
+	return len(v)
+}
+
+func (v extendedVoteInfos) Less(i, j int) bool {
+	if v[i].Validator.Power == v[j].Validator.Power {
+		return bytes.Compare(v[i].Validator.Address, v[j].Validator.Address) == -1
+	}
+	return v[i].Validator.Power > v[j].Validator.Power
+}
+
+func (v extendedVoteInfos) Swap(i, j int) {
+	v[i], v[j] = v[j], v[i]
+}
```
