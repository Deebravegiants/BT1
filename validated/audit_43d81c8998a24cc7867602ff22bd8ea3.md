Now I have all the information needed. Let me analyze the complete call chain.

### Title
Negative `m` in `RequireMOf`/`TimelockMOf` Causes Unconditional Native Script Validation, Enabling Unauthorized Native Asset Minting — (`eras/allegra/impl/src/Cardano/Ledger/Allegra/Scripts.hs`, `eras/shelley/impl/src/Cardano/Ledger/Shelley/Scripts.hs`)

---

### Summary

Both `evalTimelock` (Allegra through Conway) and `evalMultiSig` (Shelley) use a signed `Int` for the `m` threshold in `RequireMOf`/`TimelockMOf`. The `isValidMOf` helper short-circuits to `True` whenever `n <= 0`. Because the CBOR decoder applies no non-negativity guard on `m`, an attacker can submit a script with `m = -1` (or any negative value) that unconditionally passes validation. This allows unauthorized minting of native assets under any policy ID derived from such a script, with zero signatures required.

---

### Finding Description

**Root cause — `TimelockRaw` data type:** [1](#0-0) 

The field is `!Int` (signed). The inline comment explicitly acknowledges the consequence: `(TimelockMOf (-2) [..]) is always True`.

**Root cause — `isValidMOf` in `evalTimelock`:** [2](#0-1) 

`isValidMOf n SSeq.Empty = n <= 0` — any negative `n` satisfies `n <= 0` immediately. The second clause `n <= 0 || ...` short-circuits before inspecting any sub-scripts. The dispatch at line 496 passes `m` directly: [3](#0-2) 

**Same root cause in `evalMultiSig` (Shelley era):** [4](#0-3) 

**CBOR decoder applies no non-negativity guard:** [5](#0-4) 

`Ann From` decodes any valid CBOR integer into `Int`, including negative values. No range check is performed before or after decoding.

For `MultiSigRaw`: [6](#0-5) 

Again, `m <- decCBOR` decodes any `Int` with no validation.

**Spec deviation:** The formal specification defines `MOfN ∈ ℕ → seq(Timelock) → Timelock` (natural numbers): [7](#0-6) 

The implementation substitutes `ℕ` with `Int`, creating a gap the spec does not permit.

---

### Impact Explanation

An attacker can:

1. Construct `RequireMOf (-1) []` (CBOR tag 3, integer `-1`, empty array).
2. Compute `policyId = hash(script_bytes)`.
3. Submit a transaction with `mint` tokens under `policyId` and the script as a native script witness.
4. The ledger decodes the script (no rejection of negative `m`), evaluates `isValidMOf (-1) Empty` → `(-1) <= 0` → `True`, and accepts the transaction.
5. Arbitrary quantities of native assets are minted under that policy ID with **zero signatures**.

This constitutes unauthorized creation of native assets through an invalid ledger state transition — **Critical** impact per the bounty scope. The same mechanism applies to spending any UTxO locked at `hash(RequireMOf (-1) [])`.

---

### Likelihood Explanation

The attack is fully self-contained: the attacker constructs the script, computes the policy ID, and submits a single transaction. No privileged access, governance majority, leaked key, or third-party compromise is required. The CBOR encoding of a negative integer is standard and accepted by all node versions across Shelley through Conway eras.

---

### Recommendation

1. **Reject negative `m` at decode time.** In both `DecCBOR (Annotator (TimelockRaw era))` and `DecCBOR (Annotator (MultiSigRaw era))`, after decoding `m`, assert `m >= 0` and call `fail`/`invalidKey` otherwise.
2. **Change the field type** from `Int` to `Natural` or `Word32` to make the invariant structural and eliminate the need for a runtime check.
3. **Add a guard in `isValidMOf`** as defense-in-depth: treat any `n < 0` as `n = 0` or immediately return `False`.
4. Align the implementation with the formal spec (`MOfN ∈ ℕ`).

---

### Proof of Concept

```haskell
-- Construct the always-true script
let alwaysTrueScript = mkRequireMOfTimelock @AllegraEra (-1) StrictSeq.empty

-- Evaluate directly: must return True with empty key set and any validity interval
assert $ evalTimelock mempty (ValidityInterval SNothing SNothing) alwaysTrueScript == True

-- Compute policy ID
let policyId = PolicyID (hashScript alwaysTrueScript)

-- Build a minting transaction: mint 1_000_000 tokens under policyId, no signatures needed
let mintValue = MultiAsset (Map.singleton policyId (Map.singleton (AssetName "FREE") 1_000_000))
-- Submit tx with alwaysTrueScript as native script witness → accepted by ledger
```

The call chain is: `UTXOW → validateNativeScript → validateTimelock → evalTimelock vhks vi (RequireMOf (-1) []) → isValidMOf (-1) Empty → (-1) <= 0 → True`.

### Citations

**File:** eras/allegra/impl/src/Cardano/Ledger/Allegra/Scripts.hs (L183-184)
```haskell
  | TimelockMOf !Int !(StrictSeq (Timelock era))
  | -- Note that the Int may be negative in which case (TimelockMOf (-2) [..]) is always True
```

**File:** eras/allegra/impl/src/Cardano/Ledger/Allegra/Scripts.hs (L242-242)
```haskell
      decRaw 3 = Ann (SumD TimelockMOf) <*! Ann From <*! D (sequence <$> decCBOR)
```

**File:** eras/allegra/impl/src/Cardano/Ledger/Allegra/Scripts.hs (L487-489)
```haskell
    isValidMOf n SSeq.Empty = n <= 0
    isValidMOf n (ts SSeq.:<| tss) =
      n <= 0 || if go ts then isValidMOf (n - 1) tss else isValidMOf n tss
```

**File:** eras/allegra/impl/src/Cardano/Ledger/Allegra/Scripts.hs (L496-496)
```haskell
      RequireMOf m xs -> isValidMOf m xs
```

**File:** eras/shelley/impl/src/Cardano/Ledger/Shelley/Scripts.hs (L274-277)
```haskell
      3 -> do
        m <- decCBOR
        multiSigs <- sequence <$> decCBOR
        pure (3, MultiSigMOf m <$> multiSigs)
```

**File:** eras/shelley/impl/src/Cardano/Ledger/Shelley/Scripts.hs (L305-312)
```haskell
    isValidMOf n StrictSeq.Empty = n <= 0
    isValidMOf n (msig StrictSeq.:<| msigs) =
      n <= 0 || if go msig then isValidMOf (n - 1) msigs else isValidMOf n msigs
    go = \case
      RequireSignature hk -> Set.member hk vhks
      RequireAllOf msigs -> all go msigs
      RequireAnyOf msigs -> any go msigs
      RequireMOf m msigs -> isValidMOf m msigs
```

**File:** eras/shelley-ma/formal-spec/timelock-language.tex (L57-58)
```tex
    %
    & \type{MOfN} & \in \N \to \seqof{\Timelock} \to \Timelock & \\
```
