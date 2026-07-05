### Title
Double-Counting of Deposit Refunds Across Sub-Transactions Enables ADA Creation - (File: eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs)

### Summary

In the Dijkstra era, the value-conservation check (`consumed == produced`) computes deposit refunds for all sub-transactions using the **original, pre-transaction** `certState`. Because the lookup function is never updated as sub-transactions are applied sequentially, an attacker can craft a batch where the same deposit is counted as a refund twice in the consumed side while only one deposit appears on the produced side, violating preservation of value and creating ADA from nothing.

### Finding Description

The Dijkstra era introduces nested ("sub") transactions. The top-level UTXO rule enforces value conservation over the entire batch at once:

```haskell
-- eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs, line 381
runTest $ Shelley.validateValueNotConservedUTxO pp originalUtxo certState txBody
```

`certState` here is the **original** state, before any sub-transaction is applied. [1](#0-0) 

`validateValueNotConservedUTxO` calls `consumed`, which for `DijkstraEra` resolves to `getConsumedDijkstraValue`:

```haskell
-- eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs, lines 78-91
getConsumedDijkstraValue pp lookupStakingDeposit lookupDRepDeposit utxo txBody =
  withBothTxLevels txBody
    ( \topTxBody ->
        txBodyConsumedValue topTxBody <> subTransactionsConsumedValue topTxBody
    )
    txBodyConsumedValue
  where
    txBodyConsumedValue = getConsumedMaryValue pp lookupStakingDeposit lookupDRepDeposit utxo
    subTransactionsConsumedValue topTxBody =
      foldMap'
        (getConsumedValue pp lookupStakingDeposit lookupDRepDeposit utxo . view bodyTxL)
        (topTxBody ^. subTransactionsTxBodyL)
``` [2](#0-1) 

The **same** `lookupStakingDeposit` closure (derived from the original `certState`) is passed to every sub-transaction's consumed-value computation. It is never updated to reflect the state changes made by earlier sub-transactions.

**Attack construction:**

Let `D` = current `keyDeposit` protocol parameter.

1. Attacker registers `stakingCred`, paying deposit `D`.
2. Attacker submits a top-level transaction containing two sub-transactions:
   - **subTx1** certs: `[UnRegDepositTxCert stakingCred D]`
   - **subTx2** certs: `[RegDepositTxCert stakingCred D, UnRegDepositTxCert stakingCred D]`

**Value-conservation check (uses original state for all lookups):**

| Side | Component | Amount |
|------|-----------|--------|
| Consumed | subTx1 refund (`lookupStakingDeposit` finds `D` in original state) | `D` |
| Consumed | subTx2 refund (reg+dereg in same tx → `keyDeposit = D`) | `D` |
| Produced | subTx2 deposit (re-registration) | `D` |

Equation: `inputs + 2D = outputs + fee + D` → `outputs = inputs + D - fee`

The attacker can place `D - fee` more ADA in outputs than they put in inputs. The check passes.

**Actual sequential execution (SUBENTITIES rule):**

- subTx1: `stakingCred` is registered → deregistration succeeds; credential removed.
- subTx2: `stakingCred` is now absent → re-registration succeeds; then immediate deregistration succeeds.

Both sub-transactions execute without error. The ledger accepts the transaction, and the attacker has created `D - fee` ADA from nothing.

The developers are aware of a related gap. The test file contains a disabled (`xit`) test titled "Multiple subtransactions cannot get the same refund" with the placeholder `error "TODO: predicate failure not yet implemented"`, confirming no guard exists yet: [3](#0-2) 

### Impact Explanation

**Critical. Direct creation of ADA through an invalid ledger state transition.**

An unprivileged user can repeatedly execute this batch to drain the deposit pot, creating unbounded ADA. Each execution yields `D - fee` net ADA. With `keyDeposit` currently set to 2 ADA and fees on the order of 0.2 ADA, each batch yields ~1.8 ADA. The attack is limited only by the attacker's ability to submit transactions and the size of the deposit pot.

### Likelihood Explanation

**High.** The entry path requires only a standard transaction submission — no privileged access, no governance majority, no key compromise. The Dijkstra era is the newest era in this repository and sub-transactions are a new feature. The disabled test and `TODO` comment confirm the gap is known but unguarded. Any user who reads the source or the test suite can reproduce this.

### Recommendation

The `getConsumedDijkstraValue` function must not reuse the original `lookupStakingDeposit` across sub-transactions. Two complementary fixes are needed:

1. **Thread updated state through sub-transaction consumed-value computation.** After each sub-transaction's certificates are applied, derive a new `lookupStakingDeposit` from the updated `certState` and use it for the next sub-transaction's refund calculation.

2. **Add a cross-sub-transaction deduplication guard.** Before accepting the batch, verify that no credential appears in a deregistration certificate in more than one sub-transaction (or that the net refund across the batch does not exceed the deposit recorded in the original state for any single credential).

The `validateBatchWithdrawals` function already demonstrates the correct pattern — it aggregates withdrawals across all sub-transactions and checks them against the **original** balance, preventing double-withdrawal. An analogous `validateBatchRefunds` check should be added for deposit refunds. [4](#0-3) 

### Proof of Concept

```
Setup:
  keyDeposit = D (e.g. 2 ADA)
  stakingCred = freshly generated staking credential

Step 1 – Register credential (pays D to deposit pot):
  tx_reg = { certs: [RegDepositTxCert stakingCred D] }
  submit tx_reg  -- deposit pot increases by D

Step 2 – Exploit batch:
  subTx1 = { inputs: [utxo_in1],
             certs:  [UnRegDepositTxCert stakingCred D],
             outputs: [addr1 ← (value_in1 + D)] }

  subTx2 = { inputs: [utxo_in2],
             certs:  [RegDepositTxCert stakingCred D,
                      UnRegDepositTxCert stakingCred D],
             outputs: [addr2 ← value_in2] }

  topTx  = { inputs: [utxo_fee],
             subTransactions: [subTx1, subTx2],
             outputs: [change ← (value_fee - fee)] }

Value conservation check (original certState):
  consumed = value_in1 + value_in2 + value_fee + D (subTx1) + D (subTx2) = Σ + 2D
  produced = (value_in1 + D) + value_in2 + (value_fee - fee) + fee + D (subTx2 reg)
           = Σ + 2D  ✓  (check passes)

Execution:
  subTx1: UnReg stakingCred → succeeds (was registered), deposit pot −D
  subTx2: Reg stakingCred  → succeeds (now absent),     deposit pot +D
          UnReg stakingCred → succeeds (just registered), deposit pot −D

Net deposit pot change: −D (one net deregistration)
Net attacker ADA gain:  +D − fee  (addr1 received D extra)
```

The transaction is accepted. The attacker has created `D - fee` ADA. Repeating the attack (re-registering between rounds) allows unbounded extraction.

### Citations

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

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs (L344-381)
```haskell
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

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs (L78-91)
```haskell
getConsumedDijkstraValue pp lookupStakingDeposit lookupDRepDeposit utxo txBody =
  withBothTxLevels
    txBody
    ( \topTxBody ->
        txBodyConsumedValue topTxBody <> subTransactionsConsumedValue topTxBody
    )
    txBodyConsumedValue
  where
    txBodyConsumedValue :: forall m. TxBody m era -> Value era
    txBodyConsumedValue = getConsumedMaryValue pp lookupStakingDeposit lookupDRepDeposit utxo
    subTransactionsConsumedValue topTxBody =
      foldMap'
        (getConsumedValue pp lookupStakingDeposit lookupDRepDeposit utxo . view bodyTxL)
        (topTxBody ^. subTransactionsTxBodyL)
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
