### Title
Sub-Transaction Plutus Script ExUnits Excluded from Block and Transaction Execution-Unit Limit Checks — (`File: eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Bbody.hs`)

---

### Summary

The Dijkstra era introduces nested sub-transactions (`subTransactions`) embedded inside a top-level transaction body. Sub-transactions carry their own witness sets, including redeemers with declared `ExUnits` budgets for Plutus script execution. However, the block-level execution-unit cap (`maxBlockExUnits`) and the per-transaction cap (`maxTxExUnits`) are enforced exclusively against the top-level transaction's redeemers. Sub-transaction redeemers are structurally invisible to `totExUnits`, so an unprivileged sender can pack arbitrarily large Plutus execution budgets into sub-transactions and bypass both limits.

---

### Finding Description

**`totExUnits` only reads top-level witnesses.**

`totExUnits` is defined as:

```haskell
totExUnits tx = foldMap snd $ tx ^. witsTxL . rdmrsTxWitsL . unRedeemersL
``` [1](#0-0) 

It traverses only the top-level transaction's `TxWits`. Sub-transactions are stored in the top-level `TxBody` field `dtbrSubTransactions`, not in the top-level witnesses, so their redeemers are never reached. [2](#0-1) 

**Block-level check uses `totExUnits` over top-level transactions only.**

`dijkstraBbodyTransition` calls:

```haskell
Alonzo.validateExUnits @era txs $ pp ^. ppMaxBlockExUnitsL
``` [3](#0-2) 

`validateExUnits` folds `totExUnits` over the top-level transaction sequence:

```haskell
validateExUnits txs ppMax =
  let txTotal = foldMap totExUnits txs
  in pointWiseExUnits (<=) txTotal ppMax ...
``` [4](#0-3) 

Sub-transaction redeemers contribute zero to `txTotal`.

**Per-transaction check is equally blind.**

The Dijkstra UTXO rule enforces:

```haskell
{- totExunits tx ≤ maxTxExUnits pp -}
runTest $ Alonzo.validateExUnitsTooBigUTxO pp tx
``` [5](#0-4) 

Again, `tx` is the top-level transaction; sub-transaction redeemers are not summed.

**Sub-transactions are structured to execute Plutus scripts.**

`DijkstraSubTxBodyRaw` carries `dstbrScriptIntegrityHash`, which is only meaningful when Plutus scripts are executed (it commits to cost models, redeemers, and datums): [6](#0-5) 

`DijkstraStAnnSubTx` carries `dsastPlutusScriptsWithContext` and `dsastPlutusLanguagesUsed`, confirming that sub-transactions are annotated with Plutus execution contexts: [7](#0-6) 

**`SubUtxo` rule omits `validateExUnitsTooBigUTxO`.**

The sub-transaction validation rule (`SubUtxo`) performs input, output, network-ID, and size checks but contains no call to `validateExUnitsTooBigUTxO`, confirming there is no compensating per-sub-transaction cap: [8](#0-7) 

---

### Impact Explanation

`maxBlockExUnits` and `maxTxExUnits` exist to bound the CPU and memory consumed by Plutus script evaluation during block validation, ensuring that honest nodes can validate blocks within their time and memory budgets. By embedding Plutus scripts exclusively in sub-transactions, an attacker can submit a top-level transaction whose declared top-level ExUnits are zero (or minimal), while the sub-transactions collectively carry arbitrarily large ExUnits budgets. The block-level cap is never triggered. Nodes must execute all sub-transaction scripts regardless, consuming resources beyond the protocol's intended ceiling.

This matches the allowed Medium impact: **attacker-controlled transactions exceed intended validation limits outside design parameters**.

---

### Likelihood Explanation

Any unprivileged transaction sender can construct a Dijkstra-era top-level transaction with an `OMap` of sub-transactions, each carrying redeemers with large `ExUnits` declarations. No privileged access, governance majority, or key compromise is required. The Dijkstra era is the active development target in this repository and the code paths are production-bound.

---

### Recommendation

Extend `totExUnits` (or introduce a Dijkstra-specific variant) to recursively sum ExUnits from all sub-transaction redeemers:

```haskell
totExUnitsDijkstra tx =
  totExUnits tx
    <> foldMap totExUnits (OMap.elems $ tx ^. bodyTxL . subTransactionsTxBodyL)
```

Use this extended function in both `validateExUnitsTooBigUTxO` (per-transaction check) and `validateExUnits` (per-block check) when operating in the Dijkstra era. Additionally, add a per-sub-transaction ExUnits check inside the `SubUtxo` rule analogous to the existing `validateExUnitsTooBigUTxO` call in the top-level UTXO rule.

---

### Proof of Concept

1. Construct a Dijkstra top-level transaction with an empty top-level redeemer map (`ExUnits 0 0` total at the top level).
2. Embed N sub-transactions, each with a redeemer declaring `ExUnits { exUnitsMem = M, exUnitsSteps = S }` where `N * (M, S) >> maxBlockExUnits`.
3. Submit the block. `validateExUnits` computes `txTotal = ExUnits 0 0` (from the top-level transaction only) and passes the check.
4. Nodes execute all sub-transaction Plutus scripts, consuming `N * (M, S)` execution units — far exceeding `maxBlockExUnits` — with no predicate failure raised. [9](#0-8)

### Citations

**File:** eras/alonzo/impl/src/Cardano/Ledger/Alonzo/Tx.hs (L391-394)
```haskell
  (EraTx era, AlonzoEraTxWits era) =>
  Tx l era ->
  ExUnits
totExUnits tx = foldMap snd $ tx ^. witsTxL . rdmrsTxWitsL . unRedeemersL
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/TxBody.hs (L184-184)
```haskell
    , dtbrSubTransactions :: !(OMap TxId (Tx SubTx era))
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/TxBody.hs (L198-198)
```haskell
    , dstbrScriptIntegrityHash :: !(StrictMaybe ScriptIntegrityHash)
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Bbody.hs (L335-371)
```haskell
dijkstraBbodyTransition = do
  TRC
    ( Shelley.BbodyEnv pp account
      , Shelley.BbodyState ls blocksMade
      , DijkstraBbodySignal block@Block {blockBody}
      ) <-
    judgmentContext

  Shelley.validateBlockBodySize block (pp ^. ppProtocolVersionL)

  Shelley.validateBlockBodyHash block

  let bhSlot = block ^. slotNoBlockHeaderL

  (firstSlot, curEpoch) <- liftSTS $ slotToEpochBoundary bhSlot

  let txs = blockBody ^. txSeqBlockBodyL

  ls' <-
    trans @(EraRule "LEDGERS" era) $
      TRC
        ( Shelley.LedgersEnv bhSlot curEpoch pp account
        , ls
        , fromStrict txs
        )

  Alonzo.validateExUnits @era txs $ pp ^. ppMaxBlockExUnitsL

  Conway.validateBodyRefScriptsSizeTooBig @era pp blockBody (ls ^. utxoL)

  case blockBody ^. perasCertBlockBodyL of
    SNothing -> pure ()
    SJust cert ->
      let nonce = block ^. prevNonceBlockHeaderL
       in validatePerasCert nonce PerasKey cert ?! injectFailure (PerasCertValidationFailed cert nonce)

  pure $ Shelley.BbodyState ls' $ incrBlocks block firstSlot (pp ^. ppDG) blocksMade
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

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs (L414-415)
```haskell
  {- totExunits tx ≤ maxTxExUnits pp -}
  runTest $ Alonzo.validateExUnitsTooBigUTxO pp tx
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Tx.hs (L383-391)
```haskell
  DijkstraStAnnSubTx ::
    { dsastTx :: !(Tx SubTx era)
    , dsastScriptsNeeded :: ScriptsNeeded era
    , dsastScriptsProvided :: ScriptsProvided era
    , dsastTxInfoResult :: TxInfoResult era
    , dsastPlutusLanguagesUsed :: Set Language
    , dsastPlutusScriptsWithContext :: Either (NonEmpty (CollectError era)) [PlutusWithContext]
    } ->
    DijkstraStAnnTx SubTx era
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/SubUtxo.hs (L241-278)
```haskell
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
