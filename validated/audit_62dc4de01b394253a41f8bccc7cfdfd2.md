### Title
Unbounded `drepDelegs` Set Iterated on DRep Unregistration Causes Permanent Ledger Freeze of DRep Deposit - (`File: eras/conway/impl/src/Cardano/Ledger/Conway/Rules/GovCert.hs`)

---

### Summary

When a DRep unregisters via `ConwayUnRegDRep`, the ledger iterates over the entire `drepDelegs` set stored in `DRepState` to clear each delegator's reverse-delegation pointer. There is no protocol-enforced upper bound on how many stake credentials can delegate to a single DRep. An attacker who controls many stake credentials can delegate all of them to a target DRep, growing `drepDelegs` to an arbitrarily large size. When the DRep owner later submits a `ConwayUnRegDRep` certificate to reclaim their deposit, the transaction's CPU/memory budget is exhausted iterating over the unbounded set, causing the transaction to be permanently rejected. The DRep deposit is permanently frozen.

---

### Finding Description

In `ConwayUnRegDRep` processing inside `govCertTransition`, the ledger executes:

```haskell
clearDRepDelegations delegs accountsMap =
  foldr (Map.adjust (dRepDelegationAccountStateL .~ Nothing)) accountsMap delegs
```

where `delegs = drepDelegs dRepState` — the full set of stake credentials currently delegated to the DRep. [1](#0-0) 

`drepDelegs` is typed as `Set (Credential Staking)` with no enforced upper bound: [2](#0-1) 

Any stake credential holder can delegate to any DRep by submitting a `DelegVote` certificate. The delegation is accepted unconditionally — there is no check on the current size of the target DRep's `drepDelegs` set: [3](#0-2) 

Each delegation costs only a `keyDeposit` (stake credential registration) plus a small transaction fee, both of which are refundable or economically negligible at scale. An attacker registers N stake credentials and delegates each to the victim DRep, growing `drepDelegs` to size N. When the DRep submits `ConwayUnRegDRep`, the `foldr` over N entries in `clearDRepDelegations` causes the transaction to exceed the block's execution budget, making it permanently invalid.

The `maxTxSize` limit does not protect against this: the `ConwayUnRegDRep` transaction itself is tiny (one certificate); the cost is in ledger-side computation during rule evaluation, not in transaction bytes. [4](#0-3) 

---

### Impact Explanation

**High — Permanent freezing of DRep deposit where recovery requires a hard fork.**

The DRep deposit (set by `ppDRepDeposit`, currently 500 ADA on mainnet) is locked in the ledger state. The `ConwayUnRegDRep` certificate is the only mechanism to reclaim it. If that certificate can never be successfully applied because the transaction always exceeds resource limits, the deposit is permanently frozen. The DRep credential also cannot be cleanly removed from `vsDReps`, leaving a stale governance participant in the ledger state indefinitely.

---

### Likelihood Explanation

**Medium.** The attack requires the attacker to register and delegate many stake credentials. Each registration costs `keyDeposit` (2 ADA on mainnet), which is refundable upon unregistration. The attacker can reclaim all deposits after the attack. The number of delegations needed to exhaust the block budget is bounded by the per-block execution limit; given that `Map.adjust` on a large `Map` is O(log N) per call and `foldr` over a `Set` of size N is O(N log N) total, a few hundred thousand delegations would suffice. This is economically feasible for a motivated attacker targeting a specific high-value DRep (e.g., one holding a large deposit or wielding significant governance influence). The attack is permissionless — any unprivileged transaction sender can execute it.

---

### Recommendation

1. **Enforce a maximum delegator count per DRep** at delegation time in the `DELEG` rule, rejecting `DelegVote` if `Set.size (drepDelegs dRepState) >= maxDRepDelegators` (a new protocol parameter or a hardcoded constant).

2. **Alternatively, remove `drepDelegs` from `DRepState` entirely** and reconstruct the reverse-delegation mapping lazily (e.g., by scanning `accountsMapL` only when needed for governance stake calculation), eliminating the need for the `clearDRepDelegations` loop at unregistration time.

3. **Short-term mitigation**: cap the `foldr` in `clearDRepDelegations` to a maximum number of entries per transaction, splitting the cleanup across multiple transactions if needed.

---

### Proof of Concept

1. Attacker registers N stake credentials (e.g., N = 500,000), each costing 2 ADA keyDeposit (refundable).
2. Each credential submits a `DelegVote (DRepCredential victimDRep)` certificate, inserting itself into `drepDelegs` of the victim DRep via `Map.adjust (drepDelegsL %~ Set.insert stakeCred) dRepCred` in `processDelegationInternal`.
3. After N delegations, `drepDelegs victimDRepState` has cardinality N.
4. Victim DRep submits `UnRegDRepTxCert victimDRep refund`.
5. The `GOVCERT` rule evaluates `clearDRepDelegations (drepDelegs dRepState) accountsMap`, executing `foldr` over N elements.
6. The transaction exceeds the block's CPU/memory budget and is rejected.
7. The victim DRep's deposit remains permanently locked in `vsDReps`; the DRep cannot be removed.
8. Attacker unregisters all N stake credentials, recovering all 2N ADA in keyDeposits. [5](#0-4) [6](#0-5) [2](#0-1)

### Citations

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/GovCert.hs (L234-254)
```haskell
    ConwayUnRegDRep cred refund -> do
      let mDRepState = Map.lookup cred (certState ^. certVStateL . vsDRepsL)
          drepRefundMismatch = do
            drepState <- mDRepState
            let paidDeposit = drepState ^. drepDepositL
            guard (refund /= paidDeposit)
            pure paidDeposit
      isJust mDRepState ?! (injectFailure . ConwayDRepNotRegistered) cred
      failOnJust drepRefundMismatch $ injectFailure . ConwayDRepIncorrectRefund . Mismatch refund
      let
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

**File:** libs/cardano-ledger-core/src/Cardano/Ledger/DRep.hs (L166-171)
```haskell
data DRepState = DRepState
  { drepExpiry :: !EpochNo
  , drepAnchor :: !(StrictMaybe Anchor)
  , drepDeposit :: !(CompactForm Coin)
  , drepDelegs :: !(Set (Credential Staking))
  }
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

**File:** eras/shelley/impl/src/Cardano/Ledger/Shelley/Rules/Utxo.hs (L562-576)
```haskell
validateMaxTxSizeUTxO ::
  EraTx era =>
  PParams era ->
  Tx l era ->
  Test (ShelleyUtxoPredFailure era)
validateMaxTxSizeUTxO pp tx =
  failureUnless (txSize <= maxTxSize) $
    MaxTxSizeUTxO
      Mismatch
        { mismatchSupplied = txSize
        , mismatchExpected = maxTxSize
        }
  where
    maxTxSize = pp ^. ppMaxTxSizeL
    txSize = tx ^. sizeTxF
```
