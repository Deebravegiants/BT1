### Title
Sub-Transaction Reference Script Fees Not Included in Minimum Fee Calculation - (File: `eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs`)

### Summary

In the Dijkstra era, the `getMinFeeTxUtxo` implementation reuses `getConwayMinFeeTxUtxo`, which only measures reference script sizes from the **top-level transaction**. A Dijkstra-specific function `batchNonDistinctRefScriptsSize` exists and correctly aggregates reference script sizes across the top-level transaction **and all sub-transactions**, but it is never used in the fee calculation. As a result, an attacker can include large reference scripts exclusively in sub-transactions, paying a fee that does not cover the deserialization cost of those scripts.

### Finding Description

The Dijkstra era introduces nested ("sub") transactions. The codebase defines `batchNonDistinctRefScriptsSize` to compute the total reference script byte size across the entire batch:

```haskell
-- eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs:271-277
batchNonDistinctRefScriptsSize utxo tx =
  txNonDistinctRefScriptsSize utxo tx
    + getSum
      ( foldMap'
          (Sum . txNonDistinctRefScriptsSize utxo)
          (tx ^. bodyTxL . subTransactionsTxBodyL)
      )
```

This function is correctly used in `validateAllRefScriptSize` (the size-limit check in the LEDGER rule) to enforce `ppMaxRefScriptSizePerTx` across the whole batch. [1](#0-0) 

However, the `EraUTxO DijkstraEra` instance assigns `getMinFeeTxUtxo` to the Conway implementation:

```haskell
-- eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs:141
getMinFeeTxUtxo = getConwayMinFeeTxUtxo
``` [2](#0-1) 

`getConwayMinFeeTxUtxo` calls only `txNonDistinctRefScriptsSize`, which inspects only the top-level transaction's inputs and reference inputs:

```haskell
-- eras/conway/impl/src/Cardano/Ledger/Conway/UTxO.hs:174-175
getConwayMinFeeTxUtxo pparams tx utxo =
  getMinFeeTx pparams tx $ txNonDistinctRefScriptsSize utxo tx
``` [3](#0-2) 

`txNonDistinctRefScriptsSize` only unions the top-level tx's `referenceInputsTxBodyL` and `inputsTxBodyL`; it never descends into sub-transactions:

```haskell
-- eras/conway/impl/src/Cardano/Ledger/Conway/UTxO.hs:183-187
txNonDistinctRefScriptsSize utxo tx = getSum $ foldMap (Sum . originalBytesSize . snd) refScripts
  where
    inputs = (tx ^. bodyTxL . referenceInputsTxBodyL) `Set.union` (tx ^. bodyTxL . inputsTxBodyL)
    refScripts = getReferenceScriptsNonDistinct utxo inputs
``` [4](#0-3) 

The UTXO rule for Dijkstra enforces the minimum fee using this under-counting path:

```haskell
-- eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs:372-373
{- minfee pp txTop utxo₀ ≤ txfee txb -}
runTest $ Shelley.validateFeeTooSmallUTxO pp tx originalUtxo
``` [5](#0-4) 

`validateFeeTooSmallUTxO` calls `getMinFeeTxUtxo`, which resolves to `getConwayMinFeeTxUtxo` for `DijkstraEra`, silently omitting all sub-transaction reference script costs from the minimum fee. [6](#0-5) 

The analogy to the external report is exact: a more-complete fee value (`batchNonDistinctRefScriptsSize`) is computed and used for the size-limit check, but the fee enforcement path uses the narrower Conway-era value (`txNonDistinctRefScriptsSize`) that ignores sub-transactions entirely.

### Impact Explanation

An attacker submits a Dijkstra-era top-level transaction with an empty or minimal reference-script set at the top level, while packing sub-transactions with reference scripts up to the `ppMaxRefScriptSizePerTx` byte limit. The fee paid covers only the top-level reference script cost (potentially zero), while every validating node must deserialize and process all sub-transaction reference scripts. This is the same DDoS attack vector that was explicitly fixed in Conway (see ADR-009) but is re-opened for sub-transactions in Dijkstra. The fee paid is below the protocol's intended design parameters for the actual computational work performed. This matches the **Medium** impact category: attacker-controlled transactions modify fees outside design parameters. [7](#0-6) 

### Likelihood Explanation

Any unprivileged transaction sender can craft such a transaction. No special access, key compromise, or governance majority is required. The Dijkstra era is the current development target, so this is reachable once the era is live. The attack is cheap to mount repeatedly because the fee is artificially low.

### Recommendation

Override `getMinFeeTxUtxo` in the `EraUTxO DijkstraEra` instance with a Dijkstra-specific implementation that uses `batchNonDistinctRefScriptsSize` instead of `txNonDistinctRefScriptsSize`:

```haskell
-- In eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs
getDijkstraMinFeeTxUtxo ::
  ( EraTx era
  , DijkstraEraTxBody era
  , BabbageEraTxBody era
  ) =>
  PParams era -> Tx l era -> UTxO era -> Coin
getDijkstraMinFeeTxUtxo pparams tx utxo =
  getMinFeeTx pparams tx $ batchNonDistinctRefScriptsSize utxo tx

instance EraUTxO DijkstraEra where
  ...
  getMinFeeTxUtxo = getDijkstraMinFeeTxUtxo  -- was: getConwayMinFeeTxUtxo
``` [8](#0-7) 

### Proof of Concept

1. Construct a Dijkstra-era top-level transaction with zero reference inputs at the top level (fee contribution from `txNonDistinctRefScriptsSize` = 0 bytes of ref scripts).
2. Embed N sub-transactions, each referencing a UTxO output that carries a large Plutus reference script (e.g., 25 KiB each), staying within `ppMaxRefScriptSizePerTx`.
3. Set `txfee` to the minimum fee computed by `getConwayMinFeeTxUtxo` (which ignores sub-transaction reference scripts).
4. Submit the transaction. `validateFeeTooSmallUTxO` passes because `minFee` was computed without sub-transaction reference script costs.
5. Every validating node deserializes all sub-transaction reference scripts at no additional fee cost to the attacker.

The size-limit check (`validateAllRefScriptSize`) will still reject batches exceeding `ppMaxRefScriptSizePerTx`, but within that limit the attacker pays far less than the protocol intends for the deserialization work performed. [9](#0-8)

### Citations

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

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs (L372-373)
```haskell
  {- minfee pp txTop utxo₀ ≤ txfee txb -}
  runTest $ Shelley.validateFeeTooSmallUTxO pp tx originalUtxo
```

**File:** eras/shelley/impl/src/Cardano/Ledger/Shelley/Rules/Utxo.hs (L446-456)
```haskell
validateFeeTooSmallUTxO pp tx utxo =
  failureUnless (minFee <= txFee) $
    FeeTooSmallUTxO
      Mismatch
        { mismatchSupplied = txFee
        , mismatchExpected = minFee
        }
  where
    minFee = getMinFeeTxUtxo pp tx utxo
    txFee = txb ^. feeTxBodyL
    txb = tx ^. bodyTxL
```

**File:** docs/adr/2024-08-14_009-refscripts-fee-change.md (L15-19)
```markdown
It was identified a while ago that there is an overhead associated with deserializing scripts, so much so that it would be possible to create a very large script that was fairly expensive to deserialize, but very cheap to execute. This opened up an attack vector when such a Plutus script would be used as a reference script. This problem was exacerbated by the fact that there was no real limit on the total size of reference scripts that could be used in a transaction, thus being limited only by the size of the transaction itself. Therefore this opened up Cardano to a DDoS attack where an attacker could submit many such transactions that would cost very little, but would be expensive for a `cardano-node` to validate.

In order to prevent such an attack a `"minFeeRefScriptCostPerByte"` protocol parameter was introduced in the Conway era. The idea was fairly simple: we would calculate the total size of reference scripts used by a transaction and multiply it by the value specified by this protocol parameter. Result would be added to the transaction fee. However, in order for this approach to be a definite deterrent of such attacks this parameter would have to be set to a fairly high value. Community was not very keen on having this value set to a high enough value, since that could make reference scripts almost as expensive to use as regular scripts, thus significantly reducing their usability. Taking this fact into consideration, a decision was made to set this parameter to a fairly moderate value to at l ... (truncated)

Unfortunately things did not go exactly as planned, because on [June 25th 2024 an attack like this actually took place](https://cardanospot.io/news/ddos-attack-on-the-cardano-blockchain-mRIKAzZTNnzq5NGd). This attack forced us to make a quick decision on implementing a definite prevention of such attacks, while trying to not have a drastic impact on the common use case that DApp developers rely on so much.
```
