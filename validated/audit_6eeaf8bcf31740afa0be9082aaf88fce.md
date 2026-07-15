Looking at the actual code in `chia/full_node/weight_proof.py`, I need to trace the full validation path carefully.

The code path is concrete and I can trace it precisely.

**Key structural fact:** `__get_rc_sub_slot` is called exclusively on `segments[0]` of each sub-epoch (line 979). It returns `None` — failing validation — if `segments[0]` has no challenge block (lines 1456-1464). This guard does **not** apply to any segment at index > 0.

**`_validate_segment` (lines 1028-1051):**
```python
after_challenge = False
to_validate = []
for idx, sub_slot_data in enumerate(segment.sub_slots):
    if sampled and sub_slot_data.is_challenge():
        after_challenge = True
        required_iters = __validate_pospace(...)   # PoSpace check
        ...
        vdf_list = _get_challenge_block_vdfs(...)
        to_validate.extend(vdf_list)
    elif sampled and after_challenge:
        ...
    slot_iters += curr_ssi
    slots += uint64(1)
return True, ip_iters, slot_iters, slots, to_validate  # returns True regardless
```

There is **no guard** that checks `after_challenge` was ever set before returning `True`. If `sampled=True` and no sub_slot satisfies `is_challenge()`, the function returns `(True, 0, slot_iters, slots, [])` — an empty VDF list, no PoSpace checked.

**The test `test_weight_proof_validation_no_challenge_block_in_segment` (lines 718-755) does NOT cover this path.** It modifies the first segment with `sub_epoch_n > 0`, which is `segments[0]` of that sub-epoch. That case is caught by `__get_rc_sub_slot`, not by any fix in `_validate_segment`. The test asserts `not valid` and passes — but only because `__get_rc_sub_slot` rejects it, not because `_validate_segment` rejects it.

**Exploitability of the non-first-segment path:**
- `sampled_seg_index = rng.choice(range(len(segments)))` (line 977)
- The RNG seed is `summaries[-2].get_hash()` — deterministic and derived from public chain data
- The attacker controls `len(segments)` per sub-epoch (up to `max_segments = 25` on mainnet)
- The attacker can enumerate `len(segments)` values to find one where `rng.choice(range(N))` returns an index > 0, then place a crafted all-slot-end segment at that index
- `segments[0]` is provided legitimately (passes `__get_rc_sub_slot` and `reward_chain_hash` check)
- The crafted segment at the sampled index has all `cc_slot_end` set → `is_challenge()` never True → `_validate_segment` returns `True` with empty `vdf_list`

---

### Title
Sampled non-first segment with no challenge block bypasses all PoSpace and VDF validation in weight proof — (`chia/full_node/weight_proof.py`)

### Summary
`_validate_segment` returns `True` with an empty VDF list when called with `sampled=True` on a segment whose every `SubSlotData` has `cc_slot_end` set. The only guard against this (`__get_rc_sub_slot`) applies exclusively to `segments[0]` of each sub-epoch. An attacker who predicts the deterministic RNG output can craft a weight proof where the sampled segment is at index > 0 and contains no challenge block, causing the entire sampled-segment cryptographic check to be silently skipped.

### Finding Description

In `_validate_sub_epoch_segments`, for each sub-epoch the sampled index is chosen as:

```python
sampled_seg_index = rng.choice(range(len(segments)))
``` [1](#0-0) 

The only structural guard that would catch a segment with no challenge block is `__get_rc_sub_slot`, called on `segments[0]` only: [2](#0-1) 

Inside `__get_rc_sub_slot`, if no sub_slot has `cc_slot_end is None`, it logs an error and returns `None`, failing validation: [3](#0-2) 

But `_validate_segment` has no equivalent guard. When `sampled=True` and no `sub_slot_data.is_challenge()` is ever True, `after_challenge` stays `False`, neither branch executes, and the function returns `True` with an empty `to_validate`: [4](#0-3) 

The existing test `test_weight_proof_validation_no_challenge_block_in_segment` only modifies `segments[0]` of a sub-epoch, which is caught by `__get_rc_sub_slot` — it does not exercise the non-first-segment path: [5](#0-4) 

### Impact Explanation
A remote peer serving a crafted `WeightProof` can cause a light-client wallet to accept a proof where the sampled segment's work is entirely unverified. The wallet's sync state is corrupted: it may adopt a lower-work fork as canonical, leading to incorrect balance display and susceptibility to double-spend attacks. This matches the **High** impact category: *Corruption of wallet sync state with direct security impact*.

### Likelihood Explanation
The RNG seed (`summaries[-2].get_hash()`) is derived from public chain data. The attacker can enumerate `len(segments)` values (1–25 on mainnet) to find one where `rng.choice(range(N))` returns an index > 0, then supply a valid `segments[0]` from the real chain and a crafted all-slot-end segment at the sampled index. No privileged access is required; any peer serving weight proofs can mount this attack.

### Recommendation
In `_validate_segment`, after the loop, add an explicit check:

```python
if sampled and not after_challenge:
    log.error("sampled segment contains no challenge block")
    return False, uint64(0), uint64(0), uint64(0), []
```

This mirrors the existing guard in `__get_rc_sub_slot` and ensures that every sampled segment must contain at least one PoSpace-verified challenge block.

### Proof of Concept
1. Obtain a legitimate weight proof `wp` for the chain tip.
2. Compute the RNG state (seed = `summaries[-2].get_hash()`; replay `validate_sub_epoch_sampling` calls) to determine, for each sub-epoch, what `rng.choice(range(N))` returns for various `N`.
3. For a target sub-epoch, find `N` such that the sampled index `k > 0`.
4. Replace `wp.sub_epoch_segments[target_sub_epoch][k]` with a crafted segment where every `SubSlotData` has `cc_slot_end` set (copy any legitimate slot-end entry).
5. Submit the modified proof to a wallet performing light-client sync.
6. Observe that `_validate_segment` returns `(True, 0, slot_iters, slots, [])` for the sampled segment, `vdfs_to_validate` contains no entries for it, and the proof is accepted — with zero cryptographic verification of the sampled segment's work.

### Citations

**File:** chia/full_node/weight_proof.py (L977-977)
```python
        sampled_seg_index = rng.choice(range(len(segments)))
```

**File:** chia/full_node/weight_proof.py (L978-984)
```python
        if sub_epoch_n > 0:
            rc_sub_slot = __get_rc_sub_slot(constants, segments[0], summaries, curr_ssi)
            if rc_sub_slot is None:
                log.error(f"failed to reconstruct rc sub slot for sub_epoch {sub_epoch_n}")
                return None
            prev_ses = summaries[sub_epoch_n - 1]
            rc_sub_slot_hash = rc_sub_slot.get_hash()
```

**File:** chia/full_node/weight_proof.py (L1028-1051)
```python
    ip_iters, slot_iters, slots = 0, 0, 0
    after_challenge = False
    to_validate = []
    for idx, sub_slot_data in enumerate(segment.sub_slots):
        if sampled and sub_slot_data.is_challenge():
            after_challenge = True
            required_iters = __validate_pospace(
                constants, segment, idx, curr_difficulty, ses, first_segment_in_se, height
            )
            if required_iters is None:
                return False, uint64(0), uint64(0), uint64(0), []
            assert sub_slot_data.signage_point_index is not None
            ip_iters += calculate_ip_iters(constants, curr_ssi, sub_slot_data.signage_point_index, required_iters)
            vdf_list = _get_challenge_block_vdfs(constants, idx, segment.sub_slots, curr_ssi)
            to_validate.extend(vdf_list)
        elif sampled and after_challenge:
            validated, vdf_list = _validate_sub_slot_data(constants, idx, segment.sub_slots, curr_ssi)
            if not validated:
                log.error(f"failed to validate sub slot data {idx} vdfs")
                return False, uint64(0), uint64(0), uint64(0), []
            to_validate.extend(vdf_list)
        slot_iters += curr_ssi
        slots += uint64(1)
    return True, ip_iters, slot_iters, slots, to_validate
```

**File:** chia/full_node/weight_proof.py (L1456-1464)
```python
    for idx, curr in enumerate(segment.sub_slots):
        if curr.cc_slot_end is None:
            first_idx = idx
            first = curr
            break

    if first_idx is None or first is None or first.signage_point_index is None:
        log.error("segment missing challenge block or signage_point_index")
        return None
```

**File:** chia/_tests/weight_proof/test_weight_proof.py (L736-755)
```python
        modified_segments = list(wp.sub_epoch_segments)
        target_found = False
        for i, seg in enumerate(modified_segments):
            if seg.sub_epoch_n > 0:
                slot_end_donor = next(ssd for ssd in seg.sub_slots if ssd.cc_slot_end is not None)
                new_sub_slots = [slot_end_donor if ssd.cc_slot_end is None else ssd for ssd in seg.sub_slots]
                assert all(ssd.cc_slot_end is not None for ssd in new_sub_slots)
                modified_segments[i] = seg.replace(sub_slots=new_sub_slots)
                target_found = True
                break

        assert target_found, "No segment found with a challenge block to replace"

        modified_wp = dataclasses.replace(wp, sub_epoch_segments=modified_segments)

        wpf_verify = WeightProofHandler(
            blockchain_constants, BlockchainMock(sub_blocks, header_cache, height_to_hash, {})
        )
        valid, _fork_point = wpf_verify.validate_weight_proof_single_proc(modified_wp)
        assert not valid
```
