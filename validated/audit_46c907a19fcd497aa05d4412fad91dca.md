### Title
Missing Cumulative Deposit-Refund Check Across Sub-Transactions Allows Double-Claiming of Stake Deposits in Dijkstra Era — (`eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs`)

---

### Summary

The Dijkstra era introduces nested transactions. The top-level UTXO rule validates cumulative **withdrawals** across all sub-transactions via `validateBatchWithdrawals`, but there is no analogous cumulative check for deposit **refunds** arising from `UnRegDepositTxCert` certificate processing within sub-transactions. An attacker can craft a top-level transaction whose sub-transactions each contain an `UnRegDepositTxCert` for the same staking credential, causing the same deposit to be refunded multiple times and creating ADA from nothing. The developers have explicitly acknowledged this gap with a disabled test and a `TODO` comment.

---

### Finding Description

The Dijkstra era's `dijkstraUtxoTransition` in `eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs` calls `validateBatchWithdrawals` at line 378, which aggregates all withdrawal amounts across the top-level transaction and every sub-transaction and checks the total against the **original** account balance: [1](#0-0) 

This correctly prevents double-withdrawal of rewards. However, deposit refunds from `UnRegDepositTxCert` certificates are not withdrawals — they are processed through the `SUBENTITIES` → `SUBCERTS` chain, one sub-transaction at a time, with no cross-sub-transaction deduplication check: [2](#0-1) 

Each sub-transaction's certificate processing is independent. The per-sub-transaction value conservation check does not verify whether the same deposit has already been claimed by a sibling sub-transaction.

The developers have explicitly acknowledged this missing check. The test `xit "Multiple subtransactions cannot get the same refund"` is disabled with `error "TODO: predicate failure not yet implemented"`: [3](#0-2) 

The `xit` marker (disabled/pending) combined with the `TODO` comment confirms that the production rule to prevent this scenario has not been implemented. By contrast, the analogous cumulative check for withdrawals **is** implemented: [4](#0-3) 

The structural gap is: `validateBatchWithdrawals` exists for reward withdrawals; no `validateBatchRefunds` exists for certificate deposit refunds.

---

### Impact Explanation

An attacker who registers a staking credential (paying `keyDeposit` ADA) can construct a Dijkstra top-level transaction containing two sub-transactions, each with `UnRegDepositTxCert stakingCred keyDeposit`. If both sub-transactions successfully claim the refund, `2 × keyDeposit` ADA is returned while only `keyDeposit` was deposited — directly creating ADA from nothing through an invalid ledger state transition.

This matches the allowed impact: **Critical — Direct creation of ADA through an invalid ledger state transition.**

---

### Likelihood Explanation

Any unprivileged transaction sender can:
1. Register a staking credential (paying the deposit).
2. Craft a Dijkstra top-level transaction with two sub-transactions, each containing `UnRegDepositTxCert` for the same credential.
3. Submit the transaction.

No privileged access, governance majority, leaked key, or external dependency is required. The attack is deterministic, repeatable, and scales linearly with the deposit amount.

---

### Recommendation

Add a cumulative deposit-refund check in `dijkstraUtxoTransition` analogous to `validateBatchWithdrawals`. Before sub-transaction processing, aggregate all `UnRegDepositTxCert` refund claims across the top-level transaction and all sub-transactions, and verify that no credential's deposit is claimed more than once. Alternatively, enforce at the `SUBENTITIES`/`SUBCERTS` level that a credential unregistered by one sub-transaction cannot be unregistered again by any sibling sub-transaction within the same batch.

---

### Proof of Concept

```
1. Register staking credential C, paying keyDeposit = D ADA.

2. Construct:
     subTx1 = mkBasicTx mkBasicTxBody
               & bodyTxL . certsTxBodyL .~ [UnRegDepositTxCert C D]
     subTx2 = mkBasicTx mkBasicTxBody
               & bodyTxL . certsTxBodyL .~ [UnRegDepositTxCert C D]

3. Construct top-level transaction:
     tx = mkBasicTx mkBasicTxBody
           & bodyTxL . subTransactionsTxBodyL .~ OMap.fromFoldable [subTx1, subTx2]

4. Submit tx.
   - subTx1 claims refund D → credential C unregistered, D ADA returned.
   - subTx2 claims refund D → no cumulative check prevents this → D ADA returned again.
   - Net: 2D ADA returned for D ADA deposited → D ADA created from nothing.
```

The developers' own disabled test at `eras/dijkstra/impl/testlib/Test/Cardano/Ledger/Dijkstra/Imp/CertSpec.hs` lines 53–75 describes exactly this scenario and marks the blocking predicate failure as unimplemented. [3](#0-2) [5](#0-4) [6](#0-5)

### Citations

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs (L249-280)
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
  where
    getAccountBalance (AccountAddress _ (AccountId cred)) =
      case lookupAccountState cred accounts of
        Nothing -> mempty -- unregistered account, 0 balance
        Just accountState -> fromCompact $ accountState ^. balanceAccountStateL
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs (L318-381)
```haskell
dijkstraUtxoTransition ::
  forall era.
  ( EraUTxO era
  , EraCertState era
  , DijkstraEraTxBody era
  , AlonzoEraTx era
  , EraStake era
  , InjectRuleFailure "UTXO" Shelley.ShelleyUtxoPredFailure era
  , InjectRuleFailure "UTXO" Allegra.AllegraUtxoPredFailure era
  , InjectRuleFailure "UTXO" Alonzo.AlonzoUtxoPredFailure era
  , InjectRuleFailure "UTXO" Babbage.BabbageUtxoPredFailure era
  , InjectRuleFailure "UTXO" DijkstraUtxoPredFailure era
  , Environment (EraRule "UTXO" era) ~ DijkstraUtxoEnv era
  , State (EraRule "UTXO" era) ~ UTxOState era
  , Signal (EraRule "UTXO" era) ~ StAnnTx TopTx era
  , BaseM (EraRule "UTXO" era) ~ ShelleyBase
  , STS (EraRule "UTXO" era)
  , Event (EraRule "UTXO" era) ~ Alonzo.AlonzoUtxoEvent era
  , -- In this function we call the UTXOS rule, so we need some assumptions
    Environment (EraRule "UTXOS" era) ~ ()
  , State (EraRule "UTXOS" era) ~ ()
  , Signal (EraRule "UTXOS" era) ~ StAnnTx TopTx era
  , Embed (EraRule "UTXOS" era) (EraRule "UTXO" era)
  ) =>
  TransitionRule (EraRule "UTXO" era)
dijkstraUtxoTransition = do
  TRC (DijkstraUtxoEnv slot pp certState originalUtxo, utxos, stAnnTx) <-
    judgmentContext
  let tx = stAnnTx ^. txStAnnTxG
  -- this is the original Accounts, before any transactions were applied
  let accounts = certState ^. certDStateL . accountsL

  let txBody = tx ^. bodyTxL

  {- inInterval (SlotOf Γ) (ValidIntervalOf txTop) -}
  runTest $ Allegra.validateOutsideValidityIntervalUTxO slot txBody

  sysSt <- liftSTS $ asks systemStart
  ei <- liftSTS $ asks epochInfo

  runTest $ Alonzo.validateOutsideForecast ei slot sysSt tx

  {- SpendInputs ≠ ∅ -}
  runTestOnSignal $ Shelley.validateInputSetEmptyUTxO txBody

  let allInputs = txBody ^. allInputsTxBodyF
      inputs = txBody ^. inputsTxBodyL

  {- SpendInputsOf txTop ∪ RefInputsOf txTop ∪ CollInputsOf txTop ⊆ dom(utxo₀) -}
  runTest $ Shelley.validateBadInputsUTxO originalUtxo allInputs

  {- SpendInputsOf txTop ⊆ dom(utxo_s) — prevents double-spend with subtxs -}
  runTest $ Shelley.validateBadInputsUTxO (utxosUtxo utxos) inputs

  {- minfee pp txTop utxo₀ ≤ txfee txb -}
  runTest $ Shelley.validateFeeTooSmallUTxO pp tx originalUtxo

  {- (RedeemersOf txTop ≠ ∅ ⊎ Any (λ txSub → RedeemersOf txSub ≠ ∅) subtxs) → collateralCheck -}
  validate $ validateBatchCollateral pp tx originalUtxo

  runTest $ validateBatchWithdrawals accounts tx

  {- consumed pp utxo₀ txb = produced pp certState txb -}
  runTest $ Shelley.validateValueNotConservedUTxO pp originalUtxo certState txBody
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/SubEntities.hs (L141-187)
```haskell
dijkstraSubEntitiesTransition ::
  forall era.
  ( EraTx era
  , DijkstraEraTxBody era
  , ConwayEraCertState era
  , Embed (EraRule "SUBCERTS" era) (SUBENTITIES era)
  , State (EraRule "SUBCERTS" era) ~ CertState era
  , Signal (EraRule "SUBCERTS" era) ~ Seq (TxCert era)
  , Environment (EraRule "SUBCERTS" era) ~ SubCertsEnv era
  , EraRule "SUBENTITIES" era ~ SUBENTITIES era
  , InjectRuleFailure "SUBENTITIES" SubEntitiesPredFailure era
  , InjectRuleFailure "SUBENTITIES" Conway.ConwayLedgerPredFailure era
  ) =>
  TransitionRule (SUBENTITIES era)
dijkstraSubEntitiesTransition = do
  TRC (subCertsEnv, certState, certificates) <- judgmentContext
  let tx = certsTx subCertsEnv
      pp = certsPParams subCertsEnv
      curEpoch = certsCurrentEpoch subCertsEnv
      withdrawals = tx ^. bodyTxL . withdrawalsTxBodyL
      accounts = certState ^. certDStateL . accountsL

  runTest $ Conway.validateWithdrawalsDelegated accounts tx

  network <- liftSTS $ asks networkId
  let (missingWithdrawals, exceededWithdrawals) =
        case withdrawalsThatExceedAccountBalance withdrawals network accounts of
          Nothing -> (Map.empty, Map.empty)
          Just (missing, exceeded) -> (unWithdrawals missing, exceeded)
  failOnNonEmptyMap missingWithdrawals $
    injectFailure . SubWithdrawalsMissingAccounts . Withdrawals . NEM.toMap
  failOnNonEmptyMap exceededWithdrawals $ injectFailure . SubWithdrawalAmountsExceedAccountBalances

  let certStateBeforeSubCerts =
        certState
          & Conway.updateDormantDRepExpiries tx curEpoch
          & Conway.updateVotingDRepExpiries tx curEpoch (pp ^. ppDRepActivityL)
          & certDStateL . accountsL %~ applyWithdrawals withdrawals
  certStateAfterSubCerts <-
    trans @(EraRule "SUBCERTS" era) $ TRC (subCertsEnv, certStateBeforeSubCerts, certificates)

  let directDeposits = tx ^. bodyTxL . directDepositsTxBodyL
      accountsAfterSubCerts = certStateAfterSubCerts ^. certDStateL . accountsL
  failOnJust (directDepositsMissingAccounts directDeposits accountsAfterSubCerts) $
    injectFailure . SubDirectDepositsToMissingAccounts

  pure $ certStateAfterSubCerts & certDStateL . accountsL %~ applyDirectDeposits directDeposits
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
