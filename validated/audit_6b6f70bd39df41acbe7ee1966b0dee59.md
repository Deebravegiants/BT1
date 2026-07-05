The exploit path is concrete and traceable through the code. Here is the complete analysis.

---

### Title
`danglingVRFKeyHashes` uses `Map.withoutKeys` (unconditional delete) instead of `removeVRFKeyHashOccurrences` (decrement), allowing a pre-v11 shared VRF key to be silently evicted from `psVRFKeyHashes` and re-registered post-v11 — (`eras/shelley/impl/src/Cardano/Ledger/Shelley/Rules/PoolReap.hs`)

---

### Summary

When the v11 hardfork fires, `populateVRFKeyHashes` correctly seeds `psVRFKeyHashes` with reference counts, so a VRF key shared by N pre-fork pools gets count N. However, when any one of those pools re-registers with a fresh VRF key post-v11, `poolReapTransition` removes the old VRF key from `psVRFKeyHashes` via `Map.withoutKeys danglingVRFKeyHashes` — an unconditional delete that ignores the count. The remaining pools that still hold the old VRF key are now invisible to the uniqueness guard, and a new pool can register with that key, producing two simultaneously active pools sharing the same VRF key.

---

### Finding Description

**Step 1 — Hardfork migration populates counts correctly.**

`hardforkTransition` at `pvMajor newPv == natVersion @11` calls `populateVRFKeyHashes`: [1](#0-0) 

`populateVRFKeyHashes` iterates both `psStakePools` and `psFutureStakePoolParams`, incrementing a counter per VRF key: [2](#0-1) 

After the hardfork, if Pool_A and Pool_B both hold VRF_X, `psVRFKeyHashes = {VRF_X: 2}`. This is confirmed by the existing test: [3](#0-2) 

**Step 2 — Pool_A re-registers with fresh VRF_Y post-v11.**

The re-registration guard in `poolTransition` passes because VRF_Y is not yet in `psVRFKeyHashes`: [4](#0-3) 

`updateFutureVRFKeyHash` inserts VRF_Y with count 1 (Pool_A has no prior future params): [5](#0-4) 

State after re-registration: `psVRFKeyHashes = {VRF_X: 2, VRF_Y: 1}`.

**Step 3 — Epoch boundary: `poolReapTransition` unconditionally deletes VRF_X.**

`danglingVRFKeyHashes` is computed by comparing current vs. future VRF for each pool that has a pending re-registration. Pool_A's current VRF is VRF_X and future is VRF_Y, so VRF_X enters the set: [6](#0-5) 

Then the update is applied: [7](#0-6) 

`Map.withoutKeys danglingVRFKeyHashes` removes VRF_X **entirely**, regardless of its count of 2. Pool_B is still active with VRF_X, but `psVRFKeyHashes = {VRF_Y: 1}` — VRF_X is gone.

**Step 4 — New Pool_C registers with VRF_X.**

The new-pool guard checks: [8](#0-7) 

`Map.notMember VRF_X psVRFKeyHashes` is now `True`. Pool_C is accepted. Two active pools — Pool_B and Pool_C — now share VRF_X, violating the invariant `hardforkConwayDisallowDuplicatedVRFKeys` is meant to enforce: [9](#0-8) 

**Root cause in one line:** `danglingVRFKeyHashes` should be processed with `removeVRFKeyHashOccurrences` (decrement-then-remove-at-zero), exactly as `retiredVRFKeyHashes` is. Instead it uses `Map.withoutKeys`, which is a blind delete. [10](#0-9) 

---

### Impact Explanation

Two simultaneously active pools share the same VRF secret key. In Praos, the VRF key determines slot-leader eligibility: both pools compute identical VRF outputs for every slot, so both are eligible leaders for the same slots. Both can produce valid, ledger-accepted blocks for those slots. Honest nodes receive two valid competing blocks per affected slot, creating forks. This constitutes **High — deterministic disagreement between honest nodes from ledger rule evaluation**: the ledger has accepted a state that its own post-v11 invariant forbids, and the resulting duplicate slot-leadership is a deterministic, reproducible source of chain disagreement.

---

### Likelihood Explanation

The precondition — two pools sharing a VRF key registered before v11 — was explicitly legal and is known to exist on mainnet (the hardfork test suite explicitly models it). Any operator who controlled such a pair and re-registers one of them with a new VRF key post-v11 triggers the bug automatically at the next epoch boundary, with no further privileges required.

---

### Recommendation

In `poolReapTransition`, replace the unconditional `Map.withoutKeys danglingVRFKeyHashes` with a call to `removeVRFKeyHashOccurrences` (the same helper already used for `retiredVRFKeyHashes`). This decrements the counter for each dangling VRF key and only removes the map entry when the count reaches zero, preserving the entry for any other pool that still holds that key.

```haskell
-- current (buggy)
& certPStateL . psVRFKeyHashesL
  %~ ( removeVRFKeyHashOccurrences retiredVRFKeyHashes
         . (`Map.withoutKeys` danglingVRFKeyHashes)
     )

-- fixed
& certPStateL . psVRFKeyHashesL
  %~ ( removeVRFKeyHashOccurrences retiredVRFKeyHashes
         . removeVRFKeyHashOccurrences (Set.toList danglingVRFKeyHashes)
     )
```

---

### Proof of Concept

State-transition test at pv=10, then enact v11 hardfork:

1. Register Pool_A with VRF_X (pre-v11).
2. Register Pool_B with VRF_X (pre-v11).
3. Enact hardfork to v11 → assert `psVRFKeyHashes = {VRF_X: 2}`.
4. Submit re-registration of Pool_A with fresh VRF_Y → assert `psVRFKeyHashes = {VRF_X: 2, VRF_Y: 1}`.
5. `passEpoch` → assert **`psVRFKeyHashes = {VRF_Y: 1}`** (VRF_X incorrectly evicted despite Pool_B still active).
6. Submit new pool registration for Pool_C with VRF_X → assert it is **accepted** (bug) rather than rejected with `VRFKeyHashAlreadyRegistered`.
7. Assert both Pool_B and Pool_C are active in `psStakePools` with VRF_X.

The existing test suite covers retirement of shared-VRF pools but has no test for the re-registration path that triggers `danglingVRFKeyHashes` when the count is > 1. [11](#0-10)

### Citations

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/HardFork.hs (L77-78)
```haskell
        | pvMajor newPv == natVersion @11 =
            esLStateL . lsCertStateL . certPStateL %~ populateVRFKeyHashes
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

**File:** eras/shelley/impl/src/Cardano/Ledger/Shelley/Rules/Pool.hs (L265-267)
```haskell
          when (hardforkConwayDisallowDuplicatedVRFKeys pv) $ do
            Map.notMember sppVrf psVRFKeyHashes
              ?! injectFailure (VRFKeyHashAlreadyRegistered sppId sppVrf)
```

**File:** eras/shelley/impl/src/Cardano/Ledger/Shelley/Rules/Pool.hs (L279-282)
```haskell
          when (hardforkConwayDisallowDuplicatedVRFKeys pv) $ do
            sppVrf == stakePoolState ^. spsVrfL
              || Map.notMember sppVrf psVRFKeyHashes
                ?! injectFailure (VRFKeyHashAlreadyRegistered sppId sppVrf)
```

**File:** eras/shelley/impl/src/Cardano/Ledger/Shelley/Rules/Pool.hs (L283-295)
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

**File:** eras/shelley/impl/src/Cardano/Ledger/Shelley/Era.hs (L259-262)
```haskell
hardforkConwayDisallowDuplicatedVRFKeys ::
  ProtVer ->
  Bool
hardforkConwayDisallowDuplicatedVRFKeys pv = pvMajor pv > natVersion @10
```
