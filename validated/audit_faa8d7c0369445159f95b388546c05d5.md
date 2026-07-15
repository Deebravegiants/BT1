### Title
Malicious Third-Party Harvester Can Unconditionally Redirect Farmer Block Rewards via Unenforced `farmer_reward_address_override` — (`chia/farmer/farmer_api.py`)

---

### Summary

A malicious third-party harvester (CHIP-22) can redirect the farmer's block reward (1/8 of block reward per block won) to any arbitrary puzzle hash by setting `farmer_reward_address_override` in its `RespondSignatures` message. The CHIP-22 fee quality convention is supposed to restrict how much a harvester can take, but the farmer enforces **nothing** — it only logs a warning and unconditionally uses the harvester-supplied address in `DeclareProofOfSpace`. There is no enforcement at all on the `RespondSignatures` path.

---

### Finding Description

**Vulnerability class**: Trusted-but-restricted party (harvester) bypasses a fee-quality convention to divert farmer block rewards — directly analogous to the external report's Method 2 (malicious price feed with no sanity check).

**Step 1 — Fee quality check is advisory only.**

In `farmer_api.py`, when `NewProofOfSpace` arrives with `farmer_reward_address_override` set, the farmer calls `notify_farmer_reward_taken_by_harvester_as_fee`: [1](#0-0) 

That function computes a fee quality score and compares it to the harvester-supplied threshold, but **only logs a warning** — it never rejects the override or aborts the block-making flow: [2](#0-1) 

**Step 2 — The actual reward address used in the block comes from `RespondSignatures`, with zero check.**

In `_process_respond_signatures`, the farmer unconditionally replaces `farmer_reward_address` with whatever the harvester supplies in `RespondSignatures.farmer_reward_address_override`: [3](#0-2) 

There is no fee quality check here. The `RespondSignatures` field is a separate message from `NewProofOfSpace`, so a malicious harvester can:

- Send `NewProofOfSpace` with `farmer_reward_address_override=None` (skipping the advisory check entirely), then send `RespondSignatures` with `farmer_reward_address_override=attacker_address`; **or**
- Send `NewProofOfSpace` with a plausible override (passing the advisory check), then send `RespondSignatures` with a completely different attacker address.

In both cases the farmer builds and submits `DeclareProofOfSpace` with the attacker's address: [4](#0-3) 

The `RespondSignatures` protocol message that carries the override: [5](#0-4) 

---

### Impact Explanation

**High — Unauthorized payout redirection of XCH.**

Every block the malicious harvester wins on behalf of the farmer, the farmer's 1/8 block reward (`calculate_base_farmer_reward`) is sent to the attacker's puzzle hash instead of the farmer's configured `farmer_target`. The farmer has no on-chain recourse; the coin is already created at the attacker's address. [6](#0-5) 

This matches the allowed High impact: *"Bypass of … authorization that enables … payout redirection … affecting XCH."*

---

### Likelihood Explanation

The attacker must operate a harvester that the farmer connects to. This is the explicit CHIP-22 third-party harvester model — farmers are expected to use external harvesters for competitive reasons. Once connected, the harvester can redirect **every** block reward it finds, with no per-block consent from the farmer and no on-chain enforcement of the fee quality convention.

---

### Recommendation

1. **Enforce the fee quality convention, not just log it.** In `_process_respond_signatures`, before accepting `farmer_reward_address_override`, verify that the fee quality passes the threshold. If it does not, fall back to `self.farmer.farmer_target` and log the violation.

2. **Cross-check `NewProofOfSpace` and `RespondSignatures` overrides.** If `NewProofOfSpace.farmer_reward_address_override` is `None` but `RespondSignatures.farmer_reward_address_override` is set, treat it as a protocol violation and reject the response.

3. **Allow farmers to configure a maximum fee rate** (e.g., max percentage of farmer reward) and enforce it before building `DeclareProofOfSpace`.

---

### Proof of Concept

1. Attacker deploys a harvester that accepts connections from farmers (standard CHIP-22 setup).
2. Farmer connects to the malicious harvester.
3. Harvester finds a valid proof of space for a signage point.
4. Harvester sends `NewProofOfSpace` with `farmer_reward_address_override=None` (no advisory check triggered).
5. Farmer sends `RequestSignatures` back to the harvester.
6. Harvester sends `RespondSignatures` with `farmer_reward_address_override=<attacker_puzzle_hash>`.
7. Farmer's `_process_respond_signatures` unconditionally sets `farmer_reward_address = attacker_puzzle_hash` with no check.
8. Farmer submits `DeclareProofOfSpace` to the full node; the farmer reward coin (1/8 of block reward) is created at the attacker's address.
9. The farmer's `farmer_target` receives nothing for that block.

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

**File:** chia/farmer/farmer.py (L915-934)
```python
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

**File:** chia/protocols/harvester_protocol.py (L131-140)
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

**File:** chia/consensus/block_rewards.py (L33-52)
```python
def calculate_base_farmer_reward(height: uint32) -> uint64:
    """
    Returns the base farmer reward at a certain block height.
    The base fee reward is 1/8 of total block reward

    Returns the coinbase reward at a certain block height. These halving events will not be hit at the exact times
    (3 years, etc), due to fluctuations in difficulty. They will likely come early, if the network space and VDF
    rates increase continuously.
    """
    if height == 0:
        return uint64((1 / 8) * 21000000 * _mojo_per_chia)
    elif height < 3 * _blocks_per_year:
        return uint64((1 / 8) * 2 * _mojo_per_chia)
    elif height < 6 * _blocks_per_year:
        return uint64((1 / 8) * 1 * _mojo_per_chia)
    elif height < 9 * _blocks_per_year:
        return uint64((1 / 8) * 0.5 * _mojo_per_chia)
    elif height < 12 * _blocks_per_year:
        return uint64((1 / 8) * 0.25 * _mojo_per_chia)
    else:
```
