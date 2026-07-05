### Title
Sub-Transaction Reference Script Fees Not Included in Dijkstra Minimum Fee Calculation - (File: `eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs`)

### Summary
The Dijkstra era introduces batch transactions with embedded sub-transactions. A helper function `batchNonDistinctRefScriptsSize` exists to aggregate reference script sizes across both the top-level transaction and all sub-transactions, but the `getMinFeeTxUtxo` method for `DijkstraEra` is bound to `getConwayMinFeeTxUtxo`, which only counts reference scripts from the top-level transaction body. Reference scripts attached to sub-transaction inputs are never counted in the minimum fee calculation, allowing an attacker to include arbitrarily large reference scripts in sub-transactions without paying the corresponding tiered fee.

### Finding Description

The `EraUTxO DijkstraEra` instance sets:

```haskell
getMinFeeTxUtxo = getConwayMinFeeTxUtxo
``` [1](#0-0) 

`getConwayMinFeeTxUtxo` computes the reference script size by calling `txNonDistinctRefScriptsSize`, which only inspects the top-level transaction's `inputsTxBodyL` and `referenceInputsTxBodyL`:

```haskell
getConwayMinFeeTxUtxo pparams tx utxo =
  getMinFeeTx pparams tx $ txNonDistinctRefScriptsSize utxo tx
``` [2](#0-1) 

```haskell
txNonDistinctRefScriptsSize utxo tx = getSum $ foldMap (Sum . originalBytesSize . snd) refScripts
  where
    inputs = (tx ^. bodyTxL . referenceInputsTxBodyL) `Set.union` (tx ^. bodyTxL . inputsTxBodyL)
    refScripts = getReferenceScriptsNonDistinct utxo inputs
``` [3](#0-2) 

The Dijkstra-specific function `batchNonDistinctRefScriptsSize` was written precisely to aggregate reference script sizes across the top-level transaction **and** all sub-transactions:

```haskell
batchNonDistinctRefScriptsSize utxo tx =
  txNonDistinctRefScriptsSize utxo tx
    + getSum
      ( foldMap'
          (Sum . txNonDistinctRefScriptsSize utxo)
          (tx ^. bodyTxL . subTransactionsTxBodyL)
      )
``` [4](#0-3) 

`batchNonDistinctRefScriptsSize` is exported from the module but is never called by `getMinFeeTxUtxo`. As a result, the reference script fee contribution from every sub-transaction is always zero — an exact structural analog to the reported `*=` vs `=` bug, where a zero-initialized accumulator is never correctly populated.

The tiered reference-script fee (`tierRefScriptFee`) was introduced specifically to deter DDoS attacks via large, cheap-to-submit but expensive-to-validate scripts (ADR-009): [5](#0-4) [6](#0-5) 

### Impact Explanation

An unprivileged transaction author can craft a Dijkstra batch transaction whose top-level body carries no reference scripts (or small ones) while embedding sub-transactions that each reference large Plutus scripts. The `FeeTooSmallUTxO` check passes because `getMinFeeTxUtxo` only measures the top-level reference script size. The attacker pays only the base linear fee, while every validating node must deserialize and process the full set of large reference scripts from all sub-transactions. This directly undermines the fee-based deterrent against the reference-script DDoS vector that was exploited on mainnet in June 2024.

**Impact class:** Medium — attacker-controlled transactions modify fees outside design parameters.

### Likelihood Explanation

The Dijkstra era is the current development head. Any transaction author can submit a batch transaction with sub-transactions containing large reference scripts. No privileged access, governance majority, or key compromise is required. The only prerequisite is that the Dijkstra era is active on the target network.

### Recommendation

Replace `getConwayMinFeeTxUtxo` with a Dijkstra-specific implementation that uses `batchNonDistinctRefScriptsSize` instead of `txNonDistinctRefScriptsSize`:

```haskell
getDijkstraMinFeeTxUtxo ::
  ( EraTx era
  , DijkstraEraTxBody era
  ) =>
  PParams era ->
  Tx l era ->
  UTxO era ->
  Coin
getDijkstraMinFeeTxUtxo pparams tx utxo =
  getMinFeeTx pparams tx $ batchNonDistinctRefScriptsSize utxo tx
```

Then update the `EraUTxO DijkstraEra` instance:

```haskell
getMinFeeTxUtxo = getDijkstraMinFeeTxUtxo
``` [1](#0-0) 

### Proof of Concept

1. Construct a Dijkstra `TopTx` whose top-level body has no reference inputs.
2. Embed N sub-transactions, each with `referenceInputsTxBodyL` pointing to UTxO entries that carry large Plutus V3 scripts (e.g., 25 KiB each).
3. Set the transaction fee to the value returned by `getMinFeeTxUtxo` (which calls `txNonDistinctRefScriptsSize` on the top-level body only → 0 bytes of reference scripts → no tiered surcharge).
4. Submit the transaction. The `FeeTooSmallUTxO` predicate passes because the minimum fee is computed without the sub-transaction reference scripts.
5. Every validating node must deserialize all N × 25 KiB reference scripts, incurring O(N) deserialization cost at O(1) fee cost to the attacker.

The discrepancy between `batchNonDistinctRefScriptsSize` (correct, unused) and `txNonDistinctRefScriptsSize` (incomplete, used) is the root cause, directly mirroring the `*=` vs `=` pattern in the reported `getFundingFee` bug. [7](#0-6) [8](#0-7)

### Citations

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs (L141-141)
```haskell
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

**File:** docs/adr/2024-08-14_009-refscripts-fee-change.md (L15-19)
```markdown
It was identified a while ago that there is an overhead associated with deserializing scripts, so much so that it would be possible to create a very large script that was fairly expensive to deserialize, but very cheap to execute. This opened up an attack vector when such a Plutus script would be used as a reference script. This problem was exacerbated by the fact that there was no real limit on the total size of reference scripts that could be used in a transaction, thus being limited only by the size of the transaction itself. Therefore this opened up Cardano to a DDoS attack where an attacker could submit many such transactions that would cost very little, but would be expensive for a `cardano-node` to validate.

In order to prevent such an attack a `"minFeeRefScriptCostPerByte"` protocol parameter was introduced in the Conway era. The idea was fairly simple: we would calculate the total size of reference scripts used by a transaction and multiply it by the value specified by this protocol parameter. Result would be added to the transaction fee. However, in order for this approach to be a definite deterrent of such attacks this parameter would have to be set to a fairly high value. Community was not very keen on having this value set to a high enough value, since that could make reference scripts almost as expensive to use as regular scripts, thus significantly reducing their usability. Taking this fact into consideration, a decision was made to set this parameter to a fairly moderate value to at l ... (truncated)

Unfortunately things did not go exactly as planned, because on [June 25th 2024 an attack like this actually took place](https://cardanospot.io/news/ddos-attack-on-the-cardano-blockchain-mRIKAzZTNnzq5NGd). This attack forced us to make a quick decision on implementing a definite prevention of such attacks, while trying to not have a drastic impact on the common use case that DApp developers rely on so much.
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Tx.hs (L116-136)
```haskell
tierRefScriptFee ::
  HasCallStack =>
  -- | Growth factor or step multiplier
  Rational ->
  -- | Increment size in which price grows linearly according to the price
  Int ->
  -- | Base fee. Currently this is customizable by `ppMinFeeRefScriptCostPerByteL`
  Rational ->
  -- | Total RefScript size in bytes
  Int ->
  Coin
tierRefScriptFee multiplier sizeIncrement
  | multiplier <= 0 || sizeIncrement <= 0 = error "Size increment and multiplier must be positive"
  | otherwise = go 0
  where
    go !acc !curTierPrice !n
      | n < sizeIncrement =
          Coin $ floor (acc + toRational n * curTierPrice)
      | otherwise =
          go (acc + sizeIncrementRational * curTierPrice) (multiplier * curTierPrice) (n - sizeIncrement)
    sizeIncrementRational = toRational sizeIncrement
```
