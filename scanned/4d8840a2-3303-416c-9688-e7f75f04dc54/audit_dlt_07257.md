# [?] cs: fix nondeterministic tests (#3582)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cometbft/cometbft
Published: 2019-04-23
Source: https://github.com/cometbft/cometbft/commit/b738add80cb9f7e7e91cbad38ec6db297f3535e6
Type: security-commit

## Details
cs: fix nondeterministic tests (#3582)

Should fix #3451, #2723 and #3317.

Test TestResetTimeoutPrecommitUponNewHeight is simplified so it reduces a risk of timeout failure. Furthermore, timeout we wait for TimeoutEvents is increased, and the timeout value is more precisely computed. This should hopefully decrease a chance of non-deterministic test failures.

This assertion is problematic to ensure consistently due to dependency on scheduler. On the other hand, if I am not wrong, order in which messages are read from the channel respects order in which messages are written. Therefore, process will receive 2f+1 precommits that are not all for v (one is for nil) so TriggeredTimeoutPrecommit would be set to true. So we don't need to assert it. I know that it would be better to still assert to it but I don't know how to do it without sleep and that is ugly and is causing us nondeterministic failures.

## Patch
### CHANGELOG_PENDING.md
```diff
@@ -25,3 +25,4 @@
 - [state] [\#3537](https://github.com/tendermint/tendermint/pull/3537#issuecomment-482711833) LoadValidators: do not return an empty validator set
 - [p2p] \#3532 limit the number of attempts to connect to a peer in seed mode
   to 16 (as a result, the node will stop retrying after a 35 hours time window)
+- [consensus] \#2723, \#3451 and \#3317 Fix non-deterministic tests 
\ No newline at end of file
```

### consensus/common_test.go
```diff
@@ -351,7 +351,7 @@ func ensureNoNewUnlock(unlockCh <-chan tmpubsub.Message) {
 }
 
 func ensureNoNewTimeout(stepCh <-chan tmpubsub.Message, timeout int64) {
-	timeoutDuration := time.Duration(timeout*5) * time.Nanosecond
+	timeoutDuration := time.Duration(timeout*10) * time.Nanosecond
 	ensureNoNewEvent(
 		stepCh,
 		timeoutDuration,
@@ -398,7 +398,7 @@ func ensureNewRound(roundCh <-chan tmpubsub.Message, height int64, round int) {
 }
 
 func ensureNewTimeout(timeoutCh <-chan tmpubsub.Message, height int64, round int, timeout int64) {
-	timeoutDuration := time.Duration(timeout*5) * time.Nanosecond
+	timeoutDuration := time.Duration(timeout*10) * time.Nanosecond
 	ensureNewEvent(timeoutCh, height, round, timeoutDuration,
 		"Timeout expired while waiting for NewTimeout event")
 }
```

### consensus/state_test.go
```diff
@@ -370,7 +370,7 @@ func TestStateLockNoPOL(t *testing.T) {
 
 	// (note we're entering precommit for a second time this round)
 	// but with invalid args. then we enterPrecommitWait, and the timeout to new round
-	ensureNewTimeout(timeoutWaitCh, height, round, cs1.config.TimeoutPrecommit.Nanoseconds())
+	ensureNewTimeout(timeoutWaitCh, height, round, cs1.config.Precommit(round).Nanoseconds())
 
 	///
 
@@ -384,7 +384,7 @@ func TestStateLockNoPOL(t *testing.T) {
 	incrementRound(vs2)
 
 	// now we're on a new round and not the proposer, so wait for timeout
-	ensureNewTimeout(timeoutProposeCh, height, round, cs1.config.TimeoutPropose.Nanoseconds())
+	ensureNewTimeout(timeoutProposeCh, height, round, cs1.config.Propose(round).Nanoseconds())
 
 	rs := cs1.GetRoundState()
 
@@ -403,7 +403,7 @@ func TestStateLockNoPOL(t *testing.T) {
 
 	// now we're going to enter prevote again, but with invalid args
 	// and then prevote wait, which should timeout. then wait for precommit
-	ensureNewTimeout(timeoutWaitCh, height, round, cs1.config.TimeoutPrevote.Nanoseconds())
+	ensureNewTimeout(timeoutWaitCh, height, round, cs1.config.Prevote(round).Nanoseconds())
 
 	ensurePrecommit(voteCh, height, round) // precommit
 	// the proposed block should still be locked and our precommit added
@@ -416,7 +416,7 @@ func TestStateLockNoPOL(t *testing.T) {
 
 	// (note we're entering precommit for a second time this round, but with invalid args
 	// then we enterPrecommitWait and timeout into NewRound
-	ensureNewTimeout(timeoutWaitCh, height, round, cs1.config.TimeoutPrecommit.Nanoseconds())
+	ensureNewTimeout(timeoutWaitCh, height, round, cs1.config.Precommit(round).Nanoseconds())
 
 	round = round + 1 // entering new round
 	ensureNewRound(newRoundCh, height, round)
@@ -441,15 +441,15 @@ func TestStateLockNoPOL(t *testing.T) {
 	signAddVotes(cs1, types.PrevoteType, hash, rs.ProposalBlock.MakePartSet(partSize).Header(), vs2)
 	ensurePrevote(voteCh, height, round)
 
-	ensureNewTimeout(timeoutWaitCh, height, round, cs1.config.TimeoutPrevote.Nanoseconds())
+	ensureNewTimeout(timeoutWaitCh, height, round, cs1.config.Prevote(round).Nanoseconds())
 	ensurePrecommit(voteCh, height, round) // precommit
 
 	validatePrecommit(t, cs1, round, 0, vss[0], nil, theBlockHash) // precommit nil but be locked on proposal
 
 	signAddVotes(cs1, types.PrecommitType, hash, rs.ProposalBlock.MakePartSet(partSize).Header(), vs2) // NOTE: conflicting precommits at same height
 	ensurePrecommit(voteCh, height, round)
 
-	ensureNewTimeout(timeoutWaitCh, height, round, cs1.config.TimeoutPrecommit.Nanoseconds())
+	ensureNewTimeout(timeoutWaitCh, height, round, cs1.config.Precommit(round).Nanoseconds())
 
 	cs2, _ := randConsensusState(2) // needed so generated block is different than locked block
 	// before we time out into new round, set next proposal block
@@ -482,7 +482,7 @@ func TestStateLockNoPOL(t *testing.T) {
 	signAddVotes(cs1, types.PrevoteType, propBlock.Hash(), propBlock.MakePartSet(partSize).Header(), vs2)
 	ensurePrevote(voteCh, height, round)
 
-	ensureNewTimeout(timeoutWaitCh, height, round, cs1.config.TimeoutPrevote.Nanoseconds())
+	ensureNewTimeout(timeoutWaitCh, height, round, cs1.config.Prevote(round).Nanoseconds())
 	ensurePrecommit(voteCh, height, round)
 	validatePrecommit(t, cs1, round, 0, vss[0], nil, theBlockHash) // precommit nil but locked on proposal
 
@@ -542,7 +542,7 @@ func TestStateLockPOLRelock(t *testing.T) {
 	incrementRound(vs2, vs3, vs4)
 
 	// timeout to new round
-	ensureNewTimeout(timeoutWaitCh, height, round, cs1.config.TimeoutPrecommit.Nanoseconds())
+	ensureNewTimeout(timeoutWaitCh, height, round, cs1.config.Precommit(round).Nanoseconds())
 
 	round = round + 1 // moving to the next round
 	//XXX: this isnt guaranteed to get there before the timeoutPropose ...
@@ -632,7 +632,7 @@ func TestStateLockPOLUnlock(t *testing.T) {
 	propBlockParts := propBlock.MakePartSet(partSize)
 
 	// timeout to new round
-	ensureNewTimeout(timeoutWaitCh, height, round, cs1.config.TimeoutPrecommit.Nanoseconds())
+	ensureNewTimeout(timeoutWaitCh, height, round, cs1.config.Precommit(round).Nanoseconds())
 	rs = cs1.GetRoundState()
 	lockedBlockHash := rs.LockedBlock.Hash()
 
@@ -710,7 +710,7 @@ func TestStateLockPOLSafety1(t *testing.T) {
 
 	// cs1 precommit nil
 	ensurePrecommit(voteCh, height, round)
-	ensureNewTimeout(timeoutWaitCh, height, round, cs1.config.TimeoutPrecommit.Nanoseconds())
+	ensureNewTimeout(timeoutWaitCh, height, round, cs1.config.Precommit(round).Nanoseconds())
 
 	t.Log("### ONTO ROUND 1")
 
@@ -754,7 +754,7 @@ func TestStateLockPOLSafety1(t *testing.T) {
 
 	signAddVotes(cs1, types.PrecommitType, nil, types.PartSetHeader{}, vs2, vs3, vs4)
 
-	ensureNewTimeout(timeoutWaitCh, height, round, cs1.config.TimeoutPrecommit.Nanoseconds())
+	ensureNewTimeout(timeoutWaitCh, height, round, cs1.config.Precommit(round).Nanoseconds())
 
 	incrementRound(vs2, vs3, vs4)
 	round = round + 1 // moving to the next round
@@ -767,7 +767,7 @@ func TestStateLockPOLSafety1(t *testing.T) {
 	*/
 
 	// timeout of propose
-	ensureNewTimeout(timeoutProposeCh, height, round, cs1.config.TimeoutPropose.Nanoseconds())
+	ensureNewTimeout(timeoutProposeCh, height, round, cs1.config.Propose(round).Nanoseconds())
 
 	// finish prevote
 	ensurePrevote(voteCh, height, round)
@@ -850,7 +850,7 @@ func TestStateLockPOLSafety2(t *testing.T) {
 	incrementRound(vs2, vs3, vs4)
 
 	// timeout of precommit wait to new round
-	ensureNewTimeout(timeoutWaitCh, height, round, cs1.config.TimeoutPrecommit.Nanoseconds())
+	ensureNewTimeout(timeoutWaitCh, height, round, cs1.config.Precommit(round).Nanoseconds())
 
 	round = round + 1 // moving to the next round
 	// in round 2 we see the polkad block from round 0
@@ -919,7 +919,7 @@ func TestProposeValidBlock(t *testing.T) {
 
 	signAddVotes(cs1, types.PrecommitType, nil, types.PartSetHeader{}, vs2, vs3, vs4)
 
-	ensureNewTimeout(timeoutWaitCh, height, round, cs1.config.TimeoutPrecommit.Nanoseconds())
+	ensureNewTimeout(timeoutWaitCh, height, round, cs1.config.Precommit(round).Nanoseconds())
 
 	incrementRound(vs2, vs3, vs4)
 	round = round + 1 // moving to the next round
@@ -929,7 +929,7 @@ func TestProposeValidBlock(t *testing.T) {
 	t.Log("### ONTO ROUND 2")
 
 	// timeout of propose
-	ensureNewTimeout(timeoutProposeCh, height, round, cs1.config.TimeoutPropose.Nanoseconds())
+	ensureNewTimeout(timeoutProposeCh, height, round, cs1.config.Propose(round).Nanoseconds())
 
 	ensurePrevote(voteCh, height, round)
 	validatePrevote(t, cs1, round, vss[0], propBlockHash)
@@ -952,7 +952,7 @@ func TestProposeValidBlock(t *testing.T) {
 	ensureNewRound(newRoundCh, height, round)
 	t.Log("### ONTO ROUND 3")
 
-	ensureNewTimeout(timeoutWaitCh, height, round, cs1.config.TimeoutPrecommit.Nanoseconds())
+	ensureNewTimeout(timeoutWaitCh, height, round, cs1.config.Precommit(round).Nanoseconds())
 
 	round = round + 1 // moving to the next round
 
@@ -1004,7 +1004,7 @@ func TestSetValidBlockOnDelayedPrevote(t *testing.T) {
 	// vs3 send prevote nil
 	signAddVotes(cs1, types.PrevoteType, nil, types.PartSetHeader{}, vs3)
 
-	ensureNewTimeout(timeoutWaitCh, height, round, cs1.config.TimeoutPrevote.Nanoseconds())
+	ensureNewTimeout(timeoutWaitCh, height, round, cs1.config.Prevote(round).Nanoseconds())
 
 	ensurePrecommit(voteCh, height, round)
 	// we should have precommitted
@@ -1052,7 +1052,7 @@ func TestSetValidBlockOnDelayedProposal(t *testing.T) {
 	startTestRound(cs1, cs1.Height, round)
 	ensureNewRound(newRoundCh, height, round)
 
-	ensureNewTimeout(timeoutProposeCh, height, round, cs1.config.TimeoutPropose.Nanoseconds())
+	ensureNewTimeout(timeoutProposeCh, height, round, cs1.config.Propose(round).Nanoseconds())
 
 	ensurePrevote(voteCh, height, round)
 	validatePrevote(t, cs1, round, vss[0], nil)
@@ -1065,7 +1065,7 @@ func TestSetValidBlockOnDelayedProposal(t *testing.T) {
 	signAddVotes(cs1, types.PrevoteType, propBlockHash, propBlockParts.Header(), vs2, vs3, vs4)
 	ensureNewValidBlock(validBlockCh, height, round)
 
-	ensureNewTimeout(timeoutWaitCh, height, round, cs1.config.TimeoutPrevote.Nanoseconds())
+	ensureNewTimeout(timeoutWaitCh, height, round, cs1.config.Prevote(round).Nanoseconds())
 
 	ensurePrecommit(voteCh, height, round)
 	validatePrecommit(t, cs1, round, -1, vss[0], nil, nil)
@@ -1099,7 +1099,7 @@ func TestWaitingTimeoutOnNilPolka(t *testing.T) {
 
 	signAddVotes(cs1, types.PrecommitType, nil, types.PartSetHeader{}, vs2, vs3, vs4)
 
-	ensureNewTimeout(timeoutWaitCh, height, round, cs1.config.TimeoutPrecommit.Nanoseconds())
+	ensureNewTimeout(timeoutWaitCh, height, round, cs1.config.Precommit(round).Nanoseconds())
 	ensureNewRound(newRoundCh, height, round+1)
 }
 
@@ -1131,7 +1131,7 @@ func TestWaitingTimeoutProposeOnNewRound(t *testing.T) {
 	rs := cs1.GetRoundState()
 	assert.True(t, rs.Step == cstypes.RoundStepPropose) // P0 does not prevote before timeoutPropose expires
 
-	ensureNewTimeout(timeoutWaitCh, height, round, cs1.config.TimeoutPropose.Nanoseconds())
+	ensureNewTimeout(timeoutWaitCh, height, round, cs1.config.Propose(round).Nanoseconds())
 
 	ensurePrevote(voteCh, height, round)
 	validatePrevote(t, cs1, round, vss[0], nil)
@@ -1165,7 +1165,7 @@ func TestRoundSkipOnNilPolkaFromHigherRound(t *testing.T) {
 	ensurePrecommit(voteCh, height, round)
 	validatePrecommit(t, cs1, round, -1, vss[0], nil, nil)
 
-	ensureNewTimeout(timeoutWaitCh, height, round, cs1.config.TimeoutPrecommit.Nanoseconds())
+	ensureNewTimeout(timeoutWaitCh, height, round, cs1.config.Precommit(round).Nanoseconds())
 
 	round = round + 1 // moving to the next round
 	ensureNewRound(newRoundCh, height, round)
@@ -1191,7 +1191,7 @@ func TestWaitTimeoutProposeOnNilPolkaForTheCurrentRound(t *testing.T) {
 	incrementRound(vss[1:]...)
 	signAddVotes(cs1, types.PrevoteType, nil, types.PartSetHeader{}, vs2, vs3, vs4)
 
-	ensureNewTimeout(timeoutProposeCh, height, round, cs1.config.TimeoutPropose.Nanoseconds())
+	ensureNewTimeout(timeoutProposeCh, height, round, cs1.config.Propose(round).Nanoseconds())
 
 	ensurePrevote(voteCh, height, round)
 	validatePrevote(t, cs1, round, vss[0], nil)
@@ -1332,7 +1332,7 @@ func TestStartNextHeightCorrectly(t *testing.T) {
 
 	cs1.txNotifier.(*fakeTxNotifier).Notify()
 
-	ensureNewTimeout(timeoutProposeCh, height+1, round, cs1.config.TimeoutPropose.Nanoseconds())
+	ensureNewTimeout(timeoutProposeCh, height+1, round, cs1.config.Propose(round).Nanoseconds())
 	rs = cs1.GetRoundState()
 	assert.False(t, rs.TriggeredTimeoutPrecommit, "triggeredTimeoutPrecommit should be false at the beginning of each round")
 }
@@ -1375,12 +1375,8 @@ func TestResetTimeoutPrecommitUponNewHeight(t *testing.T) {
 	// add precommits
 	signAddVotes(cs1, types.PrecommitType, nil, types.PartSetHeader{}, vs2)
 	signAddVotes(cs1, types.PrecommitType, theBlockHash, theBlockParts, vs3)
-	time.Sleep(5 * time.Millisecond)
 	signAddVotes(cs1, types.PrecommitType, theBlockHash, theBlockParts, vs4)
 
-	rs = cs1.GetRoundState()
-	assert.True(t, rs.TriggeredTimeoutPrecommit)
-
 	ensureNewBlockHeader(newBlockHeader, height, theBlockHash)
 
 	prop, propBlock := decideProposal(cs1, vs2, height+1, 0)
@@ -1519,7 +1515,7 @@ func TestStateHalt1(t *testing.T) {
 	incrementRound(vs2, vs3, vs4)
 
 	// timeout to new round
-	ensureNewTimeout(timeoutWaitCh, height, round, cs1.config.TimeoutPrecommit.Nanoseconds())
+	ensureNewTimeout(timeoutWaitCh, height, round, cs1.config.Precommit(round).Nanoseconds())
 
 	round = round + 1 // moving to the next round
 
```
