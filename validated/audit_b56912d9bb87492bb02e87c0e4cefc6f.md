### Title
Dijkstra Sub-Transaction Reference Script Fees Not Charged in `getMinFeeTxUtxo` - (File: `eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs`)

### Summary

The Dijkstra era introduces sub-transactions embedded inside a top-level transaction. During validation, reference scripts from sub-transaction inputs are deserialized and loaded. However, the minimum-fee calculation for the Dijkstra era reuses `getConwayMinFeeTxUtxo`, which only measures reference-script size for the top-level transaction's inputs. A helper function `batchNonDistinctRefScriptsSize` that correctly aggregates reference-script sizes across all sub-transactions is defined in the same file but is never wired into the fee calculation. An unprivileged sender can therefore craft a batch transaction whose sub-transactions reference large scripts stored in UTxO entries, forcing validators to deserialize those scripts without paying the corresponding `minFeeRefScriptCostPerByte`-based fee.

### Finding Description

The Dijkstra era's `EraUTxO` instance delegates minimum-fee computation to the Conway implementation:

```haskell
-- eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs, line 141
getMinFeeTxUtxo = getConwayMinFeeTxUtxo
```

`getConwayMinFeeTxUtxo` (Conway UTxO.hs lines 166–175) calls `txNonDistinctRefScriptsSize`, which only inspects the top-level transaction's `inputsTxBodyL` and `referenceInputsTxBodyL`:

```haskell
-- eras/conway/impl/src/Cardano/Ledger/Conway/UTxO.hs, lines 183-187
txNonDistinctRefScriptsSize utxo tx = getSum $ foldMap (Sum . originalBytesSize . snd) refScripts
  where
    inputs = (tx ^. bodyTxL . referenceInputsTxBodyL) `Set.union` (tx ^. bodyTxL . inputsTxBodyL)
    refScripts = getReferenceScriptsNonDistinct utxo inputs
```

Sub-transactions are stored in `dtbrSubTransactions :: !(OMap TxId (Tx SubTx era))` inside the top-level body. Each sub-transaction has its own `dstbrReferenceInputs` and `dstbrSpendInputs` fields that may point to UTxO entries carrying reference scripts. These scripts are actively loaded during validation by `getDijkstraScriptsProvided`:

```haskell
-- eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs, lines 153-164
getDijkstraScriptsProvided utxo tx =
  withBothTxLevels tx
    ( \topTx ->
        ScriptsProvided $ Map.unions $
          unScriptsProvided (getBabbageScriptsProvided utxo topTx)
            : [ unScriptsProvided (getBabbageScriptsProvided utxo subTx)
              | subTx <- OMap.elems (topTx ^. bodyTxL . subTransactionsTxBodyL) ]
    )
    (getBabbageScriptsProvided utxo)
```

The Dijkstra module already defines the correct aggregation function:

```haskell
-- eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs, lines 264-277
batchNonDistinctRefScriptsSize utxo tx =
  txNonDistinctRefScriptsSize utxo tx
    + getSum ( foldMap' (Sum . txNonDistinctRefScriptsSize utxo)
                        (tx ^. bodyTxL . subTransactionsTxBodyL) )
```

`batchNonDistinctRefScriptsSize` is exported but never passed to `getMinFeeTx`. The fee calculation therefore ignores all reference-script bytes that belong to sub-transactions.

### Impact Explanation

The `minFeeRefScriptCostPerByte` / `tierRefScriptFee` mechanism was introduced specifically to compensate validators for the cost of deserializing reference scripts (see ADR 009 and the June 2024 DDoS incident). By embedding sub-transactions that each carry reference inputs pointing to large scripts, an attacker pays only the flat `txFeePerByte × txSize` component for those scripts (which covers their serialized bytes inside the transaction body) but pays zero of the exponentially-tiered reference-script fee that the protocol intends to charge. This allows the attacker to force validators to deserialize an amount of reference-script data whose cost is not reflected in the fee, modifying the effective fee outside the design parameters of the protocol. This matches the allowed impact: **Medium — attacker-controlled transactions modify fees outside design parameters**.

### Likelihood Explanation

The Dijkstra era is the newest era and sub-transactions are a novel feature. The existence of `batchNonDistinctRefScriptsSize` in the same file as the fee instance, combined with the fact that it is never called from `getMinFeeTxUtxo`, strongly suggests an oversight rather than a deliberate design choice. Any unprivileged user who can submit a Dijkstra-era transaction can exploit this by constructing sub-transactions with reference inputs pointing to UTxO entries that hold large Plutus scripts. No special privilege, key, or governance majority is required.

### Recommendation

Override `getMinFeeTxUtxo` in the `EraUTxO DijkstraEra` instance to use `batchNonDistinctRefScriptsSize` instead of delegating to `getConwayMinFeeTxUtxo`:

```haskell
getMinFeeTxUtxo pparams tx utxo =
  getMinFeeTx pparams tx (batchNonDistinctRefScriptsSize utxo tx)
```

Additionally, verify that the `maxRefScriptSizePerTx` and `maxRefScriptSizePerBlock` limit checks in the Dijkstra UTxO rule also use `batchNonDistinctRefScriptsSize` (not `txNonDistinctRefScriptsSize`) so that the cap and the fee are computed over the same set of scripts.

### Proof of Concept

1. Publish several large Plutus reference scripts to UTxO entries (e.g., scripts near the per-entry size limit).
2. Construct a Dijkstra top-level transaction with N sub-transactions, each containing a `referenceInputs` set pointing to those UTxO entries.
3. The top-level transaction body carries no reference inputs of its own, so `txNonDistinctRefScriptsSize` returns 0 for the top-level tx.
4. `getMinFeeTxUtxo` therefore charges only `txFeePerByte × txSize` (covering the serialized sub-transaction bodies) and zero reference-script fee.
5. During validation, `getDijkstraScriptsProvided` iterates all sub-transactions and calls `getBabbageScriptsProvided` for each, deserializing every referenced script from storage.
6. The validator bears the full deserialization cost; the sender pays none of the tiered `tierRefScriptFee` that the protocol intends to charge for this work.

**Root cause files:** [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs (L141-141)
```haskell
  getMinFeeTxUtxo = getConwayMinFeeTxUtxo
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs (L153-164)
```haskell
getDijkstraScriptsProvided utxo tx =
  withBothTxLevels
    tx
    ( \topTx ->
        ScriptsProvided $
          Map.unions $
            unScriptsProvided (getBabbageScriptsProvided utxo topTx)
              : [ unScriptsProvided (getBabbageScriptsProvided utxo subTx)
                | subTx <- OMap.elems (topTx ^. bodyTxL . subTransactionsTxBodyL)
                ]
    )
    (getBabbageScriptsProvided utxo)
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

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/UTxO.hs (L166-175)
```haskell
getConwayMinFeeTxUtxo ::
  ( EraTx era
  , BabbageEraTxBody era
  ) =>
  PParams era ->
  Tx l era ->
  UTxO era ->
  Coin
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
