### Title
Hardcoded Reference Script Fee Curve Parameters in Conway Era Cannot Be Adjusted via Governance - (File: `eras/conway/impl/src/Cardano/Ledger/Conway/PParams.hs`)

---

### Summary

In the Conway era, four critical reference-script fee and size parameters are hardcoded as compile-time constants rather than being stored as adjustable protocol parameters. Because they are exposed only as `SimpleGetter`s returning fixed values, no governance action can change them. If the hardcoded values prove insufficient to deter a new attack, the only recourse is a hard fork.

---

### Finding Description

The `ConwayEraPParams` type-class defines four getters for reference-script fee/limit parameters. In the `ConwayEra` instance these are implemented as constant functions:

```haskell
-- eras/conway/impl/src/Cardano/Ledger/Conway/PParams.hs, lines 980-983
ppMaxRefScriptSizePerTxG    = L.to . const $ 200 * 1024          -- 204,800 bytes
ppMaxRefScriptSizePerBlockG = L.to . const $ 1024 * 1024         -- 1,048,576 bytes
ppRefScriptCostMultiplierG  = L.to . const . fromJust $ boundRational 1.2
ppRefScriptCostStrideG      = L.to . const $ knownNonZeroBounded @25_600
```

These constants are consumed directly in the minimum-fee calculation:

```haskell
-- eras/conway/impl/src/Cardano/Ledger/Conway/Tx.hs, lines 107-112
refScriptsFee =
  tierRefScriptFee
    (unboundRational $ pp ^. ppRefScriptCostMultiplierG)   -- always 1.2
    (fromIntegral @Word32 @Int . unNonZero $ pp ^. ppRefScriptCostStrideG)  -- always 25600
    refScriptCostPerByte
    refScriptsSize
```

The ADR (`docs/adr/2024-08-14_009-refscripts-fee-change.md`, line 23) explicitly acknowledges the design choice: *"we had to hard code some values, which will be turned into proper protocol parameters in the next era."*

By contrast, `ppMinFeeRefScriptCostPerByteL` is a real `Lens'` backed by `cppMinFeeRefScriptCostPerByte` in `ConwayPParams`, so it **can** be updated via governance. The multiplier and stride cannot.

The Dijkstra era corrects this by storing all four values as proper protocol parameters (`dppRefScriptCostStride`, `dppRefScriptCostMultiplier`, `dppMaxRefScriptSizePerBlock`, `dppMaxRefScriptSizePerTx`) in `DijkstraPParams`, each with a governance-update lens.

---

### Impact Explanation

**Medium — Attacker-controlled transactions modify fees outside design parameters.**

Because the fee-curve shape (multiplier = 1.2, stride = 25,600 bytes) is immutable in Conway, an attacker who characterises the exact pricing tiers can craft reference-script bundles that maximise the ratio of node validation cost to lovelace fee paid. The community cannot raise the multiplier or lower the stride in response without a hard fork. If the hardcoded values are insufficient (as the June 2024 DDoS demonstrated for the earlier linear model), every block producer must process transactions whose fee does not cover their actual deserialization cost, constituting a fee-accounting deviation outside the intended design parameters.

Additionally, the hardcoded per-transaction cap (200 KiB) and per-block cap (1 MiB) cannot be tightened via governance if a new attack vector is discovered that exploits scripts near those limits.

---

### Likelihood Explanation

**Medium.** The June 2024 DDoS attack on Cardano mainnet (referenced in the ADR) already proved that the prior linear pricing was exploitable. The tiered curve raises the bar but does not eliminate the risk: the multiplier of 1.2 was chosen as a community compromise between deterrence and usability, not as a mathematically proven lower bound on attack cost. Any unprivileged transaction sender can submit transactions with reference scripts up to the hardcoded 200 KiB limit; no special role or key is required.

---

### Recommendation

1. Expedite the promotion of `ppRefScriptCostMultiplierG` and `ppRefScriptCostStrideG` to real, governance-updatable protocol parameters (as already done in the Dijkstra era). Until then, document the Conway-era immutability prominently so node operators understand that a hard fork is the only remediation path.
2. Add a validation rule that rejects a `PParamsUpdate` that would set `minFeeRefScriptCostPerByte` to zero while the multiplier/stride remain at their hardcoded values, preventing a governance action from inadvertently making reference scripts free.

---

### Proof of Concept

The root cause is directly visible at the four constant-returning `SimpleGetter` definitions: [1](#0-0) 

These are consumed in the fee calculation: [2](#0-1) 

The ADR confirms the intentional hardcoding and its acknowledged risk: [3](#0-2) 

The Dijkstra era's corrected, governance-updatable counterparts confirm the intended final design: [4](#0-3) 

An attacker submits a transaction with reference scripts totalling just under 200 KiB (the hardcoded per-tx cap). The fee is computed using the fixed 1.2 multiplier and 25,600-byte stride. Because neither value can be raised via a governance `PParamsUpdate` in Conway, the community has no on-chain lever to increase the cost of such transactions if the current curve proves insufficient — exactly the "hardcoded peg" failure mode described in the external report.

### Citations

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

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/PParams.hs (L584-587)
```haskell
  ppMaxRefScriptSizePerTxG = ppLensHKD . hkdMaxRefScriptSizePerTxL
  ppMaxRefScriptSizePerBlockG = ppLensHKD . hkdMaxRefScriptSizePerBlockL
  ppRefScriptCostMultiplierG = ppLensHKD . hkdRefScriptCostMultiplierL
  ppRefScriptCostStrideG = ppLensHKD . hkdRefScriptCostStrideL
```
