### Title
Governance Proposal Deposit Permanently Lost When Return Address Unregistered During Bootstrap Phase - (File: eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Gov.hs)

### Summary
During the Conway bootstrap phase, the `conwayGovTransition` rule in `Gov.hs` skips the `ProposalReturnAccountDoesNotExist` check. This allows any unprivileged user to submit a governance proposal (ParameterChange, HardForkInitiation, or InfoAction) with an unregistered return address, paying the governance action deposit. When the proposal expires, the deposit cannot be credited to the unregistered account and is permanently redirected to the treasury, causing the proposer to lose their ADA deposit.

### Finding Description
In `conwayGovTransition`, the return-address registration check is guarded by `unless (hardforkConwayBootstrapPhase ...)`:

```haskell
unless (hardforkConwayBootstrapPhase $ pp ^. ppProtocolVersionL) $ do
  let refundAddress = proposal ^. pProcReturnAddrL
      govAction = proposal ^. pProcGovActionL
  isAccountRegistered (refundAddress ^. accountAddressCredentialL) (certDState ^. accountsL)
    ?! (injectFailure . ProposalReturnAccountDoesNotExist) refundAddress
  case govAction of
    TreasuryWithdrawals withdrawals _ -> do
      ...
      failOnNonEmpty
        (Map.keys nonRegisteredAccounts)
        (injectFailure . TreasuryWithdrawalReturnAccountsDoNotExist)
    _ -> pure ()
```

During bootstrap, `checkBootstrapProposal` still permits `ParameterChange`, `HardForkInitiation`, and `InfoAction` proposals. However, the `isAccountRegistered` guard on `pProcReturnAddr` is entirely absent. A user can therefore submit any of these three proposal types with a `pProcReturnAddr` whose credential is not present in `certDState ^. accountsL`.

The deposit is collected at submission time. When the proposal later expires, `updateAccountBalances` uses `Map.adjust`, which silently no-ops on missing credentials:

```haskell
Map.adjust
  ( \account ->
      account & balanceAccountStateL .~ updateBalance (compactCoinOrError amount) account
  )
  credential
```

The deposit amount is therefore never credited to the proposer and is absorbed into the treasury, as confirmed by the existing test `depositMovesToTreasuryWhenStakingAddressUnregisters`.

The test suite explicitly encodes this asymmetry as expected behavior:

```haskell
submitBootstrapAwareFailingProposal_ proposal $
  FailPostBootstrap
    [injectFailure $ ProposalReturnAccountDoesNotExist unregisteredAccountAddress]
```

`FailPostBootstrap` means the check only fires after bootstrap; during bootstrap the proposal is accepted without error.

### Impact Explanation
Any user who submits a valid bootstrap-phase governance proposal with an unregistered return address permanently loses the governance action deposit (ADA). The deposit is not returned on expiry and is not recoverable without a hard fork to retroactively credit the account. This modifies deposit refunds outside the intended design parameter that "the amount deposited is always returned" (per the individual-deposit tracking ADR). Impact: **Medium** — attacker-controlled proposal modifies deposit refunds outside design parameters.

### Likelihood Explanation
The bootstrap phase is a real, live network state. Any user who (a) is unaware of the registration requirement, (b) uses a freshly generated key as the return address before registering it, or (c) deliberately exploits the gap, can trigger the loss. The window is bounded to the bootstrap period, and the user must actively submit a proposal, so likelihood is **Low** (analogous to the external report's 3/10).

### Recommendation
Remove the `unless (hardforkConwayBootstrapPhase ...)` guard from the `isAccountRegistered` check on `pProcReturnAddr`, or add an equivalent check inside the `checkBootstrapProposal` path. The deposit-return guarantee should be unconditional regardless of era phase:

```haskell
-- Apply to ALL proposals, not just post-bootstrap ones:
isAccountRegistered (refundAddress ^. accountAddressCredentialL) (certDState ^. accountsL)
  ?! (injectFailure . ProposalReturnAccountDoesNotExist) refundAddress
```

### Proof of Concept
1. Network is in Conway bootstrap phase (`hardforkConwayBootstrapPhase pv == True`).
2. Attacker generates a fresh key pair; does **not** register the stake credential.
3. Attacker submits a `ParameterChange` or `InfoAction` proposal with `pProcReturnAddr = AccountAddress Testnet (AccountId freshCred)` and `pProcDeposit = ppGovActionDepositL pp`.
4. The `GOV` rule accepts the proposal (no `ProposalReturnAccountDoesNotExist` failure).
5. The deposit is deducted from the attacker's UTxO.
6. After `ppGovActionLifetimeL` epochs the proposal expires; the epoch-boundary rule attempts to credit `freshCred` via `updateAccountBalances` / `Map.adjust`, which silently no-ops because `freshCred` is absent from `accountsMap`.
7. The deposit is absorbed into the treasury. The attacker's ADA is permanently lost.

---

**Root cause location:** [1](#0-0) 

**`updateAccountBalances` silent no-op on missing credential:** [2](#0-1) 

**Test confirming bootstrap-only suppression of the check:** [3](#0-2) 

**`depositMovesToTreasuryWhenStakingAddressUnregisters` confirming treasury absorption:** [4](#0-3)

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

**File:** libs/cardano-ledger-core/src/Cardano/Ledger/State/Account.hs (L312-323)
```haskell
updateAccountBalances updateBalance balanceMap =
  accountsMapL %~ \accountsMap ->
    Map.foldrWithKey'
      ( \(AccountAddress _ (AccountId credential)) amount ->
          Map.adjust
            ( \account ->
                account & balanceAccountStateL .~ updateBalance (compactCoinOrError amount) account
            )
            credential
      )
      accountsMap
      balanceMap
```

**File:** eras/conway/impl/testlib/Test/Cardano/Ledger/Conway/Imp/GovSpec.hs (L90-97)
```haskell
    it "ProposalReturnAccountDoesNotExist" $ do
      mkProposal InfoAction >>= submitProposal_
      unregisteredAccountAddress <- freshKeyHash >>= getAccountAddressFor . KeyHashObj

      proposal <- mkProposalWithAccountAddress InfoAction unregisteredAccountAddress
      submitBootstrapAwareFailingProposal_ proposal $
        FailPostBootstrap
          [injectFailure $ ProposalReturnAccountDoesNotExist unregisteredAccountAddress]
```

**File:** eras/conway/impl/testlib/Test/Cardano/Ledger/Conway/Imp/EpochSpec.hs (L415-417)
```haskell
    it
      "deposit is moved to treasury when the reward address is not registered"
      depositMovesToTreasuryWhenStakingAddressUnregisters
```
