### Title
CHIP-22 Fee Quality Check Computed But Never Enforced — Malicious Harvester Can Unconditionally Redirect Farmer XCH Reward - (File: chia/farmer/farmer.py, chia/farmer/farmer_api.py)

### Summary
The CHIP-22 fee convention computes a `fee_quality` value and checks it against the harvester-supplied `applied_fee_threshold`, but the result of that check is never enforced. A malicious third-party harvester can unconditionally redirect the farmer's XCH block reward (1/8 of the block reward) to any address it chooses, regardless of whether the fee quality threshold is legitimately met.

### Finding Description

The CHIP-22 convention (implemented in `chia/farmer/farmer.py`) allows a third-party harvester to redirect the farmer's block reward to itself by setting `farmer_reward_address_override` in `NewProofOfSpace`. The harvester is supposed to only do this when its proof's `fee_quality` is ≤ its self-reported `applied_fee_threshold`.

In `farmer_api.py`, when a `NewProofOfSpace` arrives with `farmer_reward_address_override` set, the farmer calls `notify_farmer_reward_taken_by_harvester_as_fee()`: [1](#0-0) 

Inside that function, `fee_quality` is computed and compared against `fee_threshold`: [2](#0-1) 

When the check **fails** (`fee_quality > fee_threshold`), the function only emits a `log.warning()`. It does not raise an exception, does not return a sentinel, and does not set any state that would block the override. The function signature is `-> None`.

Immediately after, in `_process_respond_signatures`, the `farmer_reward_address_override` from the harvester's `RespondSignatures` is applied **unconditionally**: [3](#0-2) 

This `farmer_reward_address` is then embedded in `DeclareProofOfSpace` and forwarded to the full node, which accepts it as the legitimate farmer reward puzzle hash: [4](#0-3) 

The full node has no knowledge of the CHIP-22 convention and does not validate whether the override was legitimately earned. Block body validation only checks that the reward coins match the puzzle hashes declared in the foliage: [5](#0-4) 

This is a direct structural analog to the Beanstalk bug: a value (`fee_quality` check result) is computed but the original unchecked value (`farmer_reward_address_override`) is used regardless.

### Impact Explanation

A malicious third-party harvester can redirect the farmer's XCH block reward (1/8 of the block reward, currently ~0.25 XCH per block) to any address it controls, without meeting the fee quality threshold. The farmer's XCH is permanently diverted with no recourse. This constitutes unauthorized reward diversion affecting XCH — a Critical/High impact per the allowed scope.

### Likelihood Explanation

Any third-party harvester that has an established connection to a farmer can exploit this. The harvester simply sets `farmer_reward_address_override` to its own puzzle hash in every `NewProofOfSpace` and `RespondSignatures` message. No special privileges, leaked keys, or cryptographic breaks are required. The farmer's own code will accept and propagate the override.

### Recommendation

In `farmer_api.py`, after calling `notify_farmer_reward_taken_by_harvester_as_fee()`, the farmer should reject the proof (return `None` and not proceed with `RequestSignatures`) when the fee quality check fails. The `notify_farmer_reward_taken_by_harvester_as_fee()` function should return a boolean indicating whether the check passed, and the caller should gate further processing on that result.

Similarly, in `_process_respond_signatures`, the farmer should verify that the `farmer_reward_address_override` in `RespondSignatures` matches the one originally declared in `NewProofOfSpace`, and that the fee quality check passed for that proof, before applying the override.

### Proof of Concept

1. A malicious third-party harvester connects to a farmer.
2. When it finds a valid proof of space, it sends `NewProofOfSpace` with `farmer_reward_address_override` set to its own puzzle hash and `fee_info.applied_fee_threshold = 0` (which will always fail the check since `fee_quality >= 0`).
3. The farmer calls `notify_farmer_reward_taken_by_harvester_as_fee()`, which computes `fee_quality > 0 = fee_threshold`, logs a warning, and returns `None`.
4. The farmer proceeds to send `RequestSignatures` to the harvester.
5. The harvester responds with `RespondSignatures` also containing `farmer_reward_address_override` set to its own address.
6. The farmer's `_process_respond_signatures` unconditionally sets `farmer_reward_address = response.farmer_reward_address_override` and emits `DeclareProofOfSpace` with the harvester's puzzle hash as the farmer reward address.
7. The full node accepts the block. The farmer's 1/8 block reward is paid to the harvester's address. [6](#0-5) [1](#0-0) [3](#0-2)

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

**File:** chia/farmer/farmer_api.py (L921-933)
```python
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

**File:** chia/consensus/block_body_validation.py (L311-315)
```python
    if set(block.transactions_info.reward_claims_incorporated) != expected_reward_coins:
        return Err.INVALID_REWARD_COINS

    if len(block.transactions_info.reward_claims_incorporated) != len(expected_reward_coins):
        return Err.INVALID_REWARD_COINS
```
