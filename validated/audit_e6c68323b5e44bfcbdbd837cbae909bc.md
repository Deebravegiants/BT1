The code path is concrete and traceable. Let me lay out the full analysis.

---

### Title
Malicious Harvester Can Redirect Farmer Block Rewards via Unvalidated `farmer_reward_address_override` in `RespondSignatures` — (`chia/farmer/farmer_api.py`)

---

### Summary

A malicious harvester peer can permanently redirect the farmer's block reward to an attacker-controlled puzzle hash by setting `farmer_reward_address_override` in a `RespondSignatures` message. The farmer's `_process_respond_signatures` function accepts this field from the harvester without any validation against the farmer's configured `farmer_target`.

---

### Finding Description

**Step 1 — `RespondSignatures` carries an attacker-controlled field**

`RespondSignatures` (the harvester's reply to `RequestSignatures`) contains a `farmer_reward_address_override: bytes32 | None` field that is fully controlled by the harvester: [1](#0-0) 

**Step 2 — The farmer uses this field without validation**

In `_process_respond_signatures`, the farmer unconditionally replaces its own configured `farmer_target` with whatever the harvester supplies: [2](#0-1) 

There is no check that `response.farmer_reward_address_override` equals `self.farmer.farmer_target`, is on an allowlist, or matches the value originally sent in `NewProofOfSpace`. The override is used verbatim as `farmer_reward_address` in `DeclareProofOfSpace`: [3](#0-2) 

**Step 3 — The `NewProofOfSpace` override is not stored for cross-check**

When `new_proof_of_space` receives a `farmer_reward_address_override`, it calls `notify_farmer_reward_taken_by_harvester_as_fee` (a notification/logging call) and then stores only the proof identifier and proof itself — not the override value: [4](#0-3) [5](#0-4) 

This means the harvester can send `NewProofOfSpace` with `farmer_reward_address_override=None` (avoiding any notification), and then inject an attacker address only in the subsequent `RespondSignatures`. The farmer has no stored value to compare against.

**Step 4 — `DeclareProofOfSpace` is broadcast to all full nodes**

`respond_signatures` broadcasts the result to all full nodes: [6](#0-5) 

The full node creates the reward coin at the puzzle hash specified in `DeclareProofOfSpace.farmer_reward_puzzle_hash`, making the diversion permanent and on-chain.

---

### Impact Explanation

A malicious harvester with a valid winning proof can cause the farmer's block reward (currently 0.125 XCH per block) to be created at an attacker-controlled address. The farmer receives nothing. This is an unauthorized reward diversion affecting XCH — a Critical/High impact per the scope rules.

---

### Likelihood Explanation

The attack requires:
1. A harvester peer with a valid proof that passes the block filter and quality threshold — a normal operational condition.
2. The ability to set `farmer_reward_address_override` in `RespondSignatures` — trivially achievable by any harvester implementation.

Third-party harvesters (CHIP-22) are an explicitly supported use case, making this attack surface realistic. The farmer has no defense: there is no signature over the override, no allowlist check, and no comparison against the farmer's own configured address.

---

### Recommendation

In `_process_respond_signatures`, validate `response.farmer_reward_address_override` before use:
- Reject it if it does not equal `self.farmer.farmer_target` (for standard harvesters), or
- Compare it against a farmer-configured allowlist of permitted override addresses with a maximum fee threshold, and reject if outside bounds.

Additionally, the override value from `NewProofOfSpace` should be stored alongside the proof in `proofs_of_space` and cross-checked against the value in `RespondSignatures` to prevent injection at the response stage.

---

### Proof of Concept

```python
# Malicious harvester implementation:
# 1. Receive RequestSignatures from farmer for a winning proof
# 2. Respond with RespondSignatures where farmer_reward_address_override = attacker_ph

attacker_ph = bytes32(b'\xde\xad' * 16)

respond = RespondSignatures(
    plot_identifier=...,
    challenge_hash=...,
    sp_hash=...,
    local_pk=...,
    farmer_pk=...,
    message_signatures=[...],  # valid signatures
    include_source_signature_data=True,
    farmer_reward_address_override=attacker_ph,  # injected here
)
# Farmer's _process_respond_signatures will set:
#   farmer_reward_address = attacker_ph
# and broadcast DeclareProofOfSpace with farmer_reward_puzzle_hash=attacker_ph
# Full node creates reward coin at attacker_ph — permanent on-chain diversion.
```

Assert: `DeclareProofOfSpace.farmer_reward_puzzle_hash == attacker_ph != farmer.farmer_target` — the invariant is violated.

### Citations

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

**File:** chia/farmer/farmer_api.py (L128-129)
```python
                if new_proof_of_space.farmer_reward_address_override is not None:
                    self.farmer.notify_farmer_reward_taken_by_harvester_as_fee(sp, new_proof_of_space)
```

**File:** chia/farmer/farmer_api.py (L170-177)
```python
                if new_proof_of_space.sp_hash not in self.farmer.proofs_of_space:
                    self.farmer.proofs_of_space[new_proof_of_space.sp_hash] = []
                self.farmer.proofs_of_space[new_proof_of_space.sp_hash].append(
                    (
                        new_proof_of_space.plot_identifier,
                        new_proof_of_space.proof,
                    )
                )
```

**File:** chia/farmer/farmer_api.py (L603-614)
```python
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
