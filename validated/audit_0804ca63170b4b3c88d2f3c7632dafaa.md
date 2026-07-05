### Title
`psVRFKeyHashes` Reference Count Corrupted by `Map.withoutKeys` in `poolReapTransition` When Multiple Pools Share a Legacy VRF Key — (`eras/shelley/impl/src/Cardano/Ledger/Shelley/Rules/PoolReap.hs`)

---

### Summary

`poolReapTransition` computes a set called `danglingVRFKeyHashes` — VRF keys whose owning pool has re-registered with a different VRF key — and removes them from `psVRFKeyHashes` with `Map.withoutKeys`. This unconditional deletion is correct only when a VRF key is held by exactly one pool. Before the v11 hard fork, duplicate VRF keys were permitted; `populateVRFKeyHashes` (called at the v11 transition) correctly records their reference counts. After v11, if one of those legacy-duplicate-VRF pools re-registers with a fresh VRF key, `Map.withoutKeys` deletes the shared VRF key's entry entirely, even though the other pool still holds it. The `psVRFKeyHashes` map then shows the key as absent, so the POOL rule's `Map.notMember` guard passes, and an attacker can register a new pool with that VRF key — re-introducing a duplicate that v11 was designed to prevent.

---

### Finding Description

**Shared-resource accounting in `psVRFKeyHashes`**

`psVRFKeyHashes :: Map (VRFVerKeyHash StakePoolVRF) (NonZero Word64)` is a reference-counted map: each entry records how many currently-registered pools use that VRF key. It was introduced at the v11 hard fork via `populateVRFKeyHashes`, which counts every VRF key across both `psStakePools` and `psFutureStakePoolParams`.

**The POOL re-registration path (correct in isolation)**

When pool A re-registers with a new VRF key Y (replacing its current VRF key X), the POOL rule:
- Inserts Y with count 1 into `psVRFKeyHashes`.
- Does **not** decrement X's count (the comment explains this is deferred to POOLREAP). [1](#0-0) 

**The POOLREAP path (incorrect for shared keys)**

At the epoch boundary, `poolReapTransition` builds `danglingVRFKeyHashes` — the set of current VRF keys that are being replaced by future re-registrations — and removes them from `psVRFKeyHashes` with `Map.withoutKeys`: [2](#0-1) [3](#0-2) 

`Map.withoutKeys` deletes the key unconditionally, ignoring its reference count. If X has count 2 (pools A and B both registered with X before v11), removing it entirely is wrong — pool B still holds X. After the epoch boundary, `psVRFKeyHashes` no longer contains X, so the POOL rule's guard:

```haskell
Map.notMember sppVrf psVRFKeyHashes
  ?! injectFailure (VRFKeyHashAlreadyRegistered sppId sppVrf)
``` [4](#0-3) 

…passes for X, allowing a new pool C to register with VRF key X. Pools B and C now share VRF key X in the live ledger state, violating the post-v11 uniqueness invariant.

**Contrast with the retirement path (correct)**

Pool retirements use `removeVRFKeyHashOccurrences`, which decrements the count and only removes the entry when it reaches zero: [5](#0-4) 

The dangling-key path should use the same decrement-based removal, but instead uses `Map.withoutKeys`.

**The existing test does not cover the shared-key case**

The test `"re-register a pool with a fresh VRF"` only registers a single pool with VRF key X before re-registering it with Y, so `psVRFKeyHashes[X]` has count 1 and `Map.withoutKeys` happens to produce the correct result: [6](#0-5) 

No test exercises the scenario where two pools share a VRF key (legacy state) and one of them re-registers.

---

### Impact Explanation

After the bug is triggered, `psVRFKeyHashes` no longer reflects the true reference count for the displaced VRF key. A new pool registration certificate with that VRF key passes the `Map.notMember` guard and is accepted by all honest nodes. The result is a post-v11 ledger state containing duplicate VRF keys — an invalid state that the v11 hard fork was specifically designed to prevent. This constitutes an attacker-controlled certificate exceeding the intended validation limit (`VRFKeyHashAlreadyRegistered`).

**Allowed impact matched**: *Medium — attacker-controlled certificates exceed intended validation limits.*

---

### Likelihood Explanation

The precondition is that two pools share the same VRF key in the ledger state at the time of the v11 hard fork. Before v11, duplicate VRF keys were explicitly permitted: [7](#0-6) 

`populateVRFKeyHashes` was introduced precisely because such duplicates existed on mainnet: [8](#0-7) 

Any pool operator who registered two pools with the same VRF key before v11 can trigger this bug by submitting a single re-registration certificate after v11. No privileged role, governance majority, or key compromise is required.

---

### Recommendation

Replace the unconditional `Map.withoutKeys danglingVRFKeyHashes` with the same decrement-based removal used for retired pools:

```haskell
-- Before (incorrect):
& certPStateL . psVRFKeyHashesL
  %~ ( removeVRFKeyHashOccurrences retiredVRFKeyHashes
         . (`Map.withoutKeys` danglingVRFKeyHashes)
     )

-- After (correct):
& certPStateL . psVRFKeyHashesL
  %~ ( removeVRFKeyHashOccurrences retiredVRFKeyHashes
         . removeVRFKeyHashOccurrences (Set.toList danglingVRFKeyHashes)
     )
```

`removeVRFKeyHashOccurrences` already implements the correct semantics — it decrements the count and removes the entry only when the count reaches zero: [5](#0-4) 

A regression test should be added that registers two pools with the same VRF key before v11, enacts the v11 hard fork, re-registers one pool with a fresh VRF key, passes an epoch, and then asserts that the original VRF key's count is 1 (not 0) and that registering a new pool with that key is rejected.

---

### Proof of Concept

```
1. Protocol version < 11:
   - Register pool A with VRF key X  →  psVRFKeyHashes = {}  (not yet populated)
   - Register pool B with VRF key X  →  psVRFKeyHashes = {}

2. Enact v11 hard fork (populateVRFKeyHashes):
   →  psVRFKeyHashes = { X → 2 }

3. Pool A re-registers with VRF key Y (Y ∉ psVRFKeyHashes → check passes):
   POOL rule:  psVRFKeyHashes = { X → 2, Y → 1 }
               psFutureStakePoolParams[A] = { vrf: Y }

4. Epoch boundary — POOLREAP:
   danglingVRFKeyHashes = { X }   (pool A: current VRF X ≠ future VRF Y)
   Map.withoutKeys { X }  →  psVRFKeyHashes = { Y → 1 }
   (X is gone, but pool B still uses X!)

5. Register pool C with VRF key X:
   Map.notMember X psVRFKeyHashes  →  True  →  check passes
   psVRFKeyHashes = { X → 1, Y → 1 }

6. Ledger state now contains pools B and C both using VRF key X.
   The post-v11 uniqueness invariant is violated.
   psVRFKeyHashes undercounts X (should be 2, is 1).
```

### Citations

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

**File:** eras/shelley/impl/testlib/Test/Cardano/Ledger/Shelley/Imp/PoolSpec.hs (L83-94)
```haskell
    it "register a new pool with an already registered VRF" $ do
      pv <- getsPParams ppProtocolVersionL
      (kh, vrf) <- registerNewPool
      khNew <- freshKeyHash
      registerPoolTx <$> poolParams khNew vrf >>= \tx ->
        if pvMajor pv < natVersion @11
          then do
            submitTx_ tx
            expectPool khNew (Just vrf)
          else do
            submitFailingTx tx [injectFailure $ VRFKeyHashAlreadyRegistered khNew vrf]
            expectPool khNew Nothing
```

**File:** eras/shelley/impl/testlib/Test/Cardano/Ledger/Shelley/Imp/PoolSpec.hs (L183-195)
```haskell
    it "re-register a pool with a fresh VRF" $ do
      (kh, vrf) <- registerNewPool
      vrfNew <- freshKeyHashVRF
      registerPoolTx <$> poolParams kh vrfNew >>= submitTx_
      expectPool kh (Just vrf)
      expectFuturePool kh (Just vrfNew)
      passEpoch
      expectPool kh (Just vrfNew)
      expectVRFs [vrfNew]
      -- now the original VRF can be reused
      khNew <- freshKeyHash
      registerPoolTx <$> poolParams khNew vrf >>= submitTx_
      expectVRFs [vrf, vrfNew]
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
