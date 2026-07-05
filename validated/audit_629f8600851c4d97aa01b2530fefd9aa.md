### Title
Sub-transaction ExUnits excluded from per-transaction and per-block resource-limit checks, enabling fee and execution-budget bypass — (`eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs`)

---

### Summary

In the Dijkstra era, the `validateExUnitsTooBigUTxO` check and the block-level `validateExUnits` check both delegate to `totExUnits`, which sums only the **top-level transaction's** redeemer ExUnits. Sub-transactions embedded in a Dijkstra top-level transaction carry their own redeemers and scripts, but their ExUnits are invisible to every resource-limit and fee-calculation path that uses `totExUnits`. An unprivileged submitter can therefore craft a top-level transaction whose top-level ExUnits are zero (or minimal) while packing arbitrarily many sub-transactions, each with scripts budgeted up to `maxTxExUnits`, bypassing both the per-transaction cap and the per-block cap, and paying no script-execution fee for the sub-transaction scripts.

---

### Finding Description

**Root cause — `totExUnits` is blind to sub-transaction redeemers**

`totExUnits` is defined in `eras/alonzo/impl/src/Cardano/Ledger/Alonzo/Tx.hs`:

```haskell
totExUnits tx = foldMap snd $ tx ^. witsTxL . rdmrsTxWitsL . unRedeemersL
```

It folds only over `witsTxL`, the top-level transaction's witness set. [1](#0-0) 

Sub-transactions in the Dijkstra era are stored in `subTransactionsTxBodyL` and each carries its own `witsTxL` with its own `rdmrsTxWitsL`. These are never visited by `totExUnits`.

**Per-transaction ExUnits check misses sub-transactions**

The Dijkstra UTXO transition rule calls the Alonzo validator unchanged:

```haskell
{- totExunits tx ≤ maxTxExUnits pp -}
runTest $ Alonzo.validateExUnitsTooBigUTxO pp tx
``` [2](#0-1) 

`Alonzo.validateExUnitsTooBigUTxO` computes `totalExUnits = totExUnits tx`, which is the top-level ExUnits only. [3](#0-2) 

**Per-block ExUnits check misses sub-transactions**

The block-body rule sums `totExUnits` across all top-level transactions:

```haskell
validateExUnits txs ppMax =
  let txTotal = foldMap totExUnits txs
   in pointWiseExUnits (<=) txTotal ppMax ...
``` [4](#0-3) 

Sub-transaction ExUnits are again absent from `txTotal`.

**Fee calculation misses sub-transaction ExUnits**

`minfee` includes `txscriptfee (prices pp) (totExUnits tx)`:

```
minfee pp tx = a·txSize tx + b + txscriptfee (prices pp) (totExunits tx)
``` [5](#0-4) 

Because `totExUnits` ignores sub-transaction redeemers, the script-execution fee for sub-transaction scripts is zero regardless of how many ExUnits those scripts declare.

**Contrast with reference-script size — the asymmetry**

The Dijkstra era correctly aggregates reference-script sizes across sub-transactions via `batchNonDistinctRefScriptsSize`:

```haskell
batchNonDistinctRefScriptsSize utxo tx =
  txNonDistinctRefScriptsSize utxo tx
    + getSum (foldMap' (Sum . txNonDistinctRefScriptsSize utxo)
                       (tx ^. bodyTxL . subTransactionsTxBodyL))
``` [6](#0-5) 

The analogous aggregation is absent for ExUnits.

**Sub-transactions can carry redeemers**

`validateBatchCollateral` explicitly checks whether *any* sub-transaction has redeemers:

```haskell
hasAnyRedeemers t =
  hasRedeemers t || any hasRedeemers (t ^. bodyTxL . subTransactionsTxBodyL)
hasRedeemers = not . null . (^. witsTxL . rdmrsTxWitsL . unRedeemersL)
``` [7](#0-6) 

This confirms sub-transactions are expected to carry redeemers and have their scripts executed, yet their ExUnits are never counted against any limit.

---

### Impact Explanation

**Allowed impact matched: Medium — attacker-controlled transactions exceed intended validation limits and modify fees outside design parameters.**

1. **Execution-budget bypass**: A single top-level transaction with `k` sub-transactions, each declaring `maxTxExUnits` of ExUnits, causes the node to execute scripts totalling `k × maxTxExUnits`. The per-transaction cap is bypassed entirely. A block containing `n` such transactions causes `n × k × maxTxExUnits` of script execution, bypassing `maxBlockExUnits`. This forces validators to spend unbounded CPU/memory on script evaluation, degrading throughput and potentially causing honest nodes to time out on block validation.

2. **Fee manipulation**: Sub-transaction script fees are not included in `minfee`, so the submitter pays zero script-execution fee for sub-transaction scripts. This modifies the effective fee outside the design parameters established by `prices` and `maxTxExUnits`.

---

### Likelihood Explanation

The Dijkstra era is the newest era and introduces sub-transactions as a novel feature. Any DApp developer or adversary who reads the specification and notices that sub-transactions accept redeemers can exploit this without any privileged access. The attack requires only the ability to submit a valid top-level transaction — an unprivileged operation. The cost to the attacker is the base transaction fee (no script-execution fee for sub-transactions), making repeated attacks cheap.

---

### Recommendation

1. **Aggregate sub-transaction ExUnits in `totExUnits`**: Override or extend `totExUnits` for the Dijkstra era to recursively sum ExUnits from all sub-transactions, mirroring the pattern already used in `batchNonDistinctRefScriptsSize`.

2. **Apply the aggregated total to all three enforcement points**:
   - `validateExUnitsTooBigUTxO` in the Dijkstra UTXO rule
   - `validateExUnits` in the Dijkstra/Conway BBODY rule
   - `minfee` / `txscriptfee` in the minimum-fee calculation

3. **Consider a separate sub-transaction ExUnits cap** (e.g., `maxSubTxExUnits`) as a protocol parameter to allow independent tuning of the sub-transaction budget.

---

### Proof of Concept

An attacker submits a top-level Dijkstra transaction with `k` sub-transactions. Each sub-transaction spends a UTxO locked by an `alwaysSucceeds` Plutus script and declares `ExUnits { exUnitsMem = M, exUnitsSteps = S }` where `(M, S) = maxTxExUnits`.

**Step 1 — top-level ExUnits check passes:**
```
totExUnits topTx = foldMap snd (topTx ^. witsTxL . rdmrsTxWitsL . unRedeemersL)
                 = ExUnits 0 0   -- top-level tx has no redeemers
```
`validateExUnitsTooBigUTxO` sees `ExUnits 0 0 ≤ maxTxExUnits` → passes.

**Step 2 — fee calculation ignores sub-transaction scripts:**
```
minfee pp topTx = a·size + b + txscriptfee prices (ExUnits 0 0)
               = a·size + b   -- no script fee charged
```

**Step 3 — actual execution:**
The UTXOS rule processes `stAnnTx` including all `k` sub-transactions. Each sub-transaction's script is executed with its declared `maxTxExUnits` budget. Total execution = `k × maxTxExUnits`.

**Step 4 — block-level check also passes:**
```
foldMap totExUnits [topTx] = ExUnits 0 0 ≤ maxBlockExUnits
```

With `k` chosen so that `k × maxTxExUnits >> maxBlockExUnits`, the block validator performs far more script execution than the protocol intends, while the attacker pays only the base byte-size fee.

### Citations

**File:** eras/alonzo/impl/src/Cardano/Ledger/Alonzo/Tx.hs (L391-394)
```haskell
  (EraTx era, AlonzoEraTxWits era) =>
  Tx l era ->
  ExUnits
totExUnits tx = foldMap snd $ tx ^. witsTxL . rdmrsTxWitsL . unRedeemersL
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs (L296-302)
```haskell
  when (hasAnyRedeemers tx) $
    Babbage.validateTotalCollateral pp (tx ^. bodyTxL) utxoCollateral
  where
    utxoCollateral = Map.restrictKeys utxo (tx ^. bodyTxL . collateralInputsTxBodyL)
    hasAnyRedeemers t =
      hasRedeemers t || any hasRedeemers (t ^. bodyTxL . subTransactionsTxBodyL)
    hasRedeemers = not . null . (^. witsTxL . rdmrsTxWitsL . unRedeemersL)
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs (L414-415)
```haskell
  {- totExunits tx ≤ maxTxExUnits pp -}
  runTest $ Alonzo.validateExUnitsTooBigUTxO pp tx
```

**File:** eras/alonzo/impl/src/Cardano/Ledger/Alonzo/Rules/Utxo.hs (L459-465)
```haskell
validateExUnitsTooBigUTxO pp tx =
  failureUnless (pointWiseExUnits (<=) totalExUnits maxTxExUnits) $
    ExUnitsTooBigUTxO Mismatch {mismatchSupplied = totalExUnits, mismatchExpected = maxTxExUnits}
  where
    maxTxExUnits = pp ^. ppMaxTxExUnitsL
    -- This sums up the ExUnits for all embedded Plutus Scripts anywhere in the transaction:
    totalExUnits = totExUnits tx
```

**File:** eras/alonzo/impl/src/Cardano/Ledger/Alonzo/Rules/Bbody.hs (L147-167)
```haskell
-- | Validate that total execution units (all transactions) do not exceed block limit.
-- ∑(tx ∈ txs)(totExunits tx) ≤ maxBlockExUnits pp
validateExUnits ::
  forall era.
  ( AlonzoEraTx era
  , InjectRuleFailure "BBODY" AlonzoBbodyPredFailure era
  ) =>
  StrictSeq.StrictSeq (Tx TopTx era) ->
  -- | Max block exunits protocol parameter.
  ExUnits ->
  Rule (EraRule "BBODY" era) 'Transition ()
validateExUnits txs ppMax =
  let txTotal = foldMap totExUnits txs
   in pointWiseExUnits (<=) txTotal ppMax
        ?! injectFailure
          ( TooManyExUnits $
              Mismatch
                { mismatchSupplied = txTotal
                , mismatchExpected = ppMax
                }
          )
```

**File:** eras/alonzo/formal-spec/utxo.tex (L36-39)
```tex
    &\fun{minfee} : \PParams \to \Tx \to \Coin \\
    &\fun{minfee}~\var{pp}~\var{tx} = \\
    &~~(\fun{a}~\var{pp}) \cdot \fun{txSize}~\var{tx} + (\fun{b}~\var{pp}) +
    \hldiff{\fun{txscriptfee}~(\fun{prices}~{pp})~(\fun{totExunits}~(\fun{txbody}~{tx}))}
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs (L263-276)
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
```
