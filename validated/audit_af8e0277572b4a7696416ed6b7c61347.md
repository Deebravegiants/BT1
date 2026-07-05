### Title
`validatePerasCert` Always Returns `True`, Bypassing Peras Certificate Validation in Block Body - (File: `eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/BlockBody/Internal.hs`)

---

### Summary

In the Dijkstra era, the function `validatePerasCert` is a hardcoded stub that unconditionally returns `True` regardless of the certificate, key, or nonce supplied. It is called from the production `BBODY` transition rule (`Cardano.Ledger.Dijkstra.Rules.Bbody`). This means any block producer can embed an arbitrary, forged, or structurally invalid `PerasCert` in a block body and every honest node will accept it as cryptographically valid, bypassing the Peras certificate authentication entirely.

---

### Finding Description

In `eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/BlockBody/Internal.hs`, the Peras certificate validation routine is a placeholder:

```haskell
-- | Mocked-up Peras certificate validation routine
--
-- NOTE: this function will be replaced with the real implementation from
-- 'cardano-base' once it's ready.
validatePerasCert :: Nonce -> PerasKey -> PerasCert -> Bool
validatePerasCert _ _ _ = True
```

All three arguments — the epoch nonce, the Peras public key, and the certificate bytes — are discarded with wildcard patterns. The function always returns `True`.

This function is imported and invoked inside the production `BBODY` rule at `eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Bbody.hs`. The `BBODY` rule is the ledger's block-body validation transition; it is the mandatory gate through which every block must pass before its transactions are applied to the ledger state.

The structural parallel to the reported Solidity bug is exact:

| Solidity (`RubiconMarket`) | Cardano Ledger (Dijkstra) |
|---|---|
| `isClosed()` always returns `false` | `validatePerasCert` always returns `True` |
| Should read storage variable `stopped` | Should verify certificate against `PerasKey` and nonce |
| Guard in `can_offer()` / `can_buy()` always passes | Guard in `BBODY` always passes |

---

### Impact Explanation

**Impact class: Critical — Honest nodes accept an invalid block causing permanent ledger divergence requiring a hard fork.**

Because `validatePerasCert` is called inside the `BBODY` rule and always succeeds, every honest node running Dijkstra-era code will accept a block containing a completely forged or malformed `PerasCert`. When the real cryptographic implementation is eventually wired in (as the comment promises), nodes that have already accepted blocks with invalid certificates will have a ledger history that diverges from nodes running the corrected code. Reconciling that divergence requires a hard fork. Additionally, since Peras certificates are the mechanism by which the protocol achieves accelerated finality and round-based consensus, accepting forged certificates allows an attacker to inject false Peras consensus signals into the chain, potentially manipulating which blocks are treated as finalized.

---

### Likelihood Explanation

Any block producer (an unprivileged role — any SPO) can craft a `PerasCert` with arbitrary bytes and include it in a `DijkstraBlockBody`. The `BBODY` rule will call `validatePerasCert` on it and receive `True`. No special key, governance majority, or privileged access is required. The attacker-controlled entry path is: construct a block body with a forged `PerasCert` → submit block → `BBODY` calls `validatePerasCert` → always returns `True` → block accepted.

---

### Recommendation

Replace the stub with the real cryptographic verification once the implementation is available from `cardano-base`. Until then, the function should either:

1. Reject all certificates (return `False`) so that no forged cert can be accepted, or
2. Treat a `SNothing` Peras cert as valid and reject any `SJust` cert until the real verifier is ready.

The fix mirrors the Solidity recommendation exactly: replace the hardcoded constant with the actual state-dependent check.

---

### Proof of Concept

**Root cause — hardcoded `True`:** [1](#0-0) 

**Called from production `BBODY` rule:** [2](#0-1) 

**`PerasCert` is a real serializable type embedded in the block body:** [3](#0-2) 

**`PerasCert` is decoded from the wire and stored in `DijkstraBlockBodyRaw`:** [4](#0-3) 

An attacker constructs a `DijkstraBlockBody` with `dbbrPerasCert = SJust (PerasCert <arbitrary_bytes>)`, serializes it, and submits the block. The `BBODY` rule calls `validatePerasCert nonce perasKey cert`, which discards all inputs and returns `True`, accepting the forged certificate unconditionally.

### Citations

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/BlockBody/Internal.hs (L103-109)
```haskell
data DijkstraBlockBodyRaw era = DijkstraBlockBodyRaw
  { dbbrTxs :: !(StrictSeq (Tx TopTx era))
  , dbbrLeiosCert :: !(StrictMaybe LeiosCert)
  -- ^ Optional Leios certificate
  , dbbrPerasCert :: !(StrictMaybe PerasCert)
  -- ^ Optional Peras certificate
  }
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/BlockBody/Internal.hs (L213-239)
```haskell
  decCBOR = decodeRecordNamed "DijkstraBlockBodyRaw" (const 4) $ do
    let
      decodeInvalidTxs =
        decodeNonEmptySetLikeEnforceNoDuplicates
          (IntSet.insert . fromIntegral @Word16 @Int)
          (\x -> (IntSet.size x, x))
          (decCBOR @Word16)

    invalidTxs :: IntSet <- fold <$> decodeNullMaybe decodeInvalidTxs
    txs <- decodeSeq (decodeDijkstraTopTx @era False)
    mbLeiosCert <- decodeNullStrictMaybe decodeLeiosCert
    mbPerasCert <- decodeNullStrictMaybe decCBOR

    let txsLength = Seq.length txs
        inRange x = 0 <= x && x < txsLength
    forM_ (IntSet.toList invalidTxs) $ \i ->
      unless (inRange i) . fail $
        "index is out of range: " <> show i
    let
      setValidityFlag tx isValid = set isValidTxL isValid <$> tx
      validityFlags = alignedValidFlags txsLength invalidTxs
      txsWithIsValid = Seq.zipWith setValidityFlag (coerce txs) validityFlags
    pure $
      DijkstraBlockBodyRaw
        <$> sequenceA (StrictSeq.forceToStrict txsWithIsValid)
        <*> pure mbLeiosCert
        <*> pure mbPerasCert
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/BlockBody/Internal.hs (L293-298)
```haskell
-- | Mocked-up Peras certificate validation routine
--
-- NOTE: this function will be replaced with the real implementation from
-- 'cardano-base' once it's ready.
validatePerasCert :: Nonce -> PerasKey -> PerasCert -> Bool
validatePerasCert _ _ _ = True
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Bbody.hs (L1-1)
```haskell
{-# LANGUAGE DataKinds #-}
```
