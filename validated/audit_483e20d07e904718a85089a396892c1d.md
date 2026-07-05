### Title
`directDeposits` Omitted from `produced` Value in Dijkstra UTxO Balance Equation — (`eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs`)

---

### Summary

The Dijkstra era introduces a `directDeposits` field in the transaction body that credits ADA directly to registered staking accounts. However, `directDeposits` is not included in either the `produced` or `consumed` side of the UTxO preservation-of-value equation. Because the balance check passes without accounting for direct deposits, an unprivileged transaction author can include an arbitrary `directDeposits` amount without supplying the corresponding ADA in UTxO inputs, causing the ledger to create ADA out of thin air.

---

### Finding Description

The Dijkstra era's `dijkstraProducedValue` function computes the "produced" side of the balance equation:

```haskell
dijkstraProducedValue pp isRegPoolId txBody =
  conwayProducedValue pp isRegPoolId txBody
    <> foldMap'
      (getProducedValue pp isRegPoolId . view bodyTxL)
      (txBody ^. subTransactionsTxBodyL)
```

`conwayProducedValue` is:

```haskell
conwayProducedValue pp isStakePool txBody =
  getProducedMaryValue pp isStakePool txBody
    <+> inject (txBody ^. treasuryDonationTxBodyL)
```

This covers: UTxO outputs + fee + certificate deposits + treasury donation. Notably, `treasuryDonation` **is** included (it is ADA leaving the UTxO and going to the treasury), but `directDeposits` — which is ADA leaving the UTxO and going to staking accounts — is **not** included.

The consumed side (`getConsumedDijkstraValue`) also does not include `directDeposits`:

```haskell
getConsumedDijkstraValue pp lookupStakingDeposit lookupDRepDeposit utxo txBody =
  withBothTxLevels txBody
    (\topTxBody -> txBodyConsumedValue topTxBody <> subTransactionsConsumedValue topTxBody)
    txBodyConsumedValue
  where
    txBodyConsumedValue = getConsumedMaryValue pp lookupStakingDeposit lookupDRepDeposit utxo
```

The Dijkstra UTxO transition enforces the balance check as:

```haskell
{- consumed pp utxo₀ txb = produced pp certState txb -}
runTest $ Shelley.validateValueNotConservedUTxO pp originalUtxo certState txBody
```

Since `directDeposits` appears in neither `consumed` nor `produced`, the balance check is satisfied regardless of the `directDeposits` amount.

Separately, the `ENTITIES` rule unconditionally applies direct deposits to accounts after validating only that target accounts are registered:

```haskell
let directDeposits = tx ^. bodyTxL . directDepositsTxBodyL
    accountsAfterCerts = certStateAfterCerts ^. certDStateL . accountsL
failOnJust (directDepositsMissingAccounts directDeposits accountsAfterCerts) $
  injectFailure . DirectDepositsToMissingAccounts
pure $ certStateAfterCerts & certDStateL . accountsL %~ applyDirectDeposits directDeposits
```

`applyDirectDeposits` adds the specified coin to each target account balance:

```haskell
applyDirectDeposits (DirectDeposits dd) =
  updateAccountBalances
    (\amount account -> addCompactCoin amount (account ^. balanceAccountStateL))
    dd
```

There is no check that the direct deposit amounts are covered by UTxO inputs.

---

### Impact Explanation

An attacker can construct a Dijkstra transaction where:

1. `directDeposits` targets one or more registered accounts with an arbitrary ADA amount X.
2. UTxO inputs cover only `outputs + fee + cert deposits + treasury donation` (i.e., the balance equation without X).
3. The `validateValueNotConservedUTxO` check passes because `directDeposits` is absent from both sides.
4. The `ENTITIES` rule applies the direct deposits, crediting X ADA to the target accounts.

Net result: X ADA is created in staking accounts with no corresponding deduction from any UTxO or pot. This is a direct violation of the preservation-of-value invariant and constitutes **unbounded ADA creation** by an unprivileged transaction author.

This matches the **Critical** impact class: *Direct creation of ADA through an invalid ledger state transition.*

---

### Likelihood Explanation

- No special privileges, governance majority, or key compromise is required.
- Any transaction author who can submit a Dijkstra-era transaction can exploit this.
- The exploit is deterministic and requires only constructing a well-formed transaction body with a non-zero `directDeposits` field and UTxO inputs that balance without it.
- The only prerequisite is that the target account address is registered, which the attacker can arrange by registering their own staking credential.

---

### Recommendation

Include `directDeposits` in the `produced` value calculation, mirroring the treatment of `treasuryDonation`. In `dijkstraProducedValue` (or a dedicated Dijkstra override of `conwayProducedValue`), add:

```haskell
<+> inject (fold . unDirectDeposits $ txBody ^. directDepositsTxBodyL)
```

This ensures that the ADA credited to accounts via direct deposits must be supplied by the transaction's UTxO inputs, preserving the total ADA supply.

---

### Proof of Concept

**Step 1.** Register a staking credential `cred` and obtain its `AccountAddress`.

**Step 2.** Construct a Dijkstra `TxBody` with:
- `inputs`: a UTxO entry worth exactly `fee + outputs_value` (no extra for direct deposits).
- `outputs`: change output returning the remainder.
- `directDeposits`: `{ accountAddress → 1_000_000_000 }` (1000 ADA).
- `fee`, `certs`, `treasuryDonation`: all zero/empty.

**Step 3.** The balance check evaluates:
- `consumed` = UTxO input value
- `produced` = outputs + fee = UTxO input value
- `consumed == produced` → **passes**.

**Step 4.** The `ENTITIES` rule sees `directDeposits` is non-empty, confirms `accountAddress` is registered, and calls `applyDirectDeposits`, adding 1,000,000,000 lovelace to the account balance.

**Step 5.** The account now holds 1000 ADA that was never deducted from any UTxO or pot. Total ADA in the system has increased by 1000 ADA. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

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

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs (L380-381)
```haskell
  {- consumed pp utxo₀ txb = produced pp certState txb -}
  runTest $ Shelley.validateValueNotConservedUTxO pp originalUtxo certState txBody
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
