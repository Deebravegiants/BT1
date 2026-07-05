### Title
Bootstrap-Phase DRep Reverse-Delegation Desynchronization Enables Silent Vote-Delegation Erasure on DRep Unregistration — (`eras/conway/impl/src/Cardano/Ledger/Conway/Rules/GovCert.hs`, `eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Deleg.hs`)

---

### Summary

During the Conway bootstrap phase (protocol version 9), `processDelegationInternal` in `Deleg.hs` intentionally preserves a known desynchronization between two data structures that must be kept in sync:

1. `AccountState.dRepDelegation` — the **forward** delegation (stake credential → DRep)
2. `DRepState.drepDelegs` — the **reverse** delegation set (DRep → set of stake credentials)

When a stake credential redelegates from DRep A to DRep B during bootstrap, the credential is added to DRep B's `drepDelegs` but is **not removed** from DRep A's `drepDelegs`. This stale entry persists in the on-chain ledger state indefinitely.

When DRep A later submits an `UnRegDRepTxCert`, the `ConwayUnRegDRep` handler in `GovCert.hs` calls `clearDRepDelegations (drepDelegs dRepAState)`, which unconditionally sets `dRepDelegationAccountStateL .~ Nothing` for every credential in `drepDelegs` — including stale entries. This silently erases the vote delegation of stake credentials that have already moved to DRep B, reducing DRep B's governance voting power without any on-chain error.

---

### Finding Description

**Root cause — `Deleg.hs`, `processDelegationInternal`:** [1](#0-0) 

The `Bool` parameter `preserveIncorrectDelegation` is set to `pvMajor pv < natVersion @10` at the call site: [2](#0-1) 

When `preserveIncorrectDelegation` is `True` (bootstrap, PV9), the `delegVote` branch only **inserts** the credential into the new DRep's `drepDelegs` and never removes it from the old DRep's `drepDelegs`: [3](#0-2) 

The correct post-bootstrap path calls `unDelegReDelegDRep`, which does remove the credential from the old DRep's set: [4](#0-3) 

**Downstream impact — `GovCert.hs`, `ConwayUnRegDRep`:**

When a DRep unregisters, the handler uses `drepDelegs` to clear forward delegations: [5](#0-4) 

`clearDRepDelegations` applies `dRepDelegationAccountStateL .~ Nothing` to every credential in `drepDelegs` with no check of what the credential's current delegation actually is. If `drepDelegs` contains a stale entry for credential S (which has since moved to DRep B), S's forward delegation is set to `Nothing` even though it correctly points to DRep B.

The two structures are now permanently out of sync:

| Structure | Expected state | Actual state after DRep A unregisters |
|---|---|---|
| `AccountState(S).dRepDelegation` | `Just (DRepCredential dRepB)` | `Nothing` ← **incorrectly cleared** |
| `DRepState(B).drepDelegs` | contains S | still contains S (orphaned) |

---

### Impact Explanation

An unprivileged DRep operator who participated during the bootstrap phase can submit a valid `UnRegDRepTxCert` transaction that silently removes the vote delegations of stake credentials that had previously delegated to them and then moved to a different DRep. The affected credentials' `dRepDelegationAccountStateL` is set to `Nothing`, so their stake is no longer counted toward any DRep's voting power in `computeDRepDistr`. This modifies governance vote-weight accounting outside design parameters — the intended invariant is that unregistering DRep A only clears delegations of credentials **currently** delegated to DRep A.

In a targeted scenario, an attacker who accumulated delegators during bootstrap and then watched them migrate to a high-influence DRep B can unregister to reduce DRep B's effective voting power, potentially tipping ratification thresholds for governance proposals.

This matches: **Medium — attacker-controlled transaction modifies governance vote-weight outside design parameters.**

---

### Likelihood Explanation

The Conway bootstrap phase (PV9) has already executed on mainnet. Any DRep that received delegations during bootstrap and had some of those delegators subsequently redelegate to other DReps will have stale entries in `drepDelegs`. The trigger — submitting `UnRegDRepTxCert` — is a normal, permissionless ledger operation requiring only the DRep's own signing key. No governance majority or privileged access is needed. The stale state is permanent until the affected credential itself redelegates or unregisters post-bootstrap.

---

### Recommendation

`clearDRepDelegations` must guard against stale entries by checking that the credential's current forward delegation actually points to the DRep being unregistered before clearing it:

```haskell
-- In ConwayUnRegDRep, replace:
clearDRepDelegations delegs accountsMap =
  foldr (Map.adjust (dRepDelegationAccountStateL .~ Nothing)) accountsMap delegs

-- With:
clearDRepDelegations drepCred delegs accountsMap =
  foldr
    ( Map.adjust $ \as ->
        if as ^. dRepDelegationAccountStateL == Just (DRepCredential drepCred)
          then as & dRepDelegationAccountStateL .~ Nothing
          else as
    )
    accountsMap
    delegs
```

Additionally, a one-time migration at the PV9→PV10 era transition should reconcile all `drepDelegs` sets against the authoritative forward-delegation map in `AccountState` to eliminate

### Citations

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Deleg.hs (L287-292)
```haskell
            processDelegationInternal
              (pvMajor pv < natVersion @10)
              internedCred
              (Just accountState)
              delegatee
              certState
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Deleg.hs (L320-323)
```haskell
processDelegationInternal ::
  ConwayEraCertState era =>
  -- | Preserve the buggy behavior where DRep delegations are not updated correctly (See #4772)
  Bool ->
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Deleg.hs (L363-365)
```haskell
                | isNothing mAccountState || preserveIncorrectDelegation ->
                    certVStateL . vsDRepsL
                      %~ Map.adjust (drepDelegsL %~ Set.insert stakeCred) dRepCred
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/State/VState.hs (L129-137)
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
