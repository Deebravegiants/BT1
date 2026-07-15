Let me look at the full node's `declare_proof_of_space` handler and how `quality_string` is broadcast to understand the full attack surface.

### Title
Farmer signs attacker-controlled foliage block data hash without hash-data consistency check — (`chia/farmer/farmer_api.py`)

### Summary

`FarmerAPI.request_signed_values` forwards `foliage_block_data_hash` from the full node's `RequestSignedValues` message directly to the harvester for signing without ever verifying that `foliage_block_data.get_hash() == foliage_block_data_hash`. A malicious full node that has a TLS connection to the farmer and knows a valid `quality_string` (obtained from the farmer's broadcast `DeclareProofOfSpace`) can supply an arbitrary `foliage_block_data_hash` — e.g., the hash of a foliage block whose `farmer_reward_puzzle_hash` points to the attacker — and obtain a valid plot-key signature over it, enabling farmer reward diversion.

---

### Finding Description

**Entry point — `FarmerAPI.request_signed_values`** [1](#0-0) 

The handler performs exactly one guard: it checks that `quality_string` is present in `quality_str_to_identifiers`. [2](#0-1) 

When `foliage_block_data` is non-`None`, the farmer packages the raw bytes as `message_data` (source data for CHIP-22 third-party harvesters) but then unconditionally uses the caller-supplied `foliage_block_data_hash` as the actual message to sign — with **no assertion that the two are consistent**: [3](#0-2) 

**Harvester signs blindly**

`HarvesterAPI.request_signatures` iterates over `request.messages` and signs each one with the local plot key. It never inspects `message_data` to verify that `data.get_hash() == message`: [4](#0-3) 

**Farmer co-signs blindly**

`_process_respond_signatures` takes `foliage_block_data_hash` straight from the harvester's echoed response and signs it with the farmer's private key: [5](#0-4) 

**The check exists only in a test interceptor, not in production**

The integration test for CHIP-22 (`test_third_party_harvesters.py`) wraps `request_signed_values` with an interceptor that asserts consistency — confirming the invariant is expected but absent from production code: [6](#0-5) 

**`quality_string` is broadcast to every connected full node**

When the farmer produces a `DeclareProofOfSpace`, it is sent to **all** connected full nodes, so any peer — including a malicious one — learns the `quality_string`: [7](#0-6) 

---

### Impact Explanation

A malicious full node can:

1. Connect to the farmer over TLS (normal peer relationship).
2. Receive `DeclareProofOfSpace` and extract `quality_string`.
3. Craft a `RequestSignedValues` where `foliage_block_data_hash = SHA256(evil_foliage)` and `foliage_block_data = any_legitimate_foliage` (or `None`), where `evil_foliage` contains the attacker's `farmer_reward_puzzle_hash`.
4. The farmer and harvester both sign `H(evil_foliage)` without complaint.
5. The attacker assembles a valid `UnfinishedBlock` containing `evil_foliage` and the obtained signature, which the rest of the network accepts because the BLS signature verifies against `evil_foliage.get_hash()`.

Result: the farmer's block reward is diverted to the attacker's address. This is a **High** impact: unauthorized payout redirection via unauthorized signing.

---

### Likelihood Explanation

- Requires only a standard TLS peer connection to the farmer — no key theft, no cryptographic break.
- The `quality_string` is passively obtained from the normal `DeclareProofOfSpace` broadcast.
- The farmer has no mechanism to authenticate which full node sent `RequestSignedValues` (`@metadata.request()` without `peer_required=True` means the peer identity is not even available inside the handler).
- Exploitable on every block the farmer wins while connected to the malicious peer.

---

### Recommendation

Inside `request_signed_values`, before constructing `RequestSignatures`, add:

```python
if full_node_request.foliage_block_data is not None:
    if full_node_request.foliage_block_data.get_hash() != full_node_request.foliage_block_data_hash:
        self.farmer.log.error("foliage_block_data hash mismatch — dropping request")
        return None
if full_node_request.foliage_transaction_block_data is not None:
    if full_node_request.foliage_transaction_block_data.get_hash() != full_node_request.foliage_transaction_block_hash:
        self.farmer.log.error("foliage_transaction_block_data hash mismatch — dropping request")
        return None
```

Additionally, consider making `request_signed_values` `peer_required=True` so the farmer can enforce that the request originates from the same full node that received the `DeclareProofOfSpace`.

---

### Proof of Concept

```python
# Pseudocode unit test
farmer_api.farmer.quality_str_to_identifiers[quality_string] = (
    "plot_1", challenge_hash, sp_hash, harvester_peer_id
)

evil_foliage = FoliageBlockData(..., farmer_reward_puzzle_hash=attacker_address, ...)
legitimate_foliage = FoliageBlockData(..., farmer_reward_puzzle_hash=farmer_address, ...)

request = RequestSignedValues(
    quality_string=quality_string,
    foliage_block_data_hash=evil_foliage.get_hash(),   # attacker's hash
    foliage_transaction_block_hash=bytes32.zeros,
    foliage_block_data=legitimate_foliage,              # mismatched data
)

result = await farmer_api.request_signed_values(request)

# Assert: farmer returned SignedValues (no error raised)
assert result is not None
assert ProtocolMessageTypes(result.type).name == "signed_values"

# The harvester was asked to sign evil_foliage.get_hash(), not legitimate_foliage.get_hash()
# Verify the forwarded RequestSignatures contained the evil hash
forwarded = harvester_incoming_queue.get_nowait()
req_sigs = harvester_protocol.RequestSignatures.from_bytes(forwarded.data)
assert req_sigs.messages[0] == evil_foliage.get_hash()   # passes — vulnerability confirmed
```

### Citations

**File:** chia/farmer/farmer_api.py (L609-614)
```python
        if isinstance(request, DeclareProofOfSpace):
            self.farmer.state_changed("proof", {"proof": request, "passed_filter": True})
            message = make_msg(ProtocolMessageTypes.declare_proof_of_space, request)
        if isinstance(request, SignedValues):
            message = make_msg(ProtocolMessageTypes.signed_values, request)
        await self.farmer.server.send_to_all([message], NodeType.FULL_NODE)
```

**File:** chia/farmer/farmer_api.py (L722-756)
```python
    @metadata.request()
    async def request_signed_values(self, full_node_request: farmer_protocol.RequestSignedValues) -> Message | None:
        if full_node_request.quality_string not in self.farmer.quality_str_to_identifiers:
            self.farmer.log.error(f"Do not have quality string {full_node_request.quality_string}")
            return None

        (plot_identifier, challenge_hash, sp_hash, node_id) = self.farmer.quality_str_to_identifiers[
            full_node_request.quality_string
        ]

        message_data: list[SignatureRequestSourceData | None] | None = None

        if full_node_request.foliage_block_data is not None:
            message_data = [
                SignatureRequestSourceData(
                    uint8(SigningDataKind.FOLIAGE_BLOCK_DATA), bytes(full_node_request.foliage_block_data)
                ),
                (
                    None
                    if full_node_request.foliage_transaction_block_data is None
                    else SignatureRequestSourceData(
                        uint8(SigningDataKind.FOLIAGE_TRANSACTION_BLOCK),
                        bytes(full_node_request.foliage_transaction_block_data),
                    )
                ),
            ]

        request = harvester_protocol.RequestSignatures(
            plot_identifier,
            challenge_hash,
            sp_hash,
            [full_node_request.foliage_block_data_hash, full_node_request.foliage_transaction_block_hash],
            message_data=message_data,
            rc_block_unfinished=full_node_request.rc_block_unfinished,
        )
```

**File:** chia/farmer/farmer_api.py (L938-959)
```python
                    foliage_block_data_hash,
                    foliage_sig_harvester,
                ) = response.message_signatures[0]
                (
                    foliage_transaction_block_hash,
                    foliage_transaction_block_sig_harvester,
                ) = response.message_signatures[1]
                pk = sk.get_g1()
                if pk == response.farmer_pk:
                    agg_pk = generate_plot_public_key(response.local_pk, pk, include_taproot)
                    assert agg_pk == pospace.plot_public_key
                    if include_taproot:
                        taproot_sk = generate_taproot_sk(response.local_pk, pk)
                        foliage_sig_taproot: G2Element = AugSchemeMPL.sign(taproot_sk, foliage_block_data_hash, agg_pk)
                        foliage_transaction_block_sig_taproot: G2Element = AugSchemeMPL.sign(
                            taproot_sk, foliage_transaction_block_hash, agg_pk
                        )
                    else:
                        foliage_sig_taproot = G2Element()
                        foliage_transaction_block_sig_taproot = G2Element()

                    foliage_sig_farmer = AugSchemeMPL.sign(sk, foliage_block_data_hash, agg_pk)
```

**File:** chia/harvester/harvester_api.py (L510-513)
```python
        message_signatures: list[tuple[bytes32, G2Element]] = []
        for message in request.messages:
            signature: G2Element = AugSchemeMPL.sign(local_sk, message, agg_pk)
            message_signatures.append((message, signature))
```

**File:** chia/_tests/farmer_harvester/test_third_party_harvesters.py (L234-246)
```python
        # Ensure the FullNode included the source data for the signatures
        assert request.foliage_block_data
        assert request.foliage_block_data.get_hash() == request.foliage_block_data_hash
        assert request.foliage_transaction_block_data
        assert request.foliage_transaction_block_data.get_hash() == request.foliage_transaction_block_hash

        assert (
            request.foliage_block_data.farmer_reward_puzzle_hash == farmer_reward_address
            or request.foliage_block_data.farmer_reward_puzzle_hash
            == bytes32(full_node_2.constants.GENESIS_PRE_FARM_FARMER_PUZZLE_HASH)
        )

        return await FarmerAPI.request_signed_values(farmer.server.api, request)
```
