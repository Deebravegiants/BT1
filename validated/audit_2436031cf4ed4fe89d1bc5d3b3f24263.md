### Title
Cross-Request Response Substitution in `respond_verify_foreign_tx` Enables Forged Foreign-Chain Verification Attestation - (File: `crates/contract/src/lib.rs`)

---

### Summary

`respond_verify_foreign_tx` verifies that the submitted signature is valid over the caller-supplied `response.payload_hash`, but never checks that `payload_hash` actually commits to the `request` being resolved. A single Byzantine attested participant can replay a valid `(payload_hash, signature)` pair from any previously completed foreign-chain verification as the response to a completely different pending request, causing the MPC contract to attest that a different foreign-chain transaction was verified.

---

### Finding Description

In `respond_verify_foreign_tx`, the on-chain signature check is:

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

The contract then resolves all yields queued under `request`:

```rust
pending_requests::resolve_yields_for(
    &mut self.pending_verify_foreign_tx_requests,
    &request,
    serde_json::to_vec(&response).unwrap(),
)
``` [2](#0-1) 

The two checks are entirely independent: the contract verifies that `sig` is valid over `payload_hash` under the root key, and separately that `request` exists in the pending map — but it never verifies that `payload_hash` is the correct hash for `request`. Specifically, it never checks that `payload_hash == SHA-256(borsh(ForeignTxSignPayload::V1 { request, values }))`.

This is structurally different from `respond()` for regular signatures, where the payload is extracted directly from the request object and cannot be substituted:

```rust
let payload_hash = request.payload.as_ecdsa().expect("Payload is not ECDSA");
near_mpc_signature_verifier::verify_ecdsa_signature(
    signature_response,
    payload_hash,
    &expected_public_key,
)
``` [3](#0-2) 

In `respond_verify_foreign_tx`, `payload_hash` comes from the response and is never validated against the request.

The design document specifies that `payload_hash` must commit to both the request and the extracted values:

```
msg_hash = SHA-256(borsh(ForeignTxSignPayload))
```

where `ForeignTxSignPayloadV1 { request, values }` binds the hash to the specific `ForeignChainRpcRequest`. [4](#0-3) 

Because all `verify_foreign_transaction` responses are signed under the same root key (no per-request key derivation), any valid `(payload_hash_A, sig_A)` from a previous response is cryptographically valid as a response to any other pending request. [5](#0-4) 

The `VerifyForeignTransactionRequest` struct used as the pending-map key contains only `(request, domain_id, payload_version)` — no caller identity, no nonce, no commitment to the expected extracted values: [6](#0-5) 

The `args_into_verify_foreign_tx_request` conversion confirms no caller binding is added at submission time: [7](#0-6) 

---

### Impact Explanation

**Impact: High — Forged foreign-chain verification enabling invalid bridge execution.**

The primary use case of `verify_foreign_transaction` is the Omnibridge inbound flow (foreign chain → NEAR), where the MPC network's signed attestation is the sole proof that a foreign transaction finalized. [8](#0-7) 

By substituting `(payload_hash_A, sig_A)` from transaction A as the response to a pending request for transaction B, the attacker causes the MPC contract to fan out a `VerifyForeignTransactionResponse` to all callers of `verify_foreign_transaction(B)` where `payload_hash` commits to transaction A, not B. Any downstream bridge contract that trusts the MPC-signed response without independently recomputing and checking the payload hash binding would accept this as proof that transaction B was verified — enabling unauthorized bridge execution or double-spend conditions.

The SDK's `ForeignChainSignatureVerifier::verify_signature` does check `expected_payload_hash == response.payload_hash`, [9](#0-8)  but this check is optional and client-side — the MPC contract itself does not enforce it, so any bridge contract that omits this check is vulnerable.

---

### Likelihood Explanation

**Likelihood: Medium.**

The attack requires the adversary to be an attested MPC participant (to call `respond_verify_foreign_tx`). [10](#0-9)  This is a Byzantine participant strictly below the signing threshold — within the allowed threat model.

The adversary does not need to collude with other participants or forge a threshold signature. They only need:
1. A valid `(payload_hash_A, sig_A)` from any previously completed `respond_verify_foreign_tx` call — these are permanently public on-chain.
2. A pending `verify_foreign_transaction` request for a different transaction — trivially arranged by submitting one themselves or waiting for a victim's submission.

A single Byzantine node can execute this unilaterally.

---

### Recommendation

In `respond_verify_foreign_tx`, require the responder to also supply the extracted values (`Vec<ExtractedValue>`) alongside the signature. The contract should then:

1. Reconstruct `ForeignTxSignPayload::V1 { request, values }` from the submitted `request` and `values`.
2. Compute `expected_payload_hash = SHA-256(borsh(payload))`.
3. Assert `response.payload_hash == expected_payload_hash` before accepting the response.

This binds the `payload_hash` to the specific `request` being resolved, closing the substitution gap. The `VerifyForeignTransactionResponse` type and the node-side `VerifyForeignTransactionRespondArgs` would need to be extended to carry the extracted values.

---

### Proof of Concept

1. **Setup**: Attested participant P observes a previously completed `respond_verify_foreign_tx` call on-chain for Bitcoin transaction A (`tx_id_A`). The call arguments `(request_A, response_A = {payload_hash_A, sig_A})` are public.

2. **Victim submits**: A bridge contract calls `verify_foreign_transaction` for Bitcoin transaction B (`tx_id_B`, a large inbound transfer). This queues a yield under `request_B` in `pending_verify_foreign_tx_requests`.

3. **Attack**: P calls `respond_verify_foreign_tx(request=request_B, response={payload_hash_A, sig_A})`.

4. **Contract check passes**:
   - `verify_ecdsa_signature(sig_A, payload_hash_A, root_pk)` → valid (sig_A was produced by the MPC network). [11](#0-10) 
   - `pending_verify_foreign_tx_requests.get(&request_B)` → found (victim submitted it). [2](#0-1) 

5. **Result**: All yields queued under `request_B` are resolved with `{payload_hash_A, sig_A}`. The bridge contract receives a `VerifyForeignTransactionResponse` where `payload_hash` commits to transaction A, not B. If the bridge does not re-verify the payload hash binding, it treats this as proof that transaction B was finalized and releases funds — a forged foreign-chain verification.

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

**File:** crates/contract/src/lib.rs (L697-705)
```rust
        let signer = Self::assert_caller_is_signer();

        log!(
            "respond_verify_foreign_tx: signer={}, request={:?}",
            &signer,
            &request
        );

        self.assert_caller_is_attested_participant_and_protocol_active();
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

**File:** docs/foreign-chain-transactions.md (L7-10)
```markdown
This feature lets the MPC network sign payloads only after verifying a specific foreign-chain transaction, so NEAR contracts can react to external chain events without a trusted relayer. Primary use cases:

* Omnibridge inbound flow (foreign chain -> NEAR) where Chain Signatures are required to attest that a foreign transaction finalized successfully.
* Broader chain abstraction: a single MPC network verifies foreign chain state and returns small, typed observations that contracts can interpret.
```

**File:** docs/foreign-chain-transactions.md (L182-189)
```markdown
The 32-byte `msg_hash` that nodes sign is computed as:

```
msg_hash = SHA-256(borsh(ForeignTxSignPayload))
```

Callers select the payload version via `VerifyForeignTransactionRequestArgs::payload_version`.
Borsh field ordering is stability-critical — fields and enum variants must never be reordered.
```

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L124-128)
```rust
pub struct VerifyForeignTransactionRequest {
    pub request: ForeignChainRpcRequest,
    pub domain_id: DomainId,
    pub payload_version: ForeignTxPayloadVersion,
}
```

**File:** crates/contract/src/dto_mapping.rs (L840-848)
```rust
pub fn args_into_verify_foreign_tx_request(
    args: dtos::VerifyForeignTransactionRequestArgs,
) -> dtos::VerifyForeignTransactionRequest {
    dtos::VerifyForeignTransactionRequest {
        domain_id: args.domain_id,
        request: args.request,
        payload_version: args.payload_version,
    }
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
