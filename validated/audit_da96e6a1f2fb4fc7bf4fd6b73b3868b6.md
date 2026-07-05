### Title
Incomplete Reference Script Fee Accounting for Sub-Transactions in Dijkstra Era - (File: `eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs`)

---

### Summary

The Dijkstra era's minimum fee calculation reuses `getConwayMinFeeTxUtxo`, which only measures reference script sizes for the **top-level** transaction. Sub-transactions in a Dijkstra batch can carry their own reference inputs with scripts, but those deserialization costs are never added to the fee. A helper function `batchNonDistinctRefScriptsSize` that correctly aggregates reference script sizes across all sub-transactions exists in the same file but is never wired into the fee validation path.

---

### Finding Description

The `EraUTxO DijkstraEra` instance delegates fee calculation to the Conway implementation:

```haskell
getMinFeeTxUtxo = getConwayMinFeeTxUtxo
``` [1](#0-0) 

`getConwayMinFeeTxUtxo` computes the minimum fee as:

```haskell
getConwayMinFeeTxUtxo pparams tx utxo =
  getMinFeeTx pparams tx $ txNonDistinctRefScriptsSize utxo tx
``` [2](#0-1) 

`txNonDistinctRefScriptsSize` only inspects the top-level transaction's `inputsTxBodyL` and `referenceInputsTxBodyL`:

```haskell
txNonDistinctRefScriptsSize utxo tx = getSum $ foldMap (Sum . originalBytesSize . snd) refScripts
  where
    inputs = (tx ^. bodyTxL . referenceInputsTxBodyL) `Set.union` (tx ^. bodyTxL . inputsTxBodyL)
    refScripts = getReferenceScriptsNonDistinct utxo inputs
``` [3](#0-2) 

However, a Dijkstra top-level transaction body (`DijkstraTxBodyRaw TopTx`) embeds a map of sub-transactions, each of which is a full `Tx SubTx era` with its own `dstbrReferenceInputs`: [4](#0-3) 

Sub-transaction reference inputs can point to UTxO entries containing large Plutus scripts. Deserializing those scripts is a real per-node validation cost, but it is never charged.

The correct aggregation function already exists in the same file:

```haskell
batchNonDistinctRefScriptsSize utxo tx =
  txNonDistinctRefScriptsSize utxo tx
    + getSum
      ( foldMap'
          (Sum . txNonDistinctRefScriptsSize utxo)
          (tx ^. bodyTxL . subTransactionsTxBodyL)
      )
``` [5](#0-4) 

`batchNonDistinctRefScriptsSize` is exported but never called from the fee validation path. The Dijkstra UTXO rule enforces the minimum fee via:

```haskell
{- minfee pp txTop utxo₀ ≤ txfee txb -}
runTest $ Shelley.validateFeeTooSmallUTxO pp tx originalUtxo
``` [6](#0-5) 

`validateFeeTooSmallUTxO` calls `getMinFeeTxUtxo`, which resolves to `getConwayMinFeeTxUtxo` — the top-level-only path — so sub-transaction reference script costs are silently omitted from the enforced minimum fee.

---

### Impact Explanation

An unprivileged transaction sender can construct a Dijkstra batch transaction whose top-level body carries zero or minimal reference scripts while embedding sub-transactions that each reference large Plutus scripts via `dstbrReferenceInputs`. The fee check passes because only the top-level reference script size is measured. Every validating node must deserialize all sub-transaction reference scripts, but the submitter pays fees as if those scripts do not exist. This allows attacker-controlled transactions to **modify fees outside design parameters** — specifically, to pay a fee below the intended minimum for the actual validation work imposed on the network. This matches the Medium impact category: *attacker-controlled transactions modify fees outside design parameters*.

---

### Likelihood Explanation

The Dijkstra era is the newest era and sub-transactions are a novel feature. Any user who can submit a Dijkstra transaction (no privilege required) can exploit this. The exploit requires only knowledge of the fee formula and the ability to craft a transaction with sub-transactions referencing large scripts — both are straightforward for a technically capable attacker. The `batchNonDistinctRefScriptsSize` function's existence in the same file signals that the gap was anticipated but not yet connected to the enforcement path.

---

### Recommendation

Replace the Dijkstra `getMinFeeTxUtxo` binding with a Dijkstra-specific implementation that uses `batchNonDistinctRefScriptsSize` instead of `txNonDistinctRefScriptsSize`:

```haskell
getDijkstraMinFeeTxUtxo :: (EraTx era, DijkstraEraTxBody era, BabbageEraTxBody era)
  => PParams era -> Tx TopTx era -> UTxO era -> Coin
getDijkstraMinFeeTxUtxo pparams tx utxo =
  getMinFeeTx pparams tx $ batchNonDistinctRefScriptsSize utxo tx
```

Then in the `EraUTxO DijkstraEra` instance:

```haskell
getMinFeeTxUtxo = getDijkstraMinFeeTxUtxo
```

This ensures that reference script deserialization costs for all sub-transactions are included in the enforced minimum fee, consistent with the design intent evidenced by `batchNonDistinctRefScriptsSize`.

---

### Proof of Concept

1. Obtain a UTxO entry whose output contains a large Plutus script as a reference script (e.g., near the 200 KiB per-transaction limit).
2. Construct a Dijkstra top-level transaction with:
   - No reference inputs at the top level (zero reference script cost at the top level).
   - One or more sub-transactions, each with `dstbrReferenceInputs` pointing to the large-script UTxO entry.
3. Compute the minimum fee using `getMinFeeTxUtxo` (i.e., `getConwayMinFeeTxUtxo`): it returns a fee based solely on the top-level transaction size and zero reference script bytes.
4. Submit the transaction with that fee.
5. The `validateFeeTooSmallUTxO` check passes because `minFee ≤ txFee` holds under the incomplete calculation.
6. Every node validates the transaction by deserializing the large reference scripts in each sub-transaction — work that was not charged for.

The root cause is the assignment `getMinFeeTxUtxo = getConwayMinFeeTxUtxo` at line 141 of `eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs`, which ignores `batchNonDistinctRefScriptsSize` defined at lines 263–277 of the same file. [1](#0-0) [5](#0-4)

### Citations

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs (L141-141)
```haskell
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

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/TxBody.hs (L184-191)
```haskell
    , dtbrSubTransactions :: !(OMap TxId (Tx SubTx era))
    , dtbrDirectDeposits :: !DirectDeposits
    , dtbrAccountBalanceIntervals :: !(AccountBalanceIntervals era)
    } ->
    DijkstraTxBodyRaw TopTx era
  DijkstraSubTxBodyRaw ::
    { dstbrSpendInputs :: !(Set TxIn)
    , dstbrReferenceInputs :: !(Set TxIn)
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs (L372-373)
```haskell
  {- minfee pp txTop utxo₀ ≤ txfee txb -}
  runTest $ Shelley.validateFeeTooSmallUTxO pp tx originalUtxo
```
