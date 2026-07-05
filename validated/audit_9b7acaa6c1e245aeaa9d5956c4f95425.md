I need to trace the exact code paths for both the LEDGER-level and BBODY-level reference script size checks in the Dijkstra era.

### Title
Block-Level Reference Script Size Limit Bypassed via Subtransaction Reference Scripts in Dijkstra Era — (`eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Bbody.hs`)

---

### Summary

The Dijkstra BBODY rule delegates its per-block reference script size check to `Conway.validateBodyRefScriptsSizeTooBig`, which internally calls `totalRefScriptSizeInBlock` → `txNonDistinctRefScriptsSize` per top-level transaction. `txNonDistinctRefScriptsSize` only inspects the top-level transaction body's `inputsTxBodyL` and `referenceInputsTxBodyL`; it never traverses into subtransactions. The Dijkstra LEDGER rule, by contrast, uses `validateAllRefScriptSize` → `batchNonDistinctRefScriptsSize`, which correctly aggregates the top-level tx plus all subtransactions. The result is a structural gap: a block producer can craft a block whose subtransactions collectively reference far more script bytes than `ppMaxRefScriptSizePerBlock` while the BBODY check reports a total of zero (or near-zero).

---

### Finding Description

**BBODY path (incomplete):**

`dijkstraBbodyTransition` at line 363 calls:
```
Conway.validateBodyRefScriptsSizeTooBig @era pp blockBody (ls ^. utxoL)
``` [1](#0-0) 

`validateBodyRefScriptsSizeTooBig` computes `totalRefScriptSizeInBlock protVer txs utxo`: [2](#0-1) 

`totalRefScriptSizeInBlock` folds over top-level txs and calls `txNonDistinctRefScriptsSize (UTxO accUtxo) tx` per tx: [3](#0-2) 

`txNonDistinctRefScriptsSize` only reads `tx ^. bodyTxL . referenceInputsTxBodyL` and `tx ^. bodyTxL . inputsTxBodyL` — the top-level body only, no subtransaction traversal: [4](#0-3) 

**LEDGER path (correct):**

`dijkstraLedgerTransition` calls `validateAllRefScriptSize pp originalUtxo tx`: [5](#0-4) 

`validateAllRefScriptSize` uses `batchNonDistinctRefScriptsSize`: [6](#0-5) 

`batchNonDistinctRefScriptsSize` correctly sums the top-level tx plus all subtransactions: [7](#0-6) 

**The gap:** `totalRefScriptSizeInBlock` was written for Conway, where there are no subtransactions. The Dijkstra BBODY rule reuses it unchanged, so subtransaction reference scripts are invisible to the block-level check.

---

### Impact Explanation

The per-block reference script size limit (`ppMaxRefScriptSizePerBlock`) was introduced specifically to cap the total deserialization work validators must perform per block (see ADR 009). By placing all reference scripts inside subtransactions and keeping the top-level tx bodies free of reference inputs, a block producer can submit a block whose true reference script byte total is `N × ppMaxRefScriptSizePerTxG` (one batch per top-level tx, each passing the per-tx LEDGER check) while the BBODY check measures zero. This exceeds the intended per-block resource limit, matching the Medium impact category: attacker-controlled blocks exceed intended validation limits.

---

### Likelihood Explanation

Exploitation requires being an active block producer (SPO). This is a legitimate, permissionless protocol role achievable through stake delegation. The Dijkstra era is pre-deployment, making this a pre-production finding. The construction is straightforward: craft top-level txs with empty `referenceInputsTxBodyL` but subtransactions that each reference large scripts up to `ppMaxRefScriptSizePerTxG`.

---

### Recommendation

Replace the call to `Conway.validateBodyRefScriptsSizeTooBig` in `dijkstraBbodyTransition` with a Dijkstra-specific block-level check that uses `batchNonDistinctRefScriptsSize` (or an equivalent block-level aggregation) for each top-level transaction, so that subtransaction reference scripts are included in the per-block total.

---

### Proof of Concept

1. Set `ppMaxRefScriptSizePerTxG = 200 KiB`, `ppMaxRefScriptSizePerBlock = 1 MiB`.
2. Produce 10 top-level transactions. Each top-level tx has:
   - Zero reference inputs in its own body (`referenceInputsTxBodyL = ∅`).
   - One subtransaction referencing scripts totalling ~200 KiB.
3. Each batch passes `validateAllRefScriptSize` (200 KiB ≤ 200 KiB).
4. `totalRefScriptSizeInBlock` reports 0 for each top-level tx (no top-level ref inputs), so the BBODY check passes (0 ≤ 1 MiB).
5. True total = 10 × 200 KiB = 2 MiB, which is 2× the intended block limit.
6. Assert: BBODY accepts the block; actual deserialization load is 2 MiB of reference scripts.

### Citations

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Bbody.hs (L363-363)
```haskell
  Conway.validateBodyRefScriptsSizeTooBig @era pp blockBody (ls ^. utxoL)
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Bbody.hs (L342-355)
```haskell
validateBodyRefScriptsSizeTooBig pp blockBody utxo =
  let protVer = pp ^. ppProtocolVersionL
      txs = blockBody ^. txSeqBlockBodyL
      totalSize = totalRefScriptSizeInBlock protVer txs utxo
      maxSize = fromIntegral @Word32 @Int $ pp ^. ppMaxRefScriptSizePerBlockG
   in totalSize
        <= maxSize
          ?! injectFailure
            ( BodyRefScriptsSizeTooBig $
                Mismatch
                  { mismatchSupplied = totalSize
                  , mismatchExpected = maxSize
                  }
            )
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Bbody.hs (L357-370)
```haskell
totalRefScriptSizeInBlock ::
  (AlonzoEraTx era, BabbageEraTxBody era) => ProtVer -> StrictSeq (Tx TopTx era) -> UTxO era -> Int
totalRefScriptSizeInBlock protVer txs (UTxO utxo)
  | pvMajor protVer <= natVersion @10 =
      getSum $ foldMap' (Monoid.Sum . txNonDistinctRefScriptsSize (UTxO utxo)) txs
  | otherwise =
      snd $ F.foldl' accum (utxo, 0) txs
  where
    accum (!accUtxo, !accSum) tx =
      let updatedUtxo = accUtxo `Map.union` unUTxO toAdd
          toAdd
            | IsValid True <- tx ^. isValidTxL = txouts $ tx ^. bodyTxL
            | otherwise = collOuts $ tx ^. bodyTxL
       in (updatedUtxo, accSum + txNonDistinctRefScriptsSize (UTxO accUtxo) tx)
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/UTxO.hs (L183-187)
```haskell
txNonDistinctRefScriptsSize :: (EraTx era, BabbageEraTxBody era) => UTxO era -> Tx l era -> Int
txNonDistinctRefScriptsSize utxo tx = getSum $ foldMap (Sum . originalBytesSize . snd) refScripts
  where
    inputs = (tx ^. bodyTxL . referenceInputsTxBodyL) `Set.union` (tx ^. bodyTxL . inputsTxBodyL)
    refScripts = getReferenceScriptsNonDistinct utxo inputs
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

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Ledger.hs (L391-392)
```haskell
        runTest $ Conway.validateTreasuryValue txBody (chainAccountState ^. casTreasuryL)
        runTest $ validateAllRefScriptSize pp originalUtxo tx
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
