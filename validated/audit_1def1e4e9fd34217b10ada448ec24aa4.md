### Title
Dijkstra Era `getMinFeeTxUtxo` Under-Accounts Sub-Transaction Reference Script Costs, Allowing Fee Bypass - (File: `eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs`)

---

### Summary

The Dijkstra era introduces nested ("sub") transactions. The minimum fee calculation for a top-level Dijkstra transaction uses `getConwayMinFeeTxUtxo`, which calls `txNonDistinctRefScriptsSize` — a function that only measures reference script sizes from the **top-level** transaction's inputs. Sub-transactions can carry their own `referenceInputs` pointing to UTxOs with large reference scripts, but those sizes are never added to the fee. A helper function `batchNonDistinctRefScriptsSize` was explicitly written to aggregate reference script sizes across the top-level transaction and all sub-transactions, but it is never wired into the fee enforcement path. As a result, an unprivileged sender can submit a Dijkstra transaction whose sub-transactions reference arbitrarily large scripts while paying a fee that is lower than the protocol intends.

---

### Finding Description

**Root cause — `getMinFeeTxUtxo` delegates to the Conway implementation unchanged:** [1](#0-0) 

`DijkstraEra` sets `getMinFeeTxUtxo = getConwayMinFeeTxUtxo`. That Conway function is: [2](#0-1) 

It passes `txNonDistinctRefScriptsSize utxo tx` as the reference-script-size argument to `getMinFeeTx`. That function only unions the top-level transaction's `referenceInputsTxBodyL` and `inputsTxBodyL`: [3](#0-2) 

**Sub-transactions have their own `referenceInputs` field:** [4](#0-3) 

`dstbrReferenceInputs` is a full `Set TxIn` that can point to UTxOs carrying large reference scripts. These inputs are never visited by `txNonDistinctRefScriptsSize`.

**The correct aggregation function exists but is unused:** [5](#0-4) 

`batchNonDistinctRefScriptsSize` sums `txNonDistinctRefScriptsSize` over the top-level transaction and every sub-transaction. It is exported from the module but never called from `getMinFeeTxUtxo` or any fee-enforcement rule.

**The fee check in the Dijkstra UTXO rule calls `validateFeeTooSmallUTxO`, which internally calls `getMinFeeTxUtxo`:** [6](#0-5) 

Because `getMinFeeTxUtxo` returns an under-counted minimum fee, `validateFeeTooSmallUTxO` accepts transactions whose actual reference-script overhead is not covered by the declared fee.

**Secondary under-accounting — sub-transaction ExUnits are also excluded from `totExUnits`:** [7](#0-6) 

`totExUnits` folds only over the top-level transaction's redeemers. Sub-transactions carry their own witnesses (including redeemers with declared `ExUnits`), so the script-fee component `txscriptfee prices (totExUnits tx)` inside `alonzoMinFeeTx` also under-counts execution costs. The same `totExUnits` is used in `validateExUnitsTooBigUTxO`: [8](#0-7) 

and in the block-level check: [9](#0-8) 

meaning both `maxTxExUnits` and `maxBlockExUnits` can be exceeded by distributing scripts across sub-transactions.

---

### Impact Explanation

An unprivileged transaction sender can craft a Dijkstra top-level transaction whose sub-transactions reference UTxOs containing large Plutus scripts via `referenceInputs`. The ledger's fee check passes because `minfee` is computed without those reference script sizes. The sender pays a fee that is lower than the protocol intends, violating the fee design parameters. The same structural gap allows the declared ExUnits across sub-transactions to exceed `maxTxExUnits` without triggering the per-transaction limit, and the sum across all transactions in a block to exceed `maxBlockExUnits` without triggering the block limit. This maps to the allowed impact: **"Attacker-controlled transactions modify fees outside design parameters"** (Medium) and **"exceed intended validation limits"** (Medium).

---

### Likelihood Explanation

The Dijkstra era is the only era with sub-transactions. Any Dijkstra transaction that places reference inputs in sub-transactions triggers the under-accounting. No special privilege is required — any transaction sender can construct such a transaction. The `batchNonDistinctRefScriptsSize` function being defined but unused is a strong indicator that the gap was not intentional.

---

### Recommendation

1. Override `getMinFeeTxUtxo` in the `EraUTxO DijkstraEra` instance to use a Dijkstra-specific implementation that calls `batchNonDistinctRefScriptsSize` instead of `txNonDistinctRefScriptsSize`:

```haskell
getDijkstraMinFeeTxUtxo :: (EraTx era, DijkstraEraTxBody era) => PParams era -> Tx TopTx era -> UTxO era -> Coin
getDijkstraMinFeeTxUtxo pparams tx utxo =
  getMinFeeTx pparams tx $ batchNonDistinctRefScriptsSize utxo tx
```

2. Define a `dijkstraTotExUnits` that folds over both the top-level transaction's redeemers and each sub-transaction's redeemers, and use it in `validateExUnitsTooBigUTxO` and `validateExUnits` for the Dijkstra era.

3. Add a block-level check that sums ExUnits across all sub-transactions of all transactions in the block against `maxBlockExUnits`.

---

### Proof of Concept

1. Deploy a UTxO `U` containing a large Plutus reference script (e.g., 50 KiB).
2. Construct a Dijkstra top-level transaction `T` with an empty `referenceInputsTxBodyL` and `inputsTxBodyL` (no reference scripts at the top level).
3. Add a sub-transaction `S` to `T` with `dstbrReferenceInputs = {U}`.
4. Set `T`'s fee to `minfee pp T utxo` as computed by the current (buggy) `getConwayMinFeeTxUtxo`, which returns a fee that ignores `U`'s 50 KiB script.
5. Submit `T`. The `validateFeeTooSmallUTxO` check passes because `minfee` is under-counted. The transaction is accepted with a fee that does not cover the reference script overhead that the protocol intends to charge, violating the fee design parameters established by `minFeeRefScriptCostPerByte`. [10](#0-9) [5](#0-4) [11](#0-10) [6](#0-5)

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

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/TxBody.hs (L189-209)
```haskell
  DijkstraSubTxBodyRaw ::
    { dstbrSpendInputs :: !(Set TxIn)
    , dstbrReferenceInputs :: !(Set TxIn)
    , dstbrOutputs :: !(StrictSeq (Sized (TxOut era)))
    , dstbrCerts :: !(OSet.OSet (TxCert era))
    , dstbrWithdrawals :: !Withdrawals
    , dstbrVldt :: !ValidityInterval
    , dstbrGuards :: !(OSet (Credential Guard))
    , dstbrMint :: !MultiAsset
    , dstbrScriptIntegrityHash :: !(StrictMaybe ScriptIntegrityHash)
    , dstbrAuxDataHash :: !(StrictMaybe TxAuxDataHash)
    , dstbrNetworkId :: !(StrictMaybe Network)
    , dstbrVotingProcedures :: !(VotingProcedures era)
    , dstbrProposalProcedures :: !(OSet.OSet (ProposalProcedure era))
    , dstbrCurrentTreasuryValue :: !(StrictMaybe Coin)
    , dstbrTreasuryDonation :: !Coin
    , dstbrRequiredTopLevelGuards :: !(Map (Credential Guard) (StrictMaybe (Data era)))
    , dstbrDirectDeposits :: !DirectDeposits
    , dstbrAccountBalanceIntervals :: !(AccountBalanceIntervals era)
    } ->
    DijkstraTxBodyRaw SubTx era
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs (L372-373)
```haskell
  {- minfee pp txTop utxo₀ ≤ txfee txb -}
  runTest $ Shelley.validateFeeTooSmallUTxO pp tx originalUtxo
```

**File:** eras/alonzo/impl/src/Cardano/Ledger/Alonzo/Tx.hs (L390-394)
```haskell
totExUnits ::
  (EraTx era, AlonzoEraTxWits era) =>
  Tx l era ->
  ExUnits
totExUnits tx = foldMap snd $ tx ^. witsTxL . rdmrsTxWitsL . unRedeemersL
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

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Bbody.hs (L361-361)
```haskell
  Alonzo.validateExUnits @era txs $ pp ^. ppMaxBlockExUnitsL
```
