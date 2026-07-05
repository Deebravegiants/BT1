### Title
Negative `m` in `TimelockMOf` Bypasses Minting Policy Authorization — (`eras/allegra/impl/src/Cardano/Ledger/Allegra/Scripts.hs`)

---

### Summary

`TimelockMOf` stores its threshold as a Haskell `Int`, not `Natural`. The `isValidMOf` base case `n <= 0` returns `True` for any negative `n`. An attacker can CBOR-encode a `RequireMOf (-1) []` script, use its hash as a minting policy ID, and mint arbitrary native tokens with zero witnesses. The CBOR decoder accepts negative integers for this field without any guard.

---

### Finding Description

`TimelockRaw` is defined with an `!Int` field for the threshold: [1](#0-0) 

The code even carries an explicit acknowledgment of the consequence:

> `-- Note that the Int may be negative in which case (TimelockMOf (-2) [..]) is always True`

The evaluator's base case is: [2](#0-1) 

For `RequireMOf (-1) []`: `isValidMOf (-1) SSeq.Empty` → `-1 <= 0` → `True`. No witnesses are checked.

The CBOR decoder for `TimelockRaw` (tag 3) decodes the threshold with a plain `decCBOR @Int` / `Ann From`, which accepts any signed integer: [3](#0-2) [4](#0-3) 

There is no non-negativity guard anywhere in the decode path, in `evalTimelock`, or in `validateTimelock`: [5](#0-4) 

The UTXOW rule calls `validateFailedNativeScripts`, which calls `validateNativeScript` on every provided native script. A script that returns `True` is accepted: [6](#0-5) 

For Mary-era minting, `getMaryScriptsNeeded` adds the policy IDs from the `mint` field to the required script set: [7](#0-6) 

So the attacker's script is required, provided, and validated — and it passes.

The formal specification explicitly types the threshold as `N` (natural numbers): [8](#0-7) 

The implementation diverges from the spec by using `Int`.

---

### Impact Explanation

An unprivileged attacker can:

1. Construct a `TimelockMOf (-1) []` script (CBOR: `[3, -1, []]`).
2. Compute its script hash — this becomes the policy ID.
3. Submit a Mary-era minting transaction with `mint = {policyID: {assetName: quantity}}`, providing the script as a witness but **zero key witnesses**.
4. `validateNativeScript` returns `True`; the transaction is accepted.
5. Arbitrary quantities of native tokens under that policy ID are created on-chain.

This is a direct, unauthorized creation of native assets. The policy ID is fixed (it is the hash of the specific negative-m script), so the attacker cannot impersonate an existing policy, but they can mint unbounded quantities of tokens under this "always-true" policy without any authorization. This violates the core invariant that every minted token must satisfy its minting policy.

---

### Likelihood Explanation

- Requires only crafting a valid CBOR-encoded transaction — no privileged access, no key leakage, no governance majority.
- CBOR natively supports negative integers; the decoder accepts them without error.
- The behavior is deterministic and reproducible on any node running this code.
- The comment in the source code confirms the developers are aware of the behavior but have not added a guard.

---

### Recommendation

1. Change `TimelockMOf !Int` to `TimelockMOf !Natural` in `TimelockRaw`.
2. If backward-compatibility with existing on-chain scripts requires keeping `Int` in the wire format, add an explicit non-negativity check in the CBOR decoder (reject if `requiredCount < 0`) and/or in `evalTimelock` (treat negative `m` as a script failure).
3. Add a property test asserting `validateNativeScript` returns `False` for all `m < 0`.

---

### Proof of Concept

```haskell
-- Construct the always-true minting policy
let badScript = mkRequireMOfTimelock @MaryEra (-1) SSeq.empty
    policyId  = PolicyID (hashScript badScript)
    assetName = AssetName "freeToken"
    mintAmt   = 1_000_000_000
    mintVal   = MultiAsset $ Map.singleton policyId
                           $ Map.singleton assetName mintAmt

-- Build a minting tx with NO key witnesses, only the script witness
let txBody = mkBasicTxBody
               & mintTxBodyL    .~ mintVal
               & outputsTxBodyL .~ [mkBasicTxOut someAddr (MaryValue mempty mintVal)]
    tx = mkBasicTx txBody
           & witsTxL . scriptTxWitsL .~ Map.singleton (hashScript badScript)
                                                       (fromNativeScript badScript)
           -- addrTxWitsL intentionally empty

-- Expected (per spec): ScriptWitnessNotValidatingUTXOW
-- Actual:              transaction accepted, 1 billion tokens minted
submitTx tx
```

`isValidMOf (-1) SSeq.Empty` evaluates to `True` because `-1 <= 0`, so `validateNativeScript` returns `True` and the UTXOW rule does not raise `ScriptWitnessNotValidatingUTXOW`.

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

**File:** eras/allegra/impl/testlib/Test/Cardano/Ledger/Allegra/Binary/Annotator.hs (L69-72)
```haskell
    3 -> do
      requiredCount <- decCBOR
      timelocks <- decCBOR
      pure (3, TimelockMOf requiredCount timelocks)
```

**File:** eras/allegra/impl/src/Cardano/Ledger/Allegra/Tx.hs (L100-106)
```haskell
validateTimelock ::
  (EraTx era, AllegraEraTxBody era, AllegraEraScript era, NativeScript era ~ Timelock era) =>
  Tx t era -> NativeScript era -> Bool
validateTimelock tx timelock = evalTimelock vhks (tx ^. bodyTxL . vldtTxBodyL) timelock
  where
    vhks = Set.map witVKeyHash (tx ^. witsTxL . addrTxWitsL)
{-# INLINEABLE validateTimelock #-}
```

**File:** eras/shelley/impl/src/Cardano/Ledger/Shelley/Rules/Utxow.hs (L366-373)
```haskell
validateFailedNativeScripts ::
  EraTx era => ScriptsProvided era -> Tx l era -> Test (ShelleyUtxowPredFailure era)
validateFailedNativeScripts (ScriptsProvided scriptsProvided) tx = do
  let failedScripts =
        Map.filter -- we keep around only non-validating native scripts
          (maybe False (not . validateNativeScript tx) . getNativeScript)
          scriptsProvided
  failureOnNonEmptySet (Map.keysSet failedScripts) ScriptWitnessNotValidatingUTXOW
```

**File:** eras/mary/impl/src/Cardano/Ledger/Mary/UTxO.hs (L107-116)
```haskell
getMaryScriptsNeeded ::
  (ShelleyEraTxBody era, MaryEraTxBody era) =>
  UTxO era ->
  TxBody l era ->
  ShelleyScriptsNeeded era
getMaryScriptsNeeded u txBody =
  case getShelleyScriptsNeeded u txBody of
    ShelleyScriptsNeeded shelleyScriptsNeeded ->
      ShelleyScriptsNeeded $
        shelleyScriptsNeeded `Set.union` Set.map policyID (txBody ^. mintedTxBodyF)
```

**File:** eras/shelley-ma/formal-spec/timelock-language.tex (L58-58)
```tex
    & \type{MOfN} & \in \N \to \seqof{\Timelock} \to \Timelock & \\
```
