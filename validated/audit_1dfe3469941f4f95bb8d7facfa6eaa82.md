### Title
Hardcoded Reference-Script Fee Parameters in Conway Era Cannot Be Adjusted via Governance, Allowing Fees to Deviate from Design Parameters - (File: `eras/conway/impl/src/Cardano/Ledger/Conway/PParams.hs`)

---

### Summary

In the Conway era, four critical reference-script fee and size-limit parameters are hardcoded as compile-time constants rather than adjustable protocol parameters. They cannot be changed via `ParameterChange` governance actions. If these values are miscalibrated or if new attack patterns emerge, the protocol cannot respond without a hard fork, allowing transaction senders to submit transactions whose reference-script validation cost exceeds the fee charged.

---

### Finding Description

The `ConwayEraPParams` type class declares four getters as `SimpleGetter` (read-only) rather than `Lens'` (read-write):

```haskell
ppMaxRefScriptSizePerTxG   :: SimpleGetter (PParams era) Word32
ppMaxRefScriptSizePerBlockG :: SimpleGetter (PParams era) Word32
ppRefScriptCostMultiplierG  :: SimpleGetter (PParams era) PositiveInterval
ppRefScriptCostStrideG      :: SimpleGetter (PParams era) (NonZero Word32)
```

The `ConwayEra` instance resolves all four to compile-time constants:

```haskell
ppMaxRefScriptSizePerTxG    = L.to . const $ 200 * 1024        -- 204,800 bytes
ppMaxRefScriptSizePerBlockG = L.to . const $ 1024 * 1024       -- 1,048,576 bytes
ppRefScriptCostMultiplierG  = L.to . const . fromJust $ boundRational 1.2
ppRefScriptCostStrideG      = L.to . const $ knownNonZeroBounded @25_600
``` [1](#0-0) 

These four values drive the `tierRefScriptFee` computation inside `getConwayMinFeeTx`:

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
``` [2](#0-1) 

Because these are `SimpleGetter`s backed by constants, they are absent from `eraPParams` (the list of updatable parameters) and absent from `conwayApplyPPUpdates`. No `ParameterChange` governance action can touch them. [3](#0-2) 

The ADR explicitly acknowledges this design choice: *"One of the constraints we had to operate under was inability to add any new protocol parameters, since that was a bit too late in the release cycle of the Conway era. In other words we had to hard code some values, which will be turned into proper protocol parameters in the next era."* [4](#0-3) 

The Dijkstra era corrects this by promoting all four to proper protocol parameters with governance-update support: [5](#0-4) [6](#0-5) 

---

### Impact Explanation

**Medium. Attacker-controlled transactions modify fees outside design parameters.**

Any unprivileged transaction sender can submit a transaction referencing up to 204,800 bytes of reference scripts. The fee charged is computed using the hardcoded multiplier (1.2) and stride (25,600 bytes). Because governance cannot raise the multiplier, lower the per-tx cap, or adjust the stride in response to new attack patterns, the fee charged for reference-script validation may fall below the actual node-side deserialization and execution cost. This is the same class of issue that enabled the June 2024 DDoS attack: the original `minFeeRefScriptCostPerByte` was set too low and could not be raised quickly enough. The hardcoded replacement values carry the same structural risk — they are fixed and unresponsive to on-chain governance.

The block-level limit (`ppMaxRefScriptSizePerBlockG = 1 MiB`) is also hardcoded and enforced in `validateBodyRefScriptsSizeTooBig`: [7](#0-6) 

If the hardcoded 1 MiB block limit is too permissive for the actual hardware cost, governance cannot tighten it without a hard fork.

---

### Likelihood Explanation

**Medium.** The hardcoded values were calibrated against the June 2024 attack profile. However, the Cardano network's hardware landscape, Plutus script sizes, and attacker economics can change. Because the values are immutable in Conway, any future miscalibration requires a hard fork to correct — exactly the scenario the ADR warns about. The entry path is trivially reachable: any wallet can construct a transaction with reference inputs pointing to large scripts up to the 200 KiB per-tx cap.

---

### Recommendation

1. **Short-term (Conway):** Add a `ppuWellFormed` check that rejects `ParameterChange` proposals that set `ppMinFeeRefScriptCostPerByte` to zero, since zero base cost nullifies the tiered pricing entirely regardless of the hardcoded multiplier.
2. **Long-term (already addressed in Dijkstra):** Promote `maxRefScriptSizePerTx`, `maxRefScriptSizePerBlock`, `refScriptCostMultiplier`, and `refScriptCostStride` to proper protocol parameters with governance-update support, as done in `DijkstraPParams`. [8](#0-7) 

---

### Proof of Concept

1. In Conway era (protocol version 9 or 10), submit a transaction with `referenceInputs` pointing to UTxO entries whose combined script bytes total exactly `200 * 1024 - 1 = 204,799` bytes (just under the hardcoded per-tx cap).
2. The fee is computed by `getConwayMinFeeTx` using the hardcoded multiplier 1.2 and stride 25,600. The base rate `ppMinFeeRefScriptCostPerByte` is the only governance-adjustable component.
3. Propose a `ParameterChange` governance action to reduce `ppMinFeeRefScriptCostPerByte` toward its minimum. Because `ppuWellFormed` for Conway does not validate this field against a lower bound, the proposal passes well-formedness checks.
4. Once enacted, the tiered fee curve still uses the hardcoded 1.2 multiplier and 25,600-byte stride, but the base cost is near zero, making large-reference-script transactions nearly free — reproducing the pre-fix DDoS condition.
5. Governance cannot raise the multiplier or lower the per-tx cap to compensate, because those are hardcoded constants in `ConwayEraPParams ConwayEra`. [9](#0-8)

### Citations

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/PParams.hs (L861-893)
```haskell
  eraPParams =
    [ ppTxFeePerByte
    , ppTxFeeFixed
    , ppMaxBBSize
    , ppMaxTxSize
    , ppMaxBHSize
    , ppKeyDeposit
    , ppPoolDeposit
    , ppEMax
    , ppNOpt
    , ppA0
    , ppRho
    , ppTau
    , ppGovProtocolVersion
    , ppMinPoolCost
    , ppCoinsPerUTxOByte
    , ppCostModels
    , ppPrices
    , ppMaxTxExUnits
    , ppMaxBlockExUnits
    , ppMaxValSize
    , ppCollateralPercentage
    , ppMaxCollateralInputs
    , ppPoolVotingThresholds
    , ppDRepVotingThresholds
    , ppCommitteeMinSize
    , ppCommitteeMaxTermLength
    , ppGovActionLifetime
    , ppGovActionDeposit
    , ppDRepDeposit
    , ppDRepActivity
    , ppMinFeeRefScriptCostPerByte
    ]
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/PParams.hs (L933-953)
```haskell
instance ConwayEraPParams ConwayEra where
  ppuWellFormed pv ppu =
    and
      [ -- Numbers
        isValid (/= 0) ppuMaxBBSizeL
      , isValid (/= 0) ppuMaxTxSizeL
      , isValid (/= 0) ppuMaxBHSizeL
      , isValid (/= 0) ppuMaxValSizeL
      , isValid (/= 0) ppuCollateralPercentageL
      , isValid (/= EpochInterval 0) ppuCommitteeMaxTermLengthL
      , isValid (/= EpochInterval 0) ppuGovActionLifetimeL
      , -- Coins
        isValid (/= CompactCoin 0) ppuPoolDepositCompactL
      , isValid (/= CompactCoin 0) ppuGovActionDepositCompactL
      , isValid (/= CompactCoin 0) ppuDRepDepositCompactL
      , hardforkConwayBootstrapPhase pv
          || isValid ((/= CompactCoin 0) . unCoinPerByte) ppuCoinsPerUTxOByteL
      , ppu /= emptyPParamsUpdate
      , pvMajor pv < natVersion @11
          || isValid (/= 0) ppuNOptL
      ]
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/PParams.hs (L980-983)
```haskell
  ppMaxRefScriptSizePerTxG = L.to . const $ 200 * 1024
  ppMaxRefScriptSizePerBlockG = L.to . const $ 1024 * 1024
  ppRefScriptCostMultiplierG = L.to . const . fromJust $ boundRational 1.2
  ppRefScriptCostStrideG = L.to . const $ knownNonZeroBounded @25_600
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

**File:** docs/adr/2024-08-14_009-refscripts-fee-change.md (L23-23)
```markdown
Linear pricing was either too expensive when the multiplier was set too high or was an inadequate deterrent when the multiplier was set too low. Therefore, we needed to implement a pricing mechanism that would be very expensive for usage with large quantities of large plutus scripts, while keeping the pricing reasonably low for the most common use case of a total size of reference scripts of at most 25KiB per transaction. One of the constraints we had to operate under was inability to add any new protocol parameters, since that was a bit too late in the release cycle of the Conway era. In other words we had to hard code some values, which will be turned into proper protocol parameters in the next era.
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/PParams.hs (L151-157)
```haskell
  , dppMaxRefScriptSizePerBlock :: !(THKD ('PPGroups 'NetworkGroup 'SecurityGroup) f Word32)
  -- ^ Limit on the total number of bytes of all reference scripts combined from
  -- all transactions within a block.
  , dppMaxRefScriptSizePerTx :: !(THKD ('PPGroups 'NetworkGroup 'SecurityGroup) f Word32)
  -- ^ Limit on the total number of bytes of reference scripts that a transaction can use.
  , dppRefScriptCostStride :: !(THKD ('PPGroups 'NetworkGroup 'SecurityGroup) f (NonZero Word32))
  , dppRefScriptCostMultiplier :: !(THKD ('PPGroups 'NetworkGroup 'SecurityGroup) f PositiveInterval)
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/PParams.hs (L488-514)
```haskell
ppRefScriptCostStride :: PParam DijkstraEra
ppRefScriptCostStride =
  PParam
    { ppName = "refScriptCostStride"
    , ppLens = ppRefScriptCostStrideL
    , ppEraDecoder = Nothing
    , ppUpdate =
        Just
          PParamUpdate
            { ppuTag = 36
            , ppuLens = ppuRefScriptCostStrideL
            }
    }

ppRefScriptCostMultiplier :: PParam DijkstraEra
ppRefScriptCostMultiplier =
  PParam
    { ppName = "refScriptCostMultiplier"
    , ppLens = ppRefScriptCostMultiplierL
    , ppEraDecoder = Nothing
    , ppUpdate =
        Just
          PParamUpdate
            { ppuTag = 37
            , ppuLens = ppuRefScriptCostMultiplierL
            }
    }
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/PParams.hs (L584-587)
```haskell
  ppMaxRefScriptSizePerTxG = ppLensHKD . hkdMaxRefScriptSizePerTxL
  ppMaxRefScriptSizePerBlockG = ppLensHKD . hkdMaxRefScriptSizePerBlockL
  ppRefScriptCostMultiplierG = ppLensHKD . hkdRefScriptCostMultiplierL
  ppRefScriptCostStrideG = ppLensHKD . hkdRefScriptCostStrideL
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
