### Title
Governance Proposal Deposit Permanently Lost to Treasury When Submitted with Unregistered Return Address During Bootstrap Phase - (File: `eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Gov.hs`)

---

### Summary

During the Conway bootstrap phase (protocol version 9), the `GOV` rule skips the check that a proposal's deposit-return address is a registered stake account. Any transaction sender can submit a governance proposal with an unregistered return address, pay the required deposit, and when the proposal expires or is removed, the deposit is irrecoverably routed to the treasury instead of being refunded to the proposer.

---

### Finding Description

In `conwayGovTransition` (`eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Gov.hs`), the return-address registration check is wrapped in an `unless (hardforkConwayBootstrapPhase ...)` guard:

```haskell
unless (hardforkConwayBootstrapPhase $ pp ^. ppProtocolVersionL) $ do
  let refundAddress = proposal ^. pProcReturnAddrL
  isAccountRegistered (refundAddress ^. accountAddressCredentialL) (certDState ^. accountsL)
    ?! (injectFailure . ProposalReturnAccountDoesNotExist) refundAddress
``` [1](#0-0) 

`hardforkConwayBootstrapPhase` returns `True` when the major protocol version equals 9:

```haskell
hardforkConwayBootstrapPhase :: ProtVer -> Bool
hardforkConwayBootstrapPhase pv = pvMajor pv == natVersion @9
``` [2](#0-1) 

During bootstrap, only "bootstrap actions" (e.g., `HardForkInitiation`, security-group `ParameterChange`) are permitted via `checkBootstrapProposal`, but the return-address registration check is entirely absent. A proposal with an unregistered `pProcReturnAddr` is accepted and the deposit is collected.

At epoch boundary, `returnProposalDeposits` in `Epoch.hs` attempts to credit the deposit back to the return address. If the credential is not registered, the deposit is placed in `unclaimed`:

```haskell
processProposal gas (!accounts, !unclaimed)
  | (Just _accountState, newAccounts) <- updateLookupAccountState addRefund cred accounts =
      (newAccounts, unclaimed)
  | otherwise = (accounts, Map.insert (gasId gas) (gasDeposit gas) unclaimed)
``` [3](#0-2) 

The `unclaimed` map is then swept into the treasury:

```haskell
& casTreasuryL <>~ (utxoState0 ^. utxosDonationL <> fold unclaimed)
``` [4](#0-3) 

The deposit is permanently lost to the proposer. The treasury is only accessible via a subsequent governance action, which the original proposer does not control.

This is structurally identical to the external report's pattern: a recovery mechanism (return-address registration check) is bypassed for a specific state (bootstrap phase), making previously deposited funds irrecoverable through the normal path.

---

### Impact Explanation

**Medium.** An unprivileged transaction sender who submits a governance proposal during bootstrap with an unregistered return address loses their entire governance deposit (`ppGovActionDepositL` ADA) permanently. The deposit is routed to the treasury rather than refunded. Recovery requires a separate governance action (a `TreasuryWithdrawals` proposal) that the victim does not control and that requires ratification by DReps and the Constitutional Committee. This modifies deposit refunds outside design parameters — the post-bootstrap check (`ProposalReturnAccountDoesNotExist`) was introduced precisely to prevent this outcome.

---

### Likelihood Explanation

**Low.** The window is limited to protocol version 9 (the Conway bootstrap phase). The proposer must either accidentally or be socially-engineered into supplying an unregistered return address. No privileged access is required; any transaction sender can trigger this path. The deposit amount is a governance parameter and can be substantial.

---

### Recommendation

Apply the `ProposalReturnAccountDoesNotExist` check unconditionally, regardless of bootstrap phase, or explicitly document and enforce that the return address must be registered before a proposal deposit is accepted. The post-bootstrap guard at line 504 should be removed so that the check:

```haskell
isAccountRegistered (refundAddress ^. accountAddressCredentialL) (certDState ^. accountsL)
  ?! (injectFailure . ProposalReturnAccountDoesNotExist) refundAddress
``` [5](#0-4) 

applies during bootstrap as well. This mirrors the fix in the external report: implement a proper recovery/validation path rather than silently routing funds to an inaccessible destination.

---

### Proof of Concept

1. Network is at protocol version 9 (bootstrap phase, `hardforkConwayBootstrapPhase` = `True`).
2. Attacker/user constructs a `ProposalProcedure` with:
   - `pProcGovAction = HardForkInitiation SNothing someProtVer` (a bootstrap-allowed action)
   - `pProcReturnAddr = AccountAddress Testnet (AccountId unregisteredCred)` where `unregisteredCred` has no entry in `certDState ^. accountsL`
   - `pProcDeposit = ppGovActionDepositL pp` (correct deposit amount)
3. The `GOV` rule processes the proposal:
   - `checkBootstrapProposal` passes (it is a bootstrap action).
   - The `unless (hardforkConwayBootstrapPhase ...)` block is **skipped** — no registration check is performed.
   - The deposit is collected from the submitter's UTxO.
4. The proposal lives for `ppGovActionLifetimeL` epochs and expires without ratification.
5. At the epoch boundary, `returnProposalDeposits` finds `unregisteredCred` absent from `accounts`, inserts the deposit into `unclaimed`, and `epochTransition` adds it to `casTreasury`.
6. The submitter's deposit is gone; the treasury balance increases by `ppGovActionDepositL`.

The existing test `depositMovesToTreasuryWhenStakingAddressUnregisters` confirms the treasury-routing behavior for the post-submission unregistration case; the bootstrap-phase submission gap is the additional attack surface not covered by that test. [6](#0-5)

### Citations

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Gov.hs (L504-508)
```haskell
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

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Epoch.hs (L350-350)
```haskell
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
