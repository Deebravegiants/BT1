### Title
Stale Reverse-Delegation Entries in `drepDelegs` During Bootstrap Phase Allow Malicious DRep Unregistration to Erase Active Vote Delegations — (`eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Deleg.hs`)

---

### Summary

During the Conway bootstrap phase (protocol version 9), when a stake credential re-delegates its vote from DRep A to DRep B, the credential is inserted into DRep B's `drepDelegs` reverse-index but is **not** removed from DRep A's `drepDelegs`. This is the direct analog of the SwingTraderManager bug: an element is unconditionally added to an "active" tracking set without cleaning up the stale entry in the old set. When DRep A subsequently unregisters, `clearDRepDelegations` unconditionally sets `dRepDelegationAccountStateL` to `Nothing` for every credential in DRep A's `drepDelegs`—including credentials that have already re-delegated to DRep B—silently erasing their active vote delegation and removing their stake from DRep B's governance distribution.

---

### Finding Description

**Root cause — `processDelegationInternal` in `eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Deleg.hs`:** [1](#0-0) 

When `preserveIncorrectDelegation` is `True` (i.e., `pvMajor pv < natVersion @10`, the bootstrap phase) **and** `mAccountState` is `Just` (the credential already exists and is re-delegating), the branch taken is:

```haskell
| isNothing mAccountState || preserveIncorrectDelegation ->
    certVStateL . vsDRepsL
      %~ Map.adjust (drepDelegsL %~ Set.insert stakeCred) dRepCred
```

This inserts `stakeCred` into the **new** DRep's `drepDelegs` but never calls `unDelegReDelegDRep` to remove it from the **old** DRep's `drepDelegs`. The credential now appears in both DRep A's and DRep B's `drepDelegs` sets, while the account's `dRepDelegationAccountStateL` correctly points to DRep B.

**Propagation — `ConwayUnRegDRep` in `eras/conway/impl/src/Cardano/Ledger/Conway/Rules/GovCert.hs`:** [2](#0-1) 

```haskell
clearDRepDelegations delegs accountsMap =
  foldr (Map.adjust (dRepDelegationAccountStateL .~ Nothing)) accountsMap delegs
```

This function iterates over every credential in the unregistering DRep's `drepDelegs` and **unconditionally** sets `dRepDelegationAccountStateL` to `Nothing`—with no check of whether the credential's current delegation still points to the unregistering DRep. Because `stakeCred` was never removed from DRep A's `drepDelegs`, unregistering DRep A clears `stakeCred`'s delegation even though it now belongs to DRep B.

**Effect on DRep distribution — `computeDRepDistr` in `eras/conway/impl/src/Cardano/Ledger/Conway/Governance/DRepPulser.hs`:** [3](#0-2) 

`computeDRepDistr` reads `accountState ^. dRepDelegationAccountStateL` to determine which DRep receives the credential's stake. After the erasure, this field is `Nothing`, so the credential's stake is counted for **no** DRep—silently reducing DRep B's voting power.

**Effect on ratification — `dRepAcceptedRatio` in `eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Ratify.hs`:** [4](#0-3) 

The DRep distribution (`reDRepDistr`) fed into `dRepAcceptedRatio` is built by `computeDRepDistr`. With the affected credentials' stake removed from DRep B's entry, the yes/total ratio is computed over a deflated denominator and numerator, potentially flipping whether a governance action is accepted or rejected.

---

### Impact Explanation

An attacker who controls DRep A can:

1. Register as a DRep (permissionless; requires only the `ppDRepDeposit`).
2. Attract stake delegations from honest delegators.
3. Wait for those delegators to re-delegate to DRep B during the bootstrap phase (PV9).
4. Submit a `ConwayUnRegDRep` certificate to unregister DRep A.

Step 4 causes `clearDRepDelegations` to erase the `dRepDelegationAccountStateL` of every credential that was ever in DRep A's `drepDelegs`, including those that have already moved to DRep B. DRep B's stake in `reDRepDistr` is reduced by the sum of those credentials' stake, directly altering the `dRepAcceptedRatio` used in `ratifyTransition`. Depending on the margin, this can:

- Prevent a legitimate governance action (e.g., a treasury withdrawal, protocol-parameter change, or hard-fork initiation) from reaching the required threshold, permanently blocking it until it expires.
- Allow a governance action that DRep B was blocking to cross the threshold, enacting an unauthorized change.

This matches the allowed impact: **High — attacker-controlled transactions modify governance vote counts outside design parameters**, and potentially **Critical — unauthorized governance action is enacted**.

---

### Likelihood Explanation

- The bootstrap phase (PV9) is the current live Conway phase; the bug is exploitable on mainnet today.
- DRep registration is permissionless; the only barrier is the `ppDRepDeposit`.
- Attracting delegations requires social engineering but is realistic for a well-resourced attacker.
- The attack is a single `ConwayUnRegDRep` transaction after delegators have re-delegated; no further privileged access is needed.
- The fix (`updateDRepDelegations`) only runs at the PV10 hardfork transition; until then, every re-delegation during bootstrap leaves a stale entry exploitable by this path.

---

### Recommendation

In `clearDRepDelegations` (called from `ConwayUnRegDRep`), guard the erasure: only set `dRepDelegationAccountStateL` to `Nothing` if the credential's current delegation still points to the unregistering DRep:

```haskell
clearDRepDelegations unregCred delegs accountsMap =
  foldr
    ( Map.adjust $ \as ->
        if as ^. dRepDelegationAccountStateL == Just (DRepCredential unregCred)
          then as & dRepDelegationAccountStateL .~ Nothing
          else as
    )
    accountsMap
    delegs
```

This mirrors the correct post-bootstrap behavior already implemented in `unDelegReDelegDRep`. [5](#0-4) 

---

### Proof of Concept

```
Epoch 0 (PV9 bootstrap):
  1. Attacker registers DRep_A.
  2. Honest delegator C submits RegDepositDelegTxCert(C, DelegVote(DRep_A)).
     → C's account: dRepDelegationAccountStateL = Just DRep_A
     → DRep_A.drepDelegs = {C}

Epoch 1:
  3. C re-delegates: DelegTxCert(C, DelegVote(DRep_B)).
     processDelegationInternal (preserveIncorrectDelegation=True):
       - C's account: dRepDelegationAccountStateL = Just DRep_B  ✓
       - DRep_B.drepDelegs = {C}                                 ✓
       - DRep_A.drepDelegs = {C}  ← NOT removed                 ✗

Epoch 2:
  4. Attacker submits UnRegDRepTxCert(DRep_A, deposit).
     clearDRepDelegations {C} accountsMap:
       Map.adjust (dRepDelegationAccountStateL .~ Nothing) C accountsMap
       → C's account: dRepDelegationAccountStateL = Nothing      ✗ (should be Just DRep_B)

Result:
  - C's stake is no longer counted for DRep_B in computeDRepDistr.
  - dRepAcceptedRatio for any proposal DRep_B voted on is computed
    over a deflated distribution, potentially flipping ratification.
```

### Citations

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
