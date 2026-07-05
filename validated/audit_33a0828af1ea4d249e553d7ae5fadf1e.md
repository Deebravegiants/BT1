### Title
Persistent Hot Key Authorization After `UpdateCommittee` Proposal Rejection Creates Invalid Committee State - (File: `eras/conway/impl/src/Cardano/Ledger/Conway/Rules/GovCert.hs`)

---

### Summary

The `GOVCERT` rule's `conwayGovCertTransition` permits a cold credential to authorize a hot key based solely on membership in a **pending, unratified** `UpdateCommittee` proposal. If that proposal is subsequently rejected or expires, the hot key authorization persists in `csCommitteeCredsL` — an exact analog to the Vault report's "migrate outside vault context" pattern, where an operation is performed in a context that may never be validated, leaving the system in an incoherent state. At protocol version 10 (pre-`hardforkConwayDisallowUnelectedCommitteeFromVoting`), this allows an unprivileged transaction sender to submit committee votes that pass the `GOV` rule's validation but are silently discarded during ratification, exceeding intended validation limits.

---

### Finding Description

In `conwayGovCertTransition`, the inner helper `checkAndOverwriteCommitteeMemberState` decides whether to accept a `ConwayAuthCommitteeHotKey` certificate:

```haskell
let isCurrentMember =
      strictMaybe False (Map.member coldCred . committeeMembers) cgceCurrentCommittee
    committeeUpdateContainsColdCred GovActionState {gasProposalProcedure} =
      case pProcGovAction gasProposalProcedure of
        UpdateCommittee _ _ newMembers _ -> Map.member coldCred newMembers
        _ -> False
    isPotentialFutureMember =
      any committeeUpdateContainsColdCred cgceCommitteeProposals
isCurrentMember || isPotentialFutureMember
  ?! (injectFailure . ConwayCommitteeIsUnknown) coldCred
pure $
  certState
    & certVStateL . vsCommitteeStateL . csCommitteeCredsL
      %~ Map.insert coldCred newMemberState
```

<cite repo="Linkmegit/cardano-ledger--027" path="eras/conway/impl/src/Cardano/Ledger/Conway/Rules/GovCert.hs"