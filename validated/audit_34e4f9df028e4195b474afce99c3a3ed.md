### Title
Block-Level Reference Script Size Limit Bypass via Intra-Block UTxO State Inconsistency in `totalRefScriptSizeInBlock` - (File: `eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Bbody.hs`)

### Summary

In Conway era at protocol version ≤ 10, the block-level reference script size check (`validateBodyRefScriptsSizeTooBig`) computes the total reference script size using the **initial UTxO state** at the start of the block, not the incrementally updated UTxO. An attacker can create reference-script-bearing UTxOs in one transaction and consume them as reference inputs in subsequent transactions within the same block, causing the block-level limit to count zero bytes for those inputs while the node still performs the full deserialization work. This bypasses the 1 MiB per-block hard cap introduced to prevent the reference-script DDoS class of attack.

### Finding Description

**Root cause.** `totalRefScriptSizeInBlock` in `eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Bbody.hs` has two code paths gated on protocol version:

```haskell
totalRefScriptSizeInBlock protVer txs (UTxO utxo)
  | pvMajor protVer <= natVersion @10 =
      getSum $ foldMap' (Monoid.Sum . txNonDistinctRefScriptsSize (UTxO utxo)) txs
  | otherwise =
      snd $ F.foldl' accum (utxo, 0) txs
  where
    accum (!accUtxo, !accSum) tx =
      let updatedUtxo = accUtxo `Map.union` unUTxO toAdd
          ...
       in (updatedUtxo, accSum + txNonDistinctRefScriptsSize (UTxO accUtxo) tx)
``` [1](#0-0) 

For protocol version ≤ 10 (valid within Conway era, whose `ProtVerLow = 9` and `ProtVerHigh = 11`), the function folds over all transactions using the **same fixed initial UTxO** for every call to `txNonDistinctRefScriptsSize`. The `otherwise` branch (version ≥ 11) correctly threads the UTxO forward, accumulating outputs from each applied transaction before measuring the next.

**Block-level check call site.** `validateBodyRefScriptsSizeTooBig` is called with `ls ^. utxoL`, the ledger state UTxO at the start of the block, before any transaction in the block has been applied:

```haskell
validateBodyRefScriptsSizeTooBig @era pp blockBody (ls ^. utxoL)
``` [2](#0-1) 

**Hardcoded limits.** The Conway era implements `ppMaxRefScriptSizePerTxG` and `ppMaxRefScriptSizePerBlockG` as hardcoded constants (not updatable protocol parameters), as acknowledged in the ADR:

```haskell
ppMaxRefScriptSizePerTxG    = L.to . const $ 200 * 1024   -- 200 KiB per tx
ppMaxRefScriptSizePerBlockG = L.to . const $ 1024 * 1024  -- 1 MiB per block
``` [3](#0-2) 

**Exploit path.**

1. Attacker submits transaction **T1** that creates N UTxO outputs, each carrying a reference script of size S ≤ 200 KiB. T1 itself uses no reference inputs, so it passes the per-transaction check (`validateRefScriptSize`).
2. Attacker submits transactions **T2 … T(N+1)**, each spending a regular input and listing one of T1's outputs as a reference input (S bytes each). Each passes the per-tx check because S ≤ 200 KiB.
3. A block producer includes T1 … T(N+1) in the same block.
4. `validateBodyRefScriptsSizeTooBig` runs with the initial UTxO. T1's outputs do not yet exist in that UTxO, so `txNonDistinctRefScriptsSize` returns 0 for T2 … T(N+1). The block-level check sees 0 bytes and passes.
5. The LEDGERS rule then applies T1 (creating the UTxOs), then T2 … T(N+1) sequentially. Each per-tx check passes because S ≤ 200 KiB.
6. The block is accepted. The node has deserialized N × S bytes of reference scripts — exceeding the 1 MiB block cap when N × S > 1 MiB (e.g., N = 6, S = 200 KiB → 1.2 MiB).

The per-tx check (`validateRefScriptSize` in the LEDGER rule) correctly uses the incrementally updated UTxO and catches individual transactions exceeding 200 KiB, but it cannot enforce the aggregate block-level cap when the block-level check is blind to intra-block UTxO changes. [4](#0-3) 

### Impact Explanation

**Medium.** Attacker-controlled transactions exceed the intended block-level reference script size validation limit. The 1 MiB per-block cap was introduced specifically to prevent the reference-script deserialization DDoS class (which caused a real mainnet incident on June 25, 2024, as documented in `docs/adr/2024-08-14_009-refscripts-fee-change.md`). By bypassing this cap, an attacker forces every validating node to perform more deserialization work per block than the protocol intends, degrading block validation throughput. This matches the allowed Medium impact: "Attacker-controlled transactions … exceed intended validation limits." [5](#0-4) 

### Likelihood Explanation

**Medium.** The attack requires no privileged access — any unprivileged transaction submitter can craft T1 … T(N+1). The attacker must pay transaction fees including the tiered `minFeeRefScriptCostPerByte` surcharge, which raises cost but does not prevent the attack. The attack is limited to protocol version ≤ 10 within Conway era; once the network upgrades to protocol version 11 (still within Conway), the `otherwise` branch of `totalRefScriptSizeInBlock` is used and the vulnerability is mitigated. The vulnerability is present in the production codebase for any node running Conway at protocol version 9 or 10.

### Recommendation

Backport the protocol-version-11 UTxO-threading logic to the `pvMajor protVer <= natVersion @10` branch, or remove the version gate entirely since the corrected accumulating fold is strictly more accurate and produces identical results for blocks that contain no intra-block reference-script creation. Alternatively, document the version-gated behavior explicitly and ensure the per-block limit is enforced at the LEDGER level (post-application) rather than only at the BBODY level (pre-application) for protocol version ≤ 10.

### Proof of Concept

**Setup (Conway era, protocol version 10):**

```
maxRefScriptSizePerTx    = 200 * 1024  = 204,800 bytes
maxRefScriptSizePerBlock = 1024 * 1024 = 1,048,576 bytes
```

**Transactions in one block:**

| Tx | Action | Ref-script bytes counted by block check | Ref-script bytes counted by per-tx check |
|----|--------|-----------------------------------------|------------------------------------------|
| T1 | Creates UTxO₁…UTxO₆, each with 200 KiB ref script | 0 (T1 uses no ref inputs) | 0 |
| T2 | Uses UTxO₁ as reference input | 0 (UTxO₁ not in initial UTxO) | 204,800 ✓ |
| T3 | Uses UTxO₂ as reference input | 0 | 204,800 ✓ |
| T4 | Uses UTxO₃ as reference input | 0 | 204,800 ✓ |
| T5 | Uses UTxO₄ as reference input | 0 | 204,800 ✓ |
| T6 | Uses UTxO₅ as reference input | 0 | 204,800 ✓ |
| T7 | Uses UTxO₆ as reference input | 0 | 204,800 ✓ |

**Block-level check result:** 0 ≤ 1,048,576 → **passes**
**Actual deserialization work:** 6 × 204,800 = **1,228,800 bytes** (117% of the intended cap)

The block is accepted by all honest nodes running protocol version 10, each performing 1.2 MiB of reference-script deserialization — exceeding the 1 MiB block limit by design. [6](#0-5) [1](#0-0) [7](#0-6)

### Citations

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Bbody.hs (L314-314)
```haskell
  validateBodyRefScriptsSizeTooBig @era pp blockBody (ls ^. utxoL)
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Bbody.hs (L342-355)
```haskell
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

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/PParams.hs (L980-983)
```haskell
  ppMaxRefScriptSizePerTxG = L.to . const $ 200 * 1024
  ppMaxRefScriptSizePerBlockG = L.to . const $ 1024 * 1024
  ppRefScriptCostMultiplierG = L.to . const . fromJust $ boundRational 1.2
  ppRefScriptCostStrideG = L.to . const $ knownNonZeroBounded @25_600
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Ledger.hs (L456-471)
```haskell
validateRefScriptSize ::
  ( EraTx era
  , BabbageEraTxBody era
  , ConwayEraPParams era
  ) =>
  PParams era -> UTxO era -> Tx l era -> Test (ConwayLedgerPredFailure era)
validateRefScriptSize pp utxo tx =
  let totalRefScriptSize = txNonDistinctRefScriptsSize utxo tx
      maxRefScriptSizePerTx = fromIntegral @Word32 @Int $ pp ^. ppMaxRefScriptSizePerTxG
   in failureUnless (totalRefScriptSize <= maxRefScriptSizePerTx) $
        ( ConwayTxRefScriptsSizeTooBig
            Mismatch
              { mismatchSupplied = totalRefScriptSize
              , mismatchExpected = maxRefScriptSizePerTx
              }
        )
```

**File:** docs/adr/2024-08-14_009-refscripts-fee-change.md (L15-19)
```markdown
It was identified a while ago that there is an overhead associated with deserializing scripts, so much so that it would be possible to create a very large script that was fairly expensive to deserialize, but very cheap to execute. This opened up an attack vector when such a Plutus script would be used as a reference script. This problem was exacerbated by the fact that there was no real limit on the total size of reference scripts that could be used in a transaction, thus being limited only by the size of the transaction itself. Therefore this opened up Cardano to a DDoS attack where an attacker could submit many such transactions that would cost very little, but would be expensive for a `cardano-node` to validate.

In order to prevent such an attack a `"minFeeRefScriptCostPerByte"` protocol parameter was introduced in the Conway era. The idea was fairly simple: we would calculate the total size of reference scripts used by a transaction and multiply it by the value specified by this protocol parameter. Result would be added to the transaction fee. However, in order for this approach to be a definite deterrent of such attacks this parameter would have to be set to a fairly high value. Community was not very keen on having this value set to a high enough value, since that could make reference scripts almost as expensive to use as regular scripts, thus significantly reducing their usability. Taking this fact into consideration, a decision was made to set this parameter to a fairly moderate value to at l ... (truncated)

Unfortunately things did not go exactly as planned, because on [June 25th 2024 an attack like this actually took place](https://cardanospot.io/news/ddos-attack-on-the-cardano-blockchain-mRIKAzZTNnzq5NGd). This attack forced us to make a quick decision on implementing a definite prevention of such attacks, while trying to not have a drastic impact on the common use case that DApp developers rely on so much.
```
