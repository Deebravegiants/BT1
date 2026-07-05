### Title
Sub-Transaction Plutus Script Execution Units Excluded from Minimum Fee Calculation - (File: `eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs`)

### Summary
In the Dijkstra era, the minimum fee check applied to a top-level transaction does not account for the Plutus script execution units declared in embedded sub-transactions. An unprivileged sender can construct a top-level transaction with zero or minimal top-level redeemers but include sub-transactions containing arbitrarily expensive Plutus scripts, paying only the byte-size component of the fee while forcing all nodes to execute the sub-transaction scripts without compensation.

### Finding Description

The Dijkstra era introduces nested ("sub") transactions embedded inside a top-level transaction body via `dtbrSubTransactions`. Sub-transactions carry their own witnesses, including redeemers for Plutus scripts.

The minimum fee for a Dijkstra transaction is computed through the following call chain:

`dijkstraUtxoTransition` → `Shelley.validateFeeTooSmallUTxO pp tx originalUtxo` → `getMinFeeTxUtxo pp tx utxo` → `getMinFeeTx pparams tx (txNonDistinctRefScriptsSize utxo tx)` → `alonzoMinFeeTx pp tx <+> refScriptsFee`

The `alonzoMinFeeTx` function is:

```haskell
alonzoMinFeeTx pp tx =
  (tx ^. sizeTxF <×> ...) <+> (pp ^. ppTxFeeFixedL)
    <+> txscriptfee (pp ^. ppPricesL) allExunits
  where
    allExunits = totExUnits tx
```

And `totExUnits` is:

```haskell
totExUnits tx = foldMap snd $ tx ^. witsTxL . rdmrsTxWitsL . unRedeemersL
```

This only reads `tx ^. witsTxL` — the **top-level** transaction's witnesses. Sub-transaction witnesses are stored separately in each `Tx SubTx era` value inside `dtbrSubTransactions` and are never folded into `allExunits`.

Meanwhile, `validateBatchCollateral` explicitly recognises that sub-transactions can have redeemers and that their scripts are executed:

```haskell
hasAnyRedeemers t =
  hasRedeemers t || any hasRedeemers (t ^. bodyTxL . subTransactionsTxBodyL)
hasRedeemers = not . null . (^. witsTxL . rdmrsTxWitsL . unRedeemersL)
```

The existence of the dedicated `DijkstraSUBUTXOW` and `DijkstraSUBUTXO` rules (listed in the Dijkstra CHANGELOG) confirms that sub-transaction Plutus scripts are independently validated and executed. The collateral requirement is triggered by sub-transaction redeemers, but the minimum fee is not.

The result is a structural inconsistency: the collateral path accounts for sub-transaction script execution, but the fee path does not.

### Impact Explanation

An attacker can submit a top-level Dijkstra transaction that declares zero ExUnits in its own redeemers but embeds sub-transactions with redeemers budgeting the maximum allowed ExUnits (`maxTxExUnits`). The `validateFeeTooSmallUTxO` check passes because `totExUnits tx` returns zero (or a small value), so the minimum fee is only the byte-size component. Every validating node must execute all sub-transaction Plutus scripts at full cost without receiving the corresponding script-execution fee. This allows attacker-controlled transactions to modify fees outside design parameters — specifically, to pay a fee that is systematically lower than the actual computation cost imposed on the network.

This maps to the **Medium** allowed impact: *Attacker-controlled transactions modify fees outside design parameters.*

### Likelihood Explanation

Any unprivileged transaction sender can craft such a transaction. No special keys, governance majority, or privileged access is required. The Dijkstra era is the current development frontier, and the sub-transaction fee model is new, making this gap plausible as an oversight rather than an intentional design choice. The collateral check already treating sub-transaction redeemers as cost-bearing is strong evidence the omission from the fee calculation is unintentional.

### Recommendation

Extend `totExUnits` (or introduce a Dijkstra-specific override of `getMinFeeTx`) to also sum the execution units from all sub-transaction redeemers:

```haskell
dijkstraTotExUnits tx =
  totExUnits tx
    <> foldMap totExUnits (OMap.elems $ tx ^. bodyTxL . subTransactionsTxBodyL)
```

Use this aggregate in the Dijkstra minimum fee calculation so that the fee covers the full script execution cost of the entire transaction batch.

### Proof of Concept

**Root cause — `totExUnits` ignores sub-transaction redeemers:** [1](#0-0) 

**`alonzoMinFeeTx` uses only `totExUnits tx` (top-level):** [2](#0-1) 

**Dijkstra UTXO transition calls `validateFeeTooSmallUTxO` with the top-level `tx` only:** [3](#0-2) 

**`validateBatchCollateral` explicitly checks sub-transaction redeemers, confirming they are executed:** [4](#0-3) 

**Sub-transactions carry their own witnesses (including redeemers) in `DijkstraTxBodyRaw`:** [5](#0-4) 

**`DijkstraSubTxBodyRaw` has no fee field, confirming sub-transaction fees are not self-declared and must be covered by the top-level fee — which is currently under-calculated:** [6](#0-5)

### Citations

**File:** eras/alonzo/impl/src/Cardano/Ledger/Alonzo/Tx.hs (L383-388)
```haskell
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

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs (L372-373)
```haskell
  {- minfee pp txTop utxo₀ ≤ txfee txb -}
  runTest $ Shelley.validateFeeTooSmallUTxO pp tx originalUtxo
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/TxBody.hs (L184-184)
```haskell
    , dtbrSubTransactions :: !(OMap TxId (Tx SubTx era))
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
