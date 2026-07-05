### Title
Missing Lower Bound Validation for `maxRefScriptSizePerTx` and `maxRefScriptSizePerBlock` in `ppuWellFormed` for `DijkstraEra` — (`File: eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/PParams.hs`)

---

### Summary

The `ppuWellFormed` implementation for `DijkstraEra` omits lower-bound (non-zero) validation for the two new Dijkstra-era reference-script size-limit parameters: `maxRefScriptSizePerTx` and `maxRefScriptSizePerBlock`. Any transaction sender who pays the governance-action deposit can submit a `ParameterChange` proposal setting either parameter to `0`. The proposal passes the `actionWellFormed` gate without triggering `MalformedProposal`. If ratified and enacted, `validateRefScriptSize` would reject every transaction that touches a reference script, permanently freezing funds locked in reference-script-dependent UTxOs until a corrective governance action is enacted.

---

### Finding Description

`ppuWellFormed` is the ledger's gatekeeper for `ParameterChange` governance proposals. It is called from `actionWellFormed` in the GOV rule:

```haskell
-- eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Gov.hs
actionWellFormed pv ga = failureUnless isWellFormed $ MalformedProposal ga
  where
    isWellFormed = case ga of
      ParameterChange _ ppd _ -> ppuWellFormed pv ppd
      _ -> True
``` [1](#0-0) 

For `DijkstraEra`, the `ConwayEraPParams DijkstraEra` instance implements `ppuWellFormed` as follows:

```haskell
instance ConwayEraPParams DijkstraEra where
  ppuWellFormed _pv ppu =
    and
      [ isValid (/= 0) ppuMaxBBSizeL
      , isValid (/= 0) ppuMaxTxSizeL
      , isValid (/= 0) ppuMaxBHSizeL
      , isValid (/= 0) ppuMaxValSizeL
      , isValid (/= 0) ppuCollateralPercentageL
      , isValid (/= EpochInterval 0) ppuCommitteeMaxTermLengthL
      , isValid (/= EpochInterval 0) ppuGovActionLifetimeL
      , isValid (/= mempty) ppuPoolDepositL
      , isValid (/= zero) ppuGovActionDepositL
      , isValid (/= zero) ppuDRepDepositL
      , isValid ((/= CompactCoin 0) . unCoinPerByte) ppuCoinsPerUTxOByteL
      , ppu /= emptyPParamsUpdate
      , isValid (/= 0) ppuNOptL
      ]
``` [2](#0-1) 

The check validates that legacy parameters such as `ppuMaxBBSizeL`, `ppuMaxTxSizeL`, `ppuMaxValSizeL`, and `ppuCollateralPercentageL` are non-zero. However, the four new Dijkstra-era parameters — `ppuMaxRefScriptSizePerBlockL`, `ppuMaxRefScriptSizePerTxL`, `ppuRefScriptCostStrideL`, and `ppuRefScriptCostMultiplierL` — are entirely absent from this check. [3](#0-2) 

`maxRefScriptSizePerTx` and `maxRefScriptSizePerBlock` are plain `Word32` fields with no type-level non-zero constraint, so they can be set to `0` in a `PParamsUpdate`. The `ppuWellFormed` check does not reject this, so the proposal passes `actionWellFormed` and enters the governance queue.

Once enacted, `validateRefScriptSize` in the LEDGER rule enforces the limit:

```haskell
validateRefScriptSize pp utxo tx =
  let totalRefScriptSize = txNonDistinctRefScriptsSize utxo tx
      maxRefScriptSizePerTx = fromIntegral @Word32 @Int $ pp ^. ppMaxRefScriptSizePerTxG
   in failureUnless (totalRefScriptSize <= maxRefScriptSizePerTx) $
        ConwayTxRefScriptsSizeTooBig ...
``` [4](#0-3) 

With `maxRefScriptSizePerTx = 0`, any transaction whose `totalRefScriptSize > 0` — i.e., any transaction that references a UTxO containing a script — is rejected. This covers all DApps that rely on reference scripts (Plutus V2/V3/V4 scripts stored in UTxOs), which is the dominant pattern since Babbage.

The same applies to `maxRefScriptSizePerBlock = 0`, which would cause every block containing such transactions to be rejected at the BBODY level.

---

### Impact Explanation

**Allowed impact matched**: *Medium — Attacker-controlled proposals exceed intended validation limits or modify fees, deposits, refunds, rewards, treasury donations, or withdrawals outside design parameters.*

A proposal author (any transaction sender who pays the governance deposit) can submit a `ParameterChange` governance action with `maxRefScriptSizePerTx = 0` or `maxRefScriptSizePerBlock = 0`. The `ppuWellFormed` check — the intended validation gate — does not reject it. The proposal enters the governance queue with parameter values that are outside design parameters (the entire purpose of these parameters is to set a positive DDoS-prevention ceiling, as documented in ADR-009). [5](#0-4) 

If enacted, all transactions using reference scripts are rejected by `validateRefScriptSize`, freezing funds in reference-script-dependent UTxOs until a corrective governance action is enacted.

---

### Likelihood Explanation

The attacker-controlled step — submitting the malformed proposal — requires only the governance action deposit and a valid return address. The `actionWellFormed` check is the only ledger-level gate, and it delegates entirely to `ppuWellFormed`, which does not cover these parameters. Enactment requires governance majority (DReps, SPOs, Constitutional Committee), which substantially reduces the probability of the worst-case outcome. However, the missing validation means the proposal is not rejected at submission time as the protocol intends, and the malformed proposal can persist in the governance queue for its full lifetime.

---

### Recommendation

Add non-zero lower-bound checks for `ppuMaxRefScriptSizePerTxL` and `ppuMaxRefScriptSizePerBlockL` inside the `ppuWellFormed` implementation for `DijkstraEra`, consistent with how analogous size-limit parameters are validated:

```haskell
instance ConwayEraPParams DijkstraEra where
  ppuWellFormed _pv ppu =
    and
      [ ...
      , isValid (/= 0) ppuMaxRefScriptSizePerTxL
      , isValid (/= 0) ppuMaxRefScriptSizePerBlockL
      , ...
      ]
``` [6](#0-5) 

This mirrors the existing pattern for `ppuMaxBBSizeL`, `ppuMaxTxSizeL`, `ppuMaxValSizeL`, and `ppuCollateralPercentageL`, all of which are `Word32`/`Word16` parameters that are already guarded against zero.

---

### Proof of Concept

1. **Missing check**: `ppuWellFormed` for `DijkstraEra` (lines 539–565 of `eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/PParams.hs`) contains no entry for `ppuMaxRefScriptSizePerTxL` or `ppuMaxRefScriptSizePerBlockL`. [2](#0-1) 

2. **Proposal submission**: A transaction sender constructs a `ParameterChange` governance action with `ppuMaxRefScriptSizePerTxL = SJust 0`. The GOV rule calls `actionWellFormed`, which calls `ppuWellFormed`. Because `ppuWellFormed` has no check for this lens, it returns `True`. The proposal is accepted and enters the governance queue without a `MalformedProposal` failure. [1](#0-0) 

3. **Contrast with Conway**: The `ConwayEra` instance of `ppuWellFormed` (lines 933–961 of `eras/conway/impl/src/Cardano/Ledger/Conway/PParams.hs`) also lacks these checks, but Conway does not expose `maxRefScriptSizePerTx`/`maxRefScriptSizePerBlock` as updatable parameters (they are hardcoded). The Dijkstra era promotes them to governance-updatable parameters without adding the corresponding well-formedness guards. [7](#0-6) 

4. **Enforcement path**: After enactment, `validateRefScriptSize` compares `totalRefScriptSize` against `pp ^. ppMaxRefScriptSizePerTxG`, which now resolves to the live `dppMaxRefScriptSizePerTx` field. With the field set to `0`, every transaction referencing a script-bearing UTxO fails with `ConwayTxRefScriptsSizeTooBig`. [4](#0-3)

### Citations

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Gov.hs (L393-399)
```haskell
actionWellFormed ::
  ConwayEraPParams era => ProtVer -> GovAction era -> Test (ConwayGovPredFailure era)
actionWellFormed pv ga = failureUnless isWellFormed $ MalformedProposal ga
  where
    isWellFormed = case ga of
      ParameterChange _ ppd _ -> ppuWellFormed pv ppd
      _ -> True
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

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/PParams.hs (L539-565)
```haskell
instance ConwayEraPParams DijkstraEra where
  ppuWellFormed _pv ppu =
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
        isValid (/= mempty) ppuPoolDepositL
      , isValid (/= zero) ppuGovActionDepositL
      , isValid (/= zero) ppuDRepDepositL
      , isValid ((/= CompactCoin 0) . unCoinPerByte) ppuCoinsPerUTxOByteL
      , ppu /= emptyPParamsUpdate
      , isValid (/= 0) ppuNOptL
      ]
    where
      isValid ::
        (t -> Bool) ->
        Lens' (PParamsUpdate DijkstraEra) (StrictMaybe t) ->
        Bool
      isValid p l = case ppu ^. l of
        SJust x -> p x
        SNothing -> True
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

**File:** docs/adr/2024-08-14_009-refscripts-fee-change.md (L71-78)
```markdown
### Reference script size limit

In order to further increase the resilience to this sort of attacks we added hard limits on the total size of reference scripts that can be used per transaction and per block.

Hard caps that are currently hard coded, but will be turned into actual protocol parameters in the next era after Conway:

* Limit per transaction: `200KiB` (or `204800` bytes)
* Limit per block: `1MiB` (or `1048576` bytes)
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
