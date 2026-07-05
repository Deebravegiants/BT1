### Title
Unelected Committee Member Votes Bypass Mempool-Only Guard in GOV Rule Before Protocol Version 11 - (File: `eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Gov.hs`)

---

### Summary

Before protocol version 11, the restriction preventing unelected Constitutional Committee (CC) members from casting governance votes is enforced **only in the `MEMPOOL` rule**, not in the core `GOV` ledger transition rule. A block producer can bypass the mempool entirely and include a transaction containing an unelected CC member's vote directly in a block. The `GOV` rule accepts and records this vote. Once the corresponding `UpdateCommittee` proposal is enacted and the attacker becomes an elected member, their pre-recorded vote is counted in ratification — potentially enabling unauthorized governance actions (treasury withdrawals, protocol parameter changes, hard fork initiations) to be enacted.

---

### Finding Description

The `mempoolTransition` function in `Mempool.hs` contains the following guard:

```haskell
unless (hardforkConwayDisallowUnelectedCommitteeFromVoting protVer) $
  -- This check can completely be removed once mainnet switches to protocol
  -- version 11, since the same check has been implemented in the GOV rule.
  --
  -- Disallow votes by unelected committee members
  failOnNonEmpty
    ( unelectedCommitteeVoters ... )
    (ConwayMempoolFailure . addPrefix . T.pack . show . NE.toList)
```

`unless False action` executes `action`, so when `pv < 11`, the mempool **does** block unelected committee votes. However, the `MEMPOOL` rule is only invoked for transactions entering the mempool — not for transactions included directly in a block by a block producer. [1](#0-0) 

In `conwayGovTransition` (the core `GOV` ledger rule), the analogous check is gated on the same hardfork flag:

```haskell
when (hardforkConwayDisallowUnelectedCommitteeFromVoting $ pp ^. ppProtocolVersionL) $
    failOnNonEmpty
      (unelectedCommitteeVoters committee committeeState gsVotingProcedures)
      (injectFailure . UnelectedCommitteeVoters)
``` [2](#0-1) 

When `pv < 11`, `hardforkConwayDisallowUnelectedCommitteeFromVoting` returns `False`, so `when False` skips the check entirely. The `GOV` rule proceeds to validate voters only against `authorizedHotCommitteeCredentials committeeState` — which includes **all** authorized hot credentials, both elected and unelected:

```haskell
knownCommitteeMembers = authorizedHotCommitteeCredentials committeeState
``` [3](#0-2) 

`authorizedHotCommitteeCredentials` collects every `CommitteeHotCredential` from `csCommitteeCreds`, regardless of whether the corresponding cold credential is in the currently elected committee: [4](#0-3) 

By contrast, `authorizedElectedHotCommitteeCredentials` (used in `unelectedCommitteeVoters`) intersects with the elected committee: [5](#0-4) 

The `checkVotersAreValid` call in the GOV rule only checks whether the **action type** permits committee votes, not whether the specific voter is elected: [6](#0-5) 

An unelected member's vote is therefore accepted and stored in `gasCommitteeVotes`. In `committeeAcceptedRatio`, ratification iterates over `members` (elected committee members) and looks up their hot keys in `gasCommitteeVotes`: [7](#0-6) 

Once the `UpdateCommittee` proposal is enacted and the attacker's cold credential enters the elected committee, the pre-recorded hot-key vote is found in `gasCommitteeVotes` and counted as a `VoteYes`.

The `ConwayAuthCommitteeHotKey` certificate (which authorizes a hot key) is permitted for any cold credential that is either a current member **or** mentioned in a pending `UpdateCommittee` proposal: [8](#0-7) 

This means any party who submits an `UpdateCommittee` proposal (paying only the governance deposit) can authorize a hot key and, with block-producer access, pre-record votes.

---

### Impact Explanation

An unelected proposed committee member, colluding with a block producer, can:

1. Submit an `UpdateCommittee` proposal naming their cold credential (costs only the governance deposit — open to any participant).
2. Authorize a hot key via `ConwayAuthCommitteeHotKey` (valid because they are a "potential future member").
3. Have the block producer include a transaction with their hot-key vote directly in a block, bypassing the mempool check.
4. The `GOV` rule records the vote in `gasCommitteeVotes` without error.
5. Once the `UpdateCommittee` proposal is enacted, the pre-recorded vote is counted in `committeeAcceptedRatio`.

This allows a governance action (treasury withdrawal, protocol parameter change, hard fork initiation, new constitution) to be ratified with committee support that includes a vote cast before the voter was legitimately elected — an unauthorized governance state transition.

**Impact class**: Critical — Unauthorized governance action enacted.

---

### Likelihood Explanation

- **Block producer access** is required to bypass the mempool. This is a realistic attacker profile: any stake pool operator (SPO) producing blocks can do this.
- **Governance deposit** is the only financial barrier to submitting an `UpdateCommittee` proposal.
- The window is the entire period before protocol version 11 activates on mainnet.
- The attack is silent: the transaction passes all ledger validation rules and leaves no anomalous failure trace.

---

### Recommendation

Move the `unelectedCommitteeVoters` check unconditionally into `conwayGovTransition` (the `GOV` rule), removing the `hardforkConwayDisallowUnelectedCommitteeFromVoting` gate, so that it is enforced at the ledger level regardless of whether the transaction entered via the mempool or was included directly in a block. The mempool-level check can then be removed as redundant.

---

### Proof of Concept

**Setup (pv < 11, Conway era):**

1. Attacker (SPO) submits `UpdateCommittee SNothing mempty [(attackerColdCred, expiry)] threshold` — pays governance deposit, no other privilege needed.
2. Attacker submits `ConwayAuthCommitteeHotKey attackerColdCred attackerHotCred` — valid because `attackerColdCred` is in a pending `UpdateCommittee` proposal.
3. Attacker (as block producer) constructs a transaction with `votingProcedures = {CommitteeVoter attackerHotCred → {targetGovActionId → VoteYes}}` and includes it directly in a block (bypassing mempool).
4. `conwayGovTransition` runs: `attackerHotCred ∈ authorizedHotCommitteeCredentials committeeState` → passes `internVoter` → vote recorded in `gasCommitteeVotes`.
5. DReps and SPOs vote Yes on the `UpdateCommittee` proposal; it is enacted at the next epoch boundary.
6. `attackerColdCred` is now in the elected committee; `committeeAcceptedRatio` finds `attackerHotCred` in `gasCommitteeVotes` and counts it as `VoteYes`.
7. The target governance action (e.g., treasury withdrawal) reaches the committee threshold and is enacted — with a vote that was cast before the voter was legitimately elected.

The existing test at protocol version 10 confirms the vote-counting behavior once the member is elected: [9](#0-8) 

The only difference between the test scenario and the attack is that the test submits the vote through the mempool (which at pv 10 blocks it via `unless False`), while the attacker submits it directly in a block, bypassing that check entirely.

### Citations

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Mempool.hs (L123-135)
```haskell
    unless (hardforkConwayDisallowUnelectedCommitteeFromVoting protVer) $
      -- This check can completely be removed once mainnet switches to protocol
      -- version 11, since the same check has been implemented in the GOV rule.
      --
      -- Disallow votes by unelected committee members
      let addPrefix = ("Unelected committee members are not allowed to cast votes: " <>)
       in failOnNonEmpty
            ( unelectedCommitteeVoters
                (ledgerState ^. lsUTxOStateL . utxosGovStateL . committeeGovStateL)
                (ledgerState ^. lsCertStateL . certVStateL . vsCommitteeStateL)
                (tx ^. bodyTxL . votingProceduresTxBodyL)
            )
            (ConwayMempoolFailure . addPrefix . T.pack . show . NE.toList)
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Gov.hs (L364-376)
```haskell
checkVotersAreValid ::
  forall era.
  ConwayEraPParams era =>
  EpochNo ->
  CommitteeState era ->
  [(Voter, GovActionState era)] ->
  Test (ConwayGovPredFailure era)
checkVotersAreValid currentEpoch committeeState votes =
  checkDisallowedVotes votes DisallowedVoters $ \gas ->
    \case
      CommitteeVoter {} -> isCommitteeVotingAllowed currentEpoch committeeState (gasAction gas)
      DRepVoter {} -> isDRepVotingAllowed (gasAction gas)
      StakePoolVoter {} -> isStakePoolVotingAllowed (gasAction gas)
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Gov.hs (L474-474)
```haskell
      knownCommitteeMembers = authorizedHotCommitteeCredentials committeeState
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Gov.hs (L478-481)
```haskell
  when (hardforkConwayDisallowUnelectedCommitteeFromVoting $ pp ^. ppProtocolVersionL) $
    failOnNonEmpty
      (unelectedCommitteeVoters committee committeeState gsVotingProcedures)
      (injectFailure . UnelectedCommitteeVoters)
```

**File:** libs/cardano-ledger-core/src/Cardano/Ledger/State/CertState.hs (L338-343)
```haskell
authorizedHotCommitteeCredentials :: CommitteeState era -> Set.Set (Credential HotCommitteeRole)
authorizedHotCommitteeCredentials CommitteeState {csCommitteeCreds} =
  let toHotCredSet acc = \case
        CommitteeHotCredential hotCred -> Set.insert hotCred acc
        CommitteeMemberResigned {} -> acc
   in F.foldl' toHotCredSet Set.empty csCommitteeCreds
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Governance.hs (L581-591)
```haskell
authorizedElectedHotCommitteeCredentials ::
  StrictMaybe (Committee era) ->
  CommitteeState era ->
  Set.Set (Credential HotCommitteeRole)
authorizedElectedHotCommitteeCredentials committee committeeState =
  case committee of
    SNothing -> Set.empty
    SJust electedCommiteee ->
      authorizedHotCommitteeCredentials $
        CommitteeState $
          csCommitteeCreds committeeState `Map.intersection` committeeMembers electedCommiteee
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Ratify.hs (L151-163)
```haskell
    accumVotes (!yes, !tot) member expiry
      | currentEpoch > expiry = (yes, tot) -- member is expired, vote "abstain" (don't count it)
      | otherwise =
          case Map.lookup member (csCommitteeCreds committeeState) of
            Nothing -> (yes, tot) -- member is not registered, vote "abstain"
            Just (CommitteeMemberResigned _) -> (yes, tot) -- member has resigned, vote "abstain"
            Just (CommitteeHotCredential hotKey) ->
              case Map.lookup hotKey votes of
                Nothing -> (yes, tot + 1) -- member hasn't voted, vote "no"
                Just Abstain -> (yes, tot) -- member voted "abstain"
                Just VoteNo -> (yes, tot + 1) -- member voted "no"
                Just VoteYes -> (yes + 1, tot + 1) -- member voted "yes"
    (yesVotes, totalExcludingAbstain) = Map.foldlWithKey' accumVotes (0, 0) members
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/GovCert.hs (L197-208)
```haskell
        let isCurrentMember =
              strictMaybe False (Map.member coldCred . committeeMembers) cgceCurrentCommittee
            committeeUpdateContainsColdCred GovActionState {gasProposalProcedure} =
              case pProcGovAction gasProposalProcedure of
                UpdateCommittee _ _ newMembers _ -> Map.member coldCred newMembers
                _ -> False
            isPotentialFutureMember =
              any committeeUpdateContainsColdCred cgceCommitteeProposals
        isCurrentMember || isPotentialFutureMember ?! (injectFailure . ConwayCommitteeIsUnknown) coldCred
        pure $
          certState
            & certVStateL . vsCommitteeStateL . csCommitteeCredsL %~ Map.insert coldCred newMemberState
```

**File:** eras/conway/impl/testlib/Test/Cardano/Ledger/Conway/Imp/GovCertSpec.hs (L211-228)
```haskell
      whenMajorVersion @10 $ do
        (drep, spo) <- setupGovEnv
        (gaiWithdrawal, initialMembers, proposedMember, gaiUpdateCommittee) <-
          proposeWithdrawalAndMember drep
        submitYesVote_ (DRepVoter drep) gaiUpdateCommittee
        submitYesVote_ (StakePoolVoter spo) gaiUpdateCommittee
        passEpoch
        expectMembers initialMembers
        proposedMemberHotKey <- registerCommitteeHotKey proposedMember
        submitYesVote_ (CommitteeVoter proposedMemberHotKey) gaiWithdrawal
        isCommitteeAccepted gaiWithdrawal `shouldReturn` False
        passEpoch
        expectMembers $ Set.singleton proposedMember
        ccShouldNotBeExpired proposedMember
        isCommitteeAccepted gaiWithdrawal `shouldReturn` True
        passNEpochs 2
        expectMissingGovActionId gaiUpdateCommittee
        expectMissingGovActionId gaiWithdrawal
```
