### Title
Unvalidated `payload_hash` in `respond_verify_foreign_tx` Enables Cross-Request Replay by a Single Byzantine Participant - (File: `crates/contract/src/lib.rs`)

### Summary

`respond_verify_foreign_tx` verifies only that the node-supplied `response.payload_hash` is correctly signed by the root key, but never checks that `payload_hash` actually corresponds to the original pending request's transaction data. A single attested participant below the signing threshold can replay a valid `(payload_hash, signature)` pair from any past response to permanently resolve a different pending foreign-tx request with fabricated data, bypassing the foreign-chain verification guarantee.

### Finding Description

The `respond_verify_foreign_tx` function in `crates/contract/src/lib.rs` performs the following checks:

1. Caller is an attested participant.
2. Protocol is running.
3. `response.signature` is a valid ECDSA signature over `response.payload_hash` under the root public key.
4. `request` exists in `pending_verify_foreign_tx_requests`. [1](#0-0) 

What it does **not** check is that `response.payload_hash` is the canonical hash of `ForeignTxSignPayload{request, extracted_values}` for the specific pending `request`. The `payload_hash` is taken directly from the node-supplied response without any reconstruction or comparison against the stored request. [2](#0-1) 

By contrast, the regular `respond` function derives `payload_hash` from `request.payload` (which is part of the stored request key), so the signature is always verified against the correct payload: [3](#0-2) 

The `ForeignTxSignPayload` is defined as `{request: ForeignChainRpcRequest, values: Vec<ExtractedValue>}` and its hash is `SHA-256(borsh(payload))`. The contract stores only the `request` portion in the pending map; the `extracted_values` are determined off-chain by nodes querying the foreign chain. Because the contract cannot reconstruct the expected hash without the extracted values, it accepts whatever `payload_hash` the responding node provides, as long as the signature over it is valid. [4](#0-3) 

The SDK-side verifier (`ForeignChainSignatureVerifier::verify_signature`) does perform this check — it reconstructs the expected hash and compares — but this check lives in the **caller's bridge contract**, not in the MPC contract itself. [5](#0-4) 

### Impact Explanation

A single Byzantine attested participant (strictly below the signing threshold) can:

1. Observe any previously-submitted valid `respond_verify_foreign_tx` call on-chain, extracting `(payload_hash_old, signature_old)` — both are public.
2. When a new `verify_foreign_transaction` request is pending for a different transaction (`tx_id_B`), call `respond_verify_foreign_tx(request={tx_id_B, ...}, response={payload_hash: payload_hash_old, signature: signature_old})`.
3. The contract verifies `signature_old` is valid for `payload_hash_old` under the root key — it is — and resolves the pending yield for `tx_id_B` with the fabricated response.
4. The pending request is permanently consumed and removed from `pending_verify_foreign_tx_requests`. [6](#0-5) 

Bridge contracts that do not use `ForeignChainSignatureVerifier` (or implement their own verification) may accept the response and execute an invalid bridge action (e.g., releasing funds for a transaction that was never actually verified on the foreign chain). Bridge contracts that do validate the `payload_hash` will reject the response, but the pending request is already consumed — the user cannot receive a correct response without resubmitting.

This maps directly to the external report's pattern: an authorized actor (attested participant, analogous to the "authorized borrower") can take an action (resolve a pending request) without the required constraint (payload integrity check), corrupting the request lifecycle and potentially enabling invalid bridge execution.

### Likelihood Explanation

- Requires only **one** Byzantine attested participant — strictly below the signing threshold.
- No cryptographic forgery is needed; the attacker replays a legitimately-produced signature that is already public on-chain.
- The attacker must be an attested participant (TEE-attested node), which is a realistic Byzantine assumption in the threat model.
- The attack is repeatable for every pending `verify_foreign_transaction` request.

### Recommendation

The contract should verify that `response.payload_hash` is consistent with the stored `request`. Since the contract cannot reconstruct the full `ForeignTxSignPayload` (it lacks `extracted_values`), two mitigations are possible:

1. **Commit-then-reveal**: Have nodes commit to `payload_hash` via a threshold vote before any single node can call `respond_verify_foreign_tx`. Only accept a `payload_hash` that has been agreed upon by at least `t` participants.
2. **Include extracted values in the response and validate on-chain**: Accept `extracted_values` as part of the response, reconstruct `payload_hash = SHA-256(borsh({request, extracted_values}))` inside the contract, and verify the signature against the reconstructed hash rather than the node-supplied one. This eliminates the trust in the node-provided `payload_hash` entirely.

Option 2 mirrors how `respond` handles regular sign requests — the payload is always derived from the stored request, never from the node's response.

### Proof of Concept

```rust
// Step 1: Observe a past valid response on-chain for request_A
// (payload_hash_old, signature_old) are public in the transaction history.

// Step 2: A new request for tx_id_B is pending.
// A single Byzantine attested participant calls:
contract.respond_verify_foreign_tx(
    request = VerifyForeignTransactionRequest {
        tx_id: tx_id_B,          // the new pending request
        extractors: [...],
        domain_id: 0,
        payload_version: V1,
    },
    response = VerifyForeignTransactionResponse {
        payload_hash: payload_hash_old,   // replayed from a past response for tx_id_A
        signature: signature_old,          // valid signature for payload_hash_old
    },
);
// The contract accepts: signature_old is valid for payload_hash_old under the root key.
// The pending yield for tx_id_B is resolved with fabricated data.
// The user's bridge contract receives payload_hash_old instead of the correct hash for tx_id_B.
// If the bridge does not validate payload_hash, it executes an invalid bridge action.
// If it does validate, the user's transaction fails and the request slot is permanently consumed.
``` [7](#0-6)

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
