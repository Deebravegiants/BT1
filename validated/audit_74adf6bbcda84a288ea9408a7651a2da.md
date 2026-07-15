### Title
Malicious Harvester Can Unconditionally Redirect Farmer Block Rewards via Unenforced `farmer_reward_address_override` - (File: chia/farmer/farmer_api.py)

### Summary

CHIP-22 introduced `farmer_reward_address_override` to allow third-party harvesters to take a fee from the farmer's 1/8 block reward, governed by a deterministic "fee quality" check. However, the farmer never enforces this check — it only logs a warning when the check fails. A malicious harvester connected to the farmer can set `farmer_reward_address_override` to any arbitrary address on every block it finds, unconditionally redirecting the farmer's XCH block reward to the attacker's wallet. The farmer's own signing key is used to declare the block with the attacker's reward address.

### Finding Description

**Root cause:** `notify_farmer_reward_taken_by_harvester_as_fee()` is advisory-only — it logs but never rejects or halts processing.

**Code path:**

1. A harvester sends `NewProofOfSpace` with `farmer_reward_address_override` set to the attacker's address.

In `farmer_api.py`, `new_proof_of_space()`:
```python
if new_proof_of_space.farmer_reward_address_override is not None:
    self.farmer.notify_farmer_reward_taken_by_harvester_as_fee(sp, new_proof_of_space)
# Execution continues unconditionally — no return/reject
``` [1](#0-0) 

2. `notify_farmer_reward_taken_by_harvester_as_fee()` computes the fee quality and compares it to the harvester-supplied threshold. When the check fails, it only emits `log.warning(...)` — there is no `return`, no exception, no rejection of the override: [2](#0-1) 

3. The farmer proceeds to request signatures from the harvester. When the harvester returns `RespondSignatures`, the farmer unconditionally substitutes the attacker's address as `farmer_reward_address`:

```python
farmer_reward_address = self.farmer.farmer_target
if response.farmer_reward_address_override is not None:
    farmer_reward_address = response.farmer_reward_address_override  # no guard
    include_source_signature_data = True
``` [3](#0-2) 

4. The farmer then signs and broadcasts `DeclareProofOfSpace` with the attacker's address as `farmer_reward_address`, using the farmer's own private key: [4](#0-3) 

The `farmer_reward_address_override` field is defined in both `NewProofOfSpace` and `RespondSignatures` protocol messages: [5](#0-4) [6](#0-5) 

### Impact Explanation

**High — Unauthorized payout redirection of XCH block rewards.**

A malicious third-party harvester can redirect the farmer's 1/8 block reward (currently 0.25 XCH per block) to any address it controls, on every block it finds. The farmer's signing key is used to authorize the block with the attacker's reward address. The farmer receives no reward for blocks won by the malicious harvester. This is a direct, permanent loss of XCH with no on-chain recourse once the block is confirmed.

### Likelihood Explanation

Third-party harvesters are an explicitly supported and common deployment pattern (CHIP-22). Any harvester operator who has been granted a connection to the farmer (via the private CA SSL certificate) can exploit this. The farmer operator has no in-protocol defense — the only mitigation is to disconnect the harvester after observing log warnings, which requires active monitoring.

### Recommendation

The farmer must enforce the fee quality check, not merely log it. When `farmer_reward_address_override` is present and the fee quality check fails (or `fee_info` is absent), the farmer should reject the proof and not proceed with block declaration:

```python
if new_proof_of_space.farmer_reward_address_override is not None:
    fee_quality = calculate_harvester_fee_quality(
        new_proof_of_space.proof.proof, sp.challenge_hash
    )
    if (new_proof_of_space.fee_info is None or
            fee_quality > new_proof_of_space.fee_info.applied_fee_threshold):
        self.farmer.log.warning("Rejecting invalid fee override from harvester")
        return None  # Hard reject
    self.farmer.notify_farmer_reward_taken_by_harvester_as_fee(sp, new_proof_of_space)
```

The same enforcement must be applied in `_process_respond_signatures` before accepting `response.farmer_reward_address_override`.

### Proof of Concept

1. Operator connects a malicious third-party harvester to the farmer (legitimate SSL connection via private CA).
2. Harvester finds a valid proof of space for a block-winning challenge.
3. Harvester sends `NewProofOfSpace` with `farmer_reward_address_override = attacker_address` and `fee_info = ProofOfSpaceFeeInfo(applied_fee_threshold=0xFFFFFFFF)` (maximum threshold, always passes the log check).
4. Farmer calls `notify_farmer_reward_taken_by_harvester_as_fee()` — logs "Fee threshold passed" — and continues.
5. Farmer requests signatures; harvester returns `RespondSignatures` with `farmer_reward_address_override = attacker_address`.
6. Farmer executes `farmer_reward_address = response.farmer_reward_address_override` at line 918 and broadcasts `DeclareProofOfSpace` with `farmer_reward_address = attacker_address`.
7. Block is confirmed on-chain; 0.25 XCH farmer reward is paid to `attacker_address`. The farmer receives nothing.

Alternatively, even with `fee_info=None` or a failing threshold, the farmer still proceeds (only a `log.warning` is emitted), so the attacker does not even need to supply a valid `fee_info`. [7](#0-6)

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

**File:** chia/farmer/farmer.py (L911-934)
```python
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
