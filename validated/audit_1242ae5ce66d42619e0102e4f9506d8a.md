Let me read the full POOLREAP transition and the re-registration branch more carefully to trace the exact logic.

I now have all the code needed for a definitive trace. Let me walk through each step precisely.

---

**Step 1 — `populateVRFKeyHashes` at v11 hardfork**

`populateVRFKeyHashes` (HardFork.hs:107-125) counts VRF keys from both `psStakePools` and `psFutureStakePoolParams`. With P1 and P2 both in `psStakePools` using VRF_X: `psVRFKeyHashes[VRF_X] = 2`.

**Step 2 — P1 re-registers with VRF_Y (Pool.hs:283-306)**

Re-registration branch, first re-registration (no prior future params):
```haskell
case Map.lookup sppId psFutureStakePoolParams of
  Nothing -> Map.insert sppVrf (knownNonZeroBounded @1)
```
This inserts `VRF_Y → 1` but does **not touch VRF_X**. After: `psVRFKeyHashes = {VRF_X: 2, VRF_Y: 1}`, `psFutureStakePoolParams = {P1: {sppVrf: VRF_Y}}`.

**Step 3 — POOLREAP computes `danglingVRFKeyHashes` (PoolReap.hs:138-148)**

```haskell
danglingVRFKeyHashes =
  Set.fromList $ Map.elems $
    Map.merge
      Map.dropMissing   -- drop pools only in psStakePools (P2 is dropped here)
      Map.dropMissing   -- drop pools only in psFutureStakePoolParams
      (Map.zipWithMaybeMatched $ \_ sps sppF ->
          if sps ^. spsVrfL /= sppF ^. sppVrfL then Just (sps ^. spsVrfL) else Nothing)
      (ps0 ^. psStakePoolsL)
      (ps0 ^. psFutureStakePoolParamsL)
```

- P1 is in both maps: current VRF_X ≠ future VRF_Y → `Just VRF_X`
- P2 is only in `psStakePools`, not in `psFutureStakePoolParams` → **dropped by `Map.dropMissing`**
- Result: `danglingVRFKeyHashes = {VRF_X}`

**Step 4 — `Map.withoutKeys` removes VRF_X entirely (PoolReap.hs:224-227)**

```haskell
& certPStateL . psVRFKeyHashesL
  %~ ( removeVRFKeyHashOccurrences retiredVRFKeyHashes
         . (`Map.withoutKeys` danglingVRFKeyHashes)
     )
```

`Map.withoutKeys psVRFKeyHashes {VRF_X}` deletes the entire `VRF_X` entry regardless of its count being 2. After: `psVRFKeyHashes = {VRF_Y: 1}`. P2 still holds VRF_X in `psStakePools` but it is no longer tracked.

**Step 5 — New pool P3 registers with VRF_X (Pool.hs:265-267)**

```haskell
when (hardforkConwayDisallowDuplicatedVRFKeys pv) $ do
  Map.notMember sppVrf psVRFKeyHashes
    ?! injectFailure (VRFKeyHashAlreadyRegistered sppId sppVrf)
```

`Map.notMember VRF_X psVRFKeyHashes = True` → check passes → P3 registers with VRF_X. P2 and P3 now share VRF_X with no tracking in `psVRFKeyHashes`.

**Root cause**: `Map.withoutKeys` is a bulk-delete that ignores reference counts. The correct operation for `danglingVRFKeyHashes` is the same reference-count decrement used for retired pools (`removeVRFKeyHashOccurrences`), not a full key removal.

---

### Title
VRF Key Reference Count Corrupted by `Map.withoutKeys` in POOLREAP — (`eras/shelley/impl/src/Cardano/Ledger/Shelley/Rules/PoolReap.hs`)

### Summary
`poolReapTransition` uses `Map.withoutKeys` to remove "dangling" VRF key hashes when a pool re-registers with a new VRF key. This unconditionally deletes the entire map entry regardless of the reference count, corrupting the `psVRFKeyHashes` invariant when the same VRF key is shared by multiple pools (a valid pre-v11 state). After the deletion, the VRF uniqueness guard in `poolTransition` no longer sees the key, allowing a new pool to register with a VRF key that is still actively used by another pool.

### Finding Description

`populateVRFKeyHashes` (called at the v11 hardfork) correctly initialises reference counts: [1](#0-0) 

If two pools P1 and P2 share VRF_X, the count is set to 2.

When P1 re-registers with VRF_Y, the re-registration branch in `poolTransition` inserts VRF_Y with count 1 but leaves VRF_X's count unchanged (it is deferred to POOLREAP): [2](#0-1) 

At POOLREAP, `danglingVRFKeyHashes` is computed as the set of old VRF keys for pools that have a pending re-registration with a different VRF. Because `Map.dropMissing` is used on both sides of the merge, P2 (which has no future params) is excluded — only P1's old VRF_X is collected: [3](#0-2) 

The removal then uses `Map.withoutKeys`, which deletes the entire entry for VRF_X regardless of its count: [4](#0-3) 

Compare with the correct decrement-by-one logic used for retired pools: [5](#0-4) 

After POOLREAP, `psVRFKeyHashes` no longer contains VRF_X, so the uniqueness guard in `poolTransition` passes for any new pool attempting to register with VRF_X: [6](#0-5) 

### Impact Explanation

The VRF uniqueness invariant — that `psVRFKeyHashes[vrf]` equals the count of active+future pools using that VRF — is broken. A new pool P3 can register with VRF_X while P2 still actively uses it. Both pools will be elected as slot leaders for the same slots (identical VRF outputs), undermining the slot-leadership uniqueness guarantee of Ouroboros Praos and allowing an attacker to register a pool that shadows an existing pool's VRF-based slot claims. This bypasses an intended validation limit introduced at protocol version 11 via attacker-controlled `RegPool` certificates.

### Likelihood Explanation

The preconditions are realistic and reachable on mainnet:
- Pre-v11, VRF key sharing across pools was permitted and may exist in the live state.
- `populateVRFKeyHashes` at the v11 hardfork correctly records those shared counts.
- A single unprivileged pool operator controlling P1 submits one `RegPool` certificate (re-registration with a new VRF). No governance majority, no key compromise, no Sybil attack is required.
- The bug fires deterministically at the next POOLREAP epoch boundary.

### Recommendation

Replace `Map.withoutKeys danglingVRFKeyHashes` with `removeVRFKeyHashOccurrences (Set.toList danglingVRFKeyHashes)` so that each dangling VRF key has its reference count decremented by exactly 1, consistent with how retired-pool VRF keys are handled. The entry is only removed when the count reaches zero.

```haskell
-- current (buggy)
%~ ( removeVRFKeyHashOccurrences retiredVRFKeyHashes
       . (`Map.withoutKeys` danglingVRFKeyHashes)
   )

-- fixed
%~ ( removeVRFKeyHashOccurrences retiredVRFKeyHashes
       . removeVRFKeyHashOccurrences (Set.toList danglingVRFKeyHashes)
   )
```

### Proof of Concept

State test (pseudo-Haskell, mirrors the existing `HardForkSpec` pattern):

```
1. Register P1 and P2 both with VRF_X (pre-v11).
2. Enact hardfork to v11.
   → psVRFKeyHashes = {VRF_X: 2}
3. P1 submits RegPool with VRF_Y (re-registration).
   → psVRFKeyHashes = {VRF_X: 2, VRF_Y: 1}
   → psFutureStakePoolParams = {P1: {sppVrf: VRF_Y}}
4. passEpoch  -- POOLREAP fires
   → danglingVRFKeyHashes = {VRF_X}
   → Map.withoutKeys removes VRF_X entirely
   → psVRFKeyHashes = {VRF_Y: 1}   -- BUG: should be {VRF_X: 1, VRF_Y: 1}
5. Register P3 with VRF_X.
   → Map.notMember VRF_X psVRFKeyHashes = True  → check passes
   → P2 and P3 now share VRF_X with no tracking
6. Assert psVRFKeyHashes[VRF_X] == 1  -- FAILS (key absent)
```

### Citations

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

**File:** eras/shelley/impl/src/Cardano/Ledger/Shelley/Rules/Pool.hs (L283-306)
```haskell
          let updateFutureVRFKeyHash
                | hardforkConwayDisallowDuplicatedVRFKeys pv =
                    -- If a pool re-registers with a fresh VRF, we have to record it in the map,
                    -- but also remove the previous VRFHashKey potentially stored in previous re-registration within the same epoch,
                    -- which we retrieve from futureStakePools.
                    case Map.lookup sppId psFutureStakePoolParams of
                      Nothing -> Map.insert sppVrf (knownNonZeroBounded @1)
                      Just futureStakePoolParams
                        | futureStakePoolParams ^. sppVrfL /= sppVrf ->
                            Map.insert sppVrf (knownNonZeroBounded @1)
                              . Map.delete (futureStakePoolParams ^. sppVrfL)
                        | otherwise -> id
                | otherwise = id
          tellEvent $ injectEvent $ ReregisterPool sppId
          -- This `sppId` is already registered, so we want to reregister it.
          -- That means adding it to the futureStakePoolParams or overriding it  with the new 'poolParams'.
          -- We must also unretire it, if it has been scheduled for retirement.
          -- The deposit does not change.
          pure $
            ps
              & psFutureStakePoolParamsL
                %~ Map.insert sppId stakePoolParams
              & psRetiringL %~ Map.delete sppId
              & psVRFKeyHashesL %~ updateFutureVRFKeyHash
```

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

**File:** eras/shelley/impl/src/Cardano/Ledger/Shelley/Rules/PoolReap.hs (L230-237)
```haskell
    removeVRFKeyHashOccurrences ::
      [VRFVerKeyHash StakePoolVRF] ->
      Map (VRFVerKeyHash StakePoolVRF) (NonZero Word64) ->
      Map (VRFVerKeyHash StakePoolVRF) (NonZero Word64)
    removeVRFKeyHashOccurrences vrfs vrfsMap = F.foldl' (flip removeVRFKeyHashOccurrence) vrfsMap vrfs
    removeVRFKeyHashOccurrence =
      -- Removes the key from the map if the value drops to 0
      Map.update (mapNonZero (\n -> n - 1))
```
