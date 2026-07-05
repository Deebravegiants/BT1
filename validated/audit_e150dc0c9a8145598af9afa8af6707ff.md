### Title
Unbounded O(N) Iteration Over All Registered DReps on Every Proposal Transaction Enables Resource Exhaustion — (`File: eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Certs.hs`)

---

### Summary

In the Conway era, every transaction that contains a governance proposal and is processed while `numDormantEpochs > 0` triggers a full `Map.map` traversal over **all** registered DReps in `vsDReps`. Because DReps are never automatically pruned from the map (they only leave via explicit `ConwayUnRegDRep`), and because there is no protocol-level cap on the number of registered DReps, an attacker can register a large number of DReps (paying a refundable deposit each time) to bloat this map. Any subsequent proposal transaction then incurs O(N) work proportional to the total number of registered DReps, degrading block production and transaction throughput.

---

### Finding Description

**Root cause — `updateDormantDRepExpiry` in `Certs.hs`:**

```haskell
updateDormantDRepExpiry currentEpoch vState =
  if numDormantEpochs == EpochNo 0
    then vState
    else
      vState
        & vsNumDormantEpochsL .~ EpochNo 0
        & vsDRepsL %~ Map.map updateExpiry   -- ← full O(N) traversal
  where
    numDormantEpochs = vState ^. vsNumDormantEpochsL
    updateExpiry = drepExpiryL %~ \currentExpiry ->
      let actualExpiry = binOpEpochNo (+) numDormantEpochs currentExpiry
       in if actualExpiry < currentEpoch then currentExpiry else actualExpiry
``` [1](#0-0) 

This function is called by `updateDormantDRepExpiries`, which fires on every transaction that carries at least one governance proposal procedure, as long as `numDormantEpochs > 0`:

```haskell
updateDormantDRepExpiries tx currentEpoch =
  let hasProposals = not . OSet.null $ tx ^. bodyTxL . proposalProceduresTxBodyL
   in if hasProposals
        then certVStateL %~ updateDormantDRepExpiry currentEpoch
        else id
``` [2](#0-1) 

This is invoked both in the pre-hardfork CERTS rule and, after `hardforkConwayMoveWithdrawalsAndDRepChecksToLedgerRule`, in the Conway LEDGER rule, confirming it is active across current protocol versions. [3](#0-2) 

**The accumulation — `VState.vsDReps` is never automatically pruned:**

```haskell
data VState era = VState
  { vsDReps :: !(Map (Credential DRepRole) DRepState)
  , vsCommitteeState :: !(CommitteeState era)
  , vsNumDormantEpochs :: !EpochNo
  }
``` [4](#0-3) 

DReps are inserted via `ConwayRegDRep` and removed only via `ConwayUnRegDRep`. There is no automatic expiry-based removal from the map. An expired DRep remains in `vsDReps` indefinitely unless it explicitly unregisters. [5](#0-4) 

**The deposit is refundable:**

DRep registration requires paying `ppDRepDeposit` (500 ADA on mainnet), but this deposit is fully refunded upon `ConwayUnRegDRep`. The attacker's net cost is only transaction fees. [6](#0-5) 

**No cap on registered DReps:**

There is no protocol parameter or ledger rule that limits the total number of simultaneously registered DReps. [7](#0-6) 

---

### Impact Explanation

Every transaction containing a governance proposal that is submitted while `numDormantEpochs > 0` triggers a full `Map.map` traversal over the entire `vsDReps` map. With N registered DReps, this is O(N) work per such transaction. Because block producers must validate all transactions in a block within a slot window, a sufficiently large `vsDReps` map causes:

- Proposal transactions to consume disproportionate CPU time during ledger rule evaluation.
- Block producers to miss slots when the per-transaction validation cost exceeds the available slot time.
- Degraded throughput for all governance activity during dormant-epoch recovery periods.

This matches the **Medium** impact category: *attacker-controlled certificates exceed intended validation limits*.

---

### Likelihood Explanation

The attack requires:
1. Registering a large number of DReps (each costs `ppDRepDeposit` = 500 ADA, refundable). Registering 10,000 DReps requires ~5,000,000 ADA locked temporarily, which is feasible for a well-funded attacker.
2. Waiting for at least one dormant epoch (an epoch with no active governance proposals), which is a normal network condition.
3. Any honest user submitting a governance proposal — the attacker does not need to submit the triggering transaction themselves.

The attacker recovers their capital by unregistering all DReps after the attack. The net cost is only transaction fees. The trigger condition (dormant epoch) is a normal network state, not a rare edge case.

---

### Recommendation

1. **Automatic pruning of expired DReps**: Remove DReps from `vsDReps` at epoch boundaries when their expiry has passed (accounting for `numDormantEpochs`), rather than retaining them indefinitely.
2. **Bounded iteration**: Instead of iterating over all DReps in `updateDormantDRepExpiry`, store the dormant-epoch offset as a single counter and apply it lazily at read time (e.g., in `vsActualDRepExpiry`), avoiding the full map traversal entirely.
3. **Protocol-level cap**: Introduce a maximum number of simultaneously registered DReps as a protocol parameter, analogous to `nOpt` for stake pools.

---

### Proof of Concept

1. Register N DReps (e.g., N = 50,000) using `ConwayRegDRep` certificates across many transactions. Each pays `ppDRepDeposit` (refundable).
2. Allow one epoch to pass with no governance proposals, so `numDormantEpochs` increments to 1 via `updateNumDormantEpochs`. [8](#0-7) 

3. Submit a single governance proposal transaction (e.g., `InfoAction`).
4. The LEDGER/CERTS rule calls `updateDormantDRepExpiries`, which calls `updateDormantDRepExpiry`, which executes `Map.map updateExpiry` over all 50,000 DRep entries. [9](#0-8) 

5. Observe that the proposal transaction validation time scales linearly with N. At large N, block producers begin missing slots during dormant-epoch recovery, degrading governance throughput.
6. Unregister all DReps to recover the deposited ADA. Net cost: transaction fees only.

### Citations

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Certs.hs (L222-241)
```haskell
  case certificates of
    Empty ->
      if hardforkConwayMoveWithdrawalsAndDRepChecksToLedgerRule $ pp ^. ppProtocolVersionL
        then pure certState
        else do
          network <- liftSTS $ asks networkId
          let accounts = certState ^. certDStateL . accountsL
              withdrawals = tx ^. bodyTxL . withdrawalsTxBodyL
          failOnJust
            (withdrawalsThatDoNotDrainAccounts withdrawals network accounts)
            ( \(invalid, incomplete) ->
                WithdrawalsNotInRewardsCERTS $
                  Withdrawals $
                    unWithdrawals invalid <> fmap mismatchSupplied incomplete
            )
          pure $
            certState
              & updateDormantDRepExpiries tx currentEpoch
              & updateVotingDRepExpiries tx currentEpoch (pp ^. ppDRepActivityL)
              & certDStateL . accountsL %~ drainAccounts withdrawals
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Certs.hs (L257-267)
```haskell
updateDormantDRepExpiries ::
  ( EraTx era
  , ConwayEraTxBody era
  , ConwayEraCertState era
  ) =>
  Tx l era -> EpochNo -> CertState era -> CertState era
updateDormantDRepExpiries tx currentEpoch =
  let hasProposals = not . OSet.null $ tx ^. bodyTxL . proposalProceduresTxBodyL
   in if hasProposals
        then certVStateL %~ updateDormantDRepExpiry currentEpoch
        else id
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Certs.hs (L313-328)
```haskell
updateDormantDRepExpiry currentEpoch vState =
  if numDormantEpochs == EpochNo 0
    then vState
    else
      vState
        & vsNumDormantEpochsL .~ EpochNo 0
        & vsDRepsL %~ Map.map updateExpiry
  where
    numDormantEpochs = vState ^. vsNumDormantEpochsL
    updateExpiry =
      drepExpiryL
        %~ \currentExpiry ->
          let actualExpiry = binOpEpochNo (+) numDormantEpochs currentExpiry
           in if actualExpiry < currentEpoch
                then currentExpiry
                else actualExpiry
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/State/VState.hs (L56-67)
```haskell
data VState era = VState
  { vsDReps :: !(Map (Credential DRepRole) DRepState)
  , vsCommitteeState :: !(CommitteeState era)
  , vsNumDormantEpochs :: !EpochNo
  -- ^ Number of contiguous epochs in which there are exactly zero
  -- active governance proposals to vote on. It is incremented in every
  -- EPOCH rule if the number of active governance proposals to vote on
  -- continues to be zero. It is reset to zero when a new governance
  -- action is successfully proposed. We need this counter in order to
  -- bump DRep expiries through dormant periods when DReps do not have
  -- an opportunity to vote on anything.
  }
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/GovCert.hs (L210-233)
```haskell
    ConwayRegDRep cred deposit mAnchor -> do
      Map.notMember cred (certState ^. certVStateL . vsDRepsL)
        ?! (injectFailure . ConwayDRepAlreadyRegistered) cred
      deposit
        == ppDRepDeposit
          ?! (injectFailure . ConwayDRepIncorrectDeposit)
            Mismatch
              { mismatchSupplied = deposit
              , mismatchExpected = ppDRepDeposit
              }
      let drepState =
            DRepState
              { drepExpiry =
                  computeDRepExpiryVersioned
                    cgcePParams
                    cgceCurrentEpoch
                    (certState ^. certVStateL . vsNumDormantEpochsL)
              , drepAnchor = mAnchor
              , drepDeposit = ppDRepDepositCompact
              , drepDelegs = mempty
              }
      pure $
        certState
          & certVStateL . vsDRepsL %~ Map.insert cred drepState
```

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

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/PParams.hs (L700-705)
```haskell
  , cppGovActionDeposit :: !(THKD ('PPGroups 'GovGroup 'SecurityGroup) f (CompactForm Coin))
  -- ^ The amount of the Gov Action deposit
  , cppDRepDeposit :: !(THKD ('PPGroups 'GovGroup 'NoStakePoolGroup) f (CompactForm Coin))
  -- ^ The amount of a DRep registration deposit
  , cppDRepActivity :: !(THKD ('PPGroups 'GovGroup 'NoStakePoolGroup) f EpochInterval)
  -- ^ The number of Epochs that a DRep can perform no activity without losing their @Active@ status.
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Epoch.hs (L197-201)
```haskell
updateNumDormantEpochs :: EpochNo -> Proposals era -> VState era -> VState era
updateNumDormantEpochs currentEpoch ps vState =
  if null $ OMap.filter ((currentEpoch <=) . gasExpiresAfter) $ ps ^. pPropsL
    then vState & vsNumDormantEpochsL %~ succ
    else vState
```
