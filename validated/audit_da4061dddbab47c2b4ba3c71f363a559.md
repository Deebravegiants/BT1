### Title
Dijkstra Era Minimum Fee Calculation Excludes Subtransaction Reference Scripts While Size Limit Covers the Full Batch - (`eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs`)

---

### Summary

In the Dijkstra era, the minimum fee calculation for a batch transaction only accounts for reference scripts in the **top-level transaction**, while the reference-script size enforcement (`validateAllRefScriptSize`) applies to the **combined size** of the top-level transaction and all subtransactions. An attacker can place large reference scripts exclusively in subtransactions, forcing nodes to deserialize and validate those scripts without paying the corresponding `minFeeRefScriptCostPerByte` fee.

---

### Finding Description

The Dijkstra era introduces nested ("sub") transactions. The minimum fee for a batch is computed via `getMinFeeTxUtxo`, which is set to `getConwayMinFeeTxUtxo`:

```haskell
-- eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs
getMinFeeTxUtxo = getConwayMinFeeTxUtxo
```

`getConwayMinFeeTxUtxo` calls `txNonDistinctRefScriptsSize`, which only inspects the **top-level transaction's** inputs and reference inputs:

```haskell
-- eras/conway/impl/src/Cardano/Ledger/Conway/UTxO.hs
getConwayMinFeeTxUtxo pparams tx utxo =
  getMinFeeTx pparams tx $ txNonDistinctRefScriptsSize utxo tx

txNonDistinctRefScriptsSize utxo tx = getSum $ foldMap (Sum . originalBytesSize . snd) refScripts
  where
    inputs = (tx ^. bodyTxL . referenceInputsTxBodyL) `Set.union` (tx ^. bodyTxL . inputsTxBodyL)
    refScripts = getReferenceScriptsNonDistinct utxo inputs
```

The resulting `refScriptsSize` is fed into `getConwayMinFeeTx` → `tierRefScriptFee`, which computes the exponential-growth fee for reference scripts. Subtransaction reference scripts are **never included** in this calculation.

Meanwhile, the Dijkstra LEDGER rule enforces the size limit using `batchNonDistinctRefScriptsSize`, which **does** aggregate reference scripts across the entire batch:

```haskell
-- eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs
batchNonDistinctRefScriptsSize utxo tx =
  txNonDistinctRefScriptsSize utxo tx
    + getSum (foldMap' (Sum . txNonDistinctRefScriptsSize utxo)
                       (tx ^. bodyTxL . subTransactionsTxBodyL))
```

```haskell
-- eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Ledger.hs
validateAllRefScriptSize pp utxo tx =
  let totalRefScriptSize = batchNonDistinctRefScriptsSize utxo tx
      maxRefScriptSizePerTx = fromIntegral @Word32 @Int $ pp ^. ppMaxRefScriptSizePerTxG
   in failureUnless (totalRefScriptSize <= maxRefScriptSizePerTx) $
        DijkstraTxRefScriptsSizeTooBig ...
```

The result is a direct asymmetry: the **size cap** is enforced on the full batch, but the **fee** is computed only on the top-level transaction. An attacker who places all reference scripts in subtransactions pays zero `tierRefScriptFee` for those scripts while still forcing every validating node to deserialize them.

---

### Impact Explanation

This falls under the **Medium** allowed impact:

> *Attacker-controlled transactions … modify fees … outside design parameters.*

The `minFeeRefScriptCostPerByte` / `tierRefScriptFee` mechanism was introduced specifically to price the deserialization cost of reference scripts and deter DDoS attacks (see ADR-009). By routing reference scripts through subtransactions, an attacker bypasses this pricing entirely. The attacker pays only the base `txFeePerByte` fee for the bytes of the subtransaction body, not the exponentially-growing `tierRefScriptFee`. This allows submitting transactions that are significantly more expensive to validate than the fee collected, undermining the economic deterrent against reference-script-based resource exhaustion.

---

### Likelihood Explanation

Any unprivileged transaction submitter in the Dijkstra era can exploit this. The Dijkstra era explicitly allows arbitrary ERC-20-style sub-transactions to be embedded in a top-level transaction. No special role, key, or governance action is required. The attacker simply constructs a top-level transaction with an empty reference-input set and embeds one or more subtransactions that each reference large scripts, staying within `maxRefScriptSizePerTx` in aggregate. The fee check in the UTXO rule will pass because `getConwayMinFeeTxUtxo` returns a fee that ignores the subtransaction scripts entirely.

---

### Recommendation

Override `getMinFeeTxUtxo` in the Dijkstra era to use `batchNonDistinctRefScriptsSize` instead of `txNonDistinctRefScriptsSize`, so that the fee calculation covers the full batch:

```haskell
-- eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs
getDijkstraMinFeeTxUtxo :: ... => PParams era -> Tx TopTx era -> UTxO era -> Coin
getDijkstraMinFeeTxUtxo pparams tx utxo =
  getMinFeeTx pparams tx $ batchNonDistinctRefScriptsSize utxo tx

instance EraUTxO DijkstraEra where
  ...
  getMinFeeTxUtxo = getDijkstraMinFeeTxUtxo
```

This mirrors the existing pattern where `validateAllRefScriptSize` already uses `batchNonDistinctRefScriptsSize` for the size cap, ensuring fee and size enforcement are symmetric across the full batch.

---

### Proof of Concept

1. Construct a Dijkstra top-level transaction with **no** reference inputs and **no** regular inputs that carry reference scripts.
2. Embed N subtransactions, each referencing a large Plutus script (e.g., 25 KiB each) via their `referenceInputs`. Keep the total below `maxRefScriptSizePerTx`.
3. Set the top-level fee to the minimum computed by `getConwayMinFeeTxUtxo` (which returns `alonzoMinFeeTx pp tx <+> tierRefScriptFee ... 0` = base fee only, since `txNonDistinctRefScriptsSize` returns 0 for the top-level tx).
4. Submit the transaction. The LEDGER rule's `validateAllRefScriptSize` passes (total batch size ≤ `maxRefScriptSizePerTx`). The UTXO rule's `FeeTooSmallUTxO` check also passes because the minimum fee was computed without the subtransaction scripts.
5. Every validating node must deserialize all N × 25 KiB of reference scripts, but the submitter paid only the base byte-size fee.

**Relevant code locations:** [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5)

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

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Ledger.hs (L313-329)
```haskell
validateAllRefScriptSize ::
  ( EraTx era
  , DijkstraEraTxBody era
  ) =>
  PParams era ->
  UTxO era ->
  Tx TopTx era ->
  Test (DijkstraLedgerPredFailure era)
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

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Tx.hs (L103-112)
```haskell
getConwayMinFeeTx pp tx refScriptsSize =
  alonzoMinFeeTx pp tx <+> refScriptsFee
  where
    refScriptCostPerByte = unboundRational (pp ^. ppMinFeeRefScriptCostPerByteL)
    refScriptsFee =
      tierRefScriptFee
        (unboundRational $ pp ^. ppRefScriptCostMultiplierG)
        (fromIntegral @Word32 @Int . unNonZero $ pp ^. ppRefScriptCostStrideG)
        refScriptCostPerByte
        refScriptsSize
```
