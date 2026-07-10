Looking at the `respond_verify_foreign_tx` flow in detail, I need to compare it against the regular `respond` function to find the analog to the GMX missing-check vulnerability.

**Key observation in `respond` (regular signing):**
The signature is verified against `request.payload` — the payload is taken directly from the stored request, so the signature is cryptographically bound to the original user request.

**Key observation in `respond_verify_foreign_tx`:**
The signature is verified against `response.payload_hash` — a value supplied by the calling node, not derived from the stored `request`. The contract never checks that `response.payload_hash == SHA-256(borsh(ForeignTxSignPayload{request, values}))`.

This is the structural analog: in GMX, `minOutputAmount` was checked on the swap path but skipped on the direct-transfer path. Here, the payload binding check exists in `respond` but is entirely absent in `respond_verify_foreign_tx`.

---

### Title
Missing `payload_hash`-to-Request Binding in `respond_verify_foreign_tx` Enables Cross-Request Signature Replay — (File: `crates/contract/src/lib.rs`)

### Summary

`respond_verify_foreign_tx` verifies that the submitted ECDSA signature is valid over `response.payload_hash`, but never verifies that `response.payload_hash` is derived from the original `request`. A Byzantine MPC node that acts as the signing leader for **any** pending foreign-tx request can take the resulting threshold signature and submit it as the response to a **different** pending request, delivering a cryptographically valid but semantically fraudulent attestation to every caller waiting on that second request.

### Finding Description

When a user calls `verify_foreign_transaction(request_A)`, the contract stores the request in `pending_verify_foreign_tx_requests` and suspends the caller via NEAR's yield-resume mechanism. An MPC node later calls `respond_verify_foreign_tx(request_A, response)` to deliver the result.

The contract's validation in `respond_verify_foreign_tx` is:

```
1. Caller is an attested participant
2. Protocol is running/resharing and accepting requests
3. signature is valid over response.payload_hash (using root public key)
4. request_A exists in pending_verify_foreign_tx_requests
``` [1](#0-0) 

What is **never checked**: that `response.payload_hash` equals `SHA-256(borsh(ForeignTxSignPayload{ request: request_A, values: <anything> }))`. The hash is accepted as-is from the calling node.

Contrast this with the regular `respond` function, where the payload to verify against is taken directly from the stored `request`, not from the response: [2](#0-1) 

On the node side, the leader computes `payload_hash` from the extracted foreign-chain values and submits it to the threshold signing protocol: [3](#0-2) 

The leader is the only party that assembles the final

### Citations

**File:** crates/contract/src/lib.rs (L600-608)
```rust
                let payload_hash = request.payload.as_ecdsa().expect("Payload is not ECDSA");

                // Check the signature is correct
                near_mpc_signature_verifier::verify_ecdsa_signature(
                    signature_response,
                    payload_hash,
                    &expected_public_key,
                )
                .is_ok()
```

**File:** crates/contract/src/lib.rs (L718-743)
```rust
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
```

**File:** crates/node/src/providers/verify_foreign_tx/sign.rs (L30-48)
```rust
fn build_signature_request(
    request: &VerifyForeignTxRequest,
    foreign_tx_payload: &dtos::ForeignTxSignPayload,
) -> anyhow::Result<SignatureRequest> {
    let payload_hash: [u8; ECDSA_PAYLOAD_SIZE_BYTES] =
        foreign_tx_payload.compute_msg_hash()?.into();
    let payload_bytes: BoundedVec<u8, ECDSA_PAYLOAD_SIZE_BYTES, ECDSA_PAYLOAD_SIZE_BYTES> =
        payload_hash.into();

    Ok(SignatureRequest {
        id: request.id,
        receipt_id: request.receipt_id,
        payload: Payload::Ecdsa(payload_bytes),
        tweak: Tweak::new([0u8; 32]),
        entropy: request.entropy,
        timestamp_nanosec: request.timestamp_nanosec,
        domain: request.domain_id,
    })
}
```
