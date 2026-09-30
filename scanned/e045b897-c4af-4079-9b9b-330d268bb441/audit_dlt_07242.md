# [?] Merge pull request from GHSA-95rx-m9m5-m94v

## Summary
Severity: Unknown
Chain: Cosmos
Component: cosmos/cosmos-sdk
Published: 2024-03-11
Source: https://github.com/cosmos/cosmos-sdk/commit/4467110df40797ebe916c23ebfd45c9ee7583897
Type: security-commit

## Details
Merge pull request from GHSA-95rx-m9m5-m94v

* validate ExtendedCommit against LastCommit

test cases

* account for core.comet types

* logging

* linting

* cherry-pick staking fix

* nits

* linting fix

* run tests

---------

Co-authored-by: Marko <marbar3778@yahoo.com>
Co-authored-by: Marko Baricevic <markobaricevic3778@gmail.com>

## Patch
### baseapp/abci_test.go
```diff
@@ -1790,7 +1790,10 @@ func TestABCI_PrepareProposal_VoteExtensions(t *testing.T) {
 	// set up baseapp
 	prepareOpt := func(bapp *baseapp.BaseApp) {
 		bapp.SetPrepareProposal(func(ctx sdk.Context, req *abci.RequestPrepareProposal) (*abci.ResponsePrepareProposal, error) {
-			err := baseapp.ValidateVoteExtensions(ctx, valStore, req.Height, bapp.ChainID(), req.LocalLastCommit)
+			ctx = ctx.WithBlockHeight(req.Height).WithChainID(bapp.ChainID())
+			_, info := extendedCommitToLastCommit(req.LocalLastCommit)
+			ctx = ctx.WithCometInfo(info)
+			err := baseapp.ValidateVoteExtensions(ctx, valStore, 0, "", req.LocalLastCommit)
 			if err != nil {
 				return nil, err
 			}
@@ -2097,7 +2100,10 @@ func TestBaseApp_VoteExtensions(t *testing.T) {
 
 		app.SetPrepareProposal(func(ctx sdk.Context, req *abci.RequestPrepareProposal) (*abci.ResponsePrepareProposal, error) {
 			txs := [][]byte{}
-			if err := baseapp.ValidateVoteExtensions(ctx, valStore, req.Height, app.ChainID(), req.LocalLastCommit); err != nil {
+			ctx = ctx.WithBlockHeight(req.Height).WithChainID(app.ChainID())
+			_, info := extendedCommitToLastCommit(req.LocalLastCommit)
+			ctx = ctx.WithCometInfo(info)
+			if err := baseapp.ValidateVoteExtensions(ctx, valStore, 0, "", req.LocalLastCommit); err != nil {
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
@@ -13,6 +14,8 @@ import (
 	protoio "github.com/cosmos/gogoproto/io"
 	"github.com/cosmos/gogoproto/proto"
 
+	"cosmossdk.io/core/comet"
+
 	sdk "github.com/cosmos/cosmos-sdk/types"
 	"github.com/cosmos/cosmos-sdk/types/mempool"
 )
@@ -39,11 +42,21 @@ type (
 func ValidateVoteExtensions(
 	ctx sdk.Context,
 	valStore ValidatorStore,
-	currentHeight int64,
-	chainID string,
+	_ int64,
+	_ string,
 	extCommit abci.ExtendedCommitInfo,
 ) error {
+	// Get values from context
 	cp := ctx.ConsensusParams()
+	currentHeight := ctx.HeaderInfo().Height
+	chainID := ctx.HeaderInfo().ChainID
+	commitInfo := ctx.CometInfo().GetLastCommit()
+
+	// Check that both extCommit + commit are ordered in accordance with vp/address.
+	if err := validateExtendedCommitAgainstLastCommit(extCommit, commitInfo); err != nil {
+		return err
+	}
+
 	// Start checking vote extensions only **after** the vote extensions enable
 	// height, because when `currentHeight == VoteExtensionsEnableHeight`
 	// PrepareProposal doesn't get any vote extensions in its request.
@@ -64,7 +77,6 @@ func ValidateVoteExtensions(
 		sumVP int64
 	)
 
-	cache := make(map[string]struct{})
 	for _, vote := range extCommit.Votes {
 		totalVP += vote.Validator.Power
 
@@ -89,12 +101,7 @@ func ValidateVoteExtensions(
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
@@ -140,6 +147,51 @@ func ValidateVoteExtensions(
 	return nil
 }
 
+// validateExtendedCommitAgainstLastCommit validates an ExtendedCommitInfo against a LastCommit. Specifically,
+// it checks that the ExtendedCommit + LastCommit (for the same height), are consistent with each other + that
+// they are ordered correctly (by voting power) in accordance with
+// [comet](https://github.com/cometbft/cometbft/blob/4ce0277b35f31985bbf2c25d3806a184a4510010/types/validator_set.go#L784).
+func validateExtendedCommitAgainstLastCommit(ec abci.ExtendedCommitInfo, lc comet.CommitInfo) error {
+	// check that the rounds are the same
+	if ec.Round != lc.Round() {
+		return fmt.Errorf("extended commit round %d does not match last commit round %d", ec.Round, lc.Round())
+	}
+
+	// check that the # of votes are the same
+	if len(ec.Votes) != lc.Votes().Len() {
+		return fmt.Errorf("extended commit votes length %d does not match last commit votes length %d", len(ec.Votes), lc.Votes().Len())
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
+	// check that consistency between LastCommit and ExtendedCommit
+	for i, vote := range ec.Votes {
+		// cache addresses to check for duplicates
+		if _, ok := addressCache[string(vote.Validator.Address)]; ok {
+			return fmt.Errorf("extended commit vote address %X is duplicated", vote.Validator.Address)
+		}
+		addressCache[string(vote.Validator.Address)] = struct{}{}
+
+		if !bytes.Equal(vote.Validator.Address, lc.Votes().Get(i).Validator().Address()) {
+			return fmt.Errorf("extended commit vote address %X does not match last commit vote address %X", vote.Validator.Address, lc.Votes().Get(i).Validator().Address())
+		}
+		if vote.Validator.Power != lc.Votes().Get(i).Validator().Power() {
+			return fmt.Errorf("extended commit vote power %d does not match last commit vote power %d", vote.Validator.Power, lc.Votes().Get(i).Validator().Power())
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
@@ -16,6 +17,8 @@ import (
 	"github.com/stretchr/testify/require"
 	"github.com/stretchr/testify/suite"
 
+	"cosmossdk.io/core/comet"
+	"cosmossdk.io/core/header"
 	"cosmossdk.io/log"
 
 	"github.com/cosmos/cosmos-sdk/baseapp"
@@ -98,7 +101,9 @@ func NewABCIUtilsTestSuite(t *testing.T) *ABCIUtilsTestSuite {
 		Abci: &cmtproto.ABCIParams{
 			VoteExtensionsEnableHeight: 2,
 		},
-	})
+	}).WithBlockHeader(cmtproto.Header{
+		ChainID: chainID,
+	}).WithLogger(log.NewTestLogger(t))
 	return s
 }
 
@@ -128,6 +133,8 @@ func (s *ABCIUtilsTestSuite) TestValidateVoteExtensionsHappyPath() {
 	extSig2, err := s.vals[2].privKey.Sign(bz)
 	s.Require().NoError(err)
 
+	s.ctx = s.ctx.WithBlockHeight(3).WithHeaderInfo(header.Info{Height: 3, ChainID: chainID}) // enable vote-extensions
+
 	llc := abci.ExtendedCommitInfo{
 		Round: 0,
 		Votes: []abci.ExtendedVoteInfo{
@@ -151,8 +158,13 @@ func (s *ABCIUtilsTestSuite) TestValidateVoteExtensionsHappyPath() {
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
+	s.Require().NoError(baseapp.ValidateVoteExtensions(s.ctx, s.valStore, 0, "", llc))
 }
 
 // check ValidateVoteExtensions works when a single node has submitted a BlockID_Absent
@@ -174,6 +186,8 @@ func (s *ABCIUtilsTestSuite) TestValidateVoteExtensionsSingleVoteAbsent() {
 	extSig2, err := s.vals[2].privKey.Sign(bz)
 	s.Require().NoError(err)
 
+	s.ctx = s.ctx.WithBlockHeight(3).WithHeaderInfo(header.Info{Height: 3, ChainID: chainID}) // vote-extensions are enabled
+
 	llc := abci.ExtendedCommitInfo{
 		Round: 0,
 		Votes: []abci.ExtendedVoteInfo{
@@ -196,8 +210,12 @@ func (s *ABCIUtilsTestSuite) TestValidateVoteExtensionsSingleVoteAbsent() {
 			},
 		},
 	}
+
+	llc, info := extendedCommitToLastCommit(llc)
+	s.ctx = s.ctx.WithCometInfo(info)
+
 	// expect-pass (votes of height 2 are included in next block)
-	s.Require().NoError(baseapp.ValidateVoteExtensions(s.ctx, s.valStore, 3, chainID, llc))
+	s.Require().NoError(baseapp.ValidateVoteExtensions(s.ctx, s.valStore, 0, "", llc))
 }
 
 // check ValidateVoteExtensions works with duplicate votes
@@ -223,15 +241,27 @@ func (s *ABCIUtilsTestSuite) TestValidateVoteExtensionsDuplicateVotes() {
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
+	s.ctx = s.ctx.WithBlockHeight(3).WithHeaderInfo(header.Info{Height: 3, ChainID: chainID}) // vote-extensions are enabled
+	llc, info := extendedCommitToLastCommit(llc)
+	s.ctx = s.ctx.WithCometInfo(info)
+
 	// expect fail (duplicate votes)
-	s.Require().Error(baseapp.ValidateVoteExtensions(s.ctx, s.valStore, 3, chainID, llc))
+	s.Require().Error(baseapp.ValidateVoteExtensions(s.ctx, s.valStore, 0, "", llc))
 }
 
 // check ValidateVoteExtensions works when a single node has submitted a BlockID_Nil
@@ -275,8 +305,15 @@ func (s *ABCIUtilsTestSuite) TestValidateVoteExtensionsSingleVoteNil() {
 			},
 		},
 	}
+
+	s.ctx = s.ctx.WithBlockHeight(3).WithHeaderInfo(header.Info{Height: 3, ChainID: chainID}) // vote-extensions are enabled
+
+	// create last commit
+	llc, info := extendedCommitToLastCommit(llc)
+	s.ctx = s.ctx.WithCometInfo(info)
+
 	// expect-pass (votes of height 2 are included in next block)
-	s.Require().NoError(baseapp.ValidateVoteExtensions(s.ctx, s.valStore, 3, chainID, llc))
+	s.Require().NoError(baseapp.ValidateVoteExtensions(s.ctx, s.valStore, 0, "", llc))
 }
 
 // check ValidateVoteExtensions works when two nodes have submitted a BlockID_Nil / BlockID_Absent
@@ -317,8 +354,115 @@ func (s *ABCIUtilsTestSuite) TestValidateVoteExtensionsTwoVotesNilAbsent() {
 		},
 	}
 
+	s.ctx = s.ctx.WithBlockHeight(3).WithHeaderInfo(header.Info{Height: 3, ChainID: chainID}) // vote-extensions are enabled
+
+	// create last commit
+	llc, info := extendedCommitToLastCommit(llc)
+	s.ctx = s.ctx.WithCometInfo(info)
+
+	// expect-pass (votes of height 2 are included in next block)
+	s.Require().Error(baseapp.ValidateVoteExtensions(s.ctx, s.valStore, 0, "", llc))
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
+	s.ctx = s.ctx.WithBlockHeight(3).WithHeaderInfo(header.Info{Height: 3, ChainID: chainID}) // vote-extensions are enabled
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
+	s.Require().Error(baseapp.ValidateVoteExtensions(s.ctx, s.valStore, 0, "", llc))
+}
+
+func (s *ABCIUtilsTestSuite) TestValidateVoteExtensionsIncorrectOrder() {
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
+	s.ctx = s.ctx.WithBlockHeight(3).WithHeaderInfo(header.Info{Height: 3, ChainID: chainID}) // vote-extensions are enabled
+
+	// create last commit
+	llc, info := extendedCommitToLastCommit(llc)
+	s.ctx = s.ctx.WithCometInfo(info)
+
+	// modify voting powers to differ from the last-commit
+	llc.Votes[0], llc.Votes[2] = llc.Votes[2], llc.Votes[0]
+
 	// expect-pass (votes of height 2 are included in next block)
-	s.Require().Error(baseapp.ValidateVoteExtensions(s.ctx, s.valStore, 3, chainID, llc))
+	s.Require().Error(baseapp.ValidateVoteExtensions(s.ctx, s.valStore, 0, "", llc))
 }
 
 func (s *ABCIUtilsTestSuite) TestDefaultProposalHandler_NoOpMempoolTxSelection() {
@@ -586,3 +730,47 @@ func setTxSignatureWithSecret(t *testing.T, builder client.TxBuilder, signatures
 	)
 	require.NoError(t, err)
 }
+
+func extendedCommitToLastCommit(ec abci.ExtendedCommitInfo) (abci.ExtendedCommitInfo, comet.BlockInfo) {
+	// sort the extended commit info
+	sort.Sort(extendedVoteInfos(ec.Votes))
+
+	// convert the extended commit info to last commit info
+	lastCommit := abci.CommitInfo{
+		Round: ec.Round,
+		Votes: make([]abci.VoteInfo, len(ec.Votes)),
+	}
+
+	for i, vote := range ec.Votes {
+		lastCommit.Votes[i] = abci.VoteInfo{
+			Validator: abci.Validator{
+				Address: vote.Validator.Address,
+				Power:   vote.Validator.Power,
+			},
+		}
+	}
+
+	return ec, baseapp.NewBlockInfo(
+		nil,
+		nil,
+		nil,
+		lastCommit,
+	)
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

### baseapp/info.go
```diff
@@ -10,6 +10,20 @@ import (
 
 var _ comet.BlockInfo = (*cometInfo)(nil)
 
+func NewBlockInfo(
+	misbehavior []abci.Misbehavior,
+	validatorsHash []byte,
+	proposerAddress []byte,
+	lastCommit abci.CommitInfo,
+) *cometInfo {
+	return &cometInfo{
+		Misbehavior:     misbehavior,
+		ValidatorsHash:  validatorsHash,
+		ProposerAddress: proposerAddress,
+		LastCommit:      lastCommit,
+	}
+}
+
 // CometInfo defines the properties provided by comet to the application
 type cometInfo struct {
 	Misbehavior     []abci.Misbehavior
```

### tests/integration/staking/keeper/vote_extensions_test.go
```diff
@@ -2,6 +2,7 @@ package keeper_test
 
 import (
 	"bytes"
+	"sort"
 	"testing"
 
 	abci "github.com/cometbft/cometbft/abci/types"
@@ -10,6 +11,8 @@ import (
 	"github.com/cosmos/gogoproto/proto"
 	"gotest.tools/v3/assert"
 
+	"cosmossdk.io/core/comet"
+	"cosmossdk.io/core/header"
 	"cosmossdk.io/math"
 
 	"github.com/cosmos/cosmos-sdk/baseapp"
@@ -21,17 +24,22 @@ import (
 	stakingtypes "github.com/cosmos/cosmos-sdk/x/staking/types"
 )
 
+const chainID = "chain-id-123"
+
+// TestValidateVoteExtensions is a unit test function that tests the validation of vote extensions.
+// It sets up the necessary fixtures and validators, generates vote extensions for each validator,
+// and validates the vote extensions using the baseapp.ValidateVoteExtensions function.
 func TestValidateVoteExtensions(t *testing.T) {
 	t.Parallel()
 	f := initFixture(t)
 
 	// enable vote extensions
 	cp := simtestutil.DefaultConsensusParams
 	cp.Abci = &cmtproto.ABCIParams{VoteExtensionsEnableHeight: 1}
-	f.sdkCtx = f.sdkCtx.WithConsensusParams(*cp).WithBlockHeight(2)
+	f.sdkCtx = f.sdkCtx.WithConsensusParams(*cp).WithHeaderInfo(header.Info{Height: 2, ChainID: chainID})
 
 	// setup the validators
-	numVals := 3
+	numVals := 1
 	privKeys := []cryptotypes.PrivKey{}
 	for i := 0; i < numVals; i++ {
 		privKeys = append(privKeys, ed25519.GenPrivKey())
@@ -59,9 +67,9 @@ func TestValidateVoteExtensions(t *testing.T) {
 		voteExt := []byte("something" + v.OperatorAddress)
 		cve := cmtproto.CanonicalVoteExtension{
 			Extension: voteExt,
-			Height:    f.sdkCtx.BlockHeight() - 1, // the vote extension was signed in the previous height
+			Height:    f.sdkCtx.HeaderInfo().Height - 1, // the vote extension was signed in the previous height
 			Round:     0,
-			ChainId:   "chain-id-123",
+			ChainId:   chainID,
 		}
 
 		extSignBytes, err := mashalVoteExt(&cve)
@@ -84,7 +92,10 @@ func TestValidateVoteExtensions(t *testing.T) {
 		votes = append(votes, ve)
 	}
 
-	err := baseapp.ValidateVoteExtensions(f.sdkCtx, f.stakingKeeper, f.sdkCtx.BlockHeight(), "chain-id-123", abci.ExtendedCommitInfo{Round: 0, Votes: votes})
+	eci, ci := extendedCommitToLastCommit(abci.ExtendedCommitInfo{Round: 0, Votes: votes})
+	f.sdkCtx = f.sdkCtx.WithCometInfo(ci)
+
+	err := baseapp.ValidateVoteExtensions(f.sdkCtx, f.stakingKeeper, 0, "", eci)
 	assert.NilError(t, err)
 }
 
@@ -96,3 +107,42 @@ func mashalVoteExt(msg proto.Message) ([]byte, error) {
 
 	return buf.Bytes(), nil
 }
+
+func extendedCommitToLastCommit(ec abci.ExtendedCommitInfo) (abci.ExtendedCommitInfo, comet.BlockInfo) {
+	// sort the extended commit info
+	sort.Sort(extendedVoteInfos(ec.Votes))
+
+	// convert the extended commit info to last commit info
+	lastCommit := abci.CommitInfo{
+		Round: ec.Round,
+		Votes: make([]abci.VoteInfo, len(ec.Votes)),
+	}
+
+	for i, vote := range ec.Votes {
+		lastCommit.Votes[i] = abci.VoteInfo{
+			Validator: abci.Validator{
+				Address: vote.Validator.Address,
+				Power:   vote.Validator.Power,
+			},
+		}
+	}
+
+	return ec, baseapp.NewBlockInfo(nil, nil, nil, lastCommit)
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

### x/slashing/keeper/slash_redelegation_test.go
```diff
@@ -5,24 +5,23 @@ import (
 	"testing"
 	"time"
 
+	"github.com/stretchr/testify/require"
+
 	"cosmossdk.io/core/header"
 	"cosmossdk.io/depinject"
 	"cosmossdk.io/log"
 	"cosmossdk.io/math"
+
+	"github.com/cosmos/cosmos-sdk/crypto/keys/secp256k1"
+	simtestutil "github.com/cosmos/cosmos-sdk/testutil/sims"
+	sdk "github.com/cosmos/cosmos-sdk/types"
 	bankkeeper "github.com/cosmos/cosmos-sdk/x/bank/keeper"
 	banktestutil "github.com/cosmos/cosmos-sdk/x/bank/testutil"
+	distributionkeeper "github.com/cosmos/cosmos-sdk/x/distribution/keeper"
 	slashingkeeper "github.com/cosmos/cosmos-sdk/x/slashing/keeper"
 	"github.com/cosmos/cosmos-sdk/x/slashing/testutil"
 	stakingkeeper "github.com/cosmos/cosmos-sdk/x/staking/keeper"
 	stakingtypes "github.com/cosmos/cosmos-sdk/x/staking/types"
-
-	distributionkeeper "github.com/cosmos/cosmos-sdk/x/distribution/keeper"
-
-	"github.com/cosmos/cosmos-sdk/crypto/keys/secp256k1"
-	sdk "github.com/cosmos/cosmos-sdk/types"
-	"github.com/stretchr/testify/require"
-
-	simtestutil "github.com/cosmos/cosmos-sdk/testutil/sims"
 )
 
 func TestSlashRedelegation(t *testing.T) {
@@ -100,7 +99,7 @@ func TestSlashRedelegation(t *testing.T) {
 	require.NoError(t, err)
 
 	// next block, commit height 3, move to height 4
-	// with the new delegations, evil val increases in voting power and commit byzantine behaviour at height 4 consensus
+	// with the new delegations, evil val increases in voting power and commit byzantine behavior at height 4 consensus
 	// at the same time, acc 1 and acc 2 withdraw delegation from evil val
 	ctx, err = simtestutil.NextBlock(app, ctx, time.Duration(1))
 	require.NoError(t, err)
@@ -126,9 +125,9 @@ func TestSlashRedelegation(t *testing.T) {
 	require.NoError(t, err)
 
 	// next block, commit height 4, move to height 5
-	// Slash evil val for byzantine behaviour at height 4 consensus,
+	// Slash evil val for byzantine behavior at height 4 consensus,
 	// at which acc 1 and acc 2 still contributed to evil val voting power
-	// even tho they undelegate at block 4, the valset update is applied after commited block 4 when height 4 consensus already passes
+	// even tho they undelegate at block 4, the valset update is applied after committed block 4 when height 4 consensus already passes
 	ctx, err = simtestutil.NextBlock(app, ctx, time.Duration(1))
 	require.NoError(t, err)
 
```
