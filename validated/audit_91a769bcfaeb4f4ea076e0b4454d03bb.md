### Title
Unverified `payload_hash` in `respond_verify_foreign_tx` Enables Cross-Request Attestation Forgery — (File: `crates/contract/src/lib.rs`)

---

### Summary

`respond_verify_foreign_tx` verifies only that the caller-supplied `response.payload_hash` carries a valid threshold signature, but never checks that `payload_hash` actually encodes the stored `request`. A single Byzantine MPC node acting as signing leader can produce a legitimate threshold signature for request A, then submit it as the response to a completely different pending request B. The contract accepts it, the victim caller receives a forged attestation, and request A silently times out.

---

### Finding Description

In `respond_verify_foreign_tx` the contract does:

```rust
let payload_hash: [u8; 32] = response.payload_hash.0;
// Check the signature is correct against the root public key
near_mpc_signature_verifier::verify_ecdsa_signature(
    signature_response,
    &payload_hash,
    &secp_pk,          // root key, no tweak
)
.is_ok()
```

`payload_hash` is taken verbatim from the caller-supplied `response`; the contract never recomputes it from the stored `request`. [1](#0-0) 

Contrast this with the regular `respond` path, where the payload hash is read from the **stored** request object, not from the response:

```rust
let payload_hash = request.payload.as_ecdsa().expect("Payload is not ECDSA");
near_mpc_signature_verifier::verify_ecdsa_signature(
    signature_response,
    payload_hash,
    &expected_public_key,
)
``` [2](#0-1) 

The `ForeignTxSignPayload` that nodes actually sign encodes both the chain-specific request **and** the extracted values:

```rust
pub struct ForeignTxSignPayloadV1 {
    pub request: ForeignChainRpcRequest,
    pub values: Vec<ExtractedValue>,
}
// msg_hash = SHA-256(borsh(ForeignTxSignPayload))
``` [3](#0-2) 

Because the contract stores only the `VerifyForeignTransactionRequest` key (chain query parameters) and never the extracted values, it cannot independently recompute the expected `payload_hash`. The contract therefore has no way to bind the response hash to the stored request. [4](#0-3) 

The node-side `build_signature_request` uses a **zero tweak**, meaning every foreign-tx signature is produced under the same root key regardless of which request it is for:

```rust
Ok(SignatureRequest {
    payload: Payload::Ecdsa(payload_bytes),
    tweak: Tweak::new([0u8; 32]),   // zero tweak → root key
    ...
})
``` [5](#0-4) 

This means any valid foreign-tx signature (over any `payload_hash`) will pass the contract's signature check against the root key, regardless of which pending request it is submitted against.

---

### Impact Explanation

A Byzantine leader node for request A can:

1. Coordinate the threshold signing of request A with honest follower nodes (who independently compute and sign `payload_hash_A = SHA256(borsh({request_A, extracted_values_A}))`).
2. Assemble the full threshold signature `sig_A`.
3. Call `respond_verify_foreign_tx(request_B, {payload_hash_A, sig_A})` targeting a different pending request B.
4. The contract verifies `sig_A` over `payload_hash_A` → valid; resolves request B's yield with `{payload_hash_A, sig_A}`.
5. The caller of request B receives an attestation whose `payload_hash` encodes a completely different transaction (request A's tx_id and extracted values).

Any bridge contract that only checks the ECDSA signature validity (mirroring what the MPC contract itself does) will accept this forged attestation and may execute bridge logic based on the wrong foreign-chain state. Request A is never resolved and times out, denying service to its submitter.

This maps directly to the **High** allowed impact: *"Forged foreign-chain verification … that causes invalid bridge execution or double-spend conditions."*

---

### Likelihood Explanation

- Requires exactly **one** Byzantine attested participant that happens to be elected leader for any request. Leader selection is deterministic and rotates across all participants, so every node will eventually be leader.
- The honest follower nodes contribute partial signatures without being able to detect that the leader will misroute the assembled signature; they sign the correct `payload_hash_A` in good faith.
- All pending requests are publicly visible on-chain, so the Byzantine leader can freely choose which pending request to target.
- No threshold collusion is needed; the Byzantine node exploits the assembled signature it legitimately holds as leader.

---

### Recommendation

The contract must bind the response hash to the stored request. Two complementary approaches:

1. **Recompute the hash on-chain**: Include the extracted values in the `VerifyForeignTransactionResponse` and have the contract recompute `SHA256(borsh(ForeignTxSignPayload{stored_request, extracted_values}))`, then assert it equals `response.payload_hash` before accepting the response.

2. **Domain-separate per request**: Apply a non-zero tweak derived from the request key (analogous to how `respond` derives a per-user key), so a signature produced for request A is cryptographically invalid for request B.

---

### Proof of Concept

```
1. Alice submits verify_foreign_transaction(request_A)  // Bitcoin tx X, 2 confirmations
2. Bob   submits verify_foreign_transaction(request_B)  // Bitcoin tx Y, 6 confirmations
   Both are stored in pending_verify_foreign_tx_requests.

3. Byzantine node N is elected leader for request_A.
4. N runs the threshold-ECDSA protocol with honest followers;
   all nodes independently compute:
     payload_

### Citations

**File:** crates/contract/src/lib.rs (L598-608)
```rust
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

**File:** crates/node/src/providers/verify_foreign_tx/sign.rs (L39-47)
```rust
    Ok(SignatureRequest {
        id: request.id,
        receipt_id: request.receipt_id,
        payload: Payload::Ecdsa(payload_bytes),
        tweak: Tweak::new([0u8; 32]),
        entropy: request.entropy,
        timestamp_nanosec: request.timestamp_nanosec,
        domain: request.domain_id,
    })
```
