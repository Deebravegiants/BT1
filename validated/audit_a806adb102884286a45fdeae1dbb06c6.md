### Title
Dijkstra Batch Transaction Minimum Fee Undercharges Reference Scripts in Sub-Transactions — (`eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs`)

---

### Summary

In the Dijkstra era, the `EraUTxO` instance for `DijkstraEra` delegates `getMinFeeTxUtxo` to `getConwayMinFeeTxUtxo`, which computes the reference-script fee component using only `txNonDistinctRefScriptsSize` — a function that inspects only the **top-level transaction's** inputs and reference inputs. Dijkstra batch transactions can embed sub-transactions, each of which may carry its own reference inputs pointing to large scripts. The correct batch-aware function, `batchNonDistinctRefScriptsSize`, exists and is used in the LEDGER rule's size-limit check, but it is **not** used in the minimum-fee enforcement path. The result is that the ledger enforces a minimum fee that systematically omits the reference-script cost contributed by sub-transactions, allowing an attacker to include large reference scripts in sub-transactions while paying only the fee for the top-level transaction's reference scripts.

---

### Finding Description

**Two parallel code paths compute reference-script size for a Dijkstra batch transaction, and they diverge.**

**Path 1 — fee enforcement (UTXO rule):**

`DijkstraEra`'s `EraUTxO` instance sets:

```haskell
getMinFeeTxUtxo = getConwayMinFeeTxUtxo
``` [1](#0-0) 

`getConwayMinFeeTxUtxo` computes the minimum fee as:

```haskell
getConwayMinFeeTxUtxo pparams tx utxo =
  getMinFeeTx pparams tx $ txNonDistinctRefScriptsSize utxo tx
``` [2](#0-1) 

`txNonDistinctRefScriptsSize` only unions the **top-level** transaction's `inputsTxBodyL` and `referenceInputsTxBodyL`:

```haskell
txNonDistinctRefScriptsSize utxo tx = getSum $ foldMap (Sum . originalBytesSize . snd) refScripts
  where
    inputs = (tx ^. bodyTxL . referenceInputsTxBodyL) `Set.union` (tx ^. bodyTxL . inputsTxBodyL)
    refScripts = getReferenceScriptsNonDistinct utxo inputs
``` [3](#0-2) 

This is the function called by `validateFeeTooSmallUTxO` in the Dijkstra UTXO transition rule:

```haskell
{- minfee pp txTop utxo₀ ≤ txfee txb -}
runTest $ Shelley.validateFeeTooSmallUTxO pp tx originalUtxo
``` [4](#0-3) 

**Path 2 — size-limit check (LEDGER rule):**

The LEDGER rule uses `batchNonDistinctRefScriptsSize`, which correctly aggregates reference scripts from the top-level transaction **and all sub-transactions**:

```haskell
batchNonDistinctRefScriptsSize utxo tx =
  txNonDistinctRefScriptsSize utxo tx
    + getSum
      ( foldMap'
          (Sum . txNonDistinctRefScriptsSize utxo)
          (tx ^. bodyTxL . subTransactionsTxBodyL)
      )
``` [5](#0-4) 

This function is used only in `validateAllRefScriptSize` to enforce the per-transaction size cap:

```haskell
validateAllRefScriptSize pp utxo tx =
  let totalRefScriptSize = batchNonDistinctRefScriptsSize utxo tx
      maxRefScriptSizePerTx = fromIntegral @Word32 @Int $ pp ^. ppMaxRefScriptSizePerTxG
   in failureUnless (totalRefScriptSize <= maxRefScriptSizePerTx) $
        DijkstraTxRefScriptsSizeTooBig ...
``` [6](#0-5) 

**The gap:** `batchNonDistinctRefScriptsSize` is never fed into the minimum-fee computation for `DijkstraEra`. The fee enforced by the UTXO rule is computed from the top-level transaction's reference scripts only, while the actual processing cost to nodes includes all sub-transaction reference scripts.

---

### Impact Explanation

The reference-script tiered fee (`tierRefScriptFee`) was introduced specifically to deter DDoS attacks where large scripts are cheap to include but expensive for nodes to deserialize and validate (see ADR-009). By omitting sub-transaction reference scripts from the minimum-fee calculation, the Dijkstra era reintroduces a variant of the same attack vector: an attacker can pack large reference scripts into sub-transactions and pay only the fee for the top-level transaction's reference scripts. The per-transaction size cap (`ppMaxRefScriptSizePerTxG`) bounds the maximum abuse per transaction, but within that cap the attacker pays a fee that is systematically lower than the design intends, modifying fees outside design parameters.

**Matched impact class:** Medium — Attacker-controlled transactions modify fees outside design parameters.

---

### Likelihood Explanation

Any unprivileged transaction sender can craft a Dijkstra batch transaction with sub-transactions that carry reference inputs pointing to large scripts. No special privilege, key, or governance action is required. The attack is directly reachable from the public mempool submission path. The Dijkstra era is currently experimental/pre-mainnet, which limits immediate real-world exposure, but the bug is present in the production code path and would be exploitable upon deployment.

---

### Recommendation

Replace the `getMinFeeTxUtxo` implementation for `DijkstraEra` with a version that uses `batchNonDistinctRefScriptsSize` instead of `txNonDistinctRefScriptsSize`:

```haskell
-- In eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs
getDijkstraMinFeeTxUtxo ::
  ( EraTx era
  , BabbageEraTxBody era
  , DijkstraEraTxBody era
  ) =>
  PParams era ->
  Tx TopTx era ->
  UTxO era ->
  Coin
getDijkstraMinFeeTxUtxo pparams tx utxo =
  getMinFeeTx pparams tx $ batchNonDistinctRefScriptsSize utxo tx

instance EraUTxO DijkstraEra where
  ...
  getMinFeeTxUtxo = getDijkstraMinFeeTxUtxo
```

This mirrors the pattern already used in `getConwayMinFeeTxUtxo` but substitutes the batch-aware size function. The `validateAllRefScriptSize` check in the LEDGER rule already uses `batchNonDistinctRefScriptsSize`, so aligning the fee path with it makes both checks consistent.

---

### Proof of Concept

The inconsistency can be demonstrated by constructing a Dijkstra batch transaction where the top-level transaction has no reference inputs but a sub-transaction references a large script. The fee check (`validateFeeTooSmallUTxO`) will pass with a fee computed from zero reference-script bytes, while `validateAllRefScriptSize` will correctly count the sub-transaction's reference scripts toward the size cap. Concretely:

1. Deploy a large Plutus script (e.g., 50 KiB) as a reference script in a UTxO output `O`.
2. Construct a Dijkstra top-level transaction `txTop` with no reference inputs and a sub-transaction `txSub` whose `referenceInputsTxBodyL` includes the input spending `O`.
3. Set `txTop`'s fee to the minimum computed by `getConwayMinFeeTxUtxo` (which sees 0 bytes of reference scripts).
4. Submit `txTop`. The UTXO rule's `validateFeeTooSmallUTxO` passes because it only sees the top-level transaction's reference scripts (0 bytes). The LEDGER rule's `validateAllRefScriptSize` sees 50 KiB but accepts it if it is below `ppMaxRefScriptSizePerTxG`.
5. The transaction is accepted with a fee that does not include the 50 KiB reference-script cost, which should have been charged via `tierRefScriptFee`.

### Citations

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs (L141-141)
```haskell
  getMinFeeTxUtxo = getConwayMinFeeTxUtxo
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs (L264-277)
```haskell
batchNonDistinctRefScriptsSize ::
  ( EraTx era
  , DijkstraEraTxBody era
  ) =>
  UTxO era ->
  Tx TopTx era ->
  Int
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

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Ledger.hs (L321-329)
```haskell
validateAllRefScriptSize pp utxo tx =
  let totalRefScriptSize = batchNonDistinctRefScriptsSize utxo tx
      maxRefScriptSizePerTx = fromIntegral @Word32 @Int $ pp ^. ppMaxRefScriptSizePerTxG
   in failureUnless (totalRefScriptSize <= maxRefScriptSizePerTx) $
        DijkstraTxRefScriptsSizeTooBig
          Mismatch
            { mismatchSupplied = totalRefScriptSize
            , mismatchExpected = maxRefScriptSizePerTx
            }
```
