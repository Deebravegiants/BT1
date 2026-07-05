Now let me look at `conwayProducedValue` and `conwayConsumed` to confirm what's included in the value conservation equation.

The code evidence is conclusive. Here is the full analysis:

---

### Title
Direct Deposits Not Included in Value Conservation Check Allows Unbounded ADA Inflation — (`eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs`, `eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/TxBody.hs`)

### Summary

`dijkstraTotalDepositsTxBody` omits the sum of `dtbrDirectDeposits` from the `produced` side of the value conservation equation. The ENTITIES rule unconditionally adds those coins to account balances. An unprivileged sender can therefore include a non-empty `dtbrDirectDeposits` map, keep UTxO outputs at their full value (inputs − fee), pass `validateValueNotConservedUTxO`, and have N lovelace created in account balances with no corresponding UTxO debit — unbounded ADA inflation per transaction.

### Finding Description

**Step 1 — `dijkstraTotalDepositsTxBody` omits direct deposits** [1](#0-0) 

```haskell
dijkstraTotalDepositsTxBody pp isPoolRegisted txBody =
  getTotalDepositsTxCerts pp isPoolRegisted (txBody ^. certsTxBodyL)
    <+> conwayProposalsDeposits pp txBody
```

`dtbrDirectDeposits` is never summed here. This function is the `getTotalDepositsTxBody` implementation for `DijkstraEra`. [2](#0-1) 

**Step 2 — `getProducedDijkstraValue` delegates to `conwayProducedValue`, which uses `getTotalDepositsTxBody`** [3](#0-2) 

`dijkstraProducedValue` calls `conwayProducedValue`, which calls `getProducedMaryValue`, which calls `getTotalDepositsTxBody`. Because `getTotalDepositsTxBody = dijkstraTotalDepositsTxBody`, direct deposits are absent from `produced`. [4](#0-3) 

**Step 3 — `validateValueNotConservedUTxO` uses this incomplete `produced`** [5](#0-4) 

The check is `consumed == produced`. With direct deposits absent from `produced`, the equation is:

```
consumed  = UTxO inputs + withdrawals + cert refunds
produced  = outputs + fee + cert deposits + proposal deposits + treasury donation
            (NO direct deposits)
```

**Step 4 — ENTITIES rule unconditionally adds direct deposits to account balances** [6](#0-5) 

```haskell
let directDeposits = tx ^. bodyTxL . directDepositsTxBodyL
    accountsAfterCerts = certStateAfterCerts ^. certDStateL . accountsL
failOnJust (directDepositsMissingAccounts directDeposits accountsAfterCerts) $
  injectFailure . DirectDepositsToMissingAccounts
pure $ certStateAfterCerts & certDStateL . accountsL %~ applyDirectDeposits directDeposits
```

`applyDirectDeposits` adds each entry's coin to the matching account balance: [7](#0-6) 

This runs in the LEDGER rule **after** the UTXO rule has already passed.

### Impact Explanation

An attacker constructs a transaction:

| Field | Value |
|---|---|
| UTxO inputs | X lovelace |
| UTxO outputs | X − fee lovelace (full, not reduced) |
| fee | fee lovelace |
| `dtbrDirectDeposits` | `{addr → N lovelace}` |

Value conservation check:
- `consumed` = X
- `produced` = (X − fee) + fee = X
- **Check passes** ✓

ENTITIES rule then executes `applyDirectDeposits`, adding N lovelace to `addr`'s account balance.

**Net ledger state**: UTxO holds X − fee lovelace, account balance increased by N lovelace, fee pot increased by fee lovelace. Total ADA = X + N. **N lovelace created from nothing.**

N is bounded only by the `Coin` type (up to ~45 billion ADA). Any registered account address can be targeted. The attack is repeatable every transaction.

### Likelihood Explanation

- Requires no privilege, governance action, or key compromise.
- Requires only a valid Dijkstra-era transaction with a non-empty `dtbrDirectDeposits` map targeting any registered account.
- The only guard on `dtbrDirectDeposits` is `validateWrongNetworkInDirectDeposit` (network ID check) and `directDepositsMissingAccounts` (account must be registered) — neither touches value conservation. [8](#0-7) 

### Recommendation

Include the sum of `dtbrDirectDeposits` in the `produced` side of the value conservation equation. The simplest fix is to add it to `dijkstraTotalDepositsTxBody`:

```haskell
dijkstraTotalDepositsTxBody pp isPoolRegisted txBody =
  getTotalDepositsTxCerts pp isPoolRegisted (txBody ^. certsTxBodyL)
    <+> conwayProposalsDeposits pp txBody
    <+> foldMap id (unDirectDeposits (txBody ^. directDepositsTxBodyL))
```

Alternatively, override `getProducedDijkstraValue` to add the direct-deposit total directly. Either way, the invariant `consumed == produced` must account for every lovelace that moves into account balances via `applyDirectDeposits`.

### Proof of Concept

```
Given:
  utxo    = { txIn₀ → (addr_pay, 10_000_000 lovelace) }
  fee     = 200_000 lovelace
  account = registered account at addr_stk with balance 0

Construct DijkstraTxBody:
  dtbrSpendInputs      = { txIn₀ }
  dtbrOutputs          = [ (addr_pay, 9_800_000 lovelace) ]   -- full: 10M - fee
  dtbrFee              = 200_000
  dtbrDirectDeposits   = { addr_stk → 5_000_000 lovelace }    -- N = 5 ADA

validateValueNotConservedUTxO:
  consumed = 10_000_000
  produced = 9_800_000 + 200_000 = 10_000_000
  → PASSES

ENTITIES applyDirectDeposits:
  account(addr_stk).balance += 5_000_000

Final ledger:
  UTxO total   = 9_800_000
  account bal  = 5_000_000
  fee pot      += 200_000
  Total ADA    = 15_000_000  (was 10_000_000)
  Inflation    = +5_000_000 lovelace
```

### Citations

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/TxBody.hs (L975-975)
```haskell
  getTotalDepositsTxBody = dijkstraTotalDepositsTxBody
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/TxBody.hs (L1003-1007)
```haskell
dijkstraTotalDepositsTxBody ::
  ConwayEraTxBody era => PParams era -> (KeyHash StakePool -> Bool) -> TxBody l era -> Coin
dijkstraTotalDepositsTxBody pp isPoolRegisted txBody =
  getTotalDepositsTxCerts pp isPoolRegisted (txBody ^. certsTxBodyL)
    <+> conwayProposalsDeposits pp txBody
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs (L102-106)
```haskell
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

**File:** eras/shelley/impl/src/Cardano/Ledger/Shelley/Rules/Utxo.hs (L513-518)
```haskell
validateValueNotConservedUTxO pp utxo certState txBody =
  failureUnless (consumedValue == producedValue) $
    ValueNotConservedUTxO Mismatch {mismatchSupplied = consumedValue, mismatchExpected = producedValue}
  where
    consumedValue = consumed pp certState utxo txBody
    producedValue = produced pp certState txBody
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

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs (L405-406)
```haskell
  {- direct deposit network IDs -}
  runTestOnSignal $ validateWrongNetworkInDirectDeposit netId txBody
```
