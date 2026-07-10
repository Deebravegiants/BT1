### Title
`respond_verify_foreign_tx` Accepts Unvalidated `payload_hash`, Enabling Cross-Request Replay of Foreign-Chain Verification Signatures - (File: crates/contract/src/lib.rs)

### Summary

The `respond_verify_foreign_tx()` function in the MPC contract verifies that a submitted signature is cryptographically valid over a caller-supplied `payload_hash`, but never validates that `payload_hash` is actually derived from the original pending `request`. A single malicious attested participant can replay a legitimately-computed threshold signature (obtained from on-chain history) against a different pending `verify_foreign_transaction` request, causing the contract to deliver a forged verification response to the waiting caller.

### Finding Description

When a user calls `verify_foreign_transaction(request_B)`, the contract queues a yield keyed on `request_B`. MPC nodes are expected to:
1. Query the foreign chain for `request_B`
2. Extract values
3. Compute `payload_hash_B = SHA256(borsh(ForeignTxSignPayload::V1 { request: request_B, values: extracted_values }))`
4. Produce a threshold signature over `payload_hash_B`
5. Call `respond_verify_foreign_tx(request_B, { payload_hash: payload_hash_B, signature: sig_B })`

The contract's `respond_verify_foreign_tx()` implementation at lines 718–734 only checks:

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

It verifies that `response.signature` is a valid threshold signature over `response.payload_hash`. It does **not** verify that `response.payload_hash` encodes the original `request` parameter. The `payload_hash` is entirely caller-supplied and unconstrained beyond signature validity.

A malicious attested participant can:
1. Observe the on-chain call `respond_verify_foreign_tx(request_A, { payload_hash_A, sig_A })` for a previously completed request_A (all NEAR transactions are public)
2. Extract `{ payload_hash_A, sig_A }` — a valid threshold signature over `payload_hash_A = SHA256(borsh({ request: request_A, values: values_A }))`
3. Submit `respond_verify_foreign_tx(request_B, { payload_hash: payload_hash_A, signature: sig_A })` targeting a different pending `request_B`

The contract will:
- Confirm the caller is an attested participant ✓
- Verify `sig_A` over `payload_hash_A` using the MPC root key ✓ (valid threshold signature)
- Look up the pending yield for `request_B` ✓ (request_B is pending)
- Resolve the yield for `request_B` with `{ payload_hash_A, sig_A }` ✓

The caller of `verify_foreign_transaction(request_B)` receives `{ payload_hash_A, sig_A }` — a response that commits to `request_A`'s foreign-chain data, not `request_B`'s.

### Impact Explanation

The primary use case of `verify_foreign_transaction` is the Omnibridge inbound flow: a bridge contract submits a request to verify that a specific foreign-chain transaction (e.g., a deposit on Ethereum) was finalized, then uses the signed attestation to mint tokens on NEAR. If the bridge contract receives `{ payload_hash_A, sig_A }` in response to its `request_B`, and does not independently re-derive and compare the expected `payload_hash` from `(request_B, expected_values)`, it will accept a signature that attests to a completely different foreign transaction. This enables a malicious attested participant to cause the bridge to process an invalid inbound transfer — a forged foreign-chain verification leading to invalid bridge execution or double-spend conditions.

The `near-mpc-sdk`'s `ForeignChainSignatureVerifier::verify_signature()` does perform this check client-side, but it is an optional off-chain SDK. The on-chain contract — the authoritative enforcement point — provides no such guarantee, leaving any bridge contract that trusts the contract's acceptance as sufficient authorization exposed.

### Likelihood Explanation

The attacker must be an attested MPC participant (requires a valid TEE attestation), but does **not** require threshold collusion or key-share access. The replay material (`payload_hash_A`, `sig_A`) is publicly available from any previously completed `respond_verify_foreign_tx` transaction on-chain. Pending requests are also publicly visible. The barrier is therefore a single compromised or malicious attested node, which is a realistic adversarial condition explicitly within scope (Byzantine participant strictly below the signing threshold).

### Recommendation

The contract should validate that `response.payload_hash` is consistent with the original `request`. Since the contract does not know the extracted values, it cannot fully recompute the hash. The recommended fix is to encode the `request` into the pending yield data at submission time and, upon response, verify that `response.payload_hash` is a hash whose preimage begins with the stored `request` serialization. Alternatively, the response DTO should include the `extracted_values` explicitly, and the contract should recompute and compare `SHA256(borsh(ForeignTxSignPayload::V1 { request, values }))` against `response.payload_hash` before accepting the response.

### Proof of Concept

1. Alice calls `verify_foreign_transaction(request_A)` for Bitcoin `tx_id_A`. The MPC network computes `payload_hash_A` and an honest node submits `respond_verify_foreign_tx(request_A, { payload_hash_A, sig_A })`. This transaction is recorded on-chain.

2. Bob calls `verify_foreign_transaction(request_B)` for Bitcoin `tx_id_B` (a different, potentially fraudulent transaction). `request_B` is now pending in `pending_verify_foreign_tx_requests`.

3. Mallory, a malicious attested participant, reads `{ payload_hash_A, sig_A }` from the on-chain history of step 1.

4. Mallory calls `respond_verify_foreign_tx(request_B, { payload_hash: payload_hash_A, signature: sig_A })`.

5. The contract at line 729 verifies `sig_A` over `payload_hash_A` against the MPC root key — this passes.

6. The contract at line 749 resolves the yield for `request_B` with `{ payload_hash_A, sig_A }`.

7. Bob's bridge contract receives `{ payload_hash_A, sig_A }`. If it does not re-derive the expected `payload_hash` from `(request_B, expected_values)` and compare, it accepts the response as a valid attestation of `tx_id_B` and mints tokens — despite `tx_id_B` never having been verified by the MPC network. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

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

**File:** crates/near-mpc-sdk/src/foreign_chain.rs (L41-89)
```rust
impl ForeignChainSignatureVerifier {
    pub fn verify_signature(
        self,
        response: &VerifyForeignTransactionResponse,
        // TODO(#2232): don't use interface API types for public keys
        public_key: &PublicKey,
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
        let verification_result = match (public_key, &response.signature) {
            (
                PublicKey::Secp256k1(secp256k1_public_key),
                SignatureResponse::Secp256k1(k256_signature),
            ) => near_mpc_signature_verifier::verify_ecdsa_signature(
                k256_signature,
                &expected_payload_hash,
                secp256k1_public_key,
            ),
            (PublicKey::Ed25519(ed25519_public_key), SignatureResponse::Ed25519 { signature }) => {
                near_mpc_signature_verifier::verify_eddsa_signature(
                    signature,
                    expected_payload_hash.as_slice(),
                    ed25519_public_key,
                )
            }
            // TODO(#2234): improve types so these errors can't happen
            (PublicKey::Bls12381(_bls12381_g2_public_key), _) => {
                return Err(VerifyForeignChainError::UnexpectedSignatureScheme);
            }
            _ => return Err(VerifyForeignChainError::UnexpectedSignatureScheme),
        };

        verification_result.map_err(|_| VerifyForeignChainError::SignatureVerificationFailed)
    }
```

**File:** crates/near-mpc-contract-interface/src/types/foreign_chain.rs (L147-150)
```rust
pub struct VerifyForeignTransactionResponse {
    pub payload_hash: Hash256,
    pub signature: SignatureResponse,
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
