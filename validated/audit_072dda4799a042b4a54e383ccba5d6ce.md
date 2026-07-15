### Title
Malicious Harvester Can Unconditionally Redirect Farmer Block Rewards to Arbitrary Address — (`chia/farmer/farmer_api.py`)

### Summary
A connected harvester can set `farmer_reward_address_override` to any arbitrary puzzle hash in a `NewProofOfSpace` or `RespondSignatures` message. The farmer's only response to a fee-convention violation is a log warning — the override is still unconditionally applied, redirecting the farmer's XCH block reward to the attacker's address.

### Finding Description

CHIP-22 introduced `farmer_reward_address_override` as a mechanism for third-party harvesters to take a fee from the farmer reward. The fee convention uses a deterministic "fee quality" value derived from the proof and challenge hash to determine what fraction of rewards the harvester is entitled to claim.

When a harvester sends `NewProofOfSpace` with `farmer_reward_address_override` set, the farmer calls `notify_farmer_reward_taken_by_harvester_as_fee`: [1](#0-0) 

This function checks the fee quality against the harvester-supplied `applied_fee_threshold`, but when the check fails — or when `fee_info` is `None` entirely — it only emits a log warning and returns normally: [2](#0-1) 

After this non-enforcing check, execution continues in `_process_respond_signatures`. The `farmer_reward_address_override` from the harvester's `RespondSignatures` is then unconditionally applied with no further validation: [3](#0-2) 

The overridden address is then passed directly into `DeclareProofOfSpace` as the `farmer_reward_address`: [4](#0-3) 

The `farmer_reward_address_override` field is defined as an optional `bytes32` in the protocol, meaning any 32-byte value is accepted: [5](#0-4) 

### Impact Explanation

A malicious harvester that is legitimately connected to a farmer can set `farmer_reward_address_override` to its own puzzle hash on every winning proof of space, regardless of whether the fee quality convention is satisfied. The farmer's block reward (the farmer portion of the XCH coinbase reward) is then paid to the attacker's address instead of the farmer's configured `xch_target_address`. The farmer receives only a log warning with no automated disconnection or block of the override. This constitutes unauthorized payout redirection of XCH block rewards.

### Likelihood Explanation

Any harvester connected to the farmer — including third-party harvesters that the farmer operator has deliberately connected — can exploit this. No key compromise or privileged access is required beyond the existing harvester connection. The attacker simply sets `farmer_reward_address_override` to their own address on every `NewProofOfSpace` message for a winning proof.

### Recommendation

The farmer should enforce the fee convention, not merely log violations. When `farmer_reward_address_override` is set and the fee quality check fails (or `fee_info` is absent), the farmer should reject the override and fall back to `self.farmer.farmer_target`. Optionally, repeated violations should trigger disconnection of the offending harvester peer. The check in `notify_farmer_reward_taken_by_harvester_as_fee` should return a boolean indicating whether the override is legitimate, and `_process_respond_signatures` should only apply the override when that check passes.

### Proof of Concept

1. A harvester connects to a farmer (standard setup).
2. The harvester finds a valid proof of space that qualifies for block creation.
3. The harvester sends `NewProofOfSpace` with `farmer_reward_address_override=<attacker_puzzle_hash>` and either `fee_info=None` or `fee_info` with an `applied_fee_threshold` higher than the actual fee quality.
4. The farmer calls `notify_farmer_reward_taken_by_harvester_as_fee`, which logs a warning but does not block the override.
5. The farmer sends `RequestSignatures` to the harvester.
6. The harvester responds with `RespondSignatures` also containing `farmer_reward_address_override=<attacker_puzzle_hash>`.
7. In `_process_respond_signatures`, lines 917–918 unconditionally set `farmer_reward_address = response.farmer_reward_address_override`.
8. `DeclareProofOfSpace` is submitted to the full node with `farmer_reward_address` pointing to the attacker's puzzle hash.
9. The block is accepted by the network; the farmer's XCH reward is paid to the attacker.

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

**File:** chia/farmer/farmer.py (L920-934)
```python
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

**File:** chia/protocols/harvester_protocol.py (L68-77)
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
