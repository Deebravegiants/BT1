### Title
Malicious Third-Party Harvester Can Unconditionally Redirect Farmer Block Reward via Unenforced `farmer_reward_address_override` — (`chia/farmer/farmer_api.py`)

---

### Summary

A malicious third-party harvester can redirect the farmer's block reward (1/8 of the block reward, the `farmer_reward_puzzle_hash` in `FoliageBlockData`) to an arbitrary attacker-controlled address by setting `farmer_reward_address_override` in a `RespondSignatures` message. The CHIP-22 fee quality convention check in `notify_farmer_reward_taken_by_harvester_as_fee()` is only a log warning — it never blocks the override — and it is only evaluated on the `NewProofOfSpace` message, not on `RespondSignatures`. The farmer unconditionally accepts the override from `RespondSignatures` with no fee quality enforcement at all.

---

### Finding Description

The CHIP-22 protocol (third-party harvester fee convention) allows a harvester to redirect the farmer's block reward to itself as a fee by setting `farmer_reward_address_override` in `NewProofOfSpace` and `RespondSignatures`. The intended enforcement is a fee quality check: the harvester must prove its proof meets a declared threshold.

**Step 1 — Fee check is only a log warning, never enforced.**

In `FarmerAPI.new_proof_of_space()`, when `NewProofOfSpace.farmer_reward_address_override` is set, the farmer calls `notify_farmer_reward_taken_by_harvester_as_fee()`: [1](#0-0) 

That function only emits log warnings when the fee threshold is invalid or missing — it never raises an exception, never returns a blocking value, and never prevents the block creation flow from continuing: [2](#0-1) 

**Step 2 — `RespondSignatures.farmer_reward_address_override` is accepted unconditionally.**

In `_process_respond_signatures()`, the farmer uses `response.farmer_reward_address_override` directly as the `farmer_reward_address` passed into `DeclareProofOfSpace` with zero fee quality check: [3](#0-2) 

The `RespondSignatures` protocol message carries its own independent `farmer_reward_address_override` field: [4](#0-3) 

A harvester can send `NewProofOfSpace` with `farmer_reward_address_override=None` (bypassing even the log-only check), receive `RequestSignatures`, then respond with `RespondSignatures` carrying `farmer_reward_address_override=<attacker_address>`. The farmer will use the attacker's address as `farmer_reward_address` in `DeclareProofOfSpace` with no check whatsoever.

Alternatively, even if the harvester sets the override in `NewProofOfSpace` with an invalid fee threshold, the farmer logs a warning and proceeds identically — the override still takes effect.

The resulting `DeclareProofOfSpace` carries the attacker's `farmer_reward_address`: [5](#0-4) 

This is then used by the full node in `create_foliage()` to set `farmer_reward_puzzlehash` in `FoliageBlockData`, which determines where the 1/8 farmer block reward coin is created on-chain: [6](#0-5) 

---

### Impact Explanation

A malicious third-party harvester (an unprivileged network peer connected to the farmer over the harvester protocol) can redirect the farmer's block reward — currently 0.25 XCH per block at current halving — to any arbitrary address on every block the farmer wins. This is unauthorized reward diversion affecting XCH, matching the Critical/High impact scope. The farmer has no recourse: the signed `FoliageBlockData` commits to the attacker's puzzle hash, and the block is valid on-chain.

---

### Likelihood Explanation

Any operator using a third-party harvester service (DrPlotter and similar services are explicitly supported by CHIP-22) is exposed. The attacker only needs to be a connected harvester peer — no keys, no admin access, no cryptographic break required. The attacker controls the `RespondSignatures` message content entirely.

---

### Recommendation

The fee quality check must be **enforced**, not merely logged. Specifically:

1. In `_process_respond_signatures()`, before accepting `response.farmer_reward_address_override`, independently compute `calculate_harvester_fee_quality(pospace.proof, response.challenge_hash)` and verify it is `<=` the `applied_fee_threshold` reported in the corresponding `NewProofOfSpace.fee_info`. If the check fails, reject the override and use `self.farmer.farmer_target` instead (or drop the block attempt).

2. Require that if `RespondSignatures.farmer_reward_address_override` is set, the corresponding `NewProofOfSpace` must also have had `farmer_reward_address_override` set with a valid `fee_info`, and the addresses must match. A harvester that sets the override only in `RespondSignatures` (not in `NewProofOfSpace`) should be rejected.

3. Consider making `notify_farmer_reward_taken_by_harvester_as_fee()` return a boolean and having `new_proof_of_space()` abort the block flow if the fee quality check fails.

---

### Proof of Concept

1. Attacker operates a harvester connected to a victim farmer.
2. Harvester finds a valid proof of space and sends `NewProofOfSpace` with `farmer_reward_address_override=None, fee_info=None` (standard message, no fee check triggered).
3. Farmer sends `RequestSignatures` back to the harvester.
4. Harvester responds with `RespondSignatures` where `farmer_reward_address_override=<attacker_puzzle_hash>`.
5. `_process_respond_signatures()` at line 917–918 sets `farmer_reward_address = attacker_puzzle_hash` with no validation.
6. `DeclareProofOfSpace` is sent to the full node with `farmer_reward_address=attacker_puzzle_hash`.
7. The full node calls `create_foliage(..., farmer_reward_puzzlehash=attacker_puzzle_hash, ...)` and creates a valid block. The farmer reward coin (e.g., 0.25 XCH) is created at the attacker's address.
8. The farmer receives no block reward for the block they won.

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

**File:** chia/consensus/block_creation.py (L117-128)
```python
    foliage_data = FoliageBlockData(
        reward_block_unfinished.get_hash(),
        pool_target,
        pool_target_signature,
        farmer_reward_puzzlehash,
        extension_data,
    )

    foliage_block_data_signature: G2Element = get_plot_signature(
        foliage_data.get_hash(),
        reward_block_unfinished.proof_of_space.plot_public_key,
    )
```
