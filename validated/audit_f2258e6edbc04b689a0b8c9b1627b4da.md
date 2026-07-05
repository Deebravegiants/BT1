### Title
Sub-transaction Reference Scripts Excluded from Minimum Fee Calculation in Dijkstra Era — (`File: eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs`)

---

### Summary

The Dijkstra era introduces nested (sub-)transactions. The minimum fee calculation for a Dijkstra top-level transaction uses `getConwayMinFeeTxUtxo`, which only counts reference-script bytes from the **top-level** transaction's inputs. Reference scripts resolved from sub-transaction inputs are deserialized by every validating node but are **not charged for** in the fee. An unprivileged sender can therefore pay a fee that is lower than the protocol intends, undermining the tiered reference-script pricing that was introduced specifically to prevent DDoS via cheap-to-submit but expensive-to-validate transactions.

---

### Finding Description

The Dijkstra era's `EraUTxO` instance binds the minimum-fee helper to the Conway implementation:

```haskell
-- eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs  line 141
getMinFeeTxUtxo = getConwayMinFeeTxUtxo
```

`getConwayMinFeeTxUtxo` is defined as:

```haskell
-- eras/conway/impl/src/Cardano/Ledger/Conway/UTxO.hs  line 174-175
getConwayMinFeeTxUtxo pparams tx utxo =
  getMinFeeTx pparams tx $ txNonDistinctRefScriptsSize utxo tx
```

`txNonDistinctRefScriptsSize` only inspects the **top-level** transaction's `inputsTxBodyL` and `referenceInputsTxBodyL`:

```haskell
-- eras/conway/impl/src/Cardano/Ledger/Conway/UTxO.hs  line 183-187
txNonDistinctRefScriptsSize utxo tx = getSum $ foldMap (Sum . originalBytesSize . snd) refScripts
  where
    inputs = (tx ^. bodyTxL . referenceInputsTxBodyL) `Set.union` (tx ^. bodyTxL . inputsTxBodyL)
    refScripts = getReferenceScriptsNonDistinct utxo inputs
```

The Dijkstra codebase already contains a function that correctly aggregates reference-script sizes across the top-level transaction **and all sub-transactions**:

```haskell
-- eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs  line 264-277
batchNonDistinctRefScriptsSize utxo tx =
  txNonDistinctRefScriptsSize utxo tx
    + getSum
      ( foldMap'
          (Sum . txNonDistinctRefScriptsSize utxo)
          (tx ^. bodyTxL . subTransactionsTxBodyL)
      )
```

`batchNonDistinctRefScriptsSize` is **never called** from the fee-validation path. The fee check in `dijkstraUtxoTransition` is:

```haskell
-- eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs  line 372-373
{- minfee pp txTop utxo₀ ≤ txfee txb -}
runTest $ Shelley.validateFeeTooSmallUTxO pp tx originalUtxo
```

`validateFeeTooSmallUTxO` calls `getMinFeeTxUtxo`, which resolves to `getConwayMinFeeTxUtxo`, which calls `txNonDistinctRefScriptsSize` — not `batchNonDistinctRefScriptsSize`. Sub-transaction reference scripts are therefore invisible to the fee check.

Meanwhile, script provision for sub-transactions **does** resolve reference scripts from the UTxO:

```haskell
-- eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs  line 153-164
getDijkstraScriptsProvided utxo tx =
  withBothTxLevels tx
    ( \topTx ->
        ScriptsProvided $ Map.unions $
          unScriptsProvided (getBabbageScriptsProvided utxo topTx)
            : [ unScriptsProvided (getBabbageScriptsProvided utxo subTx)
              | subTx <- OMap.elems (topTx ^. bodyTxL . subTransactionsTxBodyL)
              ]
    )
    (getBabbageScriptsProvided utxo)
```

Every validating node must deserialize those sub-transaction reference scripts, but the sender pays nothing for them.

---

### Impact Explanation

This matches the **Medium** allowed impact: *"Attacker-controlled transactions … modify fees … outside design parameters."*

The tiered reference-script fee (`minFeeRefScriptCostPerByte`, multiplier `1.2`, stride `25 KiB`) was introduced after a real DDoS attack on Cardano mainnet (June 2024) to ensure that the cost of deserializing large reference scripts is borne by the submitter. By placing large reference scripts exclusively in sub-transaction inputs, an attacker can submit a batch transaction whose actual node-side deserialization cost is far higher than the fee paid, recreating the pre-Conway DDoS vector in the Dijkstra era.

---

### Likelihood Explanation

Any unprivileged transaction sender can craft a Dijkstra-era top-level transaction with sub-transactions that reference UTxO entries carrying large Plutus scripts. No special role, key, or governance majority is required. The attacker controls the sub-transaction inputs entirely. The fee check passes because it only inspects the top-level transaction's inputs. The attack is cheap to mount and repeatable.

---

### Recommendation

Replace `getConwayMinFeeTxUtxo` with a Dijkstra-specific implementation that uses `batchNonDistinctRefScriptsSize` instead of `txNonDistinctRefScriptsSize`:

```haskell
-- eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs
getDijkstraMinFeeTxUtxo ::
  ( EraTx era
  , DijkstraEraTxBody era
  , BabbageEraTxBody era
  ) =>
  PParams era -> Tx TopTx era -> UTxO era -> Coin
getDijkstraMinFeeTxUtxo pparams tx utxo =
  getMinFeeTx pparams tx $ batchNonDistinctRefScriptsSize utxo tx

instance EraUTxO DijkstraEra where
  ...
  getMinFeeTxUtxo = getDijkstraMinFeeTxUtxo   -- was: getConwayMinFeeTxUtxo
```

---

### Proof of Concept

1. Deploy a UTxO entry containing a large Plutus V4 script (e.g., 50 KiB) as a reference script.
2. Construct a Dijkstra top-level transaction `txTop` with:
   - A minimal top-level input (no reference scripts).
   - One sub-transaction `txSub` whose `dstbReferenceInputs` includes the 50 KiB reference-script UTxO entry.
3. Compute the fee using `getConwayMinFeeTxUtxo` (the current path): the 50 KiB reference script is **not counted**; the fee is the same as a plain transaction with no reference scripts.
4. Submit `txTop`. The ledger accepts it because `validateFeeTooSmallUTxO` calls `getMinFeeTxUtxo = getConwayMinFeeTxUtxo`, which only measures top-level reference scripts.
5. Every validating node must call `getDijkstraScriptsProvided`, which calls `getBabbageScriptsProvided utxo subTx`, deserializing the 50 KiB script — at zero marginal cost to the attacker.

The discrepancy between `batchNonDistinctRefScriptsSize` (which exists and correctly aggregates sub-transaction reference scripts) and `getMinFeeTxUtxo` (which does not use it) confirms the root cause is a missing Dijkstra-specific override of the fee calculation. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5)

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
