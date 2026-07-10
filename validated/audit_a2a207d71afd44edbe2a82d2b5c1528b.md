### Title
`respond_verify_foreign_tx` Does Not Bind `response.payload_hash` to the Submitted Request, Enabling Cross-Request Response Injection by a Single Byzantine Participant — (File: `crates/contract/src/lib.rs`)

---

### Summary

`respond_verify_foreign_tx` verifies that the supplied signature is cryptographically valid over `response.payload_hash`, but never checks that `response.payload_hash` was actually derived from the `request` argument that is used as the pending-map key. A single malicious attested participant (below the signing threshold) can take a legitimately produced threshold signature for one pending request and submit it as the response for a *different* pending request, delivering a forged foreign-chain verification attestation to the caller.

---

### Finding Description

In `respond_verify_foreign_tx` the contract performs two independent checks:

1. **Caller check** – the caller must be an attested participant.
2. **Signature check** – the signature in `response` must verify over `response.payload_hash` under the domain's root public key.

```rust
// crates/contract/src/lib.rs  lines 726-734
let payload_hash: [u8; 32] = response.payload_hash.0;

// Check the signature is correct against the root public key
near_mpc_signature_verifier::verify_ecdsa_signature(
    signature_response,
    &payload_hash,
    &secp_pk,
)
.is_ok()
``` [1](#0-0) 

After both checks pass, the contract resolves every queued yield for `request` with the raw `response` bytes:

```rust
pending_requests::resolve_yields_for(
    &mut self.pending_verify_foreign_tx_requests,
    &request,
    serde_json::to_vec(&response).unwrap(),
)
``` [2](#0-1) 

**What is never checked**: that `response.payload_hash` equals `SHA-256(borsh(ForeignTxSignPayload::V1 { request, extracted_values }))` for the specific `request` being resolved. The `payload_hash` is a free field supplied entirely by the calling node.

Contrast this with the regular `respond` path, where the payload is taken directly from the stored request and is therefore immutably bound to it:

```rust
// crates/contract/src/lib.rs  line 600
let payload_hash = request.payload.as_ecdsa().expect("Payload is not ECDSA");
``` [3](#0-2) 

The canonical payload structure that nodes are supposed to sign is:

```rust
pub struct ForeignTxSignPayloadV1 {
    pub request: ForeignChainRpcRequest,
    pub values: Vec<ExtractedValue>,
}
``` [4](#0-3) 

The `request` field is embedded in the hash, so `payload_hash_A ≠ payload_hash_B` for two different requests. The contract never enforces this binding.

---

### Impact Explanation

A malicious attested participant (the leader for a signing round) can:

1. Observe that the MPC network has produced a valid threshold signature `sig_A` over `payload_hash_A` for pending `request_A`.
2. Call `respond_verify_foreign_tx(request_B, { payload_hash_A, sig_A })` while `request_B` is also pending.
3. The contract accepts the call: `sig_A` is a valid ECDSA signature over `payload_hash_A` under the root key, and `request_B` exists in the pending map.
4. Every yield queued under `request_B` is resolved with `{ payload_hash_A, sig_A }`.

The caller of `verify_foreign_transaction(request_B)` receives a `VerifyForeignTransactionResponse` whose `payload_hash` encodes `(request_A, values_A)` — a completely different foreign-chain transaction. Any NEAR contract that does not independently recompute the expected hash (using `ForeignChainSignatureVerifier` from the SDK) will treat this as a valid attestation of `request_B`'s foreign-chain state, enabling forged bridge attestations and potential double-spend conditions.

The SDK-side verifier does catch this if used correctly:

```rust
let payload_is_correct = expected_payload_hash == response.payload_hash;
if !payload_is_correct {
    return Err(VerifyForeignChainError::IncorrectPayloadSigned { ... });
}
``` [5](#0-4) 

However, the contract itself provides no on-chain enforcement of this invariant, leaving every caller that omits or misuses the SDK verifier exposed.

---

### Likelihood Explanation

**Low.** The attacker must be an active attested participant (a TEE-verified MPC node). However, the system's Byzantine fault-tolerance model explicitly tolerates up to `n − threshold` malicious participants; a single rogue node is within that budget. The attack requires only that two requests be pending simultaneously — a routine condition for any bridge service processing concurrent transactions. No threshold collusion is needed: the attacker reuses a legitimately produced threshold signature, not a forged one.

---

### Recommendation

Add an on-chain binding check inside `respond_verify_foreign_tx`. Include the `extracted_values` in the response type and verify the hash before resolving yields:

```rust
// Proposed addition in respond_verify_foreign_tx
let expected_payload = ForeignTxSignPayload::V1(ForeignTxSignPayloadV1 {
    request: request.request.clone(),
    values: response.extracted_values.clone(), // add this field to the response DTO
});
let expected_hash = expected_payload.compute_msg_hash()
    .map_err(|_| RespondError::PayloadHashComputationFailed)?;
if expected_hash != response.payload_hash {
    return Err(RespondError::PayloadHashMismatch.into());
}
```

This mirrors the binding already present in `respond`, where the payload is taken from the stored request rather than from the caller-supplied response.

---

### Proof of Concept

**Setup**: Two concurrent `verify_foreign_transaction` requests, `request_A` (Bitcoin tx `[0xAA;32]`) and `request_B` (Bitcoin tx `[0xBB;32]`), are both pending in `pending_verify_foreign_tx_requests`.

**Step 1** – MPC network legitimately signs for `request_A`:
```rust
let payload_a = ForeignTxSignPayload::V1(ForeignTxSignPayloadV1 {
    request: request_a.request.clone(),
    values: vec![ExtractedValue::BitcoinExtractedValue(
        BitcoinExtractedValue::BlockHash([0xAA; 32].into()),
    )],
});
let payload_hash_a = payload_a.compute_msg_hash().unwrap();
// threshold signature produced by MPC network over payload_hash_a
let (sig_a, recovery_id) = signing_key.sign_prehash_recoverable(&payload_hash_a.0).unwrap();
```

**Step 2** – Malicious leader injects `sig_A` as the response for `request_B`:
```rust
let forged_response = VerifyForeignTransactionResponse {
    payload_hash: payload_hash_a,          // hash of request_A's payload
    signature: dtos::SignatureResponse::Secp256k1(
        dtos::K256Signature::from_ecdsa_recoverable(&sig_a, recovery_id),
    ),
};
// Called by the malicious attested participant:
contract.respond_verify_foreign_tx(request_b.clone(), forged_response)
    .expect("contract accepts it — signature is valid, request_B is pending");
```

**Step 3** – Caller of `request_B` receives `payload_hash_A`:
The yield for `request_B` is resolved with `payload_hash_A`. Any bridge contract that reads `response.payload_hash` without recomputing the expected hash from `request_B` and its own expected extracted values will treat this as a valid attestation of `request_B`'s foreign-chain state.

The root cause — `response.payload_hash` is never verified against `request` — is at:
<cite repo="Alyssadaypin/mpc--009" path="crates/contract/src/lib.rs" start="726

### Citations

**File:** crates/contract/src/lib.rs (L600-601)
```rust
                let payload_hash = request.payload.as_ecdsa().expect("Payload is not ECDSA");

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

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L1499-1502)
```rust
pub struct ForeignTxSignPayloadV1 {
    pub request: ForeignChainRpcRequest,
    pub values: Vec<ExtractedValue>,
}
```

**File:** crates/near-mpc-sdk/src/foreign_chain.rs (L57-63)
```rust
        let payload_is_correct = expected_payload_hash == response.payload_hash;

        if !payload_is_correct {
            return Err(VerifyForeignChainError::IncorrectPayloadSigned {
                got: response.payload_hash.clone(),
                expected: expected_payload_hash,
            });
```
