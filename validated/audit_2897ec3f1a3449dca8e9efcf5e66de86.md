Now I have all the code needed to trace the full exploit path. Let me analyze it carefully.

The exploit path is real and fully traceable in production code. Here is the complete step-by-step analysis.

---

### Title
VRF Key Hash Counter Corrupted by Re-registration to Current VRF, Enabling Duplicate VRF Post-v11 — (`eras/shelley/impl/src/Cardano/Ledger/Shelley/Rules/Pool.hs`)

---

### Summary

`updateFutureVRFKeyHash` in `poolTransition` uses `Map.insert sppVrf (knownNonZeroBounded @1)` unconditionally, which **overwrites** the existing reference count rather than incrementing it. When a pool that shares a VRF key with another pool (allowed pre-v11) re-registers post-v11 with its own current VRF, the shared counter is silently reset from 2 to 1. A subsequent retirement of the co-sharing pool then decrements the counter to 0 and removes the entry, after which a brand-new pool can register with that VRF even though the original pool still holds it — breaking the post-v11 VRF uniqueness invariant.

---

### Finding Description

**Preconditions (all achievable by an unprivileged pool operator):**

- Pre-v11: Pool P and Pool Q both registered with `VRF=A` (permitted pre-v11).
- v11 hardfork fires: `populateVRFKeyHashes` correctly sets `psVRFKeyHashes = {A: 2}`. [1](#0-0) 

**Step 1 — Pool P re-registers with `VRF=A` (its own current VRF):**

The re-register guard at lines 280–282 passes because `sppVrf == stakePoolState ^. spsVrfL` is `True`: [2](#0-1) 

`updateFutureVRFKeyHash` then takes the `Nothing` branch (no prior future params for P) and executes `Map.insert A (knownNonZeroBounded @1)`: [3](#0-2) 

`Map.insert` **replaces** the existing value, so `{A: 2}` becomes `{A: 1}`. Pool Q still uses `VRF=A` in `psStakePools`, so the true count should remain 2. This is the root-cause corruption.

**Step 2 — Pool Q retires (POOLREAP):**

`retiredVRFKeyHashes = [A]`. `removeVRFKeyHashOccurrence` calls `Map.update (mapNonZero (\n -> n - 1))` on `{A: 1}`. Since `1 - 1 = 0`, `mapNonZero` returns `Nothing` and `Map.update` removes the key entirely: [4](#0-3) 

`psVRFKeyHashes` is now `{}`. Pool P still holds `VRF=A` in `psStakePools`.

**Step 3 — New pool R registers with `VRF=A`:**

The new-registration guard checks `Map.notMember sppVrf psVRFKeyHashes`: [5](#0-4) 

`Map.notMember A {}` is `True`, so the check passes and Pool R is registered with `VRF=A`. Both Pool P and Pool R now hold `VRF=A` post-v11 — the uniqueness invariant is broken.

The same corruption also occurs via the `Just futureStakePoolParams | futureStakePoolParams ^. sppVrfL /= sppVrf` branch (lines 291–293), which is the three-step sequence described in the question. Both branches share the same defect: `Map.insert sppVrf (knownNonZeroBounded @1)` is used where an increment or a no-op is required. [6](#0-5) 

---

### Impact Explanation

The `hardforkConwayDisallowDuplicatedVRFKeys` guard — the sole post-v11 mechanism preventing duplicate VRF registrations — is bypassed. Two active pools share a VRF key, which is the exact condition the v11 hardfork was designed to prevent. This falls under **Medium** impact: attacker-controlled pool-registration certificates exceed the intended validation limits of the VRF uniqueness check. The claimed "deterministic disagreement between honest nodes" does not apply — all nodes reach the same (corrupted) state deterministically; there is no fork at the ledger layer.

---

### Likelihood Explanation

The attacker needs only to:
1. Have registered a pool pre-v11 that shares a VRF with any other pool (a common pre-v11 state).
2. Submit a single re-registration certificate post-v11 with the same VRF they already hold.
3. Wait for the co-sharing pool to retire naturally.

No privileged access, governance majority, or key compromise is required. The exploit is fully within the reach of an ordinary pool operator.

---

### Recommendation

In `updateFutureVRFKeyHash`, before calling `Map.insert sppVrf (knownNonZeroBounded @1)`, check whether `sppVrf` equals the pool's **current** VRF in `psStakePools` (i.e., `stakePoolState ^. spsVrfL`). If they are equal, the counter already accounts for this pool and must not be overwritten — use `id` instead. Concretely, both the `Nothing` branch and the `Just … | … /= sppVrf` branch should guard with:

```haskell
if sppVrf == stakePoolState ^. spsVrfL
  then id   -- VRF unchanged from psStakePools; counter already correct
  else Map.insert sppVrf (knownNonZeroBounded @1)
```

(combined with the existing `Map.delete` of the superseded future VRF where applicable).

---

### Proof of Concept

```
1. Pre-v11:  registerPool P vrf=A
             registerPool Q vrf=A
             -- psVRFKeyHashes = {} (not yet populated)

2. v11 HF:   populateVRFKeyHashes fires
             -- psVRFKeyHashes = {A: 2}

3. Post-v11: reRegisterPool P vrf=A   -- same VRF, passes guard (A==A)
             -- updateFutureVRFKeyHash: Nothing branch → Map.insert A 1
             -- psVRFKeyHashes = {A: 1}  ← BUG (should be {A: 2})

4. Epoch boundary: retirePool Q
             -- POOLREAP: removeVRFKeyHashOccurrence A on {A:1} → removes A
             -- psVRFKeyHashes = {}
             -- Pool P still active with vrf=A in psStakePools

5. Post-v11: registerPool R vrf=A
             -- guard: Map.notMember A {} → True → PASSES
             -- psVRFKeyHashes = {A: 1}
             -- Pool P and Pool R both hold vrf=A  ← invariant broken

Assert: psStakePools[P].spsVrf == A  ∧  psStakePools[R].spsVrf == A
        psVRFKeyHashes[A] == 1  (should be 2, or registration of R should have failed)
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

**File:** eras/shelley/impl/src/Cardano/Ledger/Shelley/Rules/Pool.hs (L265-276)
```haskell
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

**File:** eras/shelley/impl/src/Cardano/Ledger/Shelley/Rules/Pool.hs (L279-282)
```haskell
          when (hardforkConwayDisallowDuplicatedVRFKeys pv) $ do
            sppVrf == stakePoolState ^. spsVrfL
              || Map.notMember sppVrf psVRFKeyHashes
                ?! injectFailure (VRFKeyHashAlreadyRegistered sppId sppVrf)
```

**File:** eras/shelley/impl/src/Cardano/Ledger/Shelley/Rules/Pool.hs (L283-294)
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
```

**File:** eras/shelley/impl/src/Cardano/Ledger/Shelley/Rules/PoolReap.hs (L224-237)
```haskell
          & certPStateL . psVRFKeyHashesL
            %~ ( removeVRFKeyHashOccurrences retiredVRFKeyHashes
                   . (`Map.withoutKeys` danglingVRFKeyHashes)
               )
      )
  where
    removeVRFKeyHashOccurrences ::
      [VRFVerKeyHash StakePoolVRF] ->
      Map (VRFVerKeyHash StakePoolVRF) (NonZero Word64) ->
      Map (VRFVerKeyHash StakePoolVRF) (NonZero Word64)
    removeVRFKeyHashOccurrences vrfs vrfsMap = F.foldl' (flip removeVRFKeyHashOccurrence) vrfsMap vrfs
    removeVRFKeyHashOccurrence =
      -- Removes the key from the map if the value drops to 0
      Map.update (mapNonZero (\n -> n - 1))
```
