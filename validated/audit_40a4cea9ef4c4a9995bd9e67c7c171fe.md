### Title
Unelected Committee Voter Check Absent from Block Validation in Conway Era — (File: `eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Gov.hs`)

### Summary

In Conway era (protocol version 9–10), the `unelectedCommitteeVoters` safety check is only enforced inside the `MEMPOOL` rule (a pre-block mempool filter), not inside the `GOV` rule (the authoritative block-validation transition). Because the `MEMPOOL` rule is bypassed when a block producer assembles a block directly, a block producer can include a transaction carrying votes from unelected committee members. The `GOV` rule in Conway era accepts those votes unconditionally, storing them in `gasCommitteeVotes` where the ratification engine can count them.

### Finding Description

**Root cause — the hardfork gate in `conwayGovTransition`:**

```haskell
-- Gov.hs lines 478-481
when (hardforkConwayDisallowUnelectedCommitteeFromVoting $ pp ^. ppProtocolVersionL) $
  failOnNonEmpty
    (unelectedCommitteeVoters committee committeeState gsVotingProcedures)
    (injectFailure . Un