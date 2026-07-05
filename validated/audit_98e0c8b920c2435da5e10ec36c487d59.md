### Title
`directDeposits` in Dijkstra-era transaction bodies are applied to account balances without being included in the value-conservation check, enabling unbounded ADA creation — (`eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs`)

---

### Summary

The Dijkstra era introduces a new `directDeposits` field (CDDL key `25`) in both top-level and sub-transaction bodies. When a transaction is processed, the `ENTITIES`/`SUBENTITIES` rule calls `applyDirectDeposits`, which unconditionally adds the specified coin amounts to reward-account balances. However, neither the **consumed** nor the **produced** value calculation in the UTXO rule includes `directDeposits`. Because the value-conservation check (`consumed = produced`) passes without accounting for direct deposits, and because no other ledger pot is debited when `applyDirectDeposits` runs, an attacker can include arbitrarily large `directDeposits` in a valid transaction and have that ADA credited to their accounts with no corresponding deduction anywhere in the ledger state.

---

### Finding Description

**Step 1 – Direct deposits are applied unconditionally to account balances.**

In `dijkstraEntitiesTransition` (top-level transactions):

```haskell
let directDeposits = tx ^. bodyTxL . directDepositsTxBodyL
    accountsAfterCerts = certStateAfterCerts ^. certDStateL . accountsL
failOnJust (directDepositsMissingAccounts directDeposits accountsAfterCerts) $
  injectFailure . DirectDepositsToMissingAccounts
pure $ certStateAfterCerts & certDStateL . accountsL %~ applyDirectDeposits directDeposits
``` [1](#0-0) 

And identically in `dijkstraSubEntitiesTransition` (sub-transactions): [2](#0-1) 

`applyDirectDeposits` simply adds coin to account balances with no deduction from any other pot: [3](#0-2) 

**Step 2 – The produced-value calculation for sub-transactions omits `directDeposits`.**

`dijkstraSubTxProducedValue` computes only outputs + deposits + treasury donation + burned multi-assets:

```haskell
dijkstraSubTxProducedValue pp isRegPoolId txBody =
  sumAllValue (txBody ^. outputsTxBodyL)
    <> inject (getTotalDepositsTxBody pp isRegPoolId txBody <> txBody ^. treasuryDonationTxBodyL)
    <> burnedMultiAssets txBody
``` [4](#0-3) 

**Step 3 – The produced-value calculation for top-level transactions also omits `directDeposits`.**

`dijkstraProducedValue` delegates to `conwayProducedValue` for the top-level body (Conway has no `directDeposits`) and then folds over sub-transaction produced values using the same `dijkstraSubTxProducedValue`:

```haskell
dijkstraProducedValue pp isRegPoolId txBody =
  conwayProducedValue pp isRegPoolId txBody
    <> foldMap'
      (getProducedValue pp isRegPoolId . view bodyTxL)
      (txBody ^. subTransactionsTxBodyL)
``` [5](#0-4) 

Neither `conwayProducedValue` nor `dijkstraSubTxProducedValue` includes `directDeposits`.

**Step 4 – The consumed-value calculation also omits `directDeposits`.**

`getConsumedDijkstraValue` delegates to `getConsumedMaryValue` for each body, which computes only UTxO inputs + withdrawals + key/DRep refunds + minted tokens. `directDeposits` appear in neither side of the equation. [6](#0-5) 

**Step 5 – The UTXO rule enforces value conservation before ENTITIES runs.**

The UTXO transition rule calls `validateValueNotConservedUTxO` (line 381) and then transitions to `UTXOS` (line 420). The `ENTITIES`/`SUBENTITIES` rule is invoked later by the `LEDGER` rule. Because `directDeposits` are absent from both sides of the conservation check, the check passes for any transaction regardless of the `directDeposits` amount. [7](#0-6) 

**Step 6 – `updateUTxOStateNoFees` (used for sub-transactions) does not deduct `directDeposits` from any pot.**

The UTxO state update only adjusts `utxosDeposited` by the net of regular deposits minus refunds. No deduction for `directDeposits` occurs. [8](#0-7) 

---

### Impact Explanation

An attacker who controls a registered reward account can include an arbitrarily large `directDeposits` entry in a transaction body. The value-conservation check passes because `directDeposits` are absent from both `consumed` and `produced`. The `ENTITIES` rule then credits the full amount to the attacker's account with no corresponding debit anywhere in the ledger state. This constitutes **direct, unbounded creation of ADA** through an invalid ledger state transition.

This matches the allowed impact: **Critical. Direct loss, creation, or destruction of ADA or native assets through an invalid ledger state transition.**

---

### Likelihood Explanation

The attack requires only:
1. A registered reward account (trivially obtained via a `RegTxCert` certificate).
2. A syntactically valid transaction body with any non-empty UTxO input set (to satisfy `InputSetEmptyUTxO`) and a balanced `consumed = produced` equation (ignoring `directDeposits`).
3. Inclusion of `directDeposits` targeting the attacker's account.

No privileged access, governance majority, or key compromise is required. The attack is fully attacker-controlled and deterministic once the Dijkstra era is active.

---

### Recommendation

Include `directDeposits` in the **produced** value calculation for both top-level and sub-transactions. Concretely:

- In `dijkstraSubTxProducedValue`, add `inject (sumDirectDeposits (txBody ^. directDepositsTxBodyL))` to the result.
- In `dijkstraProducedValue` (or in the `conwayProducedValue` override for Dijkstra), add the top-level `directDeposits` amount to the produced value.

This mirrors how `treasuryDonationTxBodyL` and `getTotalDepositsTxBody` are already included on the produced side: ADA leaving the UTxO into any ledger pot must be accounted for.

---

### Proof of Concept

```
1. Register reward account A.
2. Construct a top-level Dijkstra transaction T:
     inputs  = { utxo_in }          -- any UTxO entry worth V lovelace
     outputs = [ addr → (V - fee) ] -- standard change output
     fee     = <minimum fee>
     directDeposits = { A → 1_000_000_000_000 }  -- 1 million ADA
3. Submit T.
4. Value conservation check:
     consumed = V  (UTxO input)
     produced = (V - fee) + fee = V  ✓  (directDeposits absent from both sides)
5. ENTITIES rule runs: applyDirectDeposits adds 1_000_000_000_000 lovelace to account A.
6. Withdraw from A: attacker receives 1 million ADA created from nothing.
```

### Citations

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

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs (L380-382)
```haskell
  {- consumed pp utxo₀ txb = produced pp certState txb -}
  runTest $ Shelley.validateValueNotConservedUTxO pp originalUtxo certState txBody

```

**File:** eras/shelley/impl/src/Cardano/Ledger/Shelley/Rules/Utxo.hs (L618-641)
```haskell
updateUTxOStateNoFees pp utxos txBody certState govState depositChangeEvent txUtxODiffEvent = do
  let UTxOState {utxosUtxo, utxosDeposited, utxosFees, utxosDonation} = utxos
      UTxO utxo = utxosUtxo
      !utxoAdd = txouts txBody -- These will be inserted into the UTxO
      {- utxoDel  = txins txb ◁ utxo -}
      !(utxoWithout, utxoDel) = extractKeys utxo (txBody ^. inputsTxBodyL)
      {- newUTxO = (txins txb ⋪ utxo) ∪ outs txb -}
      newUTxO = utxoWithout `Map.union` unUTxO utxoAdd
      deletedUTxO = UTxO utxoDel
      totalRefunds = certsTotalRefundsTxBody pp certState txBody
      totalDeposits = certsTotalDepositsTxBody pp certState txBody
      depositChange = totalDeposits <-> totalRefunds
  depositChangeEvent depositChange
  txUtxODiffEvent deletedUTxO utxoAdd
  pure $!
    UTxOState
      { utxosUtxo = UTxO newUTxO
      , utxosDeposited = utxosDeposited <> depositChange
      , utxosFees = utxosFees
      , utxosGovState = govState
      , utxosInstantStake =
          deleteInstantStake deletedUTxO (addInstantStake utxoAdd (utxos ^. instantStakeL))
      , utxosDonation = utxosDonation
      }
```
