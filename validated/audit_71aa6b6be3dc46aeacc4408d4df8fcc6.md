Now I have all the information needed to make a determination. Let me trace the exact code paths.

**Fee check path:**
- `dijkstraUtxoTransition` line 373: `runTest $ Shelley.validateFeeTooSmallUTxO pp tx originalUtxo`
- → `validateFeeTooSmallUTxO` calls `getMinFeeTxUtxo pp tx utxo`
- → For `DijkstraEra`, `getMinFeeTxUtxo = getConwayMinFeeTxUtxo` (UTxO.hs line 141)
- → `getConwayMinFeeTxUtxo pparams tx utxo = getMinFeeTx pparams tx $ txNonDistinctRefScriptsSize utxo tx`
- → `txNonDistinctRefScriptsSize` only looks at `tx ^. bodyTxL . referenceInputsTxBodyL` and `inputsTxBodyL` of the **top-level tx only**

**Size limit check path:**
- `dijkstraLedgerTransition` line 392: `runTest $ validateAllRefScriptSize pp originalUtxo tx`
- → `validateAllRefScriptSize` calls `batchNonDistinctRefScriptsSize utxo tx`
- → `batchNonDistinctRefScriptsSize` = `txNonDistinctRefScriptsSize utxo tx` + `foldMap' (Sum . txNonDistinctRefScriptsSize utxo) (tx ^. bodyTxL . subTransactionsTxBodyL)` — **top-level + all subtransactions**

The asymmetry is real and confirmed in code. The fee is computed from top-level reference scripts only, while the size cap enforces the batch total. An attacker can load all reference scripts into subtransactions, pay zero tiered ref-script fee premium, and still pass the size cap as long as the batch total ≤ `ppMaxRefScriptSizePerTx`.

---

### Title
Fee Calculation Excludes Subtransaction Reference Scripts While Size Limit Covers the Full Batch — (`eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs`, `Rules/Ledger.hs`, `Rules/Utxo.hs`)

### Summary
In the Dijkstra era, the minimum-fee check (`validateFeeTooSmallUTxO`) computes the tiered reference-script fee premium using only the top-level transaction's inputs, while the reference-script size cap (`validateAllRefScriptSize`) enforces a limit over the entire batch (top-level + all subtransactions). An unprivileged transaction author can place all large reference scripts exclusively in subtransactions, pay a fee computed as if no reference scripts exist, and still pass the size-cap guard.

### Finding Description

`getMinFeeTxUtxo` for `DijkstraEra` is bound to `getConwayMinFeeTxUtxo`: [1](#0-0) 

`getConwayMinFeeTxUtxo` passes only the top-level tx's ref-script size to the tiered fee formula: [2](#0-1) 

`txNonDistinctRefScriptsSize` only unions the top-level tx's `referenceInputsTxBodyL` and `inputsTxBodyL`: [3](#0-2) 

The UTXO rule invokes the fee check on the top-level tx: [4](#0-3) 

Meanwhile, `validateAllRefScriptSize` in the LEDGER rule uses `batchNonDistinctRefScriptsSize`, which sums over the top-level tx **and** every subtransaction: [5](#0-4) [6](#0-5) 

The SUBUTXO rule for subtransactions has no fee check at all — there is no `validateFeeTooSmallUTxO` call in `dijkstraSubUtxoTransition`: [7](#0-6) 

### Impact Explanation

The tiered ref-script fee (`tierRefScriptFee`) is exponentially increasing and was introduced specifically to deter DDoS via large reference scripts (see ADR 009). With `ppMaxRefScriptSizePerTx = 200 KiB`, the tiered premium for a full 200 KiB batch is several ADA. An attacker who places all reference scripts in subtransactions pays **zero** tiered premium while consuming the full allowed ref-script budget. This directly modifies fees outside design parameters (Medium impact scope).

### Likelihood Explanation

The attack requires only crafting a valid `TopTx` with subtransactions that reference UTxO entries containing large scripts. No privileged access, governance majority, or key compromise is needed. The attacker must have previously created UTxO entries with large reference scripts, which is a normal on-chain operation. The exploit is deterministic and locally testable.

### Recommendation

Replace the `getMinFeeTxUtxo` instance for `DijkstraEra` with a batch-aware version that passes `batchNonDistinctRefScriptsSize utxo tx` (instead of `txNonDistinctRefScriptsSize utxo tx`) to `getMinFeeTx`. This mirrors the same correction already applied to `validateAllRefScriptSize`.

### Proof of Concept

1. Create UTxO entries containing large Plutus scripts (e.g., 8 × 25 KiB = 200 KiB total).
2. Construct a `TopTx` with **empty** `referenceInputsTxBodyL` and `inputsTxBodyL` (no top-level ref scripts), but embed N subtransactions each referencing one of those large-script UTxO entries.
3. Set `feeTxBodyL` to `getConwayMinFeeTxUtxo pp topTx utxo` — which returns the base fee with zero ref-script premium.
4. Submit. `validateFeeTooSmallUTxO` passes (fee ≥ top-level min fee). `validateAllRefScriptSize` passes (total batch size ≤ 200 KiB). The transaction is accepted.
5. Assert: `batchNonDistinctRefScriptsSize utxo topTx > 0` while `txNonDistinctRefScriptsSize utxo topTx == 0`, confirming the fee paid does not cover the batch's ref-script cost.

### Citations

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs (L141-141)
```haskell
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

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/SubUtxo.hs (L231-278)
```haskell
dijkstraSubUtxoTransition = do
  TRC (SubUtxoEnv slot pp certState originalUtxo (IsValid isValid), utxoState, stAnnTx) <-
    judgmentContext
  let tx = stAnnTx ^. txStAnnTxG

  let txBody = tx ^. bodyTxL

  runTest $ Allegra.validateOutsideValidityIntervalUTxO slot txBody

  sysSt <- liftSTS $ asks systemStart
  ei <- liftSTS $ asks epochInfo
  runTest $ Alonzo.validateOutsideForecast ei slot sysSt tx

  let allSizedOutputs = txBody ^. allSizedOutputsTxBodyF
  let allOutputs = fmap sizedValue allSizedOutputs
  runTest $ Alonzo.validateOutputTooBigUTxO pp allOutputs

  runTest $ Shelley.validateInputSetEmptyUTxO txBody

  let inputs = txBody ^. inputsTxBodyL
  let refInputs = txBody ^. referenceInputsTxBodyL
  runTest $ Shelley.validateBadInputsUTxO originalUtxo (inputs `Set.union` refInputs)
  runTest $ Shelley.validateBadInputsUTxO (utxosUtxo utxoState) inputs

  runTestOnSignal $ Shelley.validateOutputBootAddrAttrsTooBig allOutputs

  runTestOnSignal $ Babbage.validateOutputTooSmallUTxO pp allSizedOutputs

  netId <- liftSTS $ asks networkId
  runTestOnSignal $ Shelley.validateWrongNetwork netId allOutputs
  runTestOnSignal $ Shelley.validateWrongNetworkWithdrawal netId txBody
  runTestOnSignal $ validateWrongNetworkInDirectDeposit netId txBody
  runTestOnSignal $ Alonzo.validateWrongNetworkInTxBody netId txBody

  if isValid
    then do
      newState <-
        Shelley.updateUTxOStateNoFees
          pp
          utxoState
          txBody
          certState
          (utxosGovState utxoState)
          (tellEvent . TotalDeposits (hashAnnotated txBody))
          (\a b -> tellEvent $ TxUTxODiff a b)
      pure $ newState & utxosDonationL <>~ txBody ^. treasuryDonationTxBodyL
    else
      pure utxoState
```
