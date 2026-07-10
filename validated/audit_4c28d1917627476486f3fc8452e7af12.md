### Title
`respond_verify_foreign_tx` Does Not Bind `response.payload_hash` to the Submitted `request` — Cross-Request Signature Replay by a Single Byzantine Leader - (File: `crates/contract/src/lib.rs`)

---

### Summary

`respond_verify_foreign_tx` verifies that the submitted signature is cryptographically valid over `response.payload_hash`, but never checks that `response.payload_hash` is the hash that should be derived from the submitted `request`. A single Byzantine attested participant who has legitimately obtained a threshold signature over hash `H_A` (for foreign-tx request A) can replay that signature as a response to a completely different pending foreign-tx request B by supplying `payload_hash = H_A`. The contract accepts the response, resolves the user's yield, and delivers a forged `VerifyForeignTransactionResponse` to the caller.

---

### Finding Description

The vulnerability class from the external report is a **missing existence/validity check before processing**: `tokenURI` should verify the token exists before returning data. The analog here is that `respond_verify_foreign_tx` should verify that `response.payload_hash` is bound to the `request` before accepting the response — but it does not.

In `respond_verify_foreign_tx`:

```rust
let payload_hash: [u8; 32] = response.payload_hash.0;   // ← caller-supplied, not derived from `request`

near_mpc_signature_verifier::verify_ecdsa_signature(
    signature_response,
    &payload_hash,
    &secp_pk,                                             // root ForeignTx key, no tweak
)
.is_ok()
``` [1](#0-0) 

The contract verifies only that `response.signature` is a valid ECDSA signature over `response.payload_hash` under the root ForeignTx public key. It does **not** verify that `response.payload_hash` equals the hash that honest nodes would compute from `request` (i.e., `SHA-256(borsh(ForeignTxSignPayload { request, extracted_values }))`).

Compare this with the regular `respond` path, where the payload hash is taken directly from the stored `request` object — it is not caller-supplied:

```rust
let payload_hash = request.payload.as_ecdsa().expect("Payload is not ECDSA");
near_mpc_signature_verifier::verify_ecdsa_signature(signature_response, payload_hash, &expected_public_key)
``` [2](#0-1) 

For foreign-tx responses, the `payload_hash` is part of the `VerifyForeignTransactionResponse` DTO and is entirely attacker-controlled: [3](#0-2) 

The `pending_verify_foreign_tx_requests` map is keyed on `VerifyForeignTransactionRequest` (the original query), not on any hash of the expected response. So `resolve_yields_for` will drain the correct yield for request B even when the response carries the hash of a completely different transaction: [4](#0-3) 

---

### Impact Explanation

A single Byzantine attested MPC participant (below the signing threshold) who acts as leader for foreign-tx request A obtains a valid threshold signature σ over `H_A = SHA-256(borsh(ForeignTxSignPayload { request_A, extracted_values_A }))`. They then call:

```
respond_verify_foreign_tx(request_B, { payload_hash: H_A, signature: σ })
```

The contract:
1. Verifies σ is valid over `H_A` under the root ForeignTx key → **passes** (σ is a legitimate threshold signature).
2. Calls `resolve_yields_for(&request_B, serialized_response)` → **resolves** the yield for request B.

The user who submitted request B receives `VerifyForeignTransactionResponse { payload_hash: H_A, signature: σ }` — a response that attests to a completely different foreign-chain transaction. Any downstream bridge logic that trusts the contract's yield-resume result without independently re-verifying `payload_hash` against the expected transaction will accept a forged attestation, enabling invalid bridge execution or double-spend conditions.

The `ForeignChainSignatureVerifier` in the SDK does re-check `payload_hash` against the expected values: [5](#0-4) 

However, the contract itself has already resolved the yield and the user's transaction has completed. Applications that do not call the SDK verifier (or that trust the on-chain result directly) are fully exposed.

---

### Likelihood Explanation

- Any single attested MPC participant can call `respond_verify_foreign_tx`; the contract does not restrict responses to the designated leader for a given request.
- A Byzantine participant needs only to have participated in one legitimate foreign-tx signing session to obtain a reusable signature.
- The attack requires no threshold collusion: one Byzantine node below threshold is sufficient.
- The `ForeignTx` domain uses the root key with no per-request tweak, so any valid ForeignTx signature is universally reusable across all pending foreign-tx requests.

---

### Recommendation

The contract must bind `response.payload_hash` to the `request`. Two complementary approaches:

**Option 1 (preferred):** Include the `VerifyForeignTransactionRequest` (or its hash) in the signed message so that a signature for request A is cryptographically invalid for request B. Nodes should sign `SHA-256(borsh(ForeignTxSignPayload { request, extracted_values }))` where `request` is the full `VerifyForeignTransactionRequest`, and the contract should verify the signature against a hash that commits to the request key.

**Option 2 (contract-side guard):** Store the expected `payload_hash` alongside the pending yield at submission time — but this is not possible today because the hash depends on extracted values not known until nodes query the foreign chain.

**Minimum mitigation:** Require nodes to include the extracted values in the response so the contract can recompute and verify `payload_hash` independently, analogous to how `respond` derives the payload from the stored request rather than trusting the caller.

---

### Proof of Concept

1. User Alice submits `verify_foreign_transaction(request_A)` → yield stored under key `request_A`.
2. User Bob submits `verify_foreign_transaction(request_B)` → yield stored under key `request_B`.
3. Byzantine node N is elected leader for request A. It participates honestly in the threshold protocol; all threshold nodes independently compute `H_A` and sign it. N obtains the complete signature σ over `H_A`.
4. N calls `respond_verify_foreign_tx(request_B, { payload_hash: H_A, signature: σ })`.
5. Contract checks: `verify_ecdsa_signature(σ, H_A, root_foreigntx_key)` → valid ✓.
6. Contract calls `resolve_yields_for(&request_B, ...)` → Bob's yield is resolved with `{ payload_hash: H_A, signature: σ }`.
7. Bob's application receives a `VerifyForeignTransactionResponse` that attests to transaction A, not transaction B. If Bob's bridge logic does not re-verify `payload_hash`, it proceeds with a forged attestation.

The missing check — analogous to `require(_exists(tokenId))` in the ERC-721 report — is:

```rust
// Missing in respond_verify_foreign_tx:
// Verify that response.payload_hash is the correct hash for `request`
// (currently impossible without extracted values, which is itself the design gap)
``` [6](#0-5)

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

**File:** crates/contract/src/lib.rs (L692-754)
```rust
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
