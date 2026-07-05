### Title
Stale DRep Reverse Delegation During Bootstrap Phase Causes Incorrect Clearing of User Vote Delegation Upon DRep Unregistration - (`eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Deleg.hs`, `eras/conway/impl/src/Cardano/Ledger/Conway/Rules/GovCert.hs`)

---

### Summary

During the Conway bootstrap phase (protocol version 9), when a stake credential redelegates its vote from DRep A to DRep B, the old reverse delegation entry in DRep A's `drepDelegs` set is intentionally not removed. When DRep A subsequently unregisters, the `ConwayUnRegDRep` handler uses `drepDelegs` to clear all delegations — including the stale entry for the credential that has already moved to DRep B. This incorrectly sets the credential's `dRepDelegationAccountStateL` to `Nothing`, silently erasing its active delegation to DRep B. In the next epoch's DRep distribution computation, that credential's stake is excluded from all DRep distributions, effectively zeroing out its governance voting power without the user's knowledge or consent.

---

### Finding Description

**Root cause — `processDelegationInternal` in `Deleg.hs`:**

When `ConwayDelegCert` is processed during the bootstrap phase (`pvMajor pv < natVersion @10`), `processDelegationInternal` is called with `preserveIncorrectDelegation = True`: [1](#0-0) 

Inside `delegVote`, the condition for removing the old reverse delegation from DRep A is: [2](#0-1) 

When `preserveIncorrectDelegation = True` and `mAccountState` is `Just _` (existing account redelegating), the branch at line 363 fires:

```haskell
| isNothing mAccountState || preserveIncorrectDelegation ->
    certVStateL . vsDRepsL
      %~ Map.adjust (drepDelegsL %~ Set.insert stakeCred) dRepCred
```

This only **adds** the credential to DRep B's `drepDelegs` but **never removes** it from DRep A's `drepDelegs`. The correct path (`unDelegReDelegDRep`, which both removes from A and adds to B) is only taken post-bootstrap. [3](#0-2) 

**Trigger — `ConwayUnRegDRep` in `GovCert.hs`:**

When DRep A unregisters, the handler iterates over `drepDelegs dRepState` and clears `dRepDelegationAccountStateL` for every credential in that set: [4](#0-3) 

Because DRep A's `drepDelegs` still contains the stale entry for the credential that has already moved to DRep B, `clearDRepDelegations` sets that credential's `dRepDelegationAccountStateL` to `Nothing` — overwriting the valid delegation to DRep B.

**Effect on DRep distribution — `computeDRepDistr` in `DRepPulser.hs`:**

The DRep distribution pulser reads `dRepDelegationAccountStateL` from each account: [5](#0-4) 

A credential with `dRepDelegationAccountStateL = Nothing` contributes to no DRep's stake. Its ADA is excluded from `reDRepDistr` entirely, reducing the effective active voting stake used in `dRepAcceptedRatio`: [6](#0-5) 

**Confirmed by existing test:**

The test suite explicitly documents and preserves this behavior during bootstrap: [7](#0-6) 

The comment "we cannot `expectNotDelegatedVote` because the delegation is still in the DRepState of the other drep" confirms that after DRep A unregisters, the account's delegation is `Nothing` (cleared) while DRep B's `drepDelegs` still contains the credential — a split, inconsistent state.

---

### Impact Explanation

**Governance manipulation (Critical/High):**

An attacker who controls a DRep can execute the following sequence during the bootstrap phase:

1. Register as DRep A and attract delegators.
2. Wait for delegators to redelegate to DRep B (which has voted **No** on a proposal the attacker wants to pass).
3. Unregister DRep A.
4. All credentials that previously delegated to DRep A and then moved to DRep B have their `dRepDelegationAccountStateL` cleared to `Nothing`.
5. In the next epoch, those credentials' stake is absent from `reDRepDistr`. DRep B's effective stake is reduced.
6. The No-vote weight decreases, increasing `dRepAcceptedRatio` and potentially pushing a proposal past its ratification threshold.

This constitutes an **unauthorized governance action being enacted** — a proposal that should have failed due to insufficient Yes votes passes because the attacker artificially reduced the active No-voting stake.

Additionally, affected users permanently lose their DRep delegation (until they re-delegate) without any on-chain signal or error. Their ADA contributes to no governance outcome, disenfranchising them silently.

---

### Likelihood Explanation

- **Bootstrap phase is active** on mainnet while protocol version remains at major version 9 (`hardforkConwayBootstrapPhase pv = pvMajor pv == natVersion @9`).
- **Redelegation is a normal user action**: users routinely switch DReps as governance evolves.
- **DRep unregistration is permissionless**: any registered DRep can unregister at any time by submitting `UnRegDRepTxCert` with the correct refund amount.
- The attacker needs only to: (a) register as a DRep, (b) attract delegators, (c) wait for some to redelegate away, and (d) unregister. Steps (a)–(d) are all standard, unprivileged ledger operations.
- No consensus majority, leaked keys, or external dependencies are required.

---

### Recommendation

The fix is already implemented for the post-bootstrap era: `updateDRepDelegations` in `HardFork.hs` rebuilds `drepDelegs` from scratch at the PV9→PV10 transition, removing all stale entries: [8](#0-7) 

For the bootstrap phase itself, the mitigation is to ensure `ConwayUnRegDRep` does not blindly clear delegations based on `drepDelegs` when those entries may be stale. Specifically, `clearDRepDelegations` should only clear a credential's delegation if its current `dRepDelegationAccountStateL` actually points to the unregistering DRep — not unconditionally:

```haskell
-- Proposed fix: only clear if the credential is still delegated to this DRep
clearDRepDelegations cred delegs accountsMap =
  foldr
    (\stakeCred acc ->
      Map.adjust
        (\as -> if as ^. dRepDelegationAccountStateL == Just (DRepCredential cred)
                then as & dRepDelegationAccountStateL .~ Nothing
                else as)
        stakeCred acc)
    accountsMap
    delegs
```

This would prevent stale `drepDelegs` entries from incorrectly clearing valid delegations to other DReps.

---

### Proof of Concept

**Attacker-controlled entry path (all unprivileged transactions):**

```
Epoch N (bootstrap, PV9):
  Tx1: Alice registers stake credential (ConwayRegCert)
  Tx2: Alice delegates vote to DRep_Attacker (ConwayRegDelegCert / DelegVote)
       → Alice's dRepDelegationAccountStateL = Just DRep_Attacker
       → DRep_Attacker.drepDelegs = {Alice}

  Tx3: Alice redelegates vote to DRep_Honest (ConwayDelegCert / DelegVote)
       → processDelegationInternal called with preserveIncorrectDelegation=True
       → Alice's dRepDelegationAccountStateL = Just DRep_Honest  ✓
       → DRep_Honest.drepDelegs = {Alice}                        ✓
       → DRep_Attacker.drepDelegs = {Alice}  ← STALE, not removed ✗

  Tx4: DRep_Honest votes No on GovAction G

  Tx5: Attacker submits UnRegDRepTxCert for DRep_Attacker
       → clearDRepDelegations iterates DRep_Attacker.drepDelegs = {Alice}
       → Sets Alice's dRepDelegationAccountStateL = Nothing  ← INCORRECT

Epoch N+1:
  DRep pulser runs computeDRepDistr:
    Alice's accountState.dRepDelegationAccountStateL = Nothing
    → Alice's stake NOT added to any DRep's distribution
    → DRep_Honest's effective stake is reduced by Alice's ADA

  dRepAcceptedRatio for GovAction G:
    DRep_Honest's stake in reDRepDistr is lower than it should be
    → No-vote weight is reduced
    → Proposal may pass threshold it should not have reached
```

The test at `DelegSpec.hs:313–323` confirms the post-`UnRegDRep` state: `lookupDRepDelegation cred accounts` returns `Nothing` during bootstrap, proving Alice's delegation to DRep_Honest was incorrectly erased. [9](#0-8)

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

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Deleg.hs (L347-377)
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
              _
                -- AccountState existed before this delegation, therefore we need to properly handle
                -- potential undelegation of the old DRep
                | Just accountState <- mAccountState ->
                    certVStateL %~ unDelegReDelegDRep stakeCred accountState (Just dRep)
                -- If this is a fresh registration with delegation to a predefined DRep, there are
                -- no extra steps that need to be done
                | otherwise -> id
       in cState
            & certDStateL . accountsL
              %~ adjustAccountState (dRepDelegationAccountStateL ?~ dRep) stakeCred
            & handleReverseDelegation
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

**File:** eras/conway/impl/testlib/Test/Cardano/Ledger/Conway/Imp/DelegSpec.hs (L307-323)
```haskell
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
