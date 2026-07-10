### Title
Missing Cryptographic Output Validation in `respond_ckd` for Legacy `AppPublicKey` Variant Allows Single Attested Participant to Forge CKD Output - (File: crates/contract/src/lib.rs)

### Summary
The `respond_ckd` function in the MPC contract performs no cryptographic verification of the `CKDResponse` when the request uses the legacy `CKDAppPublicKey::AppPublicKey` variant. A single TEE-attested participant (below the signing threshold) can submit an arbitrary `CKDResponse` containing attacker-chosen BLS12-381 points, which the contract accepts and delivers to the requesting user as their confidential derived key. The `AppPublicKeyPV` variant has an explicit `ckd_output_check` guard; the `AppPublicKey` branch has none.

### Finding Description

In `respond_ckd`, the contract branches on the request's `app_public_key` field:

```rust
match &request.app_public_key {
    dtos::CKDAppPublicKey::AppPublicKey(_) => {}   // ← no check at all
    dtos::CKDAppPublicKey::AppPublicKeyPV(app_pk) => {
        if !ckd_output_check(&request.app_id, &response, app_pk, &public_key) {
            env::panic_str("CKD output check failed");
        }
    }
}
``` [1](#0-0) 

For `AppPublicKeyPV`, `ckd_output_check` verifies that the submitted `big_y` and `big_c` are cryptographically consistent with the master BLS12-381 public key and the derivation parameters — a pairing-based proof that the response is the genuine output of the threshold CKD protocol. For `AppPublicKey`, the arm is an empty block: the contract immediately proceeds to `resolve_yields_for`, delivering whatever `CKDResponse` the caller supplied. [2](#0-1) 

The only guards before this branch are:
1. `assert_caller_is_signer()` — predecessor must equal signer (no proxy contracts).
2. `assert_caller_is_attested_participant_and_protocol_active()` — caller must hold a valid TEE attestation and be in the active participant set. [3](#0-2) 

Neither guard verifies that the submitted `CKDResponse` is the output of a threshold computation. For `respond` (ECDSA), the contract cryptographically verifies the signature against the derived public key, so a forged response is rejected even from an attested participant. No equivalent check exists for the `AppPublicKey` CKD path. [4](#0-3) 

The `is_caller_an_attested_participant` check confirms the signer's account key matches a stored TEE attestation, but it does not verify the content of the CKD response in any way. [5](#0-4) 

### Impact Explanation

A single malicious or compromised TEE-attested participant can call `respond_ckd` with an `AppPublicKey` request and supply arbitrary `big_y` (a BLS12-381 G1 point the attacker controls) and `big_c`. The contract resolves all queued yield handles for that request with the forged response. Every user who submitted a `request_app_private_key` for that `(app_id, derivation_path)` receives a derived key that was not produced by the threshold MPC protocol — it was chosen by the attacker. The user has no on-chain means to distinguish a genuine CKD output from a forged one for the `AppPublicKey` variant, because the contract itself performs no verification. This constitutes unauthorized confidential key derivation output delivered without the required threshold-participant authorization, matching the Critical impact class: *"confidential key derivation output without the required participant authorization."*

### Likelihood Explanation

The `AppPublicKey` CKD variant is still exposed in the production ABI and contract code. Any single TEE-attested participant — one node out of the full participant set, well below the signing threshold — can exploit this. The attacker does not need to compromise the threshold, collude with other participants, or break the TEE hardware. They only need to be an active, attested participant and submit a crafted `respond_ckd` transaction directly from their own account (satisfying `assert_caller_is_signer`). The `AppPublicKeyPV` variant's guard demonstrates the developers are aware that output verification is necessary; its absence on the `AppPublicKey` branch is an oversight, not a deliberate design choice.

### Recommendation

Add a cryptographic output check for the `AppPublicKey` variant analogous to the one already present for `AppPublicKeyPV`. Specifically, verify that the submitted `big_y` is the correct BLS12-381 G1 point derived from the master public key using the request's `app_id` and derivation path, before calling `resolve_yields_for`. If a lightweight on-chain check is not feasible for the legacy variant, the `AppPublicKey` path should be deprecated and removed, forcing all callers to use `AppPublicKeyPV`.

### Proof of Concept

1. User Alice calls `request_app_private_key` with `CKDAppPublicKey::AppPublicKey(alice_bls_pk)` and `derivation_path = "alice/wallet"`. The contract queues a yield and stores the `CKDRequest` in `pending_ckd_requests`.
2. Attacker Eve is a TEE-attested participant. She observes Alice's pending request on-chain.
3. Eve generates an arbitrary BLS12-381 G1 point `evil_big_y` (a key she controls) and a matching `evil_big_c`.
4. Eve calls `respond_ckd(alice_ckd_request, CKDResponse { big_y: evil_big_y, big_c: evil_big_c })` directly from her own account.
5. The contract passes `assert_caller_is_signer()` and `assert_caller_is_attested_participant_and_protocol_active()`. The `AppPublicKey` branch executes the empty arm — no check. `resolve_yields_for` resumes Alice's yield with Eve's forged response.
6. Alice's transaction resolves with `CKDResponse { big_y: evil_big_y, big_c: evil_big_c }`. Alice believes `evil_big_y` is her MPC-derived public key. Eve controls the corresponding private key. [6](#0-5)

### Citations

**File:** crates/contract/src/lib.rs (L586-644)
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
                dtos::SignatureResponse::Ed25519 { signature },
                PublicKeyExtended::Ed25519 {
                    edwards_point: public_key_edwards_point,
                    ..
                },
            ) => {
                let derived_public_key_edwards_point = derive_public_key_edwards_point_ed25519(
                    &public_key_edwards_point,
                    &request.tweak,
                );
                let derived_public_key_32_bytes =
                    dtos::Ed25519PublicKey::from(derived_public_key_edwards_point.compress());

                let message = request.payload.as_eddsa().expect("Payload is not EdDSA");

                near_mpc_signature_verifier::verify_eddsa_signature(
                    signature,
                    message,
                    &derived_public_key_32_bytes,
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

**File:** crates/contract/src/lib.rs (L653-689)
```rust
    #[handle_result]
    pub fn respond_ckd(&mut self, request: CKDRequest, response: CKDResponse) -> Result<(), Error> {
        let signer = Self::assert_caller_is_signer();
        log!("respond_ckd: signer={}, request={:?}", &signer, &request);

        if !self.protocol_state.is_running_or_resharing() {
            return Err(InvalidState::ProtocolStateNotRunning.into());
        }

        if !self.accept_requests {
            return Err(TeeError::TeeValidationFailed.into());
        }

        self.assert_caller_is_attested_participant_and_protocol_active();

        let PublicKeyExtended::Bls12381 {
            public_key: dtos::PublicKey::Bls12381(public_key),
        } = self.public_key_extended(request.domain_id)?
        else {
            env::panic_str("Domain is not compatible with CKD (expected Bls12381 curve)");
        };

        match &request.app_public_key {
            dtos::CKDAppPublicKey::AppPublicKey(_) => {}
            dtos::CKDAppPublicKey::AppPublicKeyPV(app_pk) => {
                if !ckd_output_check(&request.app_id, &response, app_pk, &public_key) {
                    env::panic_str("CKD output check failed");
                }
            }
        }

        pending_requests::resolve_yields_for(
            &mut self.pending_ckd_requests,
            &request,
            serde_json::to_vec(&response).unwrap(),
        )
    }
```

**File:** crates/contract/src/tee/tee_state.rs (L469-498)
```rust
    pub(crate) fn is_caller_an_attested_participant(
        &self,
        participants: &Participants,
    ) -> Result<(), AttestationCheckError> {
        let signer_account_pk = env::signer_account_pk();
        let signer_id = env::signer_account_id();

        let info = participants
            .info(&signer_id)
            .ok_or(AttestationCheckError::CallerNotParticipant)?;

        let attestation = self
            .stored_attestations
            .get(&info.tls_public_key)
            .ok_or(AttestationCheckError::AttestationNotFound)?;

        if attestation.node_id.account_id != signer_id {
            return Err(AttestationCheckError::AttestationOwnerMismatch);
        }

        // Stored account keys are Ed25519 by construction; a non-Ed25519
        // signer necessarily mismatches.
        let signer_ed25519 = Ed25519PublicKey::try_from(&signer_account_pk)
            .map_err(|_| AttestationCheckError::AttestationKeyMismatch)?;
        if attestation.node_id.account_public_key != signer_ed25519 {
            return Err(AttestationCheckError::AttestationKeyMismatch);
        }

        Ok(())
    }
```
