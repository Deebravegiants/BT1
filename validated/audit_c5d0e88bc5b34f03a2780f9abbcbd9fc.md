### Title
Unchecked `farmer_reward_address_override` in `RespondSignatures` Allows Any Connected Harvester to Redirect Farmer Block Rewards - (`chia/farmer/farmer_api.py`)

### Summary
The farmer unconditionally accepts `farmer_reward_address_override` from a harvester's `RespondSignatures` message and uses it as the `farmer_puzzle_hash` in `DeclareProofOfSpace`, with no enforcement that the override satisfies the CHIP-22 fee-quality threshold. A malicious harvester can set this field to any puzzle hash it controls, causing the farmer's 1/8 block reward to be paid to the attacker's address on every block won.

### Finding Description

The CHIP-22 fee convention (referenced throughout the codebase) allows third-party harvesters to take a portion of the farmer reward by overriding `farmer_reward_address_override`. The protocol intends that the farmer should enforce a fee-quality threshold before accepting the override. However, the enforcement is entirely absent in the critical code path.

**Step 1 – Harvester sends `NewProofOfSpace` with override (optional)**

In `FarmerAPI.new_proof_of_space`, when `farmer_reward_address_override is not None`, the farmer calls `notify_farmer_reward_taken_by_harvester_as_fee`, which only **logs** a warning if the fee threshold is violated. It does not reject the proof, does not return early, and does not prevent the block-building flow from continuing. [1](#0-0) [2](#0-1) 

**Step 2 – Harvester responds to `RequestSignatures` with an arbitrary override**

After the farmer sends `RequestSignatures` to the harvester, the harvester replies with `RespondSignatures`. The `RespondSignatures` message contains its own independent `farmer_reward_address_override` field: [3](#0-2) 

**Step 3 – Farmer unconditionally accepts the override with zero validation**

In `_process_respond_signatures`, the farmer replaces its own configured `farmer_target` with whatever `bytes32` the harvester supplied, with no fee-quality check whatsoever: [4](#0-3) 

This override is then placed directly into `DeclareProofOfSpace.farmer_puzzle_hash`: [5](#0-4) 

**Step 4 – Full node uses the attacker-supplied puzzle hash without further validation**

The full node's `declare_proof_of_space` handler reads `request.farmer_puzzle_hash` directly and passes it to `create_unfinished_block` as `farmer_reward_puzzle_hash`, with no check that it matches the farmer's configured address: [6](#0-5) 

The resulting block's foliage encodes the attacker's puzzle hash as the farmer reward destination, and the 1/8 block reward is paid there on-chain.

### Impact Explanation

Every block won by the farmer while a malicious harvester is connected can have its 1/8 farmer block reward (currently ~0.25 XCH per block) redirected to an address controlled by the harvester. This is unauthorized reward diversion of XCH, matching the **High** impact category: "Bypass of farmer authorization that enables unauthorized reward diversion."

### Likelihood Explanation

Any peer that successfully connects to the farmer as a harvester can exploit this. Third-party harvesters are an explicitly supported use case (CHIP-22), so the attacker surface is real and reachable without any key compromise. The attacker only needs to:
1. Connect to the farmer as a harvester (standard protocol connection).
2. Return a valid proof of space for a winning signage point.
3. Include `farmer_reward_address_override` pointing to their own puzzle hash in `RespondSignatures`.

### Recommendation

In `_process_respond_signatures`, before accepting `response.farmer_reward_address_override`, the farmer should verify that the fee-quality derived from the proof satisfies the `applied_fee_threshold` declared in the corresponding `NewProofOfSpace.fee_info`. If the threshold is not met, the override must be rejected and the block-building flow must either abort or fall back to `self.farmer.farmer_target`. The same enforcement should be applied in `new_proof_of_space` (not just logging).

### Proof of Concept

1. Attacker operates a harvester and connects to a victim farmer.
2. Harvester finds a valid proof of space for a winning signage point.
3. Harvester sends `NewProofOfSpace` (override optional at this stage).
4. Farmer sends `RequestSignatures` back to the harvester.
5. Harvester replies with `RespondSignatures` where `farmer_reward_address_override = attacker_puzzle_hash` (any `bytes32`).
6. `_process_respond_signatures` sets `farmer_reward_address = attacker_puzzle_hash` with no validation.
7. `DeclareProofOfSpace` is sent to the full node with `farmer_puzzle_hash = attacker_puzzle_hash`.
8. Full node calls `create_unfinished_block(..., farmer_reward_puzzle_hash=attacker_puzzle_hash, ...)`.
9. The resulting block pays the 1/8 farmer reward to the attacker's address. [7](#0-6) [8](#0-7)

### Citations

**File:** chia/farmer/farmer_api.py (L128-129)
```python
                if new_proof_of_space.farmer_reward_address_override is not None:
                    self.farmer.notify_farmer_reward_taken_by_harvester_as_fee(sp, new_proof_of_space)
```

**File:** chia/farmer/farmer_api.py (L916-933)
```python
                    farmer_reward_address = self.farmer.farmer_target
                    if response.farmer_reward_address_override is not None:
                        farmer_reward_address = response.farmer_reward_address_override
                        include_source_signature_data = True

                    return farmer_protocol.DeclareProofOfSpace(
                        response.challenge_hash,
                        challenge_chain_sp,
                        signage_point_index,
                        reward_chain_sp,
                        pospace,
                        agg_sig_cc_sp,
                        agg_sig_rc_sp,
                        farmer_reward_address,
                        pool_target,
                        pool_target_signature,
                        include_signature_source_data=include_source_signature_data,
                    )
```

**File:** chia/farmer/farmer.py (L911-934)
```python
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

**File:** chia/protocols/harvester_protocol.py (L131-139)
```python
class RespondSignatures(Streamable):
    plot_identifier: str
    challenge_hash: bytes32
    sp_hash: bytes32
    local_pk: G1Element
    farmer_pk: G1Element
    message_signatures: list[tuple[bytes32, G2Element]]
    include_source_signature_data: bool
    farmer_reward_address_override: bytes32 | None
```

**File:** chia/full_node/full_node_api.py (L1062-1074)
```python
            if prev_b is None:
                pool_target = PoolTarget(
                    self.full_node.constants.GENESIS_PRE_FARM_POOL_PUZZLE_HASH,
                    uint32(0),
                )
                farmer_ph = self.full_node.constants.GENESIS_PRE_FARM_FARMER_PUZZLE_HASH
            else:
                farmer_ph = request.farmer_puzzle_hash
                if request.proof_of_space.pool_contract_puzzle_hash is not None:
                    pool_target = PoolTarget(request.proof_of_space.pool_contract_puzzle_hash, uint32(0))
                else:
                    assert request.pool_target is not None
                    pool_target = request.pool_target
```
