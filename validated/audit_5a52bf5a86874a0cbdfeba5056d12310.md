### Title
Malicious Third-Party Harvester Can Unconditionally Redirect Farmer Block Rewards via Unenforced `farmer_reward_address_override` in `RespondSignatures` - (`chia/farmer/farmer_api.py`)

---

### Summary

The Chia farmer unconditionally accepts a `farmer_reward_address_override` field in the `RespondSignatures` protocol message from any connected harvester, redirecting the farmer's block reward (250 XCH) to an arbitrary attacker-controlled puzzle hash. The CHIP-22 fee quality threshold check is only a log-only warning and is never enforced; moreover, the `RespondSignatures` handler does not verify that the override was declared in the corresponding `NewProofOfSpace` message. A malicious third-party harvester (explicitly supported by CHIP-22) can exploit this to divert the full farmer reward to any address with no cryptographic authorization from the farmer.

---

### Finding Description

CHIP-22 introduced a "fee convention" allowing third-party harvesters to take a portion of the farmer's block reward by setting `farmer_reward_address_override` in the `NewProofOfSpace` message. The farmer is supposed to validate this against a fee quality threshold before accepting the override.

The actual reward address used in `DeclareProofOfSpace` is determined in `_process_respond_signatures()` in `chia/farmer/farmer_api.py`:

```python
farmer_reward_address = self.farmer.farmer_target
if response.farmer_reward_address_override is not None:
    farmer_reward_address = response.farmer_reward_address_override
    include_source_signature_data = True
``` [1](#0-0) 

The `response` here is `RespondSignatures` from the harvester. The farmer unconditionally replaces `farmer_target` with whatever address the harvester supplies — no fee quality check, no cross-validation against `NewProofOfSpace`, no cryptographic proof of authorization.

The fee quality check exists only in `new_proof_of_space()`:

```python
if new_proof_of_space.farmer_reward_address_override is not None:
    self.farmer.notify_farmer_reward_taken_by_harvester_as_fee(sp, new_proof_of_space)
``` [2](#0-1) 

But `notify_farmer_reward_taken_by_harvester_as_fee()` only emits log warnings — it never rejects the override or blocks the block-making flow: [3](#0-2) 

Furthermore, `_process_respond_signatures()` does not check whether the `NewProofOfSpace` that triggered this flow had `farmer_reward_address_override` set. A harvester can send `NewProofOfSpace` with `farmer_reward_address_override=None` (bypassing even the log-only check), then inject an arbitrary `farmer_reward_address_override` in the subsequent `RespondSignatures`.

The `RespondSignatures` protocol message explicitly carries this optional field: [4](#0-3) 

The resulting `DeclareProofOfSpace` is broadcast to all full nodes with the attacker's address as `farmer_reward_address`: [5](#0-4) 

---

### Impact Explanation

When a block is won, the farmer reward coin (250 XCH at current issuance) is created with `farmer_reward_puzzle_hash` set to whatever address was in `DeclareProofOfSpace`. By injecting an arbitrary `farmer_reward_address_override` in `RespondSignatures`, a malicious harvester causes the farmer's 250 XCH block reward to be permanently sent to the attacker's address. The farmer receives nothing. This is an unauthorized payout redirection of XCH with direct, irreversible financial impact — matching the **High** impact category: "Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection."

---

### Likelihood Explanation

CHIP-22 explicitly enables third-party harvesters (e.g., DrPlotter and similar services). Farmers who connect to third-party harvesters are directly exposed. The attacker only needs to be a connected harvester — no leaked keys, no host compromise, no cryptographic break required. The attack is silent (no on-chain anomaly until the block is won) and requires no special timing.

---

### Recommendation

1. **Enforce the fee quality threshold**: In `_process_respond_signatures()`, before accepting `farmer_reward_address_override`, compute `calculate_harvester_fee_quality` and reject the override if `fee_quality > applied_fee_threshold`.
2. **Cross-validate with `NewProofOfSpace`**: Store whether `farmer_reward_address_override` was declared in `NewProofOfSpace` (keyed by `sp_hash` + `plot_identifier`). Reject any `RespondSignatures` that introduces an override not declared in the corresponding `NewProofOfSpace`.
3. **Reject overrides that exceed the declared threshold**: Even if declared in `NewProofOfSpace`, the farmer should refuse to use the override if the fee quality check fails, rather than merely logging a warning.

---

### Proof of Concept

1. Farmer connects to a malicious third-party harvester (e.g., a DrPlotter-compatible service).
2. Harvester finds a valid proof of space and sends `NewProofOfSpace` to the farmer with `farmer_reward_address_override=None` and `fee_info=None` — no fee convention declared, no log warning triggered.
3. Farmer sends `RequestSignatures` back to the harvester.
4. Harvester responds with `RespondSignatures` where `farmer_reward_address_override` is set to the attacker's puzzle hash (any 32-byte value).
5. `_process_respond_signatures()` at line 917 detects the non-None override and sets `farmer_reward_address = attacker_puzzle_hash`.
6. Farmer broadcasts `DeclareProofOfSpace` with `farmer_reward_address = attacker_puzzle_hash` to all full nodes.
7. Full node creates the farmer reward coin (250 XCH) at the attacker's address. The legitimate farmer receives 0 XCH from the block they won.

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
