### Title
Malicious Harvester Can Redirect Farmer Block Reward via Unvalidated `farmer_reward_address_override` in `RespondSignatures` — (`chia/farmer/farmer_api.py`)

### Summary

A harvester peer with a valid TLS connection can set `farmer_reward_address_override` to an arbitrary `bytes32` puzzle hash in a `RespondSignatures` message. The farmer's `_process_respond_signatures` accepts this value without any validation and uses it as `farmer_puzzle_hash` in `DeclareProofOfSpace`, which the full node then uses verbatim as the farmer reward address in the block. The farmer's configured `farmer_target` address is completely bypassed.

---

### Finding Description

**Step 1 — Protocol message structure**

`RespondSignatures` (the harvester→farmer signature response) carries an optional `farmer_reward_address_override` field: [1](#0-0) 

**Step 2 — Unvalidated override in `_process_respond_signatures`**

When the farmer processes a `RespondSignatures` message, it unconditionally replaces its own configured `farmer_target` with whatever the harvester supplied: [2](#0-1) 

There is no check that `response.farmer_reward_address_override` equals `self.farmer.farmer_target`, no allowlist, no signature over the override value, and no rate-limit or consent gate. Any non-`None` value from the harvester wins.

**Step 3 — Attacker-controlled address flows into `DeclareProofOfSpace`**

The tainted `farmer_reward_address` is placed directly into `DeclareProofOfSpace.farmer_puzzle_hash`: [3](#0-2) 

**Step 4 — Full node uses `farmer_puzzle_hash` verbatim**

`FullNodeAPI.declare_proof_of_space` reads `request.farmer_puzzle_hash` without any independent validation against a known farmer address: [4](#0-3) 

The full node then builds `FoliageBlockData` with `farmer_reward_puzzle_hash = attacker_ph`, which becomes the coinbase reward destination in the finished block.

**Step 5 — `notify_farmer_reward_taken_by_harvester_as_fee` is log-only**

The only "guard" is a log call triggered by `NewProofOfSpace.farmer_reward_address_override`, not by `RespondSignatures.farmer_reward_address_override`. A harvester can send `NewProofOfSpace` with `farmer_reward_address_override=None` (avoiding even the log) and then set the override only in `RespondSignatures`. The two fields are never cross-checked. [5](#0-4) 

---

### Impact Explanation

A malicious harvester with a valid TLS connection (including a legitimate third-party CHIP-22 harvester) can redirect **100% of the farmer's block reward** to an attacker-controlled puzzle hash on every block the farmer wins. The farmer receives nothing. This is an unauthorized payout redirection of XCH block rewards — a High-severity impact under the defined scope.

---

### Likelihood Explanation

Any harvester peer that can complete the TLS handshake can exploit this. Third-party harvesters (CHIP-22) are an explicitly supported use case, making the attacker surface real and non-hypothetical. No key material needs to be stolen; the harvester simply sets a field in a protocol message it already controls.

---

### Recommendation

In `_process_respond_signatures`, reject any `RespondSignatures` where `farmer_reward_address_override` differs from `self.farmer.farmer_target` unless the farmer has explicitly configured an allowlist of harvesters permitted to override the reward address, and the override address is within a farmer-configured acceptable range (e.g., a known fee address). At minimum, add a hard rejection:

```python
if response.farmer_reward_address_override is not None:
    if response.farmer_reward_address_override != self.farmer.farmer_target:
        self.farmer.log.error(
            "Harvester attempted to override farmer reward address. Rejecting."
        )
        return None
```

---

### Proof of Concept

```python
# Mock harvester sends NewProofOfSpace with farmer_reward_address_override=None
# (no log warning triggered), then responds to RequestSignatures with:
attacker_ph = bytes32(b"\xab" * 32)
respond_sig = RespondSignatures(
    plot_identifier=...,
    challenge_hash=...,
    sp_hash=...,
    local_pk=...,
    farmer_pk=...,
    message_signatures=[valid_cc_sp_sig, valid_rc_sp_sig],
    include_source_signature_data=False,
    farmer_reward_address_override=attacker_ph,   # <-- injected
)
# _process_respond_signatures returns DeclareProofOfSpace with
# farmer_puzzle_hash == attacker_ph, not farmer.farmer_target
declare = farmer_api._process_respond_signatures(respond_sig)
assert declare.farmer_puzzle_hash == attacker_ph  # passes
```

The resulting `DeclareProofOfSpace` is broadcast to the full node, which builds a block paying the farmer reward to `attacker_ph`.

### Citations

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

**File:** chia/full_node/full_node_api.py (L1068-1069)
```python
            else:
                farmer_ph = request.farmer_puzzle_hash
```
