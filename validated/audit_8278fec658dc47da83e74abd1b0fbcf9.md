### Title
Direct Deposits Not Included in Preservation-of-Value Check Allows Unbounded ADA Creation - (File: `eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs`)

---

### Summary

In the Dijkstra era, the new `directDeposits` transaction body field causes ADA to be credited to registered accounts via `applyDirectDeposits`, but the corresponding coin amounts are absent from both the `consumed` and `produced` sides of the preservation-of-value (PoV) equation. An unprivileged transaction sender can therefore include arbitrarily large `directDeposits` in a valid transaction, causing ADA to be created from nothing and credited to any registered account.

---

### Finding Description

The Dijkstra era introduces a `directDeposits :: DirectDeposits` field (a `Map AccountAddress Coin`) in both top-level and sub-transaction bodies, accessible via `directDepositsTxBodyL`. [1](#0-0) 

During the `ENTITIES` transition, after certificates are processed, `applyDirectDeposits` is called unconditionally to add each listed amount to the corresponding account balance: [2](#0-1) 

`applyDirectDeposits` adds each coin amount to the matching account's balance with no further checks: [3](#0-2) 

The preservation-of-value check in the Dijkstra UTXO rule is: [4](#0-3) 

This calls `consumed` (bound to `conwayConsumed`) and `produced` (bound to `getProducedDijkstraValue`). The consumed side is computed by `getConsumedDijkstraValue`, which sums UTxO inputs, withdrawals, and refunds across the top-level tx and all sub-txs: [5](#0-4) 

The produced side is computed by `dijkstraProducedValue`, which sums UTxO outputs, fees, certificate deposits, treasury donation, and sub-tx produced values: [6](#0-5) 

`conwayProducedValue` (the base for the top-level tx) includes only outputs, fees, certificate deposits, and treasury donation — **no `directDeposits`**: [7](#0-6) 

`getProducedMaryValue` / `shelleyProducedValue` similarly contain no direct-deposit term: [8](#0-7) 

The `directDeposits` amounts are therefore invisible to the PoV equation. The equation balances without them, yet `applyDirectDeposits` still credits those amounts to accounts, violating the invariant that total ADA in the ledger is constant.

The only validation applied to `directDeposits` before application is a network-ID check and a check that target accounts are registered: [9](#0-8) [10](#0-9) 

Neither check constrains the coin amounts or requires them to be funded by the transaction's UTxO inputs.

The same flaw exists in the `SUBENTITIES` rule for sub-transactions: [11](#0-10) 

---

### Impact Explanation

**Critical — Direct creation of ADA through an invalid ledger state transition.**

An attacker submits a Dijkstra-era transaction whose `directDeposits` field credits an arbitrary amount of ADA (e.g., 45 billion ADA) to one or more registered accounts. The PoV check passes because `directDeposits` is absent from both `consumed` and `produced`. The ENTITIES rule then calls `applyDirectDeposits`, permanently inflating account balances. Total ADA in the ledger increases beyond the fixed supply cap, constituting a direct, irreversible creation of ADA.

---

### Likelihood Explanation

**High.** The Dijkstra era is a new era under active development. Any node running Dijkstra-era rules would accept such a transaction. The attacker needs only: (1) a registered target account (trivially obtained by registering their own stake credential), (2) a valid UTxO input to fund fees, and (3) knowledge of the `directDeposits` field encoding. No privileged access, governance majority, or key compromise is required.

---

### Recommendation

Include the sum of all `directDeposits` coin amounts in the **produced** side of the preservation-of-value equation inside `dijkstraProducedValue` (and `dijkstraSubTxProducedValue`), analogously to how `treasuryDonationTxBodyL` is included in `conwayProducedValue`. Concretely:

```haskell
dijkstraProducedValue pp isRegPoolId txBody =
  conwayProducedValue pp isRegPoolId txBody
    <+> inject (foldMap id . unDirectDeposits $ txBody ^. directDepositsTxBodyL)
    <> foldMap'
         (getProducedValue pp isRegPoolId . view bodyTxL)
         (txBody ^. subTransactionsTxBodyL)
```

Apply the same fix to `dijkstraSubTxProducedValue`. This ensures the transaction author must supply sufficient UTxO inputs to fund both the UTxO outputs and the direct deposits, preserving the total ADA supply invariant.

---

### Proof of Concept

1. Register a stake credential `cred` to obtain a valid `AccountAddress addr`.
2. Construct a Dijkstra-era transaction `tx` with:
   - One UTxO input sufficient to cover only the transaction fee.
   - One UTxO output returning change (inputs − fee).
   - `directDeposits = DirectDeposits (Map.singleton addr (Coin 45_000_000_000_000_000))`.
3. Submit `tx`. The PoV check evaluates:
   - `consumed = coin_of_input`
   - `produced = coin_of_output + fee`
   - These are equal; the check passes.
4. `applyDirectDeposits` credits `45_000_000_000_000_000` lovelace to `addr`.
5. Observe that `sumBalancesAccounts accounts` has increased by `45_000_000_000_000_000` lovelace while the UTxO pot decreased only by the fee — total ADA in the ledger has increased.

### Citations

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/TxBody.hs (L1319-1319)
```haskell
  directDepositsTxBodyL :: Lens' (TxBody l era) DirectDeposits
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

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs (L304-316)
```haskell
validateWrongNetworkInDirectDeposit ::
  DijkstraEraTxBody era =>
  Network ->
  TxBody t era ->
  Test (DijkstraUtxoPredFailure era)
validateWrongNetworkInDirectDeposit netId txb =
  failureOnNonEmptySet depositsWrongNetwork (WrongNetworkInDirectDeposit netId)
  where
    depositsWrongNetwork =
      Map.keysSet $
        Map.filterWithKey
          (\a _ -> aaNetworkId a /= netId)
          (unDirectDeposits $ txb ^. directDepositsTxBodyL)
```

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

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/UTxO.hs (L121-131)
```haskell
conwayProducedValue ::
  ( ConwayEraTxBody era
  , Value era ~ MaryValue
  ) =>
  PParams era ->
  (KeyHash StakePool -> Bool) ->
  TxBody TopTx era ->
  Value era
conwayProducedValue pp isStakePool txBody =
  getProducedMaryValue pp isStakePool txBody
    <+> inject (txBody ^. treasuryDonationTxBodyL)
```

**File:** eras/mary/impl/src/Cardano/Ledger/Mary/UTxO.hs (L88-96)
```haskell
getProducedMaryValue ::
  (MaryEraTxBody era, Value era ~ MaryValue) =>
  PParams era ->
  -- | Check whether a pool with a supplied PoolStakeId is already registered.
  (KeyHash StakePool -> Bool) ->
  TxBody TopTx era ->
  MaryValue
getProducedMaryValue pp isPoolRegistered txBody =
  shelleyProducedValue pp isPoolRegistered txBody <> burnedMultiAssets txBody
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/SubEntities.hs (L182-187)
```haskell
  let directDeposits = tx ^. bodyTxL . directDepositsTxBodyL
      accountsAfterSubCerts = certStateAfterSubCerts ^. certDStateL . accountsL
  failOnJust (directDepositsMissingAccounts directDeposits accountsAfterSubCerts) $
    injectFailure . SubDirectDepositsToMissingAccounts

  pure $ certStateAfterSubCerts & certDStateL . accountsL %~ applyDirectDeposits directDeposits
```
