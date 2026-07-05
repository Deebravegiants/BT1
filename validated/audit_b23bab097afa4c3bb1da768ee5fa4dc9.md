### Title
Stale `psVRFKeyHashes` Reference Count After Pool Re-registration Allows VRF Uniqueness Bypass Post-v11 — (File: `eras/shelley/impl/src/Cardano/Ledger/Shelley/Rules/PoolReap.hs` and `eras/shelley/impl/src/Cardano/Ledger/Shelley/Rules/Pool.hs`)

---

### Summary

The `psVRFKeyHashes :: Map (VRFVerKeyHash StakePoolVRF) (NonZero Word64)` field in `PState` tracks how many registered pools use each VRF key hash. This count is used after protocol version 11 to enforce VRF key uniqueness (`VRFKeyHashAlreadyRegistered`). Two code paths fail to maintain this count correctly when a pool that shares a VRF key with another pool either (a) re-registers with its own VRF key, or (b) re-registers with a fresh VRF key. In both cases the count for the shared VRF key is incorrectly reduced to zero, causing the VRF key to be evicted from the map while another pool still holds it. A third pool can then register with that VRF key, producing two live pools with identical VRF keys — a state the protocol explicitly forbids after v11.

---

### Finding Description

**Background.** `psVRFKeyHashes` was introduced at the v11 hard fork via `populateVRFKeyHashes`, which counts every VRF key across both `psStakePools` and `psFutureStakePoolParams`. Pools registered before v11 may legitimately share a VRF key; the count records how many do. After v11, new registrations are rejected if the VRF key is already present (`Map.notMember sppVrf psVRFKeyHashes`).

**Bug 1 — `Pool.hs`, re-registration with the same VRF key (lines 283–295).**

When a pool re-registers and `psFutureStakePoolParams` has no prior entry for that pool (`Nothing` branch), `updateFutureVRFKeyHash` unconditionally executes:

```haskell
Nothing -> Map.insert sppVrf (knownNonZeroBounded @1)
```

`Map.insert` overwrites any existing value. If `sppVrf` equals the pool's current VRF key (`stakePoolState ^. spsVrfL`) — which is explicitly allowed by the check at lines 280–282 — and that VRF key has a count of `n > 1` (because `n` pools share it from before v11), the count is silently reset to `1`. The `n − 1` other pools that still hold the same VRF key are no longer reflected in the count.

**Bug 2 — `PoolReap.hs`, dangling VRF key removal at epoch boundary (lines 138–148, 224–227).**

When a pool re-registers with a *different* VRF key, the old VRF key becomes "dangling". At the epoch boundary `poolReapTransition` computes:

```haskell
danglingVRFKeyHashes =
  Set.fromList $ Map.elems $
    Map.merge Map.dropMissing Map.dropMissing
      (Map.zipWithMaybeMatched $ \_ sps sppF ->
          if sps ^. spsVrfL /= sppF ^. sppVrfL
            then Just (sps ^. spsVrfL)
            else Nothing)
      (ps0 ^. psStakePoolsL)
      (ps0 ^. psFutureStakePoolParamsL)
```

and then removes them with:

```haskell
& certPStateL . psVRFKeyHashesL
    %~ ( removeVRFKeyHashOccurrences retiredVRFKeyHashes
           . (`Map.withoutKeys` danglingVRFKeyHashes)
       )
```

`Map.withoutKeys` performs a complete deletion regardless of the stored count. If the dangling VRF key has count `n > 1` (because `n` pools share it from before v11), all `n` references are erased at once, even though only one pool changed its VRF key.

---

### Impact Explanation

After either bug triggers, `psVRFKeyHashes` no longer contains the affected VRF key even though at least one live pool still holds it. A subsequent `RegPool` certificate for a new pool carrying that VRF key passes the `Map.notMember sppVrf psVRFKeyHashes` check and is accepted. The ledger then contains two pools with identical VRF keys.

In Ouroboros Praos, VRF keys determine slot leadership: both pools compute the same VRF output for every slot and therefore win or lose the same slots simultaneously. When both win a slot, each produces a valid block, creating a fork. Honest nodes following different forks diverge deterministically and irrecoverably without a hard fork.

This maps to: **High — Deterministic disagreement between honest nodes from ledger rule evaluation.**

---

### Likelihood Explanation

Prerequisites:
1. Protocol version ≥ 11 enacted (within the Conway era range v9–11).
2. At least two pools registered with the same VRF key before v11 (permitted by the pre-v11 rules).
3. One of those pools submits a `RegPool` certificate (re-registration) after v11 — a routine pool-operator action.
4. That pool subsequently retires via `RetirePool`.
5. Any pool operator submits a `RegPool` certificate with the now-untracked VRF key.

Steps 3–5 are ordinary, unprivileged pool-operator transactions. The only non-trivial prerequisite is step 2, which is a realistic historical state given that duplicate VRF keys were allowed before v11. The `HardForkSpec` test at `eras/conway/impl/testlib/Test/Cardano/Ledger/Conway/Imp/HardForkSpec.hs` lines 54–85 exercises retirement of duplicate-VRF pools but does not cover the re-registration-then-retire path that triggers Bug 1.

---

### Recommendation

**Bug 1 (`Pool.hs`):** In the `Nothing` branch of `updateFutureVRFKeyHash`, guard the insert on whether the VRF key is actually changing:

```haskell
Nothing
  | sppVrf /= stakePoolState ^. spsVrfL ->
      Map.insert sppVrf (knownNonZeroBounded @1)
  | otherwise -> id
```

**Bug 2 (`PoolReap.hs`):** Replace the wholesale `Map.withoutKeys danglingVRFKeyHashes` deletion with the same reference-count decrement used for retired pools:

```haskell
& certPStateL . psVRFKeyHashesL
    %~ removeVRFKeyHashOccurrences retiredVRFKeyHashes
     . removeVRFKeyHashOccurrences (Set.toList danglingVRFKeyHashes)
```

Add a test covering: register two pools with the same VRF before v11 → enact v11 → re-register one pool with its own VRF → retire it → assert the VRF key is still present with count 1 and that a new pool cannot register with it.

---

### Proof of Concept

```
Epoch 0 (protocol version 10):
  RegPool kh1 vrf_X   → psStakePools[kh1].vrf = vrf_X
  RegPool kh2 vrf_X   → psStakePools[kh2].vrf = vrf_X

Epoch 1: v11 hard fork enacted
  populateVRFKeyHashes → psVRFKeyHashes[vrf_X] = 2

Epoch 1 (same epoch, after hard fork):
  RegPool kh1 vrf_X   (re-register with same VRF)
    → check: sppVrf == stakePoolState.spsVrf  ✓ (passes)
    → updateFutureVRFKeyHash (Nothing branch):
        Map.insert vrf_X (NonZero 1)
    → psVRFKeyHashes[vrf_X] = 1   ← BUG: was 2, should remain 2

  RetirePool kh1 (epoch 2)

Epoch 2: POOLREAP fires
  retiredVRFKeyHashes = [vrf_X]
  removeVRFKeyHashOccurrences [vrf_X]:
    mapNonZero (\n -> n - 1) (NonZero 1) = Nothing → Map.delete vrf_X
  → psVRFKeyHashes = {}   ← BUG: kh2 still holds vrf_X

Epoch 2 (after POOLREAP):
  RegPool kh3 vrf_X
    → Map.notMember vrf_X psVRFKeyHashes  ✓ (passes — map is empty)
    → psVRFKeyHashes[vrf_X] = 1
    → psStakePools[kh2].vrf = vrf_X  AND  psStakePools[kh3].vrf = vrf_X
    → INVARIANT VIOLATED: two live pools share vrf_X
``` [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6) [8](#0-7)

### Citations

**File:** eras/shelley/impl/src/Cardano/Ledger/Shelley/Rules/Pool.hs (L278-282)
```haskell
        Just stakePoolState -> do
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

**File:** eras/shelley/impl/src/Cardano/Ledger/Shelley/Rules/PoolReap.hs (L136-148)
```haskell
    -- find the set of VRF key hashes that are no longer relevant, since they have been overwritten
    -- via pool re-registration
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

**File:** libs/cardano-ledger-core/src/Cardano/Ledger/State/CertState.hs (L233-245)
```haskell
  { psVRFKeyHashes :: !(Map (VRFVerKeyHash StakePoolVRF) (NonZero Word64))
  -- ^ VRF key hashes that have been registered via PoolParams
  , psStakePools :: !(Map (KeyHash StakePool) StakePoolState)
  -- ^ The state of current stake pools.
  , psFutureStakePoolParams :: !(Map (KeyHash StakePool) StakePoolParams)
  -- ^ Future pool params
  -- Changes to existing stake pool parameters are staged in order
  -- to give delegators time to react to changes.
  -- See section 11.2, "Example Illustration of the Reward Cycle",
  -- of the Shelley Ledger Specification for a sequence diagram.
  , psRetiring :: !(Map (KeyHash StakePool) EpochNo)
  -- ^ A map of retiring stake pools to the epoch when they retire.
  }
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
