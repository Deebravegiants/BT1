# [?] Fix slash verify to avoid potential duplicate slashes exploit (#2914)

## Summary
Severity: Unknown
Chain: Harmony
Component: harmony-one/harmony
Published: 2020-05-02
Source: https://github.com/harmony-one/harmony/commit/2ccc20be2b276801ed17b58a1c53b9161d4bb6af
Type: security-commit

## Details
Fix slash verify to avoid potential duplicate slashes exploit (#2914)

* Remove timestamp in slash record

* Fix potential exploits of reporting duplicate slashes

* fix import

* dedup swapped votes

## Patch
### consensus/double_sign.go
```diff
@@ -1,13 +1,9 @@
 package consensus
 
 import (
-	"math/big"
-	"time"
-
 	"github.com/ethereum/go-ethereum/common"
 	"github.com/harmony-one/bls/ffi/go/bls"
 	"github.com/harmony-one/harmony/consensus/quorum"
-	"github.com/harmony-one/harmony/consensus/votepower"
 	"github.com/harmony-one/harmony/shard"
 	"github.com/harmony-one/harmony/staking/slash"
 )
@@ -73,8 +69,6 @@ func (consensus *Consensus) checkDoubleSign(recvMsg *FBFTMessage) bool {
 							return true
 						}
 
-						now := big.NewInt(time.Now().UnixNano())
-
 						leaderShardKey := shard.FromLibBLSPublicKeyUnsafe(consensus.LeaderPubKey)
 						if leaderShardKey == nil {
 							consensus.getLogger().Error().
@@ -91,25 +85,26 @@ func (consensus *Consensus) checkDoubleSign(recvMsg *FBFTMessage) bool {
 
 						go func(reporter common.Address) {
 							evid := slash.Evidence{
-								ConflictingBallots: slash.ConflictingBallots{
-									AlreadyCastBallot: *alreadyCastBallot,
-									DoubleSignedBallot: votepower.Ballot{
-										SignerPubKey:    *offender,
-										BlockHeaderHash: recvMsg.BlockHash,
-										Signature:       common.Hex2Bytes(doubleSign.SerializeToHexStr()),
-										Height:          recvMsg.BlockNum,
-										ViewID:          recvMsg.ViewID,
+								ConflictingVotes: slash.ConflictingVotes{
+									FirstVote: slash.Vote{
+										alreadyCastBallot.SignerPubKey,
+										alreadyCastBallot.BlockHeaderHash,
+										alreadyCastBallot.Signature,
+									},
+									SecondVote: slash.Vote{
+										*offender,
+										recvMsg.BlockHash,
+										common.Hex2Bytes(doubleSign.SerializeToHexStr()),
 									}},
 								Moment: slash.Moment{
-									Epoch:        curHeader.Epoch(),
-									ShardID:      consensus.ShardID,
-									TimeUnixNano: now,
+									Epoch:   curHeader.Epoch(),
+									ShardID: consensus.ShardID,
 								},
+								Offender: *addr,
 							}
 							proof := slash.Record{
 								Evidence: evid,
 								Reporter: reporter,
-								Offender: *addr,
 							}
 							consensus.SlashChan <- proof
 						}(*leaderAddr)
```

### internal/chain/engine.go
```diff
@@ -381,8 +381,8 @@ func applySlashes(
 	// First group slashes by same signed blocks
 	for i := range doubleSigners {
 		thisKey := keyStruct{
-			height:  doubleSigners[i].Evidence.AlreadyCastBallot.Height,
-			viewID:  doubleSigners[i].Evidence.AlreadyCastBallot.ViewID,
+			height:  doubleSigners[i].Evidence.Height,
+			viewID:  doubleSigners[i].Evidence.ViewID,
 			shardID: doubleSigners[i].Evidence.Moment.ShardID,
 			epoch:   doubleSigners[i].Evidence.Moment.Epoch.Uint64(),
 		}
```

### node/worker/worker.go
```diff
@@ -7,6 +7,8 @@ import (
 	"sort"
 	"time"
 
+	"github.com/harmony-one/harmony/crypto/hash"
+
 	"github.com/ethereum/go-ethereum/common"
 	"github.com/ethereum/go-ethereum/rlp"
 	"github.com/harmony-one/harmony/block"
@@ -374,10 +376,34 @@ func (w *Worker) verifySlashes(
 		return successes, failures
 	}
 
+	seenEvidences := map[common.Hash]struct{}{}
+
 	for i := range d {
+		evidenceHash := hash.FromRLPNew256(d[i].Evidence)
+		if existing, ok := seenEvidences[evidenceHash]; ok {
+			utils.Logger().Warn().
+				Interface("slashRecord1", existing).
+				Interface("slashRecord2", d[i]).
+				Msg("Duplicate slash records with different reporters")
+			failures = append(failures, d[i])
+		} else {
+			seenEvidences[evidenceHash] = struct{}{}
+
+			// In addition, need to count the same evidence with first and second vote swapped as seen
+			swapVote := d[i].Evidence
+			tmp := swapVote.ConflictingVotes.FirstVote
+			swapVote.ConflictingVotes.FirstVote = swapVote.ConflictingVotes.SecondVote
+			swapVote.ConflictingVotes.SecondVote = tmp
+			swapHash := hash.FromRLPNew256(swapVote)
+			seenEvidences[swapHash] = struct{}{}
+		}
+
 		if err := slash.Verify(
 			w.chain, workingState, &d[i],
 		); err != nil {
+			utils.Logger().Warn().Err(err).
+				Interface("slashRecord", d[i]).
+				Msg("Slash failed verification")
 			failures = append(failures, d[i])
 		}
 		successes = append(successes, d[i])
```

### staking/slash/double-sign.go
```diff
@@ -52,29 +52,37 @@ func payDebt(
 
 // Moment ..
 type Moment struct {
-	Epoch        *big.Int `json:"epoch"`
-	TimeUnixNano *big.Int `json:"time-unix-nano"`
-	ShardID      uint32   `json:"shard-id"`
+	Epoch   *big.Int `json:"epoch"`
+	ShardID uint32   `json:"shard-id"`
+	Height  uint64   `json:"height"`
+	ViewID  uint64   `json:"view-id"`
 }
 
 // Evidence ..
 type Evidence struct {
 	Moment
-	ConflictingBallots
+	ConflictingVotes
+	Offender common.Address `json:"offender"`
+}
+
+// ConflictingVotes ..
+type ConflictingVotes struct {
+	FirstVote  Vote `json:"first-vote"`
+	SecondVote Vote `json:"second-vote"`
 }
 
-// ConflictingBallots ..
-type ConflictingBallots struct {
-	AlreadyCastBallot  votepower.Ballot `json:"already-cast-vote"`
-	DoubleSignedBallot votepower.Ballot `json:"double-signed-vote"`
+// Vote is the vote of the double signer
+type Vote struct {
+	SignerPubKey    shard.BLSPublicKey `json:"bls-public-key"`
+	BlockHeaderHash common.Hash        `json:"block-header-hash"`
+	Signature       []byte             `json:"bls-signature"`
 }
 
 // Record is an proof of a slashing made by a witness of a double-signing event
 type Record struct {
 	// the reporter who will get rewarded
 	Evidence Evidence       `json:"evidence"`
 	Reporter common.Address `json:"reporter"`
-	Offender common.Address `json:"offender"`
 }
 
 // Application tracks the slash application to state
@@ -92,8 +100,8 @@ func (a *Application) String() string {
 func (e Evidence) MarshalJSON() ([]byte, error) {
 	return json.Marshal(struct {
 		Moment
-		ConflictingBallots
-	}{e.Moment, e.ConflictingBallots})
+		ConflictingVotes
+	}{e.Moment, e.ConflictingVotes})
 }
 
 // Records ..
@@ -117,7 +125,7 @@ var (
 func (r Record) MarshalJSON() ([]byte, error) {
 	reporter, offender :=
 		common2.MustAddressToBech32(r.Reporter),
-		common2.MustAddressToBech32(r.Offender)
+		common2.MustAddressToBech32(r.Evidence.Offender)
 	return json.Marshal(struct {
 		Evidence         Evidence `json:"evidence"`
 		Beneficiary      string   `json:"beneficiary"`
@@ -148,7 +156,7 @@ func Verify(
 	state *state.DB,
 	candidate *Record,
 ) error {
-	wrapper, err := state.ValidatorWrapper(candidate.Offender)
+	wrapper, err := state.ValidatorWrapper(candidate.Evidence.Offender)
 	if err != nil {
 		return err
 	}
@@ -157,13 +165,13 @@ func Verify(
 		return errAlreadyBannedValidator
 	}
 
-	if candidate.Offender == candidate.Reporter {
+	if candidate.Evidence.Offender == candidate.Reporter {
 		return errReporterAndOffenderSame
 	}
 
 	first, second :=
-		candidate.Evidence.AlreadyCastBallot,
-		candidate.Evidence.DoubleSignedBallot
+		candidate.Evidence.FirstVote,
+		candidate.Evidence.SecondVote
 	k1, k2 := len(first.SignerPubKey), len(second.SignerPubKey)
 	if k1 != shard.PublicKeySizeInBytes ||
 		k2 != shard.PublicKeySizeInBytes {
@@ -172,9 +180,7 @@ func Verify(
 		)
 	}
 
-	if first.ViewID != second.ViewID ||
-		first.Height != second.Height ||
-		first.BlockHeaderHash == second.BlockHeaderHash {
+	if first.BlockHeaderHash == second.BlockHeaderHash {
 		return errors.Wrapf(errSlashBlockNoConflict, "first %v+ second %v+", first, second)
 	}
 
@@ -210,27 +216,29 @@ func Verify(
 
 	if addr, err := subCommittee.AddressForBLSKey(
 		second.SignerPubKey,
-	); err != nil || *addr != candidate.Offender {
+	); err != nil {
 		return err
+	} else if *addr != candidate.Evidence.Offender {
+		return errors.Errorf("offender address (%x) does not match the signer's address (%x)", candidate.Evidence.Offender, addr)
 	}
 
 	// last ditch check
 	if hash.FromRLPNew256(
-		candidate.Evidence.AlreadyCastBallot,
+		candidate.Evidence.FirstVote,
 	) == hash.FromRLPNew256(
-		candidate.Evidence.DoubleSignedBallot,
+		candidate.Evidence.SecondVote,
 	) {
 		return errors.Wrapf(
 			errBallotsNotDiff,
 			"%s %s",
-			candidate.Evidence.AlreadyCastBallot.SignerPubKey.Hex(),
-			candidate.Evidence.DoubleSignedBallot.SignerPubKey.Hex(),
+			candidate.Evidence.FirstVote.SignerPubKey.Hex(),
+			candidate.Evidence.SecondVote.SignerPubKey.Hex(),
 		)
 	}
 
-	for _, ballot := range [...]votepower.Ballot{
-		candidate.Evidence.AlreadyCastBallot,
-		candidate.Evidence.DoubleSignedBallot,
+	for _, ballot := range [...]Vote{
+		candidate.Evidence.FirstVote,
+		candidate.Evidence.SecondVote,
 	} {
 		// now the only real assurance, cryptography
 		signature := &bls.Sign{}
@@ -245,11 +253,11 @@ func Verify(
 
 		// slash verification only happens in staking era, therefore want commit payload for staking epoch
 		commitPayload := consensus_sig.ConstructCommitPayload(chain,
-			chain.Config().StakingEpoch, ballot.BlockHeaderHash, ballot.Height, ballot.ViewID)
+			chain.Config().StakingEpoch, ballot.BlockHeaderHash, candidate.Evidence.Height, candidate.Evidence.ViewID)
 		utils.Logger().Debug().
 			Uint64("epoch", chain.Config().StakingEpoch.Uint64()).
-			Uint64("block-number", ballot.Height).
-			Uint64("view-id", ballot.ViewID).
+			Uint64("block-number", candidate.Evidence.Height).
+			Uint64("view-id", candidate.Evidence.ViewID).
 			Msgf("[COMMIT-PAYLOAD] doubleSignVerify %v", hex.EncodeToString(commitPayload))
 
 		if !signature.VerifyHash(publicKey, commitPayload) {
@@ -448,17 +456,17 @@ func Apply(
 	for _, slash := range slashes {
 		snapshot, err := chain.ReadValidatorSnapshotAtEpoch(
 			slash.Evidence.Epoch,
-			slash.Offender,
+			slash.Evidence.Offender,
 		)
 
 		if err != nil {
 			return nil, errors.Errorf(
 				"could not find validator %s",
-				common2.MustAddressToBech32(slash.Offender),
+				common2.MustAddressToBech32(slash.Evidence.Offender),
 			)
 		}
 
-		current, err := state.ValidatorWrapper(slash.Offender)
+		current, err := state.ValidatorWrapper(slash.Evidence.Offender)
 		if err != nil {
 			return nil, errors.Wrapf(
 				errValidatorNotFoundDuringSlash, " %s ", err.Error(),
@@ -498,7 +506,7 @@ func Rate(votingPower *votepower.Roster, records Records) numeric.Dec {
 	rate := numeric.ZeroDec()
 
 	for i := range records {
-		key := records[i].Evidence.DoubleSignedBallot.SignerPubKey
+		key := records[i].Evidence.SecondVote.SignerPubKey
 		if card, exists := votingPower.Voters[key]; exists {
 			rate = rate.Add(card.GroupPercent)
 		} else {
```

### staking/slash/double-sign_test.go
```diff
@@ -12,7 +12,6 @@ import (
 	"github.com/harmony-one/bls/ffi/go/bls"
 	"github.com/harmony-one/harmony/block"
 	"github.com/harmony-one/harmony/common/denominations"
-	"github.com/harmony-one/harmony/consensus/votepower"
 	"github.com/harmony-one/harmony/core/state"
 	"github.com/harmony-one/harmony/core/types"
 	common2 "github.com/harmony-one/harmony/internal/common"
@@ -346,30 +345,27 @@ func (s *scenario) defaultDelegationPair() (
 func defaultSlashRecord() Record {
 	return Record{
 		Evidence: Evidence{
-			ConflictingBallots: ConflictingBallots{
-				AlreadyCastBallot: votepower.Ballot{
+			ConflictingVotes: ConflictingVotes{
+				FirstVote: Vote{
 					SignerPubKey:    blsWrapA,
 					BlockHeaderHash: hashA,
 					Signature:       common.Hex2Bytes(signerABLSSignature),
-					Height:          doubleSignBlockNumber,
-					ViewID:          doubleSignViewID,
 				},
-				DoubleSignedBallot: votepower.Ballot{
+				SecondVote: Vote{
 					SignerPubKey:    blsWrapB,
 					BlockHeaderHash: hashB,
 					Signature:       common.Hex2Bytes(signerBBLSSignature),
-					Height:          doubleSignBlockNumber,
-					ViewID:          doubleSignViewID,
 				},
 			},
 			Moment: Moment{
-				Epoch:        big.NewInt(doubleSignEpoch),
-				TimeUnixNano: big.NewInt(doubleSignUnixNano),
-				ShardID:      doubleSignShardID,
+				Epoch:   big.NewInt(doubleSignEpoch),
+				ShardID: doubleSignShardID,
+				Height:  doubleSignBlockNumber,
+				ViewID:  doubleSignViewID,
 			},
+			Offender: offenderAddr,
 		},
 		Reporter: reporterAddr,
-		Offender: offenderAddr,
 	}
 }
 
```
