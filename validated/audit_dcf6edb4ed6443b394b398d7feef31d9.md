### Title
Block-Level Reference Script Size Check Omits Dijkstra Subtransaction Reference Scripts - (File: `eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs`)

---

### Summary

In the Dijkstra era, the per-block reference script size validation (`validateBodyRefScriptsSizeTooBig`) uses `totalRefScriptSizeInBlock`, which calls `txNonDistinctRefScriptsSize` on each top-level transaction only. It does not account for reference scripts embedded in subtransactions (`dtbrSubTransactions`). A dedicated batch-aware function, `batchNonDistinctRefScriptsSize`, exists and is correctly used for the per-transaction check, but the per-block check was never updated to use it. An unprivileged sender can therefore craft Dijkstra transactions whose subtransactions collectively carry reference script data far exceeding `maxRefScriptSizePerBlock`, forcing every validating node to deserialize that data without the block-level guard triggering.

---

### Finding Description

**Dijkstra nested-transaction model.** The Dijkstra era adds a `dtbrSubTransactions :: OMap TxId (Tx SubTx era)` field to the top-level transaction body. Each subtransaction is a full ledger-level transaction with its own spend inputs, reference inputs, certificates, governance actions, and witnesses. [1](#0-0) 

**Per-transaction check (correct).** `validateAllRefScriptSize` in the Dijkstra LEDGER rule calls `batchNonDistinctRefScriptsSize`, which sums `txNonDistinctRefScriptsSize` over the top-level transaction *and* every subtransaction, then compares the total against `maxRefScriptSizePerTx`. [2](#0-1) [3](#0-2) 

**Per-block check (incomplete).** `validateBodyRefScriptsSizeTooBig` in the Conway BBODY rule (inherited by Dijkstra) calls `totalRefScriptSizeInBlock`, which iterates over the sequence of top-level transactions and calls `txNonDistinctRefScriptsSize` on each one. `txNonDistinctRefScriptsSize` only inspects `referenceInputsTxBodyL ∪ inputsTxBodyL` of the top-level body — it never descends into `subTransactionsTxBodyL`. [4](#0-3) [5](#0-4) [6](#0-5) 

**Consequence.** If an attacker places all reference scripts inside subtransactions (keeping the top-level body's own inputs free of reference scripts), `totalRefScriptSizeInBlock` returns 0 for those transactions regardless of how many bytes of scripts the subtransactions actually reference. The block-level guard `maxRefScriptSizePerBlock` (1 MiB in Conway/Dijkstra genesis) is therefore never triggered for subtransaction reference scripts.

The per-transaction guard still fires: each batch is capped at `maxRefScriptSizePerTx` (200 KiB). But a block can contain many such batches. With the block guard blind to subtransaction scripts, a block can carry `N × 200 KiB` of subtransaction reference-script data — far above the intended 1 MiB block cap — as long as `N` transactions fit within `maxBBSize`.

---

### Impact Explanation

The reference-script size limits were introduced specifically after a June 2024 DDoS attack to bound the deserialization cost imposed on every validating node per block. [7](#0-6) 

By bypassing `maxRefScriptSizePerBlock`, an attacker forces every honest node to deserialize an unbounded volume of reference-script bytes per block. This matches the **Medium** allowed impact: *attacker-controlled transactions exceed intended validation limits*.

---

### Likelihood Explanation

- Any unprivileged user can submit a Dijkstra top-level transaction containing subtransactions with large reference inputs.
- No governance majority, leaked key, or consensus threshold is required.
- The attacker pays normal transaction fees, but the deserialization cost imposed on nodes scales with the total reference-script bytes, not with the fee.
- The Dijkstra era is production-targeted; the `dtbrSubTransactions` field is already serializable and decodable. [8](#0-7) 

---

### Recommendation

Replace the call to `txNonDistinctRefScriptsSize` inside `totalRefScriptSizeInBlock` (or its Dijkstra-era equivalent) with a dispatch that calls `batchNonDistinctRefScriptsSize` when the transaction is a Dijkstra top-level transaction (i.e., when `subTransactionsTxBodyL` is non-empty). Alternatively, define a Dijkstra-specific override of `validateBodyRefScriptsSizeTooBig` that uses `batchNonDistinctRefScriptsSize` for every transaction in the block sequence, mirroring the per-transaction check already in place. [9](#0-8) 

---

### Proof of Concept

1. Deploy N UTxO entries each holding a large Plutus script as a reference script (total per subtransaction ≤ `maxRefScriptSizePerTx` = 200 KiB).
2. Craft a Dijkstra top-level transaction whose `dtbrSubTransactions` map contains K subtransactions, each referencing those UTxO entries via `dstbrReferenceInputs`. Keep the top-level body's own `dtbrReferenceInputs` and `dtbrSpendInputs` free of reference scripts.
3. `validateAllRefScriptSize` passes because `batchNonDistinctRefScriptsSize` ≤ 200 KiB per batch.
4. Submit multiple such transactions in a single block. `totalRefScriptSizeInBlock` returns 0 for each (no top-level reference scripts), so `validateBodyRefScriptsSizeTooBig` never fires.
5. Each validating node must deserialize `M × K × (script bytes)` of reference-script data for the block, where M is the number of such transactions — potentially many multiples of the intended 1 MiB block cap. [10](#0-9)

### Citations

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/TxBody.hs (L163-188)
```haskell
data DijkstraTxBodyRaw l era where
  DijkstraTxBodyRaw ::
    { dtbrSpendInputs :: !(Set TxIn)
    , dtbrCollateralInputs :: !(Set TxIn)
    , dtbrReferenceInputs :: !(Set TxIn)
    , dtbrOutputs :: !(StrictSeq (Sized (TxOut era)))
    , dtbrCollateralReturn :: !(StrictMaybe (Sized (TxOut era)))
    , dtbrTotalCollateral :: !(StrictMaybe Coin)
    , dtbrCerts :: !(OSet.OSet (TxCert era))
    , dtbrWithdrawals :: !Withdrawals
    , dtbrFee :: !Coin
    , dtbrVldt :: !ValidityInterval
    , dtbrGuards :: !(OSet (Credential Guard))
    , dtbrMint :: !MultiAsset
    , dtbrScriptIntegrityHash :: !(StrictMaybe ScriptIntegrityHash)
    , dtbrAuxDataHash :: !(StrictMaybe TxAuxDataHash)
    , dtbrNetworkId :: !(StrictMaybe Network)
    , dtbrVotingProcedures :: !(VotingProcedures era)
    , dtbrProposalProcedures :: !(OSet.OSet (ProposalProcedure era))
    , dtbrCurrentTreasuryValue :: !(StrictMaybe Coin)
    , dtbrTreasuryDonation :: !Coin
    , dtbrSubTransactions :: !(OMap TxId (Tx SubTx era))
    , dtbrDirectDeposits :: !DirectDeposits
    , dtbrAccountBalanceIntervals :: !(AccountBalanceIntervals era)
    } ->
    DijkstraTxBodyRaw TopTx era
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

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Bbody.hs (L329-355)
```haskell
-- | Validate that total reference script size does not exceed block limit.
validateBodyRefScriptsSizeTooBig ::
  forall era.
  ( AlonzoEraTx era
  , BabbageEraTxBody era
  , InjectRuleFailure "BBODY" ConwayBbodyPredFailure era
  , EraBlockBody era
  , ConwayEraPParams era
  ) =>
  PParams era ->
  BlockBody era ->
  UTxO era ->
  Rule (EraRule "BBODY" era) 'Transition ()
validateBodyRefScriptsSizeTooBig pp blockBody utxo =
  let protVer = pp ^. ppProtocolVersionL
      txs = blockBody ^. txSeqBlockBodyL
      totalSize = totalRefScriptSizeInBlock protVer txs utxo
      maxSize = fromIntegral @Word32 @Int $ pp ^. ppMaxRefScriptSizePerBlockG
   in totalSize
        <= maxSize
          ?! injectFailure
            ( BodyRefScriptsSizeTooBig $
                Mismatch
                  { mismatchSupplied = totalSize
                  , mismatchExpected = maxSize
                  }
            )
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Bbody.hs (L357-370)
```haskell
totalRefScriptSizeInBlock ::
  (AlonzoEraTx era, BabbageEraTxBody era) => ProtVer -> StrictSeq (Tx TopTx era) -> UTxO era -> Int
totalRefScriptSizeInBlock protVer txs (UTxO utxo)
  | pvMajor protVer <= natVersion @10 =
      getSum $ foldMap' (Monoid.Sum . txNonDistinctRefScriptsSize (UTxO utxo)) txs
  | otherwise =
      snd $ F.foldl' accum (utxo, 0) txs
  where
    accum (!accUtxo, !accSum) tx =
      let updatedUtxo = accUtxo `Map.union` unUTxO toAdd
          toAdd
            | IsValid True <- tx ^. isValidTxL = txouts $ tx ^. bodyTxL
            | otherwise = collOuts $ tx ^. bodyTxL
       in (updatedUtxo, accSum + txNonDistinctRefScriptsSize (UTxO accUtxo) tx)
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
