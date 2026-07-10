### Title
`respond_verify_foreign_tx` Does Not Bind `response.payload_hash` to the Submitted `request` — (File: `crates/contract/src/lib.rs`)

---

### Summary

`respond_verify_foreign_tx` verifies that the MPC signature is valid over `response.payload_hash`, but never checks that `response.payload_hash` is the correct hash for the `request` argument. A Byzantine MPC participant (below threshold) who holds a valid MPC signature produced for one pending foreign-tx request can submit it as the response for a *different* pending request, causing the contract to deliver a forged foreign-chain verification attestation to the victim caller.

---

### Finding Description

The `respond_verify_foreign_tx` entry point accepts two independent arguments: a `VerifyForeignTransactionRequest` (used as the map key to locate and drain pending yields) and a `VerifyForeignTransactionResponse` (containing `payload_hash` and `signature`). [1](#0-0) 

The only cryptographic check performed is:

```rust
let payload_hash: [u8; 32] = response.payload_hash.0;
near_mpc_signature_verifier::verify_ecdsa_signature(
    signature_response,
    &payload_hash,
    &secp_pk,
).is_ok()
```

This confirms the signature is valid over *some* 32-byte hash, but **never asserts that `payload_hash` equals `SHA-256(borsh(ForeignTxSignPayload { request, values }))`** for the specific `request` being resolved. [2](#0-1) 

Contrast this with the regular `respond` path, where the payload is embedded directly inside the `SignatureRequest` key, so the signature is automatically bound to the correct payload: [3](#0-2) 

For foreign-tx requests the `payload_hash` is intentionally kept out of the request key (because extracted values are unknown at submission time), but no compensating on-chain binding check was added. [4](#0-3) 

The `ForeignChainSignatureVerifier` in the SDK does perform this binding check client-side: [5](#0-4) 

But the contract itself enforces no such invariant, leaving callers who do not use the SDK verifier fully exposed.

---

### Impact Explanation

A malicious MPC participant (a legitimate, attested participant acting Byzantine, strictly below the signing threshold) who has obtained a valid threshold signature for Request B can call:

```
respond_verify_foreign_tx(
    request  = Request_A,          // a different pending request
    response = { payload_hash_B, sig_B }  // signature produced for Request B
)
```

The contract accepts this call because:
1. `sig_B` is a valid MPC signature over `payload_hash_B` ✓
2. `Request_A` exists in `pending_verify_foreign_tx_requests` ✓ [6](#0-5) 

The yields queued under `Request_A` are drained and each caller receives `{ payload_hash_B, sig_B }` — a valid MPC signature that attests to the foreign-chain state of *Request B*, not *Request A*. Any bridge contract that does not independently verify `payload_hash` against its expected extracted values will accept this forged attestation and execute the corresponding bridge action (e.g., minting tokens for a deposit that was never actually verified). This matches the **High** impact class: *forged foreign-chain verification that causes invalid bridge execution*.

---

### Likelihood Explanation

- The attacker must be an active, attested MPC participant — a Byzantine node below threshold. This is an explicitly in-scope threat actor for the NEAR MPC bug bounty.
- Two concurrent pending `verify_foreign_transaction` requests with different `request` keys must exist simultaneously. Given that the system is designed for bridge use cases with continuous traffic, this is a routine condition.
- The attacker needs a valid MPC signature for one of the requests. Because the attacker participates in the threshold signing protocol, they receive the completed signature as part of normal operation.
- No threshold collusion is required; a single Byzantine participant suffices.

---

### Recommendation

Inside `respond_verify_foreign_tx`, after the signature check, recompute the expected `payload_hash` from the `request` and the extracted values supplied in the response, and assert equality before resolving yields. Concretely, change the response DTO to include the raw `Vec<ExtractedValue>` alongside `payload_hash`, compute `SHA-256(borsh(ForeignTxSignPayload { request, values }))` on-chain, and reject any call where the computed hash does not equal `response.payload_hash`. This mirrors how `respond` binds the signature to the payload embedded in the `SignatureRequest` key.

Alternatively, if including raw extracted values in the response is too large for NEAR's promise data limits, the contract should at minimum document that callers **must** use `ForeignChainSignatureVerifier::verify_signature` and that the contract-level response is not self-authenticating with respect to the originating request.

---

### Proof of Concept

1. Alice submits `verify_foreign_transaction(Bitcoin, tx_id=X, confirmations=6, extractors=[BlockHash])` — a bridge deposit of 1 BTC. This creates `Request_A` in `pending_verify_foreign_tx_requests`.

2. Attacker also submits `verify_foreign_transaction(Bitcoin, tx_id=Y, confirmations=6, extractors=[BlockHash])` — a deposit of 0.001 BTC. This creates `Request_B`.

3. The MPC network legitimately processes `Request_B`. The attacker (as a participant) receives the completed signature `sig_B` over `payload_hash_B = SHA-256(borsh({ request_B, block_hash_Y }))`.

4. The attacker calls:
   ```
   respond_verify_foreign_tx(
       request  = Request_A,
       response = { payload_hash: payload_hash_B, signature: sig_B }
   )
   ```

5. The contract checks `verify_ecdsa_signature(sig_B, payload_hash_B, root_pk)` → valid. It then calls `resolve_yields_for(&mut pending_verify_foreign_tx_requests, &Request_A, serialize(response))`. [6](#0-5) 

6. Alice's bridge contract receives `{ payload_hash_B, sig_B }`. If it does not call `ForeignChainSignatureVerifier::verify_signature` (which would detect `payload_hash_B ≠ expected_payload_hash_A`), it accepts the response as proof that Bitcoin tx X was confirmed and mints 1 BTC worth of tokens — while the MPC network only ever verified tx Y (0.001 BTC).

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

**File:** crates/contract/src/lib.rs (L718-747)
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
```

**File:** crates/contract/src/lib.rs (L749-753)
```rust
        pending_requests::resolve_yields_for(
            &mut self.pending_verify_foreign_tx_requests,
            &request,
            serde_json::to_vec(&response).unwrap(),
        )
```

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L124-128)
```rust
pub struct VerifyForeignTransactionRequest {
    pub request: ForeignChainRpcRequest,
    pub domain_id: DomainId,
    pub payload_version: ForeignTxPayloadVersion,
}
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
