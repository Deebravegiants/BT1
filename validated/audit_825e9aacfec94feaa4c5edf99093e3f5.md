### Title
Stale `drepDelegs` Reverse-Delegation Map Allows DRep Unregistration to Silently Wipe Active Delegations During Bootstrap Phase - (File: `eras/conway/impl/src/Cardano/Ledger/Conway/Rules/GovCert.hs`)

---

### Summary

During the Conway bootstrap phase (protocol version < 10), when a stake credential redelegates from DRep X to DRep Y, the reverse-delegation set `drepDelegs` inside DRep X's `DRepState` is never cleaned up. When DRep X subsequently unregisters, the `ConwayUnRegDRep` handler uses that stale `drepDelegs` set to clear delegations from the accounts map, silently setting the `dRepDelegationAccountStateL` of already-moved credentials to `Nothing`. This wipes the victim's active delegation to DRep Y without any action by the victim, removing their stake from DRep Y's voting power and manipulating governance ratification.

---

### Finding Description

`DRepState` holds a `drepDelegs :: Set (Credential Staking)` field — a reverse-delegation index mapping a DRep to the set of stake credentials currently delegating to it. [1](#0-0) 

During the bootstrap phase, `processDelegationInternal` is called with `preserveIncorrectDelegation = True` (when `pvMajor pv < natVersion @10`): [2](#0-1) 

Inside `processDelegationInternal`, the `delegVote` branch only **adds** the stake credential to the new DRep's `drepDelegs` set but **does not remove** it from the old DRep's `drepDelegs` set when `preserveIncorrectDelegation` is `True`: [3](#0-2) 

This is the acknowledged bug #4772. The result is that after a redelegation from DRep X → DRep Y, DRep X's `drepDelegs` still contains the credential, while the forward mapping in the accounts (`dRepDelegationAccountStateL`) correctly points to DRep Y.

The critical consequence occurs in `ConwayUnRegDRep`. When DRep X unregisters, `clearDRepDelegations` iterates over DRep X's (now stale) `drepDelegs` and sets `dRepDelegationAccountStateL .~ Nothing` for every credential in that set: [4](#0-3) 

Because the credential that moved to DRep Y is still in DRep X's `drepDelegs`, its forward delegation entry in the accounts map is overwritten to `Nothing`. The credential now has no DRep delegation at all, even though the owner never submitted any certificate to remove it.

The actual DRep voting power for ratification is computed by `computeDRepDistr`, which reads `dRepDelegationAccountStateL` from the accounts map: [5](#0-4) 

Since that field is now `Nothing`, the credential's stake is no longer counted toward DRep Y's voting power.

The fix (`updateDRepDelegations`) is only applied at the hard fork to protocol version 10, not during the bootstrap phase: [6](#0-5) 

---

### Impact Explanation

An attacker who controls DRep X can:
1. Attract delegations from stake credentials.
2. Wait for those credentials to redelegate to a target DRep Y (e.g., a DRep voting in a direction the attacker opposes).
3. Submit a `ConwayUnRegDRep` certificate to unregister DRep X.
4. `clearDRepDelegations` silently wipes the forward delegation of all credentials that previously delegated to DRep X, even those that have since moved to DRep Y.
5. DRep Y loses voting power it legitimately held, potentially causing a governance proposal to fail ratification (or pass, depending on which side the attacker targets).

This maps to: **Critical — Unauthorized governance action is enacted** (or blocked) through manipulation of DRep voting power, or at minimum **High — deterministic disagreement in ledger rule evaluation** since the ledger state diverges from what delegators intended.

---

### Likelihood Explanation

- Exploitable during the Conway bootstrap phase (protocol version 9), which is a live mainnet phase.
- Requires only that the attacker register as a DRep (permissionless, requires only a deposit) and that at least one delegator has redelegated away from them.
- No privileged access, governance majority, or key compromise is needed.
- The attacker recovers their DRep deposit upon unregistration, making the attack nearly free.
- The victim has no way to prevent or detect the wipe until their delegation is already gone.

---

### Recommendation

The `clearDRepDelegations` function in `ConwayUnRegDRep` should verify that each credential in `drepDelegs` still has its `dRepDelegationAccountStateL` pointing to the unregistering DRep before clearing it. Specifically, the adjustment should be conditional:

```haskell
clearDRepDelegations delegs cred accountsMap =
  foldr
    (\stakeCred m ->
      Map.adjust
        (\as -> if as ^. dRepDelegationAccountStateL == Just (DRepCredential cred)
                then as & dRepDelegationAccountStateL .~ Nothing
                else as)
        stakeCred m)
    accountsMap
    delegs
```

This ensures that only credentials whose forward delegation still points to the unregistering DRep are cleared, leaving credentials that have already moved to another DRep untouched.

---

### Proof of Concept

The following sequence of ledger operations (expressible as an `ImpTest`) demonstrates the issue during bootstrap phase (PV9):

1. Register stake credential `cred`.
2. Register DRep X and DRep Y.
3. Submit `RegDepositDelegTxCert cred (DelegVote (DRepCredential drepX)) deposit` — `cred` delegates to DRep X; DRep X's `drepDelegs = {cred}`.
4. Submit `DelegTxCert cred (DelegVote (DRepCredential drepY))` — `cred` redelegates to DRep Y. Due to the bootstrap bug, DRep X's `drepDelegs` still contains `cred`; DRep Y's `drepDelegs = {cred}`.
5. Submit `UnRegDRepTxCert drepX deposit` — DRep X unregisters. `clearDRepDelegations {cred} accountsMap` sets `cred`'s `dRepDelegationAccountStateL` to `Nothing`.
6. Assert: `lookupDRepDelegation cred accounts == Nothing` — delegation to DRep Y is gone.
7. Assert: DRep Y's `drepDelegs` still contains `cred` (the reverse mapping is now inconsistent in the other direction).
8. Confirm that `computeDRepDistr` no longer counts `cred`'s stake toward DRep Y. [7](#0-6) [3](#0-2)

### Citations

**File:** libs/cardano-ledger-core/src/Cardano/Ledger/DRep.hs (L166-171)
```haskell
data DRepState = DRepState
  { drepExpiry :: !EpochNo
  , drepAnchor :: !(StrictMaybe Anchor)
  , drepDeposit :: !(CompactForm Coin)
  , drepDelegs :: !(Set (Credential Staking))
  }
```

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

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Governance/DRepPulser.hs (L228-240)
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
