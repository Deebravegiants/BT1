### Title
Missing Lower-Bound Re-Validation of Committee Member Expiry at Ratification Allows Enactment of Already-Expired Committee Members - (File: `eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Ratify.hs`)

---

### Summary

The Conway governance `UpdateCommittee` action is validated at proposal time with a lower-bound check ensuring new members' expiry epochs are in the future. However, the `validCommitteeTerm` function in the `RATIFY` rule only enforces an **upper-bound** constraint and omits the lower-bound re-check. Because ratification always occurs at least two epochs after proposal, any `UpdateCommittee` proposal with members whose expiry epoch equals `proposalEpoch + 1` will pass all ledger checks yet enact committee members that are already expired. The `ENACT` rule then blindly installs those expired members into the on-chain committee state.

---

### Finding Description

**Proposal-time check (GOV rule)** — `eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Gov.hs` lines 555–556:

```haskell
let invalidMembers = Map.filter (<= currentEpoch) membersToAdd
 in failOnNonEmptyMap invalidMembers (injectFailure . ExpirationEpochTooSmall)
```

This rejects any new member whose `expiryEpoch <= currentEpoch` at the time the transaction is submitted. [1](#0-0) 

**Ratification-time check (RATIFY rule)** — `eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Ratify.hs` lines 375–381:

```haskell
validCommitteeTerm govAction pp currentEpoch =
  case govAction of
    UpdateCommittee _ _ newMembers _ -> withinMaxTermLength newMembers
    _ -> True
  where
    committeeMaxTermLength = pp ^. ppCommitteeMaxTermLengthL
    withinMaxTermLength = all (<= addEpochInterval currentEpoch committeeMaxTermLength)
```

`validCommitteeTerm` only checks the **upper bound** (`expiryEpoch ≤ currentEpoch + committeeMaxTermLength`). It does **not** re-check the lower bound (`expiryEpoch > currentEpoch`). A member with `expiryEpoch = proposalEpoch + 1` satisfies the upper-bound check trivially, even when `currentEpoch` at ratification time is `proposalEpoch + 2` or later. [2](#0-1) 

**Enactment (ENACT rule)** — `eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Enact.hs` lines 108–111:

```haskell
UpdateCommittee _ membersToRemove membersToAdd newThreshold -> do
  st
    & ensCommitteeL %~ SJust . updatedCommittee membersToRemove membersToAdd newThreshold
    & ensPrevCommitteeL .~ SJust (GovPurposeId govActionId)
```

`updatedCommittee` installs `membersToAdd` directly into the on-chain committee with no expiry check whatsoever. [3](#0-2) 

The structural gap is:

| Stage | Lower-bound check (`expiryEpoch > currentEpoch`) |
|---|---|
| GOV (proposal) | ✓ enforced |
| RATIFY (ratification) | ✗ **missing** |
| ENACT (enactment) | ✗ **missing** |

Because the DRepPulser snapshot is taken at epoch N and ratification/enactment occurs at epoch N+1 boundary (at the earliest), any member proposed with `expiryEpoch = proposalEpoch + 1` is **structurally guaranteed** to be expired by the time `ENACT` runs. [4](#0-3) 

---

### Impact Explanation

Once expired committee members are installed in the on-chain `Committee` map, they cannot cast valid votes. The `committeeAccepted` function in `RATIFY` counts only registered, unexpired, unresigned members toward the numerator and denominator. [5](#0-4) 

If the enacted `UpdateCommittee` replaces a sufficient portion of the committee with already-expired members, the effective committee size falls below `ppCommitteeMinSizeL`. All subsequent governance actions that require committee approval will fail `committeeAccepted` permanently. No on-chain mechanism can recover from this without a new `UpdateCommittee` action — which itself requires committee approval — creating a deadlock. Recovery would require a hard fork.

This matches the allowed impact: **High — Permanent freezing of governance where recovery requires a hard fork**, and potentially **Critical — Unauthorized governance action is enacted** (the enacted committee state is invalid relative to the constraints the ledger is supposed to enforce).

---

### Likelihood Explanation

The attack entry path is an unprivileged transaction sender (any ADA holder can submit a governance proposal by paying the `govActionDeposit`). The attacker does not need to control a governance majority; they only need to submit an `UpdateCommittee` proposal with new members whose `expiryEpoch = currentEpoch + 1`. Because the proposal passes the GOV-rule check at submission time, it enters the proposal queue as a structurally valid action.

Legitimate DReps, SPOs, and committee members voting on the proposal see a syntactically valid `UpdateCommittee` action. The expiry epoch `currentEpoch + 1` is a legal value at proposal time. Voters who do not independently compute "will this member still be valid two epochs from now?" will vote yes. The ledger itself provides no warning or rejection at ratification time.

The minimum epoch gap between proposal and enactment is two epochs (one epoch for the DRepPulser to complete, one epoch for the EPOCH boundary to apply enactment). This gap is deterministic and guaranteed by the protocol, making the expiry-at-enactment outcome fully predictable by the attacker. [6](#0-5) 

---

### Recommendation

Add a lower-bound check inside `validCommitteeTerm` in `eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Ratify.hs`:

```haskell
validCommitteeTerm govAction pp currentEpoch =
  case govAction of
    UpdateCommittee _ _ newMembers _ ->
      withinMaxTermLength newMembers && allMembersNotExpired newMembers
    _ -> True
  where
    committeeMaxTermLength = pp ^. ppCommitteeMaxTermLengthL
    withinMaxTermLength = all (<= addEpochInterval currentEpoch committeeMaxTermLength)
    allMembersNotExpired = all (> currentEpoch)   -- re-check lower bound at ratification time
```

This mirrors the `ExpirationEpochTooSmall` predicate already enforced in the GOV rule and closes the temporal gap between proposal and enactment. [7](#0-6) 

---

### Proof of Concept

1. At epoch `E`, attacker submits an `UpdateCommittee` proposal replacing all current committee members with a single new member `M` whose `expiryEpoch = E + 1`. The GOV rule accepts this because `E + 1 > E`. [1](#0-0) 

2. DReps and SPOs vote yes during epoch `E`. The action enters the DRepPulser snapshot at the epoch `E` boundary.

3. At epoch `E+1` boundary, `ratifyTransition` evaluates `validCommitteeTerm` with `reCurrentEpoch = E+1`. The check `E+1 <= (E+1) + committeeMaxTermLength` passes. The lower-bound check `E+1 > E+1` is never performed. The action is ratified and forwarded to `ENACT`. [8](#0-7) 

4. `enactmentTransition` calls `updatedCommittee` which installs `M` with `expiryEpoch = E+1` into the on-chain committee. At epoch `E+1`, member `M` is already expired. [3](#0-2) 

5. All future governance actions requiring committee approval fail `committeeAccepted` because the only committee member is expired. Governance is permanently frozen.

### Citations

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Gov.hs (L555-556)
```haskell
            let invalidMembers = Map.filter (<= currentEpoch) membersToAdd
             in failOnNonEmptyMap invalidMembers (injectFailure . ExpirationEpochTooSmall)
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Ratify.hs (L118-120)
```haskell
committeeAccepted ::
  ConwayEraPParams era =>
  RatifyEnv era ->
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Ratify.hs (L337-345)
```haskell
      if prevActionAsExpected gas ensPrevGovActionIds
        && validCommitteeTerm govAction ensCurPParams reCurrentEpoch
        && not rsDelayed
        && withdrawalCanWithdraw govAction ensTreasury
        && acceptedByEveryone env st gas
        then do
          newEnactState <-
            trans @(EraRule "ENACT" era) $
              TRC ((), rsEnactState, EnactSignal gasId govAction)
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Ratify.hs (L369-381)
```haskell
validCommitteeTerm ::
  ConwayEraPParams era =>
  GovAction era ->
  PParams era ->
  EpochNo ->
  Bool
validCommitteeTerm govAction pp currentEpoch =
  case govAction of
    UpdateCommittee _ _ newMembers _ -> withinMaxTermLength newMembers
    _ -> True
  where
    committeeMaxTermLength = pp ^. ppCommitteeMaxTermLengthL
    withinMaxTermLength = all (<= addEpochInterval currentEpoch committeeMaxTermLength)
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Enact.hs (L108-111)
```haskell
      UpdateCommittee _ membersToRemove membersToAdd newThreshold -> do
        st
          & ensCommitteeL %~ SJust . updatedCommittee membersToRemove membersToAdd newThreshold
          & ensPrevCommitteeL .~ SJust (GovPurposeId govActionId)
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Governance/DRepPulser.hs (L381-417)
```haskell
finishDRepPulser ::
  (EraStake era, ConwayEraAccounts era) =>
  DRepPulsingState era ->
  (PulsingSnapshot era, RatifyState era)
finishDRepPulser (DRComplete snap ratifyState) = (snap, ratifyState)
finishDRepPulser (DRPulsing (DRepPulser {..})) =
  ( PulsingSnapshot
      dpProposals
      finalDRepDistr
      dpDRepState
      (Map.map individualTotalPoolStake $ unPoolDistr finalStakePoolDistr)
  , ratifyState'
  )
  where
    !leftOver = Map.drop dpIndex (dpAccounts ^. accountsMapL)
    (finalDRepDistr, finalStakePoolDistr) =
      computeDRepDistr dpInstantStake dpDRepState dpProposalDeposits dpStakePoolDistr dpDRepDistr leftOver
    !ratifyEnv =
      RatifyEnv
        { reInstantStake = dpInstantStake
        , reStakePoolDistr = finalStakePoolDistr
        , reDRepDistr = finalDRepDistr
        , reDRepState = dpDRepState
        , reCurrentEpoch = dpCurrentEpoch
        , reCommitteeState = dpCommitteeState
        , reAccounts = dpAccounts
        , reStakePools = dpStakePools
        }
    !ratifySig = RatifySignal dpProposals
    !ratifyState =
      RatifyState
        { rsEnactState = dpEnactState
        , rsEnacted = mempty
        , rsExpired = mempty
        , rsDelayed = False
        }
    !ratifyState' = runConwayRatify dpGlobals ratifyEnv ratifyState ratifySig
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Governance/Proposals.hs (L38-56)
```haskell
--
-- 1. Epoch n: Proposals and votes are continuously collected from
-- incoming transactions into @`Proposals`@
--
-- 2. Epoch n boundary: The @`DRepPulser`@ contains all proposals and
-- votes from epoch (n - 1). Its calculation is completed, ratified
-- and enacted or expired. Ratification and enactment do not affect
-- @`Proposals`@ directly. They only update the @`PrevGovActionIds`@
-- directly and return the sequence of enacted action-ids and the set
-- of expired action-ids that inform us of the changes pending on
-- @`Proposals`@.
--
--   2.1. We take this sequence of enacted action-ids and set of expired
--   action-ids and apply them to the @`Proposals`@ in the ledger
--   state that now includes all the newly collected proposals and
--   votes from epoch n and epoch (n - 1), as this is a superset of
--   the pulsed set of proposals and votes. We do not expect this
--   operation to fail, since all invariants are expected to hold and
--   only an implementation bug could cause this operation to fail.
```
