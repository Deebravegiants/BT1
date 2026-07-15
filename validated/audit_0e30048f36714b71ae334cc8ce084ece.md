### Title
Harvester Can Unconditionally Redirect Farmer Block Reward via Unenforced `farmer_reward_address_override` — (`File: chia/farmer/farmer_api.py`)

### Summary
A connected harvester (including a third-party harvester as contemplated by CHIP-22) can redirect the farmer's block reward (0.25 XCH per block) to any arbitrary puzzle hash by setting `farmer_reward_address_override` in its `RespondSignatures` message. The fee-quality threshold that is supposed to gate this override is only advisory — it produces a log warning but does not block the redirect. A harvester can also bypass even the advisory log by omitting the override from `NewProofOfSpace` and injecting it only in `RespondSignatures`.

### Finding Description

The Chia farmer–harvester protocol (CHIP-22) allows a third-party harvester to redirect the farmer reward to itself as a fee by setting `farmer_reward_address_override` in two protocol messages:

1. `harvester_protocol.NewProofOfSpace.farmer_reward_address_override` — sent by the harvester when it reports a winning proof.
2. `harvester_protocol.RespondSignatures.farmer_reward_address_override` — sent by the harvester in response to the farmer's `RequestSignatures`.

**Step 1 — Advisory-only threshold check in `new_proof_of_space`:**

When the harvester sends `NewProofOfSpace` with a non-`None` `farmer_reward_address_override`, the farmer calls `notify_farmer_reward_taken_by_harvester_as_fee`, which computes a fee quality and compares it to the harvester-supplied threshold. If the threshold is invalid, the function only logs a warning and returns — it does **not** reject the proof or prevent the override from being applied later. [1](#0-0) [2](#0-1) 

**Step 2 — Unconditional override application in `_process_respond_signatures`:**

When the harvester's `RespondSignatures` arrives, `_process_respond_signatures` unconditionally replaces the farmer's configured reward address with whatever the harvester supplied:

```python
farmer_reward_address = self.farmer.farmer_target
if response.farmer_reward_address_override is not None:
    farmer_reward_address = response.farmer_reward_address_override
    include_source_signature_data = True
``` [3](#0-2) 

There is no check that the fee quality threshold was met, no check that the override in `RespondSignatures` matches what was declared in `NewProofOfSpace`, and no rejection path.

**Step 3 — Redirected address flows into the block:**

The `farmer_reward_address` is placed into `DeclareProofOfSpace.farmer_puzzle_hash`: [4](#0-3) 

The full node then uses `request.farmer_puzzle_hash` directly when constructing the unfinished block: [5](#0-4) 

**Bypass path — omit override from `NewProofOfSpace`:**

A harvester can avoid even the advisory log by sending `NewProofOfSpace` with `farmer_reward_address_override=None` (no log triggered), then injecting the override only in `RespondSignatures`. The farmer has no memory of what was declared in `NewProofOfSpace` when it processes `RespondSignatures`. [6](#0-5) 

### Impact Explanation

Every block the farmer wins while connected to a malicious harvester results in the 0.25 XCH farmer reward being sent to the harvester's chosen address instead of the farmer's configured address. This is a direct, permanent, per-block theft of XCH. The farmer has no on-chain recourse once the block is confirmed. This constitutes unauthorized payout redirection of XCH, matching the Critical/High impact scope.

### Likelihood Explanation

Any harvester that is connected to the farmer can exploit this. Third-party harvesters (the explicit target of CHIP-22) are an expected deployment scenario. The attacker needs only a valid proof of space for the current signage point — a normal operational requirement — and then sets `farmer_reward_address_override` in `RespondSignatures`. No key material, admin access, or cryptographic break is required.

### Recommendation

In `_process_respond_signatures`, before applying `response.farmer_reward_address_override`, the farmer should:

1. Verify that the corresponding `NewProofOfSpace` message also declared a non-`None` `farmer_reward_address_override` (i.e., the harvester declared its intent upfront).
2. Verify that the fee quality computed from the proof satisfies the harvester-supplied threshold (`fee_quality <= fee_threshold`).
3. **Reject** (return `None`) rather than merely log when the threshold is not met or when the override appears only in `RespondSignatures` without a matching declaration in `NewProofOfSpace`.

### Proof of Concept

1. Malicious harvester connects to farmer.
2. Harvester receives a `NewSignagePointHarvester` and finds a winning proof.
3. Harvester sends `NewProofOfSpace` with `farmer_reward_address_override=None` and `fee_info=None` — no log is triggered.
4. Farmer sends `RequestSignatures` back to the harvester.
5. Harvester sends `RespondSignatures` with `farmer_reward_address_override=<attacker_puzzle_hash>`.
6. Farmer's `_process_respond_signatures` sets `farmer_reward_address = attacker_puzzle_hash` with no validation.
7. Farmer sends `DeclareProofOfSpace` with `farmer_puzzle_hash=attacker_puzzle_hash` to the full node.
8. Full node constructs and propagates an unfinished block paying the farmer reward to `attacker_puzzle_hash`.
9. The 0.25 XCH farmer reward is permanently redirected to the attacker. [7](#0-6) [8](#0-7) [9](#0-8)

### Citations

**File:** chia/farmer/farmer_api.py (L71-114)
```python
    @metadata.request(peer_required=True)
    async def new_proof_of_space(
        self, new_proof_of_space: harvester_protocol.NewProofOfSpace, peer: WSChiaConnection
    ) -> None:
        """
        This is a response from the harvester, for a NewSignagePointHarvester.
        Here we check if the proof of space is sufficiently good, and if so, we
        ask for the whole proof.
        """
        if new_proof_of_space.sp_hash not in self.farmer.number_of_responses:
            self.farmer.number_of_responses[new_proof_of_space.sp_hash] = 0
            self.farmer.cache_add_time[new_proof_of_space.sp_hash] = uint64(time.time())

        max_pos_per_sp = 5

        if self.farmer.config.get("selected_network") != "mainnet":
            # This is meant to make testnets more stable, when difficulty is very low
            if self.farmer.number_of_responses[new_proof_of_space.sp_hash] > max_pos_per_sp:
                self.farmer.log.info(
                    f"Surpassed {max_pos_per_sp} PoSpace for one SP, no longer submitting PoSpace for signage point "
                    f"{new_proof_of_space.sp_hash}"
                )
                return None

        if new_proof_of_space.sp_hash not in self.farmer.sps:
            self.farmer.log.warning(
                f"Received response for a signage point that we do not have {new_proof_of_space.sp_hash}"
            )
            return None

        sps = self.farmer.sps[new_proof_of_space.sp_hash]
        for sp in sps:
            computed_quality_string = verify_and_get_quality_string(
                new_proof_of_space.proof,
                self.farmer.constants,
                new_proof_of_space.challenge_hash,
                new_proof_of_space.sp_hash,
                height=sp.peak_height,
                prev_transaction_block_height=sp.last_tx_height,
            )
            if computed_quality_string is None:
                plotid: bytes32 = new_proof_of_space.proof.compute_plot_id()
                self.farmer.log.error(f"Invalid proof of space: {plotid.hex()} proof: {new_proof_of_space.proof}")
                return None
```

**File:** chia/farmer/farmer_api.py (L128-129)
```python
                if new_proof_of_space.farmer_reward_address_override is not None:
                    self.farmer.notify_farmer_reward_taken_by_harvester_as_fee(sp, new_proof_of_space)
```

**File:** chia/farmer/farmer_api.py (L914-933)
```python
                    include_source_signature_data = response.include_source_signature_data

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

**File:** chia/full_node/full_node_api.py (L1062-1075)
```python
            if prev_b is None:
                pool_target = PoolTarget(
                    self.full_node.constants.GENESIS_PRE_FARM_POOL_PUZZLE_HASH,
                    uint32(0),
                )
                farmer_ph = self.full_node.constants.GENESIS_PRE_FARM_FARMER_PUZZLE_HASH
            else:
                farmer_ph = request.farmer_puzzle_hash
                if request.proof_of_space.pool_contract_puzzle_hash is not None:
                    pool_target = PoolTarget(request.proof_of_space.pool_contract_puzzle_hash, uint32(0))
                else:
                    assert request.pool_target is not None
                    pool_target = request.pool_target

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
