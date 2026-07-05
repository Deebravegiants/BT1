### Title
Sub-Transaction Reference Script Sizes Excluded from Minimum Fee Calculation in Dijkstra Era — (File: `eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs`)

---

### Summary

The Dijkstra era's `getMinFeeTxUtxo` reuses `getConwayMinFeeTxUtxo`, which only measures reference-script bytes from the **top-level** transaction. Sub-transactions embedded in a Dijkstra batch can carry their own reference inputs pointing to large scripts, but those bytes are never added to the fee calculation. The helper `batchNonDistinctRefScriptsSize` — which correctly aggregates all levels — exists in the same file but is not wired into the fee check, leaving a systematic underpayment path that bypasses the tiered ref-script pricing mechanism.

---

### Finding Description

In `eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs`, the `EraUTxO DijkstraEra` instance sets:

```haskell
getMinFeeTxUtxo = getConwayMinFeeTxUtxo
``` [1](#0-0) 

`getConwayMinFeeTxUtxo` (Conway UTxO) computes the minimum fee by passing only the **top-level** transaction's reference-script byte count to `getMinFeeTx`:

```haskell
getConwayMinFeeTxUtxo pparams tx utxo =
  getMinFeeTx pparams tx $ txNonDistinctRefScriptsSize utxo tx
``` [2](#0-1) 

`getMinFeeTx` for both Conway and Dijkstra is `getConwayMinFeeTx`, which feeds that size into `tierRefScriptFee` — the exponential pricing function introduced after the June 2024 DDoS:

```haskell
getConwayMinFeeTx pp tx refScriptsSize =
  alonzoMinFeeTx pp tx <+> refScriptsFee
  where
    refScriptsFee = tierRefScriptFee ... refScriptsSize
``` [3](#0-2) 

In the Dijkstra era, a top-level transaction can embed sub-transactions via `subTransactionsTxBodyL`. Each sub-transaction has its own `referenceInputsTxBodyL`, which can point to UTxO entries containing large Plutus reference scripts. The same `UTxO.hs` file defines a function that correctly aggregates all levels:

```haskell
batchNonDistinctRefScriptsSize utxo tx =
  txNonDistinctRefScriptsSize utxo tx
    + getSum
        ( foldMap'
            (Sum . txNonDistinctRefScriptsSize utxo)
            (tx ^. bodyTxL . subTransactionsTxBodyL)
        )
``` [4](#0-3) 

`batchNonDistinctRefScriptsSize` is exported from the module but is **never called** from `getMinFeeTxUtxo`. The fee validation in `dijkstraUtxoTransition` therefore only enforces a fee covering the top-level transaction's reference scripts:

```haskell
{- minfee pp txTop utxo₀ ≤ txfee txb -}
runTest $ Shelley.validateFeeTooSmallUTxO pp tx originalUtxo
``` [5](#0-4) 

The sub-transaction UTxO rule (`dijkstraSubUtxoTransition`) performs no fee check at all — `FeeTooSmallUTxO` is explicitly listed as `"Impossible"` for `SUBUTXO`: [6](#0-5) 

The unit-mismatch analogy to the external report is direct: `refundPostOpCost` (a raw gas quantity) was added to `actualGasCost` (a cost in ETH) without multiplying by the gas price. Here, sub-transaction reference-script **sizes** (raw bytes) are added to the fee calculation with an implicit multiplier of **zero** instead of the correct `tierRefScriptFee` price, because `batchNonDistinctRefScriptsSize` is never invoked.

---

### Impact Explanation

An unprivileged transaction sender can craft a Dijkstra top-level transaction with zero or minimal top-level reference inputs (keeping the declared fee low) while embedding sub-transactions that each reference large Plutus scripts stored in the UTxO. The ledger accepts the transaction because `validateFeeTooSmallUTxO` passes — it only measures top-level ref-script bytes. The node must nonetheless deserialize every sub-transaction reference script during validation, incurring computational cost not covered by the fee.

This directly bypasses the tiered `tierRefScriptFee` pricing mechanism introduced in Conway specifically to prevent DDoS via large reference-script deserialization (ADR-009). The impact matches the **Medium** allowed scope: *"Attacker-controlled transactions… modify fees… outside design parameters."* [7](#0-6) 

---

### Likelihood Explanation

- No special privileges are required; any user who can submit a Dijkstra-era transaction can exploit this.
- The attack vector is identical in class to the June 25th 2024 mainnet DDoS (documented in ADR-009), which exploited missing fee coverage for reference-script deserialization.
- The existence of `batchNonDistinctRefScriptsSize` in the same file as `getMinFeeTxUtxo` — exported but unused in the fee path — is strong evidence of an incomplete wiring rather than an intentional design choice.
- The Dijkstra era is the current development head; exploitation becomes possible upon deployment.

---

### Recommendation

Override `getMinFeeTxUtxo` in the `EraUTxO DijkstraEra` instance to use `batchNonDistinctRefScriptsSize` instead of the Conway single-level variant:

```haskell
-- eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs
instance EraUTxO DijkstraEra where
  ...
  getMinFeeTxUtxo pp tx utxo =
    getMinFeeTx pp tx $ batchNonDistinctRefScriptsSize utxo tx
```

This ensures `tierRefScriptFee` is applied to the **total** reference-script byte count across the top-level transaction and all sub-transactions, consistent with the intent expressed by `batchNonDistinctRefScriptsSize`.

---

### Proof of Concept

1. Identify a UTxO entry containing a large Plutus reference script (e.g., 100 KB, well within `maxRefScriptSizePerTx`).
2. Construct a Dijkstra top-level transaction with:
   - **No** reference inputs at the top level → `txNonDistinctRefScriptsSize` returns 0 → ref-script fee component = 0.
   - One or more sub-transactions, each with `referenceInputsTxBodyL` pointing to the large-script UTxO entry.
3. Set `feeTxBodyL` to the minimum computed by `getConwayMinFeeTxUtxo` (which ignores sub-transaction ref scripts).
4. Submit. `validateFeeTooSmallUTxO` passes because it only checks top-level ref scripts.
5. The node deserializes the large reference scripts for sub-transaction validation, incurring `tierRefScriptFee`-priced cost that is entirely uncompensated by the fee.

The discrepancy between the fee paid and the fee that `batchNonDistinctRefScriptsSize` would have required grows with the size and number of sub-transaction reference scripts, enabling a low-cost, high-impact resource exhaustion attack.

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

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Tx.hs (L103-112)
```haskell
getConwayMinFeeTx pp tx refScriptsSize =
  alonzoMinFeeTx pp tx <+> refScriptsFee
  where
    refScriptCostPerByte = unboundRational (pp ^. ppMinFeeRefScriptCostPerByteL)
    refScriptsFee =
      tierRefScriptFee
        (unboundRational $ pp ^. ppRefScriptCostMultiplierG)
        (fromIntegral @Word32 @Int . unNonZero $ pp ^. ppRefScriptCostStrideG)
        refScriptCostPerByte
        refScriptsSize
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs (L372-373)
```haskell
  {- minfee pp txTop utxo₀ ≤ txfee txb -}
  runTest $ Shelley.validateFeeTooSmallUTxO pp tx originalUtxo
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/SubUtxo.hs (L332-332)
```haskell
  FeeTooSmallUTxO _ -> error "Impossible: `FeeTooSmallUTxO` for SUBUTXO"
```

**File:** docs/adr/2024-08-14_009-refscripts-fee-change.md (L15-19)
```markdown
It was identified a while ago that there is an overhead associated with deserializing scripts, so much so that it would be possible to create a very large script that was fairly expensive to deserialize, but very cheap to execute. This opened up an attack vector when such a Plutus script would be used as a reference script. This problem was exacerbated by the fact that there was no real limit on the total size of reference scripts that could be used in a transaction, thus being limited only by the size of the transaction itself. Therefore this opened up Cardano to a DDoS attack where an attacker could submit many such transactions that would cost very little, but would be expensive for a `cardano-node` to validate.

In order to prevent such an attack a `"minFeeRefScriptCostPerByte"` protocol parameter was introduced in the Conway era. The idea was fairly simple: we would calculate the total size of reference scripts used by a transaction and multiply it by the value specified by this protocol parameter. Result would be added to the transaction fee. However, in order for this approach to be a definite deterrent of such attacks this parameter would have to be set to a fairly high value. Community was not very keen on having this value set to a high enough value, since that could make reference scripts almost as expensive to use as regular scripts, thus significantly reducing their usability. Taking this fact into consideration, a decision was made to set this parameter to a fairly moderate value to at l ... (truncated)

Unfortunately things did not go exactly as planned, because on [June 25th 2024 an attack like this actually took place](https://cardanospot.io/news/ddos-attack-on-the-cardano-blockchain-mRIKAzZTNnzq5NGd). This attack forced us to make a quick decision on implementing a definite prevention of such attacks, while trying to not have a drastic impact on the common use case that DApp developers rely on so much.
```
