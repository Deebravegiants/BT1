### Title
Missing CKD Output Verification for Legacy `AppPublicKey` Variant Allows Single Attested Participant to Forge Derived Key - (File: `crates/contract/src/lib.rs`)

### Summary

`respond_ckd()` enforces a cryptographic output check (`ckd_output_check`) only for the `AppPublicKeyPV` variant of a CKD request. The legacy `AppPublicKey` variant receives no such check. A single attested participant — strictly below the signing threshold — can call `respond_ckd()` with an arbitrary `CKDResponse` for any pending legacy-variant request and the contract will accept and deliver it to the user without any verification.

### Finding Description

`respond_ckd()` in `crates/contract/src/lib.rs` branches on the request's `app_public_key` variant:

```rust
match &request.app_public_key {
    dtos::CKDAppPublicKey::AppPublicKey(_) => {}   // ← no check at all
    dtos::CKDAppPublicKey::AppPublicKeyPV(app_pk) => {
        if !ckd_output_check(&request.app_id, &response, app_pk, &public_key) {
            env::panic_str("CKD output check failed");
        }
    }
}
```

For `AppPublicKeyPV`, `ckd_output_check` uses a BLS12-381 pairing check to prove that `(big_y, big_c)` is a correctly-derived output under the master public key and the user's app key pair. For `AppPublicKey` (the legacy, still-supported variant), the arm is an empty block — the response values `big_y` and `big_c` are serialised and delivered to the user via `pending_requests::resolve_yields_for` with zero cryptographic validation.

By contrast, `respond()` always verifies the ECDSA/EdDSA signature before resolving the yield, and `respond_verify_foreign_tx()` always verifies the signature against the root public key. `respond_ckd()` with `AppPublicKey` is the only respond path that skips output verification entirely.

The caller still passes `assert_caller_is_signer()` and `assert_caller_is_attested_participant_and_protocol_active()`, so the attacker must be a single attested participant — but that is well below the signing threshold required to produce a legitimate CKD output.

### Impact Explanation

A single malicious attested participant can:

1. Observe any pending `CKDRequest` with `AppPublicKey` in `pending_ckd_requests`.
2. Construct a `CKDResponse` with arbitrary `big_y` and `big_c` values — for example, `big_y = attacker_scalar × G` where the attacker knows `attacker_scalar`.
3. Call `respond_ckd(request, forged_response)`. The contract accepts it, resolves the yield, and delivers the forged key material to the user.
4. The user receives a "derived key" that is not derived from the MPC master secret. The attacker knows the scalar behind `big_y`, so they know the user's supposed private key.

Any data the user subsequently encrypts to or signs with this forged key is compromised. This is a direct, unilateral substitution of the confidential key derivation output by a single participant acting below the threshold — matching the "Critical: confidential key derivation output without the required participant authorization" impact class.

### Likelihood Explanation

The `AppPublicKey` variant is still accepted by the contract (it appears in the ABI snapshot and the README explicitly documents it as the legacy path). Any attested participant who is currently in the participant set can exploit this. No threshold cooperation, no key material, and no special tooling is required beyond the ability to call `respond_ckd` — which every attested participant already has. The attacker only needs to race the honest nodes to respond first for a target request.

### Recommendation

Apply `ckd_output_check` (or an equivalent verification) to the `AppPublicKey` arm as well. If a cryptographic check analogous to the PV pairing check cannot be constructed for the legacy single-point variant, the contract should at minimum verify that `big_y` lies on the correct curve and is consistent with the master public key and the request's derivation tweak. Alternatively, deprecate and remove the `AppPublicKey` variant entirely, requiring all callers to migrate to `AppPublicKeyPV`.

### Proof of Concept

```
// Attacker is an attested participant.
// Alice has a pending CKDRequest with AppPublicKey variant.

// 1. Attacker picks a scalar they control.
let attacker_scalar = random_scalar();
let forged_big_y = G1::generator() * attacker_scalar;
let forged_big_c = G1::generator() * attacker_scalar; // arbitrary

// 2. Attacker calls respond_ckd with forged values.
contract.respond_ckd(
    alice_ckd_request,          // AppPublicKey variant — no output check
    CKDResponse { big_y: forged_big_y, big_c: forged_big_c },
);

// 3. Contract resolves Alice's yield with the forged response.
// Alice receives forged_big_y as her "derived key".
// Attacker knows attacker_scalar, so they know Alice's "private key".
```

The root cause is at: [1](#0-0) 

The `AppPublicKeyPV` check that is absent for the legacy variant: [1](#0-0) 

The `respond()` function that correctly verifies its output before resolving: [2](#0-1) 

The `respond_ckd()` function in full: [3](#0-2)

### Citations

**File:** crates/contract/src/lib.rs (L563-651)
```rust
    #[handle_result]
    pub fn respond(
        &mut self,
        request: SignatureRequest,
        response: dtos::SignatureResponse,
    ) -> Result<(), Error> {
        let signer = Self::assert_caller_is_signer();

        log!("respond: signer={}, request={:?}", &signer, &request);

        self.assert_caller_is_attested_participant_and_protocol_active();

        if !self.protocol_state.is_running_or_resharing() {
            return Err(InvalidState::ProtocolStateNotRunning.into());
        }

        if !self.accept_requests {
            return Err(TeeError::TeeValidationFailed.into());
        }

        let domain = request.domain_id;
        let public_key = self.public_key_extended(domain)?;

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

        pending_requests::resolve_yields_for(
            &mut self.pending_signature_requests,
            &request,
            serde_json::to_vec(&response).unwrap(),
        )
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
