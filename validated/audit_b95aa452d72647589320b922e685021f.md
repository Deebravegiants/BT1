### Title
Missing Non-Negativity Validation on `RequireMOf` Threshold Enables Signature-Free Native Script Satisfaction - (File: `eras/allegra/impl/src/Cardano/Ledger/Allegra/Scripts.hs`)

---

### Summary

The `m` parameter in `RequireMOf` native scripts is stored and decoded as `Int` (which can be negative), but neither the CBOR decoder nor the script evaluator validates that `m >= 0`. The formal specification defines `m ∈ ℕ`. An attacker can craft a serialized native script with a negative `m` value that always evaluates to `True` regardless of provided witnesses, bypassing the intended signature threshold for minting policies, payment credentials, and staking credentials.

---

### Finding Description

The `isValidMOf` helper inside `evalMultiSig`, `evalTimelock`, and `evalDijkstraNativeScript` uses `n <= 0` as its short-circuit base case:

```haskell
isValidMOf n StrictSeq.Empty = n <= 0
isValidMOf n (msig StrictSeq.:<| msigs) =
  n <= 0 || if go msig then isValidMOf (n - 1) msigs else isValidMOf n msigs
```

When `n` is any negative integer (e.g., `-1`), the condition `n <= 0` is immediately `True`, so the entire `RequireMOf` clause passes unconditionally regardless of how many witnesses are present. [1](#0-0) 

The CBOR decoders for all three script types decode `m` as a plain `Int` with no lower-bound check:

- **`MultiSigRaw` (Shelley):** `m <- decCBOR` with no range guard [2](#0-1) 

- **`TimelockRaw` (Allegra+):** `Ann (SumD TimelockMOf) <*! Ann From` — `From` decodes a plain `Int` [3](#0-2) 

- **`DijkstraNativeScriptRaw` (Dijkstra):** `m <- decCBOR` with no range guard [4](#0-3) 

The code itself acknowledges this in a comment at line 183–184 of `eras/allegra/impl/src/Cardano/Ledger/Allegra/Scripts.hs`:

```haskell
  | TimelockMOf !Int !(StrictSeq (Timelock era))
  | -- Note that the Int may be negative in which case (TimelockMOf (-2) [..]) is always True
``` [5](#0-4) 

The formal specification (`eras/shelley/formal-spec/multi-sig.tex`) defines `RequireMOf m ts` with `m ∈ ℕ` (natural number): [6](#0-5) 

The embedded Plutus pseudocode comment in the same spec file explicitly notes `"n.b., should also check that this is >= 0"` — but no such check exists in the production evaluator or decoder: [7](#0-6) 

The `evalMultiSig` evaluator in Shelley has the same unchecked `isValidMOf`: [8](#0-7) 

And `evalDijkstraNativeScript` carries the same flaw: [9](#0-8) 

The `DecCBOR Int` instance delegates to `decodeInt`, which accepts any CBOR integer including negatives, with no post-decode validation: [10](#0-9) 

---

### Impact Explanation

An unprivileged transaction author can submit a CBOR-encoded native script with `m = -1` (or any negative value) as:

1. **A minting policy** — the policy always validates, so the attacker mints arbitrary quantities of tokens under that policy without any key signatures. This constitutes creation of native assets through an invalid ledger state transition.
2. **A payment credential** — a UTxO locked by such a script can be spent by anyone without providing any witnesses, enabling direct loss of ADA or native assets.
3. **A staking credential** — rewards accumulated under such a credential can be withdrawn without any witnesses, modifying withdrawals outside design parameters.

The `validateMultiSig` path confirms that script evaluation feeds directly into the UTXOW rule with no post-evaluation guard: [11](#0-10) 

This matches **Medium** impact (attacker-controlled scripts exceed intended validation limits, modifying minting and withdrawals outside design parameters) and potentially **Critical** impact (direct creation of native assets through an invalid ledger state transition).

---

### Likelihood Explanation

Exploitation requires only crafting a CBOR byte string with a negative integer in the `m` field of a `RequireMOf` constructor — e.g., encoding `[3, -1, [...]]`. No privileged access, key material, or consensus participation is needed. The CBOR integer type natively supports negative values, and the ledger binary library's `decodeInt` accepts them without restriction. Difficulty is low; any party who can submit a transaction can exploit this.

---

### Recommendation

In the CBOR decoders for `MultiSigRaw`, `TimelockRaw`, and `DijkstraNativeScriptRaw`, add a non-negativity check immediately after decoding `m`:

```haskell
m <- decCBOR
when (m < 0) $ fail "RequireMOf: threshold must be non-negative"
```

Alternatively, change the field type from `Int` to `Natural` (or `Word`) to enforce the constraint at the type level, matching the formal specification's `m ∈ ℕ`. The `decodeNatural` decoder already rejects negative values: [12](#0-11) 

---

### Proof of Concept

1. Construct a native script `RequireMOf (-1) [RequireSignature kh1, RequireSignature kh2]` by encoding the CBOR array `[3, -1, [[0, kh1_bytes], [0, kh2_bytes]]]`.
2. Compute the script hash and use it as a minting policy ID (or payment/staking credential).
3. Submit a transaction minting tokens under this policy with an **empty** witness set (`addrTxWits = {}`).
4. The ledger evaluates `isValidMOf (-1) [RequireSignature kh1, RequireSignature kh2]` → `(-1) <= 0` → `True`, and accepts the transaction without any signatures from `kh1` or `kh2`.
5. Tokens are minted (or UTxO spent, or rewards withdrawn) with zero valid signatures, violating the intended M-of-N threshold.

### Citations

**File:** eras/allegra/impl/src/Cardano/Ledger/Allegra/Scripts.hs (L183-185)
```haskell
  | TimelockMOf !Int !(StrictSeq (Timelock era))
  | -- Note that the Int may be negative in which case (TimelockMOf (-2) [..]) is always True
    TimelockTimeStart !SlotNo -- The start time
```

**File:** eras/allegra/impl/src/Cardano/Ledger/Allegra/Scripts.hs (L241-243)
```haskell
      decRaw 2 = Ann (SumD TimelockAnyOf) <*! D (sequence <$> decCBOR)
      decRaw 3 = Ann (SumD TimelockMOf) <*! Ann From <*! D (sequence <$> decCBOR)
      decRaw 4 = Ann (SumD TimelockTimeStart <! From)
```

**File:** eras/allegra/impl/src/Cardano/Ledger/Allegra/Scripts.hs (L487-489)
```haskell
    isValidMOf n SSeq.Empty = n <= 0
    isValidMOf n (ts SSeq.:<| tss) =
      n <= 0 || if go ts then isValidMOf (n - 1) tss else isValidMOf n tss
```

**File:** eras/shelley/impl/src/Cardano/Ledger/Shelley/Scripts.hs (L274-277)
```haskell
      3 -> do
        m <- decCBOR
        multiSigs <- sequence <$> decCBOR
        pure (3, MultiSigMOf m <$> multiSigs)
```

**File:** eras/shelley/impl/src/Cardano/Ledger/Shelley/Scripts.hs (L301-313)
```haskell
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

**File:** eras/shelley/impl/src/Cardano/Ledger/Shelley/Scripts.hs (L316-323)
```haskell
validateMultiSig ::
  (ShelleyEraScript era, EraTx era, NativeScript era ~ MultiSig era) =>
  Tx t era ->
  NativeScript era ->
  Bool
validateMultiSig tx =
  evalMultiSig $ Set.map witVKeyHash (tx ^. witsTxL . addrTxWitsL)
{-# INLINE validateMultiSig #-}
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Scripts.hs (L279-282)
```haskell
    3 -> do
      m <- decCBOR
      xs <- decCBOR
      pure (3, DijkstraRequireMOf m <$> sequence xs)
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Scripts.hs (L562-576)
```haskell
evalDijkstraNativeScript keyHashes (ValidityInterval txStart txExp) guards = go
  where
    -- the evaluation will stop as soon as it reaches the required number of valid scripts
    isValidMOf n SSeq.Empty = n <= 0
    isValidMOf n (ts SSeq.:<| tss) =
      n <= 0 || if go ts then isValidMOf (n - 1) tss else isValidMOf n tss
    go = \case
      RequireTimeStart lockStart -> lockStart `lteNegInfty` txStart
      RequireTimeExpire lockExp -> txExp `ltePosInfty` lockExp
      RequireSignature hash -> hash `Set.member` keyHashes
      RequireAllOf xs -> all go xs
      RequireAnyOf xs -> any go xs
      RequireMOf m xs -> isValidMOf m xs
      RequireGuard cred -> cred `OSet.member` guards
      _ -> error "Impossible: All NativeScripts should have been accounted for"
```

**File:** eras/shelley/formal-spec/multi-sig.tex (L751-754)
```tex
                -- ^ Minimum number of signatures required to unlock
                --   the output (should not exceed @length signatories@)
                --   n.b., should also check that this is >= 0
                }
```

**File:** eras/shelley/formal-spec/multi-sig.tex (L780-787)
```tex
      \var{msig} & \in & \type{RequireSig}~\KeyHash\\
      & \uniondistinct &
         \type{RequireAllOf}~[\ScriptMSig] \\
      & \uniondistinct&
         \type{RequireAnyOf}~[\ScriptMSig] \\
      & \uniondistinct&
        \type{RequireMOf}~\N~[\ScriptMSig]
    \end{array}
```

**File:** libs/cardano-ledger-binary/src/Cardano/Ledger/Binary/Decoding/DecCBOR.hs (L165-167)
```haskell
instance DecCBOR Int where
  decCBOR = decodeInt
  {-# INLINE decCBOR #-}
```

**File:** libs/cardano-ledger-binary/src/Cardano/Ledger/Binary/Decoding/Decoder.hs (L1479-1485)
```haskell
decodeNatural :: Decoder s Natural
decodeNatural = do
  !n <- decodeInteger
  if n >= 0
    then return $! fromInteger n
    else cborError $ DecoderErrorCustom "Natural" "got a negative number"
{-# INLINE decodeNatural #-}
```
