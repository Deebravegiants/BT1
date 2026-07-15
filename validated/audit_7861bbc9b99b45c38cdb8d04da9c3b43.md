### Title
`assert` at check 2e raises `AssertionError` instead of `ValidationError` for crafted ICC presence mismatch — (`chia/consensus/block_header_validation.py`)

### Summary

Line 203 of `validate_unfinished_header_block` uses a bare Python `assert` to enforce the ICC presence invariant. A remote peer can craft a `finished_sub_slots` entry that makes this assert fire, raising `AssertionError` instead of returning a `ValidationError`. The function's declared return type is `tuple[uint64 | None, ValidationError | None]` — it is never supposed to raise.

### Finding Description

The relevant code is at line 203:

```python
# 2e. Validate that there is not icc iff icc_challenge hash is None
assert (sub_slot.infused_challenge_chain is None) == (icc_challenge_hash is None)
``` [1](#0-0) 

`icc_challenge_hash` is computed from the **existing chain state** (specifically `prev_b.deficit`), not from the attacker's input. The attacker controls `sub_slot.infused_challenge_chain` via the crafted `finished_sub_slots` list. When the chain is in a state where `prev_b.deficit < constants.MIN_BLOCKS_PER_CHALLENGE_BLOCK`, `icc_challenge_hash` will be set to a non-None value by the validator: [2](#0-1) 

The attacker then submits a `finished_sub_slots[0]` with `infused_challenge_chain = None`. The assert at line 203 evaluates `(None is None) == (bytes32_value is None)` → `True == False` → fires `AssertionError`.

There is a second reachable assert at line 194 with the same class of defect: [3](#0-2) 

This fires when a non-first sub-slot has `reward_chain.deficit < MIN_BLOCKS_PER_CHALLENGE_BLOCK` (attacker-controlled field) but `infused_challenge_chain = None`.

Lines 205–209 also use bare `assert` for subsequent ICC field checks: [4](#0-3) 

### Impact Explanation

The function signature declares `-> tuple[uint64 | None, ValidationError | None]`. [5](#0-4) 

Callers (including `validate_finished_header_block` at line 872) expect a return value, not a raised exception: [6](#0-5) 

An `AssertionError` propagating out of this function is unhandled at the validation layer. Depending on whether the full-node message handler has a broad `except Exception` guard (which I was unable to fully confirm from available search results), the impact ranges from:

- **Minimum**: incorrect peer handling — the peer is not penalized/banned as it would be for a `ValidationError`, allowing repeated submission
- **Likely**: the asyncio task handling the peer message crashes, disrupting that connection's processing
- **Worst case**: if the block-processing coroutine is not isolated per-peer, the entire block processing loop is killed, causing a long-lived inability to process valid blocks

Additionally, if the node is ever run with Python's `-O` flag (which strips asserts), check 2e is silently skipped entirely, and the code proceeds with `icc_challenge_hash` set but `infused_challenge_chain = None`, leading to incorrect validation downstream.

### Likelihood Explanation

- The attacker only needs to be a peer on the network (no keys, no stake)
- The precondition (`prev_b.deficit < MIN_BLOCKS_PER_CHALLENGE_BLOCK`) is a normal chain state that occurs regularly
- The crafted message requires only setting `infused_challenge_chain = None` in a `SubSlotData` struct — trivially constructable
- No cryptographic forgery is required; the assert fires before any VDF validation

### Recommendation

Replace all bare `assert` statements in the ICC validation path with explicit `ValidationError` returns:

```python
# 2e. Validate that there is not icc iff icc_challenge hash is None
if (sub_slot.infused_challenge_chain is None) != (icc_challenge_hash is None):
    return None, ValidationError(Err.SHOULD_NOT_HAVE_ICC)
```

Apply the same fix to lines 194, 205–209, and audit the rest of `validate_unfinished_header_block` and `validate_finished_header_block` for similar patterns.

### Proof of Concept

1. Connect to a full node as a peer when `prev_b.deficit` is 1–4 (e.g., shortly after a challenge block).
2. Construct an `UnfinishedHeaderBlock` with `finished_sub_slots` containing one entry where `infused_challenge_chain = None` and all other fields are otherwise plausible.
3. Send it via the `new_unfinished_block` protocol message.
4. Observe: the node raises `AssertionError` at line 203 of `block_header_validation.py` rather than returning `(None, ValidationError(...))`.
5. Confirm the peer is not banned and the message can be re-sent indefinitely.

### Citations

**File:** chia/consensus/block_header_validation.py (L56-56)
```python
) -> tuple[uint64 | None, ValidationError | None]:
```

**File:** chia/consensus/block_header_validation.py (L168-183)
```python
                if prev_b.deficit < constants.MIN_BLOCKS_PER_CHALLENGE_BLOCK:
                    # There should be no ICC chain if the last block's deficit is 16
                    # Prev sb's deficit is 0, 1, 2, 3, or 4
                    if finished_sub_slot_n == 0:
                        # This is the first sub slot after the last sb, which must have deficit 1-4, and thus an ICC
                        curr = prev_b
                        while not curr.is_challenge_block(constants) and not curr.first_in_sub_slot:
                            curr = blocks.block_record(curr.prev_hash)
                        if curr.is_challenge_block(constants):
                            icc_challenge_hash = curr.challenge_block_info_hash
                            icc_iters_committed = uint64(prev_b.sub_slot_iters - curr.ip_iters(constants))
                        else:
                            assert curr.finished_infused_challenge_slot_hashes is not None
                            icc_challenge_hash = curr.finished_infused_challenge_slot_hashes[-1]
                            icc_iters_committed = prev_b.sub_slot_iters
                        icc_iters_proof = uint64(prev_b.sub_slot_iters - prev_b.ip_iters(constants))
```

**File:** chia/consensus/block_header_validation.py (L193-194)
```python
                        finished_ss = header_block.finished_sub_slots[finished_sub_slot_n - 1]
                        assert finished_ss.infused_challenge_chain is not None
```

**File:** chia/consensus/block_header_validation.py (L202-203)
```python
                # 2e. Validate that there is not icc iff icc_challenge hash is None
                assert (sub_slot.infused_challenge_chain is None) == (icc_challenge_hash is None)
```

**File:** chia/consensus/block_header_validation.py (L204-209)
```python
                if sub_slot.infused_challenge_chain is not None:
                    assert icc_vdf_input is not None
                    assert icc_iters_proof is not None
                    assert icc_iters_committed is not None
                    assert icc_challenge_hash is not None
                    assert sub_slot.proofs.infused_challenge_chain_slot_proof is not None
```

**File:** chia/consensus/block_header_validation.py (L872-884)
```python
    required_iters, validate_unfinished_err = validate_unfinished_header_block(
        constants,
        blocks,
        unfinished_header_block,
        check_filter,
        expected_vs,
        False,
        check_sub_epoch_summary=check_sub_epoch_summary,
    )

    genesis_block = False
    if validate_unfinished_err is not None:
        return None, validate_unfinished_err
```
