### Title
Unvalidated `sub_epoch_n` Index in Weight Proof Segment Validation Causes Unhandled `IndexError`, Aborting Node Sync - (File: `chia/full_node/weight_proof.py`)

### Summary
In `_validate_sub_epoch_segments`, the `sub_epoch_n` value sourced from attacker-controlled weight proof bytes is used directly as an index into the `summaries` list without a bounds check. A crafted `WeightProof` with a `sub_epoch_n` exceeding the number of validated summaries raises an unhandled `IndexError`, aborting the sync process. A parallel unfixed assert (`assert sub_slot is not None`) in `__get_cc_sub_slot` — the same class of bug already patched in `__get_rc_sub_slot` (SEC-614) — provides a second trigger path via a challenge block placed at index 0 in a sampled segment.

### Finding Description

**Path 1 — Out-of-bounds `summaries[sub_epoch_n]`**

In `_validate_sub_epoch_segments`, `segments_by_sub_epoch` is built from the attacker-supplied `weight_proof_bytes`. The loop iterates over its keys as `sub_epoch_n`:

```python
for sub_epoch_n, segments in segments_by_sub_epoch.items():
    ...
    if not summaries[sub_epoch_n].reward_chain_hash == rc_sub_slot_hash:  # line 985
```

`summaries` has length equal to the number of sub-epoch summaries in the proof (validated earlier). There is no guard that `sub_epoch_n < len(summaries)`. An attacker sets `sub_epoch_n` to any value ≥ `len(summaries)`, triggering an `IndexError`. [1](#0-0) 

**Path 2 — `assert sub_slot is not None` in `__get_cc_sub_slot`**

`__get_cc_sub_slot` walks backwards from `idx` to find a slot-end entry:

```python
def __get_cc_sub_slot(sub_slots, idx, ses):
    sub_slot: SubSlotData | None = None
    for i in reversed(range(idx)):   # empty when idx == 0
        sub_slot = sub_slots[i]
        if sub_slot.cc_slot_end_info is not None:
            break
    assert sub_slot is not None      # fires when idx == 0
``` [2](#0-1) 

This is called from `__validate_pospace` whenever the genesis-block guard is not satisfied:

```python
if first_in_sub_epoch and segment.sub_epoch_n == 0 and idx == 0:
    cc_sub_slot_hash = constants.GENESIS_CHALLENGE
else:
    cc_sub_slot_hash = __get_cc_sub_slot(segment.sub_slots, idx, ses).get_hash()
``` [3](#0-2) 

An attacker crafts a segment with `sub_epoch_n > 0` and places the challenge block at index 0. The guard `first_in_sub_epoch and segment.sub_epoch_n == 0 and idx == 0` is false, so `__get_cc_sub_slot` is called with `idx == 0`, firing the assert. The identical class of bug was already fixed for `__get_rc_sub_slot` (SEC-614 test at line 664), but `__get_cc_sub_slot` was not updated. [4](#0-3) 

### Impact Explanation

Both exceptions propagate through `validate_weight_proof_inner` → `validate_weight_proof` → `request_validate_wp`, where they are caught and re-raised as `ValueError`:

```python
try:
    validated, fork_point, summaries = await self.weight_proof_handler.validate_weight_proof(response.wp)
except Exception as e:
    await weight_proof_peer.close(CONSENSUS_ERROR_BAN_SECONDS)
    raise ValueError(f"Weight proof validation threw an error {e}")
``` [5](#0-4) 

The `ValueError` propagates to `_sync`, which catches it and logs the error, leaving the node unable to complete sync: [6](#0-5) 

An attacker controlling multiple peers can persistently prevent a syncing node from catching up by serving malicious weight proofs. Each attempt bans one peer, but if the attacker controls enough sybil peers, the node is denied sync indefinitely. The wallet's `WalletWeightProofHandler.validate_weight_proof` calls `validate_weight_proof_inner` without a surrounding try/except, so the same crafted proof can crash wallet sync entirely. [7](#0-6) 

### Likelihood Explanation

Any unprivileged peer can serve a `RespondProofOfWeight` message. The node randomly selects one peer from those advertising the target peak. No authentication or prior trust is required. Crafting the malicious `sub_epoch_n` or placing a challenge block at index 0 requires only knowledge of the wire format, which is public.

### Recommendation

1. Add a bounds check before `summaries[sub_epoch_n]` in `_validate_sub_epoch_segments`:
   ```python
   if sub_epoch_n >= len(summaries):
       log.error(f"sub_epoch_n {sub_epoch_n} out of range for summaries (len={len(summaries)})")
       return None
   ```
2. Replace `assert sub_slot is not None` in `__get_cc_sub_slot` with a graceful error return (matching the SEC-614 fix applied to `__get_rc_sub_slot`), and propagate `None` up through `__validate_pospace` → `_validate_segment` → `_validate_sub_epoch_segments`.

### Proof of Concept

**Path 1:**
1. Construct a valid-looking `WeightProof` whose `sub_epoch_segments` contains one `SubEpochChallengeSegment` with `sub_epoch_n` set to a value ≥ the number of `sub_epochs` entries in the proof.
2. Serve this proof in response to a `RequestProofOfWeight` from a syncing node.
3. `_validate_sub_epoch_segments` reaches line 985 (`summaries[sub_epoch_n]`) and raises `IndexError`, aborting sync.

**Path 2:**
1. Construct a `WeightProof` with a segment where `sub_epoch_n > 0` and the first entry in `sub_slots` has `cc_slot_end is None` (marking it as a challenge block, `idx == 0`).
2. Ensure all segments in the proof share this structure so the randomly sampled segment always triggers the path.
3. `__validate_pospace` calls `__get_cc_sub_slot(segment.sub_slots, 0, ses)`, which iterates `reversed(range(0))` (empty), leaves `sub_slot = None`, and fires `assert sub_slot is not None`, aborting sync.

### Citations

**File:** chia/full_node/weight_proof.py (L969-987)
```python
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
```

**File:** chia/full_node/weight_proof.py (L1401-1404)
```python
    if first_in_sub_epoch and segment.sub_epoch_n == 0 and idx == 0:
        cc_sub_slot_hash = constants.GENESIS_CHALLENGE
    else:
        cc_sub_slot_hash = __get_cc_sub_slot(segment.sub_slots, idx, ses).get_hash()
```

**File:** chia/full_node/weight_proof.py (L1532-1540)
```python
def __get_cc_sub_slot(sub_slots: list[SubSlotData], idx: int, ses: SubEpochSummary | None) -> ChallengeChainSubSlot:
    sub_slot: SubSlotData | None = None
    for i in reversed(range(idx)):
        sub_slot = sub_slots[i]
        if sub_slot.cc_slot_end_info is not None:
            break

    assert sub_slot is not None
    assert sub_slot.cc_slot_end_info is not None
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

**File:** chia/full_node/full_node.py (L1129-1133)
```python
        except asyncio.CancelledError:
            self.log.warning("Syncing failed, CancelledError")
        except Exception as e:
            tb = traceback.format_exc()
            self.log.error(f"Error with syncing: {type(e)}{tb}")
```

**File:** chia/full_node/full_node.py (L1183-1187)
```python
        try:
            validated, fork_point, summaries = await self.weight_proof_handler.validate_weight_proof(response.wp)
        except Exception as e:
            await weight_proof_peer.close(CONSENSUS_ERROR_BAN_SECONDS)
            raise ValueError(f"Weight proof validation threw an error {e}")
```

**File:** chia/wallet/wallet_weight_proof_handler.py (L45-67)
```python
    async def validate_weight_proof(
        self, weight_proof: WeightProof, skip_segment_validation: bool = False, old_proof: WeightProof | None = None
    ) -> list[BlockRecord]:
        start_time = time.time()
        summaries, sub_epoch_weight_list = _validate_sub_epoch_summaries(self._constants, weight_proof)
        await asyncio.sleep(0)  # break up otherwise multi-second sync code
        if summaries is None or sub_epoch_weight_list is None:
            raise ValueError("weight proof failed sub epoch data validation")
        validate_from = get_fork_ses_idx(old_proof, weight_proof)
        valid, block_records = await validate_weight_proof_inner(
            self._constants,
            self._executor,
            self._executor_shutdown_tempfile.name,
            self._num_processes,
            weight_proof,
            summaries,
            sub_epoch_weight_list,
            skip_segment_validation,
            validate_from,
        )
        if not valid:
            raise ValueError("weight proof validation failed")
        log.info(f"It took {time.time() - start_time} time to validate the weight proof {weight_proof.get_hash()}")
```
