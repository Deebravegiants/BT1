Let me examine the relevant production code to trace this claim carefully.

I have now traced all the relevant code paths. Here is my analysis.

---

## Step 1 — `dijkstraTotalDepositsTxBody` does not include direct deposits [1](#0-0) 

```haskell
dijkstraTotalDepositsTxBody pp isPoolRegisted txBody =
  getTotalDepositsTxCerts pp isPoolRegisted (txBody ^. certsTxBodyL)
    <+> conwayProposalsDeposits pp txBody
```

This is the implementation of `getTotalDepositsTxBody` for `DijkstraEra`. It sums only **cert deposits** and **proposal deposits**. `dtbrDirectDeposits` is never touched.

## Step 2 — The UTxO balance equation uses this function [2](#0-1) 

```haskell
{- consumed pp utxo₀ txb = produced pp certState txb -}
runTest $ Shelley.validateValueNotConservedUTxO pp originalUtxo certState txBody
```

`getProducedDijkstraValue` calls `conwayProducedValue`, which calls `getTotalDepositsTxBody` — i.e., `dijkstraTotalDepositsTxBody`. Direct deposits are absent from the produced side. [3](#0-2) 

`getConsumedDijkstraValue` delegates to `getConsumedMaryValue` — direct deposits are absent from the consumed side too. [4](#0-3) 

## Step 3 — `applyDirectDeposits` unconditionally adds coin to account balances [5](#0-4) 

```haskell
applyDirectDeposits (DirectDeposits dd) =
  updateAccountBalances
    (\amount account -> addCompactCoin amount (account ^. balanceAccountStateL))
    dd
```

## Step 4 — ENTITIES applies direct deposits after CERTS, with no funding check [6](#0-5) 

```haskell
certStateAfterCerts <-
  trans @(EraRule "CERTS" era) $ TRC (certsEnv, certStateBeforeCerts, certificates)

let directDeposits = tx ^. bodyTxL . directDepositsTxBodyL
    accountsAfterCerts = certStateAfterCerts ^. certDStateL . accountsL
failOnJust (directDepositsMissingAccounts directDeposits accountsAfterCerts) $
  injectFailure . DirectDepositsToMissingAccounts

pure $ certStateAfterCerts & certDStateL . accountsL %~ applyDirectDeposits directDeposits
```

The only guard is `directDepositsMissingAccounts` — it checks that target accounts **exist**, not that the coin is funded. No amount is deducted from UTxO.

## Step 5 — The invariant break

The UTxO conservation equation is:

```
inputs + withdrawals + cert_refunds  =  outputs + fees + cert_deposits + proposal_deposits + treasury
```

`directDeposits` appears on **neither side**. A transaction can carry `dtbrDirectDeposits = {addr → X}` for any `X`, and the equation balances identically whether `X = 0` or `X = 1_000_000_000_000`. The `X` lovelace credited to account balances is sourced from nowhere in the UTxO ledger.

The scenario in the question (register C + direct-deposit to C in the same tx) is valid because CERTS runs before `directDepositsMissingAccounts` is checked, so the account exists by the time the guard fires. But the registration is a red herring — the funding gap exists for **any** already-registered account too.

---

### Title
Direct deposits not included in UTxO value-conservation equation, enabling unbounded ADA creation — (`eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/TxBody.hs`, `Rules/Entities.hs`)

### Summary
`dijkstraTotalDepositsTxBody` omits `dtbrDirectDeposits` from the produced-value sum. The UTxO balance check therefore does not require direct-deposit amounts to be funded by UTxO inputs. `applyDirectDeposits` credits the amounts to account balances unconditionally, creating ADA equal to the sum of all direct deposits in the transaction.

### Finding Description
`getTotalDepositsTxBody` for `DijkstraEra` is `dijkstraTotalDepositsTxBody`, which sums only cert deposits and proposal deposits. `getProducedDijkstraValue` (and therefore `Shelley.validateValueNotConservedUTxO`) never adds `sum(directDeposits)` to the produced side. `getConsumedDijkstraValue` delegates to `getConsumedMaryValue` and also omits direct deposits from the consumed side. The ENTITIES rule applies `applyDirectDeposits` after the UTxO check has already passed, with no separate funding verification.

### Impact Explanation
An unprivileged transaction author can include a `DirectDeposits` map of arbitrary size. The UTxO equation balances regardless of the map's total value. Each lovelace in the map is credited to account balances without being deducted from any UTxO output. This is direct, unbounded ADA creation — a Critical impact.

### Likelihood Explanation
The attack requires only a valid transaction with a registered target account (or one registered in the same transaction). No governance majority, privileged key, or external dependency is needed. The path is fully local and deterministic.

### Recommendation
Add `sum(unDirectDeposits (txBody ^. directDepositsTxBodyL))` to the produced side in `dijkstraTotalDepositsTxBody` (or equivalently in `getProducedDijkstraValue`), mirroring how cert deposits are handled. The same fix is needed for sub-transactions via `dijkstraSubTxProducedValue`.

### Proof of Concept
Construct a `DijkstraTxBody` with:
- `dtbSpendInputs` = {utxo containing 10 ADA}
- `dtbOutputs` = {addr → 9 ADA}
- `dtbTxfee` = 1 ADA
- `dtbDirectDeposits` = {registered_account → 1_000_000_000_000 lovelace}

Assert `validateValueNotConservedUTxO` passes (10 = 9 + 1). Assert `applyDirectDeposits` credits 1,000,000 ADA to `registered_account`. The 1,000,000 ADA is not present in any UTxO input — it is created ex nihilo.

### Citations

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/TxBody.hs (L1003-1007)
```haskell
dijkstraTotalDepositsTxBody ::
  ConwayEraTxBody era => PParams era -> (KeyHash StakePool -> Bool) -> TxBody l era -> Coin
dijkstraTotalDepositsTxBody pp isPoolRegisted txBody =
  getTotalDepositsTxCerts pp isPoolRegisted (txBody ^. certsTxBodyL)
    <+> conwayProposalsDeposits pp txBody
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs (L380-381)
```haskell
  {- consumed pp utxo₀ txb = produced pp certState txb -}
  runTest $ Shelley.validateValueNotConservedUTxO pp originalUtxo certState txBody
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs (L65-91)
```haskell
getConsumedDijkstraValue ::
  forall era l.
  ( DijkstraEraTxBody era
  , EraUTxO era
  , Value era ~ MaryValue
  , STxLevel l era ~ STxBothLevels l era
  ) =>
  PParams era ->
  (Credential Staking -> Maybe Coin) ->
  (Credential DRepRole -> Maybe Coin) ->
  UTxO era ->
  TxBody l era ->
  Value era
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

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Entities.hs (L208-216)
```haskell
  certStateAfterCerts <-
    trans @(EraRule "CERTS" era) $ TRC (certsEnv, certStateBeforeCerts, certificates)

  let directDeposits = tx ^. bodyTxL . directDepositsTxBodyL
      accountsAfterCerts = certStateAfterCerts ^. certDStateL . accountsL
  failOnJust (directDepositsMissingAccounts directDeposits accountsAfterCerts) $
    injectFailure . DirectDepositsToMissingAccounts

  pure $ certStateAfterCerts & certDStateL . accountsL %~ applyDirectDeposits directDeposits
```
