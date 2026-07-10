Looking at the `respond_verify_foreign_tx` function in `crates/contract/src/lib.rs`, I can identify a direct analog to the external report's "insufficient validation in a post-callback check" vulnerability class.

### Title
Missing Payload-Hash-to-Request Binding in `respond_verify_foreign_tx` Enables Cross-Request Signature Replay — (File: `crates/contract/src/lib.rs`)

### Summary
`respond_verify_foreign_tx` verifies that the submitted signature is cryptographically valid for `response.payload_hash`, but never verifies that `response.payload_hash` is actually the hash of the submitted `request`. A Byzantine MPC participant who is the signing leader for one pending foreign-tx request can replay that threshold signature as the authoritative response for a *different* pending request, causing the contract to attest to fabricated extracted values for the victim request.

### Finding Description
In `respond_verify_foreign_tx` the contract performs two checks:

1. The caller is an attested participant.
2. The ECDSA signature in `response` is valid for `response.payload_hash` against the **root** public key. [1](#0-0) 

`payload_hash` is taken directly from the attacker-controlled `response` argument — it is never compared against any hash derived from the `request` argument. The contract then resolves the pending yield keyed on `request` with the full `response` blob: [2](#0-1) 

Contrast this with the regular `respond` function, where the payload is extracted from the *request itself* (`request.payload.as_ecdsa()`), so the signature is cryptographically bound to the specific request: [3](#0-2) 

Foreign-tx responses use the **root** key with no per-request tweak, as confirmed by the test comment "simulate signature with the root key (no tweak for foreign tx)": [4](#0-3) 

Because there is no tweak and no on-chain binding between `response.payload_hash` and `request`, any valid root-key signature over *any* hash passes the check.

### Impact Explanation
The `ForeignTxSignPayloadV1` struct binds the hash to a specific `ForeignChainRpcRequest` (including `tx_id`): [5](#0-4) 

A Byzantine signing leader for request **T2** assembles the complete threshold signature σ\_T2 over `H(T2, values2)`. They then call `respond_verify_foreign_tx(T1, {payload_hash: H(T2, values2), signature: σ_T2})` for a *different* pending request **T1**. The contract:

- Finds T1 in the pending map ✓
- Verifies σ\_T2 is a valid root-key signature over `H(T2, values2)` ✓
- Resolves T1's yield with `{payload_hash: H(T2, values2), signature: σ_T2}`

The user's bridge contract receives a signed MPC attestation claiming that transaction T1 produced the extracted values of T2. Any bridge that does not independently recompute and compare `payload_hash` (e.g., does not use `ForeignChainSignatureVerifier.verify_signature`) will accept this as a valid verification of T1, enabling invalid bridge execution or double-spend conditions.

The SDK does provide a client-side check: [6](#0-5) 

However, the *contract itself* provides no such guarantee, so any bridge that trusts the contract's yield result without re-verifying `payload_hash` is vulnerable.

### Likelihood Explanation
- The attacker must be a TE

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

**File:** crates/contract/src/lib.rs (L718-734)
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
```

**File:** crates/contract/src/lib.rs (L749-753)
```rust
        pending_requests::resolve_yields_for(
            &mut self.pending_verify_foreign_tx_requests,
            &request,
            serde_json::to_vec(&response).unwrap(),
        )
```

**File:** crates/contract/src/lib.rs (L3687-3693)
```rust
        let payload = ForeignTxSignPayload::V1(ForeignTxSignPayloadV1 {
            request: request.request.clone(),
            values: vec![ExtractedValue::BitcoinExtractedValue(
                BitcoinExtractedValue::BlockHash([42u8; 32].into()),
            )],
        });
        let payload_hash = payload.compute_msg_hash().unwrap().0;
```

**File:** crates/contract/src/lib.rs (L3694-3698)
```rust
        // simulate signature with the root key (no tweak for foreign tx)
        let secret_key_ec: elliptic_curve::SecretKey<Secp256k1> =
            elliptic_curve::SecretKey::from_bytes(&secret_key.to_bytes()).unwrap();
        let secret_key = SigningKey::from_bytes(&secret_key_ec.to_bytes()).unwrap();
        let (signature, recovery_id) = secret_key.sign_prehash_recoverable(&payload_hash).unwrap();
```

**File:** crates/near-mpc-sdk/src/foreign_chain.rs (L53-64)
```rust
        let expected_payload_hash = expected_payload
            .compute_msg_hash()
            .map_err(|_| VerifyForeignChainError::FailedToComputeMsgHash)?;

        let payload_is_correct = expected_payload_hash == response.payload_hash;

        if !payload_is_correct {
            return Err(VerifyForeignChainError::IncorrectPayloadSigned {
                got: response.payload_hash.clone(),
                expected: expected_payload_hash,
            });
        }
```
