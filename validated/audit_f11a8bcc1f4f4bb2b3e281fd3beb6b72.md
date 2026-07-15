### Title
Malicious Harvester Can Unconditionally Redirect Farmer's Block Reward to Arbitrary Address — (`chia/farmer/farmer_api.py`)

---

### Summary

A third-party harvester can set `farmer_reward_address_override` to any arbitrary puzzle hash in its `RespondSignatures` message. The farmer's `_process_respond_signatures()` accepts this override unconditionally and propagates it as `farmer_puzzle_hash` in `DeclareProofOfSpace` to the full node, permanently diverting the farmer's 1/8 block reward (base farmer reward) to the attacker's address. The CHIP-22 fee quality check in `notify_farmer_reward_taken_by_harvester_as_fee()` only emits log warnings and never blocks the override.

---

### Finding Description

CHIP-22 introduced `farmer_reward_address_override` in `NewProofOfSpace` and `RespondSignatures` to allow third-party harvesters to redirect the farmer's 1/8 reward as a service fee. The intended enforcement mechanism is a fee-quality threshold check: the harvester must prove its proof quality exceeds a declared threshold before the redirect is considered legitimate.

The check is implemented in `notify_farmer_reward_taken_by_harvester_as_fee()`: [1](#0-0) 

This function only logs warnings when the fee quality check fails — it never raises an exception, returns a sentinel, or sets any flag that would cause the caller to abort. The caller in `new_proof_of_space()` ignores the return value entirely: [2](#0-1) 

Later, in `_process_respond_signatures()`, the override from the harvester's `RespondSignatures` is accepted without any re-validation: [3](#0-2) 

This `farmer_reward_address` is placed directly into `DeclareProofOfSpace.farmer_puzzle_hash`: [4](#0-3) 

The full node then uses `request.farmer_puzzle_hash` verbatim as the farmer reward destination when constructing the block: [5](#0-4) 

The `farmer_reward_address_override` field is defined as an unconstrained `bytes32 | None` in the protocol: [6](#0-5) 

---

### Impact Explanation

Every block farmed by a plot managed by the malicious harvester will have its 1/8 base farmer reward (e.g., 0.25 XCH per block at current halving) permanently sent to the attacker's address instead of the farmer's configured `xch_target_address`. The diversion is on-chain and irreversible. The farmer has no mechanism to detect or prevent this at the protocol level — the warning logs are the only signal, and they are easy to suppress or ignore in a custom harvester implementation.

---

### Likelihood Explanation

Any entity that can connect a harvester to a farmer can exploit this. Third-party harvester services (the explicit target of CHIP-22) are an unprivileged attacker class. The attacker needs only to:
1. Run a harvester with valid plots that produce winning proofs.
2. Set `farmer_reward_address_override` to any address in `NewProofOfSpace` and `RespondSignatures`.

No key material, admin access, or cryptographic break is required.

---

### Recommendation

In `_process_respond_signatures()`, before accepting `response.farmer_reward_address_override`, enforce the fee quality check: compute `fee_quality = calculate_harvester_fee_quality(pospace.proof, response.challenge_hash)` and verify `fee_info is not None and fee_quality <= fee_info.applied_fee_threshold`. If the check fails, discard the override and use `self.farmer.farmer_target` instead (or drop the block candidate entirely). The same enforcement should be applied in `new_proof_of_space()` before proceeding with block creation when an override is present.

---

### Proof of Concept

1. Attacker deploys a harvester with valid plots and connects it to a victim farmer.
2. When the harvester finds a proof of space that wins a block, it sends `NewProofOfSpace` with `farmer_reward_address_override = attacker_puzzle_hash` and `fee_info = None` (or any `applied_fee_threshold`).
3. The farmer calls `notify_farmer_reward_taken_by_harvester_as_fee()`, which logs a warning but does not abort.
4. The farmer sends `RequestSignatures` to the harvester; the harvester responds with `RespondSignatures` also containing `farmer_reward_address_override = attacker_puzzle_hash`.
5. `_process_respond_signatures()` sets `farmer_reward_address = attacker_puzzle_hash` at line 918 and constructs `DeclareProofOfSpace` with this address as `farmer_puzzle_hash`.
6. The full node builds the block with `farmer_ph = request.farmer_puzzle_hash` (line 1069), minting the 1/8 farmer reward coin to `attacker_puzzle_hash`.
7. The farmer's reward is permanently lost to the attacker.

### Citations

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

**File:** chia/full_node/full_node_api.py (L1069-1069)
```python
                farmer_ph = request.farmer_puzzle_hash
```

**File:** chia/protocols/harvester_protocol.py (L74-76)
```python
    include_source_signature_data: bool
    farmer_reward_address_override: bytes32 | None
    fee_info: ProofOfSpaceFeeInfo | None
```
