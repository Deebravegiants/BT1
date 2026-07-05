### Title
`getMinFeeTxUtxo` for `DijkstraEra` reuses Conway's `getConwayMinFeeTxUtxo` which omits sub-transaction reference scripts from fee calculation - (`File: eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs`)

---

### Summary

The Dijkstra era introduces sub-transactions (`SubTx`), each of which can reference UTxO outputs containing reference scripts. The fee calculation for Dijkstra transactions is performed by `getConwayMinFeeTxUtxo`, which was designed for Conway (no sub-transactions) and only counts reference scripts in the top-level transaction body. A dedicated function `batchNonDistinctRefScriptsSize` exists that correctly aggregates reference script sizes across the top-level transaction and all sub-transactions, but it is **not** used in the fee calculation path. An attacker can therefore craft a Dijkstra transaction that loads large reference scripts exclusively through sub-transactions and pays a fee that is lower than the protocol intends.

---

### Finding Description

The `EraUTxO DijkstraEra` instance sets:

```haskell
getMinFeeTxUtxo = getConwayMinFeeTxUtxo
``` [1](#0-0) 

`getConwayMinFeeTxUtxo` is defined as:

```haskell
getConwayMinFeeTxUtxo pparams tx utxo =
  getMinFeeTx pparams tx $ txNonDistinctRefScriptsSize utxo tx
``` [2](#0-1) 

`txNonDistinctRefScriptsSize` only inspects the top-level transaction's inputs and reference inputs:

```haskell
txNonDistinctRefScriptsSize utxo tx = getSum $ foldMap (Sum . originalBytesSize . snd) refScripts
  where
    inputs = (tx ^. bodyTxL . referenceInputsTxBodyL) `Set.union` (tx ^. bodyTxL . inputsTxBodyL)
    refScripts = getReferenceScriptsNonDistinct utxo inputs
``` [3](#0-2) 

Dijkstra introduced `batchNonDistinctRefScriptsSize` specifically to aggregate reference script sizes across the top-level transaction **and all sub-transactions**:

```haskell
batchNonDistinctRefScriptsSize utxo tx =
  txNonDistinctRefScriptsSize utxo tx
    + getSum
      ( foldMap'
          (Sum . txNonDistinctRefScriptsSize utxo)
          (tx ^. bodyTxL . subTransactionsTxBodyL)
      )
``` [4](#0-3) 

`batchNonDistinctRefScriptsSize` is used in the Dijkstra LEDGER rule to enforce the per-transaction reference script size cap:

```haskell
validateAllRefScriptSize pp utxo tx =
  let totalRefScriptSize = batchNonDistinctRefScriptsSize utxo tx
      maxRefScriptSizePerTx = fromIntegral @Word32 @Int $ pp ^. ppMaxRefScriptSizePerTxG
   in failureUnless (totalRefScriptSize <= maxRefScriptSizePerTx) $ ...
``` [5](#0-4) 

The size-limit check uses the full batch size, but the **fee check** (`feesOK` → `getMinFeeTxUtxo`) uses only the top-level size. These two paths are inconsistent: the protocol enforces a size cap on the full batch but charges fees only for the top-level portion.

The `EraTxCert` typeclass signature for `getTotalRefundsTxCerts` accepts `pp`, `lookupStakingDeposit`, and `lookupDRepDeposit`, but the Dijkstra instance discards all three:

```haskell
getTotalRefundsTxCerts _ _ _ = dijkstraTotalRefundsTxCerts
``` [6](#0-5) 

This is the direct structural analog of the vyper bug: a function whose effective behavior changed (it no longer uses the parameters callers supply) while the callers (`conwayCertsTotalRefundsTxBody`, `getConsumedDijkstraValue`) continue to pass those parameters expecting them to influence the result. [7](#0-6) 

---

### Impact Explanation

**Medium.** An unprivileged transaction author can craft a Dijkstra top-level transaction whose sub-transactions reference large Plutus or native scripts stored in UTxO outputs. Because `getMinFeeTxUtxo` calls `txNonDistinctRefScriptsSize` (top-level only), the minimum fee computed by the ledger omits the sub-transaction reference script overhead. The attacker pays a fee that is lower than the protocol intends for the actual computational load imposed on validators. This modifies fees outside design parameters without requiring any privileged access.

---

### Likelihood Explanation

**Medium.** Dijkstra sub-transactions are a new feature. Any wallet or DApp that constructs Dijkstra transactions with reference scripts in sub-transactions will naturally trigger this path. A motivated attacker who understands the fee formula can deliberately exploit it to reduce costs. The code path is reachable on every Dijkstra transaction that uses sub-transaction reference scripts.

---

### Recommendation

Replace `getConwayMinFeeTxUtxo` with a Dijkstra-specific implementation that passes `batchNonDistinctRefScriptsSize utxo tx` (instead of `txNonDistinctRefScriptsSize utxo tx`) to `getMinFeeTx`:

```haskell
getDijkstraMinFeeTxUtxo pparams tx utxo =
  getMinFeeTx pparams tx $ batchNonDistinctRefScriptsSize utxo tx

instance EraUTxO DijkstraEra where
  ...
  getMinFeeTxUtxo = getDijkstraMinFeeTxUtxo
```

This aligns the fee calculation with the size-limit check already present in `validateAllRefScriptSize`, ensuring both paths use the same total reference script size.

---

### Proof of Concept

1. Deploy a UTxO output containing a large Plutus script as a reference script (e.g., 50 KiB).
2. Construct a Dijkstra `TopTx` with an empty top-level input set and a single `SubTx` whose `referenceInputsTxBodyL` points to the output from step 1.
3. Compute the minimum fee using `getMinFeeTxUtxo` (Conway path): it calls `txNonDistinctRefScriptsSize` on the top-level tx, which finds zero reference scripts, so the ref-script fee component is `Coin 0`.
4. Compute the fee using `batchNonDistinctRefScriptsSize`: it finds the 50 KiB script in the sub-transaction and produces a non-zero tiered fee.
5. Submit the transaction with the fee from step 3. The `feesOK` check passes because `minFee` (step 3) ≤ `theFee` (step 3). The `validateAllRefScriptSize` check also passes as long as 50 KiB ≤ `ppMaxRefScriptSizePerTx`.
6. The transaction is accepted with a fee that is lower than the protocol intends for the actual reference script load. [8](#0-7) [2](#0-1) [4](#0-3) [5](#0-4)

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

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/TxCert.hs (L285-285)
```haskell
  getTotalRefundsTxCerts _ _ _ = dijkstraTotalRefundsTxCerts
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/State/CertState.hs (L31-33)
```haskell
  certsTotalDepositsTxBody = conwayCertsTotalDepositsTxBody

  certsTotalRefundsTxBody = conwayCertsTotalRefundsTxBody
```
