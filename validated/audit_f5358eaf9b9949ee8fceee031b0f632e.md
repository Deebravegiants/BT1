Let me look at the exact code for the farmer's handling of `farmer_reward_address_override` to confirm the full flow.

### Title
Malicious Third-Party Harvester Can Unconditionally Redirect Farmer Block Rewards via Unenforced `farmer_reward_address_override` - (File: `chia/farmer/farmer_api.py`)

---

### Summary

The CHIP-22 fee convention allows a third-party harvester to redirect the farmer's block reward to itself as a fee, gated by a `fee_quality` threshold check. However, the farmer's implementation only **logs** when the threshold is violated — it never enforces rejection. A malicious harvester can unconditionally redirect the farmer's 1/8-block reward (base farmer reward) to any address on every block won, with zero cryptographic or protocol-level barrier.

---

### Finding Description

The CHIP-22 fee convention is implemented across two protocol messages:

**Step 1 — `NewProofOfSpace` (harvester → farmer):**
The harvester sets `farmer_reward_address_override` and optionally `fee_info.applied_fee_threshold`. The farmer calls `notify_farmer_reward_taken_by_harvester_as_fee`, which computes `fee_quality` independently and compares it to the harvester's self-reported `applied_fee_threshold`. [1](#0-0) 

Critically, this function is **void** — it only logs. Whether the threshold check passes or fails, execution continues identically. There is no returned boolean, no raised exception, and no flag set to block the subsequent override. [2](#0-1) 

**Step 2 — `RespondSignatures` (harvester → farmer):**
When the harvester returns its signatures, `_process_respond_signatures` unconditionally replaces the farmer's own reward address with whatever the harvester provides in `response.farmer_reward_address_override`: [3](#0-2) 

This override is then embedded directly into `DeclareProofOfSpace.farmer_reward_address`, which the full node uses to create the on-chain farmer reward coin: [4](#0-3) 

There is **no fee quality check at all** in `_process_respond_signatures`. The check in Step 1 is purely advisory logging.

The harvester-controlled fields that enable this: [5](#0-4) [6](#0-5) 

---

### Impact Explanation

**High — Unauthorized payout redirection of XCH.**

Every time the farmer wins a block, the base farmer reward (`calculate_base_farmer_reward(height)` = 0.25 XCH at current heights) is created as an on-chain coin at the puzzle hash specified in `DeclareProofOfSpace.farmer_reward_address`. A malicious harvester controls this field unconditionally. The redirection is permanent and on-chain — the farmer receives nothing for that block. [7](#0-6) 

---

### Likelihood Explanation

Third-party harvesters are a standard operational pattern (DrPlotter, GPU harvesters, remote plot farms). Any harvester that connects to a farmer's port can exploit this. The attacker needs no keys, no admin access, and no cryptographic capability beyond what a legitimate harvester already possesses. The attack is silent — the farmer logs "Fee threshold passed" when `applied_fee_threshold = 0xFFFFFFFF` (always ≥ any `fee_quality`), producing no anomalous output.

---

### Recommendation

`notify_farmer_reward_taken_by_harvester_as_fee` must return a boolean indicating whether the fee is legitimate, and `new_proof_of_space` must gate the `RequestSignatures` flow on that result. Additionally, `_process_respond_signatures` must independently re-validate the fee quality before accepting `farmer_reward_address_override`. Specifically:

1. Change `notify_farmer_reward_taken_by_harvester_as_fee` to return `bool`.
2. In `new_proof_of_space`, if the return is `False`, do not proceed to `RequestSignatures` (or proceed but clear the override intent).
3. In `_process_respond_signatures`, re-check fee quality before applying `farmer_reward_address_override`; if the check fails, use `self.farmer.farmer_target` instead.

---

### Proof of Concept

1. A malicious harvester connects to a farmer's harvester port.
2. It finds a valid proof of space for a winning challenge.
3. It sends `NewProofOfSpace` with:
   - `farmer_reward_address_override = attacker_puzzle_hash`
   - `fee_info.applied_fee_threshold = 0xFFFFFFFF` (guarantees `fee_quality <= fee_threshold` always)
4. The farmer calls `notify_farmer_reward_taken_by_harvester_as_fee`, which logs `"Fee threshold passed"` and returns `None`. Execution continues unconditionally. [8](#0-7) 
5. The farmer sends `RequestSignatures` to the harvester.
6. The harvester responds with `RespondSignatures` containing `farmer_reward_address_override = attacker_puzzle_hash`.
7. `_process_respond_signatures` sets `farmer_reward_address = attacker_puzzle_hash` with no further check. [9](#0-8) 
8. `DeclareProofOfSpace` is submitted to the full node with `farmer_reward_address = attacker_puzzle_hash`.
9. The full node creates the farmer reward coin at `attacker_puzzle_hash`. The farmer receives 0 XCH for the block.

### Citations

**File:** chia/farmer/farmer.py (L908-934)
```python
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
