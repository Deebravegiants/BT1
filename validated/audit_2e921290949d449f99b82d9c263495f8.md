### Title
Unelected Committee Members Can Cast Governance Votes at Protocol Version 10 Due to Missing On-Chain Enforcement in GOV Rule - (File: eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Gov.hs)

### Summary

At Conway protocol version 10, the `GOV` ledger rule does not enforce the restriction on unelected committee members casting votes. The only enforcement exists in the `MEMPOOL` rule, which is a soft mempool-admission policy that block producers can bypass by forging blocks directly. This allows an unelected committee member to have their vote recorded on-chain and counted toward governance ratification once they become elected, enabling unauthorized governance outcomes.

### Finding Description

In `conwayGovTransition`, the check for unelected committee voters is gated behind `hardforkConwayDisallowUnelectedCommitteeFromVoting`:

```haskell
when (hardforkConwayDisallowUnelectedCommitteeFromVoting $ pp ^. ppProtocolVersionL) $
    failOnNonEmpty
      (unelectedCommitteeVoters committee committeeState gsVotingProcedures)
      (injectFailure . UnelectedCommitteeVoters)
```

`hardforkConwayDisallowUnelectedCommitteeFromVoting` returns `True` only when `pvMajor pv > natVersion @10`, meaning the check is **entirely absent from the GOV rule at protocol version 10**. [1](#0-0) [2](#0-1) 

The only enforcement at PV10 lives in `mempoolTransition`:

```haskell
unless (hardforkConwayDisallowUnelectedCommitteeFromVoting protVer) $
  -- This check can completely be removed once mainnet switches to protocol
  -- version 11, since the same check has been implemented in the GOV rule.
  ...
  failOnNonEmpty
    ( unelectedCommitteeVoters ... )
    (ConwayMempoolFailure . addPrefix . T.pack . show . NE.toList)
``` [3](#0-2) 

The `MEMPOOL` rule is applied only to transactions entering the mempool, not during block validation. Block validation applies the `LEDGER` rule (which invokes `GOV`), but **not** `MEMPOOL`. A block producer can forge a block containing a transaction with an unelected committee member's vote, which the `GOV` rule will accept at PV10 without any election-status check.

The `knownCommitteeMembers` set used for the `VotersDoNotExist` check is populated from `authorizedHotCommitteeCredentials committeeState` — all authorized hot credentials, not just those belonging to elected members:

```haskell
knownCommitteeMembers = authorizedHotCommitteeCredentials committeeState
``` [4](#0-3) 

`authorizedHotCommitteeCredentials` returns hot credentials for **all** cold credentials in `CommitteeState`, regardless of whether those cold credentials appear in the current elected `Committee`: [5](#0-4) 

By contrast, `authorizedElectedHotCommitteeCredentials` (used only in the gated `unelectedCommitteeVoters` check) intersects `CommitteeState` with the current elected `Committee`: [6](#0-5) 

The result: at PV10, an unelected committee member who has registered a hot key passes both the `VotersDoNotExist` check and `checkVotersAreValid` (which only checks action-type eligibility, not election status), and their vote is written into `gasCommitteeVotes`. [7](#0-6) 

The existing test suite confirms that at PV10 a pre-election vote **is** counted toward ratification once the member becomes elected: [8](#0-7) 

### Impact Explanation

**Critical — Unauthorized governance action is enacted.**

A block producer at PV10 can include a transaction carrying an unelected committee member's `CommitteeVoter` vote directly in a forged block. The `GOV` rule records the vote in `gasCommitteeVotes`. When the governance action reaches ratification and the member has since been elected, the pre-election vote is counted. This can tip the committee-acceptance threshold, causing a governance action (treasury withdrawal, protocol-parameter change, hard-fork initiation, new constitution, etc.) to be ratified that would not have been ratified with only legitimately-cast votes.

### Likelihood Explanation

**Medium.** The attacker must be a block producer (a realistic role in the allowed attacker profiles). No privileged key or governance majority is required beyond the ability to forge a block. The attack requires coordinating the timing of an `UpdateCommittee` proposal, a hot-key authorization, a pre-election vote included in a forged block, and the subsequent enactment of the committee update — all feasible within normal protocol operation at PV10.

### Recommendation

Remove the `hardforkConwayDisallowUnelectedCommitteeFromVoting` guard from the `UnelectedCommitteeVoters` check in `conwayGovTransition`, or apply the check unconditionally starting from the first post-bootstrap protocol version (PV10). The `MEMPOOL`-only enforcement is insufficient because block producers can bypass mempool admission entirely. The fix already exists for PV11; it should be back-ported to PV10 to close the gap.

### Proof of Concept

1. Network is at Conway protocol version 10 (post-bootstrap, pre-PV11).
2. An `UpdateCommittee` proposal is submitted adding cold credential `ccCold` with a future expiry; it has not yet been enacted.
3. `ccCold` submits `AuthCommitteeHotKeyTxCert ccCold ccHot` — this succeeds because `GOVCERT` does not require the cold credential to be in the current elected committee.
4. A block producer forges a block containing a transaction with `CommitteeVoter ccHot` voting `Yes` on a governance action (e.g., a treasury withdrawal). The `MEMPOOL` rule is **not** invoked during block validation; the `GOV` rule accepts the vote because `hardforkConwayDisallowUnelectedCommitteeFromVoting PV10 == False`.
5. The vote is stored in `gasCommitteeVotes` of the governance action state.
6. In a subsequent epoch the `UpdateCommittee` proposal is ratified and enacted; `ccCold` is now an elected committee member.
7. At the next ratification pulse, `ccHot`'s pre-election `Yes` vote is counted toward the committee threshold, potentially causing the treasury withdrawal to be ratified and enacted without the member having been legitimately elected at the time of voting.

### Citations

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

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Era.hs (L259-262)
```haskell
-- | Starting with protocol version 11, we do not allow unelected committee
-- members to submit votes.
hardforkConwayDisallowUnelectedCommitteeFromVoting :: ProtVer -> Bool
hardforkConwayDisallowUnelectedCommitteeFromVoting pv = pvMajor pv > natVersion @10
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Mempool.hs (L121-135)
```haskell
  whenFailureFreeDefault ledgerState $ do
    let protVer = ledgerEnv ^. Shelley.ledgerPpL . ppProtocolVersionL
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
