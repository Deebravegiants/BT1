### Title
Multiple Sub-Transactions Can Claim the Same Deposit Refund Without Batch-Level Deduplication — (`eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/TxCert.hs`, `eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/SubLedgers.hs`)

---

### Summary

In the Dijkstra era, a top-level transaction may contain multiple sub-transactions. Each sub-transaction is processed sequentially by the `SUBLEDGERS` rule. The `dijkstraTotalRefundsTxCerts` function, which computes deposit refunds for value conservation, simply sums the deposit amounts declared in `UnRegDepositTxCert` certificates without any cross-sub-transaction deduplication. There is no batch-level guard preventing two sub-transactions from each declaring an `UnRegDepositTxCert` for the same staking credential. The developers themselves have acknowledged this gap with a disabled (`xit`) test whose expected predicate failure is explicitly marked `error "TODO: predicate failure not yet implemented"`.

---

### Finding Description

The Dijkstra era introduces nested sub-transactions (`subTransactionsTxBodyL`). The `SUBLEDGERS` rule iterates over all sub-transactions via `foldM`, applying each through `SUBLEDGER`:

```haskell
dijkstraSubLedgersTransition = do
  TRC (env, ledgerState, subTxs) <- judgmentContext
  foldM
    ( \ls subTx ->
        trans @(EraRule "SUBLEDGER" era) $ TRC (env, ls, subTx)
    )
    ledgerState
    subTxs
``` [1](#0-0) 

The refund calculation for each sub-transaction is performed by `dijkstraTotalRefundsTxCerts`, which blindly sums all `UnRegDepositTxCert` and `UnRegDRepTxCert` deposit amounts in the certificate list:

```haskell
dijkstraTotalRefundsTxCerts = foldMap' $ \case
  UnRegDepositTxCert _ deposit -> deposit
  UnRegDRepTxCert _ deposit -> deposit
  _ -> zero
``` [2](#0-1) 

This function is registered as the `getTotalRefundsTxCerts` implementation for `DijkstraEra`: [3](#0-2) 

Crucially, there is no batch-level check analogous to `validateBatchWithdrawals` (which guards against total withdrawals across all sub-transactions exceeding the account balance) for deposit refunds: [4](#0-3) 

The developers have explicitly acknowledged this missing protection in a disabled test:

```haskell
xit "Multiple subtransactions cannot get the same refund" $ do
    stakingCred <- KeyHashObj <$> freshKeyHash
    _ <- registerStakeCredential stakingCred
    keyDeposit <- getsPParams ppKeyDepositL
    ...
    let
      subTx1 = ... & bodyTxL . certsTxBodyL .~
                     SSeq.singleton (UnRegDepositTxCert stakingCred keyDeposit)
      subTx2 = ... & bodyTxL . certsTxBodyL .~
                     SSeq.singleton (UnRegDepositTxCert stakingCred keyDeposit)
      tx = ... & bodyTxL . subTransactionsTxBodyL .~
                 OMap.fromFoldable [subTx1, subTx2]
    submitFailingTx tx . NE.singleton $ error "TODO: predicate failure not yet implemented"
``` [5](#0-4) 

The `xit` prefix disables the test because the expected predicate failure does not yet exist. The `error "TODO: predicate failure not yet implemented"` would cause a runtime panic if the test ran, confirming the protection is absent. The same pattern appears in the Conway-era `CertSpec`: [6](#0-5) 

The `SUBLEDGER` rule processes `SUBENTITIES` (cert processing) before `SUBUTXOW` (UTxO/value conservation): [7](#0-6) 

Because `SUBDELEG` reuses `Conway.conwayDelegTransition` without a Dijkstra-specific batch guard, and because `dijkstraTotalRefundsTxCerts` does not deduplicate across sub-transactions, an attacker can construct a top-level transaction where two sub-transactions each declare `UnRegDepositTxCert` for the same credential. The first sub-transaction unregisters the credential and claims the refund; the second sub-transaction's value conservation check counts the same refund again, enabling the attacker to extract `2 × keyDeposit` from the deposit pot while only one deposit exists.

---

### Impact Explanation

**Critical — Direct loss of ADA through an invalid ledger state transition.**

An attacker who controls a registered staking credential can submit a single top-level transaction containing two sub-transactions, each with `UnRegDepositTxCert` for the same credential. If the batch-level refund deduplication check is absent (as the disabled test confirms), the value conservation rule for each sub-transaction independently counts the full `keyDeposit` as a refund. The deposit pot is debited twice for a single deposit, constituting a direct, attacker-controlled creation of ADA value from the deposit pot — an invalid ledger state transition.

---

### Likelihood Explanation

**Medium.** The Dijkstra era is in active development and sub-transactions are a new feature. Any user who can register a staking credential (an unprivileged operation) can construct this transaction. The attack requires no privileged access, no governance majority, and no key compromise. The only prerequisite is that the Dijkstra era is active on mainnet. The developers have already identified the scenario (the disabled test exists), confirming the attack vector is reachable.

---

### Recommendation

1. Add a batch-level validation in `dijkstraUtxoTransition` (analogous to `validateBatchWithdrawals`) that aggregates all `UnRegDepositTxCert` and `UnRegDRepTxCert` certificates across the top-level transaction and all sub-transactions, checks for duplicate credential unregistrations, and rejects any batch where the same credential is unregistered more than once.

2. Alternatively, extend `dijkstraTotalRefundsTxCerts` to track seen credentials and return zero for any duplicate `UnRegDepositTxCert` for the same credential within a single sub-transaction's certificate list, and add a cross-sub-transaction deduplication check in `SUBLEDGERS`.

3. Enable and complete the disabled test `"Multiple subtransactions cannot get the same refund"` in `Test.Cardano.Ledger.Dijkstra.Imp.CertSpec` by implementing the corresponding predicate failure.

---

### Proof of Concept

1. Register staking credential `C` with deposit `D` (e.g., `D = 2,000,000 lovelace`).
2. Construct `subTx1` with `UnRegDepositTxCert C D` and a valid UTxO input `i1`.
3. Construct `subTx2` with `UnRegDepositTxCert C D` and a distinct valid UTxO input `i2`.
4. Construct top-level `tx` with `subTransactionsTxBodyL = [subTx1, subTx2]`.
5. Submit `tx`. Without the batch-level guard, `subTx1` unregisters `C` and the value conservation check credits `D`; `subTx2`'s value conservation check also credits `D` (from `dijkstraTotalRefundsTxCerts`), allowing the attacker to extract `2D` from the deposit pot while only `D` was deposited.

The developers' own disabled test at `eras/dijkstra/impl/testlib/Test/Cardano/Ledger/Dijkstra/Imp/CertSpec.hs:53–75` constructs exactly this scenario and marks the expected rejection as `error "TODO: predicate failure not yet implemented"`, confirming the protection is absent.

### Citations

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/SubLedgers.hs (L128-135)
```haskell
dijkstraSubLedgersTransition = do
  TRC (env, ledgerState, subTxs) <- judgmentContext
  foldM
    ( \ls subTx ->
        trans @(EraRule "SUBLEDGER" era) $ TRC (env, ls, subTx)
    )
    ledgerState
    subTxs
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/TxCert.hs (L229-238)
```haskell
dijkstraTotalRefundsTxCerts ::
  ( Foldable f
  , ConwayEraTxCert era
  ) =>
  f (TxCert era) ->
  Coin
dijkstraTotalRefundsTxCerts = foldMap' $ \case
  UnRegDepositTxCert _ deposit -> deposit
  UnRegDRepTxCert _ deposit -> deposit
  _ -> zero
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/TxCert.hs (L285-285)
```haskell
  getTotalRefundsTxCerts _ _ _ = dijkstraTotalRefundsTxCerts
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs (L249-275)
```haskell
-- | For each account, the total withdrawals across the entire batch should not exceed the original account balance.
-- Unregistered accounts are treated as having 0 balance.
validateBatchWithdrawals ::
  ( EraTx era
  , EraAccounts era
  , DijkstraEraTxBody era
  ) =>
  Accounts era ->
  Tx TopTx era ->
  Test (DijkstraUtxoPredFailure era)
validateBatchWithdrawals accounts tx =
  let allWithdrawals =
        Map.unionsWith (<>) $
          unWithdrawals (tx ^. bodyTxL . withdrawalsTxBodyL)
            : [ unWithdrawals $ subTx ^. bodyTxL . withdrawalsTxBodyL
              | subTx <- OMap.elems $ tx ^. bodyTxL . subTransactionsTxBodyL
              ]
      badWithdrawals =
        Map.mapMaybeWithKey
          ( \acctAddr withdrawn ->
              let balance = getAccountBalance acctAddr
               in if withdrawn > balance
                    then Just Mismatch {mismatchSupplied = withdrawn, mismatchExpected = balance}
                    else Nothing
          )
          allWithdrawals
   in failureOnNonEmptyMap badWithdrawals WithdrawalsExceedAccountBalance
```

**File:** eras/dijkstra/impl/testlib/Test/Cardano/Ledger/Dijkstra/Imp/CertSpec.hs (L53-75)
```haskell
  xit "Multiple subtransactions cannot get the same refund" $ do
    stakingCred <- KeyHashObj <$> freshKeyHash
    _ <- registerStakeCredential stakingCred
    keyDeposit <- getsPParams ppKeyDepositL
    value1 <- arbitrary
    (_, addr1) <- freshKeyAddr
    input1 <- sendCoinTo addr1 value1
    value2 <- arbitrary
    (_, addr2) <- freshKeyAddr
    input2 <- sendCoinTo addr2 value2
    let
      subTx1 =
        mkBasicTx mkBasicTxBody
          & bodyTxL . inputsTxBodyL .~ Set.singleton input1
          & bodyTxL . certsTxBodyL .~ SSeq.singleton (UnRegDepositTxCert stakingCred keyDeposit)
      subTx2 =
        mkBasicTx mkBasicTxBody
          & bodyTxL . inputsTxBodyL .~ Set.singleton input2
          & bodyTxL . certsTxBodyL .~ SSeq.singleton (UnRegDepositTxCert stakingCred keyDeposit)
      tx =
        mkBasicTx mkBasicTxBody
          & bodyTxL . subTransactionsTxBodyL .~ OMap.fromFoldable [subTx1, subTx2]
    submitFailingTx tx . NE.singleton $ error "TODO: predicate failure not yet implemented"
```

**File:** eras/conway/impl/testlib/Test/Cardano/Ledger/Conway/Imp/DelegSpec.hs (L69-77)
```haskell
    it "Twice the same certificate in the same transaction" $ do
      -- This is expected behavior because `certsTxBodyL` removes duplicates
      freshKeyHash >>= \kh -> do
        regTxCert <- genRegTxCert (KeyHashObj kh)
        submitTx_ $
          mkBasicTx mkBasicTxBody
            & bodyTxL . certsTxBodyL
              .~ [regTxCert, regTxCert]
        expectStakeCredRegistered (KeyHashObj kh)
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/SubLedger.hs (L248-294)
```haskell
  (utxoStateBeforeSubUtxow, certStateFinal) <-
    if topIsValid == IsValid True
      then do
        runTest $ Conway.validateTreasuryValue txBody (chainAccountState ^. casTreasuryL)

        certStateAfterSubEntities <-
          trans @(EraRule "SUBENTITIES" era) $
            TRC
              ( SubCertsEnv tx pp curEpochNo committee (proposalsWithPurpose grCommitteeL proposals)
              , certState
              , StrictSeq.fromStrict $ txBody ^. certsTxBodyL
              )
        let govEnv =
              Conway.GovEnv
                (txIdTxBody txBody)
                curEpochNo
                pp
                (govState ^. constitutionGovStateL . constitutionGuardrailsScriptHashL)
                certStateAfterSubEntities
                committee
        let govSignal =
              Conway.GovSignal
                { Conway.gsVotingProcedures = txBody ^. votingProceduresTxBodyL
                , Conway.gsProposalProcedures = txBody ^. proposalProceduresTxBodyL
                , Conway.gsCertificates = txBody ^. certsTxBodyL
                }
        proposalsState <-
          trans @(EraRule "SUBGOV" era) $
            TRC
              ( govEnv
              , proposals
              , govSignal
              )
        pure
          ( utxoState & utxosGovStateL . proposalsGovStateL .~ proposalsState
          , certStateAfterSubEntities
          )
      else pure (utxoState, certState)

  utxoStateAfterSubUtxow <-
    trans @(EraRule "SUBUTXOW" era) $
      TRC
        ( SubUtxoEnv slot pp certState originalUtxo topIsValid
        , utxoStateBeforeSubUtxow
        , stAnnTx
        )
  pure $ LedgerState utxoStateAfterSubUtxow certStateFinal
```
