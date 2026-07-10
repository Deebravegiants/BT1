### Title
`respond_verify_foreign_tx` Does Not Validate That `response.payload_hash` Corresponds to the Submitted `request` — (File: `crates/contract/src/lib.rs`)

---

### Summary

`respond_verify_foreign_tx` verifies only that `response.signature` is a valid ECDSA signature over `response.payload_hash`. It never checks that `payload_hash` is actually the hash of `ForeignTxSignPayload { request: <the submitted request>, values: ... }`. A single Byzantine attested participant can therefore replay a legitimately-produced MPC signature from one foreign-chain verification request as the response to a completely different pending request, causing the contract to resolve that request with a forged payload hash.

---

### Finding Description

`respond_verify_foreign_tx` in `crates/contract/src/lib.rs` performs the following check:

```rust
let payload_hash: [u8; 32] = response.payload_hash.0;

near_mpc_signature_verifier::verify_ecdsa_signature(
    signature_response,
    &payload_hash,
    &secp_pk,
)
.is_ok()
``` [1](#0-0) 

It then resolves all queued yields for the submitted `request` with the raw `response` bytes:

```rust
pending_requests::resolve_yields_for(
    &mut self.pending_verify_foreign_tx_requests,
    &request,
    serde_json::to_vec(&response).unwrap(),
)
``` [2](#0-1) 

The signed payload is defined as `SHA-256(borsh(ForeignTxSignPayload))` where `ForeignTxSignPayload` contains both the `ForeignChainRpcRequest` and the `values` (extracted chain data):

```rust
pub struct ForeignTxSignPayloadV1 {
    pub request: ForeignChainRpcRequest,
    pub values: Vec<ExtractedValue>,
}
``` [3](#0-2) 

The contract never reconstructs or validates that `response.payload_hash` equals `SHA-256(borsh(ForeignTxSignPayload { request: <the pending request>, values: ... }))`. The `values` are not submitted to the contract, so the contract cannot recompute the expected hash — but it also makes no attempt to bind the hash to the request in any other way.

**Cross-request replay attack path:**

1. Two requests are pending: request A (Bitcoin tx A) and request B (Bitcoin tx B).
2. The MPC network legitimately processes request B, producing `(hash_B, sig_B)` where `hash_B = SHA-256(borsh(ForeignTxSignPayload { request: B, values: [blockHash_B] }))`.
3. A single Byzantine attested participant calls `respond_verify_foreign_tx(request=A, response={ payload_hash: hash_B, signature: sig_B })`.
4. The contract checks: is `sig_B` a valid signature over `hash_B` against the root public key? **Yes** — the signature is genuine.
5. The contract resolves all yields queued for request A with `{ payload_hash: hash_B, signature: sig_B }`.
6. The caller who submitted request A receives a response whose `payload_hash` encodes the verification of Bitcoin tx B, not Bitcoin tx A.

The caller's NEAR contract receives `{ payload_hash, signature }` but not the full `ForeignTxSignPayload`. It cannot reconstruct the expected hash without knowing `values`, so it cannot detect that `payload_hash` encodes a different transaction. The docs acknowledge that callers are expected to verify the hash locally, but this is impossible without the `values`. [4](#0-3) 

---

### Impact Explanation

A bridge contract (e.g., Omnibridge inbound flow) that calls `verify_foreign_transaction` to attest that a specific foreign-chain deposit occurred before releasing funds will receive a `VerifyForeignTransactionResponse` whose `payload_hash` and `signature` are cryptographically valid but correspond to a *different* foreign-chain transaction. Because the caller cannot verify the binding between `payload_hash` and their submitted request (the `values` are never returned), the bridge contract may incorrectly conclude that its target transaction was verified and release funds for a transaction that was never confirmed or that corresponds to a different amount/recipient. This enables forged foreign-chain verification and invalid bridge execution — a High-severity impact under the allowed scope.

---

### Likelihood Explanation

The attack requires only a single Byzantine attested participant. No threshold collusion is needed: the attacker simply waits for the MPC network to legitimately produce a signature for any other pending request, then replays that `(hash, signature)` pair against a different pending request. Any attested participant observes the signatures produced during the MPC protocol and can extract them. The attack is therefore realistic for any participant who turns adversarial.

---

### Recommendation

Have nodes submit the full `ForeignTxSignPayload` (not just the hash) in the response. The contract should then:

1. Recompute `expected_hash = SHA-256(borsh(payload))`.
2. Assert `expected_hash == response.payload_hash`.
3. Assert `payload.request == request` (the pending request key).

This binds the signature to the specific pending request and eliminates the cross-request replay vector. Alternatively, include a domain-separation tag or the request's unique yield ID inside the signed payload so that signatures produced for one request cannot be reused for another.

---

### Proof of Concept

```
1. Alice submits verify_foreign_transaction(request=A) → pending request A queued.
2. Bob  submits verify_foreign_transaction(request=B) → pending request B queued.
3. MPC network processes request B → produces (hash_B, sig_B).
4. Byzantine attested participant calls:
       respond_verify_foreign_tx(
           request = A,                          // Alice's request
           response = { payload_hash: hash_B,   // hash of request B's payload
                        signature:    sig_B }    // valid sig over hash_B
       )
5. Contract: verify_ecdsa_signature(sig_B, hash_B, root_pk) → OK.
6. Contract resolves Alice's yield with { payload_hash: hash_B, signature: sig_B }.
7. Alice's bridge contract receives the response, verifies the signature (valid),
   and cannot distinguish hash_B from the expected hash for request A.
8. Bridge releases funds as if Bitcoin tx A was confirmed.
```

### Citations

**File:** crates/contract/src/lib.rs (L718-753)
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

        if !signature_is_valid {
            return Err(RespondError::InvalidSignature.into());
        }

        pending_requests::resolve_yields_for(
            &mut self.pending_verify_foreign_tx_requests,
            &request,
            serde_json::to_vec(&response).unwrap(),
        )
```

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L1499-1502)
```rust
pub struct ForeignTxSignPayloadV1 {
    pub request: ForeignChainRpcRequest,
    pub values: Vec<ExtractedValue>,
}
```
