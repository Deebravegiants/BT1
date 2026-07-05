Let me look more closely at the `TimelockMOf` negative `m` issue and the `MultiSig` decoder to confirm the full attack path.

### Title
Negative threshold in `TimelockMOf`/`MultiSigMOf` bypasses M-of-N witness validation — (`eras/allegra/impl/src/Cardano/Ledger/Allegra/Scripts.hs`, `eras/shelley/impl/src/Cardano/Ledger/Shelley/Scripts.hs`)

---

### Summary

The `m` parameter in `TimelockMOf` (Allegra–Dijkstra) and `MultiSigMOf` (Shelley) native scripts is typed as a signed `Int`. The CBOR decoders accept negative values without any range check. The evaluator `isValidMOf` immediately returns `True` whenever `m ≤ 0`, so a script author can craft a serialized native script with `m = -1` that always passes witness validation regardless of which — or how many — signatures are present.

---

### Finding Description

**Formal-spec divergence.** Both the Shelley and ShelleyMA formal specifications define the constructor as `RequireMOf ∈ ℕ → [Script] → Script` — `m` is a natural number. The Shelley multi-sig spec even carries an inline note:

> `-- n.b., should also check that this is >= 0` [1](#0-0) 

**Implementation uses signed `Int`.** Both data types store `m` as `!Int`: [2](#0-1) [3](#0-2) 

The developer comment on line 184 explicitly acknowledges the consequence: *"Note that the Int may be negative in which case (TimelockMOf (-2) [..]) is always True"*.

**CBOR decoders accept negative values.** Neither decoder validates `m ≥ 0`:

- Shelley `MultiSigMOf`: `m <- decCBOR` (decodes any CBOR integer into `Int`) [4](#0-3) 

- Allegra `TimelockMOf`: `Ann (SumD TimelockMOf) <*! Ann From <*! ...` (`Ann From` accepts any CBOR integer) [5](#0-4) 

- Dijkstra `DijkstraRequireMOf`: same pattern, `m <- decCBOR` [6](#0-5) 

**Evaluator short-circuits to `True` for any `m ≤ 0`.** Both `evalMultiSig` and `evalTimelock` share the same `isValidMOf` logic:

```haskell
isValidMOf n SSeq.Empty = n <= 0          -- True when n < 0
isValidMOf n (ts SSeq.:<| tss) =
  n <= 0 || ...                            -- True immediately when n < 0
``` [7](#0-6) [8](#0-7) 

When `n = -1`, the condition `n <= 0` is `True` at every recursive step, so the script evaluates to `True` with zero valid signatures.

---

### Impact Explanation

A script author submits a CBOR-encoded native script `[3, -1, [kh1, kh2, kh3]]` (tag 3 = MOf, threshold = −1, three key hashes). The script hash is computed from these bytes and used as a locking credential. Any transaction spending a UTxO at that address passes native-script witness validation with **no signatures at all**, because `isValidMOf (-1) xs` is unconditionally `True`. This constitutes a witness-validation bypass: attacker-controlled serialized scripts exceed the intended validation limits of the M-of-N construct, allowing unauthorized spending of ADA or native assets locked by such scripts.

This matches the allowed impact: **Medium — attacker-controlled scripts exceed intended validation limits**.

---

### Likelihood Explanation

The attack requires the script author to be malicious and the counterparty to not independently verify the script before sending funds. This is realistic in:

- Multi-party treasury or escrow setups where one participant proposes the script
- DApps that accept user-supplied native scripts
- Protocols that display only the script hash, not the decoded threshold

The CBOR encoding of a negative integer (`0x20` for −1) is a single byte and is syntactically valid. No special tooling is needed.

---

### Recommendation

1. Change `!Int` to `!Natural` (or `!Word`) in `MultiSigMOf` and `TimelockMOf` across all eras. This makes negative values unrepresentable at the type level.
2. As a belt-and-suspenders measure, add a decoder-level guard:
   ```haskell
   3 -> do
     m <- decCBOR
     when (m < 0) $ fail "RequireMOf: negative threshold"
     ...
   ```
3. Add a conformance test that attempts to deserialize a script with `m = -1` and asserts it is rejected.

---

### Proof of Concept

```haskell
-- Construct the offending script in-process:
let badScript = TimelockMOf (-1) StrictSeq.empty  -- or with sub-scripts

-- Evaluator result with empty witness set:
-- isValidMOf (-1) Empty
--   = (-1 <= 0)
--   = True                          ← script passes with zero signatures

-- The same script round-trips through CBOR unchanged:
-- encCBOR (TimelockMOf (-1) []) == [3, 0x20, []]
-- decCBOR that bytes == TimelockMOf (-1) []   (no rejection)

-- Any transaction spending a UTxO locked by hash(badScript)
-- is accepted by evalTimelock {} anyVI badScript == True
``` [9](#0-8) [10](#0-9)

### Citations

**File:** eras/shelley/formal-spec/multi-sig.tex (L751-754)
```tex
                -- ^ Minimum number of signatures required to unlock
                --   the output (should not exceed @length signatories@)
                --   n.b., should also check that this is >= 0
                }
```

**File:** eras/shelley/impl/src/Cardano/Ledger/Shelley/Scripts.hs (L103-103)
```haskell
    MultiSigMOf !Int !(StrictSeq (MultiSig era))
```

**File:** eras/shelley/impl/src/Cardano/Ledger/Shelley/Scripts.hs (L274-277)
```haskell
      3 -> do
        m <- decCBOR
        multiSigs <- sequence <$> decCBOR
        pure (3, MultiSigMOf m <$> multiSigs)
```

**File:** eras/shelley/impl/src/Cardano/Ledger/Shelley/Scripts.hs (L296-313)
```haskell
evalMultiSig ::
  (ShelleyEraScript era, NativeScript era ~ MultiSig era) =>
  Set.Set (KeyHash Witness) ->
  NativeScript era ->
  Bool
evalMultiSig vhks = go
  where
    -- The important part of this validator is that it will stop as soon as it reaches the
    -- required number of valid scripts
    isValidMOf n StrictSeq.Empty = n <= 0
    isValidMOf n (msig StrictSeq.:<| msigs) =
      n <= 0 || if go msig then isValidMOf (n - 1) msigs else isValidMOf n msigs
    go = \case
      RequireSignature hk -> Set.member hk vhks
      RequireAllOf msigs -> all go msigs
      RequireAnyOf msigs -> any go msigs
      RequireMOf m msigs -> isValidMOf m msigs
      _ -> error "Impossible: All NativeScripts should have been accounted for"
```

**File:** eras/allegra/impl/src/Cardano/Ledger/Allegra/Scripts.hs (L183-184)
```haskell
  | TimelockMOf !Int !(StrictSeq (Timelock era))
  | -- Note that the Int may be negative in which case (TimelockMOf (-2) [..]) is always True
```

**File:** eras/allegra/impl/src/Cardano/Ledger/Allegra/Scripts.hs (L242-242)
```haskell
      decRaw 3 = Ann (SumD TimelockMOf) <*! Ann From <*! D (sequence <$> decCBOR)
```

**File:** eras/allegra/impl/src/Cardano/Ledger/Allegra/Scripts.hs (L477-497)
```haskell
evalTimelock ::
  (AllegraEraScript era, NativeScript era ~ Timelock era) =>
  Set.Set (KeyHash Witness) ->
  ValidityInterval ->
  NativeScript era ->
  Bool
evalTimelock vhks (ValidityInterval txStart txExp) = go
  where
    -- The important part of this validator is that it will stop as soon as it reaches the
    -- required number of valid scripts
    isValidMOf n SSeq.Empty = n <= 0
    isValidMOf n (ts SSeq.:<| tss) =
      n <= 0 || if go ts then isValidMOf (n - 1) tss else isValidMOf n tss
    go = \case
      RequireTimeStart lockStart -> lockStart `lteNegInfty` txStart
      RequireTimeExpire lockExp -> txExp `ltePosInfty` lockExp
      RequireSignature hash -> hash `Set.member` vhks
      RequireAllOf xs -> all go xs
      RequireAnyOf xs -> any go xs
      RequireMOf m xs -> isValidMOf m xs
      _ -> error "Impossible: All NativeScripts should have been accounted for"
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Scripts.hs (L279-282)
```haskell
    3 -> do
      m <- decCBOR
      xs <- decCBOR
      pure (3, DijkstraRequireMOf m <$> sequence xs)
```
