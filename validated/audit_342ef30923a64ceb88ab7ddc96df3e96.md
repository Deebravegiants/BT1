### Title
Harvester Can Unconditionally Redirect Farmer Block Reward to Arbitrary Address Without Fee Quality Enforcement — (`chia/farmer/farmer_api.py`)

### Summary
The `FarmerAPI._process_respond_signatures()` function in `chia/farmer/farmer_api.py` unconditionally accepts the `farmer_reward_address_override` field from any connected harvester's `RespondSignatures` message and uses it as the block reward destination, with no enforcement of the CHIP-22 fee quality threshold. The only check is a log warning in `notify_farmer_reward_taken_by_harvester_as_fee()`, which does not block the override. Any harvester connected to a farmer can redirect 100% of the farmer's XCH block rewards to an arbitrary puzzle hash of the harvester's choosing.

### Finding Description

**Root cause:** In `_process_respond_signatures()`, lines 916–919 of `chia/farmer/farmer_api.py`:

```python
farmer_reward_address = self.farmer.farmer_target
if response.farmer_reward_address_override is not None:
    farmer_reward_address = response.farmer_reward_address_override
    include_source_signature_data = True
```

The `farmer_reward_address_override` field from the harvester's `RespondSignatures` message is accepted and used unconditionally. The resulting `farmer_reward_address` is then passed directly into `DeclareProofOfSpace` (line 929) and submitted to the full node, causing the block reward to be paid to the harvester-specified address.

**The only "check" is advisory:** When `new_proof_of_space.farmer_reward_address_override is not None` (line 128 of `farmer_api.py`), the farmer calls `notify_farmer_reward_taken_by_harvester_as_fee()`. This function (lines 888–934 of `farmer.py`) computes the fee quality and logs a warning if the threshold is not met or if `fee_info` is absent — but it **does not reject the override, does not return an error, and does not prevent the farmer from using the attacker-supplied address**.

**Protocol context:** CHIP-22 defines a convention where third-party harvesters may legitimately take a fee by redirecting the farmer reward, but only when `fee_quality <= applied_fee_threshold`. The farmer is the enforcement point for this rule. The current implementation treats the threshold as advisory only.

**Attack path:**
1. Attacker operates a harvester and connects it to a victim farmer (standard harvester connection, no privileged keys required beyond the TLS handshake for the harvester role).
2. When the harvester finds a valid proof of space, it sends `NewProofOfSpace` with `farmer_reward_address_override` set to the attacker's puzzle hash and optionally sets `fee_info` with an inflated `applied_fee_threshold` (or omits `fee_info` entirely).
3. The farmer calls `notify_farmer_reward_taken_by_harvester_as_fee()`, which logs a warning but does not block.
4. The farmer proceeds to build `DeclareProofOfSpace` with `farmer_reward_address = response.farmer_reward_address_override` (attacker's address).
5. The full node accepts the block and pays the farmer reward to the attacker's address. The legitimate farmer receives nothing.

### Impact Explanation

**High — Unauthorized payout redirection of XCH farmer block rewards.**

Any harvester connected to a farmer can redirect the farmer's block reward (currently 0.25 XCH per block for the farmer coin) to an arbitrary address. Since the check is purely a log warning with no enforcement, a malicious harvester can steal 100% of the farmer's block rewards for every block the harvester's plots win, with no cryptographic barrier. This directly matches the allowed High impact: "Bypass of … pool … authorization that enables … payout redirection."

### Likelihood Explanation

A harvester connecting to a farmer is a standard, unprivileged role in the Chia farming architecture. Third-party harvester software (e.g., DrPlotter and similar) is explicitly supported. A malicious third-party harvester operator needs only to connect to a farmer and set `farmer_reward_address_override` to their own address on every `RespondSignatures` response. The farmer has no mechanism to detect or prevent this beyond a log warning that most operators will never see.

### Recommendation

In `_process_respond_signatures()`, before accepting `farmer_reward_address_override`, enforce the CHIP-22 fee quality rule: reject (return `None`) if the override is set but `fee_info` is absent, or if `calculate_harvester_fee_quality(pospace.proof, sp.challenge_hash) > fee_info.applied_fee_threshold`. The existing `notify_farmer_reward_taken_by_harvester_as_fee()` logic already computes this — it should be converted from a logging function into an enforcement gate that returns a boolean, and `_process_respond_signatures()` should return `None` (dropping the block submission) when the threshold is not met.

### Proof of Concept

1. Implement a harvester that, on every `request_signatures` call, returns a valid `RespondSignatures` with `farmer_reward_address_override` set to the attacker's puzzle hash and `fee_info=None` (or `applied_fee_threshold=0xFFFFFFFF`).
2. Connect this harvester to a victim farmer.
3. When the harvester's plots win a block, observe that `DeclareProofOfSpace.farmer_reward_puzzle_hash` equals the attacker's address (confirmed by the test in `test_third_party_harvesters.py` lines 134–139, which demonstrates the farmer unconditionally respects the override).
4. The farmer reward coin is created at the attacker's puzzle hash; the legitimate farmer receives 0 XCH for that block.

**Key code references:** [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

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
