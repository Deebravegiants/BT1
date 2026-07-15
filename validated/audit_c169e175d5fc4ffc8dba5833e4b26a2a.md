### Title
Malicious Harvester Can Unconditionally Redirect Farmer Block Reward via Unvalidated `farmer_reward_address_override` in `RespondSignatures` - (File: chia/farmer/farmer_api.py)

---

### Summary

The CHIP-22 fee convention allows third-party harvesters to redirect the farmer's block reward to their own address as a fee. However, `FarmerAPI._process_respond_signatures()` accepts `RespondSignatures.farmer_reward_address_override` unconditionally — with no fee-convention enforcement — allowing any connected harvester to permanently redirect the farmer's XCH block reward to an arbitrary attacker-controlled address.

---

### Finding Description

**Root cause — two compounding gaps:**

**Gap 1 — Fee check is advisory only (`new_proof_of_space`, line 128–129):**

When a harvester sends `NewProofOfSpace` with `farmer_reward_address_override` set, the farmer calls `notify_farmer_reward_taken_by_harvester_as_fee()`. That function computes `fee_quality` and compares it to `applied_fee_threshold`, but when the convention is violated it **only emits a `log.warning`** — it never returns an error, never sets a flag, and never prevents the block-making flow from continuing. [1](#0-0) [2](#0-1) 

**Gap 2 — `RespondSignatures.farmer_reward_address_override` is accepted with zero validation (`_process_respond_signatures`, lines 916–919):**

After the farmer sends `RequestSignatures` to the harvester, the harvester's `RespondSignatures` reply also carries a `farmer_reward_address_override` field. The farmer replaces its own configured `farmer_target` with whatever address the harvester supplies, with no check that the fee convention was satisfied, and no check that this field is consistent with what was declared in `NewProofOfSpace`. [3](#0-2) 

The resulting `farmer_reward_address` is placed directly into `DeclareProofOfSpace` and broadcast to the full node: [4](#0-3) 

**Protocol field definitions:** [5](#0-4) [6](#0-5) 

**Simplest exploit path (bypasses even the advisory log):**

1. Attacker's harvester sends `NewProofOfSpace` with `farmer_reward_address_override=None` — the fee-convention check in `new_proof_of_space()` is never triggered at all (the `if` at line 128 is false).
2. Farmer sends `RequestSignatures` to the harvester.
3. Harvester replies with `RespondSignatures` where `farmer_reward_address_override = attacker_puzzle_hash`.
4. `_process_respond_signatures()` unconditionally sets `farmer_reward_address = attacker_puzzle_hash` (lines 917–918).
5. `DeclareProofOfSpace` is sent to the full node with the attacker's address as the farmer reward destination.
6. The full node creates the block; the farmer reward coin (currently 0.25 XCH) is created at the attacker's puzzle hash.

**Alternative path (fee check triggered but not enforced):**

1. Harvester sends `NewProofOfSpace` with `farmer_reward_address_override = attacker_address`.
2. `notify_farmer_reward_taken_by_harvester_as_fee()` logs `"Invalid fee threshold"` but returns normally.
3. Block-making flow continues; harvester sets the same override in `RespondSignatures`.
4. Same outcome — reward redirected. [7](#0-6) 

---

### Impact Explanation

**High — unauthorized payout redirection affecting XCH.**

Every block the farmer wins while the malicious harvester is connected has its 0.25 XCH farmer reward permanently sent to the attacker's address. The farmer receives nothing. The loss is irreversible once the block is confirmed. This directly matches the allowed High impact: *"payout redirection… affecting XCH… or pool wallets."*

---

### Likelihood Explanation

CHIP-22 explicitly supports third-party harvesters (e.g., DrPlotter). A farmer operator who connects to any external harvester service is fully exposed. The attacker needs only a valid proof of space for the current signage point — which the harvester legitimately produces — and then injects the override in `RespondSignatures`. No key material, no admin access, and no cryptographic break is required. The farmer's own signing keys are used to complete the block, making the redirect indistinguishable from a legitimate fee at the consensus layer.

---

### Recommendation

1. **Enforce, not just log, the fee convention.** In `notify_farmer_reward_taken_by_harvester_as_fee()`, return a boolean indicating whether the convention passed, and in `new_proof_of_space()` abort the block-making flow (do not send `RequestSignatures`) when it fails.

2. **Validate `RespondSignatures.farmer_reward_address_override` against the pre-approved state.** Store whether the fee convention was accepted for a given `(sp_hash, plot_identifier)` tuple when processing `NewProofOfSpace`. In `_process_respond_signatures()`, only accept `farmer_reward_address_override` if that stored flag is set and the override address matches what was declared in `NewProofOfSpace`.

3. **Reject mismatches between `NewProofOfSpace.farmer_reward_address_override` and `RespondSignatures.farmer_reward_address_override`.** If `NewProofOfSpace` carried `None` but `RespondSignatures` carries a non-`None` override, the farmer should drop the response.

---

### Proof of Concept

```python
# Attacker-controlled harvester pseudocode

def on_request_signatures(request):
    # Produce a valid signature for the SP hashes as normal
    sigs = sign_normally(request)
    # Inject attacker's puzzle hash — no fee info needed
    return RespondSignatures(
        ...sigs,
        farmer_reward_address_override=ATTACKER_PUZZLE_HASH,  # arbitrary address
    )

def on_new_signage_point(sp):
    proof = find_proof(sp)
    if proof:
        send NewProofOfSpace(
            proof=proof,
            farmer_reward_address_override=None,  # bypass advisory check
            fee_info=None,
        )
```

The farmer's `_process_respond_signatures()` at lines 917–918 unconditionally replaces `farmer_target` with `ATTACKER_PUZZLE_HASH`, and the resulting `DeclareProofOfSpace` at line 929 carries the attacker's address to the full node. The farmer's XCH reward is permanently lost on every block won. [8](#0-7)

### Citations

**File:** chia/farmer/farmer_api.py (L127-130)
```python
            if required_iters < calculate_sp_interval_iters(self.farmer.constants, sp.sub_slot_iters):
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

**File:** chia/farmer/farmer.py (L920-928)
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
```

**File:** chia/protocols/harvester_protocol.py (L60-76)
```python
@streamable
@dataclass(frozen=True)
class ProofOfSpaceFeeInfo(Streamable):
    applied_fee_threshold: uint32


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
