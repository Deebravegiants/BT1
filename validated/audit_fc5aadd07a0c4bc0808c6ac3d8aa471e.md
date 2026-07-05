### Title
Sub-Transaction ExUnits Not Validated Against Protocol Limits in Dijkstra Era - (File: eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs)

### Summary

The Dijkstra era introduces sub-transactions that can carry Plutus scripts with their own ExUnits budgets. The per-transaction ExUnits limit check (`validateExUnitsTooBigUTxO`) and the per-block ExUnits limit check (`validateExUnits`) both operate only on the top-level transaction's redeemers. Sub-transaction ExUnits are never aggregated or checked against `maxTxExUnits` or `maxBlockExUnits`. An unprivileged transaction author can craft a top-level transaction embedding many sub-transactions, each declaring an ExUnits budget up to `maxTxExUnits`, causing validators to execute computation that far exceeds the intended protocol-parameter limits without paying the corresponding fees.

### Finding Description

**Root cause — per-transaction check misses sub-transactions.**

In `eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs` the UTXO transition rule calls:

```haskell
{- totExunits tx ≤ maxTxExUnits pp -}
runTest $ Alonzo.validateExUnitsTooBigUTxO pp tx
```

`validateExUnitsTooBigUTxO` is defined in `eras/alonzo/impl/src/Cardano/Ledger/Alonzo/Rules/Utxo.hs` as:

```haskell
validateExUnitsTooBigUTxO pp tx =
  failureUnless (pointWiseExUnits (<=) totalExUnits maxTxExUnits) ...
  where
    maxTxExUnits = pp ^. ppMaxTxExUnitsL
    totalExUnits = totExUnits tx
```

`totExUnits` is defined in `eras/alonzo/impl/src/Cardano/Ledger/Alonzo/Tx.hs`:

```haskell
totExUnits tx = foldMap snd $ tx ^. witsTxL . rdmrsTxWitsL . unRedeemersL
```

This only folds over the **top-level transaction's** redeemer map. Sub-transactions are stored in `dtbrSubTransactions :: !(OMap TxId (Tx SubTx era))` inside `DijkstraTxBodyRaw` and each carries its own `TxWits` (including redeemers). Those redeemers are never reached by `totExUnits`.

**Root cause — per-block check misses sub-transactions.**

In `eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Bbody.hs` the BBODY transition calls:

```haskell
Alonzo.validateExUnits @era txs $ pp ^. ppMaxBlockExUnitsL
```

`validateExUnits` in `eras/alonzo/impl/src/Cardano/Ledger/Alonzo/Rules/Bbody.hs` is:

```haskell
validateExUnits txs ppMax =
  let txTotal = foldMap totExUnits txs
```

Again `totExUnits` is applied to each top-level transaction only; sub-transaction ExUnits are excluded from the block-level sum.

**Root cause — sub-transaction rule chain has no ExUnits check.**

Sub-transactions are processed through `SUBLEDGERS → SUBLEDGER → SUBUTXOW → SUBUTXO`. The `DijkstraSubUtxoPredFailure` type in `eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/SubUtxo.hs` contains no `ExUnitsTooBigUTxO` constructor, confirming there is no ExUnits limit check anywhere in the sub-transaction validation path.

**Contrast with reference-script size handling.**

The Dijkstra era correctly aggregates sub-transaction reference-script sizes via `batchNonDistinctRefScriptsSize` in `eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs` and enforces the combined limit in `validateAllRefScriptSize` inside the LEDGER rule. No analogous aggregation exists for ExUnits.

**Fee calculation also excludes sub-transaction ExUnits.**

`alonzoMinFeeTx` in `eras/alonzo/impl/src/Cardano/Ledger/Alonzo/Tx.hs` computes:

```haskell
alonzoMinFeeTx pp tx =
  ...
    <+> txscriptfee (pp ^. ppPricesL) allExunits
  where
    allExunits = totExUnits tx
```

Because `totExUnits tx` excludes sub-transaction ExUnits, the minimum-fee check (`validateFeeTooSmallUTxO`) in the Dijkstra UTXO rule does not charge for sub-transaction script execution, allowing the attacker to obtain unbounded computation at the price of only the top-level transaction's ExUnits.

### Impact Explanation

An attacker can submit a single Dijkstra top-level transaction containing N sub-transactions, each declaring an ExUnits budget of `maxTxExUnits`. The top-level transaction itself also declares `maxTxExUnits`. The total computation demanded from every validating node is `(N+1) × maxTxExUnits`, which can be made arbitrarily large by increasing N. Neither the per-transaction nor the per-block limit is triggered. The fee paid covers only the top-level ExUnits. This constitutes an attacker-controlled transaction exceeding intended validation limits — matching the **Medium** impact category: *"Attacker-controlled transactions, blocks, certificates, votes, proposals, scripts, witnesses, or serialized inputs exceed intended validation limits or modify fees, deposits, refunds, rewards, treasury donations, or withdrawals outside design parameters."*

### Likelihood Explanation

**Medium.** The Dijkstra era is newly introduced and sub-transactions are a new feature. Any unprivileged user who can submit a valid Dijkstra transaction can exploit this. No privileged keys, governance majority, or external dependency compromise is required. The only constraint is constructing a syntactically valid transaction with sub-transactions, which is a standard user-level operation.

### Recommendation

1. Aggregate ExUnits across the entire batch (top-level + all sub-transactions) before applying the `maxTxExUnits` check, analogously to how `batchNonDistinctRefScriptsSize` aggregates reference-script sizes.
2. Update the block-level `validateExUnits` (or introduce a Dijkstra-specific override) to sum ExUnits from sub-transactions as well as top-level transactions.
3. Update `getMinFeeTx` for the Dijkstra era to include sub-transaction ExUnits in the fee calculation, so that the cost of sub-transaction script execution is reflected in the minimum fee.

### Proof of Concept

1. Attacker obtains `maxTxExUnits = ExUnits M S` from the current protocol parameters.
2. Attacker constructs a Dijkstra top-level transaction `txTop` with:
   - Its own redeemers declaring `ExUnits M S` (passes `validateExUnitsTooBigUTxO`).
   - N sub-transactions `subTx_1 … subTx_N`, each with redeemers declaring `ExUnits M S`.
3. The UTXO rule checks `totExUnits txTop = ExUnits M S ≤ maxTxExUnits` — **passes**.
4. The BBODY rule checks `foldMap totExUnits [txTop] = ExUnits M S ≤ maxBlockExUnits` — **passes** (assuming one tx per block for simplicity).
5. Sub-transactions are processed through `SUBLEDGERS`; no ExUnits check is performed.
6. Every validating node executes `(N+1) × ExUnits M S` worth of Plutus computation.
7. The fee paid by the attacker covers only `ExUnits M S`, not `(N+1) × ExUnits M S`.

By choosing N large enough, the attacker forces validators to perform computation exceeding `maxBlockExUnits` while paying fees proportional only to `maxTxExUnits`. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6) [8](#0-7) [9](#0-8) [10](#0-9)

### Citations

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

**File:** eras/alonzo/impl/src/Cardano/Ledger/Alonzo/Tx.hs (L375-388)
```haskell
alonzoMinFeeTx ::
  ( EraTx era
  , AlonzoEraTxWits era
  , AlonzoEraPParams era
  ) =>
  PParams era ->
  Tx l era ->
  Coin
alonzoMinFeeTx pp tx =
  (tx ^. sizeTxF <×> (fromCompact . unCoinPerByte) (pp ^. ppTxFeePerByteL))
    <+> (pp ^. ppTxFeeFixedL)
    <+> txscriptfee (pp ^. ppPricesL) allExunits
  where
    allExunits = totExUnits tx
```

**File:** eras/alonzo/impl/src/Cardano/Ledger/Alonzo/Tx.hs (L390-394)
```haskell
totExUnits ::
  (EraTx era, AlonzoEraTxWits era) =>
  Tx l era ->
  ExUnits
totExUnits tx = foldMap snd $ tx ^. witsTxL . rdmrsTxWitsL . unRedeemersL
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Bbody.hs (L361-363)
```haskell
  Alonzo.validateExUnits @era txs $ pp ^. ppMaxBlockExUnitsL

  Conway.validateBodyRefScriptsSizeTooBig @era pp blockBody (ls ^. utxoL)
```

**File:** eras/alonzo/impl/src/Cardano/Ledger/Alonzo/Rules/Bbody.hs (L158-167)
```haskell
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

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/SubUtxo.hs (L72-110)
```haskell
data DijkstraSubUtxoPredFailure era
  = -- | The bad transaction inputs
    SubBadInputsUTxO (NonEmptySet TxIn)
  | SubOutsideValidityIntervalUTxO
      -- | transaction's validity interval
      ValidityInterval
      -- | current slot
      SlotNo
  | SubMaxTxSizeUTxO (Mismatch RelLTEQ Word32)
  | SubInputSetEmptyUTxO
  | -- | the set of addresses with incorrect network IDs
    SubWrongNetwork
      -- | the expected network id
      Network
      -- | the set of addresses with incorrect network IDs
      (NonEmptySet Addr)
  | SubWrongNetworkWithdrawal
      -- | the expected network id
      Network
      -- | the set of reward addresses with incorrect network IDs
      (NonEmptySet AccountAddress)
  | -- | list of supplied bad transaction outputs
    SubOutputBootAddrAttrsTooBig (NonEmpty (TxOut era))
  | -- | list of supplied bad transaction output triples (actualSize,PParameterMaxValue,TxOut)
    SubOutputTooBigUTxO (NonEmpty (Int, Int, TxOut era))
  | -- | Wrong Network ID in body
    SubWrongNetworkInTxBody
      (Mismatch RelEQ Network)
  | -- | slot number outside consensus forecast range
    SubOutsideForecast SlotNo
  | -- | list of supplied transaction outputs that are too small,
    -- together with the minimum value for the given output.
    SubBabbageOutputTooSmallUTxO (NonEmpty (TxOut era, Coin))
  | SubWrongNetworkInDirectDeposit
      -- | the expected network id
      Network
      -- | the set of account addresses with incorrect network IDs
      (NonEmptySet AccountAddress)
  deriving (Generic)
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

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/TxBody.hs (L183-188)
```haskell
    , dtbrTreasuryDonation :: !Coin
    , dtbrSubTransactions :: !(OMap TxId (Tx SubTx era))
    , dtbrDirectDeposits :: !DirectDeposits
    , dtbrAccountBalanceIntervals :: !(AccountBalanceIntervals era)
    } ->
    DijkstraTxBodyRaw TopTx era
```
