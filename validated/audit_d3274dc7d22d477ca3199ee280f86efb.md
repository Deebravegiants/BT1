### Title
Missing Cryptographic Validity Check for `AppPublicKey` CKD Responses Allows Single Attested Participant to Forge Key Material - (File: `crates/contract/src/lib.rs`)

### Summary

`respond_ckd` enforces a BLS12-381 pairing-based output check (`ckd_output_check`) only for the `AppPublicKeyPV` variant of a CKD request. For the legacy `AppPublicKey` variant, the match arm is completely empty — any attested participant can call `respond_ckd` with arbitrary `big_y` / `big_c` values and the contract will accept and deliver the forged key material to the waiting user, bypassing the threshold-agreement requirement entirely.

### Finding Description

In `respond_ckd`, after verifying the caller is an attested participant, the contract branches on the request's `app_public_key` type:

```rust
match &request.app_public_key {
    dtos::CKDAppPublicKey::AppPublicKey(_) => {}          // ← empty: no check
    dtos::CKDAppPublicKey::AppPublicKeyPV(app_pk) => {
        if !ckd_output_check(&request.app_id, &response, app_pk, &public_key) {
            env::panic_str("CKD output check failed");
        }
    }
}
``` [1](#0-0) 

For `AppPublicKeyPV`, the contract verifies `e(big_c, g2) = e(big_y, app_pk2) · e(hash_point, public_key)` via `ckd_output_check`, which requires knowledge of the MPC secret key to satisfy. [2](#0-1) 

For `AppPublicKey` (the legacy default used by the CLI and most callers), the arm is empty — no pairing check, no signature verification, nothing. The response is immediately passed to `resolve_yields_for`, which resumes all queued yields with the attacker-supplied bytes. [3](#0-2) 

The existing unit test for the `AppPublicKey` path confirms this: it passes `big_y = [1u8; 48]` and `big_c = [2u8; 48]` (cryptographically invalid points) and the call succeeds without error. [4](#0-3) 

By contrast, `respond` (ECDSA/EdDSA) always verifies the signature against the derived public key before resolving yields. [5](#0-4) 

### Impact Explanation

A single malicious attested participant — strictly below the signing threshold — can call `respond_ckd` with an arbitrary `CKDResponse` for any pending `AppPublicKey` CKD request. The contract accepts the response and delivers attacker-controlled `(big_y, big_c)` to the user. The user then derives a key from this forged ciphertext, obtaining a secret that the attacker knows (or controls). This is unauthorized confidential key derivation output: the threshold-agreement requirement is completely bypassed for the legacy variant.

**Impact class:** Critical — unauthorized confidential key derivation output without the required participant authorization.

### Likelihood Explanation

The `AppPublicKey` variant is the legacy default. The CKD example CLI uses it, and the e2e test `ckd_response__passes_cryptographic_verification` exercises it. [6](#0-5)  Any single attested participant (any node that has submitted a valid TEE attestation via `submit_participant_info`) can execute this attack. The `CKDRequest` key is deterministic from the user's account ID and derivation path, so the attacker can reconstruct it from on-chain events. The attack requires no collusion, no leaked keys, and no privileged access beyond being an attested participant.

### Recommendation

Apply the same cryptographic output check to the `AppPublicKey` variant. For the privately-verifiable case, the check must use only the G1 component of the app public key and the MPC BLS12-381 public key. Specifically, verify that `e(big_c - big_y · app_pk1, g2) = e(hash_point, public_key)` (or an equivalent relation derivable from the protocol definition in `confidential-key-derivation.md`). Alternatively, require all new CKD requests to use `AppPublicKeyPV` and deprecate the `AppPublicKey` path.

### Proof of Concept

1. User calls `request_app_private_key` with `AppPublicKey` variant and `derivation_path = "mykey"`. A `CKDRequest` is queued. [7](#0-6) 

2. Attacker (any single attested participant) reconstructs the `CKDRequest` from the user's `account_id` and `derivation_path` (both are public on-chain). [8](#0-7) 

3. Attacker calls `respond_ckd(ckd_request, CKDResponse { big_y: attacker_point, big_c: attacker_point })`. The `AppPublicKey` match arm is empty — no check runs. `resolve_yields_for` resumes the user's yield with the forged bytes. [9](#0-8) 

4. User receives `(big_y, big_c)` chosen by the attacker. The derived secret is either known to the attacker or is cryptographically garbage, breaking the confidentiality guarantee of the CKD protocol.

### Citations

**File:** crates/contract/src/lib.rs (L469-511)
```rust
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

**File:** crates/contract/src/lib.rs (L675-688)
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

**File:** crates/contract/src/primitives/ckd.rs (L76-102)
```rust
/// Check that `e(big_c, g2) = e(big_y, app_pk2) . e(hash_point, public_key)`.
///
/// Point validation is fully delegated to the host, as in
/// [`app_public_key_check`].
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

**File:** crates/e2e-tests/tests/ckd_verification.rs (L40-91)
```rust
/// Verify that a CKD response (AppPublicKey variant) is mathematically correct.
#[tokio::test]
#[expect(non_snake_case)]
async fn ckd_response__passes_cryptographic_verification() {
    // given
    let (cluster, running) =
        common::must_setup_cluster(common::CKD_VERIFICATION_PORT_SEED, |_| {}).await;

    let bls_domain = running
        .domains
        .domains
        .iter()
        .find(|d| {
            Curve::from(d.protocol) == Curve::Bls12381 && matches!(d.purpose, DomainPurpose::CKD)
        })
        .expect("no Bls12381 CKD domain found")
        .clone();

    let mpc_pk = common::must_get_bls_public_key(&running, bls_domain.id);
    let user = cluster.default_user_account().clone();

    let mut rng = rand::rngs::StdRng::seed_from_u64(1);
    let private_key = Scalar::random(&mut rng);
    let app_public_key = CKDAppPublicKey::AppPublicKey(Bls12381G1PublicKey::from(
        &(G1Projective::generator() * private_key),
    ));

    // when
    let outcome = cluster
        .send_ckd_request(bls_domain.id, app_public_key, &user)
        .await
        .expect("CKD request transaction failed");

    // then
    assert!(
        outcome.is_success(),
        "CKD request failed: {:?}",
        outcome.failure_message()
    );

    let response: serde_json::Value = outcome.json().expect("failed to deserialize CKD response");
    let big_y: Bls12381G1PublicKey =
        serde_json::from_value(response["big_y"].clone()).expect("failed to parse big_y");
    let big_c: Bls12381G1PublicKey =
        serde_json::from_value(response["big_c"].clone()).expect("failed to parse big_c");

    assert!(
        verify_ckd(&user, DERIVATION_PATH, &mpc_pk, private_key, &big_y, &big_c)
            .expect("verify_ckd failed"),
        "CKD response failed cryptographic verification"
    );
}
```

**File:** crates/near-mpc-crypto-types/src/ckd.rs (L84-97)
```rust
impl CKDRequest {
    pub fn new(
        app_public_key: CKDAppPublicKey,
        domain_id: DomainId,
        predecessor_id: &AccountId,
        derivation_path: &str,
    ) -> Self {
        let app_id = crate::kdf::derive_app_id(predecessor_id, derivation_path);
        Self {
            app_public_key,
            app_id,
            domain_id,
        }
    }
```
