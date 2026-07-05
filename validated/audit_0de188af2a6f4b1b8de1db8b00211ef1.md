### Title
Block-Level ExUnits Limit Bypassed by Sub-Transaction Redeemers in Dijkstra Era — (`File: eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs`, `eras/alonzo/impl/src/Cardano/Ledger/Alonzo/Tx.hs`, `eras/alonzo/impl/src/Cardano/Ledger/Alonzo/Rules/Bbody.hs`)

---

### Summary

In the Dijkstra era, a top-level transaction may embed an unbounded number of sub-transactions (each carrying its own Plutus redeemers). The per-block ExUnits ceiling (`maxBlockExUnits`) is enforced by summing `totExUnits` over every top-level transaction in the block. However, `totExUnits` only reads the redeemers of the single transaction it is given — it does not traverse sub-transactions. Sub-transaction redeemers are therefore invisible to the block-level accounting, allowing an attacker to cause a block to execute arbitrarily more Plutus computation than `maxBlockExUnits` permits.

---

### Finding Description

**`totExUnits` is blind to sub-transaction redeemers.**

`totExUnits` is defined as:

```haskell
totExUnits tx = foldMap snd $ tx ^. witsTxL . rdmrsTxWitsL . unRedeemersL
```

It folds only over the redeemers stored in the single `tx` argument's witness set. [1](#0-0) 

**The block-level check uses `totExUnits` over top-level transactions only.**

`validateExUnits` in the BBODY rule computes:

```haskell
let txTotal = foldMap totExUnits txs
```

where `txs` is the sequence of top-level transactions in the block. [2](#0-1) 

Because `totExUnits` does not recurse into sub-transactions, every redeemer declared inside a sub-transaction body is excluded from `txTotal`. The check `txTotal ≤ maxBlockExUnits` therefore only accounts for the top-level transaction's redeemers.

**The Dijkstra UTXO rule applies the per-transaction check only to the top-level `tx`.**

```haskell
  {- totExunits tx ≤ maxTxExUnits pp -}
  runTest $ Alonzo.validateExUnitsTooBigUTxO pp tx
``` [3](#0-2) 

Sub-transactions are processed through the `SUBLEDGERS` rule, which iterates over them with `foldM` and calls the `SUBLEDGER` → `LEDGER` → `UTXOW` → `UTXO` chain for each one. [4](#0-3) 

Each sub-transaction is individually checked against `maxTxExUnits`, but none of their ExUnits are ever aggregated into the block-level total.

**Sub-transactions are not count-limited in the CDDL.**

The CDDL schema defines:

```
sub_transactions = nonempty_oset<sub_transaction>
```

with no upper-bound on cardinality. [5](#0-4) 

The only practical bound is the overall transaction size (`maxTxSize`), which limits how many sub-transactions can be packed in, but each sub-transaction can independently carry redeemers up to `maxTxExUnits`.

---

### Impact Explanation

An attacker submits a single top-level transaction whose body contains `N` sub-transactions. The top-level transaction carries zero or minimal redeemers; each sub-transaction carries redeemers budgeted at `maxTxExUnits`. The block-level check sees only the top-level ExUnits (≈ 0), while the actual Plutus execution budget consumed by the block is `N × maxTxExUnits`. A block producer can include such a transaction alongside other transactions and still pass the `maxBlockExUnits` gate, causing honest validating nodes to execute far more Plutus computation per block than the protocol parameter was designed to allow.

This exceeds intended validation limits set by the `maxBlockExUnits` protocol parameter — a **Medium** impact under the allowed scope: *"Attacker-controlled transactions … exceed intended validation limits."*

If the excess computation causes some nodes to time out or stall while others complete validation, it could also escalate to a **High** impact: *"Deterministic disagreement between honest nodes from ledger rule evaluation."*

---

### Likelihood Explanation

The Dijkstra era is the first era to introduce sub-transactions. The `totExUnits` function predates sub-transactions and was never updated to recurse into them. Any unprivileged transaction sender can exploit this by constructing a valid top-level transaction with multiple sub-transactions, each containing a Plutus script and a redeemer. No special privileges, keys, or governance access are required. The transaction must be valid (pass all other checks), but that is achievable with legitimate UTxO inputs.

---

### Recommendation

1. **Extend `totExUnits` (or introduce a batch variant)** to sum ExUnits across the top-level transaction and all its sub-transactions:

   ```haskell
   batchTotExUnits :: (DijkstraEraTxBody era, AlonzoEraTxWits era) => Tx TopTx era -> ExUnits
   batchTotExUnits tx =
     totExUnits tx
       <> foldMap totExUnits (tx ^. bodyTxL . subTransactionsTxBodyL)
   ```

2. **Use `batchTotExUnits` in the Dijkstra UTXO rule** for the per-transaction ExUnits check, replacing the current call to `Alonzo.validateExUnitsTooBigUTxO pp tx`.

3. **Use `batchTotExUnits` in the Dijkstra BBODY rule** (or override `validateExUnits`) so that the block-level sum includes sub-transaction ExUnits.

---

### Proof of Concept

1. Obtain `N` UTxO entries locked by a Plutus script (e.g., `alwaysSucceeds`).
2. Construct `N` sub-transactions, each spending one UTxO and carrying a redeemer with `ExUnits = maxTxExUnits`.
3. Construct a top-level transaction embedding all `N` sub-transactions with zero top-level redeemers.
4. Submit the transaction. The UTXO rule checks `totExUnits topTx ≤ maxTxExUnits` (passes, ≈ 0) and each sub-transaction individually (each passes, = `maxTxExUnits`).
5. The BBODY rule checks `foldMap totExUnits [topTx] ≤ maxBlockExUnits` (passes, ≈ 0).
6. Actual Plutus execution budget consumed: `N × maxTxExUnits`, which can be made arbitrarily larger than `maxBlockExUnits` by increasing `N` (bounded only by `maxTxSize`).

### Citations

**File:** eras/alonzo/impl/src/Cardano/Ledger/Alonzo/Tx.hs (L390-394)
```haskell
totExUnits ::
  (EraTx era, AlonzoEraTxWits era) =>
  Tx l era ->
  ExUnits
totExUnits tx = foldMap snd $ tx ^. witsTxL . rdmrsTxWitsL . unRedeemersL
```

**File:** eras/alonzo/impl/src/Cardano/Ledger/Alonzo/Rules/Bbody.hs (L158-167)
```haskell
validateExUnits txs ppMax =
  let txTotal = foldMap totExUnits txs
   in pointWiseExUnits (<=) txTotal ppMax
        ?! injectFailure
          ( TooManyExUnits $
              Mismatch
                { mismatchSupplied = txTotal
                , mismatchExpected = ppMax
                }
          )
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs (L414-415)
```haskell
  {- totExunits tx ≤ maxTxExUnits pp -}
  runTest $ Alonzo.validateExUnitsTooBigUTxO pp tx
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/SubLedgers.hs (L128-135)
```haskell
dijkstraSubLedgersTransition = do
  TRC (env, ledgerState, subTxs) <- judgmentContext
  foldM
    ( \ls subTx ->
        trans @(EraRule "SUBLEDGER" era) $ TRC (env, ls, subTx)
    )
    ledgerState
    subTxs
```

**File:** eras/dijkstra/impl/cddl/data/dijkstra.cddl (L783-783)
```text
sub_transactions = nonempty_oset<sub_transaction>
```
