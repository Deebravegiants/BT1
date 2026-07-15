### Title
Unvalidated `farmer_reward_address_override` in Harvester Protocol Allows Malicious Harvester to Unconditionally Redirect Farmer Block Rewards - (`chia/farmer/farmer_api.py`)

### Summary

A third-party harvester connected to a farmer can set `farmer_reward_address_override` to any arbitrary puzzle hash in a `NewProofOfSpace` or `RespondSignatures` message. The farmer's handler accepts this override and uses it verbatim in `DeclareProofOfSpace`, redirecting the XCH block reward to the attacker's address. The CHIP-22 fee quality threshold check in `notify_farmer_reward_taken_by_harvester_as_fee()` is purely advisory — it only emits log warnings and never rejects or suppresses the override. A malicious harvester can therefore steal 100% of the farmer's block rewards for every block won.

### Finding Description

**Root cause — no enforcement of the fee quality threshold:**

In `chia/farmer/farmer_api.py`, `new_proof_of_space()` handles the `NewProofOfSpace` message sent by a harvester. When `farmer_reward_address_override` is non-`None`, the farmer calls `notify_farmer_reward_taken_by_harvester_as_fee()`: [1](#0-0) 

That function computes the fee quality and checks it against the harvester-supplied `applied_fee_threshold`, but **only logs a warning** when the threshold is violated — it never returns an error, raises an exception, or signals the caller to abort: [2](#0-1) 

Execution continues unconditionally after the call, and the farmer proceeds to request signatures from the harvester.

**The override is applied without any re-check in `_process_respond_signatures()`:**

When the harvester replies with `RespondSignatures`, the farmer's `_process_respond_signatures()` blindly substitutes the harvester-supplied `farmer_reward_address_override` for the farmer's own configured reward address: [3](#0-2) 

No fee quality check is performed here at all. The resulting `DeclareProofOfSpace` carries the attacker-controlled address as `farmer_reward_address`: [4](#0-3) 

**Protocol message definitions:**

`farmer_reward_address_override` is a plain `bytes32 | None` field in both `NewProofOfSpace` and `RespondSignatures` — fully attacker-controlled with no cryptographic binding to the harvester's identity or to any agreed fee rate: [5](#0-4) [6](#0-5) 

**Exploit path:**

1. Attacker operates a third-party harvester and connects it to a victim farmer (a legitimate, unprivileged role).
2. When the harvester finds a winning proof, it sends `NewProofOfSpace` with `farmer_reward_address_override = attacker_puzzle_hash` and any `fee_info` (or `fee_info=None`).
3. The farmer calls `notify_farmer_reward_taken_by_harvester_as_fee()`, which logs a warning but does not block the flow.
4. The farmer sends `RequestSignatures` to the harvester.
5. The harvester replies with `RespondSignatures` also containing `farmer_reward_address_override = attacker_puzzle_hash`.
6. `_process_respond_signatures()` replaces `self.farmer.farmer_target` with the attacker's address.
7. The farmer submits `DeclareProofOfSpace` with the attacker's puzzle hash as the block reward destination.
8. The block is accepted by the network; the XCH reward is paid to the attacker.

### Impact Explanation

**HIGH** — Unauthorized reward diversion of XCH. A malicious third-party harvester can redirect 100% of the farmer's block rewards to any address for every block the harvester helps win. The farmer has no in-protocol mechanism to enforce a maximum fee rate or reject overrides that exceed the agreed threshold. The only recourse is manual disconnection after the theft has already occurred.

### Likelihood Explanation

Third-party harvesters are a supported, documented use case (CHIP-22). Any operator of a third-party harvester service can exploit this without any privileged access — they only need a farmer to connect to them, which is the normal operating mode for farmers using remote harvesters.

### Recommendation

Enforce the fee quality threshold before accepting the override. In `new_proof_of_space()`, after calling `notify_farmer_reward_taken_by_harvester_as_fee()`, compute `fee_quality` and compare it against `applied_fee_threshold`; if the threshold is not met (or `fee_info` is absent), set `farmer_reward_address_override` to `None` and proceed with the farmer's own configured address. Apply the same check in `_process_respond_signatures()` before substituting the override. This converts the advisory log into an enforced guard.

### Proof of Concept

```python
# Malicious harvester sends NewProofOfSpace with override set to attacker address
new_pos = harvester_protocol.NewProofOfSpace(
    challenge_hash=...,
    sp_hash=...,
    plot_identifier=...,
    proof=valid_proof_of_space,
    signage_point_index=...,
    include_source_signature_data=True,
    farmer_reward_address_override=attacker_puzzle_hash,  # any bytes32
    fee_info=ProofOfSpaceFeeInfo(applied_fee_threshold=uint32(0xFFFFFFFF)),  # max threshold
)
# farmer_api.py:128-129: notify_farmer_reward_taken_by_harvester_as_fee() logs only
# farmer_api.py:916-919: _process_respond_signatures() uses override unconditionally
# DeclareProofOfSpace.farmer_reward_address == attacker_puzzle_hash
# Block reward paid to attacker
```

The `applied_fee_threshold=0xFFFFFFFF` ensures `fee_quality <= fee_threshold` always passes the log check, but even with `fee_info=None` the override is still applied — the farmer only logs an additional warning and continues. [1](#0-0) [7](#0-6) [8](#0-7)

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

**File:** chia/protocols/harvester_protocol.py (L68-76)
```python
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
