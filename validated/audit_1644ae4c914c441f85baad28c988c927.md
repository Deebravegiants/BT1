### Title
Incomplete SEC-614 Fix: `__get_cc_sub_slot` Crashes with `AssertionError` on Crafted Weight Proof — (`File: chia/full_node/weight_proof.py`)

### Summary

The SEC-614 fix hardened `__get_rc_sub_slot` against a challenge block appearing at sub-slot index 0 in `segments[0]` of a sub-epoch. However, `__get_cc_sub_slot` — called from `__validate_pospace` for every sampled segment — contains the same unguarded `assert sub_slot is not None` that crashes with `AssertionError` when the challenge block is at index 0 in any segment other than `segments[0]`. An unprivileged peer can send a crafted `WeightProof` that reliably triggers this crash during sync.

### Finding Description

`__get_cc_sub_slot` searches backwards from `idx` for a slot-end entry:

```python
def __get_cc_sub_slot(sub_slots, idx, ses):
    sub_slot: SubSlotData | None = None
    for i in reversed(range(idx)):   # empty when idx == 0
        sub_slot = sub_slots[i]
        if sub_slot.cc_slot_end_info is not None:
            break
    assert sub_slot is not None          # AssertionError when idx == 0
    assert sub_slot.cc_slot_end_info is not None
``` [1](#0-0) 

When `idx == 0`, `reversed(range(0))` yields nothing, `sub_slot` stays `None`, and the `assert` raises `AssertionError`.

`__get_cc_sub_slot` is called from `__validate_pospace`:

```python
if first_in_sub_epoch and segment.sub_epoch_n == 0 and idx == 0:
    cc_sub_slot_hash = constants.GENESIS_CHALLENGE
else:
    cc_sub_slot_hash = __get_cc_sub_slot(segment.sub_slots, idx, ses).get_hash()
``` [2](#0-1) 

The guard only covers `sub_epoch_n == 0`. For any segment where `sub_epoch_n > 0` and the challenge block is the first sub-slot (`idx == 0`), `__get_cc_sub_slot` is called unconditionally and crashes.

The SEC-614 fix added a guard only to `__get_rc_sub_slot`:

```python
idx -= 1
if idx < 0:
    log.error("malformed segment: no slot-end entry before challenge block")
    return None
``` [3](#0-2) 

This prevents the crash only when `segments[0]` itself has the challenge block at index 0 (because `__get_rc_sub_slot` is called exclusively on `segments[0]` and returns `None` early). If `segments[0]` is structurally valid but any later segment has the challenge block at index 0, `__get_rc_sub_slot` succeeds, validation proceeds to `_validate_segment` for the later segment, and `__get_cc_sub_slot` crashes. [4](#0-3) 

The test added for SEC-614 only covers the `segments[0]`-at-index-0 case and does not exercise the later-segment scenario: [5](#0-4) 

### Impact Explanation

A syncing node requests a weight proof from a peer. A malicious peer sends a crafted proof in which `segments[0]` of a sub-epoch with `sub_epoch_n > 0` is structurally valid (so `__get_rc_sub_slot` succeeds and the `rc_sub_slot_hash` check passes), while one or more later segments have the challenge block placed at sub-slot index 0. When `_validate_segment` processes the crafted segment and `sampled_seg_index` selects it, `__validate_pospace` calls `__get_cc_sub_slot(..., idx=0, ...)`, which raises `AssertionError`. This exception propagates through `_validate_sub_epoch_segments` and `validate_weight_proof_inner`, disrupting the node's sync path. Because the attacker controls all segments beyond `segments[0]`, they can place the malformed entry in every non-zero segment, making the crash near-certain regardless of the random sampling. [6](#0-5) 

### Likelihood Explanation

Any peer on the network can send a `WeightProof` message to a syncing node. Constructing the crafted proof requires taking a legitimate proof and replacing the sub-slot list of one or more later segments so the first entry has `cc_slot_end is None` (i.e., is a challenge block). This is straightforward serialization manipulation requiring no keys or privileged access.

### Recommendation

Apply the same defensive pattern used in `__get_rc_sub_slot` to `__get_cc_sub_slot`: replace the bare `assert` statements with explicit checks that return an error indicator (e.g., `None` or raise a typed exception) when `idx == 0` and no slot-end entry exists before the challenge block. Additionally, extend the guard in `__validate_pospace` to cover `sub_epoch_n > 0` cases where `idx == 0`.

### Proof of Concept

1. Obtain a legitimate `WeightProof` from a full node.
2. Locate any `SubEpochChallengeSegment` with `sub_epoch_n > 0` that is not `segments[0]` of its sub-epoch.
3. Replace its `sub_slots` list with a list whose first entry has `cc_slot_end = None` (marking it as a challenge block at index 0) and no preceding slot-end entries.
4. Serve this crafted proof to a syncing node.
5. `_validate_sub_epoch_segments` calls `__validate_pospace` with `idx=0` for the crafted segment; `__get_cc_sub_slot` raises `AssertionError`, crashing weight proof validation and blocking the node's sync. [7](#0-6)

### Citations

**File:** chia/full_node/weight_proof.py (L950-1014)
```python
def _validate_sub_epoch_segments(
    constants: ConsensusConstants,
    rng: random.Random,
    weight_proof_bytes: bytes,
    summaries_bytes: list[bytes],
    height: uint32,
    validate_from: int = 0,
) -> list[tuple[VDFProof, ClassgroupElement, VDFInfo]] | None:
    summaries = summaries_from_bytes(summaries_bytes)
    sub_epoch_segments: SubEpochSegments = SubEpochSegments.from_bytes(weight_proof_bytes)
    rc_sub_slot_hash = constants.GENESIS_CHALLENGE
    total_blocks, total_ip_iters = 0, 0
    total_slot_iters, total_slots = 0, 0
    total_ip_iters = 0
    prev_ses: SubEpochSummary | None = None
    segments_by_sub_epoch = map_segments_by_sub_epoch(sub_epoch_segments.challenge_segments)
    curr_ssi = constants.SUB_SLOT_ITERS_STARTING
    vdfs_to_validate = []
    max_segments = _max_sub_epoch_segments(constants)
    for sub_epoch_n, segments in segments_by_sub_epoch.items():
        if len(segments) > max_segments:
            log.error(f"sub_epoch {sub_epoch_n} has {len(segments)} segments, maximum allowed is {max_segments}")
            return None
        prev_ssi = curr_ssi
        curr_difficulty, curr_ssi = _get_curr_diff_ssi(constants, sub_epoch_n, summaries)
        log.debug(f"validate sub epoch {sub_epoch_n}")
        # recreate RewardChainSubSlot for next ses rc_hash
        sampled_seg_index = rng.choice(range(len(segments)))
        if sub_epoch_n > 0:
            rc_sub_slot = __get_rc_sub_slot(constants, segments[0], summaries, curr_ssi)
            if rc_sub_slot is None:
                log.error(f"failed to reconstruct rc sub slot for sub_epoch {sub_epoch_n}")
                return None
            prev_ses = summaries[sub_epoch_n - 1]
            rc_sub_slot_hash = rc_sub_slot.get_hash()
        if not summaries[sub_epoch_n].reward_chain_hash == rc_sub_slot_hash:
            log.error(f"failed reward_chain_hash validation sub_epoch {sub_epoch_n}")
            return None

        # skip validation up to fork height
        if sub_epoch_n < validate_from:
            continue

        for idx, segment in enumerate(segments):
            valid_segment, ip_iters, slot_iters, slots, vdf_list = _validate_segment(
                constants,
                segment,
                curr_ssi,
                prev_ssi,
                curr_difficulty,
                prev_ses,
                idx == 0,
                sampled_seg_index == idx,
                height,
            )
            vdfs_to_validate.extend(vdf_list)
            if not valid_segment:
                log.error(f"failed to validate sub_epoch {segment.sub_epoch_n} segment {idx} slots")
                return None
            prev_ses = None
            total_blocks += 1
            total_slot_iters += slot_iters
            total_slots += slots
            total_ip_iters += ip_iters
    return vdfs_to_validate
```

**File:** chia/full_node/weight_proof.py (L1401-1404)
```python
    if first_in_sub_epoch and segment.sub_epoch_n == 0 and idx == 0:
        cc_sub_slot_hash = constants.GENESIS_CHALLENGE
    else:
        cc_sub_slot_hash = __get_cc_sub_slot(segment.sub_slots, idx, ses).get_hash()
```

**File:** chia/full_node/weight_proof.py (L1491-1493)
```python
        if idx < 0:
            log.error("malformed segment: no slot-end entry before challenge block")
            return None
```

**File:** chia/full_node/weight_proof.py (L1532-1554)
```python
def __get_cc_sub_slot(sub_slots: list[SubSlotData], idx: int, ses: SubEpochSummary | None) -> ChallengeChainSubSlot:
    sub_slot: SubSlotData | None = None
    for i in reversed(range(idx)):
        sub_slot = sub_slots[i]
        if sub_slot.cc_slot_end_info is not None:
            break

    assert sub_slot is not None
    assert sub_slot.cc_slot_end_info is not None

    icc_vdf = sub_slot.icc_slot_end_info
    icc_vdf_hash: bytes32 | None = None
    if icc_vdf is not None:
        icc_vdf_hash = icc_vdf.get_hash()
    cc_sub_slot = ChallengeChainSubSlot(
        sub_slot.cc_slot_end_info,
        icc_vdf_hash,
        None if ses is None else ses.get_hash(),
        None if ses is None else ses.new_sub_slot_iters,
        None if ses is None else ses.new_difficulty,
    )

    return cc_sub_slot
```

**File:** chia/_tests/weight_proof/test_weight_proof.py (L664-715)
```python
    @pytest.mark.anyio
    async def test_weight_proof_validation_challenge_at_segment_start(
        self, default_1000_blocks: list[FullBlock], blockchain_constants: ConsensusConstants
    ) -> None:
        """SEC-614: validation must not crash when a segment's challenge block
        is the first sub-slot entry (first_idx == 0).

        In legitimately-constructed proofs, segment creation always places at
        least one slot-end entry before the challenge block (first_idx >= 1).
        A malicious peer could send a crafted proof where first_idx == 0; the
        old ``assert first_idx`` rejected this with an AssertionError instead
        of cleanly failing validation.
        """
        blocks = default_1000_blocks
        header_cache, height_to_hash, sub_blocks, summaries = await load_blocks_dont_validate(
            blocks, blockchain_constants
        )
        wpf = WeightProofHandler(
            blockchain_constants, BlockchainMock(sub_blocks, header_cache, height_to_hash, summaries)
        )
        wp = await wpf.get_proof_of_weight(blocks[-1].header_hash)
        assert wp is not None

        # Find the first segment of sub_epoch > 0 and strip the leading
        # slot-end entries so the challenge block lands at index 0.
        modified_segments = list(wp.sub_epoch_segments)
        target_found = False
        for i, seg in enumerate(modified_segments):
            if seg.sub_epoch_n > 0:
                challenge_idx = next(
                    (j for j, ssd in enumerate(seg.sub_slots) if ssd.cc_slot_end is None),
                    None,
                )
                if challenge_idx is not None and challenge_idx > 0:
                    new_sub_slots = list(seg.sub_slots[challenge_idx:])
                    assert new_sub_slots[0].cc_slot_end is None
                    modified_segments[i] = seg.replace(sub_slots=new_sub_slots)
                    target_found = True
                    break

        assert target_found, "No segment found with leading slot-end entries to strip"

        modified_wp = dataclasses.replace(wp, sub_epoch_segments=modified_segments)

        # Pre-fix: AssertionError in __get_rc_sub_slot crashes validation.
        # Post-fix: the malformed segment causes a hash mismatch, returning
        # (False, 0) cleanly.
        wpf_verify = WeightProofHandler(
            blockchain_constants, BlockchainMock(sub_blocks, header_cache, height_to_hash, {})
        )
        valid, _fork_point = wpf_verify.validate_weight_proof_single_proc(modified_wp)
        assert not valid
```
