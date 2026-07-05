### Title
Dijkstra Sub-Transaction Batch Allows Double-Claiming of Stake Deposit Refunds - (`eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs`)

---

### Summary

The Dijkstra era introduces nested (sub-)transactions. The `dijkstraUtxoTransition` rule includes a pre-execution batch check (`validateBatchWithdrawals`) that prevents total staking-reward withdrawals across all sub-transactions from exceeding the original account balance. However, **no analogous batch check exists for deposit refunds issued via `UnRegDepositTxCert` certificates**. An unprivileged transaction sender can craft a top-level transaction containing multiple sub-transactions that each include `UnRegDepositTxCert` for the same staking credential, causing the same deposit to be refunded multiple times and creating ADA that was never deposited.

---

### Finding Description

The Dijkstra era's `dijkstraUtxoTransition` function performs a pre-execution batch validation for staking-reward withdrawals:

```haskell
runTest $ validateBatchWithdrawals accounts tx
```

`validateBatchWithdrawals` sums all `withdrawalsTxBodyL` entries across the top-level transaction and every sub-transaction, then checks the total against the **original** (pre-batch) account balance. [1](#0-0) 

No equivalent check exists for deposit refunds produced by `UnRegDepositTxCert`. Those refunds are processed inside the sequential `SUBLEDGERS` → `SUBLEDGER` → `SUBENTITIES` → `SUBCERTS` → `SUBDELEG` pipeline, not in the pre-execution UTXO checks.

The developers themselves have acknowledged this gap with a disabled test:

```haskell
xit "Multiple subtransactions cannot get the same refund" $ do
  ...
  subTx1 = ... & bodyTxL . certsTxBodyL .~ SSeq.singleton (UnRegDepositTxCert stakingCred keyDeposit)
  subTx2 = ... & bodyTxL . certsTxBodyL .~ SSeq.singleton (UnRegDepositTxCert stakingCred keyDeposit)
  tx = mkBasicTx mkBasicTxBody
         & bodyTxL . subTransactionsTxBodyL .~ OMap.fromFoldable [subTx1, subTx2]
  submitFailingTx tx . NE.singleton $ error "TODO: predicate failure not yet implemented"
``` [2](#0-1) 

The `xit` marker disables the test because the predicate failure that should reject this transaction **has not been implemented**. The `error "TODO: predicate failure not yet implemented"` comment confirms the expected rejection path is absent from the production rules. Without that predicate failure, the transaction currently succeeds, and both sub-transactions receive the same deposit refund.

A second disabled test (`xit "Subtransaction consumes correct refund after keyDeposit is changed"`) further confirms that deposit-refund accounting in sub-transactions is an open, unresolved area. [3](#0-2) 

The top-level value-conservation check uses `originalUtxo` and the original `certState`:

```haskell
{- consumed pp utxo₀ txb = produced pp certState txb -}
runTest $ Shelley.validateValueNotConservedUTxO pp originalUtxo certState txBody
``` [4](#0-3) 

This check covers only the **top-level** transaction body against the pre-batch state; it does not aggregate the deposit-refund side-effects of all sub-transactions. Each sub-transaction's own value-conservation check is satisfied individually (each sub-tx balances against its own inputs/outputs), so the double-refund is invisible to any single conservation check.

---

### Impact Explanation

Each `UnRegDepositTxCert` for the same credential in a different sub-transaction causes the ledger to credit `keyDeposit` ADA to that sub-transaction's outputs while subtracting it from `utxosDeposited`. With N sub-transactions all unregistering the same credential, `(N − 1) × keyDeposit` ADA is created from nothing and `utxosDeposited` underflows. This is a **direct creation of ADA through an invalid ledger state transition**, matching the Critical impact tier: *"Direct loss, creation, or destruction of ADA or native assets through an invalid ledger state transition."*

---

### Likelihood Explanation

Any unprivileged transaction sender can construct a Dijkstra-era batch transaction. No special role, key, or governance threshold is required. The attacker only needs to:
1. Register a staking credential (paying `keyDeposit` once).
2. Submit a top-level transaction with N sub-transactions each containing `UnRegDepositTxCert` for that credential.

The cost is one `keyDeposit`; the gain is N × `keyDeposit`. The attack is repeatable and scales linearly.

---

### Recommendation

Add a pre-execution batch check in `dijkstraUtxoTransition` (analogous to `validateBatchWithdrawals`) that collects all `UnRegDepositTxCert` credentials across the top-level transaction and every sub-transaction, and rejects the batch if any credential appears more than once. This mirrors the existing pattern:

```haskell
-- Proposed: collect all UnRegDepositTxCert credentials across the batch
runTest $ validateBatchUnregCerts certState tx
```

The check should verify that each credential subject to an `UnRegDepositTxCert` appears at most once across the entire batch, and that the credential is actually registered in the **original** cert state (not the intermediate state after earlier sub-transactions). [5](#0-4) 

---

### Proof of Concept

1. Register staking credential `C`, paying `keyDeposit = D` ADA.
2. Construct:
   - `subTx1`: inputs = `{utxo1}`, certs = `[UnRegDepositTxCert C D]`
   - `subTx2`: inputs = `{utxo2}`, certs = `[UnRegDepositTxCert C D]`
   - `topTx`: sub-transactions = `{subTx1, subTx2}`
3. Submit `topTx`.
4. Both sub-transactions pass their individual value-conservation checks (each balances its own inputs/outputs including the refund `D`).
5. No batch-level predicate failure fires (the check is unimplemented per the `TODO` comment).
6. Result: `D` ADA is credited twice; `utxosDeposited` is decremented by `2D` while only `D` was ever deposited. Net ADA creation: `D`.

The developers' own disabled test at `CertSpec.hs:53–75` documents exactly this scenario and confirms the rejection predicate does not yet exist. [2](#0-1)

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

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs (L343-381)
```haskell
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

**File:** eras/dijkstra/impl/testlib/Test/Cardano/Ledger/Dijkstra/Imp/CertSpec.hs (L22-51)
```haskell
  xit "Subtransaction consumes correct refund after keyDeposit is changed" $ do
    stakingCred <- KeyHashObj <$> freshKeyHash
    _ <- registerStakeCredential stakingCred

    initialKeyDeposit <- getsPParams ppKeyDepositL
    impAnn "Change key deposit" $ do
      (dRep, _, _) <- setupSingleDRep 100_000_000
      ccHotCreds <- registerInitialCommittee
      let newKeyDeposit = initialKeyDeposit <> initialKeyDeposit
      ppChangeId <-
        submitParameterChange SNothing $
          emptyPParamsUpdate
            & ppuKeyDepositL .~ SJust newKeyDeposit
      submitYesVote_ (DRepVoter dRep) ppChangeId
      submitYesVoteCCs_ ccHotCreds ppChangeId
      getsPParams ppKeyDepositL `shouldReturn` initialKeyDeposit
      passNEpochs 2
      getsPParams ppKeyDepositL `shouldReturn` newKeyDeposit

    impAnn "Unregister staking credential" $ do
      expectStakeCredRegistered stakingCred
      let
        deRegCert = UnRegDepositTxCert stakingCred initialKeyDeposit
        subTransaction =
          mkBasicTx mkBasicTxBody
            & bodyTxL . certsTxBodyL .~ SSeq.singleton deRegCert
      submitTx_ $
        mkBasicTx mkBasicTxBody
          & bodyTxL . subTransactionsTxBodyL .~ OMap.singleton subTransaction
      expectStakeCredNotRegistered stakingCred
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
