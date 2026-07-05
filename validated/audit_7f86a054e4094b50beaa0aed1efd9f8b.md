Looking at the production code in `eras/shelley/impl/src/Cardano/Ledger/Shelley/Scripts.hs`, I can trace every step of the claimed exploit path precisely.

**Step 1 — Type definition accepts negative `m`:**

`MultiSigMOf` stores `!Int`, not `!Natural` or `!Word`: [1](#0-0) 

**Step 2 — CBOR decoder has no non-negativity guard:**

The `decCBOR` for tag `3` decodes `m` as a plain `Int` with no bounds check: [2](#0-1) 

**Step 3 — `isValidMOf` trivially returns `True` for any negative `n`:**

```haskell
isValidMOf n StrictSeq.Empty = n <= 0
``` [3](#0-2) 

With `n = -1`, `(-1) <= 0` is `True` immediately, and the short-circuit `n <= 0 ||` on the cons case also fires immediately regardless of witnesses.

---

**However, the specific "deterministic split" framing in the question is incorrect.**

The question claims a split between "a node that enforces m >= 0" and one that does not. Examining the entire file, there is **no node in the current codebase that enforces `m >= 0`** — not at decode time, not in `evalMultiSig`, not in any STS rule. Every honest node running this code would decode and evaluate a `m = -1` script identically. There is no divergence between nodes; they all accept it. The "deterministic disagreement" impact category therefore does not apply.

**The real impact is unauthorized spending**, and it is conditional:**

For the exploit to cause loss of funds, a UTxO must already be locked at the address `hash(CBOR(RequireMOf (-1) scripts))`. This requires either:
- Social engineering: the attacker crafts a script that appears to be a legitimate multi-sig (e.g., `RequireMOf (-1) [RequireSignature alice, RequireSignature bob]`) and convinces a victim to lock funds at that address.
- A wallet bug that generates a negative `m`.

The attacker cannot retroactively apply a `m < 0` script to funds already locked under a legitimately constructed script address — the script hash must match the address.

---

### Title
Negative `m` accepted in `RequireMOf` allows zero-witness script satisfaction — (`eras/shelley/impl/src/Cardano/Ledger/Shelley/Scripts.hs`)

### Summary
`MultiSigMOf` stores `m` as `!Int`. The CBOR decoder applies no non-negativity check, and `isValidMOf` returns `True` for any `n <= 0` against an empty witness set. A script with `m = -1` is accepted by every node and satisfies with zero witnesses.

### Finding Description
- `MultiSigRaw` constructor `MultiSigMOf !Int !(StrictSeq (MultiSig era))` accepts any signed integer. [1](#0-0) 
- The `DecCBOR` instance for tag `3` calls `m <- decCBOR` with no guard. [4](#0-3) 
- `isValidMOf n Empty = n <= 0` and `isValidMOf n (x :<| xs) = n <= 0 || ...` both short-circuit to `True` when `n < 0`. [3](#0-2) 
- `evalMultiSig` passes `m` directly to `isValidMOf` with no pre-check. [5](#0-4) 

### Impact Explanation
Any UTxO locked at an address whose script encodes `m < 0` can be spent by anyone with zero witnesses. The impact is **direct loss of ADA** for any funds locked at such an address. The "deterministic disagreement" framing does not apply because all nodes behave identically — there is no split.

### Likelihood Explanation
**Low-Medium.** Exploitation requires funds to already reside at an address derived from a `m < 0` script. This demands either social engineering (attacker supplies the script to a victim) or a wallet-level bug. An attacker cannot redirect funds already locked under a legitimately constructed script. The barrier is meaningful but not cryptographic.

### Recommendation
1. Change `MultiSigMOf !Int` to `MultiSigMOf !Natural` (or `!Word`) in `MultiSigRaw`. [1](#0-0) 
2. Add an explicit non-negativity check in the `DecCBOR` instance for tag `3`, failing with `invalidKey` or a custom decoder error if `m < 0`. [6](#0-5) 
3. Update `mkRequireMOf` and the `ShelleyEraScript` class signature to use `Natural`/`Word` consistently. [7](#0-6) 

### Proof of Concept
```haskell
-- Encode RequireMOf with m = -1, empty script list
-- CBOR: array(3, -1, [])  →  83 03 20 80
let badCbor = BS.pack [0x83, 0x03, 0x20, 0x80]
case decodeFull shelleyProtVer badCbor :: Either DecoderError (MultiSig ShelleyEra) of
  Left _  -> putStrLn "SAFE: decoder rejected negative m"
  Right s -> do
    let result = evalMultiSig Set.empty s
    -- result == True  ← script validates with zero witnesses
    assertBool "VULNERABLE: negative m accepted and validates" (not result)
```

### Citations

**File:** eras/shelley/impl/src/Cardano/Ledger/Shelley/Scripts.hs (L103-103)
```haskell
    MultiSigMOf !Int !(StrictSeq (MultiSig era))
```

**File:** eras/shelley/impl/src/Cardano/Ledger/Shelley/Scripts.hs (L117-118)
```haskell
  mkRequireMOf :: Int -> StrictSeq (NativeScript era) -> NativeScript era
  getRequireMOf :: NativeScript era -> Maybe (Int, StrictSeq (NativeScript era))
```

**File:** eras/shelley/impl/src/Cardano/Ledger/Shelley/Scripts.hs (L273-278)
```haskell
        pure (2, MultiSigAnyOf <$> multiSigs)
      3 -> do
        m <- decCBOR
        multiSigs <- sequence <$> decCBOR
        pure (3, MultiSigMOf m <$> multiSigs)
      k -> invalidKey k
```

**File:** eras/shelley/impl/src/Cardano/Ledger/Shelley/Scripts.hs (L305-307)
```haskell
    isValidMOf n StrictSeq.Empty = n <= 0
    isValidMOf n (msig StrictSeq.:<| msigs) =
      n <= 0 || if go msig then isValidMOf (n - 1) msigs else isValidMOf n msigs
```

**File:** eras/shelley/impl/src/Cardano/Ledger/Shelley/Scripts.hs (L312-312)
```haskell
      RequireMOf m msigs -> isValidMOf m msigs
```
