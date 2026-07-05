### Title
Sub-Transaction Reference Script Size Excluded from Minimum Fee Calculation in Dijkstra Batch Transactions - (File: eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs)

### Summary

In the Dijkstra era, the minimum fee validation for a batch (top-level + sub-transactions) uses `getConwayMinFeeTxUtxo`, which computes the reference-script size contribution to the fee using only the top-level transaction's reference scripts (`txNonDistinctRefScriptsSize`). The correct function for a batch, `batchNonDistinctRefScriptsSize`, which aggregates reference script sizes across the top-level transaction and all sub-transactions, is defined and exported but never wired into the fee check. An attacker can therefore include arbitrarily large reference scripts exclusively inside sub-transactions, pay a fee computed as if those scripts do not exist, and force every validating node to deserialize them — the exact DDoS vector the tiered reference-script fee was introduced to close.

### Finding Description

The Dijkstra era introduces nested ("sub") transactions. The `EraUTxO DijkstraEra` instance sets:

```haskell
getMinFeeTxUtxo = getConwayMinFeeTxUtxo
```

`getConwayMinFeeTxUtxo` is:

```haskell
getConwayMinFeeTxUtxo pparams tx utxo =
  getMinFeeTx pparams tx $ txNonDistinctRefScriptsSize utxo tx
```

`txNonDistinctRefScriptsSize` inspects only the top-level transaction's spend inputs, reference inputs, and collateral inputs. It is completely unaware of sub-transactions.

The same file defines and exports the correct batch-aware counterpart:

```haskell
batchNonDistinctRefScriptsSize utxo tx =
  txNonDistinctRefScriptsSize utxo tx
    + getSum
      ( foldMap'
          (Sum . txNonDistinctRefScriptsSize utxo)
          (tx ^. bodyTxL . subTransactionsTxBodyL)
      )
```

This function is never called from `getMinFeeTxUtxo` or from the Dijkstra UTXO transition rule. The fee check in the Dijkstra UTXO rule is:

```haskell
{- minfee pp txTop utxo₀ ≤ txfee txb -}
runTest $ Shelley.validateFeeTooSmallUTxO pp tx originalUtxo
```

`validateFeeTooSmallUTxO` calls `getMinFeeTxUtxo pp tx utxo`, which resolves to `getConwayMinFeeTxUtxo` — the top-level-only variant. Sub-transaction reference scripts are therefore invisible to the minimum fee check.

This is structurally identical to the reported Debita bug: the wrong variable (`txNonDistinctRefScriptsSize`, analogous to `offer.maxDeadline`) is used in the accounting formula instead of the correct variable (`batchNonDistinctRefScriptsSize`, analogous to `nextDeadline() - m_loan.startedAt`).

### Impact Explanation

The tiered reference-script fee (introduced in Conway via ADR-9 after the June 2024 DDoS) is the primary on-chain deterrent against submitting transactions that are cheap to include but expensive for nodes to validate. By placing large Plutus reference scripts exclusively in sub-transactions, an attacker pays a fee computed from zero reference-script bytes while forcing every node to deserialize the full batch. The fee paid is outside the design parameters of the protocol: it is lower than the minimum the protocol intends to charge for that amount of deserialization work. This matches the allowed Medium impact: "Attacker-controlled transactions… modify fees… outside design parameters."

### Likelihood Explanation

Any unprivileged transaction sender can craft a `DijkstraTxBody` with an empty top-level reference-input set and one or more sub-transactions whose reference inputs point to UTxO entries carrying large Plutus scripts. No special role, key, or governance action is required. The Dijkstra era is the only era where this attack surface exists, and the discrepancy between the defined-but-unused `batchNonDistinctRefScriptsSize` and the wired-in `txNonDistinctRefScriptsSize` makes the root cause straightforward to exploit once the era is live.

### Recommendation

Replace `getConwayMinFeeTxUtxo` with a Dijkstra-specific override in the `EraUTxO DijkstraEra` instance that uses `batchNonDistinctRefScriptsSize`:

```haskell
getMinFeeTxUtxo pparams tx utxo =
  getMinFeeTx pparams tx $ batchNonDistinctRefScriptsSize utxo tx
```

This ensures the tiered reference-script pricing applies to the total deserialization cost of the entire batch, not just the top-level transaction.

### Proof of Concept

1. Construct a `DijkstraTxBody` whose `dtbSpendInputs`, `dtbReferenceInputs`, and `dtbCollateralInputs` are all empty or minimal (zero reference-script bytes at the top level).
2. Embed one sub-transaction (`dtbSubTransactions`) whose `dstbReferenceInputs` points to a UTxO entry carrying a large Plutus V3 script (e.g., 200 KiB).
3. Set `dtbTxfee` to the value returned by `getConwayMinFeeTxUtxo` — which sees 0 reference-script bytes and therefore charges only the base `a + b * txSize` fee.
4. Submit the transaction. `validateFeeTooSmallUTxO` passes because it calls `getMinFeeTxUtxo = getConwayMinFeeTxUtxo`, which ignores the sub-transaction's 200 KiB reference script.
5. Every validating node must deserialize the 200 KiB script to validate the batch, but the fee collected is orders of magnitude below what the tiered pricing formula would require for that script size. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

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

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs (L372-373)
```haskell
  {- minfee pp txTop utxo₀ ≤ txfee txb -}
  runTest $ Shelley.validateFeeTooSmallUTxO pp tx originalUtxo
```

**File:** docs/adr/2024-08-14_009-refscripts-fee-change.md (L41-60)
```markdown
### Formula for the cost due to reference script usage

Once we have the total size of reference scripts used in a transaction we can proceed to computing the amount of Lovelace that will be added to the fee of a transaction. Instead of using the same linear cost for the whole size we split this total size into `25KiB` chunks and each subsequent chunk will get a linear pricing cost that is higher than the previous one by a multiplier of `1.2`. In other words pricing for the first `25KiB` will be as with the initial approach, just the value of `minFeeRefScriptCostPerByte`. The following `25KiB` will have the price of `minFeeRefScriptCostPerByte * multiplier` and  so on. These are the two new hardcoded values in the fee computation:

* Size increment: `25KiB` (or 25,600 bytes)
* Multiplier: `1.2`
* minFeeRefScriptCostPerByte: `15` (supplied in Conway genesis)

This tiered pricing for reference scripts is defined by this recursive function:

```haskell
tierRefScriptFee :: Integer -> Integer
tierRefScriptFee = go 0 minFeeRefScriptCostPerByte
  where
    go acc curTierPrice n
      | n < sizeIncrement =
          floor (acc + (n % 1) * curTierPrice)
      | otherwise =
          let acc' = acc + curTierPrice * (sizeIncrement % 1)
           in go acc' (multiplier * curTierPrice) (n - sizeIncrement)
```
