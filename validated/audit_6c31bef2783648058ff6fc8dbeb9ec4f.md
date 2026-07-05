### Title
`directDeposits` Omitted from Preservation-of-Value Check Enables Unconstrained ADA Creation — (File: `eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs`)

---

### Summary

The Dijkstra era introduces a `directDeposits` field in transaction bodies that deposits ADA directly into registered reward accounts. However, the total amount of these deposits is never included in either the `consumed` or `produced` side of the preservation-of-value (PoV) equation. The `ENTITIES` rule applies `directDeposits` to account balances unconditionally, while the `UTXO` rule's PoV check remains unaware of them. An unprivileged transaction submitter can therefore create arbitrary ADA from nothing by populating `directDeposits` in a Dijkstra-era transaction.

---

### Finding Description

**New feature — `directDeposits`**

`DijkstraTxBodyRaw` (both `TopTx` and `SubTx` variants) carries a `dtbrDirectDeposits :: !DirectDeposits` / `dstbrDirectDeposits :: !DirectDeposits` field. [1](#0-0) [2](#0-1) 

`applyDirectDeposits` unconditionally **adds** the specified coin to each target account balance: [3](#0-2) 

**Where `directDeposits` are applied — `ENTITIES` / `SUBENTITIES` rules**

Both `dijkstraEntitiesTransition` and `dijkstraSubEntitiesTransition` apply `directDeposits` after processing certificates. The only guard is that every target credential is registered; there is no solvency check: [4](#0-3) [5](#0-4) 

**Where `directDeposits` are absent — the PoV equation**

The Dijkstra `UTXO` rule enforces PoV via the standard `validateValueNotConservedUTxO`: [6](#0-5) 

For `DijkstraEra`, `consumed = conwayConsumed` and `produced = getProducedDijkstraValue`. Neither path touches `directDeposits`:

```
consumed  = inputs + withdrawals + deposit_refunds          (no directDeposits)
produced  = outputs + fee + cert_deposits + donation        (no directDeposits)
```

`dijkstraProducedValue` (top-level) aggregates `conwayProducedValue` plus sub-transaction produced values: [7](#0-6) 

`dijkstraSubTxProducedValue` (sub-transaction) is: [8](#0-7) 

Neither function includes `directDeposits`. The `EraUTxO` instance confirms these are the authoritative implementations: [9](#0-8) 

**Net effect**: the PoV check passes for any value of `directDeposits`; the `ENTITIES` rule then credits those coins to accounts. The total ADA in the system increases by exactly `sum(directDeposits)` with no corresponding debit anywhere.

---

### Impact Explanation

**Critical — Direct creation of ADA through an invalid ledger state transition.**

An attacker can mint an unbounded quantity of ADA into their own reward account(s) in a single Dijkstra-era transaction. The coins are immediately withdrawable. This violates the fundamental preservation-of-value invariant and constitutes direct, unrecoverable loss of monetary integrity for the entire ledger.

---

### Likelihood Explanation

Any unprivileged transaction submitter can trigger this path. No special role, key, or governance threshold is required. The only prerequisite is that the target account(s) be registered, which the attacker controls. The Dijkstra era is the current development era; once deployed, every node that accepts Dijkstra-era transactions is exposed.

---

### Recommendation

Include the total `directDeposits` amount on the **produced** side of the PoV equation, mirroring how `treasuryDonation` was added to `conwayProducedValue`. Concretely:

1. In `dijkstraProducedValue` (top-level), add `inject (sumDirectDeposits txBody)` — and likewise aggregate over sub-transactions.
2. In

### Citations

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/TxBody.hs (L184-186)
```haskell
    , dtbrSubTransactions :: !(OMap TxId (Tx SubTx era))
    , dtbrDirectDeposits :: !DirectDeposits
    , dtbrAccountBalanceIntervals :: !(AccountBalanceIntervals era)
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/TxBody.hs (L205-207)
```haskell
    , dstbrRequiredTopLevelGuards :: !(Map (Credential Guard) (StrictMaybe (Data era)))
    , dstbrDirectDeposits :: !DirectDeposits
    , dstbrAccountBalanceIntervals :: !(AccountBalanceIntervals era)
```

**File:** libs/cardano-ledger-core/src/Cardano/Ledger/State/Account.hs (L290-298)
```haskell
applyDirectDeposits ::
  EraAccounts era =>
  DirectDeposits ->
  Accounts era ->
  Accounts era
applyDirectDeposits (DirectDeposits dd) =
  updateAccountBalances
    (\amount account -> addCompactCoin amount (account ^. balanceAccountStateL))
    dd
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Entities.hs (L211-216)
```haskell
  let directDeposits = tx ^. bodyTxL . directDepositsTxBodyL
      accountsAfterCerts = certStateAfterCerts ^. certDStateL . accountsL
  failOnJust (directDepositsMissingAccounts directDeposits accountsAfterCerts) $
    injectFailure . DirectDepositsToMissingAccounts

  pure $ certStateAfterCerts & certDStateL . accountsL %~ applyDirectDeposits directDeposits
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/SubEntities.hs (L182-187)
```haskell
  let directDeposits = tx ^. bodyTxL . directDepositsTxBodyL
      accountsAfterSubCerts = certStateAfterSubCerts ^. certDStateL . accountsL
  failOnJust (directDepositsMissingAccounts directDeposits accountsAfterSubCerts) $
    injectFailure . SubDirectDepositsToMissingAccounts

  pure $ certStateAfterSubCerts & certDStateL . accountsL %~ applyDirectDeposits directDeposits
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs (L380-381)
```haskell
  {- consumed pp utxo₀ txb = produced pp certState txb -}
  runTest $ Shelley.validateValueNotConservedUTxO pp originalUtxo certState txBody
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs (L93-106)
```haskell
dijkstraProducedValue ::
  ( DijkstraEraTxBody era
  , EraUTxO era
  , Value era ~ MaryValue
  ) =>
  PParams era ->
  (KeyHash StakePool -> Bool) ->
  TxBody TopTx era ->
  MaryValue
dijkstraProducedValue pp isRegPoolId txBody =
  conwayProducedValue pp isRegPoolId txBody
    <> foldMap'
      (getProducedValue pp isRegPoolId . view bodyTxL)
      (txBody ^. subTransactionsTxBodyL)
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs (L124-131)
```haskell
instance EraUTxO DijkstraEra where
  type ScriptsNeeded DijkstraEra = AlonzoScriptsNeeded DijkstraEra

  consumed = conwayConsumed

  getConsumedValue = getConsumedDijkstraValue

  getProducedValue = getProducedDijkstraValue
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs (L252-261)
```haskell
dijkstraSubTxProducedValue ::
  (ConwayEraTxBody era, Value era ~ MaryValue) =>
  PParams era ->
  (KeyHash StakePool -> Bool) ->
  TxBody SubTx era ->
  Value era
dijkstraSubTxProducedValue pp isRegPoolId txBody =
  sumAllValue (txBody ^. outputsTxBodyL)
    <> inject (getTotalDepositsTxBody pp isRegPoolId txBody <> txBody ^. treasuryDonationTxBodyL)
    <> burnedMultiAssets txBody
```
