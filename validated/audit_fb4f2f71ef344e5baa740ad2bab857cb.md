Based on my code analysis, here is the verdict:

---

### Title
Malicious Harvester Can Unconditionally Override Farmer Block Reward Address via `RespondSignatures.farmer_reward_address_override` — (`chia/farmer/farmer_api.py`)

### Summary

A harvester that has a legitimate plot registered with the farmer can set `farmer_reward_address_override` to any attacker-controlled `bytes32` in a `RespondSignatures` message. The farmer's `_process_respond_signatures` accepts this override unconditionally — with no fee-threshold check — and forwards it directly as `farmer_reward_address` in `DeclareProofOfSpace` to the full node, permanently redirecting the block reward.

### Finding Description

**Protocol message definition — `RespondSignatures` lacks `fee_info`:**

`RespondSignatures` carries `farmer_reward_address_override: bytes32 | None` but has **no** `fee_info` field: [1](#0-0) 

By contrast, `NewProofOfSpace` carries both `farmer_reward_address_override` **and** `fee_info: ProofOfSpaceFeeInfo | None`, which is the field that was intended to gate the override under CHIP-22 fee-threshold logic: [2](#0-1) 

**Unconditional acceptance in `_process_respond_signatures`:** [3](#0-2) 

Lines 917–918 check only `if response.farmer_reward_address_override is not None` and immediately substitute the attacker-supplied address. There is no fee-threshold gate, no comparison against `self.farmer.farmer_target`, and no cryptographic commitment to the override value. The resulting `DeclareProofOfSpace` carries the attacker's `puzzle_hash` as `farmer_reward_address`.

**Guards that exist but do not block the attack:**

The function does verify:
- `response.sp_hash` is a known signage point (line 828–830) [4](#0-3) 
- `response.plot_identifier` has a registered proof of space (lines 845–849) [5](#0-4) 
- The SP-phase BLS aggregate signatures are valid (lines 882–893) [6](#0-5) 

All three guards are satisfiable by any legitimately connected harvester that has a plot and a valid proof for the current signage point. None of them constrain `farmer_reward_address_override`.

### Impact Explanation

Every block won while the malicious harvester is connected has its farmer reward (`1.75 XCH` pre-halving, `0.875 XCH` post-halving) permanently redirected to the attacker's address. The full node receives and acts on the `DeclareProofOfSpace` as-is; it has no knowledge of the farmer's configured `farmer_target` and cannot reject the override. This is an unauthorized payout redirection of XCH — a **High** impact under the allowed scope ("bypass of authorization that enables payout redirection").

### Likelihood Explanation

The attacker must be a harvester that:
1. Has a valid TLS certificate accepted by the farmer (i.e., is a connected, "trusted" harvester).
2. Has at least one plot registered in `proofs_of_space` for the current signage point.

This is the exact threat model for third-party harvester services (e.g., DrPlotter, referenced in the codebase). A malicious or compromised third-party harvester service satisfies both preconditions trivially. No leaked keys, broken crypto, or external assumptions are required.

### Recommendation

1. **Add `fee_info` to `RespondSignatures`** (mirroring `NewProofOfSpace`) and enforce the same fee-threshold gate before accepting `farmer_reward_address_override` in `_process_respond_signatures`.
2. **Alternatively**, reject `farmer_reward_address_override` in `RespondSignatures` entirely and only honour it from the `NewProofOfSpace` path where `fee_info` is already present and can be validated.
3. Log and alert whenever `farmer_reward_address_override` differs from `farmer_target`, regardless of whether it is accepted.

### Proof of Concept

```python
# Malicious harvester side (pseudocode):
# 1. Receive NewSignagePointHarvester from farmer (normal operation).
# 2. Find a valid proof of space for the signage point.
# 3. Send NewProofOfSpace to farmer (normal) so the proof is registered
#    in farmer.proofs_of_space[sp_hash].
# 4. Compute valid SP-phase BLS signatures (challenge_chain_sp, reward_chain_sp)
#    using the harvester's local_sk and the farmer's farmer_pk.
# 5. Construct RespondSignatures with:
#      farmer_reward_address_override = ATTACKER_PUZZLE_HASH  # arbitrary bytes32
#      fee_info = None  # field doesn't exist in RespondSignatures anyway
#      message_signatures = [(sp_hash, cc_sp_sig), (rc_sp_hash, rc_sp_sig)]
# 6. Send RespondSignatures to farmer.
#
# Expected result:
#   farmer._process_respond_signatures() reaches line 917, sets
#   farmer_reward_address = ATTACKER_PUZZLE_HASH, and returns
#   DeclareProofOfSpace(farmer_reward_address=ATTACKER_PUZZLE_HASH, ...)
#   which is broadcast to the full node.
#   The block reward coin is created at ATTACKER_PUZZLE_HASH.
```

The test can be validated by asserting that the `DeclareProofOfSpace` message sent to the full node carries `ATTACKER_PUZZLE_HASH` rather than `farmer.farmer_target`.

### Citations

**File:** chia/protocols/harvester_protocol.py (L66-77)
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

**File:** chia/protocols/harvester_protocol.py (L129-140)
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

**File:** chia/farmer/farmer_api.py (L828-830)
```python
        if response.sp_hash not in self.farmer.sps:
            self.farmer.log.warning(f"Do not have challenge hash {response.challenge_hash}")
            return None
```

**File:** chia/farmer/farmer_api.py (L845-849)
```python
        pospace = None
        for plot_identifier, candidate_pospace in self.farmer.proofs_of_space[response.sp_hash]:
            if plot_identifier == response.plot_identifier:
                pospace = candidate_pospace
        assert pospace is not None
```

**File:** chia/farmer/farmer_api.py (L882-893)
```python
                    farmer_share_cc_sp = AugSchemeMPL.sign(sk, challenge_chain_sp, agg_pk)
                    agg_sig_cc_sp = AugSchemeMPL.aggregate(
                        [challenge_chain_sp_harv_sig, farmer_share_cc_sp, taproot_share_cc_sp]
                    )
                    assert AugSchemeMPL.verify(agg_pk, challenge_chain_sp, agg_sig_cc_sp)

                    # This means it passes the sp filter
                    farmer_share_rc_sp = AugSchemeMPL.sign(sk, reward_chain_sp, agg_pk)
                    agg_sig_rc_sp = AugSchemeMPL.aggregate(
                        [reward_chain_sp_harv_sig, farmer_share_rc_sp, taproot_share_rc_sp]
                    )
                    assert AugSchemeMPL.verify(agg_pk, reward_chain_sp, agg_sig_rc_sp)
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
