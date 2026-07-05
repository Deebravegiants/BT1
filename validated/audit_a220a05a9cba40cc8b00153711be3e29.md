### Title
POOLREAP `danglingVRFKeyHashes` Uses `Map.withoutKeys` Instead of Decrement, Permanently Erasing Shared VRF Key Entries — (`eras/shelley/impl/src/Cardano/Ledger/Shelley/Rules/PoolReap.hs`)

---

### Summary

`poolReapTransition` computes `danglingVRFKeyHashes` — the set of old VRF keys being replaced by pool re-registration — and removes them from `psVRFKeyHashes` using `Map.withoutKeys`. This is a **complete deletion** regardless of the reference count stored in the map. Because `psVRFKeyHashes` is a reference-counted map (`NonZero Word64` values), the correct operation is a decrement (as used by `removeVRFKeyHashOccurrences` for retired pools). When two pools share a VRF key pre-v11 and one is re-registered post-v11, the epoch boundary unconditionally deletes the shared key, leaving the other pool's VRF key untracked and permanently allowing a third pool to register with the same VRF key.

---

### Finding Description

**Root cause — `Map.withoutKeys` vs. decrement:**

In `poolReapTransition`, `danglingVRFKeyHashes` is the set of old VRF hashes that pool P is replacing via re-registration: [1](#0-0) 

These are then removed from `psVRFKeyHashes` with: [2](#0-1) 

`Map.withoutKeys danglingVRFKeyHashes` **unconditionally deletes** the entire map entry for every key in the set, regardless of its count. This is inconsistent with `removeVRFKeyHashOccurrences`, which correctly decrements the count and only removes the entry when it reaches zero: [3](#0-2) 

**Re-registration logic (Pool.hs) does not remove V1 at re-registration time:**

When pool P re-registers with VRF=V2 post-v11, `updateFutureVRFKeyHash` inserts V2 with count 1 but does **not** decrement V1 (it only removes a previously staged future VRF key, not the current active one): [4](#0-3) 

V1's removal is intentionally deferred to POOLREAP. The design intent is that POOLREAP should decrement V1's count by 1 (since P is giving it up). Instead, it deletes V1 entirely.

**v11 hard fork populates the reference-counted map correctly:**

At the v11 upgrade, `populateVRFKeyHashes` correctly counts all VRF keys across both `psStakePools` and `psFutureStakePoolParams`, producing a count of 2 for V1 when both Q and P use it: [5](#0-4) 

---

### Impact Explanation

After the epoch boundary, `psVRFKeyHashes` no longer contains V1 even though pool Q is still actively registered with VRF=V1. The duplicate-VRF guard in `poolTransition` checks: [6](#0-5) 

Since V1 is absent from `psVRFKeyHashes`, `Map.notMember V1 psVRFKeyHashes` returns `True`, and a new pool R can register with VRF=V1. The `hardforkConwayDisallowDuplicatedVRFKeys` invariant is permanently violated: two pools (Q and R) share VRF=V1 in the live ledger state. Recovery requires a hard fork. If the attacker controls the VRF=V1 private key, they can produce valid slot-leadership proofs for pool R while Q is also eligible, enabling double-signing of slots.

**Impact: High** — permanent invariant violation allowing duplicate VRF key registrations; recovery requires a hard fork.

---

### Likelihood Explanation

The precondition (two pools sharing a VRF key) is achievable on any network that has not yet enacted v11, since the duplicate-VRF check (`hardforkConwayDisallowDuplicatedVRFKeys`) is only enforced post-v11. The attacker is an unprivileged pool operator. The entry point is a standard `RegPool` certificate in a transaction. The trigger is a single epoch boundary after re-registration. The path is fully local-testable.

---

### Recommendation

Replace `Map.withoutKeys danglingVRFKeyHashes` with a decrement-based removal, consistent with `removeVRFKeyHashOccurrences`:

```haskell
& certPStateL . psVRFKeyHashesL
  %~ ( removeVRFKeyHashOccurrences retiredVRFKeyHashes
         . removeVRFKeyHashOccurrences (Set.toList danglingVRFKeyHashes)  -- decrement, not delete
     )
```

This ensures that if V1 has count 2 (shared by Q and P) and P re-registers with V2, V1's count is decremented to 1 (still tracked for Q) rather than deleted entirely.

---

### Proof of Concept

```
State before v11 upgrade:
  psStakePools         = { Q → VRF=V1, P → VRF=V1 }
  psFutureStakePoolParams = {}
  psVRFKeyHashes       = {}   (not yet populated)

After v11 upgrade (populateVRFKeyHashes):
  psVRFKeyHashes       = { V1 → 2 }

Pool P re-registers with VRF=V2 (post-v11 tx):
  psFutureStakePoolParams = { P → VRF=V2 }
  psVRFKeyHashes       = { V1 → 2, V2 → 1 }

Epoch boundary (POOLREAP):
  danglingVRFKeyHashes = { V1 }   (P: current=V1 ≠ future=V2)
  Map.withoutKeys { V1 } applied:
  psVRFKeyHashes       = { V2 → 1 }   ← V1 deleted entirely!
  psStakePools         = { Q → VRF=V1, P → VRF=V2 }

New pool R registers with VRF=V1:
  Map.notMember V1 psVRFKeyHashes → True  ← guard bypassed!
  Registration succeeds.

Final state:
  psStakePools         = { Q → VRF=V1, P → VRF=V2, R → VRF=V1 }
  psVRFKeyHashes       = { V1 → 1, V2 → 1 }
  → Q and R share VRF=V1; invariant permanently violated.
```

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
