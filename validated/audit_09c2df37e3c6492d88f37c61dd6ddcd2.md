### Title
`poolReapTransition` Unconditionally Deletes Shared VRF Key Hash Entry on Pool Re-registration, Allowing Post-v11 VRF Uniqueness Bypass - (`eras/shelley/impl/src/Cardano/Ledger/Shelley/Rules/PoolReap.hs`)

---

### Summary

In `poolReapTransition`, when a pool re-registers with a new VRF key, the old VRF key hash is removed **entirely** from `psVRFKeyHashes` via `Map.withoutKeys danglingVRFKeyHashes`, regardless of the reference count stored in that map. This is structurally identical to the external report's bug: one tracking structure (`psVRFKeyHashes`) is updated incorrectly while the other (`psStakePools`) retains the stale reference, creating a state inconsistency. The consequence is that the post-v11 VRF key uniqueness check can be bypassed, allowing a new pool to register with a VRF key still actively used by another pool.

---

### Finding Description

`psVRFKeyHashes` is a `Map (VRFVerKeyHash StakePoolVRF) (NonZero Word64)` that tracks how many registered pools use each VRF key hash. It was introduced at the v11 hard fork via `populateVRFKeyHashes`, which counts every occurrence across both `psStakePools` and `psFutureStakePoolParams`. The count is used to enforce uniqueness: a new pool registration is rejected if its VRF hash is already present in `psVRFKeyHashes`. [1](#0-0) 

At the epoch boundary, `poolReapTransition` computes `danglingVRFKeyHashes` — the set of old VRF hashes belonging to pools that re-registered with a new VRF during the epoch: [2](#0-1) 

It then applies this set to `psVRFKeyHashes` using `Map.withoutKeys`, which **deletes the key entirely** from the map: [3](#0-2) 

The same file already defines `removeVRFKeyHashOccurrences` / `removeVRFKeyHashOccurrence`, which correctly **decrements** the count and only removes the key when it reaches zero: [4](#0-3) 

`Map.withoutKeys` is correct only when the count is exactly 1. When the count is ≥ 2 (i.e., multiple pools share the same VRF hash — a state that is valid and explicitly handled by `populateVRFKeyHashes` at the v11 hard fork), the entire entry is deleted even though other pools still reference that VRF hash. This leaves `psStakePools` containing pools whose VRF hash is no longer tracked in `psVRFKeyHashes`, breaking the invariant that `psVRFKeyHashes` reflects the true reference count of every VRF hash in use.

The v11 hard fork explicitly accounts for pre-existing duplicate VRF registrations by counting them: [5](#0-4) 

The test in `HardForkSpec.hs` confirms that after v11, retiring two of three pools sharing a VRF correctly leaves count = 1: [6](#0-5) 

However, no test covers the re-registration path with a shared VRF, which is the vulnerable path.

---

### Impact Explanation

**Medium. Attacker-controlled pool registration certificates exceed intended validation limits.**

After the bug is triggered, `psVRFKeyHashes` no longer contains a VRF hash that is still actively used by a registered pool. The uniqueness check at new pool registration time (`Map.notMember sppVrf psVRFKeyHashes`) then passes for that VRF hash, allowing a new pool to register with it. This bypasses the post-v11 invariant that each VRF key hash is used by at most one pool. Two pools sharing a VRF key are both elected as slot leaders at identical slots (since slot leadership is determined by `VRF(vrf_key, nonce, slot) < threshold`), enabling the attacker's pool to produce competing blocks at every slot the victim pool is elected, diverting block rewards outside design parameters.

---

### Likelihood Explanation

The precondition is that two pools share a VRF hash in a state that survived the v11 hard fork (i.e., they were registered before v11 when duplicates were permitted). This is a realistic historical state on mainnet. After v11, any operator of one of those pools can trigger the bug by submitting a single re-registration certificate with a fresh VRF key. The subsequent registration of a new pool with the freed VRF hash requires only a standard pool registration certificate. Both operations are fully within the capability of an unprivileged transaction sender (pool operator).

---

### Recommendation

Replace the unconditional `Map.withoutKeys danglingVRFKeyHashes` with the existing `removeVRFKeyHashOccurrences` helper, converting the set to a list:

```haskell
-- Before (buggy):
& certPStateL . psVRFKeyHashesL
  %~ ( removeVRFKeyHashOccurrences retiredVRFKeyHashes
         . (`Map.withoutKeys` danglingVRFKeyHashes)
     )

-- After (fixed):
& certPStateL . psVRFKeyHashesL
  %~ ( removeVRFKeyHashOccurrences retiredVRFKeyHashes
         . removeVRFKeyHashOccurrences (Set.toList danglingVRFKeyHashes)
     )
```

This mirrors the correct pattern already used for `retiredVRFKeyHashes` and ensures the count is decremented rather than the entry deleted outright, preserving the invariant when multiple pools share a VRF hash.

---

### Proof of Concept

**Setup (before v11):**
```
Register Pool A: (kh1, vrf1)   -- psVRFKeyHashes not yet populated
Register Pool B: (kh2, vrf1)   -- duplicate VRF allowed pre-v11
```

**v11 hard fork — `populateVRFKeyHashes` runs:**
```
psVRFKeyHashes = { vrf1 → 2 }
psStakePools   = { kh1 → {vrf: vrf1, ...}, kh2 → {vrf: vrf1, ...} }
```

**Pool A re-registers with vrf2 (within the epoch, before epoch boundary):**
```
psFutureStakePoolParams = { kh1 → {vrf: vrf2, ...} }
psVRFKeyHashes          = { vrf1 → 2, vrf2 → 1 }   -- vrf2 added, vrf1 unchanged
``` [7](#0-6) 

**Epoch boundary — `poolReapTransition` runs:**
```
danglingVRFKeyHashes = { vrf1 }   -- kh1's old VRF differs from future VRF
Map.withoutKeys { vrf1 } applied:
  psVRFKeyHashes = { vrf2 → 1 }   -- vrf1 DELETED entirely, count was 2
  psStakePools   = { kh1 → {vrf: vrf2}, kh2 → {vrf: vrf1} }  -- kh2 still uses vrf1!
``` [2](#0-1) [3](#0-2) 

**Attacker registers Pool C with vrf1:**
```
Map.notMember vrf1 psVRFKeyHashes  →  True  (vrf1 was deleted)
Registration succeeds.
psVRFKeyHashes = { vrf1 → 1, vrf2 → 1 }
psStakePools   = { kh1 → {vrf: vrf2}, kh2 → {vrf: vrf1}, kh3 → {vrf: vrf1} }
``` [8](#0-7) 

Pool B (`kh2`) and Pool C (`kh3`) now share `vrf1` post-v11, bypassing the uniqueness invariant. Both are elected slot leaders at identical slots, allowing Pool C to compete for and divert rewards that would otherwise go to Pool B.

### Citations

**File:** eras/shelley/impl/src/Cardano/Ledger/Shelley/Rules/Pool.hs (L264-276)
```haskell
        Nothing -> do
          when (hardforkConwayDisallowDuplicatedVRFKeys pv) $ do
            Map.notMember sppVrf psVRFKeyHashes
              ?! injectFailure (VRFKeyHashAlreadyRegistered sppId sppVrf)
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
