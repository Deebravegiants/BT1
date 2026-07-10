### Title
Unverified `payload_hash`–to–`request` Binding in `respond_verify_foreign_tx` Allows a Single Byzantine Participant to Forge Foreign-Chain Verification Attestations - (File: `crates/contract/src/lib.rs`)

---

### Summary

`respond_verify_foreign_tx` verifies that the submitted `response.signature` is a valid ECDSA signature over `response.payload_hash` under the ForeignTx domain's root public key, but it **never verifies that `payload_hash` was actually derived from the submitted `request`**. A single Byzantine attested participant can recycle a legitimately-produced `(payload_hash, signature)` pair from one foreign-chain verification response and submit it as the answer to a completely different pending request, causing the contract to deliver a cryptographically-valid but semantically-forged attestation to the waiting caller.

---

### Finding Description

The `ForeignTxSignPayload` is defined as:

```rust
pub struct ForeignTxSignPayloadV1 {
    pub request: ForeignChainRpcRequest,
    pub values: Vec<ExtractedValue>,
}
// msg_hash = SHA-256(borsh(ForeignTxSignPayload))
``` [1](#0-0) 

The hash commits to **both** the original chain request (tx id, chain, extractors) **and** the extracted values (block hash, log data, etc.). The MPC nodes sign this hash and submit it via `respond_verify_foreign_tx(request, response)` where `response = { payload_hash, signature }`.

Inside `respond_verify_foreign_tx`, the contract performs two checks:

1. **Signature validity**: `verify_ecdsa_signature(signature, payload_hash, root_public_key)` — confirms the signature is valid over the supplied `payload_hash`.
2. **Request lookup**: `resolve_yields_for(pending_verify_foreign_tx_requests, &request, response_bytes)` — confirms a pending yield exists for the supplied `request`. [2](#0-1) 

**The missing check**: the contract never recomputes `expected_hash = SHA-256(borsh(ForeignTxSignPayload::V1 { request, values }))` and never asserts `response.payload_hash == expected_hash`. Because `values` are not included in the response, the contract has no way to verify the binding between `payload_hash` and `request`. The two checks above are entirely independent — a valid `(payload_hash_Y, signature_Y)` pair produced for request Y passes check 1, and a legitimately-queued request X passes check 2, even when Y ≠ X.

Contrast this with the regular `respond` function, where the signature is verified against a **derived key** computed from `request.tweak = hash(predecessor || path)`, cryptographically binding the signature to the specific request: [3](#0-2) 

No equivalent binding exists in `respond_verify_foreign_tx`.

---

### Impact Explanation

A bridge contract (e.g., Omnibridge inbound flow) calls `verify_foreign_transaction` for Bitcoin tx X expecting to receive an MPC-signed attestation that tx X finalized with block hash B_X. Instead, it receives a valid MPC signature over `payload_hash_Y = SHA-256(borsh({ request_Y, values_Y }))`, which commits to a completely different transaction Y's data (e.g., block hash B_Y, different log values, different amounts). The signature is cryptographically valid under the MPC root key — the bridge contract cannot distinguish it from a legitimate response. The bridge then acts on forged extracted values, enabling:

- **Double-spend**: attacker replays the attestation for a small/already-processed deposit as proof of a large deposit.
- **Unauthorized bridge execution**: attacker substitutes extracted values (e.g., token amount, recipient address) from a different transaction to trigger an unintended bridge action.

This matches the **High** impact category: *forged foreign-chain verification that causes invalid bridge execution or double-spend conditions*.

---

### Likelihood Explanation

The attack requires a **single Byzantine attested participant** (strictly below the signing threshold). The attacker:

1. Participates in the MPC network as a legitimate node (TEE-attested).
2. Observes any legitimately-produced `(payload_hash_Y, signature_Y)` for request Y — this is submitted on-chain and is publicly readable.
3. Races to call `respond_verify_foreign_tx(request=request_X, response={payload_hash_Y, signature_Y})` before the honest leader submits the legitimate response for request X.

The race window is the time between when request X is queued on-chain and when the honest MPC leader submits its response. This window is non-trivial (seconds to minutes depending on RPC latency and block times). The attacker does not need to collude with any other participant. The only prerequisite is being an attested participant, which is the normal operational state for any MPC node.

---

### Recommendation

Include the `extracted_values` in `VerifyForeignTransactionResponse` so the contract can independently recompute and verify the `payload_hash`:

```rust
pub struct VerifyForeignTransactionResponse {
    pub payload_hash: Hash256,
    pub signature: SignatureResponse,
    pub values: Vec<ExtractedValue>,  // add this
}
```

In `respond_verify_foreign_tx`, after verifying the signature, add:

```rust
let expected_hash = ForeignTxSignPayload::V1(ForeignTxSignPayloadV1 {
    request: request.request.clone(),
    values: response.values.clone(),
}).compute_msg_hash()?;

if expected_hash != response.payload_hash {
    return Err(RespondError::InvalidPayloadHash.into());
}
```

This recomputes the hash from the known `request` and the submitted `values`, and asserts it matches `response.payload_hash`. A Byzantine node can no longer substitute a `payload_hash` from a different request because the `values` would not produce the correct hash for the target `request`.

---

### Proof of Concept

**Setup**: Two pending `verify_foreign_transaction` requests are queued:
- Request X: `Bitcoin { tx_id: [0xAA; 32], extractors: [BlockHash] }` — submitted by a bridge contract expecting block hash `B_X`.
- Request Y: `Bitcoin { tx_id: [0xBB; 32], extractors: [BlockHash] }` — submitted by an attacker.

**Step 1**: The MPC network legitimately processes request Y and the honest leader calls:
```
respond_verify_foreign_tx(
    request = request_Y,
    response = { payload_hash_Y, signature_Y }
)
```
`payload_hash_Y = SHA-256(borsh({ request_Y, values: [BlockHash(B_Y)] }))`. This is now on-chain.

**Step 2**: The Byzantine participant (before the honest leader responds to X) calls:
```
respond_verify_foreign_tx(
    request = request_X,          // matches a pending yield for X
    response = { payload_hash_Y, signature_Y }  // recycled from Y
)
```

**Step 3**: The contract checks:
- `verify_ecdsa_signature(signature_Y, payload_hash_Y, root_pk)` → **PASSES** (signature is valid).
- `resolve_yields_for(pending_requests, &request_X, ...)` → **PASSES** (request X is pending).

**Step 4**: The bridge contract's `verify_foreign_transaction` call for tx X resolves with `{ payload_hash_Y, signature_Y }`. The bridge reconstructs the payload locally and finds the hash matches a payload committing to tx Y's block hash B_Y — not B_X. The bridge is deceived into treating B_Y as the verified block hash for tx X. [4](#0-3) [1](#0-0) [3](#0-2)

### Citations

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L1499-1509)
```rust
pub struct ForeignTxSignPayloadV1 {
    pub request: ForeignChainRpcRequest,
    pub values: Vec<ExtractedValue>,
}

impl ForeignTxSignPayload {
    pub fn compute_msg_hash(&self) -> std::io::Result<Hash256> {
        let mut hasher = sha2::Sha256::new();
        borsh::BorshSerialize::serialize(self, &mut hasher)?;
        Ok(Hash256(hasher.finalize().into()))
    }
```

**File:** crates/contract/src/lib.rs (L597-608)
```rust
                let expected_public_key =
                    derive_key_secp256k1(&affine, &request.tweak).map_err(RespondError::from)?;

                let payload_hash = request.payload.as_ecdsa().expect("Payload is not ECDSA");

                // Check the signature is correct
                near_mpc_signature_verifier::verify_ecdsa_signature(
                    signature_response,
                    payload_hash,
                    &expected_public_key,
                )
                .is_ok()
```

**File:** crates/contract/src/lib.rs (L691-754)
```rust
    #[handle_result]
    pub fn respond_verify_foreign_tx(
        &mut self,
        request: VerifyForeignTransactionRequest,
        response: VerifyForeignTransactionResponse,
    ) -> Result<(), Error> {
        let signer = Self::assert_caller_is_signer();

        log!(
            "respond_verify_foreign_tx: signer={}, request={:?}",
            &signer,
            &request
        );

        self.assert_caller_is_attested_participant_and_protocol_active();

        if !self.protocol_state.is_running_or_resharing() {
            return Err(InvalidState::ProtocolStateNotRunning.into());
        }

        if !self.accept_requests {
            return Err(TeeError::TeeValidationFailed.into());
        }

        let domain = request.domain_id;
        let public_key = self.public_key_extended(domain.0.into())?;

        let signature_is_valid = match (&response.signature, public_key) {
            (
                dtos::SignatureResponse::Secp256k1(signature_response),
                PublicKeyExtended::Secp256k1 { near_public_key },
            ) => {
                let secp_pk = dtos::Secp256k1PublicKey::try_from(&near_public_key)
                    .expect("Secp256k1 variant always has a secp256k1 key");

                let payload_hash: [u8; 32] = response.payload_hash.0;

                // Check the signature is correct against the root public key
                near_mpc_signature_verifier::verify_ecdsa_signature(
                    signature_response,
                    &payload_hash,
                    &secp_pk,
                )
                .is_ok()
            }
            (signature_response, public_key_requested) => {
                return Err(RespondError::SignatureSchemeMismatch {
                    mpc_scheme: Box::new(signature_response.clone()),
                    user_scheme: Box::new(public_key_requested),
                }
                .into());
            }
        };

        if !signature_is_valid {
            return Err(RespondError::InvalidSignature.into());
        }

        pending_requests::resolve_yields_for(
            &mut self.pending_verify_foreign_tx_requests,
            &request,
            serde_json::to_vec(&response).unwrap(),
        )
    }
```
