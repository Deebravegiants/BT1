### Title
Malicious Third-Party Harvester Can Unconditionally Redirect Farmer Block Rewards via Unvalidated `farmer_reward_address_override` in `RespondSignatures` - (File: chia/farmer/farmer_api.py)

---

### Summary

The CHIP-22 third-party harvester protocol allows a connected harvester to supply a `farmer_reward_address_override` field in both `NewProofOfSpace` and `RespondSignatures` messages. The farmer's `_process_respond_signatures` method in `chia/farmer/farmer_api.py` accepts this override **unconditionally** — with no fee-quality enforcement, no address allowlist, and no cross-check against what was declared in `NewProofOfSpace`. A malicious harvester can redirect 100% of the farmer's XCH block reward to an arbitrary puzzle hash on every won block.

---

### Finding Description

CHIP-22 introduces a convention where third-party harvesters may take a fraction of the farmer's block reward as a fee, gated by a proof-quality threshold. The farmer is supposed to enforce this convention. In practice it does not.

**Step 1 — Fee check is warning-only and operates on `NewProofOfSpace`, not `RespondSignatures`.**

`notify_farmer_reward_taken_by_harvester_as_fee` is called in `new_proof_of_space` only when `new_proof_of_space.farmer_reward_address_override is not None`: [1](#0-0) 

The function computes fee quality and logs a warning if the threshold is violated, but **never returns an error, never sets a flag, and never prevents the signing flow from continuing**: [2](#0-1) 

**Step 2 — The actual reward address used in the block comes from `RespondSignatures`, not `NewProofOfSpace`.**

After the farmer sends `RequestSignatures` to the harvester, the harvester replies with `RespondSignatures`, which also carries `farmer_reward_address_override`: [3](#0-2) 

In `_process_respond_signatures`, the farmer replaces its own configured `farmer_target` with whatever the harvester supplies, with zero validation: [4](#0-3) 

This address is then placed directly into `DeclareProofOfSpace` and broadcast to the full node: [5](#0-4) 

**Step 3 — The two fields are never cross-checked.**

The farmer stores no record of what `farmer_reward_address_override` (if any) was declared in `NewProofOfSpace`. The harvester can send `NewProofOfSpace` with `farmer_reward_address_override=None` (so `notify_farmer_reward_taken_by_harvester_as_fee` is never even called), then inject an arbitrary override in `RespondSignatures`. The farmer has no mechanism to detect this discrepancy.

---

### Impact Explanation

**High — Unauthorized reward diversion affecting XCH.**

Every time the farmer wins a block using a plot served by the malicious harvester, the entire farmer reward (currently 0.25 XCH per block) is sent to the attacker's puzzle hash instead of the farmer's configured address. The full node performs no validation of the farmer reward puzzle hash for non-genesis blocks; it accepts whatever address is in `DeclareProofOfSpace`. The loss is permanent and per-block.

---

### Likelihood Explanation

CHIP-22 and the `test_third_party_harvesters.py` test suite explicitly model third-party harvesters as a supported, production use case: [6](#0-5) 

Any operator who runs a third-party harvester service that a farmer connects to can exploit this. The farmer–harvester connection is TLS-authenticated, but TLS only proves the harvester's identity — it does not constrain what puzzle hash the harvester may supply. A harvester operator who is legitimately trusted to serve plots is not trusted to redirect rewards, yet the code grants that power unconditionally.

---

### Recommendation

1. **Enforce the CHIP-22 fee convention with rejection, not just logging.** In `notify_farmer_reward_taken_by_harvester_as_fee`, return a boolean and abort the signing flow when fee quality fails.
2. **Cross-check `RespondSignatures.farmer_reward_address_override` against `NewProofOfSpace.farmer_reward_address_override`.** Store the override from `NewProofOfSpace` alongside the proof-of-space cache entry and reject any `RespondSignatures` that introduces a different (or newly non-`None`) override.
3. **Optionally, allow farmers to configure an allowlist of puzzle hashes** that harvesters are permitted to redirect rewards to, rejecting any override not on the list.

---

### Proof of Concept

```
Attacker setup:
  - Operate a third-party harvester that a victim farmer connects to.

Attack sequence:
  1. Harvester receives NewSignagePointHarvester from farmer.
  2. Harvester finds a winning proof of space.
  3. Harvester sends NewProofOfSpace to farmer with:
       farmer_reward_address_override = None   # no fee check triggered
       fee_info = None
  4. Farmer validates the proof, calls RequestSignatures back to harvester.
  5. Harvester responds with RespondSignatures containing:
       farmer_reward_address_override = attacker_puzzle_hash  # injected here
  6. Farmer executes _process_respond_signatures:
       farmer_reward_address = self.farmer.farmer_target       # line 916
       if response.farmer_reward_address_override is not None: # line 917 → True
           farmer_reward_address = response.farmer_reward_address_override  # line 918
  7. Farmer broadcasts DeclareProofOfSpace with farmer_reward_address = attacker_puzzle_hash.
  8. Full node accepts the block; farmer reward (XCH) is paid to attacker_puzzle_hash.
  9. Farmer's own address receives nothing for that block.
```

The farmer logs nothing unusual because `notify_farmer_reward_taken_by_harvester_as_fee` was never called (override was `None` in step 3). The attack is silent and repeatable on every block the harvester wins.

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

**File:** chia/_tests/farmer_harvester/test_third_party_harvesters.py (L59-74)
```python
@pytest.mark.anyio
async def test_harvester_receive_source_signing_data(
    farmer_harvester_2_simulators_zero_bits_plot_filter: tuple[
        FarmerService,
        HarvesterService,
        FullNodeService | SimulatorFullNodeService,
        FullNodeService | SimulatorFullNodeService,
        BlockTools,
    ],
) -> None:
    """
    Tests that the source data for the signatures requests sent to the
    harvester are indeed available and also tests that overrides of
    the farmer reward address, as specified by the harvester, are respected.
    See: CHIP-22: https://github.com/Chia-Network/chips/pull/88
    """
```
