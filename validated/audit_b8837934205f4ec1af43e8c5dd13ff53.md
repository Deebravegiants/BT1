### Title
Stale DRep Reverse Delegation During Bootstrap Phase Allows Unregistering DRep to Silently Clear Delegators' Active Vote Delegations - (File: `eras/conway/impl/src/Cardano/Ledger/Conway/Rules/GovCert.hs`)

---

### Summary

During the Conway bootstrap phase (protocol version 9), when a stake credential re-delegates its vote from DRep A to DRep B, the old reverse-delegation entry in DRep A's `drepDelegs` set is intentionally not removed (issue #4772). When DRep A subsequently submits a `ConwayUnRegDRep` certificate, the `clearDRepDelegations` helper in the `GOVCERT` rule unconditionally sets `dRepDelegationAccountStateL .~ Nothing` for every credential in DRep A's stale `drepDelegs` — including credentials whose canonical delegation already points to DRep B. There is no check that a credential's current delegation still targets the unregistering DRep before clearing it. The result is that an attacker-controlled DRep unregistration silently erases active vote delegations belonging to users who have already moved to a different DRep, reducing that DRep's governance voting power without any action by the affected delegators.

---

### Finding Description

**Root cause — missing cleanup on re-delegation (bootstrap phase)**

In `processDelegationInternal`, the `delegVote` branch is called with `preserveIncorrectDelegation = True` whenever `pvMajor pv < natVersion @10` (i.e., the bootstrap phase, PV9): [1](#0-0) 

When `preserveIncorrectDelegation` is `True` and the new target is a credential DRep, the code only **adds** the stake credential to the new DRep's `drepDelegs` set; it never **removes** it from the old DRep's `drepDelegs` set: [2](#0-1) 

After re-delegation, the canonical source of truth (`accountState.dRepDelegationAccountStateL`) correctly records DRep B, but DRep A's `DRepState.drepDelegs` still contains the stake credential as a stale entry.

**Exploitable consequence — unconditional delegation clear on DRep unregistration**

When DRep A unregisters via `ConwayUnRegDRep`, the `GOVCERT` rule calls `clearDRepDelegations` using DRep A's (stale) `drepDelegs`: [3](#0-2) 

`clearDRepDelegations` unconditionally sets `dRepDelegationAccountStateL .~ Nothing` for every credential in the set, with no check that the credential's current delegation still points to the unregistering DRep: [4](#0-3) 

This is the direct analog to the `transferPower` bug: just as `transferPower` lacked a check that `m.agent == msg.sender` before modifying state, `clearDRepDelegations` lacks a check that `accountState.dRepDelegationAccountStateL == Just (DRepCredential unregisteringDRep)` before clearing the delegation.

**Effect on governance vote distribution**

The DRep stake distribution used for ratification is computed by `computeDRepDistr`, which reads `dRepDelegationAccountStateL` from each account: [5](#0-4) 

Once `clearDRepDelegations` sets a credential's `dRepDelegationAccountStateL` to `Nothing`, that credential's stake is excluded from every DRep's distribution. DRep B loses the voting weight of all credentials that were silently cleared, directly affecting `dRepAcceptedRatio`: [6](#0-5) 

The test suite explicitly confirms this behavior during bootstrap: [7](#0-6) 

The comment "we cannot `expectNotDelegatedVote` because the delegation is still in the DRepState of the other drep" confirms that unregistering DRep A clears `stakeCred`'s delegation to DRep B.

**Bootstrap phase definition** [8](#0-7) 

The bootstrap phase is exactly protocol version 9. The `updateDRepDelegations` migration applied at the PV9→PV10 hard fork reconstructs `drepDelegs` from scratch, but this does not retroactively restore delegations that were already cleared by a DRep unregistration during PV9: [9](#0-8) 

---

### Impact Explanation

An attacker who controls a DRep can:
1. Register as a DRep during bootstrap (PV9).
2. Attract delegators.
3. Wait for some delegators to re-delegate to a competing DRep B (their `dRepDelegationAccountStateL` now points to DRep B, but DRep A's `drepDelegs` still contains them).
4. Submit a `ConwayUnRegDRep` certificate to unregister.
5. `clearDRepDelegations` silently sets `dRepDelegationAccountStateL .~ Nothing` for all stale entries, including credentials that have already moved to DRep B.
6. DRep B's effective voting power is reduced without any action by the affected delegators.

This modifies governance vote delegation outside design parameters via an attacker-controlled certificate, mapping to the **Medium** allowed impact: *"Attacker-controlled transactions... modify... withdrawals outside design parameters"* — and potentially **Critical** if the reduced voting power causes a governance action (e.g., a hard-fork initiation, committee change, or treasury withdrawal) to be ratified or blocked contrary to the true stake distribution.

---

### Likelihood Explanation

- Requires the network to be at protocol version 9 (bootstrap phase).
- Requires at least one delegator to have re-delegated away from the attacker's DRep to a target DRep.
- The attacker's only required action is submitting a standard `ConwayUnRegDRep` certificate, which is a normal, permissionless ledger operation.
- The attack is silent: affected delegators receive no on-chain notification that their delegation was cleared.

**Likelihood: Medium** — constrained to PV9, but the attacker action is trivial and the victim action (re-delegation) is routine.

---

### Recommendation

In `clearDRepDelegations` (or its call site in `ConwayUnRegDRep`), add a guard that only clears a credential's delegation if its current `dRepDelegationAccountStateL` actually points to the unregistering DRep:

```haskell
clearDRepDelegations drepCred delegs accountsMap =
  foldr
    ( Map.adjust
        ( \as ->
            if as ^. dRepDelegationAccountStateL == Just (DRepCredential drepCred)
              then as & dRepDelegationAccountStateL .~ Nothing
              else as
        )
    )
    accountsMap
    delegs
```

This mirrors the correct behavior already implemented in `unDelegReDelegDRep`, which checks `if Just dRep == mNewDRep then id` before modifying state: [10](#0-9) 

---

### Proof of Concept

Attack sequence (all on a PV9 network):

1. Attacker registers DRep A (`ConwayRegDRep`).
2. Victim registers stake credential and delegates vote to DRep A (`ConwayRegDelegCert` with `DelegVote (DRepCredential drepA)`).
   - `accountState.dRepDelegationAccountStateL = Just (DRepCredential drepA)`
   - `DRepState_A.drepDelegs = {victim}`
3. Victim re-delegates to DRep B (`ConwayDelegCert` with `DelegVote (DRepCredential drepB)`).
   - `accountState.dRepDelegationAccountStateL = Just (DRepCredential drepB)` ✓
   - `DRepState_A.drepDelegs = {victim}` ← stale, not removed (bootstrap bug)
   - `DRepState_B.drepDelegs = {victim}` ✓
4. Attacker submits `ConwayUnRegDRep drepA refund`.
   - `clearDRepDelegations {victim} accountsMap` runs.
   - `victim`'s `dRepDelegationAccountStateL` is set to `Nothing`.
5. DRep B's stake distribution no longer includes victim's stake.
   - `computeDRepDistr` skips victim (no delegation).
   - `dRepAcceptedRatio` for DRep B is reduced.

The test at line 313–323 of `DelegSpec.hs` confirms step 4 produces `expectNothingExpr (lookupDRepDelegation cred accounts)` during bootstrap, proving the delegation is cleared. [7](#0-6)

### Citations

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Deleg.hs (L347-365)
```haskell
    delegVote dRep cState =
      let handleReverseDelegation =
            case dRepToCred dRep of
              Just dRepCred
                -- This is the case where we only add the new reverse delegation and do not remove
                -- the old one, which is the behavior that we want:
                --
                -- 1) for new accounts, since there is no old reverse delegation to remove
                --
                -- 2) in the bootstrap phase, in order to preserve the incorrect behavior, where old reverse
                --   delegation for the prior DRep was wrongfully retained. It is important to note
                --   that in case when the new delegation was to a predefined DRep, the reverse
                --   delegations where handled correctly even in the boostrap phase
                --
                -- For reference here is the original bug report:
                --   https://github.com/IntersectMBO/cardano-ledger/issues/4772
                | isNothing mAccountState || preserveIncorrectDelegation ->
                    certVStateL . vsDRepsL
                      %~ Map.adjust (drepDelegsL %~ Set.insert stakeCred) dRepCred
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/GovCert.hs (L244-254)
```haskell
        certState' =
          certState & certVStateL . vsDRepsL %~ Map.delete cred
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

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Ratify.hs (L258-281)
```haskell
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
                    -- the vote but we consider it in the denominator:
                    Nothing -> (yes, tot + stake)
                    Just VoteYes -> (yes + stake, tot + stake)
                    Just Abstain -> (yes, tot)
                    Just VoteNo -> (yes, tot + stake)
        DRepAlwaysNoConfidence ->
          case govAction of
            NoConfidence _ -> (yes + stake, tot + stake)
            _ -> (yes, tot + stake)
        DRepAlwaysAbstain -> (yes, tot)
    (yesStake, totalExcludingAbstainStake) = Map.foldlWithKey' accumStake (0, 0) reDRepDistr
```

**File:** eras/conway/impl/testlib/Test/Cardano/Ledger/Conway/Imp/DelegSpec.hs (L313-323)
```haskell
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

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/State/VState.hs (L129-143)
```haskell
unDelegReDelegDRep stakeCred accountState mNewDRep =
  fromMaybe (vsDRepsL %~ addNewDelegation) $ do
    dRep@(DRepCredential dRepCred) <- accountState ^. dRepDelegationAccountStateL
    pure $
      -- There is no need to update set of delegations if delegation is unchanged
      if Just dRep == mNewDRep
        then id
        else
          vsDRepsL %~ addNewDelegation . Map.adjust (drepDelegsL %~ Set.delete stakeCred) dRepCred
  where
    addNewDelegation =
      case mNewDRep of
        Just (DRepCredential dRepCred) ->
          Map.adjust (drepDelegsL %~ Set.insert stakeCred) dRepCred
        _ -> id
```
