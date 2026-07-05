### Title
`DirectDeposits` Omitted from Value Conservation Check Enables ADA Creation from Thin Air — (`eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs`)

---

### Summary

In the Dijkstra era, the `directDeposits` field present in both top-level and sub-transaction bodies is applied to account balances by the `ENTITIES`/`SUBENTITIES` rules, but is **never included in the "produced" value** used by the UTXO value conservation check. An unprivileged transaction submitter can craft a balanced transaction (where `consumed == produced` without `directDeposits`) that also carries non-zero `directDeposits`, causing ADA to be credited to account balances without being funded by any transaction input — creating ADA from thin air.

---

### Finding Description

The Dijkstra era introduces two new transaction body fields:

- `dtbrDirectDeposits` / `dstbrDirectDeposits` (`DirectDeposits`) — a map of `AccountAddress → Coin` that is applied to account balances by the `ENTITIES` rule (top-level tx) and the `SUBENTITIES` rule (sub-transactions).

The `ENTITIES` rule applies these deposits unconditionally after certificate processing:

```haskell
-- eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Entities.hs:211-216
let directDeposits = tx ^. bodyTxL . directDepositsTxBodyL
    accountsAfterCerts = certStateAfterCerts ^. certDStateL . accountsL
failOnJust (directDepositsMissingAccounts directDeposits accountsAfterCerts) $
  injectFailure . DirectDepositsToMissingAccounts
pure $ certStateAfterCerts & certDStateL . accountsL %~ applyDirectDeposits directDeposits
```

The `SUBENTITIES` rule does the same for sub-transactions:

```haskell
-- eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/SubEntities.hs:182-187
let directDeposits = tx ^. bodyTxL . directDepositsTxBodyL
    accountsAfterSubCerts = certStateAfterSubCerts ^. certDStateL . accountsL
failOnJust (directDepositsMissingAccounts directDeposits accountsAfterSubCerts) $
  injectFailure . SubDirectDepositsToMissingAccounts
pure $ certStateAfterSubCerts & certDStateL . accountsL %~ applyDirectDeposits directDeposits
```

However, the produced-value functions used by the UTXO value conservation check do **not** include `directDeposits`.

For sub-transactions, `dijkstraSubTxProducedValue` computes:

```haskell
-- eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs:258-261
dijkstraSubTxProducedValue pp isRegPoolId txBody =
  sumAllValue (txBody ^. outputsTxBodyL)
    <> inject (getTotalDepositsTxBody pp isRegPoolId txBody <> txBody ^. treasuryDonationTxBodyL)
    <> burnedMultiAssets txBody
```

`directDeposits` are absent. For top-level transactions, `dijkstraProducedValue` delegates to `conwayProducedValue`, which also has no knowledge of `directDeposits`:

```haskell
-- eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs:102-106
dijkstraProducedValue pp isRegPoolId txBody =
  conwayProducedValue pp isRegPoolId txBody
    <> foldMap'
      (getProducedValue pp isRegPoolId . view bodyTxL)
      (txBody ^. subTransactionsTxBodyL)
```

The UTXO rule enforces value conservation using these functions:

```haskell
-- eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs:380-381
{- consumed pp utxo₀ txb = produced pp certState txb -}
runTest $ Shelley.validateValueNotConservedUTxO pp originalUtxo certState txBody
```

Because `directDeposits` are absent from `produced`, the conservation equation is:

```
consumed(inputs + withdrawals + refunds) = produced(outputs + fee + cert_deposits + treasury_donation)
```

`directDeposits` appear on neither side. A transaction where `inputs = outputs + fee + cert_deposits` (balanced) passes the check regardless of the `directDeposits` amount. The `ENTITIES`/`SUBENTITIES` rules then credit those coins to account balances, creating ADA that was never funded by any input.

The `DirectDeposits` type is defined as a simple map:

```haskell
-- libs/cardano-ledger-core/src/Cardano/Ledger/Address.hs:991-993
newtype DirectDeposits = DirectDeposits {unDirectDeposits :: Map AccountAddress Coin}
```

There is no upper bound on the total amount, and the only validation performed is that target accounts are registered (`directDepositsMissingAccounts`). No check verifies that the sum of `directDeposits` is covered by the transaction's inputs.

---

### Impact Explanation

**Critical — Direct creation of ADA through an invalid ledger state transition.**

An attacker who controls a registered stake credential can:

1. Register a stake credential to create an account.
2. Submit a Dijkstra-era transaction with balanced inputs/outputs (so `consumed == produced` passes) and a `directDeposits` map crediting an arbitrary amount of ADA to their account.
3. The UTXO rule accepts the transaction (value conservation satisfied).
4. The ENTITIES/SUBENTITIES rule credits the `directDeposits` amount to the attacker's account balance.
5. The attacker withdraws the newly created ADA in a subsequent transaction.

This violates the fundamental preservation-of-value invariant of the Cardano ledger. The total ADA supply increases without any corresponding deduction from reserves, treasury, or UTxO, constituting direct ADA creation.

---

### Likelihood Explanation

The Dijkstra era is the latest era in this codebase and `directDeposits` is a newly introduced feature. Any unprivileged transaction submitter can exploit this — no special role, key, or governance threshold is required. The only prerequisite is having a registered stake credential (itself a permissionless operation). The attack is deterministic and repeatable.

---

### Recommendation

Include the sum of `directDeposits` in the produced-value calculation for both top-level and sub-transactions. Analogously to how `treasuryDonation` is included in `dijkstraSubTxProducedValue`, `directDeposits` must also be accounted for:

```haskell
dijkstraSubTxProducedValue pp isRegPoolId txBody =
  sumAllValue (txBody ^. outputsTxBodyL)
    <> inject (  getTotalDepositsTxBody pp isRegPoolId txBody
              <> txBody ^. treasuryDonationTxBodyL
              <> fold (unDirectDeposits (txBody ^. directDepositsTxBodyL))  -- ADD THIS
              )
    <> burnedMultiAssets txBody
```

The same fix must be applied to the top-level produced-value function (`dijkstraProducedValue` / `conwayProducedValue` path) for `dtbrDirectDeposits`.

---

### Proof of Concept

1. Register stake credential `cred` and obtain its `AccountAddress`.
2. Construct a Dijkstra-era top-level transaction:
   - `inputs`: one UTxO entry worth exactly `fee` ADA (e.g., 0.2 ADA).
   - `outputs`: empty (or one output returning change so inputs = outputs + fee).
   - `directDeposits`: `{ AccountAddress(cred) → 1_000_000_000_000 }` (1 million ADA).
3. Submit the transaction. The UTXO value conservation check passes because `consumed(fee) == produced(fee)`.
4. The ENTITIES rule applies `directDeposits`, crediting 1 million ADA to `cred`'s account.
5. Submit a withdrawal transaction draining the account balance.

The attacker has extracted 1 million ADA from the ledger without providing any corresponding input value. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6) [8](#0-7)

### Citations

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs (L102-106)
```haskell
dijkstraProducedValue pp isRegPoolId txBody =
  conwayProducedValue pp isRegPoolId txBody
    <> foldMap'
      (getProducedValue pp isRegPoolId . view bodyTxL)
      (txBody ^. subTransactionsTxBodyL)
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

**File:** libs/cardano-ledger-core/src/Cardano/Ledger/Address.hs (L991-993)
```haskell
newtype DirectDeposits = DirectDeposits {unDirectDeposits :: Map AccountAddress Coin}
  deriving (Show, Eq, Generic)
  deriving newtype (NoThunks, NFData, EncCBOR, DecCBOR)
```

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
