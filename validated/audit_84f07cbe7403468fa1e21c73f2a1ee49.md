I need to carefully trace the exact code path to determine if this invariant can actually break.

### Title
`danglingVRFKeyHashes` Removal Ignores Reference Count, Allowing Post-v11 Duplicate VRF Registration — (`eras/shelley/impl/src/Cardano/Ledger/Shelley/Rules/PoolReap.hs`)

---

### Summary

`poolReapTransition` uses `Map.withoutKeys` to remove "dangling" VRF key hashes from `psVRFKeyHashes`. Because `psVRFKeyHashes` is a **reference-counted** map (`NonZero Word64`), this unconditional deletion is incorrect when the same VRF key is shared by more than one pool. The entry is deleted entirely even though other active pools still hold a reference to it, corrupting the map and allowing a new pool to register with that VRF key post-v11, bypassing the uniqueness guard.

---

### Finding Description

**Root cause — `Map.withoutKeys` vs. `removeVRFKeyHashOccurrence`**

`psVRFKeyHashes` is a reference-counted map: each entry's value is the number of pools currently using that VRF key. Two helper functions exist to maintain it correctly:

- `removeVRFKeyHashOccurrence` — decrements the count and removes the key only when the count reaches zero. [1](#0-0) 
- `Map.withoutKeys` — unconditionally deletes every key in the supplied set, ignoring the count entirely.

`poolReapTransition` uses the correct helper for **retired** pools but uses `Map.withoutKeys` for **dangling** VRF hashes (old VRF keys abandoned by re-registrations):

```haskell
& certPStateL . psVRFKeyHashesL
  %~ ( removeVRFKeyHashOccurrences retiredVRFKeyHashes   -- correct: decrements
         . (`Map.withoutKeys` danglingVRFKeyHashes)       -- BUG: deletes entirely
     )
``` [2](#0-1) 

**`danglingVRFKeyHashes` computation**

The set is built by finding pools whose current VRF (`spsVrfL`) differs from their pending future VRF (`sppVrfL`). Only pools present in **both** maps are considered; pools that share the same VRF but have no pending re-registration are silently dropped by `Map.dropMissing`:

```haskell
danglingVRFKeyHashes =
  Set.fromList $ Map.elems $
    Map.merge
      Map.dropMissing          -- pools only in psStakePools  → ignored
      Map.dropMissing          -- pools only in psFutureParams → ignored
      (Map.zipWithMaybeMatched $ \_ sps sppF ->
          if sps ^. spsVrfL /= sppF ^. sppVrfL
            then Just (sps ^. spsVrfL) else Nothing)
      (ps0 ^. psStakePoolsL)
      (ps0 ^. psFutureStakePoolParamsL)
``` [3](#0-2) 

If VRF `v` is shared by kh1 (which re-registers) and kh2 (which does not), only kh1 appears in the merge result, so `danglingVRFKeyHashes = {v}`. `Map.withoutKeys` then deletes `v` entirely, even though kh2 still holds a live reference.

**Re-registration path does not remove the old VRF from `psVRFKeyHashes`**

When kh1 re-registers with a fresh VRF `v2` post-v11, `updateFutureVRFKeyHash` only inserts `v2`; it does not decrement `v`. The comment in the code confirms the old VRF removal is intentionally deferred to POOLREAP:

```haskell
case Map.lookup sppId psFutureStakePoolParams of
  Nothing -> Map.insert sppVrf (knownNonZeroBounded @1)   -- adds v2, leaves v untouched
  ...
``` [4](#0-3) 

POOLREAP is therefore the sole place responsible for cleaning up `v`, and it does so incorrectly.

**Hard-fork population**

At the v11 hard fork, `populateVRFKeyHashes` correctly counts every pool in both `psStakePoolsL` and `psFutureStakePoolParamsL`, so `psVRFKeyHashes[v] = 2` after the fork when kh1 and kh2 both use `v`. [5](#0-4) 

**Post-POOLREAP uniqueness check bypass**

After `Map.withoutKeys` removes `v`, the new-pool registration guard at Pool.hs line 266 sees `Map.notMember v psVRFKeyHashes = True` and allows kh3 to register with `v`, even though kh2 is still active with that key. [6](#0-5) 

---

### Impact Explanation

The VRF uniqueness invariant introduced at v11 is violated: two active pools (kh2 and kh3) share the same VRF key post-v11. This is a design-parameter bypass — the ledger accepts a state it is explicitly designed to reject. The attacker must control the VRF private key `v` (they chose it for kh1), so they can produce blocks with both kh2 and kh3 using the same key.

The governance double-vote claim in the question is **not** directly enabled by this bug. SPO governance votes are keyed by `KeyHash StakePool`, not by VRF key hash; the attacker already has two distinct pool key hashes (kh2, kh3) and can vote twice regardless.

**Impact: Medium** — attacker-controlled certificates exceed the intended VRF-uniqueness validation limit, placing the ledger in a state that violates its own post-v11 invariant.

---

### Likelihood Explanation

The exploit requires:
1. Registering two pools with the same VRF key before v11 (explicitly allowed pre-v11).
2. Re-registering one of them with a new VRF after the v11 hard fork (a normal, unprivileged transaction).
3. Waiting one epoch for POOLREAP to run.
4. Registering a third pool with the original VRF (now incorrectly absent from `psVRFKeyHashes`).

All four steps are achievable by an unprivileged SPO submitting standard pool certificates. The hard fork is a scheduled protocol upgrade; the attacker does not need to influence it.

---

### Recommendation

Replace `Map.withoutKeys danglingVRFKeyHashes` with `removeVRFKeyHashOccurrences (Set.toList danglingVRFKeyHashes)` so that the dangling-VRF cleanup path uses the same reference-count-aware decrement logic already used for retired pools:

```haskell
& certPStateL . psVRFKeyHashesL
  %~ ( removeVRFKeyHashOccurrences retiredVRFKeyHashes
         . removeVRFKeyHashOccurrences (Set.toList danglingVRFKeyHashes)  -- was: Map.withoutKeys
     )
```

This ensures that when kh1 abandons VRF `v`, the count is decremented from 2 to 1 (reflecting kh2's continued use), rather than the entry being deleted outright.

---

### Proof of Concept

```
-- Pre-v11
RegPool kh1 v          -- psStakePools[kh1].spsVrf = v
RegPool kh2 v          -- psStakePools[kh2].spsVrf = v  (allowed pre-v11)

-- Hard fork to v11
enactHardForkV11       -- populateVRFKeyHashes: psVRFKeyHashes = {v: 2}

-- Post-v11
RegPool kh1 v2         -- psFutureStakePoolParams[kh1].sppVrf = v2
                       -- psVRFKeyHashes = {v: 2, v2: 1}  (v NOT decremented here)

-- Epoch boundary (POOLREAP)
passEpoch
-- danglingVRFKeyHashes = {v}  (kh1: spsVrf=v ≠ sppVrf=v2; kh2 absent from merge)
-- Map.withoutKeys {v} deletes v entirely
-- psVRFKeyHashes = {v2: 1}    ← BUG: kh2 still uses v

-- Bypass uniqueness check
RegPool kh3 v          -- Map.notMember v psVRFKeyHashes = True → accepted!
                       -- kh2 and kh3 now both active with VRF v post-v11

assert: psVRFKeyHashes[v] == 1  -- FAILS: v is absent
```

The invariant that should hold after POOLREAP — `∀ vrf ∈ psVRFKeyHashes, psVRFKeyHashes[vrf] = |{kh | psStakePools[kh].spsVrf = vrf}|` — is violated.

### Citations

**File:** eras/shelley/impl/src/Cardano/Ledger/Shelley/Rules/PoolReap.hs (L138-148)
```haskell
    danglingVRFKeyHashes =
      Set.fromList $
        Map.elems $
          Map.merge
            Map.dropMissing
            Map.dropMissing
            ( Map.zipWithMaybeMatched $ \_ sps sppF ->
                if sps ^. spsVrfL /= sppF ^. sppVrfL then Just (sps ^. spsVrfL) else Nothing
            )
            (ps0 ^. psStakePoolsL)
            (ps0 ^. psFutureStakePoolParamsL)
```

**File:** eras/shelley/impl/src/Cardano/Ledger/Shelley/Rules/PoolReap.hs (L224-227)
```haskell
          & certPStateL . psVRFKeyHashesL
            %~ ( removeVRFKeyHashOccurrences retiredVRFKeyHashes
                   . (`Map.withoutKeys` danglingVRFKeyHashes)
               )
```

**File:** eras/shelley/impl/src/Cardano/Ledger/Shelley/Rules/PoolReap.hs (L235-237)
```haskell
    removeVRFKeyHashOccurrence =
      -- Removes the key from the map if the value drops to 0
      Map.update (mapNonZero (\n -> n - 1))
```

**File:** eras/shelley/impl/src/Cardano/Ledger/Shelley/Rules/PoolReap.hs (L283-294)
```haskell

```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/HardFork.hs (L107-125)
```haskell
populateVRFKeyHashes :: PState era -> PState era
populateVRFKeyHashes pState =
  pState
    & psVRFKeyHashesL
      %~ accumulateVRFKeyHashes (pState ^. psStakePoolsL) (^. spsVrfL)
        . accumulateVRFKeyHashes (pState ^. psFutureStakePoolParamsL) (^. sppVrfL)
  where
    accumulateVRFKeyHashes ::
      Map (KeyHash StakePool) a ->
      (a -> VRFVerKeyHash StakePoolVRF) ->
      Map (VRFVerKeyHash StakePoolVRF) (NonZero Word64) ->
      Map (VRFVerKeyHash StakePoolVRF) (NonZero Word64)
    accumulateVRFKeyHashes spMap getVrf acc =
      Map.foldr' (addVRFKeyHashOccurrence . getVrf) acc spMap
    addVRFKeyHashOccurrence vrfKeyHash =
      Map.insertWith combine vrfKeyHash (knownNonZeroBounded @1)
      where
        -- Saturates at maxBound: if (+1) would overflow to 0, keep existing value
        combine _ oldVal = fromMaybe oldVal $ mapNonZero (+ 1) oldVal
```

**File:** eras/shelley/impl/src/Cardano/Ledger/Shelley/Rules/Pool.hs (L265-267)
```haskell
          when (hardforkConwayDisallowDuplicatedVRFKeys pv) $ do
            Map.notMember sppVrf psVRFKeyHashes
              ?! injectFailure (VRFKeyHashAlreadyRegistered sppId sppVrf)
```
