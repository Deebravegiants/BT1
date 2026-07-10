Let me check how `resolve_yields_for` works and whether there's any threshold enforcement, plus how the CKD response is consumed.

### Title
Single Byzantine Attested Participant Can Forge CKD Output for `AppPublicKey` Variant — (`crates/contract/src/lib.rs`)

---

### Summary

The `respond_ckd` function performs no cryptographic verification of the `CKDResponse` when the request uses the `CKDAppPublicKey::AppPublicKey` (non-PV) variant. A single attested MPC participant can submit an arbitrary `big_y` / `big_c` pair, the contract accepts it unconditionally, and the yield is resolved with the forged output. This breaks the threshold-security model for the non-PV CKD path.

---

### Finding Description

`respond_ckd` dispatches on the request variant:

```rust
match &request.app_public_key {
    dtos::CKDAppPublicKey::AppPublicKey(_) => {}          // ← no check at all
    dtos::CKDAppPublicKey::AppPublicKeyPV(app_pk) => {
        if !ckd_output_check(&request.app_id, &response, app_pk, &public_key) {
            env::panic_str("CKD output check failed");
        }
    }
}
``` [1](#0-0) 

For the `AppPublicKeyPV` arm, `ckd_output_check` enforces the pairing equation `e(big_c, g2) = e(big_y, app_pk2) · e(H(pk‖app_id), msk·g2)`, which cryptographically binds the response to the MPC network secret key and the caller's `app_id`. [2](#0-1) 

For the `AppPublicKey` arm the body is empty. After the match, `resolve_yields_for` is called unconditionally with whatever `response` the participant supplied: [3](#0-2) 

For `respond_sign`, the threshold is enforced implicitly: only a cryptographically valid signature (which requires threshold computation) passes the on-chain ECDSA/EdDSA check. No analogous binding exists for the `AppPublicKey` CKD path. [4](#0-3) 

---

### Impact Explanation

The attacker is a single Byzantine attested participant. They observe a pending CKD request with the `AppPublicKey` variant, then call `respond_ckd` with self-chosen `big_y = a·G` and `big_c = b·G` for arbitrary scalars `a, b` they know. The contract resolves the yield with `(big_y, big_c)`. The caller receives a `CKDResponse` that is not bound to the MPC network secret key. Because the attacker chose `a` and `b`, they know the discrete logs and can compute any secret the caller derives from `big_c`. This is unauthorized confidential key derivation output delivered without the required MPC threshold computation.

---

### Likelihood Explanation

The `AppPublicKey` variant is a production code path (not behind a feature flag, exercised in e2e tests). Any single attested participant who turns Byzantine can race to call `respond_ckd` before the honest participants do. The guard `assert_caller_is_attested_participant_and_protocol_active` only requires attestation, not a threshold quorum. [5](#0-4) 

---

### Recommendation

Apply `ckd_output_check` to the `AppPublicKey` arm as well, or reject `AppPublicKey` requests at the contract level and require callers to use `AppPublicKeyPV`. If the non-PV variant must be retained for backward compatibility, the contract must enforce a threshold quorum (e.g., require `t` matching responses before resolving the yield) rather than resolving on the first response.

---

### Proof of Concept

```rust
// In a sandbox/unit test:
// 1. Submit a CKD request with AppPublicKey variant.
let request = CKDRequest::new(
    CKDAppPublicKey::AppPublicKey(Bls12381G1PublicKey([0x80, 0, ..., 0])),
    domain_id,
    &"alice.near".parse().unwrap(),
    "path",
);
contract.request_ckd(request.clone());

// 2. As a single attested participant, respond with arbitrary bytes.
let forged = CKDResponse {
    big_y: Bls12381G1PublicKey([1u8; 48]),
    big_c: Bls12381G1PublicKey([2u8; 48]),
};
// Contract accepts without any pairing check:
contract.respond_ckd(request, forged).unwrap();

// 3. Assert the yield was resolved with the forged output.
// The caller receives big_c = [2u8;48], chosen entirely by the attacker.
```

The `AppPublicKey` arm at line 676 is a no-op, so the forged response passes straight through to `resolve_yields_for`. [6](#0-5)

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

**File:** crates/contract/src/lib.rs (L654-666)
```rust
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
```

**File:** crates/contract/src/lib.rs (L675-689)
```rust
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

**File:** crates/contract/src/primitives/ckd.rs (L80-102)
```rust
pub(crate) fn ckd_output_check(
    app_id: &dtos::CkdAppId,
    output: &CKDResponse,
    app_public_key: &dtos::CKDAppPublicKeyPV,
    public_key: &dtos::Bls12381G2PublicKey,
) -> bool {
    let big_c = env::bls12381_p1_decompress(&output.big_c);
    let big_y = env::bls12381_p1_decompress(&output.big_y);
    let pk2 = env::bls12381_p2_decompress(&app_public_key.pk2);
    let pk = env::bls12381_p2_decompress(public_key);
    let hash_point = hash_app_id_with_pk(public_key.as_slice(), app_id.as_ref());

    let pairing_input = [
        big_c.as_slice(),
        MINUS_G2_GENERATOR_UNCOMPRESSED.as_slice(),
        big_y.as_slice(),
        pk2.as_slice(),
        hash_point.as_slice(),
        pk.as_slice(),
    ]
    .concat();
    env::bls12381_pairing_check(&pairing_input)
}
```
