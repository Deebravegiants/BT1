### Title
DRep Deposit Permanently Locked Without Unregistration Action — (File: `eras/conway/impl/src/Cardano/Ledger/Conway/Rules/GovCert.hs`)

---

### Summary

In the Conway era, a DRep's registration deposit can only be recovered by the DRep themselves via a `ConwayUnRegDRep` certificate signed with their own credential. There is no timeout, expiry-triggered refund, or governance-forced recovery path. If a DRep loses their private key or becomes permanently inactive, their deposit is irrecoverably locked in the deposit pot — an exact structural analog to the `rotateLiquidity()` single-actor lock described in the external report.

---

### Finding Description

The `GOVCERT` STS rule in `GovCert.hs` is the sole handler for DRep lifecycle transitions. On registration (`ConwayRegDRep`), the deposit is stored in `drepDeposit` inside `DRepState`: [1](#0-0) 

On unregistration (`ConwayUnRegDRep`), the deposit is returned only when the DRep's own credential signs the transaction: [2](#0-1) 

The `ConwayUnRegDRep` certificate type requires the DRep credential as its first argument — there is no alternative signer, no governance override, and no protocol-level forced unregistration: [3](#0-2) 

The DRep expiry mechanism (`drepExpiry`) marks a DRep as inactive for voting purposes but **does not trigger any deposit refund**. The `EPOCH` rule's `returnProposalDeposits` handles governance-action deposits on expiry, but there is no equivalent function for DRep deposits: [4](#0-3) 

The epoch transition confirms that only proposal deposits flow back to accounts or to the treasury on removal; DRep deposits have no such path: [5](#0-4) 

There is no governance action type (`GovAction`) that can forcibly unregister a DRep or redirect their deposit. The full set of `GovAction` constructors (`NoConfidence`, `UpdateCommittee`, `NewConstitution`, `HardForkInitiation`, `ParameterChange`, `TreasuryWithdrawals`, `InfoAction`) contains no DRep-unregistration path: [6](#0-5) 

---

### Impact Explanation

A DRep who loses their signing key — or whose script credential becomes permanently unspendable — leaves their deposit locked in the deposit pot with no protocol-level escape. The deposit cannot be returned to the DRep, redirected to the treasury, or recovered by any other party without a hard fork that forcibly removes the DRep entry from `vsDRepsL`. This satisfies the allowed impact:

> **High. Permanent freezing of funds, deposits, rewards, or withdrawals where recovery requires a hard fork.**

The deposit amount is set by `ppDRepDepositL` (a governance-controlled protocol parameter), so the locked value scales with the parameter and the number of affected DReps.

---

### Likelihood Explanation

Any user can register as a DRep by submitting a `ConwayRegDRep` certificate — no special privilege is required. Key loss is a realistic operational risk for long-lived DReps, particularly those using cold keys stored offline. The scenario does not require a malicious actor: accidental key loss, hardware failure, or death of the key holder suffices. The likelihood is **low-to-medium** per individual DRep, but the aggregate risk grows with DRep adoption.

---

### Recommendation

Add an epoch-boundary sweep that automatically returns the deposit of any DRep whose `drepExpiry` has passed by more than a configurable grace period (analogous to the `ppGovActionLifetimeL` timeout for governance proposals). Alternatively, introduce a governance action type that can forcibly unregister an expired DRep and route their deposit to the treasury, preventing indefinite lock-up.

---

### Proof of Concept

1. DRep registers: `ConwayRegDRep cred deposit SNothing` — deposit `D` is stored in `vsDRepsL` under `cred`.
2. DRep's signing key is lost (hardware failure, death, etc.).
3. Epochs pass; `drepExpiry` is reached — DRep becomes inactive, but `drepDeposit` remains in `vsDRepsL` unchanged.
4. No `ConwayUnRegDRep cred D` certificate can ever be submitted without the lost key.
5. `returnProposalDeposits` in `EPOCH` does not touch DRep deposits.
6. Deposit `D` is permanently locked in the deposit pot.
7. The only recovery path is a hard fork that removes the stale `DRepState` entry from ledger state.

### Citations

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

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/TxCert.hs (L571-572)
```haskell
  | ConwayUnRegDRep !(Credential DRepRole) !Coin
  | ConwayUpdateDRep !(Credential DRepRole) !(StrictMaybe Anchor)
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Epoch.hs (L179-193)
```haskell
returnProposalDeposits ::
  (Foldable f, EraAccounts era) =>
  f (GovActionState era) ->
  Accounts era ->
  (Accounts era, Map.Map GovActionId Coin)
returnProposalDeposits removedProposals oldAccounts =
  foldr' processProposal (oldAccounts, mempty) removedProposals
  where
    processProposal gas (!accounts, !unclaimed)
      | (Just _accountState, newAccounts) <- updateLookupAccountState addRefund cred accounts =
          (newAccounts, unclaimed)
      | otherwise = (accounts, Map.insert (gasId gas) (gasDeposit gas) unclaimed)
      where
        addRefund = balanceAccountStateL <>~ compactCoinOrError (gasDeposit gas)
        cred = gasReturnAddr gas ^. accountAddressCredentialL
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Epoch.hs (L327-350)
```haskell
    allRemovedGovActions = Map.unions [expiredActions, enactedActions, removedDueToEnactment]
    (newAccounts, unclaimed) =
      returnProposalDeposits allRemovedGovActions $ dState2 ^. accountsL
  tellEvent $
    GovInfoEvent
      (Set.fromList $ Map.elems enactedActions)
      (Set.fromList $ Map.elems removedDueToEnactment)
      (Set.fromList $ Map.elems expiredActions)
      unclaimed

  let
    certState2 =
      mkConwayCertState
        -- Increment the dormant epoch counter
        ( updateNumDormantEpochs eNo newProposals vState
            -- Remove cold credentials of committee members that were removed or were invalid
            & vsCommitteeStateL %~ updateCommitteeState (govState1 ^. cgsCommitteeL)
        )
        (certState1 ^. certPStateL)
        (dState2 & accountsL .~ newAccounts)
    chainAccountState3 =
      chainAccountState2
        -- Move donations and unclaimed rewards from proposals to treasury:
        & casTreasuryL <>~ (utxoState0 ^. utxosDonationL <> fold unclaimed)
```

**File:** eras/conway/impl/cddl/data/conway.cddl (L648-656)
```text
gov_action =
  [  parameter_change_action
  // hard_fork_initiation_action
  // treasury_withdrawals_action
  // no_confidence
  // update_committee
  // new_constitution
  // info_action
  ]
```
