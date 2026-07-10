### Title
Single Attested Participant Can Submit Arbitrary CKD Response for `AppPublicKey` Requests — (File: `crates/contract/src/lib.rs`)

### Summary

The `respond_ckd` contract method performs no cryptographic verification of the CKD output when the original request used `CKDAppPublicKey::AppPublicKey`. Any single attested participant — strictly below the signing threshold — can call `respond_ckd` with an arbitrary `CKDResponse` and the contract will accept it, resolve the pending yield, and deliver the forged derived-key material to the requesting user. The threshold guarantee that is supposed to protect CKD operations is entirely absent for this request variant.

### Finding Description

In `respond_ckd` (`crates/contract/src/lib.rs`, lines 653–689), after confirming the caller is an attested participant, the contract branches on the request's `app_public_key` field:

```rust
match &request.app_public_key {
    dtos::CKDAppPublicKey::AppPublicKey(_) => {}          // ← no verification
    dtos::CKDAppPublicKey::AppPublicKeyPV(app_pk) => {
        if !ckd_output_check(&request.app_id, &response, app_pk, &public_key) {
            env::panic_str("CKD output check failed");
        }
    }
}
```

For `AppPublicKeyPV`, `ckd_output_check` cryptographically verifies that the submitted `CKDResponse` is consistent with the BLS12-381 root public key and the user-supplied app public key. For `AppPublicKey`, the branch is a no-op: the response is accepted unconditionally.

Contrast this with `respond` (lines 563–651), where the submitted ECDSA/EdDSA signature is always verified against the expected derived public key before the yield is resolved. That cryptographic check is what enforces the threshold off-chain: a single node cannot produce a valid threshold signature alone, so the contract check acts as a second line of defence. For `respond_ckd` with `AppPublicKey`, that second line of defence is missing entirely. [1](#0-0) [2](#0-1) 

### Impact Explanation

A Byzantine participant (one whose TEE software stack has been compromised or who is otherwise acting maliciously, strictly below the signing threshold) can:

1. Observe a pending `CKDRequest` with `AppPublicKey` variant in the contract state.
2. Craft an arbitrary `CKDResponse` — e.g., a derived key they control or a key that leaks the user's secret.
3. Call `respond_ckd` with that forged response. The contract's only gate is `assert_caller_is_attested_participant_and_protocol_active()`, which the attacker passes.
4. The contract resolves the yield and delivers the forged derived-key material to the user.

The user receives confidential key derivation output that was not produced by the required threshold of participants. This directly matches the allowed critical impact: **"Unauthorized… confidential key derivation output without the required participant authorization."** [3](#0-2) 

### Likelihood Explanation

The attacker must be an attested participant. The scope explicitly lists "Byzantine participant strictly below the signing threshold" as a valid attacker model. A participant whose node software is compromised (e.g., via a supply-chain attack on the Docker image, a software vulnerability in the TEE runtime, or a malicious operator who passes TEE attestation with a patched image before the whitelist is updated) satisfies this model without requiring physical hardware access. The `AppPublicKey` variant is a production-facing API path (it is accepted by `request_app_private_key` and has no deprecation notice), so the attack surface is live. [4](#0-3) 

### Recommendation

Apply the same pattern used for `AppPublicKeyPV`: require a verifiable proof of correctness for every CKD response variant before resolving the yield. If a cryptographic proof cannot be constructed for the `AppPublicKey` variant (because the user does not supply a reference public key), the contract should either:

1. Require a threshold-signed attestation from multiple participants before accepting the response (analogous to how governance votes require a quorum), or
2. Deprecate the `AppPublicKey` variant in favour of `AppPublicKeyPV`, which carries a verifiable proof.

At minimum, add a comment documenting that `AppPublicKey` responses are accepted on TEE-integrity assumptions alone, so that future maintainers understand the weakened security model.

### Proof of Concept

```
1. User calls `request_app_private_key` with:
     app_public_key = AppPublicKey(some_bls_pk)
     domain_id      = <valid CKD domain>
   → Contract queues a CKDRequest and yields.

2. Attacker (single attested participant, account = attacker.near) calls:
     respond_ckd(request = <the queued CKDRequest>,
                 response = CKDResponse { /* arbitrary forged key material */ })

3. Contract execution path:
     assert_caller_is_signer()                          → passes (signer == predecessor)
     assert_caller_is_attested_participant_...()         → passes (attacker is attested)
     match request.app_public_key {
         AppPublicKey(_) => {}                           → no-op, no verification
     }
     resolve_yields_for(...)                             → yield resolved, forged response delivered

4. User's original `request_app_private_key` call returns the attacker-chosen
   CKDResponse, believing it was produced by the threshold of honest participants.
``` [1](#0-0)

### Citations

**File:** crates/contract/src/lib.rs (L468-512)
```rust
    #[payable]
    pub fn request_app_private_key(&mut self, request: CKDRequestArgs) {
        log!(
            "request_app_private_key: predecessor={:?}, request={:?}",
            env::predecessor_account_id(),
            request
        );

        let domain_id: DomainId = request.domain_id;
        let (_, predecessor) = self.check_request_preconditions(
            domain_id,
            DomainPurpose::CKD,
            Gas::from_tgas(self.config.ckd_call_gas_attachment_requirement_tera_gas),
            MINIMUM_CKD_REQUEST_DEPOSIT,
        );

        match &request.app_public_key {
            dtos::CKDAppPublicKey::AppPublicKey(_) => {}
            dtos::CKDAppPublicKey::AppPublicKeyPV(pk) => {
                if !app_public_key_check(pk) {
                    env::panic_str("app public key check failed")
                }
            }
        }

        let request = CKDRequest::new(
            request.app_public_key,
            domain_id,
            &predecessor,
            &request.derivation_path,
        );

        let callback_gas = Gas::from_tgas(
            self.config
                .return_ck_and_clean_state_on_success_call_tera_gas,
        );

        let callback_args = serde_json::to_vec(&(&request,)).unwrap();
        self.enqueue_yield_request(
            method_names::RETURN_CK_AND_CLEAN_STATE_ON_SUCCESS,
            callback_args,
            callback_gas,
            move |this, id| this.add_ckd_request(request, id),
        );
    }
```

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
