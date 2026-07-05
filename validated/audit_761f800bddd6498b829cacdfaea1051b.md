### Title
Governance Proposal Deposit Permanently Lost to Treasury via Missing Return-Address Registration Check During Bootstrap Phase — (File: `eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Gov.hs`)

---

### Summary

During the Conway bootstrap phase (protocol version 9), the ledger skips the check that a governance proposal's `pProcReturnAddr` is a registered account. A transaction sender can therefore submit a valid proposal whose deposit refund address is unregistered. When the proposal later expires or is superseded, `returnProposalDeposits` cannot credit the unregistered address and silently routes the entire deposit to the treasury — permanently destroying the proposer's funds with no on-chain error.

---

### Finding Description

In `conwayGovTransition` the return-address registration check is guarded by `unless (hardforkConwayBootstrapPhase ...)`:

```haskell
-- Gov.hs lines 504-520
unless (hardforkConwayBootstrapPhase $ pp ^. ppProtocolVersionL) $ do
  let refundAddress = proposal ^. pProcReturnAddrL
  isAccountRegistered (refundAddress ^. accountAddressCredentialL) (certDState ^. accountsL)
    ?! (injectFailure . ProposalReturnAccountDoesNotExist) refundAddress
``` [1](#0-0) 

`hardforkConwayBootstrapPhase` is `True` for any protocol version whose major component equals 9:

```haskell
hardforkConwayBootstrapPhase pv = pvMajor pv == natVersion @9
``` [2](#0-1) 

Because the guard is `unless`, the entire block — including `ProposalReturnAccountDoesNotExist` — is **never evaluated** during bootstrap. The proposal is accepted, the deposit is deducted from the proposer's UTxO, and the unregistered return address is stored verbatim in `GovActionState.gasReturnAddr`.

At the epoch boundary, `returnProposalDeposits` iterates over all removed proposals (expired, enacted, or superseded) and attempts to credit each return address:

```haskell
processProposal gas (!accounts, !unclaimed)
  | (Just _accountState, newAccounts) <-
        updateLookupAccountState addRefund cred accounts = (newAccounts, unclaimed)
  | otherwise = (accounts, Map.insert (gasId gas) (gasDeposit gas) unclaimed)
  where
    cred = gasReturnAddr gas ^. accountAddressCredentialL
``` [3](#0-2) 

If `cred` is not registered, the `otherwise` branch fires and the deposit is placed in `unclaimed`. `epochTransition` then sweeps `unclaimed` into the treasury:

```haskell
& casTreasuryL <>~ (utxoState0 ^. utxosDonationL <> fold unclaimed)
``` [4](#0-3) 

The deposit is gone. No predicate failure is raised; no event distinguishes this from a normal treasury donation. The existing test `depositMovesToTreasuryWhenStakingAddressUnregisters` confirms this path is reachable and produces exactly this outcome: [5](#0-4) 

---

### Impact Explanation

A governance action deposit (`ppGovActionDepositL`) is a substantial ADA amount (100,000 ADA on mainnet). When the deposit is routed to `unclaimed` and swept into the treasury, it is irreversibly removed from the proposer's control. The treasury is governed collectively; no individual can unilaterally recover the lost deposit. Recovery would require a governance action to withdraw the exact amount back — itself requiring a deposit — or a hard fork. This constitutes **permanent loss of ADA deposits outside design parameters**, matching the allowed impact: *Medium — attacker-controlled transactions modify deposits or refunds outside design parameters*, and potentially *High — permanent freezing of deposits where recovery requires a hard fork*.

---

### Likelihood Explanation

The bootstrap phase is active for any node running protocol version 9 (the initial Conway deployment). Any unprivileged transaction sender who submits a `ProposalProcedure` with a freshly generated (never-registered) credential as `pProcReturnAddr` during bootstrap will trigger this path. The proposer may do so accidentally (e.g., using a key that has not yet been registered) or be socially engineered into doing so. The ledger provides no rejection, no warning, and no event distinguishing this from a normal proposal. The `GovInfoEvent` emitted at epoch boundary does record `unclaimed` deposits, but only as an opaque map of `GovActionId → Coin` with no indication that the loss was avoidable.

---

### Recommendation

**Short term:** Remove the `unless (hardforkConwayBootstrapPhase ...)` guard from the return-address registration check, or add a separate, always-active check that rejects proposals whose `pProcReturnAddr` is unregistered regardless of bootstrap status. The bootstrap guard was introduced to relax *action-type* restrictions, not to waive deposit-safety invariants.

**Long term:** Emit a distinct predicate failure (e.g., `ProposalReturnAccountDoesNotExistBootstrap`) when a bootstrap-phase proposal carries an unregistered return address, so that wallets and tooling can surface a clear error rather than silently accepting a deposit-destroying transaction.

---

### Proof of Concept

1. Node is at protocol version 9 (bootstrap phase; `hardforkConwayBootstrapPhase` returns `True`).
2. Generate a fresh key hash `kh`; do **not** register it as a stake credential.
3. Construct a `ProposalProcedure` with `pProcReturnAddr = AccountAddress Testnet (AccountId (KeyHashObj kh))` and `pProcGovAction = InfoAction` (a bootstrap-allowed action type per `isBootstrapAction`).
4. Submit the transaction. The `GOV` rule accepts it: `checkBootstrapProposal` only checks action type; the `isAccountRegistered` check is skipped by `unless (hardforkConwayBootstrapPhase ...)`.
5. Allow the proposal to expire (`ppGovActionLifetimeL` epochs pass without ratification).
6. At the epoch boundary, `returnProposalDeposits` finds `kh` unregistered → deposit enters `unclaimed` → `casTreasuryL <>~ fold unclaimed` moves it to the treasury.
7. The proposer's deposit is permanently lost; the treasury balance increases by exactly `ppGovActionDepositL`.

### Citations

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Gov.hs (L504-520)
```haskell
        unless (hardforkConwayBootstrapPhase $ pp ^. ppProtocolVersionL) $ do
          let refundAddress = proposal ^. pProcReturnAddrL
              govAction = proposal ^. pProcGovActionL
          isAccountRegistered (refundAddress ^. accountAddressCredentialL) (certDState ^. accountsL)
            ?! (injectFailure . ProposalReturnAccountDoesNotExist) refundAddress
          case govAction of
            TreasuryWithdrawals withdrawals _ -> do
              let nonRegisteredAccounts =
                    flip Map.filterWithKey withdrawals $ \withdrawalAddress _ ->
                      not $
                        isAccountRegistered
                          (withdrawalAddress ^. accountAddressCredentialL)
                          (certDState ^. accountsL)
              failOnNonEmpty
                (Map.keys nonRegisteredAccounts)
                (injectFailure . TreasuryWithdrawalReturnAccountsDoNotExist)
            _ -> pure ()
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
