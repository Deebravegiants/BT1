### Title
`respond_ckd` Accepts Unvalidated CKD Response for `AppPublicKey` Variant, Allowing Single Attested Participant to Forge Derived Key Output - (File: crates/contract/src/lib.rs)

### Summary

`respond_ckd` in the MPC contract validates the CKD response only when the request uses the `AppPublicKeyPV` variant. When the request uses the `AppPublicKey` variant, the response is accepted with **zero cryptographic validation**. Any single attested participant can call `respond_ckd` with an arbitrary forged `CKDResponse`, bypassing the threshold requirement and delivering an attacker-controlled derived key to the user.

### Finding Description

In `crates/contract/src/lib.rs`, the `respond_ckd` function contains the following asymmetric validation:

```rust
match &request.app_public_key {
    dtos::CKDAppPublicKey::AppPublicKey(_) => {}   // ← no validation whatsoever
    dtos::CKDAppPublicKey::AppPublicKeyPV(app_pk) => {
        if !ckd_output_check(&request.app_id, &response, app_pk, &public_key) {
            env::panic_str("CKD output check failed");
        }
    }
}
``` [1](#0-0) 

For the `AppPublicKeyPV` variant, `ckd_output_check` enforces the pairing equation `e(big_c, g2) = e(big_y, app_pk2) · e(hash_point, public_key)`, which cryptographically proves the response was computed correctly by the threshold MPC protocol. [2](#0-1) 

For the `AppPublicKey` variant, **no equivalent check exists**. The contract simply resolves the pending yield with whatever `(big_y, big_c)` the caller provides.

The `respond_ckd` entry point only requires the caller to be an attested participant — it does not require threshold collusion: [3](#0-2) 

The CKD protocol is designed so that the user decrypts `big_c - a * big_y` to recover the secret `S = msk · H(pk ‖ app_id)`. An attacker who controls `(big_y, big_c)` can set `big_y = G1_identity` and `big_c = S_attacker` (any G1 point they know). The user then decrypts `S_attacker - a · 0 = S_attacker`. The attacker knows `S_attacker`, so they fully control the derived key the user receives. The identity point is a valid G1 encoding accepted by the host: [4](#0-3) 

### Impact Explanation

A single malicious attested participant can forge the CKD output for any pending `AppPublicKey` request. The user receives a derived key whose secret is known to the attacker. This is unauthorized confidential key derivation output without the required threshold participant authorization — the entire purpose of the threshold MPC protocol for CKD is bypassed by one node acting alone.

This maps to: **Critical — confidential key derivation output without the required participant authorization; bypass of threshold-signature requirements.**

### Likelihood Explanation

**High.** The `AppPublicKey` variant is the primary (non-publicly-verifiable) CKD mode used in production (as shown in the e2e test `ckd_response__passes_cryptographic_verification`). [5](#0-4) 

Any single attested participant can race to call `respond_ckd` for any pending `AppPublicKey` request. No special privilege, key material, or collusion is required beyond holding a valid TEE attestation.

### Recommendation

Apply `ckd_output_check` unconditionally for both variants. For `AppPublicKey`, the check can be performed using only the G1 public key (`pk1`) by constructing a synthetic `CKDAppPublicKeyPV` with `pk2 = pk1_scalar * G2` — or, more directly, add a separate pairing check that verifies `e(big_c - big_y * a, g2) = e(H(pk ‖ app_id), msk_pk)` using only the G1 app public key and the known MPC G2 public key. Alternatively, require all CKD requests to use the `AppPublicKeyPV` variant so the existing on-chain check always applies.

### Proof of Concept

1. User submits `request_app_private_key` with `CKDAppPublicKey::AppPublicKey(user_g1_pk)` for a BLS12-381 CKD domain.
2. The contract queues the request in `pending_ckd_requests`.
3. Malicious attested participant constructs a forged response:
   ```
   big_y = G1_identity  (compressed encoding of the identity point)
   big_c = S_attacker   (any G1 point the attacker knows, e.g. G1_generator)
   ```
4. Attacker calls `respond_ckd(request, CKDResponse { big_y, big_c })`.
5. Contract passes the `AppPublicKey` branch with no validation and resolves the yield.
6. User receives `(big_y, big_c)` and decrypts `big_c - a * big_y = S_attacker - a * 0 = S_attacker`.
7. Attacker knows `S_attacker` and therefore knows the user's derived key, bypassing the threshold MPC protocol entirely. [6](#0-5) [7](#0-6)

### Citations

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

**File:** crates/contract/src/primitives/ckd.rs (L479-495)
```rust
    /// Documents the pre-existing behavior that identity key pairs satisfy
    /// the pairing equation and are accepted.
    #[test]
    #[expect(non_snake_case)]
    fn app_public_key_check__should_accept_identity_key_pair() {
        // Given
        let app_pk = dtos::CKDAppPublicKeyPV {
            pk1: dtos::Bls12381G1PublicKey(G1Projective::identity().to_compressed()),
            pk2: dtos::Bls12381G2PublicKey(G2Projective::identity().to_compressed()),
        };

        // When
        let accepted = app_public_key_check(&app_pk);

        // Then
        assert!(accepted);
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
