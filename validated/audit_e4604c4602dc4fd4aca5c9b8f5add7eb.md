### Title
Unelected Committee Member Votes Accepted by GOV Rule Before Protocol Version 11, Enabling Unauthorized Governance Enactment - (File: `eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Gov.hs`)

---

### Summary

Before protocol version 11, the `GOV` transition rule does not enforce the `UnelectedCommitteeVoters` check. That check lives exclusively in the `MEMPOOL` rule. Because block validation invokes `LEDGER → GOV` directly and never passes through `MEMPOOL`, a block producer can include a transaction containing an unelected committee member's vote directly in a block. The `GOV` rule accepts and records the vote, allowing it to count toward governance ratification thresholds.

---

### Finding Description

`hardforkConwayDisallowUnelectedCommitteeFromVoting` is defined as:

```haskell
hardforkConwayDisallowUnelectedCommitteeFromVoting :: ProtVer -> Bool
hardforkConwayDisallowUnelectedCommitteeFromVoting pv = pvMajor pv > natVersion @10
``` [1](#0-0) 

This returns `False` for protocol versions 9 and 10 (the entire initial Conway deployment).

Inside `conwayGovTransition`, the unelected-committee check is guarded by this flag:

```haskell
when (hardforkConwayDisallowUnelectedCommitteeFromVoting $ pp ^. ppProtocolVersionL) $
  failOnNonEmpty
    (unelectedCommitteeVoters committee committeeState gsVotingProcedures)
    (injectFailure . UnelectedCommitteeVoters)
``` [2](#0-1) 

So at PV 9–10, `conwayGovTransition` never calls `unelectedCommitteeVoters`. The only place that check runs is the `MEMPOOL` rule:

```haskell
unless (hardforkConwayDisallowUnelectedCommitteeFromVoting protVer) $
  -- This check can completely be removed once mainnet switches to protocol
  -- version 11, since the same check has been implemented in the GOV rule.
  --
  -- Disallow votes by unelected committee members
  ...
  failOnNonEmpty
    ( unelectedCommitteeVoters ... )
    (ConwayMempoolFailure . addPrefix . T.pack . show . NE.toList)
``` [3](#0-2) 

The `MEMPOOL` rule is only applied during mempool admission, not during block validation. Block validation applies `BBODY → LEDGER → GOV`. An unelected committee member's hot credential is present in `knownCommitteeMembers` because `authorizedHotCommitteeCredentials` returns all hot credentials in `CommitteeState` regardless of election status:

```haskell
knownCommitteeMembers = authorizedHotCommitteeCredentials committeeState
``` [4](#0-3) 

Therefore the vote passes the `VotersDoNotExist` check. The `checkVotersAreValid` function only checks whether the voter *type* is allowed for the action type (e.g., committee cannot vote on `UpdateCommittee`); it does not check whether the specific committee member is elected:

```haskell
CommitteeVoter {} -> isCommitteeVotingAllowed currentEpoch committeeState (gasAction gas)
``` [5](#0-4) 

The vote is then recorded into `gasCommitteeVotes` and participates in ratification.

---

### Impact Explanation

An unelected committee member's yes-vote can be the deciding vote that pushes a governance action past the committee ratification threshold. Governance actions that can be enacted this way include `TreasuryWithdrawals`, `HardForkInitiation`, `ParameterChange`, and `NewConstitution`. This maps to:

- **Critical**: Unauthorized governance, treasury, protocol-parameter, committee, constitution, or hard-fork action is enacted.

---

### Likelihood Explanation

The attacker must be, or collude with, a block producer who includes the crafted transaction directly into a block rather than routing it through the mempool. This is a "block producer below consensus threshold" scenario explicitly listed in scope. The unelected committee member only needs to have submitted an `AuthCommitteeHotKey` certificate (a normal on-chain operation) and then construct a voting transaction. No key compromise or supermajority is required. The window is the entire PV 9–10 deployment period of Conway.

---

### Recommendation

Move the `unelectedCommitteeVoters` enforcement unconditionally into `conwayGovTransition` for all Conway protocol versions, rather than relying on the `MEMPOOL` rule as the sole enforcement point before PV 11. The `MEMPOOL` rule is not part of the consensus-critical validation path and cannot be relied upon to enforce ledger invariants.

---

### Proof of Concept

1. Network is running at protocol version 9 or 10 (Conway era, `hardforkConwayDisallowUnelectedCommitteeFromVoting = False`).
2. Attacker submits an `AuthCommitteeHotKey` certificate for a cold credential that is proposed but not yet enacted as a committee member (e.g., pending in an `UpdateCommittee` proposal).
3. A governance action (e.g., `TreasuryWithdrawals`) is live and needs one more committee yes-vote to reach the ratification threshold.
4. Attacker constructs a transaction containing `VotingProcedures { CommitteeVoter hotCred → VoteYes }`.
5. Submitting via the mempool fails: `ConwayMempoolFailure "Unelected committee members are not allowed to cast votes: ..."`.
6. Attacker (who is also a stake pool operator, or colludes with one) includes the transaction directly in a produced block.
7. Block validation runs `BBODY → LEDGER → GOV → conwayGovTransition`. The `when (hardforkConwayDisallowUnelectedCommitteeFromVoting ...)` guard is `False`, so `unelectedCommitteeVoters` is never called. The vote passes `VotersDoNotExist` (hot credential is in `CommitteeState`) and `checkVotersAreValid` (committee voting is allowed for `TreasuryWithdrawals`).
8. The vote is recorded. At the next epoch boundary, the ratification threshold is met and the treasury withdrawal is enacted.

### Citations

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Era.hs (L259-262)
```haskell
-- | Starting with protocol version 11, we do not allow unelected committee
-- members to submit votes.
hardforkConwayDisallowUnelectedCommitteeFromVoting :: ProtVer -> Bool
hardforkConwayDisallowUnelectedCommitteeFromVoting pv = pvMajor pv > natVersion @10
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Gov.hs (L373-376)
```haskell
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
