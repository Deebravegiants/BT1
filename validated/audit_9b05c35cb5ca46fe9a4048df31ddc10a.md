### Title
Harvester Can Unconditionally Redirect Farmer Block Rewards to Arbitrary Address via Unenforced `farmer_reward_address_override` — (`chia/farmer/farmer_api.py`)

### Summary

The `RespondSignatures` harvester protocol message contains a `farmer_reward_address_override` field. When set by a harvester, the farmer unconditionally substitutes this address for its own configured `farmer_target` in the `DeclareProofOfSpace` message sent to the full node. The only guard — a fee-quality threshold check — is advisory (log-only) and never enforced. Any connected harvester can redirect 100% of the farmer's block reward (XCH) to an attacker-controlled puzzle hash on every block won.

### Finding Description

`RespondSignatures` carries an optional `farmer_reward_address_override` field: [1](#0-0) 

In `_process_respond_signatures()`, the farmer unconditionally replaces its own `farmer_target` with whatever the harvester supplies: [2](#0-1) 

The resulting `DeclareProofOfSpace` carries the attacker-controlled address as `farmer_reward_address`: [3](#0-2) 

CHIP-22 introduced a fee-quality convention to legitimize this override: the harvester is supposed to prove its proof quality meets a threshold before taking the reward. The farmer calls `notify_farmer_reward_taken_by_harvester_as_fee()` when the override is present: [4](#0-3) 

But `notify_farmer_reward_taken_by_harvester_as_fee()` only logs warnings — it never rejects the override or prevents the farmer from proceeding: [5](#0-4) 

The full node accepts whatever `farmer_puzzle_hash` the farmer declares; there is no on-chain validation of this field for non-genesis blocks: [6](#0-5) 

Block header validation only checks the pool target, not the farmer reward puzzle hash: [7](#0-6) 

### Impact Explanation

Every block won by the farmer while connected to a malicious harvester will pay the farmer reward (currently 0.25 XCH per block) to the attacker's address. The farmer's own wallet receives nothing. This is an unauthorized payout redirection of XCH — a Critical/High impact under the allowed scope ("payout redirection … affecting XCH … or pool wallets").

### Likelihood Explanation

Third-party harvesters (e.g., DrPlotter) are common in the Chia ecosystem. Any harvester that connects to the farmer over the standard protocol can set `farmer_reward_address_override` to an arbitrary `bytes32` in its `RespondSignatures` reply. No key compromise, admin access, or cryptographic break is required. The harvester is a network peer, not a privileged administrator.

### Recommendation

1. **Enforce the fee-quality threshold**: If `farmer_reward_address_override` is set and the proof quality does not satisfy the declared `applied_fee_threshold`, the farmer must **drop** the `RespondSignatures` message and not proceed with block creation, rather than only logging a warning.
2. **Require `fee_info` when override is present**: If `farmer_reward_address_override` is non-`None` but `fee_info` is `None`, reject the response outright.
3. **Validate consistency**: Ensure the `farmer_reward_address_override` in `RespondSignatures` matches the one declared in the corresponding `NewProofOfSpace` message, preventing a harvester from switching the target address between the two messages.

### Proof of Concept

1. A malicious harvester connects to a farmer over the standard Chia harvester protocol.
2. When the harvester finds a valid proof of space, it sends `NewProofOfSpace` with `farmer_reward_address_override = attacker_puzzle_hash` and `fee_info = None` (or any `applied_fee_threshold`).
3. The farmer calls `notify_farmer_reward_taken_by_harvester_as_fee()`, which logs a warning but does not reject the message. [8](#0-7) 
4. The farmer requests signatures from the harvester via `RequestSignatures`.
5. The harvester replies with `RespondSignatures` containing `farmer_reward_address_override = attacker_puzzle_hash`.
6. `_process_respond_signatures()` sets `farmer_reward_address = attacker_puzzle_hash` with no further check. [2](#0-1) 
7. `DeclareProofOfSpace` is sent to the full node with the attacker's puzzle hash as the farmer reward destination.
8. The full node creates a block paying the farmer reward to the attacker. The farmer's wallet receives 0 XCH for the block.

### Citations

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

**File:** chia/full_node/full_node_api.py (L1068-1074)
```python
            else:
                farmer_ph = request.farmer_puzzle_hash
                if request.proof_of_space.pool_contract_puzzle_hash is not None:
                    pool_target = PoolTarget(request.proof_of_space.pool_contract_puzzle_hash, uint32(0))
                else:
                    assert request.pool_target is not None
                    pool_target = request.pool_target
```

**File:** chia/consensus/block_header_validation.py (L776-794)
```python
    # 20b. If pospace has a pool pk, check pool target signature. Should not check this for genesis block.
    elif header_block.reward_chain_block.proof_of_space.pool_public_key is not None:
        assert header_block.reward_chain_block.proof_of_space.pool_contract_puzzle_hash is None
        assert header_block.foliage.foliage_block_data.pool_signature is not None

        if not AugSchemeMPL.verify(
            header_block.reward_chain_block.proof_of_space.pool_public_key,
            bytes(header_block.foliage.foliage_block_data.pool_target),
            header_block.foliage.foliage_block_data.pool_signature,
        ):
            return None, ValidationError(Err.INVALID_POOL_SIGNATURE)
    else:
        # 20c. Otherwise, the plot is associated with a contract puzzle hash, not a public key
        assert header_block.reward_chain_block.proof_of_space.pool_contract_puzzle_hash is not None
        if (
            header_block.foliage.foliage_block_data.pool_target.puzzle_hash
            != header_block.reward_chain_block.proof_of_space.pool_contract_puzzle_hash
        ):
            return None, ValidationError(Err.INVALID_POOL_TARGET)
```
