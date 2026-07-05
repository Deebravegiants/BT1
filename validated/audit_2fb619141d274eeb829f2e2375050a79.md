### Title
Attacker-Controlled `UpdateCommittee` Proposal Enables Unauthorized Committee Hot-Key Authorization and Voting Before `hardforkConwayDisallowUnelectedCommitteeFromVoting` - (File: eras/conway/impl/src/Cardano/Ledger/Conway/Rules/GovCert.hs)

---

### Summary

The GOVCERT rule's `checkAndOverwriteCommitteeMemberState` helper permits any cold credential that appears in a **pending, unratified** `UpdateCommittee` governance proposal to immediately authorize a committee hot key. At protocol versions below the `hardforkConwayDisallowUnelectedCommitteeFromVoting` threshold, the GOV rule contains no guard against votes cast by such unelected committee members. An unprivileged attacker can therefore submit a self-referencing `UpdateCommittee` proposal, authorize a hot key for their own cold credential, and cast committee votes that are accepted and counted toward governance ratification thresholds—potentially enacting unauthorized treasury withdrawals, protocol-parameter changes, or hard-fork initiations.

---

### Finding Description

Two cooperating code paths form the root cause.

**Path 1 — GOVCERT rule (`eras/conway/impl/src/Cardano/Ledger/Conway/Rules/GovCert.hs`, lines 190–208)**

`checkAndOverwriteCommitteeMemberState` is called for both `ConwayAuthCommitteeHotKey` and `ConwayResignCommitteeColdKey`. It accepts a cold credential if either `isCurrentMember` **or** `isPotentialFutureMember` is `True`:

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

`cgceCommitteeProposals` contains **all live, unratified** `UpdateCommittee` proposals. An attacker who submits such a proposal in transaction T can, in the very next transaction, submit `ConwayAuthCommitteeHotKey coldCredA hotCredA` and have it accepted—because `isPotentialFutureMember` is already `True`. The hot credential is then inserted into `csCommitteeCredsL`, making it part of `authorizedHotCommitteeCredentials committeeState`.

**Path 2 — GOV rule (`eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Gov.hs`, lines 478–481)**

```haskell
when (hardforkConwayDisallowUnelectedCommitteeFromVoting $ pp ^. ppProtocolVersionL) $
  failOnNonEmpty
    (unelectedCommitteeVoters committee committeeState gsVotingProcedures)
    (injectFailure . UnelectedCommitteeVoters)
```

This guard is **absent** at protocol versions below the `hardforkConwayDisallowUnelectedCommitteeFromVoting` threshold. The only remaining check is `VotersDoNotExist`, which passes because `hotCredA` is now in `knownCommitteeMembers` (derived from `authorizedHotCommitteeCredentials committeeState`). The vote is therefore stored in `gasCommitteeVotes` and counted during ratification.

**End-to-end attack path (protocol version < threshold):**

1. Attacker submits an `UpdateCommittee` proposal that includes their own cold credential `coldCredA` (pays `ppGovActionDepositL`; no other privilege required).
2. Attacker submits `ConwayAuthCommitteeHotKey coldCredA hotCredA`; passes `checkAndOverwriteCommitteeMemberState` because `isPotentialFutureMember` is `True`. `hotCredA` is inserted into `csCommitteeCredsL`.
3. Attacker submits `VoteYes (CommitteeVoter hotCredA) targetGovActionId`. The `VotersDoNotExist` check passes; the `UnelectedCommitteeVoters` guard is absent at this protocol version.
4. The vote is stored in `gasCommitteeVotes` and counted toward the committee ratification threshold.
5. If the attacker's vote tips the threshold, the targeted governance action (e.g., `TreasuryWithdrawals`, `ParameterChange`, `HardForkInitiation`) is ratified and enacted.

The test at `eras/conway/impl/testlib/Test/Cardano/Ledger/Conway/Imp/GovCertSpec.hs` line 208–209 explicitly demonstrates that submitting an `UpdateCommittee` proposal is sufficient to unblock `AuthCommitteeHotKeyTxCert` for an otherwise unknown cold credential. The test at `eras/conway/impl/testlib/Test/Cardano/Ledger/Conway/Imp/RatifySpec.hs` lines 1883–1906 confirms that before `hardforkConwayDisallowUnelectedCommittee