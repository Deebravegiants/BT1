### Title
Malicious Harvester Unconditionally Redirects Farmer Block Reward via Unenforced `farmer_reward_address_override` in `RespondSignatures` — (File: chia/farmer/farmer_api.py)

### Summary
A malicious third-party harvester can redirect the farmer's XCH block reward to an arbitrary address by injecting `farmer_reward_address_override` into `RespondSignatures`. The farmer accepts this field unconditionally in `_process_respond_signatures` with no fee-quality check, completely bypassing the CHIP-22 authorization convention.

### Finding Description
CHIP-22 defines a voluntary fee convention: a third-party harvester may redirect the farmer's block reward to itself as a fee, but only when a deterministic fee-quality check passes. The fee-quality check is computed in `notify_farmer_reward_taken_by_harvester_as_fee` and is triggered **only** when `NewProofOfSpace.farmer_reward_address_override` is non-`None`. [1](#0-0) 

However, in `_process_respond_signatures`, the farmer unconditionally replaces its own configured reward address with whatever the harvester supplies in `RespondSignatures.farmer_reward_address_override`, with **no fee-quality check at all**: [2](#0-1) 

The resulting `farmer_reward_address` is then embedded in `DeclareProofOfSpace` and forwarded to the full node, which signs and finalises the block with the harvester-controlled address as the reward destination. [3](#0-2) 

A malicious harvester therefore has two independent bypass paths:

1. **Direct bypass via `RespondSignatures`**: Send `NewProofOfSpace` with `farmer_reward_address_override=None` (no fee-quality check triggered), then return `RespondSignatures` with `farmer_reward_address_override` set to an attacker-controlled address. The farmer uses it without any check.

2. **Soft-check bypass via `NewProofOfSpace`**: Even when `NewProofOfSpace.farmer_reward_address_override` is set and the fee-quality check fires, `notify_farmer_reward_taken_by_harvester_as_fee` only emits log warnings and never blocks the override: [4](#0-3) 

The `RespondSignatures` protocol message explicitly carries `farmer_reward_address_override` as a first-class field, confirmed by the test harness that injects it: [5](#0-4) 

The harvester's default implementation sets this field to `None`, but a malicious harvester can set it to any `bytes32`: [6](#0-5) 

### Impact Explanation
Every time the farmer wins a block while connected to a malicious third-party harvester, the entire farmer block reward (XCH) is diverted to the attacker's puzzle hash. This is a direct, repeatable financial loss — payout redirection of XCH rewards — which falls squarely under the High impact category.

### Likelihood Explanation
The CHIP-22 model explicitly anticipates farmers connecting to external, untrusted harvesters. Any harvester the farmer connects to can exploit this with zero additional privilege. The attacker only needs to be a connected harvester peer, a role reachable without any privileged assumptions.

### Recommendation
In `_process_respond_signatures`, before accepting `response.farmer_reward_address_override`, enforce the same fee-quality check that `notify_farmer_reward_taken_by_harvester_as_fee` performs. If `fee_quality > applied_fee_threshold` (or `fee_info` is absent), discard the override and fall back to `self.farmer.farmer_target`. Additionally, verify that `RespondSignatures.farmer_reward_address_override` matches the value declared in the corresponding `NewProofOfSpace` message, so the two fields cannot be set independently.

### Proof of Concept
1. Malicious harvester establishes a connection to the farmer.
2. Harvester discovers a valid proof of space and sends `NewProofOfSpace` with `farmer_reward_address_override=None` — no fee-quality check is triggered on the farmer side.
3. Farmer sends `RequestSignatures` to the harvester.
4. Malicious harvester returns `RespondSignatures` with `farmer_reward_address_override` set to an attacker-controlled puzzle hash.
5. `_process_respond_signatures` sets `farmer_reward_address = response.farmer_reward_address_override` with no validation.
6. Farmer broadcasts `DeclareProofOfSpace` to the full node with the attacker's address as the farmer reward destination.
7. The full node finalises the block; the farmer's XCH block reward is paid to the attacker.

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

**File:** chia/_tests/farmer_harvester/test_third_party_harvesters.py (L134-137)
```python
        # Inject overridden farmer reward address
        response: RespondSignatures = dataclasses.replace(
            RespondSignatures.from_bytes(result_msg.data), farmer_reward_address_override=farmer_reward_address
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
