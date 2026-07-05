### Title
Dijkstra Batch Transaction Minimum Fee Excludes Sub-Transaction Reference Scripts - (`File: eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs`)

---

### Summary

In the Dijkstra era, the minimum fee validation for a batch transaction (`TopTx` with sub-transactions) only accounts for reference scripts in the **top-level transaction**. Reference scripts attached to sub-transactions are silently excluded from the fee calculation, even though nodes must deserialize all of them. A separate size-limit check correctly aggregates the full batch, but the fee check does not. An attacker can craft a batch transaction with large reference scripts exclusively in sub-transactions, pay a fee that covers only the top-level transaction's reference script cost, and force every validating node to perform the full deserialization work at below-intended cost.

---

### Finding Description

The Dijkstra era introduces nested ("sub") transactions. A `TopTx` may carry an ordered set of `SubTx` entries in field 23 (`sub_transactions`). Sub-transactions have no fee field of their own; the single fee in the top-level body is supposed to cover the entire batch.

**Fee calculation path (broken for sub-transactions):**

`DijkstraEra`'s `EraUTxO` instance delegates minimum-fee computation to the Conway implementation:

```haskell
-- eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs, line 141
getMinFeeTxUtxo = getConwayMinFeeTxUtxo
``` [1](#0-0) 

`getConwayMinFeeTxUtxo` computes the reference-script surcharge using `txNonDistinctRefScriptsSize`:

```haskell
-- eras/conway/impl/src/Cardano/Ledger/Conway/UTxO.hs, lines 174-175
getConwayMinFeeTxUtxo pparams tx utxo =
  getMinFeeTx pparams tx $ txNonDistinctRefScriptsSize utxo tx
``` [2](#0-1) 

`txNonDistinctRefScriptsSize` only inspects the inputs and reference inputs of the **single transaction** passed to it — it has no knowledge of sub-transactions:

```haskell
-- eras/conway/impl/src/Cardano/Ledger/Conway/UTxO.hs, lines 183-187
txNonDistinctRefScriptsSize utxo tx = getSum $ foldMap (Sum . originalBytesSize . snd) refScripts
  where
    inputs = (tx ^. bodyTxL . referenceInputsTxBodyL) `Set.union` (tx ^. bodyTxL . inputsTxBodyL)
    refScripts = getReferenceScriptsNonDistinct utxo inputs
``` [3](#0-2) 

The UTXO transition rule enforces the fee check using this function:

```haskell
-- eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs, line 373
runTest $ Shelley.validateFeeTooSmallUTxO pp tx originalUtxo
``` [4](#0-3) 

**Correct batch-aware function exists but is not used for fees:**

The codebase already contains `batchNonDistinctRefScriptsSize`, which correctly sums reference script sizes across the top-level transaction **and all sub-transactions**:

```haskell
-- eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs, lines 271-277
batchNonDistinctRefScriptsSize utxo tx =
  txNonDistinctRefScriptsSize utxo tx
    + getSum
      ( foldMap'
          (Sum . txNonDistinctRefScriptsSize utxo)
          (tx ^. bodyTxL . subTransactionsTxBodyL)
      )
``` [5](#0-4) 

This function is used for the **size-limit** check in the LEDGER rule:

```haskell
-- eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Ledger.hs, lines 321-322
validateAllRefScriptSize pp utxo tx =
  let totalRefScriptSize = batchNonDistinctRefScriptsSize utxo tx
``` [6](#0-5) 

But it is **never used for fee calculation**. The minimum fee check and the size-limit check are therefore inconsistent: the size limit is enforced over the full batch, but the fee is computed only over the top-level transaction.

---

### Impact Explanation

The reference-script fee surcharge (`minFeeRefScriptCostPerByte`, tiered via `tierRefScriptFee`) was introduced specifically to make it expensive to force nodes to deserialize large scripts, preventing the DDoS attack that occurred on June 25, 2024. By placing large reference scripts exclusively in sub-transactions, an attacker bypasses this surcharge entirely while still forcing every validating node to deserialize those scripts. The attacker pays only the base `a + b*size` fee for the top-level transaction body, regardless of how many bytes of reference scripts are embedded in sub-transactions.

The total batch reference script size is bounded by `ppMaxRefScriptSizePerTxG` (enforced by `validateAllRefScriptSize`), so the attack is bounded — but within that bound the attacker can include up to `ppMaxRefScriptSizePerTxG` bytes of reference scripts in sub-transactions at zero reference-script surcharge. This allows transactions to be submitted at fees below the intended minimum, modifying fees outside design parameters.

**Impact class:** Medium — attacker-controlled transactions modify fees outside design parameters.

---

### Likelihood Explanation

Any unprivileged transaction author can craft a `TopTx` with sub-transactions. No special keys, governance majority, or privileged access is required. The Dijkstra era is the only era where sub-transactions exist, so this is a new attack surface introduced with that era. The attack is straightforward to execute: place reference inputs in sub-transaction bodies rather than the top-level body.

---

### Recommendation

Replace the call to `getConwayMinFeeTxUtxo` in `DijkstraEra`'s `EraUTxO` instance with a Dijkstra-specific implementation that uses `batchNonDistinctRefScriptsSize` instead of `txNonDistinctRefScriptsSize`:

```haskell
-- In eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs
getDijkstraMinFeeTxUtxo :: (EraTx era, BabbageEraTxBody era, DijkstraEraTxBody era) =>
  PParams era -> Tx TopTx era -> UTxO era -> Coin
getDijkstraMinFeeTxUtxo pparams tx utxo =
  getMinFeeTx pparams tx $ batchNonDistinctRefScriptsSize utxo tx

instance EraUTxO DijkstraEra where
  ...
  getMinFeeTxUtxo = getDijkstraMinFeeTxUtxo
```

This ensures the reference-script surcharge covers the full deserialization cost of the entire batch, consistent with how `validateAllRefScriptSize` already enforces the size limit.

---

### Proof of Concept

1. Produce N UTxO entries each carrying a large Plutus reference script (total size just below `ppMaxRefScriptSizePerTxG`).
2. Construct a `TopTx` with:
   - A minimal top-level body (no reference inputs, no reference scripts).
   - N sub-transactions, each referencing one of the large-script UTxOs via `referenceInputsTxBodyL`.
3. Compute the minimum fee using `getMinFeeTxUtxo` — it returns only the base `a + b*size` fee because `txNonDistinctRefScriptsSize` sees zero reference scripts in the top-level body.
4. Submit the transaction. `validateFeeTooSmallUTxO` passes (fee ≥ computed minimum). `validateAllRefScriptSize` passes (total batch size ≤ limit). The transaction is accepted.
5. Every validating node must deserialize all N large reference scripts from the sub-transactions, but the fee paid is far below what `tierRefScriptFee` would charge for the same total script bytes if they had been placed in the top-level transaction.

### Citations

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs (L141-141)
```haskell
  getMinFeeTxUtxo = getConwayMinFeeTxUtxo
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs (L271-277)
```haskell
batchNonDistinctRefScriptsSize utxo tx =
  txNonDistinctRefScriptsSize utxo tx
    + getSum
      ( foldMap'
          (Sum . txNonDistinctRefScriptsSize utxo)
          (tx ^. bodyTxL . subTransactionsTxBodyL)
      )
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/UTxO.hs (L174-175)
```haskell
getConwayMinFeeTxUtxo pparams tx utxo =
  getMinFeeTx pparams tx $ txNonDistinctRefScriptsSize utxo tx
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/UTxO.hs (L183-187)
```haskell
txNonDistinctRefScriptsSize :: (EraTx era, BabbageEraTxBody era) => UTxO era -> Tx l era -> Int
txNonDistinctRefScriptsSize utxo tx = getSum $ foldMap (Sum . originalBytesSize . snd) refScripts
  where
    inputs = (tx ^. bodyTxL . referenceInputsTxBodyL) `Set.union` (tx ^. bodyTxL . inputsTxBodyL)
    refScripts = getReferenceScriptsNonDistinct utxo inputs
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs (L372-373)
```haskell
  {- minfee pp txTop utxo₀ ≤ txfee txb -}
  runTest $ Shelley.validateFeeTooSmallUTxO pp tx originalUtxo
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Ledger.hs (L321-322)
```haskell
validateAllRefScriptSize pp utxo tx =
  let totalRefScriptSize = batchNonDistinctRefScriptsSize utxo tx
```
