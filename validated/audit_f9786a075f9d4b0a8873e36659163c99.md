### Title
`respond_verify_foreign_tx` Does Not Bind `payload_hash` to the Submitted `request`, Enabling Cross-Request Response Replay by a Single Byzantine Participant - (`File: crates/contract/src/lib.rs`)

### Summary

`respond_verify_foreign_tx` verifies only that the ECDSA signature is valid over the caller-supplied `response.payload_hash`, but never checks that `response.payload_hash` is the correct hash for the pending `request`. A single Byzantine attested participant can replay any previously observed valid `{payload_hash, signature}` pair against any currently pending foreign-tx request, causing the contract to resolve that request with a fabricated verification result.

### Finding Description

In `respond_verify_foreign_tx` the contract performs:

```rust
let payload_hash: [u8; 32] = response.payload_hash.0;

// Check the signature is correct against the root public key
near_mpc_signature_verifier::verify_ecdsa_signature(
    signature_response,
    &payload_hash,
    &secp_pk,
)
.is_ok()
``` [1](#0-0) 

The check confirms only that `signature` is a valid ECDSA signature over `response.payload_hash` under the MPC root key. It does **not** verify that `response.payload_hash` equals `SHA-256(borsh(ForeignTxSignPayload { request, values }))` for the specific `request` being resolved.

Contrast this with `respond`, where the payload is extracted directly from the user-submitted `request` and is therefore immutably bound to the request key:

```rust
let payload_hash = request.payload.as_ecdsa().expect("Payload is not ECDSA");
near_mpc_signature_verifier::verify_ecdsa_signature(
    signature_response,
    payload_hash,
    &expected_public_key,
)
``` [2](#0-1) 

In `respond`, the payload is fixed by the user's request and cannot be substituted. In `respond_verify_foreign_tx`, the `payload_hash` is a free field in the response DTO, entirely under the caller's control.

The `ForeignTxSignPayload` is designed so that the hash commits to both the `request` and the extracted `values`:

```rust
pub struct ForeignTxSignPayloadV1 {
    pub request: ForeignChainRpcRequest,
    pub values: Vec<ExtractedValue>,
}
``` [3](#0-2) 

The contract cannot recompute this hash (it lacks `values`), but it also performs no partial binding check. The `resolve_yields_for` call then delivers the attacker-chosen `response` bytes to every queued yield under the target request:

```rust
pending_requests::resolve_yields_for(
    &mut self.pending_verify_foreign_tx_requests,
    &request,
    serde_json::to_vec(&response).unwrap(),
)
``` [4](#0-3) 

The SDK-side verifier `ForeignChainSignatureVerifier::verify_signature` does perform the binding check:

```rust
let payload_is_correct = expected_payload_hash == response.payload_hash;
if !payload_is_correct {
    return Err(VerifyForeignChainError::IncorrectPayloadSigned { ... });
}
``` [5](#0-4) 

But this check lives in the **caller's** bridge contract, not in the MPC contract. The MPC contract provides no on-chain guarantee that the delivered `payload_hash` corresponds to the resolved request.

### Impact Explanation

A single Byzantine attested participant can:

1. Observe any previously submitted valid `{payload_hash_X, signature_X}` pair on-chain (for foreign tx X).
2. Wait for a new pending request B (for foreign tx Y) to appear.
3. Call `respond_verify_foreign_tx(request_B, {payload_hash: payload_hash_X, signature: signature_X})`.
4. The contract accepts the call (signature is valid over `payload_hash_X` under the root key).
5. All yields queued under `request_B` are resolved with the fabricated response.

Bridge contracts that do not use `ForeignChainSignatureVerifier::verify_signature` will receive a response asserting that foreign tx Y was verified, backed by a valid MPC signature, but the signed payload actually describes foreign tx X. This enables forged foreign-chain verification and potential double-spend or invalid bridge execution — matching the **High** impact category.

### Likelihood Explanation

- No threshold cooperation is required; a single attested participant suffices.
- `respond_verify_foreign_tx` has no leader-only guard; any attested participant may call it.
- The attacker needs only to observe a prior on-chain response (publicly available) and have a concurrent pending request to target.
- The attack is repeatable for every new pending request.

### Recommendation

The contract should bind the response to the request at the on-chain level. Two complementary mitigations:

1. **Store a request commitment at submission time.** When `verify_foreign_transaction` is called, store a hash of the `ForeignChainRpcRequest` alongside the yield queue. In `respond_verify_foreign_tx`, require the MPC node to also supply the `values`, recompute `SHA-256(borsh(ForeignTxSignPayload { request, values }))` on-chain, and assert it equals `response.payload_hash`. (This requires the response to carry `values`, which may need a size budget review.)

2. **Alternatively, include a nonce or request-specific tag in the signed payload.** Extend `ForeignTxSignPayloadV1` with a unique per-request identifier (e.g., the NEAR receipt ID stored at submission time) so that a signature produced for one request is cryptographically invalid for any other.

### Proof of Concept

```
// Setup: request A for Bitcoin tx X is submitted and legitimately resolved.
// The on-chain response {payload_hash_X, sig_X} is now publicly visible.

// Attacker (single Byzantine attested participant) observes payload_hash_X and sig_X.

// A new request B for Bitcoin tx Y is submitted by a bridge contract.
// pending_verify_foreign_tx_requests[request_B] = [yield_id_B]

// Attacker calls:
respond_verify_foreign_tx(
    request  = request_B,          // matches the pending request key
    response = VerifyForeignTransactionResponse {
        payload_hash: payload_hash_X,  // hash of tx X, not tx Y
        signature:    sig_X,           // valid signature over payload_hash_X
    }
)

// Contract checks:
//   assert_caller_is_attested_participant_and_protocol_active() -> OK
//   verify_ecdsa_signature(sig_X, payload_hash_X, root_pk) -> OK (valid)
//   resolve_yields_for(request_B, serialize({payload_hash_X, sig_X})) -> OK

// Bridge contract for request_B receives:
//   VerifyForeignTransactionResponse { payload_hash: payload_hash_X, signature: sig_X }
// If it skips ForeignChainSignatureVerifier::verify_signature, it accepts
// this as proof that tx Y was verified — but it was not.
```

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

**File:** crates/contract/src/lib.rs (L726-734)
```rust
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
