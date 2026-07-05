### Title
`psVRFKeyHashes` Reference Count Zeroed Instead of Decremented on Pool Re-Registration, Enabling Post-v11 VRF Uniqueness Bypass — (File: `eras/shelley/impl/src/Cardano/Ledger/Shelley/Rules/PoolReap.hs`)

---

### Summary

In `poolReapTransition`, when a pool re-registers with a fresh VRF key, the old VRF's entry in `psVRFKeyHashes` is removed entirely via `Map.withoutKeys danglingVRFKeyHashes` instead of being decremented. If the old VRF has a reference count > 1 — possible for legacy pools that shared a VRF before the v11 hard fork — the entry is incorrectly zeroed out. This allows a new pool to register with the "freed" VRF, bypassing the post-v11 VRF uniqueness invariant and enabling duplicate VRF key registrations.

---

### Finding Description

`PState.psVRFKeyHashes :: Map (VRFVerKeyHash StakePoolVRF) (NonZero Word64)` tracks how many registered pools use each VRF key hash. [1](#0-0) 

The count is maintained in three places:

**1. New pool registration** — always inserts with count 1 (correct for post-v11 where duplicates are rejected): [2](#0-1) 

**2. Pool retirement** — correctly decrements via `removeVRFKeyHashOccurrences`: [3](#0-2) 

**3. Pool re-registration with a fresh VRF ("dangling" VRF removal)** — **incorrectly removes the entire entry**: [4](#0-3) 

The `danglingVRFKeyHashes` set contains old VRF hashes that a pool is abandoning in favor of a new VRF. The intent (per the comment "no longer relevant, since they have been overwritten via pool re-registration") is to remove VRFs that are no longer used. But `Map.withoutKeys` removes the entire map entry regardless of the count value.

Before v11, duplicate VRF registrations were allowed. The `populateVRFKeyHashes` migration at the v11 hard fork correctly sets counts > 1 for VRFs shared by multiple legacy pools: [5](#0-4) 

After v11, new duplicate registrations are rejected by the check: [6](#0-5) 

**The bug**: if pool A (VRF X, count = 2 in `psVRFKeyHashes`) re-registers with VRF Y, `danglingVRFKeyHashes = {VRF X}`, and `Map.withoutKeys` removes VRF X entirely. Pool B still uses VRF X, but `psVRFKeyHashes` no longer contains it. The uniqueness check `Map.notMember sppVrf psVRFKeyHashes` now passes for VRF X, allowing pool C to register with VRF X.

The asymmetry is clear: retired pools use `removeVRFKeyHashOccurrences` (decrement), but dangling VRFs use `Map.withoutKeys` (full removal). The `removeVRFKeyHashOccurrence` helper itself correctly handles the count-to-zero case: [7](#0-6) 

---

### Impact Explanation

The VRF uniqueness invariant introduced in v11 is bypassed. Two pools (B and C) now share VRF X. In Praos leader election, both pools independently compute VRF proofs using the same key and are elected as slot leaders for the same slots. Both produce valid blocks for those slots. Honest nodes receive two valid competing blocks for the same slot, causing a deterministic fork in the chain that all honest nodes must resolve identically — a **High** impact deterministic disagreement arising directly from incorrect ledger rule evaluation in `POOLREAP`.

---

### Likelihood Explanation

Requires: (1)

### Citations

**File:** libs/cardano-ledger-core/src/Cardano/Ledger/State/CertState.hs (L233-233)
```haskell
  { psVRFKeyHashes :: !(Map (VRFVerKeyHash StakePoolVRF) (NonZero Word64))
```

**File:** eras/shelley/impl/src/Cardano/Ledger/Shelley/Rules/Pool.hs (L265-267)
```haskell
          when (hardforkConwayDisallowDuplicatedVRFKeys pv) $ do
            Map.notMember sppVrf psVRFKeyHashes
              ?! injectFailure (VRFKeyHashAlreadyRegistered sppId sppVrf)
```

**File:** eras/shelley/impl/src/Cardano/Ledger/Shelley/Rules/Pool.hs (L268-276)
```haskell
          let updateVRFKeyHash
                | hardforkConwayDisallowDuplicatedVRFKeys pv = Map.insert sppVrf (knownNonZeroBounded @1)
                | otherwise = id
          tellEvent $ injectEvent $ RegisterPool sppId
          pure $
            ps
              & psStakePoolsL
                %~ Map.insert sppId (mkStakePoolState (pp ^. ppPoolDepositCompactL) mempty stakePoolParams)
              & psVRFKeyHashesL %~ updateVRFKeyHash
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

**File:** eras/shelley/impl/src/Cardano/Ledger/Shelley/Rules/PoolReap.hs (L235-237)
```haskell
    removeVRFKeyHashOccurrence =
      -- Removes the key from the map if the value drops to 0
      Map.update (mapNonZero (\n -> n - 1))
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
