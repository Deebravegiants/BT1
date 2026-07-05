### Title
`Map.withoutKeys` Unconditionally Removes Shared VRF Key Hash Entries Instead of Decrementing Reference Count in POOLREAP — (`File: eras/shelley/impl/src/Cardano/Ledger/Shelley/Rules/PoolReap.hs`)

---

### Summary

In `poolReapTransition`, the secondary index `psVRFKeyHashesL` — a reference-counted `Map (VRFVerKeyHash StakePoolVRF) (NonZero Word64)` — is updated at every epoch boundary. When a pool re-registers with a new VRF key, the old ("dangling") VRF entry is removed from the map using `Map.withoutKeys`, which **deletes the entire entry regardless of its reference count**. This is the exact analog of the reported Solidity bug: a secondary tracking structure is not properly decremented on deletion, causing it to diverge from reality. After the v11 hardfork, if two pools share the same VRF key (registered before v11 when duplicates were allowed), and one re-registers with a new VRF, the shared VRF entry is wiped from `psVRFKeyHashesL` entirely. The other pool's VRF is now untracked, allowing a third pool to register with that VRF, bypassing the uniqueness constraint introduced in v11.

---

### Finding Description

`PState` holds a reference-counted secondary index:

```haskell
psVRFKeyHashes :: !(Map (VRFVerKeyHash StakePoolVRF) (NonZero Word64))
``` [1](#0-0) 

At the v11 hardfork, `populateVRFKeyHashes` populates this map by counting every VRF key hash across both `psStakePools` and `psFutureStakePoolParams`, correctly producing counts > 1 for pools that shared a VRF before v11:

```haskell
populateVRFKeyHashes pState =
  pState
    & psVRFKeyHashesL
      %~ accumulateVRFKeyHashes (pState ^. psStakePoolsL) (^. spsVrfL)
        . accumulateVRFKeyHashes (pState ^. psFutureStakePoolParamsL) (^. sppVrfL)
``` [2](#0-1) 

In `poolReapTransition`, at every epoch boundary, "dangling" VRF hashes (those belonging to pools that re-registered with a new VRF) are computed and then removed:

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
``` [3](#0-2) 

These dangling hashes are then removed from `psVRFKeyHashesL` using `Map.withoutKeys`:

```haskell
& certPStateL . psVRFKeyHashesL
  %~ ( removeVRFKeyHashOccurrences retiredVRFKeyHashes
         . (`Map.withoutKeys` danglingVRFKeyHashes)
     )
``` [4](#0-3) 

`Map.withoutKeys` removes the **entire entry** for each key in the set, regardless of the stored count. This is inconsistent with how retired pools are handled: `removeVRFKeyHashOccurrences` (used for `retiredVRFKeyHashes`) correctly decrements the count and only removes the entry when it reaches zero:

```haskell
removeVRFKeyHashOccurrence =
  -- Removes the key from the map if the value drops to 0
  Map.update (mapNonZero (\n -> n - 1))
``` [5](#0-4) 

**Concrete scenario:**

1. Before v11: Pool A (`kh1`) and Pool B (`kh2`) both register with VRF `v1` (allowed pre-v11).
2. v11 hardfork: `populateVRFKeyHashes` sets `psVRFKeyHashes[v1] = 2`.
3. After v11: Pool B re-registers with new VRF `v2`. In `Pool.hs`, `updateFutureVRFKeyHash` inserts `v2 → 1` into `psVRFKeyHashes`. `psFutureStakePoolParams[kh2]` now holds params with `v2`.
4. Epoch boundary (`POOLREAP`): `danglingVRFKeyHashes = {v1}` (Pool B's current VRF `v1` ≠ future VRF `v2`). `Map.withoutKeys {v1}` removes `v1` entirely from `psVRFKeyHashes`. Pool A still has `v1` in `psStakePools`, but `v1` is now absent from the tracking map.
5. Pool C submits a `RegPool` certificate with VRF `v1`. The uniqueness check `Map.notMember v1 psVRFKeyHashes` passes (because `v1` was incorrectly wiped). Pool C is registered with `v1`.
6. Pool A and Pool C now both hold VRF `v1`, violating the uniqueness invariant.

The re-registration certificate in step 3 is the attacker-controlled entry point. An operator of Pool B (or any pool with a shared VRF) can trigger this by submitting a `RegPool` certificate with a new VRF key. [6](#0-5) 

---

### Impact Explanation

**Medium.** An attacker-controlled pool re-registration certificate causes the VRF uniqueness validation introduced in v11 to be bypassed. A third pool can then register with a VRF key hash already held by an existing pool, exceeding the intended validation limit. Two pools sharing the same VRF key hash produce identical slot-leadership proofs for the same slots, which can cause honest nodes to accept conflicting blocks and diverge.

---

### Likelihood Explanation

**Medium.** The precondition — two pools sharing a VRF key hash — was possible on mainnet before v11 (the uniqueness check did not exist). The test suite explicitly covers this case (`"Retiring a stake pool with a duplicate VRF Keyhash after v11 HardFork"`). Any pool operator who co-registered with a duplicate VRF before v11 and subsequently re-registers with a new VRF after v11 will silently corrupt the tracking map, enabling the bypass. [7](#0-6) 

---

### Recommendation

Replace `Map.withoutKeys danglingVRFKeyHashes` with `removeVRFKeyHashOccurrences (Set.toList danglingVRFKeyHashes)` so that the reference count is decremented by one per re-registering pool, not wiped entirely:

```diff
  & certPStateL . psVRFKeyHashesL
    %~ ( removeVRFKeyHashOccurrences retiredVRFKeyHashes
-          . (`Map.withoutKeys` danglingVRFKeyHashes)
+          . removeVRFKeyHashOccurrences (Set.toList danglingVRFKeyHashes)
       )
```

This mirrors the correct treatment already applied to `retiredVRFKeyHashes` and ensures that a VRF entry is only removed from `psVRFKeyHashesL` when no remaining pool holds it.

---

### Proof of Concept

```
State before epoch boundary (after v11 hardfork):
  psStakePools         = { kh1 → StakePoolState{spsVrf=v1, ...}
                         , kh2 → StakePoolState{spsVrf=v1, ...} }
  psFutureStakePoolParams = { kh2 → StakePoolParams{sppVrf=v2, ...} }
  psVRFKeyHashes       = { v1 → 2, v2 → 1 }

poolReapTransition computes:
  danglingVRFKeyHashes = { v1 }   -- kh2's current VRF v1 ≠ future VRF v2

Applies Map.withoutKeys { v1 }:
  psVRFKeyHashes       = { v2 → 1 }   -- v1 FULLY REMOVED (count was 2, should be 1)

State after epoch boundary:
  psStakePools         = { kh1 → StakePoolState{spsVrf=v1, ...}
                         , kh2 → StakePoolState{spsVrf=v2, ...} }
  psVRFKeyHashes       = { v2 → 1 }   -- v1 missing despite kh1 still holding it

Next transaction: RegPool kh3 with sppVrf=v1
  Check: Map.notMember v1 psVRFKeyHashes  →  True  (BUG: should be False)
  Result: kh3 registered with v1; psVRFKeyHashes = { v1 → 1, v2 → 1 }
  kh1 and kh3 now share VRF v1 — uniqueness invariant violated.
```

### Citations

**File:** libs/cardano-ledger-core/src/Cardano/Ledger/State/CertState.hs (L232-234)
```haskell
data PState era = PState
  { psVRFKeyHashes :: !(Map (VRFVerKeyHash StakePoolVRF) (NonZero Word64))
  -- ^ VRF key hashes that have been registered via PoolParams
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

**File:** eras/shelley/impl/src/Cardano/Ledger/Shelley/Rules/Pool.hs (L278-306)
```haskell
        Just stakePoolState -> do
          when (hardforkConwayDisallowDuplicatedVRFKeys pv) $ do
            sppVrf == stakePoolState ^. spsVrfL
              || Map.notMember sppVrf psVRFKeyHashes
                ?! injectFailure (VRFKeyHashAlreadyRegistered sppId sppVrf)
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

**File:** eras/conway/impl/testlib/Test/Cardano/Ledger/Conway/Imp/HardForkSpec.hs (L54-85)
```haskell
  it "Retiring a stake pool with a duplicate VRF Keyhash after v11 HardFork" $ do
    whenMajorVersion @10 $ do
      -- register two pools with the same vrf keyhash before the hard fork
      (kh1, vrf) <- (,) <$> freshKeyHash <*> freshKeyHashVRF
      registerStakePool kh1 vrf
      kh2 <- freshKeyHash
      registerStakePool kh2 vrf
      kh3 <- freshKeyHash
      registerStakePool kh3 vrf

      enactHardForkV11
      expectVRFs [(vrf, 3)]
      -- retire one of the pools after the hard fork
      retireStakePool kh1 (EpochInterval 1)
      retireStakePool kh2 (EpochInterval 1)
      passEpoch
      -- the vrf keyhash should still be present, since another pool is registered with it
      expectVRFs [(vrf, 1)]

      -- registration of the same vrf should be disallowed
      kh4 <- freshKeyHash
      registerStakePoolTx kh4 vrf >>= \tx ->
        submitFailingTx
          tx
          [injectFailure $ Shelley.VRFKeyHashAlreadyRegistered kh4 vrf]

      retireStakePool kh3 (EpochInterval 1)
      passEpoch
      expectVRFs []

      registerStakePool kh4 vrf
      expectVRFs [(vrf, 1)]
```
