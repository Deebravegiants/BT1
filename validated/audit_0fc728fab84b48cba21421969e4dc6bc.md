### Title
Unenforced CHIP-22 Fee Quality Check Allows Third-Party Harvester to Unconditionally Redirect Farmer Block Rewards - (File: chia/farmer/farmer_api.py, chia/farmer/farmer.py)

### Summary

A third-party harvester connected to a farmer can set `farmer_reward_address_override` in its `RespondSignatures` message to any arbitrary puzzle hash. The farmer unconditionally accepts this override and uses it as the `farmer_puzzle_hash` in `DeclareProofOfSpace`, causing the full node to build a block that pays the 1.75 XCH farmer block reward to the harvester's chosen address instead of the farmer's configured `farmer_target`. The CHIP-22 fee quality check in `notify_farmer_reward_taken_by_harvester_as_fee()` only emits log warnings and never blocks the override, even when the fee threshold is violated.

### Finding Description

CHIP-22 introduced a mechanism allowing third-party harvesters to redirect the farmer block reward as a fee. The protocol involves two separate `farmer_reward_address_override` fields:

**Step 1 — `NewProofOfSpace` (harvester → farmer):** When a harvester sends a winning proof with `farmer_reward_address_override` set, `FarmerAPI.new_proof_of_space()` calls `notify_farmer_reward_taken_by_harvester_as_fee()`: [1](#0-0) 

`notify_farmer_reward_taken_by_harvester_as_fee()` computes a `fee_quality` and compares it to the harvester-supplied `applied_fee_threshold`. When the threshold is violated, it **only logs a warning** and returns — it never blocks the override: [2](#0-1) 

**Step 2 — `RespondSignatures` (harvester → farmer):** In `_process_respond_signatures()`, the farmer unconditionally replaces `farmer_reward_address` with whatever `farmer_reward_address_override` the harvester placed in `RespondSignatures` — with **no fee quality check at all**: [3](#0-2) 

This `farmer_reward_address` is then placed directly into `DeclareProofOfSpace.farmer_puzzle_hash`: [4](#0-3) 

The full node receives `DeclareProofOfSpace`, uses `request.farmer_puzzle_hash` verbatim to build the unfinished block: [5](#0-4) 

The resulting block's foliage encodes the harvester-controlled address as `farmer_reward_puzzle_hash`, which is validated by consensus only for signature correctness (the plot key signs the foliage hash, not the farmer address): [6](#0-5) 

There is no consensus rule that restricts `farmer_reward_puzzle_hash` to the farmer's configured address.

A harvester can also bypass even the logging path entirely by setting `NewProofOfSpace.farmer_reward_address_override = None` (suppressing the fee notification) while setting `RespondSignatures.farmer_reward_address_override = attacker_address`, since the two fields are independent and the `RespondSignatures` path has zero enforcement.

### Impact Explanation

Every block won by a plot managed by the malicious harvester pays the 1.75 XCH farmer block reward to the harvester's address instead of the farmer's `xch_target_address`. This is a direct, permanent, on-chain payout redirection of XCH. The farmer receives no reward for blocks they win. This matches the allowed High impact: "Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, **payout redirection**."

### Likelihood Explanation

Any third-party harvester connected to the farmer — a common configuration for large farming operations using CHIP-22 — can perform this attack. No special privileges, leaked keys, or cryptographic breaks are required. The harvester only needs to be a connected peer and return a valid proof of space with a valid plot signature.

### Recommendation

The farmer should enforce the fee quality check rather than merely logging it. When `fee_quality > applied_fee_threshold` (or when `fee_info` is absent), the farmer should reject the override and fall back to `self.farmer.farmer_target` instead of proceeding with the harvester-supplied address. The check should be applied consistently to both `NewProofOfSpace.farmer_reward_address_override` and `RespondSignatures.farmer_reward_address_override`.

### Proof of Concept

1. A third-party harvester connects to a farmer (standard CHIP-22 setup).
2. The harvester finds a valid proof of space for a signage point.
3. The harvester sends `NewProofOfSpace` with `farmer_reward_address_override = attacker_puzzle_hash` and `fee_info.applied_fee_threshold` set to a value that fails the fee quality check (e.g., `uint32(0xFFFFFFFF)`).
4. The farmer calls `notify_farmer_reward_taken_by_harvester_as_fee()`, which logs `"Invalid fee threshold"` but does **not** return early or block.
5. The farmer sends `RequestSignatures` to the harvester.
6. The harvester responds with `RespondSignatures` containing `farmer_reward_address_override = attacker_puzzle_hash`.
7. `_process_respond_signatures()` sets `farmer_reward_address = attacker_puzzle_hash` with no check.
8. The farmer broadcasts `DeclareProofOfSpace(farmer_puzzle_hash=attacker_puzzle_hash)` to the full node.
9. The full node builds and finalizes a block paying 1.75 XCH to `attacker_puzzle_hash`.
10. The farmer's configured `xch_target_address` receives nothing. [7](#0-6) [8](#0-7)

### Citations

**File:** chia/farmer/farmer_api.py (L128-129)
```python
                if new_proof_of_space.farmer_reward_address_override is not None:
                    self.farmer.notify_farmer_reward_taken_by_harvester_as_fee(sp, new_proof_of_space)
```

**File:** chia/farmer/farmer_api.py (L914-933)
```python
                    include_source_signature_data = response.include_source_signature_data

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

**File:** chia/farmer/farmer.py (L888-934)
```python
    def notify_farmer_reward_taken_by_harvester_as_fee(
        self, sp: farmer_protocol.NewSignagePoint, proof_of_space: harvester_protocol.NewProofOfSpace
    ) -> None:
        """
        Apply a fee quality convention (see CHIP-22: https://github.com/Chia-Network/chips/pull/88)
        given the proof and signage point. This will be tested against the fee threshold reported
        by the harvester (if any), and logged.
        """
        assert proof_of_space.farmer_reward_address_override is not None

        challenge_str = str(sp.challenge_hash)

        ph_prefix = self.config["network_overrides"]["config"][self.config["selected_network"]]["address_prefix"]
        farmer_reward_puzzle_hash = encode_puzzle_hash(proof_of_space.farmer_reward_address_override, ph_prefix)

        self.log.info(
            f"Farmer reward for challenge '{challenge_str}' "
            + f"taken by harvester for reward address '{farmer_reward_puzzle_hash}'"
        )

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

**File:** chia/full_node/full_node_api.py (L1068-1069)
```python
            else:
                farmer_ph = request.farmer_puzzle_hash
```

**File:** chia/consensus/block_header_validation.py (L731-737)
```python
    # 16. Check foliage block signature by plot key
    if not AugSchemeMPL.verify(
        header_block.reward_chain_block.proof_of_space.plot_public_key,
        header_block.foliage.foliage_block_data.get_hash(),
        header_block.foliage.foliage_block_data_signature,
    ):
        return None, ValidationError(Err.INVALID_PLOT_SIGNATURE)
```
