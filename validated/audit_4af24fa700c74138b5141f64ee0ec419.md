### Title
Stale `drepDelegs` Reverse Index Causes `ConwayUnRegDRep` to Unconditionally Wipe Active DRep Delegations of Re-delegated Stakers — (`File: eras/conway/impl/src/Cardano/Ledger/Conway/Rules/GovCert.hs`)

---

### Summary

In the Conway bootstrap phase (protocol version < 10), when a staker re-delegates their vote from DRep A to DRep B, DRep A's `drepDelegs` reverse-index set intentionally retains the staker as a stale entry (preserved for bootstrap compatibility, issue #4772). When DRep A subsequently submits a `ConwayUnRegDRep` certificate, the `clearDRepDelegations` helper unconditionally sets `dRepDelegationAccountStateL .~ Nothing` for every staker in `drepDelegs` — including stakers who have already moved to DRep B. This wipes those stakers' active DRep delegation, permanently reducing DRep B's effective voting power. The damage is not repaired by the pv-10 `updateDRepDelegations` migration, because that migration only re-populates delegations for accounts whose `dRepDelegationAccountStateL` is already `Just _`; accounts that were cleared to `Nothing` are silently skipped.

---

### Finding Description

**Root cause 1 — stale reverse-index accumulation (bootstrap phase)**

`processDelegationInternal` is called with `preserveIncorrectDelegation = pvMajor pv < natVersion @10`. [1](#0-0) 

When `preserveIncorrectDelegation` is `True` and a staker re-delegates to a new credential DRep, the branch taken is:

```haskell
| isNothing mAccountState || preserveIncorrectDelegation ->
    certVStateL . vsDRepsL
      %~ Map.adjust (drepDelegsL %~ Set.insert stakeCred) dRepCred
``` [2](#0-1) 

The new DRep's `drepDelegs` gains the staker, but the **old** DRep's `drepDelegs` is **never updated** to remove the staker. The correct path (`unDelegReDelegDRep`) that would call `Set.delete` on the old DRep is bypassed entirely. [3](#0-2) 

**Root cause 2 — unconditional clear on DRep unregistration**

`ConwayUnRegDRep` processing defines:

```haskell
clearDRepDelegations delegs accountsMap =
  foldr (Map.adjust (dRepDelegationAccountStateL .~ Nothing)) accountsMap delegs
```

and applies it to the full `drepDelegs` set of the departing DRep: [4](#0-3) 

There is **no guard** checking whether each staker's current `dRepDelegationAccountStateL` still points to the DRep being unregistered. Any staker who re-delegated to DRep B but whose credential still appears in DRep A's stale `drepDelegs` has their delegation to DRep B silently set to `Nothing`.

**Root cause 3 — pv-10 migration does not restore cleared delegations**

`updateDRepDelegations` (called at the pv-9 → pv-10 hard fork) iterates over accounts and only acts when `dRepDelegationAccountStateL` is `Just (DRepCredential _)`:

```haskell
adjustDelegations ds stakeCred accountState =
  case accountState ^. dRepDelegationAccountStateL of
    Just (DRepCredential dRep) -> ...
    _ -> (ds, accountState)   -- cleared accounts are silently skipped
``` [5](#0-4) 

Accounts whose delegation was cleared to `Nothing` by `clearDRepDelegations` fall into the `_ ->` branch and are never restored. The corruption persists post-upgrade.

**Test confirmation**

The existing test suite explicitly acknowledges this behavior in the bootstrap phase:

```haskell
-- we need to preserve the buggy behavior until the bootstrap phase is over.
ifBootstrap
  ( do
      accounts <- getsNES ...
      expectNothingExpr (lookupDRepDelegation cred accounts)   -- delegation was wiped
      expecteReverseDRepDelegation cred drepCred2 True         -- but DRep2 still lists the staker
  )
  (expectDelegatedVote cred (DRepCredential drepCred2))
``` [6](#0-5) 

The test confirms: after DRep A unregisters in the bootstrap phase, the staker's `dRepDelegationAccountStateL` is `Nothing` even though the staker intended to delegate to DRep B. DRep B's `drepDelegs` still lists the staker, creating an inconsistent ledger state.

---

### Impact Explanation

An attacker who is a registered DRep can submit a `ConwayUnRegDRep` certificate after stakers have re-delegated away from them. This unconditionally clears those stakers' current DRep delegations, reducing the effective voting stake of the DRep they moved to. The resulting inconsistency (account says `Nothing`, DRep B's `drepDelegs` still lists the staker) persists through the pv-10 migration. Governance proposals that depend on DRep B's voting threshold may fail to ratify, or the reduced active-DRep-stake denominator may allow other proposals to pass with fewer votes than intended. This constitutes attacker-controlled modification of governance voting power outside design parameters.

**Allowed impact matched**: *Medium — Attacker-controlled transactions modify governance votes/withdrawals outside design parameters.*

---

### Likelihood Explanation

The attack is reachable by any registered DRep during the Conway bootstrap phase (protocol version 9). No privileged access is required: any DRep can unregister themselves. The only precondition is that at least one staker previously delegated to the attacker's DRep and subsequently re-delegated to a different credential DRep while the protocol version was still < 10. This is a normal user action. The attacker does not need to collude with anyone; they simply wait for re-delegations to accumulate and then unregister.

---

### Recommendation

`clearDRepDelegations` should verify that each staker's current `dRepDelegationAccountStateL` actually points to the DRep being unregistered before clearing it:

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

This mirrors the guard already present in `unDelegReDelegDRep` (`if Just dRep == mNewDRep then id else ...`). [7](#0-6) 

Additionally, `updateDRepDelegations` should be extended to detect and repair accounts whose `dRepDelegationAccountStateL` is `Nothing` but whose credential still appears in some DRep's `drepDelegs`, or the stale-entry accumulation in `processDelegationInternal` should be eliminated entirely.

---

### Proof of Concept

1. Protocol version is 9 (bootstrap phase). `preserveIncorrectDelegation = True`.
2. Attacker registers as DRep A.
3. Staker S registers a stake credential and delegates vote to DRep A. DRep A's `drepDelegs = {S}`.
4. Staker S re-delegates vote to DRep B (`DelegTxCert S (DelegVote (DRepCredential drepCredB))`). Because `preserveIncorrectDelegation = True`, `unDelegReDelegDRep` is **not** called; DRep A's `drepDelegs` remains `{S}`. DRep B's `drepDelegs = {S}`. S's account: `dRepDelegationAccountStateL = Just (DRepCredential drepCredB)`.
5. Attacker submits `UnRegDRepTxCert drepCredA deposit`. `clearDRepDelegations {S} accountsMap` runs, setting S's `dRepDelegationAccountStateL .~ Nothing` unconditionally. [4](#0-3) 
6. Post-unregistration state: S's account has `dRepDelegationAccountStateL = Nothing`. DRep B's `drepDelegs` still contains S (inconsistent). S's stake is not counted toward DRep B's voting power.
7. At the pv-10 hard fork, `updateDRepDelegations` iterates accounts. S's account hits the `_ -> (ds, accountState)` branch and is not restored. [5](#0-4) 
8. DRep B permanently loses S's stake from its effective voting weight. Any governance proposal requiring DRep B's threshold may fail to ratify.

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

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/HardFork.hs (L92-100)
```haskell
      adjustDelegations ds stakeCred accountState =
        case accountState ^. dRepDelegationAccountStateL of
          Just (DRepCredential dRep) ->
            let addDelegation _ dRepState =
                  Just $ dRepState {drepDelegs = Set.insert stakeCred (drepDelegs dRepState)}
             in case Map.updateLookupWithKey addDelegation dRep ds of
                  (Nothing, _) -> (ds, accountState & dRepDelegationAccountStateL .~ Nothing)
                  (Just _, ds') -> (ds', accountState)
          _ -> (ds, accountState)
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
