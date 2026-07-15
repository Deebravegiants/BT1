Let me look at the full node's `signed_values` handler and the connection authentication to complete the analysis.

The vulnerability is real. Let me trace the complete code path to confirm.

**Key finding**: `request_signed_values` performs no validation on the foliage hashes — it only checks that the `quality_string` exists in `quality_str_to_identifiers`, then blindly forwards attacker-supplied hashes to the harvester for signing.

---

### Title
Farmer Signs Attacker-Controlled Foliage Hashes from Malicious Full Node, Enabling Farmer Reward Diversion — (`chia/farmer/farmer_api.py`)

### Summary
A malicious full node can send a `RequestSignedValues` message containing arbitrary `foliage_block_data_hash` and `foliage_transaction_block_hash` values. The farmer forwards these hashes verbatim to the harvester for signing, then co-signs them with its own farmer key, returning a `SignedValues` with valid BLS signatures over attacker-controlled data. The attacker can use these signatures to submit a block with a fraudulent `FoliageBlockData` (e.g., a different `farmer_reward_puzzle_hash`), diverting the 0.25 XCH farmer reward.

### Finding Description

`request_signed_values` in `farmer_api.py` only checks that the `quality_string` is present in `quality_str_to_identifiers`: [1](#0-0) 

It then constructs a `RequestSignatures` using the full node's supplied hashes verbatim, with no validation: [2](#0-1) 

`_process_respond_signatures` then signs whatever hashes the harvester echoes back — the farmer key signs `foliage_block_data_hash` and `foliage_transaction_block_hash` directly: [3](#0-2) 

There is no check that:
- `foliage_block_data_hash` equals `foliage_block_data.get_hash()` (even when `foliage_block_data` is provided)
- The `farmer_reward_puzzle_hash` inside `foliage_block_data` matches the farmer's configured reward address
- The hashes correspond to any block the farmer previously committed to via `DeclareProofOfSpace`

The `foliage_block_data` field in `RequestSignedValues` is optional and can be `None`: [4](#0-3) 

Even when provided, the farmer only passes it as `message_data` to the harvester (for optional harvester-side verification) but never validates the hash consistency itself: [5](#0-4) 

### Impact Explanation

The attacker constructs a `FoliageBlockData` with their own `farmer_reward_puzzle_hash`, computes its hash, and sends that hash in `RequestSignedValues`. The farmer returns valid BLS signatures over this hash. The attacker then assembles an unfinished block with the fraudulent foliage and submits it to honest full nodes. Those nodes verify the signature against `candidate.foliage.foliage_block_data.get_hash()`: [6](#0-5) 

Since the attacker chose the hash to match their fraudulent foliage, the signature verifies correctly, and the block is accepted — diverting the 0.25 XCH farmer reward per won block.

### Likelihood Explanation

The farmer connects outbound to full nodes using the **public** Chia CA (not the private CA), since `NodeType.FARMER` is not in `authenticated_client_types`: [7](#0-6) 

Any node with a valid public Chia CA certificate can act as a full node. Farmers configured with a remote `full_node_peer` (e.g., connecting to a pool's full node, or any remote node) are directly exposed. The attacker only needs the farmer to have found one valid proof (populating `quality_str_to_identifiers`), which happens during normal farming.

### Recommendation

In `request_signed_values`, before forwarding hashes to the harvester:
1. Require `foliage_block_data` to be present (not `None`) and validate `foliage_block_data.get_hash() == foliage_block_data_hash`.
2. Validate that `foliage_block_data.farmer_reward_puzzle_hash` matches the farmer's configured `farmer_target`.
3. Optionally, store the expected foliage hashes when `DeclareProofOfSpace` is sent and reject any `RequestSignedValues` whose hashes don't match.

### Proof of Concept

```python
# Precondition: farmer has quality_string Q in quality_str_to_identifiers
# (achieved by normal farming: harvester finds a proof, farmer processes new_proof_of_space)

# Attacker constructs fraudulent foliage with their own reward address
fraudulent_foliage = FoliageBlockData(
    unfinished_reward_block_hash=<legitimate_hash>,
    pool_target=<legitimate_pool_target>,
    pool_signature=<legitimate_pool_sig>,
    farmer_reward_puzzle_hash=ATTACKER_PUZZLE_HASH,  # <-- redirected reward
    extension_data=bytes32.zeros,
)
attacker_hash = fraudulent_foliage.get_hash()

# Attacker sends RequestSignedValues with attacker-chosen hashes
msg = RequestSignedValues(
    quality_string=Q,                          # valid quality string
    foliage_block_data_hash=attacker_hash,     # hash of fraudulent foliage
    foliage_transaction_block_hash=bytes32(os.urandom(32)),
    foliage_block_data=None,                   # optional, omitted
)
# farmer_api.request_signed_values() returns SignedValues with valid
# BLS signatures over attacker_hash — no validation performed.

# Attacker assembles unfinished block with fraudulent_foliage + returned signatures
# and submits to honest full nodes. Signature verifies; block is accepted.
# Farmer reward goes to ATTACKER_PUZZLE_HASH.
```

### Citations

**File:** chia/farmer/farmer_api.py (L723-730)
```python
    async def request_signed_values(self, full_node_request: farmer_protocol.RequestSignedValues) -> Message | None:
        if full_node_request.quality_string not in self.farmer.quality_str_to_identifiers:
            self.farmer.log.error(f"Do not have quality string {full_node_request.quality_string}")
            return None

        (plot_identifier, challenge_hash, sp_hash, node_id) = self.farmer.quality_str_to_identifiers[
            full_node_request.quality_string
        ]
```

**File:** chia/farmer/farmer_api.py (L734-747)
```python
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
```

**File:** chia/farmer/farmer_api.py (L749-756)
```python
        request = harvester_protocol.RequestSignatures(
            plot_identifier,
            challenge_hash,
            sp_hash,
            [full_node_request.foliage_block_data_hash, full_node_request.foliage_transaction_block_hash],
            message_data=message_data,
            rc_block_unfinished=full_node_request.rc_block_unfinished,
        )
```

**File:** chia/farmer/farmer_api.py (L959-979)
```python
                    foliage_sig_farmer = AugSchemeMPL.sign(sk, foliage_block_data_hash, agg_pk)
                    foliage_transaction_block_sig_farmer = AugSchemeMPL.sign(sk, foliage_transaction_block_hash, agg_pk)

                    foliage_agg_sig = AugSchemeMPL.aggregate(
                        [foliage_sig_harvester, foliage_sig_farmer, foliage_sig_taproot]
                    )
                    foliage_block_agg_sig = AugSchemeMPL.aggregate(
                        [
                            foliage_transaction_block_sig_harvester,
                            foliage_transaction_block_sig_farmer,
                            foliage_transaction_block_sig_taproot,
                        ]
                    )
                    assert AugSchemeMPL.verify(agg_pk, foliage_block_data_hash, foliage_agg_sig)
                    assert AugSchemeMPL.verify(agg_pk, foliage_transaction_block_hash, foliage_block_agg_sig)

                    return farmer_protocol.SignedValues(
                        computed_quality_string,
                        foliage_agg_sig,
                        foliage_block_agg_sig,
                    )
```

**File:** chia/protocols/farmer_protocol.py (L80-87)
```python
class RequestSignedValues(Streamable):
    quality_string: bytes32
    foliage_block_data_hash: bytes32
    foliage_transaction_block_hash: bytes32
    foliage_block_data: FoliageBlockData | None = None
    foliage_transaction_block_data: FoliageTransactionBlock | None = None
    rc_block_unfinished: RewardChainBlockUnfinished | None = None

```

**File:** chia/full_node/full_node_api.py (L1242-1248)
```python
        if not AugSchemeMPL.verify(
            candidate.reward_chain_block.proof_of_space.plot_public_key,
            candidate.foliage.foliage_block_data.get_hash(),
            farmer_request.foliage_block_data_signature,
        ):
            self.log.warning("Signature not valid. There might be a collision in plots. Ignore this during tests.")
            return None
```

**File:** chia/server/server.py (L170-195)
```python
        authenticated_client_types = {NodeType.HARVESTER}
        authenticated_server_types = {
            NodeType.HARVESTER,
            NodeType.FARMER,
            NodeType.WALLET,
            NodeType.DATA_LAYER,
        }

        if local_type in authenticated_client_types:
            # Authenticated clients
            private_cert_path, private_key_path = private_ssl_paths(root_path, config)
            ssl_client_context = ssl_context_for_client(
                ca_cert=ca_private_crt_path,
                ca_key=ca_private_key_path,
                cert_path=private_cert_path,
                key_path=private_key_path,
            )
        else:
            # Public clients
            public_cert_path, public_key_path = public_ssl_paths(root_path, config)
            ssl_client_context = ssl_context_for_client(
                ca_cert=chia_ca_crt_path,
                ca_key=chia_ca_key_path,
                cert_path=public_cert_path,
                key_path=public_key_path,
            )
```
