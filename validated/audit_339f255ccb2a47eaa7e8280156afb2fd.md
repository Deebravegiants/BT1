### Title
`directDeposits` Omitted from Preservation-of-Value Check Allows Unbounded ADA Creation - (File: `eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs`)

---

### Summary

The Dijkstra era introduces a `directDeposits` field in transaction bodies that credits ADA directly into registered account balances. However, `directDeposits` are never included in either the **consumed** or **produced** value calculations used by the preservation-of-value (PoV) check. Because the PoV check does not account for the ADA flowing into account balances via `directDeposits`, any transaction can deposit an arbitrary amount of ADA into accounts without providing a corresponding UTxO input to cover it, creating ADA out of thin air.

---

### Finding Description

The Dijkstra era's `UTXO` rule enforces the preservation-of-value invariant at line 381 of `eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs`:

```haskell
{- consumed pp utxo₀ txb = produced pp certState txb -}
runTest $ Shelley.validateValueNotConservedUTxO pp originalUtxo certState txBody
``` [1](#0-0) 

This calls `consumed` (bound to `conwayConsumed` → `getConsumedDijkstraValue`) and `produced` (bound to `getProducedDijkstraValue`).

**`getConsumedDijkstraValue`** sums UTxO inputs, withdrawals, and deposit refunds for the top-level transaction and all sub-transactions:

```haskell
txBodyConsumedValue = getConsumedMaryValue pp lookupStakingDeposit lookupDRepDeposit utxo
subTransactionsConsumedValue topTxBody =
  foldMap' (getConsumedValue ... utxo . view bodyTxL) (topTxBody ^. subTransactionsTxBodyL)
``` [2](#0-1) 

**`dijkstraProducedValue`** sums UTxO outputs, fees, certificate deposits, and treasury donations for the top-level transaction and all sub-transactions:

```haskell
dijkstraProducedValue pp isRegPoolId txBody =
  conwayProducedValue pp isRegPoolId txBody
    <> foldMap' (getProducedValue pp isRegPoolId . view bodyTxL) (txBody ^. subTransactionsTxBodyL)
``` [3](#0-2) 

**Neither function includes `directDeposits`.**

Meanwhile, the `ENTITIES` rule unconditionally applies `directDeposits` to account balances after the PoV check has already passed:

```haskell
let directDeposits = tx ^. bodyTxL . directDepositsTxBodyL
    accountsAfterCerts = certStateAfterCerts ^. certDStateL . accountsL
failOnJust (directDepositsMissingAccounts directDeposits accountsAfterCerts) $
  injectFailure . DirectDepositsToMissingAccounts
pure $ certStateAfterCerts & certDStateL . accountsL %~ applyDirectDeposits directDeposits
``` [4](#0-3) 

`applyDirectDeposits` simply adds the specified coin to each targeted account balance with no further checks:

```haskell
applyDirectDeposits (DirectDeposits dd) =
  updateAccountBalances
    (\amount account -> addCompactCoin amount (account ^. balanceAccountStateL))
    dd
``` [5](#0-4) 

The same omission exists for sub-transactions in `dijkstraSubEntitiesTransition`: [6](#0-5) 

**Algebraic proof of value creation:**

Let the PoV check pass: `UTxO_in + withdrawals + refunds = UTxO_out + fees + deposits + treasury_donations`.

Total ledger change after the transaction:

| Pot | Change |
|---|---|
| UTxO | `−UTxO_in + UTxO_out` |
| Account balances | `−withdrawals + directDeposits` |
| Fees pot | `+fees` |
| Deposits pot | `+deposits − refunds` |
| Treasury | `+treasury_donations` |

Summing and substituting the PoV equality, all terms cancel except **`+directDeposits`**. The total ADA in the ledger increases by exactly the `directDeposits` amount on every valid transaction that includes it.

---

### Impact Explanation

**Critical. Direct creation of ADA through an invalid ledger state transition.**

An attacker can include an arbitrarily large `directDeposits` value in a transaction body. The PoV check passes because `directDeposits` is absent from both sides of the equation. The `ENTITIES` rule then credits the full amount to the attacker's account. The attacker can immediately withdraw the ADA via a standard withdrawal. This can be repeated without bound, inflating the total ADA supply and causing direct, permanent loss to all ADA holders through debasement, and potentially draining any pool or treasury that the attacker targets.

---

### Likelihood Explanation

Any unprivileged transaction sender can exploit this. No special role, key, or governance threshold is required. The only prerequisite is a registered stake credential (a standard, low-cost operation). The `directDeposits` field is a first-class, serializable field in the Dijkstra transaction body CDDL:

```
, ? 25 : direct_deposits                 ; direct deposits
``` [7](#0-6) 

Any node that processes a Dijkstra-era block would accept such a transaction, making exploitation trivially reachable once the era activates.

---

### Recommendation

Include `directDeposits` in the **produced** side of the preservation-of-value calculation in `dijkstraProducedValue` (and `dijkstraSubTxProducedValue` for sub-transactions), analogously to how certificate deposits are included via `getTotalDepositsTxBody`:

```haskell
dijkstraProducedValue pp isRegPoolId txBody =
  conwayProducedValue pp isRegPoolId txBody
    <> inject (fold . unDirectDeposits $ txBody ^. directDepositsTxBodyL)  -- ADD THIS
    <> foldMap'
         (getProducedValue pp isRegPoolId . view bodyTxL)
         (txBody ^. subTransactionsTxBodyL)
```

The same fix must be applied to `dijkstraSubTxProducedValue` for sub-transaction bodies. A corresponding conformance/property-based test should verify that `consumed == produced` holds even when `directDeposits` are non-empty.

---

### Proof of Concept

1. Register a stake credential `cred` and obtain its `AccountAddress`.
2. Construct a Dijkstra-era transaction:
   - `inputs`: one UTxO covering only the transaction fee (e.g., 0.2 ADA).
   - `outputs`: one change output returning the remainder.
   - `directDeposits`: `{ accountAddress → 1_000_000_000_000 }` (1 million ADA).
   - `fee`: standard minimum fee.
3. Submit the transaction. The `UTXO` rule's PoV check passes because `directDeposits` is absent from `dijkstraProducedValue`. The `ENTITIES` rule credits 1,000,000 ADA to `cred`'s account balance.
4. Submit a withdrawal transaction claiming the full balance of `cred`.
5. 1,000,000 ADA has been created from a transaction that only consumed ~0.2 ADA in fees.

### Citations

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs (L380-381)
```haskell
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

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Entities.hs (L211-216)
```haskell
  let directDeposits = tx ^. bodyTxL . directDepositsTxBodyL
      accountsAfterCerts = certStateAfterCerts ^. certDStateL . accountsL
  failOnJust (directDepositsMissingAccounts directDeposits accountsAfterCerts) $
    injectFailure . DirectDepositsToMissingAccounts

  pure $ certStateAfterCerts & certDStateL . accountsL %~ applyDirectDeposits directDeposits
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

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/SubEntities.hs (L182-187)
```haskell
  let directDeposits = tx ^. bodyTxL . directDepositsTxBodyL
      accountsAfterSubCerts = certStateAfterSubCerts ^. certDStateL . accountsL
  failOnJust (directDepositsMissingAccounts directDeposits accountsAfterSubCerts) $
    injectFailure . SubDirectDepositsToMissingAccounts

  pure $ certStateAfterSubCerts & certDStateL . accountsL %~ applyDirectDeposits directDeposits
```

**File:** eras/dijkstra/impl/cddl/data/dijkstra.cddl (L131-132)
```text
  , ? 23 : sub_transactions                ; sub-transactions (NEW)
  , ? 25 : direct_deposits                 ; direct deposits
```
