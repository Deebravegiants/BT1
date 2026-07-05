### Title
Dijkstra Batch Transactions Omit Sub-Transaction Reference Script Sizes from Minimum Fee Calculation — (`File: eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs`)

---

### Summary

The Dijkstra era's `getMinFeeTxUtxo` implementation delegates to `getConwayMinFeeTxUtxo`, which calls `txNonDistinctRefScriptsSize` — a function that only measures reference scripts reachable from the **top-level** transaction's inputs. Sub-transactions embedded in a Dijkstra batch carry their own independent input sets and reference inputs, whose reference scripts are never counted. The codebase already contains the correct aggregating function `batchNonDistinctRefScriptsSize`, but it is never wired into the fee path. As a result, an attacker can embed arbitrarily large reference scripts exclusively through sub-transaction inputs, paying zero reference-script fee for them.

---

### Finding Description

The external report's vulnerability class is **fixed/hardcoded size used where a variable, context-dependent size is required**, causing the system to under-allocate or under-charge for the actual resource consumed. The Cardano analog is structurally identical: a fixed, context-insensitive size function (`txNonDistinctRefScriptsSize`, which only inspects the top-level transaction) is used where a context-sensitive one (`batchNonDistinctRefScriptsSize`, which also walks all sub-transactions) is required.

**Root cause — `getMinFeeTxUtxo` wired to the wrong size function:**

```haskell
-- eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs  line 141
instance EraUTxO DijkstraEra where
  ...
  getMinFeeTxUtxo = getConwayMinFeeTxUtxo   -- ← reuses Conway implementation unchanged
``` [1](#0-0) 

`getConwayMinFeeTxUtxo` passes only the top-level transaction's reference-script size to `getMinFeeTx`:

```haskell
-- eras/conway/impl/src/Cardano/Ledger/Conway/UTxO.hs  lines 174-175
getConwayMinFeeTxUtxo pparams tx utxo =
  getMinFeeTx pparams tx $ txNonDistinctRefScriptsSize utxo tx
``` [2](#0-1) 

`txNonDistinctRefScriptsSize` only unions the top-level body's `inputsTxBodyL` and `referenceInputsTxBodyL`:

```haskell
-- eras/conway/impl/src/Cardano/Ledger/Conway/UTxO.hs  lines 183-187
txNonDistinctRefScriptsSize utxo tx = getSum $ foldMap (Sum . originalBytesSize . snd) refScripts
  where
    inputs = (tx ^. bodyTxL . referenceInputsTxBodyL) `Set.union` (tx ^. bodyTxL . inputsTxBodyL)
    refScripts = getReferenceScriptsNonDistinct utxo inputs
``` [3](#0-2) 

Sub-transactions have their own `dstbrSpendInputs` and `dstbrReferenceInputs` fields, which are entirely invisible to this call.

The correct function already exists in the Dijkstra module but is **never called from the fee path**:

```haskell
-- eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs  lines 264-277
-- | Total size of reference scripts across a top-level transaction and all its subtransactions.
batchNonDistinctRefScriptsSize utxo tx =
  txNonDistinctRefScriptsSize utxo tx
    + getSum
      ( foldMap'
          (Sum . txNonDistinctRefScriptsSize utxo)
          (tx ^. bodyTxL . subTransactionsTxBodyL)
      )
``` [4](#0-3) 

The tiered reference-script fee (`tierRefScriptFee`) is therefore computed with `refScriptsSize = 0` for any batch whose reference scripts appear only in sub-transactions:

```haskell
-- eras/conway/impl/src/Cardano/Ledger/Conway/Tx.hs  lines 103-112
getConwayMinFeeTx pp tx refScriptsSize =
  alonzoMinFeeTx pp tx <+> refScriptsFee
  where
    refScriptCostPerByte = unboundRational (pp ^. ppMinFeeRefScriptCostPerByteL)
    refScriptsFee =
      tierRefScriptFee
        (unboundRational $ pp ^. ppRefScriptCostMultiplierG)
        (fromIntegral @Word32 @Int . unNonZero $ pp ^. ppRefScriptCostStrideG)
        refScriptCostPerByte
        refScriptsSize   -- ← zero when all ref scripts are in sub-txs
``` [5](#0-4) 

---

### Impact Explanation

The reference-script fee was introduced specifically to deter DDoS attacks where an adversary submits transactions that are cheap to include but expensive to deserialize and validate (see ADR-009). The Dijkstra era's nested-transaction model creates a new surface: an attacker can place large Plutus scripts as reference scripts reachable only through sub-transaction inputs, paying zero reference-script surcharge while still forcing every validating node to deserialize those scripts. This directly modifies the effective fee paid outside the design parameters of the protocol, matching the **Medium** allowed impact: *"Attacker-controlled transactions… modify fees… outside design parameters."* [6](#0-5) 

---

### Likelihood Explanation

Any unprivileged transaction author can construct a Dijkstra `TopTx` with one or more `SubTx` entries whose `referenceInputsTxBodyL` point to UTxO outputs carrying large Plutus scripts. No special privilege, key, or governance action is required. The attacker controls the transaction structure entirely and the ledger's fee check will accept the transaction as long as the top-level reference-script size is within limits.

---

### Recommendation

Override `getMinFeeTxUtxo` in the `EraUTxO DijkstraEra` instance to use `batchNonDistinctRefScriptsSize` instead of delegating to `getConwayMinFeeTxUtxo`:

```haskell
-- eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs
instance EraUTxO DijkstraEra where
  ...
  getMinFeeTxUtxo pp tx utxo =
    getMinFeeTx pp tx (batchNonDistinctRefScriptsSize utxo tx)
```

Additionally, audit whether `validateRefScriptSize` (the per-transaction size-limit check in the LEDGER rule) and `validateBodyRefScriptsSizeTooBig` (the per-block check in the BBODY rule) also need to be updated to use `batchNonDistinctRefScriptsSize` for Dijkstra, to ensure the hard caps on reference-script size are enforced across the full batch.

---

### Proof of Concept

1. Deploy a UTxO output containing a large Plutus V3 script (~100 KiB) as a reference script.
2. Construct a Dijkstra `TopTx` with an empty `inputsTxBodyL` / `referenceInputsTxBodyL` at the top level, but include a `SubTx` whose `dstbrReferenceInputs` points to the UTxO from step 1.
3. Compute the minimum fee using `getMinFeeTxUtxo`. Observe that `txNonDistinctRefScriptsSize` returns 0 (no top-level reference scripts), so `tierRefScriptFee` contributes 0 lovelace.
4. Submit the transaction. The ledger accepts it at the base linear fee, despite the node having to deserialize the 100 KiB script.
5. Compare with a Conway transaction referencing the same script at the top level: the Conway transaction would incur a substantial tiered reference-script surcharge, while the Dijkstra batch pays none. [7](#0-6) [4](#0-3) [2](#0-1)

### Citations

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs (L124-141)
```haskell
instance EraUTxO DijkstraEra where
  type ScriptsNeeded DijkstraEra = AlonzoScriptsNeeded DijkstraEra

  consumed = conwayConsumed

  getConsumedValue = getConsumedDijkstraValue

  getProducedValue = getProducedDijkstraValue

  getScriptsProvided = getDijkstraScriptsProvided

  getScriptsNeeded = getDijkstraScriptsNeeded

  getScriptsHashesNeeded = getAlonzoScriptsHashesNeeded

  getWitsVKeyNeeded _ = getConwayWitsVKeyNeeded

  getMinFeeTxUtxo = getConwayMinFeeTxUtxo
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs (L263-277)
```haskell
-- | Total size of reference scripts across a top-level transaction and all its subtransactions.
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

**File:** docs/adr/2024-08-14_009-refscripts-fee-change.md (L15-15)
```markdown
It was identified a while ago that there is an overhead associated with deserializing scripts, so much so that it would be possible to create a very large script that was fairly expensive to deserialize, but very cheap to execute. This opened up an attack vector when such a Plutus script would be used as a reference script. This problem was exacerbated by the fact that there was no real limit on the total size of reference scripts that could be used in a transaction, thus being limited only by the size of the transaction itself. Therefore this opened up Cardano to a DDoS attack where an attacker could submit many such transactions that would cost very little, but would be expensive for a `cardano-node` to validate.
```
