### Title
Sub-Transaction Execution Units Excluded from Block-Level `maxBlockExUnits` Enforcement — (`File: eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Bbody.hs`)

---

### Summary

In the Dijkstra era, a top-level transaction may embed an ordered set of sub-transactions (`sub_transactions`). The block-body rule (`BBODY`) enforces a per-block execution-unit ceiling via `validateExUnits`, but that function only sums `totExUnits` over the top-level transactions in the block. Because `totExUnits` reads only the top-level transaction's own witness-set redeemers, the execution units declared in every sub-transaction's witness set are invisible to the block-level check. An unprivileged transaction submitter can therefore craft a single top-level transaction whose sub-transactions collectively declare execution units far in excess of `maxBlockExUnits`, causing honest nodes to perform Plutus evaluation work that the protocol parameter was designed to cap.

---

### Finding Description

**Root cause — `totExUnits` ignores sub-transaction redeemers**

`totExUnits` is defined in `eras/alonzo/impl/src/Cardano/Ledger/Alonzo/Tx.hs`:

```haskell
totExUnits tx = foldMap snd $ tx ^. witsTxL . rdmrsTxWitsL . unRedeemersL
```

It folds only over the redeemers stored in the single `TxWits` of the supplied `Tx`. A Dijkstra top-level transaction carries its sub-transactions inside `dtbrSubTransactions :: OMap TxId (Tx SubTx era)` in the transaction body; each sub-transaction has its own independent `TxWits` with its own redeemers. Those redeemers are never reached by `totExUnits`.

**Block-body rule uses `totExUnits` exclusively**

`dijkstraBbodyTransition` in `eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Bbody.hs` calls:

```haskell
Alonzo.validateExUnits @era txs $ pp ^. ppMaxBlockExUnitsL
```

`validateExUnits` is:

```haskell
validateExUnits txs ppMax =
  let txTotal = foldMap totExUnits txs   -- only top-level tx redeemers
  in pointWiseExUnits (<=) txTotal ppMax ?! ...
```

`txs` is `blockBody ^. txSeqBlockBodyL`, the sequence of top-level transactions. Sub-transactions are not in this sequence; they are nested inside each top-level transaction body. The fold therefore never visits sub-transaction redeemers.

**Per-transaction check also misses sub-transactions**

The top-level UTXO rule (`eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs`) applies:

```haskell
runTest $ Alonzo.validateExUnitsTooBigUTxO pp tx
```

This enforces `totExUnits tx ≤ maxTxExUnits pp` for the top-level transaction only. Each sub-transaction is processed by the `SUBLEDGER` → `SUBUTXO` chain, which applies the same per-transaction check individually to each sub-transaction. So each sub-transaction is individually bounded by `maxTxExUnits`, but there is no aggregation of sub-transaction execution units at the block level.

**Asymmetry with reference-script size**

The Dijkstra LEDGER rule does aggregate sub-transaction reference-script sizes via `batchNonDistinctRefScriptsSize` in `validateAllRefScriptSize`. The analogous aggregation is absent for execution units, confirming this is an oversight rather than a design choice.

**Attack path**

1. Attacker constructs a top-level transaction with zero top-level Plutus scripts (so `totExUnits` of the top-level tx = 0).
2. The transaction body includes `K` sub-transactions, each containing Plutus scripts with redeemers declaring `maxTxExUnits` execution units.
3. The total serialized size of the transaction must fit within `maxTxSize`; with compact sub-transactions this allows a meaningful number of sub-transactions.
4. The block-level check sees `totExUnits = 0` for the top-level transaction and passes.
5. Nodes must actually evaluate `K × maxTxExUnits` worth of Plutus computation to validate the block.

---

### Impact Explanation

**Medium — attacker-controlled transactions exceed intended validation limits.**

`maxBlockExUnits` is the protocol mechanism that bounds the total Plutus evaluation work per block, ensuring block validation time and memory usage remain within safe bounds. By embedding Plutus scripts exclusively in sub-transactions, an attacker can submit a block whose actual evaluation cost is a multiple of `maxBlockExUnits`. This forces every honest node to perform unbounded (relative to the intended cap) Plutus evaluation work per block, degrading throughput and potentially causing nodes to fall behind the chain tip or exhaust memory under sustained attack. The attack requires no privileged access: any transaction submitter in the Dijkstra era can craft such a transaction.

---

### Likelihood Explanation

The Dijkstra era is the first era to support nested transactions. The `sub_transactions` field is freely available to any transaction author. The only cost to the attacker is the transaction fee (proportional to transaction size and declared execution units) and the governance deposit for any governance actions in sub-transactions. Because the top-level transaction's `totExUnits` is zero, the script-fee component of the minimum fee is also zero for the top-level transaction, making the attack relatively cheap. The constraint is `maxTxSize`, which limits how many sub-transactions can be packed into one top-level transaction, but multiple such transactions can be included in a single block.

---

### Recommendation

Extend `totExUnits` (or introduce a new aggregation function) to recursively sum execution units across all sub-transactions when operating on a Dijkstra-era top-level transaction. The block-level check in `dijkstraBbodyTransition` should use this extended function so that `∑(tx ∈ txs)(totExUnits tx + ∑(subTx ∈ subTxs(tx)) totExUnits subTx) ≤ maxBlockExUnits pp`. The per-transaction check in the top-level UTXO rule should similarly aggregate sub-transaction execution units to enforce a meaningful per-transaction ceiling. This mirrors how `validateAllRefScriptSize` already uses `batchNonDistinctRefScriptsSize` to aggregate reference-script sizes across sub-transactions.

---

### Proof of Concept

```
Block contains 1 top-level Dijkstra transaction T:
  T.body.inputs        = { some UTxO }
  T.body.fee           = minFee (no top-level scripts → script fee = 0)
  T.body.subTransactions = {
    SubTx_1: { inputs: {...}, outputs: {...},
                witnesses: { redeemers: { (Spend,0) → (datum, maxTxExUnits) } },
                scripts:   { alwaysSucceeds_v4 } },
    SubTx_2: same as SubTx_1 with different inputs,
    ...
    SubTx_K: same pattern
  }
  T.witnesses = {}   -- no top-level redeemers

Block-level check:
  txTotal = foldMap totExUnits [T]
          = totExUnits T
          = foldMap snd (T.witnesses.redeemers)
          = ExUnits 0 0          -- passes maxBlockExUnits check

Actual Plutus evaluation cost:
  K × maxTxExUnits               -- each sub-tx individually passes maxTxExUnits
                                 -- but aggregate is K × maxTxExUnits
``` [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6)

### Citations

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Bbody.hs (L351-361)
```haskell
  let txs = blockBody ^. txSeqBlockBodyL

  ls' <-
    trans @(EraRule "LEDGERS" era) $
      TRC
        ( Shelley.LedgersEnv bhSlot curEpoch pp account
        , ls
        , fromStrict txs
        )

  Alonzo.validateExUnits @era txs $ pp ^. ppMaxBlockExUnitsL
```

**File:** eras/alonzo/impl/src/Cardano/Ledger/Alonzo/Tx.hs (L390-394)
```haskell
totExUnits ::
  (EraTx era, AlonzoEraTxWits era) =>
  Tx l era ->
  ExUnits
totExUnits tx = foldMap snd $ tx ^. witsTxL . rdmrsTxWitsL . unRedeemersL
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

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs (L413-415)
```haskell

  {- totExunits tx ≤ maxTxExUnits pp -}
  runTest $ Alonzo.validateExUnitsTooBigUTxO pp tx
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/SubLedgers.hs (L128-135)
```haskell
dijkstraSubLedgersTransition = do
  TRC (env, ledgerState, subTxs) <- judgmentContext
  foldM
    ( \ls subTx ->
        trans @(EraRule "SUBLEDGER" era) $ TRC (env, ls, subTx)
    )
    ledgerState
    subTxs
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/TxBody.hs (L184-184)
```haskell
    , dtbrSubTransactions :: !(OMap TxId (Tx SubTx era))
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
