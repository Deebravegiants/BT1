### Title
Per-Block Reference Script Size Limit Bypassed via Sub-Transaction Reference Inputs in Dijkstra Era - (File: `eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Bbody.hs`)

---

### Summary

In the Dijkstra era, the per-block reference script size limit (`ppMaxRefScriptSizePerBlockG`) is enforced by `validateBodyRefScriptsSizeTooBig`, which internally calls `totalRefScriptSizeInBlock` → `txNonDistinctRefScriptsSize`. This function only counts reference scripts referenced by the **top-level** transaction's inputs. However, Dijkstra introduces sub-transactions (`subTransactionsTxBodyL`) that can independently reference scripts from the UTxO. The per-transaction check correctly uses `batchNonDistinctRefScriptsSize` (which sums top-level + sub-transaction reference scripts), but the per-block check does not. An unprivileged transaction sender can craft top-level transactions whose sub-transactions collectively reference far more script bytes than `ppMaxRefScriptSizePerBlockG` allows, forcing nodes to deserialize an unbounded amount of reference script data per block.

---

### Finding Description

**Root cause — `totalRefScriptSizeInBlock` ignores sub-transaction inputs:**

`validateBodyRefScriptsSizeTooBig` is called in both Conway and Dijkstra BBODY rules: [1](#0-0) 

It delegates to Conway's implementation: [2](#0-1) 

Which calls `totalRefScriptSizeInBlock`: [3](#0-2) 

`totalRefScriptSizeInBlock` calls `txNonDistinctRefScriptsSize` per transaction. That function only inspects the top-level transaction body's `referenceInputsTxBodyL` and `inputsTxBodyL`: [4](#0-3) 

**Contrast with the per-transaction check — `batchNonDistinctRefScriptsSize` correctly includes sub-transactions:**

The Dijkstra LEDGER rule's per-transaction check uses `batchNonDistinctRefScriptsSize`: [5](#0-4) 

`batchNonDistinctRefScriptsSize` sums the top-level transaction AND all sub-transactions: [6](#0-5) 

**The asymmetry:** The per-transaction check (`validateAllRefScriptSize`) correctly counts sub-transaction reference scripts. The per-block check (`validateBodyRefScriptsSizeTooBig`) does not — it was written before sub-transactions existed and was never updated for Dijkstra.

---

### Impact Explanation

The per-block reference script size limit was introduced specifically to cap the amount of script deserialization work a block can impose on validating nodes (see ADR-9, which documents the June 2024 DDoS attack on Cardano mainnet): [7](#0-6) 

By placing large reference script inputs exclusively inside sub-transactions (with zero reference inputs at the top level), an attacker can submit a block where:

- Each top-level transaction contributes **0 bytes** to the per-block check (no top-level reference inputs).
- Each top-level transaction's sub-transactions contribute up to `ppMaxRefScriptSizePerTxG` bytes of reference script deserialization work (passing the per-transaction check).
- The block can contain many such transactions, collectively forcing nodes to deserialize a multiple of `ppMaxRefScriptSizePerBlockG` bytes of scripts — with no ledger-level rejection.

**Impact class:** Medium — attacker-controlled transactions exceed intended validation limits (`ppMaxRefScriptSizePerBlockG`), outside design parameters.

---

### Likelihood Explanation

- Dijkstra is the current development era; sub-transactions are a new feature.
- The attack requires no privileged access: any transaction sender can craft a top-level transaction with sub-transactions referencing large Plutus scripts already in the UTxO.
- The attacker only needs to pay fees for the top-level transaction; reference scripts are already deployed UTxO outputs.
- The per-transaction limit (`ppMaxRefScriptSizePerTxG`) still bounds each individual batch, but the per-block limit is fully bypassable.

---

### Recommendation

Update `totalRefScriptSizeInBlock` (or introduce a Dijkstra-specific override) to use `batchNonDistinctRefScriptsSize` instead of `txNonDistinctRefScriptsSize` when computing the per-block reference script total. Specifically, in `eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Bbody.hs`, the `accum` function inside `totalRefScriptSizeInBlock` should be replaced with a variant that also traverses `subTransactionsTxBodyL` for each top-level transaction, mirroring the logic already present in `batchNonDistinctRefScriptsSize`.

Alternatively, Dijkstra's BBODY rule should override `validateBodyRefScriptsSizeTooBig` with a Dijkstra-aware version that calls `batchNonDistinctRefScriptsSize` per transaction.

---

### Proof of Concept

1. Deploy N large Plutus V3 scripts as reference scripts in UTxO outputs (one-time setup, any address).
2. Construct a top-level Dijkstra transaction with:
   - **Zero** reference inputs at the top level (so `txNonDistinctRefScriptsSize` returns 0 for this tx).
   - K sub-transactions, each referencing M of the large scripts via `referenceInputsTxBodyL`, such that `K * M * scriptSize ≤ ppMaxRefScriptSizePerTxG` (passes `validateAllRefScriptSize`).
3. Pack B such top-level transactions into a single block, where `B * K * M * scriptSize >> ppMaxRefScriptSizePerBlockG`.
4. Submit the block. `validateBodyRefScriptsSizeTooBig` computes `totalRefScriptSizeInBlock` = 0 (no top-level reference inputs across all B transactions) and accepts the block.
5. Each validating node must deserialize `B * K * M * scriptSize` bytes of reference scripts — far exceeding the intended per-block cap — while the ledger rule reports no violation. [3](#0-2) [8](#0-7) [5](#0-4) [1](#0-0)

### Citations

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Bbody.hs (L361-363)
```haskell
  Alonzo.validateExUnits @era txs $ pp ^. ppMaxBlockExUnitsL

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

**File:** docs/adr/2024-08-14_009-refscripts-fee-change.md (L71-78)
```markdown
### Reference script size limit

In order to further increase the resilience to this sort of attacks we added hard limits on the total size of reference scripts that can be used per transaction and per block.

Hard caps that are currently hard coded, but will be turned into actual protocol parameters in the next era after Conway:

* Limit per transaction: `200KiB` (or `204800` bytes)
* Limit per block: `1MiB` (or `1048576` bytes)
```
