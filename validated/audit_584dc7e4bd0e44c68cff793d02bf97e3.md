### Title
Unverified CKD Response for `AppPublicKey` Variant Allows Single Byzantine Participant to Forge Confidential Key Derivation Output — (`File: crates/contract/src/lib.rs`)

---

### Summary

`respond_ckd` in the MPC contract performs cryptographic output verification only for the `AppPublicKeyPV` variant of a CKD request. For the `AppPublicKey` (legacy, privately-verifiable) variant, the match arm is an empty no-op. A single attested participant can therefore call `respond_ckd` with a completely arbitrary `CKDResponse` for any pending `AppPublicKey` request, and the contract will accept it, resolve the yield, and deliver the forged key material to the user — bypassing the threshold-signature requirement entirely.

---

### Finding Description

`respond_ckd` retrieves the BLS12-381 public key for the domain and then branches on the request's `app_public_key` variant:

```rust
match &request.app_public_key {
    dtos::CKDAppPublicKey::AppPublicKey(_) => {}          // ← no check at all
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
``` [1](#0-0) 

For `AppPublicKeyPV`, `ckd_output_check` verifies that the response `(big_y, big_c)` is a valid encryption of the derived key under the network's BLS master key and the user's `(pk1, pk2)` pair. For `AppPublicKey`, there is no analogous check — the response bytes are passed directly to `resolve_yields_for` and returned to the caller.

The `AppPublicKey` variant is the default/legacy format and is the one used in the contract README's primary example: [2](#0-1) 

The existing unit test `respond_ckd__should_succeed_when_response_is_valid_and_request_exists` confirms the absence of any check: it passes `big_y: [1u8; 48], big_c: [2u8; 48]` — bytes that are not a valid BLS12-381 point, let alone a valid CKD output — and the call succeeds: [3](#0-2) 

By contrast, `respond` (for ECDSA/EdDSA signatures) always verifies the signature against the derived public key before resolving: [4](#0-3) 

---

### Impact Explanation

A single Byzantine participant (attested, below threshold) can call `respond_ckd` with an arbitrary `CKDResponse` for any pending `AppPublicKey` CKD request. The contract resolves the yield and delivers the forged output to the user. The user's application decrypts attacker-controlled key material instead of the genuine threshold-derived key. This constitutes **unauthorized confidential key derivation output without the required participant authorization** — the threshold requirement (t-of-n) is completely bypassed for the `AppPublicKey` variant.

---

### Likelihood Explanation

Any single attested participant can trigger this. The `AppPublicKey` variant is the legacy default and is the format most existing integrations use. The attacker only needs to:
1. Monitor the chain for pending `AppPublicKey` CKD requests.
2. Call `respond_ckd` with a forged `CKDResponse` before the honest nodes respond.

No collusion, no key material, and no special privilege beyond being an attested participant is required.

---

### Recommendation

Apply the same cryptographic output verification to `AppPublicKey` requests that is already applied to `AppPublicKeyPV`. For the privately-verifiable variant, the check must use only the G1 public key (`pk1`) and the network's BLS master key. Concretely, add a `ckd_output_check` (or an equivalent private-verifiability check) for the `AppPublicKey` arm, or reject `AppPublicKey` requests at the `respond_ckd` level and require all new requests to use `AppPublicKeyPV`.

---

### Proof of Concept

1. User submits `request_app_private_key` with `app_public_key = AppPublicKey(some_g1_point)`. The request is stored in `pending_ckd_requests`.
2. A single Byzantine participant calls `respond_ckd(request, CKDResponse { big_y: [0u8; 48], big_c: [0u8; 48] })`.
3. The `AppPublicKey` match arm executes `{}` — no verification.
4. `resolve_yields_for` is called; the forged response is written into the yield and returned to the user.
5. The user receives attacker-controlled `(big_y, big_c)` as their confidential key derivation output, decrypting to garbage or attacker-chosen key material.
6. The honest t-of-n threshold protocol was never consulted. [5](#0-4)

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

**File:** crates/contract/src/lib.rs (L3424-3440)
```rust
        let response = CKDResponse {
            big_y: dtos::Bls12381G1PublicKey([1u8; 48]),
            big_c: dtos::Bls12381G1PublicKey([2u8; 48]),
        };

        with_active_participant_and_attested_context(&contract);

        match contract.respond_ckd(ckd_request.clone(), response.clone()) {
            Ok(_) => {
                contract
                    .return_ck_and_clean_state_on_success(ckd_request.clone(), Ok(response))
                    .detach();

                assert!(contract.get_pending_ckd_request(&ckd_request).is_none(),);
            }
            Err(_) => panic!("respond_ckd should not fail"),
        }
```

**File:** crates/contract/README.md (L119-120)
```markdown
  - **Privately verifiable** (legacy): a single G1 point, e.g. `"bls12381g1:<base58>"` or `{"AppPublicKey": "bls12381g1:<base58>"}`.
  - **Publicly verifiable**: a pair of points `(pk1, pk2) = (a·G1, a·G2)`, passed as `{"AppPublicKeyPV": {"pk1": "bls12381g1:<base58>", "pk2": "bls12381g2:<base58>"}}`. This allows anyone to verify the encrypted result on-chain without the app's secret key.
```
