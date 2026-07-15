### Title
Farmer Fee Threshold Not Enforced — Harvester Can Unconditionally Redirect Farmer XCH Reward - (File: chia/farmer/farmer.py, chia/farmer/farmer_api.py)

### Summary
The CHIP-22 harvester fee convention provides a `farmer_reward_address_override` mechanism allowing a third-party harvester to redirect the farmer's block reward to itself as a fee, gated by a `fee_quality` / `applied_fee_threshold` check. However, the threshold check in `notify_farmer_reward_taken_by_harvester_as_fee` is **purely advisory** (logging only). The override is accepted unconditionally in `_process_respond_signatures`, meaning any connected harvester can redirect 100% of the farmer's XCH reward to an arbitrary address regardless of the configured threshold.

### Finding Description

**Step 1 — Harvester sends override with any address**

When a harvester finds a valid proof of space, it sends `NewProofOfSpace` with `farmer_reward_address_override` set to any `bytes32` puzzle hash (e.g., its own wallet) and optionally `fee_info=None` or any `applied_fee_threshold`.

**Step 2 — Farmer checks threshold but does not enforce it**

In `FarmerAPI.new_proof_of_space`, when `farmer_reward_address_override is not None`, the farmer calls `notify_farmer_reward_taken_by_harvester_as_fee`: [1](#0-0) 

Inside that function, the fee quality is computed and compared to the threshold, but the result is only logged — no exception is raised, no early return, no flag is set to block the override: [2](#0-1) 

The function returns `None` in all branches. Execution continues unconditionally.

**Step 3 — Override is accepted unconditionally in `_process_respond_signatures`**

When the harvester returns `RespondSignatures` (which also carries `farmer_reward_address_override`), the farmer builds `DeclareProofOfSpace` using the override without any threshold check: [3](#0-2) 

**Step 4 — Full node creates block with diverted reward address**

`declare_proof_of_space` in the full node accepts `request.farmer_puzzle_hash` directly from the `DeclareProofOfSpace` message with no independent validation against the farmer's configured address: [4](#0-3) 

This `farmer_ph` is passed into `create_unfinished_block` and ultimately into `create_foliage`, which mints the farmer reward coin to that puzzle hash: [5](#0-4) 

The consensus layer validates that the reward coin matches `farmer_puzzle_hash` stored in the block record — but that record was set from the attacker-controlled value, so validation passes.

### Impact Explanation

A malicious third-party harvester can redirect the farmer's entire XCH block reward (1/8 of block reward + all transaction fees at that height) to any puzzle hash. The farmer has no on-chain or protocol-level recourse once the block is submitted. This is unauthorized payout redirection of XCH from an honest farmer.

The `calculate_harvester_fee_quality` function and the `applied_fee_threshold` field in `ProofOfSpaceFeeInfo` are the intended controls: [6](#0-5) 

But since the check result is never acted upon, the threshold is meaningless — analogous to the external report's division by `1e18` making the tip percent effectively zero.

### Likelihood Explanation

Any third-party harvester the farmer connects to can exploit this. The CHIP-22 protocol is explicitly designed for third-party harvesters, so this is a realistic and reachable attack path. The harvester need only set `farmer_reward_address_override` to its own address; no cryptographic break or key compromise is required.

### Recommendation

In `FarmerAPI.new_proof_of_space`, after calling `notify_farmer_reward_taken_by_harvester_as_fee`, check whether the fee quality actually passes the threshold. If it does not (or if `fee_info` is absent), drop the proof and return `None` rather than continuing to process it:

```python
if new_proof_of_space.farmer_reward_address_override is not None:
    if not self.farmer.validate_harvester_fee_threshold(sp, new_proof_of_space):
        self.farmer.log.warning("Rejecting proof: fee threshold not met")
        return None
```

The `notify_farmer_reward_taken_by_harvester_as_fee` function should return a boolean indicating pass/fail, and the caller must act on it.

### Proof of Concept

1. Farmer connects to a malicious third-party harvester.
2. Harvester finds a valid proof of space for a block-winning challenge.
3. Harvester sends `NewProofOfSpace` with `farmer_reward_address_override = attacker_puzzle_hash` and `fee_info = None`.
4. Farmer logs: *"Harvester illegitimately took reward by failing to provide its fee rate"* — but continues processing.
5. Farmer sends `RequestSignatures` to harvester; harvester responds with `RespondSignatures` also carrying `farmer_reward_address_override = attacker_puzzle_hash`.
6. `_process_respond_signatures` sets `farmer_reward_address = attacker_puzzle_hash` unconditionally.
7. `DeclareProofOfSpace` is sent to the full node with `farmer_puzzle_hash = attacker_puzzle_hash`.
8. Full node creates and propagates a block; the farmer reward coin (e.g., 250,000,000,000 mojos + fees) is minted to `attacker_puzzle_hash`.
9. Farmer receives nothing; attacker receives the full farmer reward.

### Citations

**File:** chia/farmer/farmer_api.py (L128-129)
```python
                if new_proof_of_space.farmer_reward_address_override is not None:
                    self.farmer.notify_farmer_reward_taken_by_harvester_as_fee(sp, new_proof_of_space)
```

**File:** chia/farmer/farmer_api.py (L916-919)
```python
                    farmer_reward_address = self.farmer.farmer_target
                    if response.farmer_reward_address_override is not None:
                        farmer_reward_address = response.farmer_reward_address_override
                        include_source_signature_data = True
```

**File:** chia/farmer/farmer.py (L908-934)
```python
        fee_quality = calculate_harvester_fee_quality(proof_of_space.proof.proof, sp.challenge_hash)
        fee_quality_rate = float(fee_quality) / float(0xFFFFFFFF) * 100.0

        if proof_of_space.fee_info is not None:
            fee_threshold = proof_of_space.fee_info.applied_fee_threshold
            fee_threshold_rate = float(fee_threshold) / float(0xFFFFFFFF) * 100.0

            if fee_quality <= fee_threshold:
                self.log.info(
                    f"Fee threshold passed for challenge '{challenge_str}': "
                    + f"{fee_quality_rate:.3f}%/{fee_threshold_rate:.3f}% ({fee_quality}/{fee_threshold})"
                )
            else:
                self.log.warning(
                    f"Invalid fee threshold for challenge '{challenge_str}': "
                    + f"{fee_quality_rate:.3f}%/{fee_threshold_rate:.3f}% ({fee_quality}/{fee_threshold})"
                )
                self.log.warning(
                    "Harvester illegitimately took a fee reward that "
                    + "did not belong to it or it incorrectly applied the fee convention."
                )
        else:
            self.log.warning(
                "Harvester illegitimately took reward by failing to provide its fee rate "
                + f"for challenge '{challenge_str}'. "
                + f"Fee quality was {fee_quality_rate:.3f}% ({fee_quality} or 0x{fee_quality:08x})"
            )
```

**File:** chia/farmer/farmer.py (L937-942)
```python
def calculate_harvester_fee_quality(proof: bytes, challenge: bytes32) -> uint32:
    """
    This calculates the 'fee quality' given a convention between farmers and third party harvesters.
    See CHIP-22: https://github.com/Chia-Network/chips/pull/88
    """
    return uint32(int.from_bytes(std_hash(proof + challenge)[32 - 4 :], byteorder="big", signed=False))
```

**File:** chia/full_node/full_node_api.py (L1068-1069)
```python
            else:
                farmer_ph = request.farmer_puzzle_hash
```

**File:** chia/consensus/block_creation.py (L164-168)
```python
            farmer_coin = create_farmer_coin(
                curr.height,
                curr.farmer_puzzle_hash,
                uint64(calculate_base_farmer_reward(curr.height) + curr.fees),
                constants.GENESIS_CHALLENGE,
```
