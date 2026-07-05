### Title
Governance Proposal Deposit Permanently Lost to Treasury via Unregistered Return Address During Bootstrap Phase - (File: `eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Gov.hs`)

---

### Summary

During the Conway bootstrap phase (protocol version major == 9), the `GOV` rule skips the check that a proposal's return address stake credential is registered. This allows a transaction sender to submit a governance proposal with an unregistered return address, pay the full `ppGovActionDepositL` deposit, and then permanently lose that deposit to the treasury when the proposal expires or is removed — with no recovery mechanism.

---

### Finding Description

In `conwayGovTransition`, the return-address registration check is gated behind a bootstrap-phase guard:

```haskell
unless (hardforkConwayBootstrapPhase $ pp ^. ppProtocolVersionL) $ do
  let refundAddress = proposal ^. pProcReturnAddrL
  isAccountRegistered (refundAddress ^. accountAddressCredentialL) (certDState ^. accountsL)
    ?! (injectFailure . ProposalReturnAccountDoesNotExist) refundAddress
``` [1](#0-0) 

`hardforkConwayBootstrapPhase` returns `True` exactly when `pvMajor pv == natVersion @9`: [2](#0-1) 

During bootstrap, the entire `unless` block is skipped. A submitter can therefore include any `AccountAddress` — including one whose `Credential Staking` is not present in the accounts map — as `pProcReturnAddr` in a `ProposalProcedure`. The deposit (`pProcDeposit`) is still deducted from the submitter's UTxO via the normal value-conservation check.

At every epoch boundary, `returnProposalDeposits` is called for all expired, enacted, and pruned proposals:

```haskell
processProposal gas (!accounts, !unclaimed)
  | (Just _accountState, newAccounts) <- updateLookupAccountState addRefund cred accounts =
      (newAccounts, unclaimed)
  | otherwise = (accounts, Map.insert (gasId gas) (gasDeposit gas) unclaimed)
  where
    cred = gasReturnAddr gas ^. accountAddressCredentialL
``` [3](#0-2) 

If the credential is not registered, the deposit falls into `unclaimed`. The epoch transition then routes all unclaimed amounts directly to the treasury:

```haskell
& casTreasuryL <>~ (utxoState0 ^. utxosDonationL <> fold unclaimed)
``` [4](#0-3) 

There is no mechanism for the original depositor to reclaim funds once they have entered the treasury. The existing test `depositMovesToTreasuryWhenStakingAddressUnregisters` confirms this is the actual runtime behavior: [5](#0-4) 

Post-bootstrap (pv major ≥ 10), the `ProposalReturnAccountDoesNotExist` predicate failure prevents submission with an unregistered address. During bootstrap, that guard is absent, creating a one-way door: deposit in, no refund out.

---

### Impact Explanation

**High — Permanent freezing of funds/deposits where recovery requires a hard fork.**

The governance proposal deposit (controlled by `ppGovActionDepositL`, currently 100,000,000 lovelace on mainnet) is irrecoverably transferred to the treasury. The submitter has no on-chain action available to retrieve it. Treasury funds can only be redistributed via a ratified `TreasuryWithdrawals` governance action, which requires governance supermajority approval — effectively requiring a coordinated governance intervention or a hard fork to restore the funds to the original depositor.

---

### Likelihood Explanation

**Low-Medium.** The bootstrap phase is active only at protocol version major == 9 (the initial Conway deployment window). Any user who submits a bootstrap-allowed proposal (`ParameterChange`, `HardForkInitiation`, `InfoAction`) with a return address whose stake credential is not registered — whether by mistake (e.g., using a script credential that was never registered, or a key credential that was deregistered before proposal expiry) — permanently loses the deposit. No privileged access is required; any transaction sender can trigger this path.

---

### Recommendation

Enforce the `isAccountRegistered` check unconditionally for all protocol versions, removing the `unless (hardforkConwayBootstrapPhase ...)` guard around the return-address validation in `conwayGovTransition`. Alternatively, if bootstrap-phase proposals with unregistered return addresses must be permitted for operational reasons, add a fallback that returns the deposit to the submitter's payment address rather than routing it to the treasury.

---

### Proof of Concept

1. Network is at protocol version major == 9 (bootstrap phase active; `hardforkConwayBootstrapPhase` returns `True`).
2. Attacker/user constructs a `ProposalProcedure` with:
   - `pProcGovAction = ParameterChange ...` (a bootstrap-allowed action)
   - `pProcReturnAddr = AccountAddress Testnet (AccountId unregisteredCred)` where `unregisteredCred` is **not** present in `certDState ^. accountsL`
   - `pProcDeposit = ppGovActionDepositL pp` (correct deposit amount)
3. The `GOV` rule accepts the proposal: `checkBootstrapProposal` passes (it is a bootstrap action), and the `isAccountRegistered` check is skipped because `hardforkConwayBootstrapPhase` is `True`. [6](#0-5) 
4. The deposit is deducted from the submitter's UTxO via value conservation.
5. After `ppGovActionLifetimeL` epochs, the proposal expires and enters `expiredActions`.
6. `proposalsApplyEnactment` returns it in `allRemovedGovActions`. [7](#0-6) 
7. `returnProposalDeposits` finds `unregisteredCred` absent from accounts; the deposit is placed in `unclaimed`. [8](#0-7) 
8. `casTreasuryL <>~ fold unclaimed` moves the deposit permanently into the treasury. [4](#0-3) 
9. The original depositor has no on-chain path to recover the funds.

### Citations

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Gov.hs (L483-508)
```haskell
  let processProposal proposals (idx, proposal@ProposalProcedure {..}) = do
        runTest $ checkBootstrapProposal pp proposal

        let newGaid = GovActionId txid idx

        -- In a HardFork, check that the ProtVer can follow
        let badHardFork = do
              (prevGaid, newProtVer, prevProtVer) <-
                preceedingHardFork @era pp prevGovActionIds proposals pProcGovAction
              guard (not (pvCanFollow prevProtVer newProtVer))
              Just $
                ProposalCantFollow @era prevGaid $
                  Mismatch
                    { mismatchSupplied = newProtVer
                    , mismatchExpected = prevProtVer
                    }
        failOnJust badHardFork injectFailure

        -- PParamsUpdate well-formedness check
        runTest $ actionWellFormed (pp ^. ppProtocolVersionL) pProcGovAction

        unless (hardforkConwayBootstrapPhase $ pp ^. ppProtocolVersionL) $ do
          let refundAddress = proposal ^. pProcReturnAddrL
              govAction = proposal ^. pProcGovActionL
          isAccountRegistered (refundAddress ^. accountAddressCredentialL) (certDState ^. accountsL)
            ?! (injectFailure . ProposalReturnAccountDoesNotExist) refundAddress
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Era.hs (L256-257)
```haskell
hardforkConwayBootstrapPhase :: ProtVer -> Bool
hardforkConwayBootstrapPhase pv = pvMajor pv == natVersion @9
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Epoch.hs (L187-193)
```haskell
    processProposal gas (!accounts, !unclaimed)
      | (Just _accountState, newAccounts) <- updateLookupAccountState addRefund cred accounts =
          (newAccounts, unclaimed)
      | otherwise = (accounts, Map.insert (gasId gas) (gasDeposit gas) unclaimed)
      where
        addRefund = balanceAccountStateL <>~ compactCoinOrError (gasDeposit gas)
        cred = gasReturnAddr gas ^. accountAddressCredentialL
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Epoch.hs (L314-329)
```haskell
    (newProposals, enactedActions, removedDueToEnactment, expiredActions) =
      proposalsApplyEnactment rsEnacted rsExpired (govState0 ^. proposalsGovStateL)

    -- Apply the values from the computed EnactState to the GovState
    govState1 =
      govState0
        & cgsProposalsL .~ newProposals
        & cgsCommitteeL .~ ensCommittee
        & cgsConstitutionL .~ ensConstitution
        & cgsCurPParamsL .~ nextEpochPParams govState0
        & cgsPrevPParamsL .~ curPParams
        & cgsFuturePParamsL .~ PotentialPParamsUpdate Nothing

    allRemovedGovActions = Map.unions [expiredActions, enactedActions, removedDueToEnactment]
    (newAccounts, unclaimed) =
      returnProposalDeposits allRemovedGovActions $ dState2 ^. accountsL
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Epoch.hs (L349-350)
```haskell
        -- Move donations and unclaimed rewards from proposals to treasury:
        & casTreasuryL <>~ (utxoState0 ^. utxosDonationL <> fold unclaimed)
```

**File:** eras/conway/impl/testlib/Test/Cardano/Ledger/Conway/Imp/EpochSpec.hs (L452-487)
```haskell
depositMovesToTreasuryWhenStakingAddressUnregisters ::
  ConwayEraImp era => ImpTestM era ()
depositMovesToTreasuryWhenStakingAddressUnregisters = do
  disableTreasuryExpansion
  initialTreasury <- getsNES treasuryL
  modifyPParams $ \pp ->
    pp
      & ppGovActionLifetimeL .~ EpochInterval 8
      & ppGovActionDepositL .~ Coin 100
      & ppCommitteeMaxTermLengthL .~ EpochInterval 0
  returnAddr <- registerAccountAddress
  govActionDeposit <- getsNES $ nesEsL . curPParamsEpochStateL . ppGovActionDepositL
  keyDeposit <- getsNES $ nesEsL . curPParamsEpochStateL . ppKeyDepositL
  govPolicy <- getGovPolicy
  gaid <-
    mkProposalWithAccountAddress
      ( ParameterChange
          SNothing
          (emptyPParamsUpdate & ppuGovActionDepositL .~ SJust (Coin 1000000))
          govPolicy
      )
      returnAddr
      >>= submitProposal
  expectPresentGovActionId gaid
  replicateM_ 5 passEpoch
  expectTreasury initialTreasury
  expectRegisteredAccountAddress returnAddr
  submitTx_ $
    mkBasicTx mkBasicTxBody
      & bodyTxL . certsTxBodyL
        .~ SSeq.singleton
          (UnRegDepositTxCert (returnAddr ^. accountAddressCredentialL) keyDeposit)
  expectNotRegisteredRewardAddress returnAddr
  replicateM_ 5 passEpoch
  expectMissingGovActionId gaid
  expectTreasury $ initialTreasury <> govActionDeposit
```
