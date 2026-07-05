### Title
Governance Proposal Deposit Permanently Lost to Treasury When Return Address Is Unregistered During Bootstrap Phase - (File: `eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Gov.hs`)

---

### Summary

During the Conway bootstrap phase (protocol version 9), the `GOV` rule skips the validation that a proposal's return address must be a registered stake credential. Any transaction sender can submit a governance proposal with an unregistered return address, pay the required deposit, and permanently lose that deposit to the treasury — with no mechanism to recover it — because the `returnProposalDeposits` function at the epoch boundary cannot credit an unregistered account.

---

### Finding Description

The `conwayGovTransition` function in the `GOV` rule guards the return-address registration check behind `unless (hardforkConwayBootstrapPhase ...)`:

```haskell
unless (hardforkConwayBootstrapPhase $ pp ^. ppProtocolVersionL) $ do
  let refundAddress = proposal ^. pProcReturnAddrL
  isAccountRegistered (refundAddress ^. accountAddressCredentialL) (certDState ^. accountsL)
    ?! (injectFailure . ProposalReturnAccountDoesNotExist) refundAddress
``` [1](#0-0) 

`hardforkConwayBootstrapPhase` is true exactly when `pvMajor pv == natVersion @9`: [2](#0-1) 

During bootstrap, the check is entirely absent. A proposer can therefore submit a bootstrap-allowed governance action (e.g., `InfoAction`) with a `pProcReturnAddr` whose stake credential is **not** registered in the ledger's accounts map, while still paying the full `ppGovActionDeposit`.

At the epoch boundary, `returnProposalDeposits` iterates over all removed (expired or enacted) proposals and attempts to credit each deposit to its return address:

```haskell
processProposal gas (!accounts, !unclaimed)
  | (Just _accountState, newAccounts) <- updateLookupAccountState addRefund cred accounts =
      (newAccounts, unclaimed)
  | otherwise = (accounts, Map.insert (gasId gas) (gasDeposit gas) unclaimed)
``` [3](#0-2) 

Because the return address is not registered, the `otherwise` branch fires and the deposit is placed in `unclaimed`. The `epochTransition` then sweeps all unclaimed amounts into the treasury:

```haskell
& casTreasuryL <>~ (utxoState0 ^. utxosDonationL <> fold unclaimed)
``` [4](#0-3) 

The proposer's deposit is permanently redirected to the treasury. There is no mechanism for the proposer to recover it: the treasury can only be disbursed via a ratified `TreasuryWithdrawals` governance action, which requires DRep/CC/SPO supermajority approval and would not be directed back to the original depositor.

---

### Impact Explanation

**Medium.** An attacker-controlled (or simply mistaken) transaction modifies deposit refunds outside design parameters. The proposer pays `ppGovActionDeposit` ADA and receives nothing back; the funds are permanently redirected to the treasury. The post-bootstrap design explicitly requires a registered return address at submission time precisely to prevent this outcome, but the bootstrap guard removes that protection entirely. The deposit pot and treasury accounting remain internally consistent (no double-spend or creation of ADA), but the proposer suffers an unrecoverable loss of their deposit.

---

### Likelihood Explanation

The bootstrap phase is active for any node running Conway at protocol version 9 (the initial Conway version). Any unprivileged transaction sender can craft a `ProposalProcedure` with an arbitrary, unregistered `pProcReturnAddr` and submit it in a valid transaction. No special privilege, key compromise, or governance majority is required. The only prerequisite is that the network is still in the bootstrap phase. On mainnet this phase has passed, but the code path remains live for any network at protocol version 9 (private testnets, staging environments, or a future network bootstrapping at version 9).

---

### Recommendation

Remove the `unless (hardforkConwayBootstrapPhase ...)` guard around the return-address registration check, or extend the bootstrap-phase check to also validate that the return address is registered. The post-bootstrap behavior (rejecting proposals with unregistered return addresses) is the correct invariant and should apply unconditionally. The `ProposalReturnAccountDoesNotExist` predicate failure already exists and is serialized; enforcing it during bootstrap requires only removing the `unless` wrapper. [5](#0-4) 

---

### Proof of Concept

1. Network is at protocol version 9 (bootstrap phase active).
2. Attacker generates a fresh key pair `(vk, sk)` but does **not** register the corresponding stake credential.
3. Attacker constructs `AccountAddress { aaNetworkId = <network>, aaId = AccountId (KeyHashObj (hash vk)) }` — this address is not in the accounts map.
4. Attacker submits a transaction containing:
   ```
   ProposalProcedure
     { pProcDeposit    = ppGovActionDeposit   -- correct deposit amount
     , pProcReturnAddr = <unregistered address>
     , pProcGovAction  = InfoAction
     , pProcAnchor     = <any anchor>
     }
   ```
5. The `GOV` rule accepts the proposal because `hardforkConwayBootstrapPhase` is `True` and the `isAccountRegistered` check is skipped. [1](#0-0) 
6. After `ppGovActionLifetime` epochs, the proposal expires. `returnProposalDeposits` finds no registered account for the return address and places the deposit in `unclaimed`. [6](#0-5) 
7. `epochTransition` adds `unclaimed` to the treasury. The proposer's deposit is gone. [7](#0-6) 

The existing test `depositMovesToTreasuryWhenStakingAddressUnregisters` confirms this treasury-absorption behavior when the return address becomes unregistered after submission; the bootstrap bypass makes it reachable even when the address was never registered to begin with. [8](#0-7)

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

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Epoch.hs (L347-350)
```haskell
    chainAccountState3 =
      chainAccountState2
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
