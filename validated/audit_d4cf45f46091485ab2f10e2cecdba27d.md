### Title
Harvester Can Unconditionally Redirect Farmer Block Rewards to Any Address — (`File: chia/farmer/farmer_api.py`)

### Summary
A connected harvester can set `farmer_reward_address_override` to any arbitrary puzzle hash in `NewProofOfSpace` or `RespondSignatures` messages. The farmer accepts this override without enforcement, redirecting the farmer's XCH block reward to the attacker-controlled address. The only response to a threshold violation is a log warning; the override is still applied.

### Finding Description

The `NewProofOfSpace` and `RespondSignatures` harvester protocol messages each carry an optional `farmer_reward_address_override` field: [1](#0-0) [2](#0-1) 

In `_process_respond_signatures`, the farmer unconditionally replaces its own configured `farmer_target` with whatever address the harvester supplied: [3](#0-2) 

This `farmer_reward_address` is then placed directly into `DeclareProofOfSpace.farmer_puzzle_hash` and broadcast to the full node: [4](#0-3) 

The full node uses `request.farmer_puzzle_hash` verbatim when constructing the block foliage: [5](#0-4) 

The CHIP-22 fee convention check in `notify_farmer_reward_taken_by_harvester_as_fee` only emits log warnings when the threshold is violated — it never rejects or suppresses the override: [6](#0-5) 

The same unconditional acceptance occurs in the `new_proof_of_space` path: [7](#0-6) 

### Impact Explanation

When a block is won, the farmer reward (0.25 XCH per block) is paid to `farmer_puzzle_hash` in the block foliage. A malicious harvester that sets `farmer_reward_address_override` to its own address causes every block reward to be paid to the attacker rather than the farmer. This is direct, irreversible XCH theft — reward diversion affecting XCH — matching the Critical impact tier.

### Likelihood Explanation

Third-party harvesters (e.g., DrPlotter, explicitly referenced in the codebase) are a supported and common deployment pattern. A farmer operator who connects to an external harvesting service grants that service the ability to exploit this path. No key compromise, admin access, or cryptographic break is required — only a valid harvester connection, which is the normal operating mode for third-party harvesters. [8](#0-7) 

### Recommendation

1. **Enforce the fee quality threshold**: If `farmer_reward_address_override` is set and `fee_quality > applied_fee_threshold`, reject the override (drop the proof or revert to `farmer_target`) rather than logging a warning and proceeding.
2. **Restrict the override address**: Require the override address to match a pre-registered harvester fee address, or require the farmer operator to explicitly whitelist override addresses per harvester.
3. **Cryptographic commitment**: Require the harvester to sign the override address with the plot key so the farmer can verify the override is intentional and authorized.

### Proof of Concept

1. Attacker operates a malicious harvester (e.g., a modified DrPlotter) and connects it to a victim farmer node.
2. When the harvester finds a valid proof of space, it sends `NewProofOfSpace` with `farmer_reward_address_override = attacker_puzzle_hash` and `fee_info = ProofOfSpaceFeeInfo(applied_fee_threshold=0xFFFFFFFF)` (maximum threshold, guaranteeing the quality check always "fails").
3. The farmer calls `notify_farmer_reward_taken_by_harvester_as_fee`, logs a warning, but does **not** reject the override.
4. The farmer sends `DeclareProofOfSpace` to the full node with `farmer_puzzle_hash = attacker_puzzle_hash`.
5. The full node constructs the block with the attacker's address as the farmer reward recipient.
6. The 0.25 XCH farmer reward is paid to the attacker's address on-chain, with no recourse for the victim farmer. [9](#0-8) [10](#0-9)

### Citations

**File:** chia/protocols/harvester_protocol.py (L66-76)
```python
@streamable
@dataclass(frozen=True)
class NewProofOfSpace(Streamable):
    challenge_hash: bytes32
    sp_hash: bytes32
    plot_identifier: str
    proof: ProofOfSpace
    signage_point_index: uint8
    include_source_signature_data: bool
    farmer_reward_address_override: bytes32 | None
    fee_info: ProofOfSpaceFeeInfo | None
```

**File:** chia/protocols/harvester_protocol.py (L129-139)
```python
@streamable
@dataclass(frozen=True)
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

**File:** chia/farmer/farmer_api.py (L126-129)
```python
            # If the iters are good enough to make a block, proceed with the block making flow
            if required_iters < calculate_sp_interval_iters(self.farmer.constants, sp.sub_slot_iters):
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

**File:** chia/harvester/harvester_api.py (L515-526)
```python
        response: harvester_protocol.RespondSignatures = harvester_protocol.RespondSignatures(
            request.plot_identifier,
            request.challenge_hash,
            request.sp_hash,
            local_sk.get_g1(),
            farmer_public_key,
            message_signatures,
            False,
            None,
        )

        return make_msg(ProtocolMessageTypes.respond_signatures, response)
```
