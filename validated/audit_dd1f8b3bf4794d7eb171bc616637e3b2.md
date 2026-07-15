### Title
Malicious Harvester Can Unconditionally Redirect Farmer Block Rewards via Unvalidated `farmer_reward_address_override` — (File: `chia/farmer/farmer_api.py`)

### Summary
A harvester connected to a farmer can set `farmer_reward_address_override` in its `RespondSignatures` message to any arbitrary puzzle hash. The farmer's `_process_respond_signatures()` accepts this override unconditionally, redirecting the farmer's 0.25 XCH block reward to the attacker's address. The only response is a log warning — no enforcement or rejection occurs.

### Finding Description

In `_process_respond_signatures()`, the farmer determines the farmer reward destination as follows:

```python
farmer_reward_address = self.farmer.farmer_target
if response.farmer_reward_address_override is not None:
    farmer_reward_address = response.farmer_reward_address_override
    include_source_signature_data = True
``` [1](#0-0) 

This `farmer_reward_address` is then passed directly into `DeclareProofOfSpace` and submitted to the full node: [2](#0-1) 

The `farmer_reward_address_override` field is part of the `RespondSignatures` streamable message sent by the harvester: [3](#0-2) 

When `NewProofOfSpace` arrives with `farmer_reward_address_override` set, the farmer calls `notify_farmer_reward_taken_by_harvester_as_fee()`, which only **logs** a warning about the fee quality convention (CHIP-22) — it does not block or reject the override: [4](#0-3) 

The fee quality check at lines 915–928 only emits `log.warning()` for invalid thresholds; it never prevents the override from being used. There is no cryptographic binding between the override address and any farmer-authorized key.

### Impact Explanation

A malicious harvester (e.g., a third-party compressed-plot service operating under CHIP-22) can set `farmer_reward_address_override` to any `bytes32` puzzle hash in every `RespondSignatures` response. The farmer will unconditionally use that address as `farmer_reward_puzzle_hash` in the foliage block data, causing the 0.25 XCH farmer coinbase reward to be paid to the attacker's address on every block won. This is an unauthorized, permanent payout redirection of XCH affecting every block the farmer wins while connected to the malicious harvester.

This matches the **High** allowed impact: "Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, **payout redirection**."

### Likelihood Explanation

Third-party harvesters are an explicitly supported and common deployment pattern (CHIP-22, DrPlotter, etc.). Any farmer who connects to a third-party harvester service is exposed. The attacker needs only to operate a harvester service and respond to `RequestSignatures` with a crafted `farmer_reward_address_override`. No key material, admin access, or cryptographic break is required.

### Recommendation

The farmer should validate `farmer_reward_address_override` against a farmer-configured allowlist of authorized override addresses, or require the override to be cryptographically signed by the farmer's own key. Alternatively, the farmer should enforce the fee quality threshold (reject the override rather than just log a warning) and cap the override to the agreed fee portion rather than the full farmer reward.

### Proof of Concept

1. Attacker operates a harvester service that farmers connect to.
2. When the farmer sends `RequestSignatures` for a valid proof of space, the attacker's harvester responds with a `RespondSignatures` message where `farmer_reward_address_override` is set to the attacker's puzzle hash.
3. In `_process_respond_signatures()` at `chia/farmer/farmer_api.py:917–918`, the farmer sets `farmer_reward_address = response.farmer_reward_address_override` without any validation.
4. The farmer submits `DeclareProofOfSpace` with the attacker's puzzle hash as `farmer_reward_address`.
5. The full node validates the block — `farmer_reward_puzzle_hash` is not constrained by consensus to match any farmer-configured address (only the pool target is signature-checked for old-style plots at `block_header_validation.py:781–786`). [5](#0-4) 

6. The 0.25 XCH farmer coinbase reward is paid to the attacker's address on every block won.

### Citations

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
