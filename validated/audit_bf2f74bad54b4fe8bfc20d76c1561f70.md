### Title
`respond_verify_foreign_tx` Does Not Bind `response.payload_hash` to the Submitted `request` — (File: `crates/contract/src/lib.rs`)

### Summary

`respond_verify_foreign_tx` verifies only that the submitted signature is cryptographically valid over the submitted `payload_hash` using the domain's root public key. It does **not** verify that `payload_hash` is the canonical hash of `(request, extracted_values)` for the specific `request` key being resolved. A single Byzantine attested participant can therefore resolve any pending `verify_foreign_transaction` yield with a valid `(payload_hash, signature)` pair harvested from a completely different, previously-completed request, delivering a forged foreign-chain attestation to the caller.

---

### Finding Description

In `respond_verify_foreign_tx` the contract performs three checks:

1. Caller is an attested participant (`assert_caller_is_attested_participant_and_protocol_active`).
2. The ECDSA signature in `response` is valid over `response.payload_hash` under the **root** public key of the domain (no tweak applied).
3. The `request` key exists in `pending_verify_foreign_tx_requests`. [1](#0-0) 

What is **absent** is any check that `response.payload_hash` encodes the specific `request` that was submitted. The `payload_hash` is defined as `hash(ForeignTxSignPayloadV1 { request: ForeignChainRpcRequest, values: Vec<ExtractedValue> })`. [2](#0-1) 

Because the contract never reconstructs or checks this hash, any `(payload_hash_B, signature_B)` pair that was legitimately produced by the MPC network for **any** prior request B can be replayed into the yield slot of a completely different pending request A.

The contrast with `respond` (for plain `sign`) is instructive: there, the signature is verified against the **derived** key (root key + request-specific tweak), which cryptographically binds the response to the exact request. `respond_verify_foreign_tx` uses the root key with no tweak and no payload-hash binding. [3](#0-2) 

---

### Impact Explanation

**Impact class:** High — Forged foreign-chain verification / invalid bridge execution.

A Byzantine attested participant (single node, strictly below the signing threshold) can:

1. Submit a legitimate `verify_foreign_transaction(request_B)` (e.g., "verify Bitcoin tx Y").
2. Wait for the MPC network to produce and publish `(payload_hash_B, signature_B)` on-chain for request B. This data is public once the yield resolves.
3. While a victim's `verify_foreign_transaction(request_A)` (e.g., "verify Bitcoin tx X") is pending, call `respond_verify_foreign_tx(request_A, { payload_hash: payload_hash_B, signature: signature_B })`.
4. The contract accepts the call: `signature_B` is a valid MPC root-key signature over `payload_hash_B`, and `request_A` is present in `pending_verify_foreign_tx_requests`.
5. The victim's yield is resolved with `{ payload_hash_B, signature_B }` — a valid MPC attestation, but for tx Y, not tx X.

The victim's bridge contract receives a genuine MPC signature and may authorize a bridge action (e.g., mint tokens) believing tx X was verified, when in fact the MPC network only ever verified tx Y. This enables double-spend or invalid bridge execution.

Additionally, the victim's actual request (request_A) is permanently consumed: the yield is drained, so the MPC network will never produce a legitimate response for it. [4](#0-3) 

---

### Likelihood Explanation

**Likelihood: Medium.**

- The attacker must be an attested participant — a meaningful barrier, but explicitly within the "Byzantine participant strictly below the signing threshold" attacker model.
- The attacker needs a valid `(payload_hash, signature)` pair from the MPC network. This is trivially obtained by submitting any legitimate `verify_foreign_transaction` request and reading the on-chain response once it resolves — no threshold collusion required.
- The victim's request must be pending at the time of the attack. An attacker can time this by monitoring the mempool or the contract's `pending_verify_foreign_tx_requests` view.
- No special cryptographic capability is needed beyond being an attested participant.

---

### Recommendation

The contract must verify that `response.payload_hash` is consistent with the submitted `request`. Since the contract does not receive the extracted values, it cannot reconstruct the full `payload_hash`. Two complementary mitigations:

1. **Include the `ForeignChainRpcRequest` hash in the `payload_hash` preimage in a verifiable way**, and have the contract verify that the `payload_hash` commits to the correct `request`. For example, define `payload_hash = hash(version || hash(request) || hash(extracted_values))` and have the contract verify the `hash(request)` component by hashing the `request` field it already holds.

2. **Alternatively, have the contract store the expected `payload_hash` prefix** (i.e., `hash(request)`) at request submission time and verify it matches the prefix of the submitted `payload_hash` at response time.

3. As a defense-in-depth measure, the `near-mpc-sdk`'s `ForeignChainSignatureVerifier::verify_signature` should be documented as **mandatory** for all callers, and the contract should emit the full `request` alongside the response so callers can verify the binding. [5](#0-4) 

---

### Proof of Concept

```
// Setup: attacker is an attested participant; victim has a pending request.

// Step 1: Attacker submits a legitimate request for tx Y (Bitcoin).
attacker -> contract.verify_foreign_transaction({
    domain_id: foreign_tx_domain,
    request: BitcoinRpcRequest { tx_id: TX_Y, ... },
    payload_version: V1,
})
// MPC network verifies tx Y, produces (payload_hash_B, signature_B).
// These are published on-chain when the yield resolves.

// Step 2: Victim submits a request for tx X (Bitcoin).
victim -> contract.verify_foreign_transaction({
    domain_id: foreign_tx_domain,
    request: BitcoinRpcRequest { tx_id: TX_X, ... },
    payload_version: V1,
})
// request_A is now pending in pending_verify_foreign_tx_requests.

// Step 3: Attacker reads (payload_hash_B, signature_B) from chain history.
// Attacker calls respond_verify_foreign_tx with request_A but response_B.
attacker -> contract.respond_verify_foreign_tx(
    request = { domain_id, request: BitcoinRpcRequest { tx_id: TX_X, ... }, ... },  // request_A
    response = { payload_hash: payload_hash_B, signature: signature_B },             // response for TX_Y
)

// Contract checks:
// 1. assert_caller_is_attested_participant_and_protocol_active() -> PASS (attacker is attested)
// 2. verify_ecdsa_signature(signature_B, payload_hash_B, root_pk) -> PASS (valid MPC signature)
// 3. pending_verify_foreign_tx_requests.contains(request_A) -> PASS (victim's request is pending)
// 4. [MISSING] payload_hash_B == hash(request_A, extracted_values_A) -> NOT CHECKED

// Result: victim's yield is resolved with (payload_hash_B, signature_B).
// Victim receives a valid MPC signature attesting to TX_Y, not TX_X.
// Victim's bridge contract may authorize a bridge action for TX_X based on TX_Y's attestation.
``` [6](#0-5) [4](#0-3)

### Citations

**File:** crates/contract/src/lib.rs (L586-610)
```rust
        let signature_is_valid = match (&response, public_key) {
            (
                dtos::SignatureResponse::Secp256k1(signature_response),
                PublicKeyExtended::Secp256k1 { near_public_key },
            ) => {
                // generate the expected public key
                let secp_pk = dtos::Secp256k1PublicKey::try_from(&near_public_key)
                    .expect("Secp256k1 variant always has a secp256k1 key");
                let affine = *k256::PublicKey::try_from(&secp_pk)
                    .expect("stored key is always valid")
                    .as_affine();
                let expected_public_key =
                    derive_key_secp256k1(&affine, &request.tweak).map_err(RespondError::from)?;

                let payload_hash = request.payload.as_ecdsa().expect("Payload is not ECDSA");

                // Check the signature is correct
                near_mpc_signature_verifier::verify_ecdsa_signature(
                    signature_response,
                    payload_hash,
                    &expected_public_key,
                )
                .is_ok()
            }
            (
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

**File:** crates/node/src/providers/verify_foreign_tx/sign.rs (L30-47)
```rust
fn build_signature_request(
    request: &VerifyForeignTxRequest,
    foreign_tx_payload: &dtos::ForeignTxSignPayload,
) -> anyhow::Result<SignatureRequest> {
    let payload_hash: [u8; ECDSA_PAYLOAD_SIZE_BYTES] =
        foreign_tx_payload.compute_msg_hash()?.into();
    let payload_bytes: BoundedVec<u8, ECDSA_PAYLOAD_SIZE_BYTES, ECDSA_PAYLOAD_SIZE_BYTES> =
        payload_hash.into();

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
