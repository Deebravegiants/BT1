### Title
Harvester Can Unconditionally Redirect Farmer Block Rewards via Unvalidated `farmer_reward_address_override` in `RespondSignatures` - (File: chia/farmer/farmer_api.py)

### Summary
A malicious third-party harvester (an unprivileged peer) can redirect the farmer's XCH block reward to an arbitrary puzzle hash by setting `farmer_reward_address_override` in the `RespondSignatures` protocol message. The farmer accepts this field unconditionally with no fee-quality enforcement, and the only advisory check that exists is bypassed entirely when the override is placed in `RespondSignatures` rather than `NewProofOfSpace`.

### Finding Description

**Background — CHIP-22 fee convention**

CHIP-22 introduced `farmer_reward_address_override` as an optional field in both `NewProofOfSpace` and `RespondSignatures`. When set, the farmer is supposed to redirect its block reward to the harvester's address as a fee, but only if a probabilistic "fee quality" threshold is met. The check is implemented in `notify_farmer_reward_taken_by_harvester_as_fee()`.

**Root cause 1 — fee quality check is advisory-only**

In `FarmerAPI.new_proof_of_space()`, when `NewProofOfSpace.farmer_reward_address_override` is non-`None`, the farmer calls `notify_farmer_reward_taken_by_harvester_as_fee()`: [1](#0-0) 

Inside that function, when the fee quality check fails (threshold not met, or `fee_info` is `None`), the farmer only emits a `log.warning()` — it never returns early, raises, or discards the override: [2](#0-1) 

The override is then applied regardless of whether the check passed or failed.

**Root cause 2 — `RespondSignatures.farmer_reward_address_override` is accepted with zero validation**

In `_process_respond_signatures()`, the farmer unconditionally replaces `farmer_reward_address` with whatever the harvester placed in `RespondSignatures.farmer_reward_address_override`: [3](#0-2) 

No fee quality check is performed at this point. The `notify_farmer_reward_taken_by_harvester_as_fee()` call only happens in `new_proof_of_space()` when processing `NewProofOfSpace`, not here.

**Attack path (bypassing even the advisory check)**

1. Harvester sends `NewProofOfSpace` with `farmer_reward_address_override=None` → `notify_farmer_reward_taken_by_harvester_as_fee()` is never called; no check of any kind is triggered.
2. Farmer sends `RequestSignatures` to the harvester.
3. Harvester responds with `RespondSignatures` where `farmer_reward_address_override = <attacker_puzzle_hash>`.
4. `_process_respond_signatures()` sets `farmer_reward_address = attacker_puzzle_hash` with no validation.
5. The farmer broadcasts `DeclareProofOfSpace` with `farmer_puzzle_hash = attacker_puzzle_hash`. [4](#0-3) 

6. The full node receives `DeclareProofOfSpace`, reads `farmer_ph = request.farmer_puzzle_hash`, and creates the unfinished block with the attacker's address as the farmer reward destination: [5](#0-4) 

7. The farmer's XCH block reward is paid to the attacker.

The `RespondSignatures` protocol message is defined as: [6](#0-5) 

`farmer_reward_address_override` is a plain `bytes32 | None` field with no cryptographic binding to the proof-of-space signatures in `message_signatures`. The harvester can set it to any value after signing the challenge/reward chain hashes.

### Impact Explanation

**High — Unauthorized reward diversion affecting XCH.**

Any harvester connected to the farmer can redirect the farmer's block reward (currently 0.25 XCH per block) to an arbitrary address on every block the harvester's plots win. The farmer has no on-chain or protocol-level recourse once the `DeclareProofOfSpace` is broadcast with the attacker's puzzle hash embedded in the foliage.

### Likelihood Explanation

**High.** The attacker only needs to be a connected harvester — a standard, unprivileged role in the Chia farming architecture. No keys, admin access, or cryptographic breaks are required. The attack is silent (the farmer logs nothing when the override arrives via `RespondSignatures` with `NewProofOfSpace.farmer_reward_address_override=None`).

### Recommendation

The farmer must enforce the fee quality check and **reject** the override when the check fails, rather than merely logging. Specifically:

1. In `notify_farmer_reward_taken_by_harvester_as_fee()`, return a boolean indicating whether the override is legitimate, and have `new_proof_of_space()` drop the proof if it returns `False`.
2. In `_process_respond_signatures()`, perform the same fee quality check against the cached proof before accepting `response.farmer_reward_address_override`, and return `None` (dropping the block) if the check fails.
3. Ensure the `farmer_reward_address_override` value in `RespondSignatures` matches the value that was declared in the corresponding `NewProofOfSpace` (cross-reference via `sp_hash`/`plot_identifier`), so a harvester cannot introduce an override at the `RespondSignatures` stage that was absent at the `NewProofOfSpace` stage.

### Proof of Concept

```python
# Malicious harvester intercepts the RequestSignatures call and injects override
async def malicious_respond_signatures(request: RequestSignatures) -> RespondSignatures:
    # Sign the challenge/reward chain hashes legitimately
    legitimate_response = await real_request_signatures(request)
    # Inject attacker's puzzle hash — no fee quality check will be triggered
    # because NewProofOfSpace was sent with farmer_reward_address_override=None
    return dataclasses.replace(
        legitimate_response,
        farmer_reward_address_override=ATTACKER_PUZZLE_HASH,
    )
# Result: farmer broadcasts DeclareProofOfSpace with farmer_puzzle_hash=ATTACKER_PUZZLE_HASH
# Full node creates block paying 0.25 XCH to attacker
``` [7](#0-6)

### Citations

**File:** chia/farmer/farmer_api.py (L128-129)
```python
                if new_proof_of_space.farmer_reward_address_override is not None:
                    self.farmer.notify_farmer_reward_taken_by_harvester_as_fee(sp, new_proof_of_space)
```

**File:** chia/farmer/farmer_api.py (L602-614)
```python
    @metadata.request()
    async def respond_signatures(self, response: harvester_protocol.RespondSignatures) -> None:
        request = self._process_respond_signatures(response)
        if request is None:
            return None

        message: Message | None = None
        if isinstance(request, DeclareProofOfSpace):
            self.farmer.state_changed("proof", {"proof": request, "passed_filter": True})
            message = make_msg(ProtocolMessageTypes.declare_proof_of_space, request)
        if isinstance(request, SignedValues):
            message = make_msg(ProtocolMessageTypes.signed_values, request)
        await self.farmer.server.send_to_all([message], NodeType.FULL_NODE)
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

**File:** chia/full_node/full_node_api.py (L1069-1074)
```python
                farmer_ph = request.farmer_puzzle_hash
                if request.proof_of_space.pool_contract_puzzle_hash is not None:
                    pool_target = PoolTarget(request.proof_of_space.pool_contract_puzzle_hash, uint32(0))
                else:
                    assert request.pool_target is not None
                    pool_target = request.pool_target
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
