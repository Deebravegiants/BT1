### Title
Malicious Harvester Can Unconditionally Redirect Farmer Block Rewards to Arbitrary Address Without Enforcement - (File: chia/farmer/farmer_api.py)

### Summary

The CHIP-22 fee convention allows a third-party harvester to redirect the farmer's block reward to an arbitrary address by setting `farmer_reward_address_override` in the `NewProofOfSpace` or `RespondSignatures` protocol messages. The farmer's only response to a fee-convention violation is to emit a log warning — it never rejects or ignores the override. A malicious harvester can therefore permanently redirect every XCH farmer reward it wins to an attacker-controlled address with no on-chain or protocol-level enforcement.

### Finding Description

`NewProofOfSpace.farmer_reward_address_override` is an optional `bytes32` field in the harvester-to-farmer protocol message. [1](#0-0) 

When the farmer receives a `NewProofOfSpace` with this field set, it calls `notify_farmer_reward_taken_by_harvester_as_fee`, which computes a "fee quality" score and compares it to the harvester-supplied `applied_fee_threshold`. If the threshold is invalid or absent, the function emits a `log.warning` and **returns normally** — it does not raise, does not set a flag, and does not suppress the override. [2](#0-1) 

Immediately after this non-blocking call, `_process_respond_signatures` unconditionally replaces `farmer_reward_address` with whatever the harvester supplied: [3](#0-2) 

The resulting `DeclareProofOfSpace` message carries the attacker-controlled puzzle hash as `farmer_reward_puzzle_hash`, which the full node uses to create the coinbase reward coin. There is no subsequent check that reverts this to the farmer's configured target. [4](#0-3) 

### Impact Explanation

Every block won by the farmer while connected to the malicious harvester has its XCH farmer reward (currently 0.25 XCH per block) permanently sent to the attacker's address. The farmer receives nothing and has no on-chain recourse. This is an unauthorized payout redirection of XCH, matching the **High** impact category: "Bypass of … authorization that enables … payout redirection."

### Likelihood Explanation

The attacker must operate a harvester that the victim farmer connects to. Third-party harvester services are a normal, documented use case (CHIP-22 was designed for them). A malicious operator of such a service, or an attacker who compromises an existing harvester connection, can exploit this silently. The farmer operator has no real-time alert beyond a log line that is easy to miss in production.

### Recommendation

`notify_farmer_reward_taken_by_harvester_as_fee` must return a boolean indicating whether the fee convention was satisfied. `_process_respond_signatures` must only apply `farmer_reward_address_override` when that boolean is `True`; otherwise it must discard the override and use `self.farmer.farmer_target`. Specifically:

1. Change `notify_farmer_reward_taken_by_harvester_as_fee` to return `bool`.
2. In `_process_respond_signatures`, gate the override on the return value:
   ```python
   if response.farmer_reward_address_override is not None:
       if self.farmer.notify_farmer_reward_taken_by_harvester_as_fee(sp, new_proof_of_space):
           farmer_reward_address = response.farmer_reward_address_override
   ```

### Proof of Concept

1. Operate a harvester service that the target farmer connects to.
2. When the harvester finds a winning proof, send `NewProofOfSpace` with `farmer_reward_address_override` set to an attacker-controlled puzzle hash and `fee_info=None` (or any `applied_fee_threshold` value).
3. The farmer calls `notify_farmer_reward_taken_by_harvester_as_fee`, which logs a warning and returns `None`.
4. `_process_respond_signatures` sets `farmer_reward_address = response.farmer_reward_address_override` unconditionally.
5. The farmer broadcasts `DeclareProofOfSpace` with the attacker's puzzle hash as `farmer_reward_puzzle_hash`.
6. The full node creates the coinbase reward coin at the attacker's address; the farmer receives 0 XCH for the block.

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
