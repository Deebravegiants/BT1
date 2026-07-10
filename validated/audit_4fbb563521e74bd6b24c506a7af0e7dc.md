### Title
Unvalidated `payload_hash` in `respond_verify_foreign_tx` Allows Byzantine Leader to Permanently Block Foreign-Chain Verification Requests - (File: `crates/contract/src/lib.rs`)

### Summary

`respond_verify_foreign_tx` verifies that `response.signature` is a valid ECDSA signature over `response.payload_hash`, but never verifies that `response.payload_hash` is actually the hash of the foreign-chain transaction data described in `request`. A Byzantine leader node can compute a valid signature for one pending request and submit it as the response to a different pending request, permanently consuming the victim request with an invalid response.

### Finding Description

The `respond_verify_foreign_tx` function in `crates/contract/src/lib.rs` performs the following checks:

1. Caller is an attested participant
2. Protocol is running
3. `response.signature` is a valid ECDSA signature over `response.payload_hash` using the domain's root public key [1](#0-0) 

What it does **not** check is that `response.payload_hash` is actually `SHA-256(borsh(ForeignTxSignPayload{request: request.request, values: ...}))` — i.e., that the hash is bound to the specific foreign-chain transaction described in `request`. The `payload_hash` field in the response is entirely caller-supplied and unconstrained relative to the `request` content.

The correct binding check is only performed client-side in the SDK's `ForeignChainSignatureVerifier::verify_signature`, which is never called by the contract: [2](#0-1) 

The `args_into_verify_foreign_tx_request` mapping confirms that the stored request key is derived entirely from the user-supplied `request` content, with no hash pre-commitment: [3](#0-2) 

The `VerifyForeignTransactionRequest` stored in `pending_verify_foreign_tx_requests` contains only `{request, domain_id, payload_version}` — no pre-committed `payload_hash`: [4](#0-3) 

### Impact Explanation

**Attack path (single Byzantine leader, strictly below threshold):**

1. User A submits `verify_foreign_transaction` for `tx_id=A` on Bitcoin. User B submits `verify_foreign_transaction` for `tx_id=B` on Bitcoin. Both requests are pending in `pending_verify_foreign_tx_requests`.
2. The Byzantine leader node is selected to lead the threshold signing for request A. It orchestrates honest follower nodes to produce a valid `(payload_hash_A, sig_A)` pair — `payload_hash_A = SHA-256(borsh(ForeignTxSignPayload{request_A, values_A}))`.
3. Instead of submitting `respond_verify_foreign_tx(request=A, response={payload_hash_A, sig_A})`, the Byzantine leader submits `respond_verify_foreign_tx(request=B, response={payload_hash_A, sig_A})`.
4. The contract verifies `sig_A` is valid over `payload_hash_A` using the root public key — this passes, because the signature is cryptographically valid.
5. `pending_requests::resolve_yields_for` looks up request B in the pending map, finds it, and resolves all queued yields with the response `{payload_hash_A, sig_A}`.
6. User B's NEAR transaction receives `VerifyForeignTransactionResponse{payload_hash: payload_hash_A, signature: sig_A}`.
7. User B's downstream contract calls `ForeignChainSignatureVerifier::verify_signature`, which checks `expected_payload_hash_B == response.payload_hash` — this fails because `payload_hash_A ≠ payload_hash_B`.
8. Request B is permanently consumed. User B cannot resubmit and get a valid response because the pending entry has been cleared.

This breaks the request-lifecycle safety invariant: a legitimate pending request is permanently resolved with an invalid response, denying the user any valid attestation for their transaction.

### Likelihood Explanation

The attack requires a single Byzantine participant to be selected as the signing leader for any request. Leader selection is deterministic (lowest participant ID) and predictable. The Byzantine leader participates in the honest threshold signing for one request, then redirects the resulting signature to a different pending request. No threshold collusion is required — the follower nodes participate honestly and never learn the leader has misbehaved. All pending requests are publicly observable in contract state on NEAR.

### Recommendation

The contract should pre-commit to the expected `payload_hash` at request creation time, or at minimum verify that the `payload_hash` in the response is consistent with the `request` content. One approach: at `verify_foreign_transaction` time, store a commitment derived from the request (e.g., `SHA-256(borsh(request))`) alongside the pending yield, and in `respond_verify_foreign_tx`, verify that `response.payload_hash` starts with or is derived from that commitment. Alternatively, require nodes to submit the full `ForeignTxSignPayload` (not just the hash) so the contract can recompute and verify the hash against the stored request.

### Proof of Concept

```
// Setup: two pending requests for different Bitcoin tx_ids
User A: verify_foreign_transaction({request: Bitcoin{tx_id: [0xAA;32], ...}, domain_id: FTX_DOMAIN})
User B: verify_foreign_transaction({request: Bitcoin{tx_id: [0xBB;32], ...}, domain_id: FTX_DOMAIN})

// Byzantine leader computes valid signature for request A
payload_hash_A = SHA-256(borsh(ForeignTxSignPayload{request_A, values_A}))
sig_A = threshold_sign(payload_hash_A)  // valid, produced with honest followers

// Byzantine leader submits sig_A against request B
respond_verify_foreign_tx(
    request = VerifyForeignTransactionRequest{request: Bitcoin{tx_id: [0xBB;32], ...}, domain_id: FTX_DOMAIN},
    response = VerifyForeignTransactionResponse{payload_hash: payload_hash_A, signature: sig_A}
)

// Contract check (lib.rs:726-734): verify_ecdsa_signature(sig_A, payload_hash_A, root_pk) → OK
// Contract resolves request B's yields with {payload_hash_A, sig_A}
// User B receives invalid response; downstream verify_signature fails; request B is permanently gone
``` [5](#0-4)

### Citations

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

**File:** crates/near-mpc-sdk/src/foreign_chain.rs (L47-64)
```rust
    ) -> Result<(), VerifyForeignChainError> {
        let expected_payload = ForeignTxSignPayload::V1(ForeignTxSignPayloadV1 {
            request: self.request,
            values: self.expected_extracted_values,
        });

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

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L124-128)
```rust
pub struct VerifyForeignTransactionRequest {
    pub request: ForeignChainRpcRequest,
    pub domain_id: DomainId,
    pub payload_version: ForeignTxPayloadVersion,
}
```
