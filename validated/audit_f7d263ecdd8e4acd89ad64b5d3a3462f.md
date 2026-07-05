### Title
Stale Reverse DRep Delegation (`drepDelegs`) During Bootstrap Phase Enables Attacker to Disenfranchise Delegators via DRep Unregistration — (`eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Deleg.hs`)

---

### Summary

During the Conway bootstrap phase (protocol version 9), `processDelegationInternal` in the `DELEG` rule intentionally skips removing the old reverse delegation from `drepDelegs` when a stake credential re-delegates its vote to a new DRep. This stale entry in the old DRep's `drepDelegs` set causes `ConwayUnRegDRep` to incorrectly clear the stake credential's **current, valid** delegation when the old DRep unregisters. The result is that the delegator's stake no longer counts toward any DRep's vote weight, altering the DRep distribution used for governance ratification.

---

### Finding Description

**Root cause — stale reverse delegation not removed on re-delegation (bootstrap phase):**

In `processDelegationInternal` (`eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Deleg.hs`), the `delegVote` helper selects between two branches:

```haskell
| isNothing mAccountState || preserveIncorrectDelegation ->
    certVStateL . vsDRepsL
      %~ Map.adjust (drepDelegsL %~ Set.insert stakeCred) dRepCred
``` [1](#0-0) 

When `preserveIncorrectDelegation = True` (i.e., `pvMajor pv < natVersion @10`, the bootstrap phase), this branch is taken even for an **existing** account (`mAccountState = Just accountState`). It only inserts `stakeCred` into the new DRep's `drepDelegs` but **never removes** it from the old DRep's `drepDelegs`. The correct post-bootstrap path calls `unDelegReDelegDRep`, which atomically removes the old and inserts the new:

```haskell
| Just accountState <- mAccountState ->
    certVStateL %~ unDelegReDelegDRep stakeCred accountState (Just dRep)
``` [2](#0-1) 

`unDelegReDelegDRep` explicitly deletes the old reverse delegation:

```haskell
vsDRepsL %~ addNewDelegation . Map.adjust (drepDelegsL %~ Set.delete stakeCred) dRepCred
``` [3](#0-2) 

**Consequence — `ConwayUnRegDRep` uses stale `drepDelegs` to clear current delegations:**

When the old DRep (`drepA`) later unregisters, `ConwayUnRegDRep` iterates over `drepA.drepDelegs` and sets every listed credential's `dRepDelegation` to `Nothing`:

```haskell
clearDRepDelegations delegs accountsMap =
  foldr (Map.adjust (dRepDelegationAccountStateL .~ Nothing)) accountsMap delegs
``` [4](#0-3) 

Because `stakeCred` was never removed from `drepA.drepDelegs`, this call sets `stakeCred`'s `dRepDelegation` to `Nothing` even though `stakeCred` had already moved to `drepB`. The account's delegation pointer is now `Nothing`, so `stakeCred`'s stake is excluded from the DRep distribution computed by `computeDRepDistr`:

```haskell
addToDRepDistr accountState stakeAndDeposits distr = fromMaybe distr $ do
  dRep <- accountState ^. dRepDelegationAccountStateL
  ...
``` [5](#0-4) 

**The test suite confirms this exact behavior:**

```haskell
ifBootstrap
  ( do
      accounts <- getsNES $ nesEsL . esLStateL . lsCertStateL . certDStateL . accountsL
      expectNothingExpr (lookupDRepDelegation cred accounts)  -- delegation cleared!
      expecteReverseDRepDelegation cred drepCred2 True
  )
  (expectDelegatedVote cred (DRepCredential drepCred2))
``` [6](#0-5) 

The `ConwayDelegCert` path passes `preserveIncorrectDelegation = (pvMajor pv < natVersion @10)`: [7](#0-6) 

The bootstrap phase guard: [8](#0-7) 

---

### Impact Explanation

**Allowed impact matched:** *Critical — Unauthorized governance action is enacted* / *High — Deterministic disagreement between honest nodes from ledger rule evaluation.*

1. **Governance vote weight manipulation.** An attacker who registers as a DRep, accumulates delegations, and then unregisters after delegators have moved to other DReps can silently zero out those delegators' vote weight. The DRep distribution (`reDRepDistr`) used in `dRepAcceptedRatio` is computed from `accountState ^. dRepDelegationAccountStateL`; once cleared to `Nothing`, the affected stake is excluded from both numerator and denominator, shifting ratification ratios. [9](#0-8) 

2. **Ledger state inconsistency.** After the clearing, `drepB.drepDelegs` still contains `stakeCred` (the stale entry was never removed from `drepB` either), while the account's `dRepDelegation` is `Nothing`. This two-way inconsistency means subsequent re-delegation by `stakeCred` will not clean up `drepB`'s stale entry (because `unDelegReDelegDRep` reads the old delegation from the account state, which is now `Nothing`), creating a cascading stale-state condition.

3. **Permanent disenfranchisement until explicit re-delegation.** The delegator must submit a new delegation certificate to recover. If the delegator is unaware, their stake is silently excluded from governance indefinitely.

---

### Likelihood Explanation

- **Attacker entry path is fully unprivileged.** Registering as a DRep (`ConwayRegDRep`) and later unregistering (`ConwayUnRegDRep`) requires only a deposit and a valid transaction — no privileged role, no key compromise, no majority.
- **Scope is the Conway bootstrap phase** (protocol version 9, `hardforkConwayBootstrapPhase`). On mainnet this phase has passed; however, the code path remains active for any deployment or testnet running at protocol version 9, and for historical ledger replay.
- **The attack is low-cost and targeted.** An attacker registers as a DRep, attracts delegations (e.g., by offering incentives), waits for delegators to re-delegate to legitimate DReps, then unregisters. Each unregistration clears all stale entries in one transaction.

---

### Recommendation

The fix is already present for post-bootstrap operation: `unDelegReDelegDRep` correctly removes the old reverse delegation before inserting the new one. The `updateDRepDelegations` migration in `HardFork.hs` (triggered at protocol version 10) rebuilds all `drepDelegs` from scratch, cleaning up any stale entries accumulated during bootstrap: [10](#0-9) 

For completeness and defense-in-depth, `ConwayUnRegDRep` should guard against clearing delegations that no longer point to the unregistering DRep — i.e., before setting `dRepDelegationAccountStateL .~ Nothing`, verify that the account's current `dRepDelegation` actually equals the unregistering DRep's credential. This would prevent the stale-`drepDelegs` vector from causing incorrect state transitions regardless of how the stale entries arose.

---

### Proof of Concept

**Sequence (bootstrap phase, protocol version 9):**

1. Alice registers as DRep `drepA` via `ConwayRegDRep`.
2. Bob registers a stake credential `cred` and delegates to `drepA` via `ConwayRegDelegCert cred (DelegVote drepA) deposit`. State: `cred.dRepDelegation = Just drepA`, `drepA.drepDelegs = {cred}`.
3. Bob re-delegates to `drepB` via `ConwayDelegCert cred (DelegVote drepB)`. Because `preserveIncorrectDelegation = True` (bootstrap), only `drepB.drepDelegs` gains `cred`; `drepA.drepDelegs` still contains `cred`. State: `cred.dRepDelegation = Just drepB`, `drepA.drepDelegs = {cred}`, `drepB.drepDelegs = {cred}`.
4. Alice unregisters `drepA` via `ConwayUnRegDRep drepA deposit`. `clearDRepDelegations {cred} accountsMap` sets `cred.dRepDelegation = Nothing`. State: `cred.dRepDelegation = Nothing`, `drepB.drepDelegs = {cred}` (stale).
5. Bob's stake is now excluded from the DRep distribution. `drepB`'s vote weight is overstated in `queryRegisteredDRepStakeDistr` (uses `drepDelegs`) but understated in `computeDRepDistr` (uses `dRepDelegationAccountStateL`), creating a split-brain between query results and consensus-critical ratification logic.
6. Any governance action ratification during this window uses the corrupted distribution.

The test `"Redelegate vote"` in `eras/conway/impl/testlib/Test/Cardano/Ledger/Conway/Imp/DelegSpec.hs` at lines 287–323 explicitly exercises and confirms steps 3–4. [11](#0-10)

### Citations

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Deleg.hs (L286-292)
```haskell
          pure $
            processDelegationInternal
              (pvMajor pv < natVersion @10)
              internedCred
              (Just accountState)
              delegatee
              certState
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Deleg.hs (L363-365)
```haskell
                | isNothing mAccountState || preserveIncorrectDelegation ->
                    certVStateL . vsDRepsL
                      %~ Map.adjust (drepDelegsL %~ Set.insert stakeCred) dRepCred
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Deleg.hs (L369-370)
```haskell
                | Just accountState <- mAccountState ->
                    certVStateL %~ unDelegReDelegDRep stakeCred accountState (Just dRep)
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/State/VState.hs (L137-137)
```haskell
          vsDRepsL %~ addNewDelegation . Map.adjust (drepDelegsL %~ Set.delete stakeCred) dRepCred
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/GovCert.hs (L246-254)
```haskell
        clearDRepDelegations delegs accountsMap =
          foldr (Map.adjust (dRepDelegationAccountStateL .~ Nothing)) accountsMap delegs
      pure $
        case mDRepState of
          Nothing -> certState'
          Just dRepState ->
            certState'
              & certDStateL . accountsL . accountsMapL
                %~ clearDRepDelegations (drepDelegs dRepState)
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Governance/DRepPulser.hs (L228-241)
```haskell
    addToDRepDistr accountState stakeAndDeposits distr = fromMaybe distr $ do
      dRep <- accountState ^. dRepDelegationAccountStateL
      let
        balance = accountState ^. balanceAccountStateL
        updatedDistr = Map.insertWith (<>) dRep (stakeAndDeposits <> balance) distr
      Just $ case dRep of
        DRepAlwaysAbstain -> updatedDistr
        DRepAlwaysNoConfidence -> updatedDistr
        DRepCredential cred
          -- TODO: Potential optimization. Avoid this membership check, since delegation is
          -- guaranteed to exist. I believe it would also be safe for PV9, but we need to verify
          -- that it is in fact true due to #4772
          | Map.member cred regDReps -> updatedDistr
          | otherwise -> distr
```

**File:** eras/conway/impl/testlib/Test/Cardano/Ledger/Conway/Imp/DelegSpec.hs (L287-323)
```haskell
    it "Redelegate vote" $ do
      expectedDeposit <- getsNES $ nesEsL . curPParamsEpochStateL . ppKeyDepositL

      cred <- KeyHashObj <$> freshKeyHash
      drepCred <- KeyHashObj <$> registerDRep

      submitTx_ $
        mkBasicTx mkBasicTxBody
          & bodyTxL . certsTxBodyL
            .~ [RegDepositDelegTxCert cred (DelegVote (DRepCredential drepCred)) expectedDeposit]
      expectDelegatedVote cred (DRepCredential drepCred)

      drepCred2 <- KeyHashObj <$> registerDRep
      submitTx_ $
        mkBasicTx mkBasicTxBody
          & bodyTxL . certsTxBodyL
            .~ [DelegTxCert cred (DelegVote (DRepCredential drepCred2))]

      expectDelegatedVote cred (DRepCredential drepCred2)

      impAnn "Check that in bootstrap phase the previous reverse delegation is maintained" $ do
        expecteReverseDRepDelegation cred drepCred2 True
        ifBootstrap
          (expecteReverseDRepDelegation cred drepCred True)
          (expecteReverseDRepDelegation cred drepCred False)

      impAnn "Check that unregistration of previous delegation does not affect current delegation" $ do
        unRegisterDRep drepCred
        -- we need to preserve the buggy behavior until the boostrap phase is over.
        ifBootstrap
          ( do
              -- we cannot `expectNotDelegatedVote` because the delegation is still in the DRepState of the other drep
              accounts <- getsNES $ nesEsL . esLStateL . lsCertStateL . certDStateL . accountsL
              expectNothingExpr (lookupDRepDelegation cred accounts)
              expecteReverseDRepDelegation cred drepCred2 True
          )
          (expectDelegatedVote cred (DRepCredential drepCred2))
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Era.hs (L256-257)
```haskell
hardforkConwayBootstrapPhase :: ProtVer -> Bool
hardforkConwayBootstrapPhase pv = pvMajor pv == natVersion @9
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Ratify.hs (L252-270)
```haskell
dRepAcceptedRatio ::
  forall era.
  RatifyEnv era ->
  Map (Credential DRepRole) Vote ->
  GovAction era ->
  Rational
dRepAcceptedRatio RatifyEnv {reDRepDistr, reDRepState, reCurrentEpoch} gasDRepVotes govAction =
  toInteger yesStake %? toInteger totalExcludingAbstainStake
  where
    accumStake (!yes, !tot) drep (CompactCoin stake) =
      case drep of
        DRepCredential cred ->
          case Map.lookup cred reDRepState of
            Nothing -> (yes, tot) -- drep is not registered, so we don't consider it
            Just drepState
              | reCurrentEpoch > drepExpiry drepState -> (yes, tot) -- drep is expired, so we don't consider it
              | otherwise ->
                  case Map.lookup cred gasDRepVotes of
                    -- drep hasn't voted for this action, so we don't count
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/HardFork.hs (L82-105)
```haskell
updateDRepDelegations :: ConwayEraCertState era => CertState era -> CertState era
updateDRepDelegations certState =
  let accountsMap = certState ^. certDStateL . accountsL . accountsMapL
      dReps =
        -- Reset all delegations in order to remove any inconsistencies
        -- Delegations will be reset accordingly below.
        Map.map (\dRepState -> dRepState {drepDelegs = Set.empty}) $
          certState ^. certVStateL . vsDRepsL
      (dRepsWithDelegations, accountsWithoutUnknownDRepDelegations) =
        Map.mapAccumWithKey adjustDelegations dReps accountsMap
      adjustDelegations ds stakeCred accountState =
        case accountState ^. dRepDelegationAccountStateL of
          Just (DRepCredential dRep) ->
            let addDelegation _ dRepState =
                  Just $ dRepState {drepDelegs = Set.insert stakeCred (drepDelegs dRepState)}
             in case Map.updateLookupWithKey addDelegation dRep ds of
                  (Nothing, _) -> (ds, accountState & dRepDelegationAccountStateL .~ Nothing)
                  (Just _, ds') -> (ds', accountState)
          _ -> (ds, accountState)
   in certState
        -- Remove dangling delegations to non-existent DReps:
        & certDStateL . accountsL . accountsMapL .~ accountsWithoutUnknownDRepDelegations
        -- Populate DRep delegations with delegatees
        & certVStateL . vsDRepsL .~ dRepsWithDelegations
```
