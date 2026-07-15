### Title
Malicious Harvester Can Unconditionally Redirect Farmer Block Rewards via Unenforced `farmer_reward_address_override` in `RespondSignatures` - (File: chia/farmer/farmer_api.py)

---

### Summary

A connected harvester (e.g., a third-party harvester operating under the CHIP-22 fee convention) can set `farmer_reward_address_override` in its `RespondSignatures` message to any arbitrary puzzle hash. The farmer's `_process_respond_signatures` handler accepts this override unconditionally, redirecting the block reward (XCH) to the attacker's address. The advisory fee-quality check in `notify_farmer_reward_taken_by_harvester_as_fee` is only triggered by the earlier `NewProofOfSpace` message and only emits log warnings — it never rejects the override and is entirely bypassed when the harvester sets `farmer_reward_address_override = None` in `NewProofOfSpace` but then injects an attacker address in the subsequent `RespondSignatures`.

---

### Finding Description

CHIP-22 introduced `farmer_reward_address_override` as a field in both `harvester_protocol.NewProofOfSpace` and `harvester_protocol.RespondSignatures`, allowing third-party harvesters to redirect the farmer's block reward to themselves as a fee.

**Step 1 — Advisory check only, no enforcement.**
When the farmer receives `NewProofOfSpace` with a non-`None` `farmer_reward_address_override`, it calls `notify_farmer_reward_taken_by_harvester_as_fee`: [1](#0-0) 

That function computes a `fee_quality` and compares it to the harvester-supplied `applied_fee_threshold`, but only logs a warning on mismatch — it never returns an error, raises an exception, or prevents the override from being used: [2](#0-1) 

**Step 2 — Override is consumed from `RespondSignatures`, not `NewProofOfSpace`.**
After sending `RequestSignatures` to the harvester, the farmer processes the response in `_process_respond_signatures`. The actual reward address used in the block is taken from `response.farmer_reward_address_override` (the `RespondSignatures` field), with zero validation: [3](#0-2) 

This address is then placed directly into `DeclareProofOfSpace.farmer_puzzle_hash`: [4](#0-3) 

**Step 3 — Full node builds and the farmer signs a block with the attacker's address.**
The full node receives `DeclareProofOfSpace`, builds an `UnfinishedBlock` using `farmer_ph` (the attacker's address), stores it as a candidate, and sends `RequestSignedValues` back to the farmer: [5](#0-4) 

The farmer signs the `foliage_block_data_hash` — which commits to the attacker's `farmer_reward_puzzle_hash` — without checking whether it matches `self.farmer.farmer_target`. The full node validates only the BLS signature against `plot_public_key`: [6](#0-5) 

The block is accepted and the attacker receives the farmer's XCH block reward.

**The complete bypass path:**
A harvester can send `NewProofOfSpace` with `farmer_reward_address_override = None` (skipping even the advisory log check), then return `RespondSignatures` with `farmer_reward_address_override = <attacker_address>`. The farmer uses the `RespondSignatures` value unconditionally.

---

### Impact Explanation

**High — Unauthorized payout redirection of XCH block rewards.**

A malicious connected harvester can redirect 100% of the farmer's block rewards to an arbitrary address on every block the farmer wins. The farmer's configured `farmer_target` address is silently overridden. The farmer signs the block without verifying the reward address, and the full node accepts it. This is a direct, permanent financial loss of XCH for the farmer with no on-chain recourse.

---

### Likelihood Explanation

The attacker must be a harvester that has established a TLS connection to the farmer. In the CHIP-22 third-party harvester model — the exact scenario this feature was designed for — such a harvester is a realistic, semi-trusted counterparty. The farmer has no configuration option to disable `farmer_reward_address_override` acceptance, and no enforcement mechanism exists to cap or validate the override. Any third-party harvester operator can exploit this silently.

---

### Recommendation

1. **Enforce the fee-quality threshold before accepting the override.** In `_process_respond_signatures`, compute `calculate_harvester_fee_quality` and compare it to the harvester-supplied `applied_fee_threshold`. If the threshold is not met (or `fee_info` is absent), ignore the override and use `self.farmer.farmer_target`.
2. **Cross-validate `RespondSignatures.farmer_reward_address_override` against `NewProofOfSpace.farmer_reward_address_override`.** If the harvester did not declare an override in `NewProofOfSpace`, the farmer should reject a non-`None` override in `RespondSignatures`.
3. **Optionally, allow farmers to disable the CHIP-22 fee mechanism entirely** via a config flag, so operators who do not use third-party harvesters are not exposed.

---

### Proof of Concept

1. Malicious harvester connects to farmer (standard TLS handshake).
2. Harvester sends `NewProofOfSpace` with a valid proof and `farmer_reward_address_override = None` — no fee-quality check is triggered.
3. Farmer sends `RequestSignatures` to the harvester.
4. Harvester returns `RespondSignatures` with `farmer_reward_address_override = <attacker_puzzle_hash>`.
5. Farmer's `_process_respond_signatures` sets `farmer_reward_address = <attacker_puzzle_hash>` (line 918) and emits `DeclareProofOfSpace` with that address as `farmer_puzzle_hash`.
6. Full node builds `UnfinishedBlock` with `farmer_ph = <attacker_puzzle_hash>`, sends `RequestSignedValues` to farmer.
7. Farmer signs `foliage_block_data_hash` (which commits to `<attacker_puzzle_hash>`) — no address check performed.
8. Full node validates BLS signature, accepts block, propagates to network.
9. Block reward (XCH) is paid to `<attacker_puzzle_hash>`.

Relevant code locations:
- `chia/farmer/farmer_api.py` — `_process_respond_signatures`, lines 916–919 (unconditional override acceptance)
- `chia/farmer/farmer.py` — `notify_farmer_reward_taken_by_harvester_as_fee`, lines 920–928 (log-only, no enforcement)
- `chia/protocols/harvester_protocol.py` — `RespondSignatures.farmer_reward_address_override`, line 139 [3](#0-2) [7](#0-6) [8](#0-7)

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

**File:** chia/full_node/full_node_api.py (L1143-1194)
```python
            unfinished_block: UnfinishedBlock = create_unfinished_block(
                self.full_node.constants,
                total_iters_pos_slot,
                infusion_point_total_iters,
                request.signage_point_index,
                sp_iters,
                request.proof_of_space,
                cc_challenge_hash,
                farmer_ph,
                pool_target,
                get_plot_sig,
                get_pool_sig,
                sp_vdfs,
                timestamp,
                self.full_node.blockchain,
                b"",
                new_block_gen,
                prev_b,
                finished_sub_slots,
            )
            self.log.info("Made the unfinished block")
            if prev_b is not None:
                height = uint32(prev_b.height + 1)
            else:
                height = uint32(0)
            self.full_node.full_node_store.add_candidate_block(quality_string, height, unfinished_block)

            foliage_sb_data_hash = unfinished_block.foliage.foliage_block_data.get_hash()
            if unfinished_block.is_transaction_block():
                foliage_transaction_block_hash = unfinished_block.foliage.foliage_transaction_block_hash
            else:
                foliage_transaction_block_hash = bytes32.zeros
            assert foliage_transaction_block_hash is not None

            foliage_block_data: FoliageBlockData | None = None
            foliage_transaction_block_data: FoliageTransactionBlock | None = None
            rc_block_unfinished: RewardChainBlockUnfinished | None = None
            if request.include_signature_source_data:
                foliage_block_data = unfinished_block.foliage.foliage_block_data
                rc_block_unfinished = unfinished_block.reward_chain_block
                if unfinished_block.is_transaction_block():
                    foliage_transaction_block_data = unfinished_block.foliage_transaction_block

            message = farmer_protocol.RequestSignedValues(
                quality_string,
                foliage_sb_data_hash,
                foliage_transaction_block_hash,
                foliage_block_data=foliage_block_data,
                foliage_transaction_block_data=foliage_transaction_block_data,
                rc_block_unfinished=rc_block_unfinished,
            )
            await peer.send_message(make_msg(ProtocolMessageTypes.request_signed_values, message))
```

**File:** chia/full_node/full_node_api.py (L1242-1248)
```python
        if not AugSchemeMPL.verify(
            candidate.reward_chain_block.proof_of_space.plot_public_key,
            candidate.foliage.foliage_block_data.get_hash(),
            farmer_request.foliage_block_data_signature,
        ):
            self.log.warning("Signature not valid. There might be a collision in plots. Ignore this during tests.")
            return None
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
