### Title
`respond_ckd` Accepts Unverified CKD Output for `AppPublicKey` Variant, Enabling Single-Participant Forgery - (File: `crates/contract/src/lib.rs`)

---

### Summary

`respond_ckd` performs a cryptographic output check (`ckd_output_check`) only for the `AppPublicKeyPV` (publicly verifiable) variant of CKD requests. For the `AppPublicKey` (privately verifiable, legacy) variant, the branch is a no-op — any `CKDResponse` is accepted and resolved unconditionally. A single Byzantine attested participant can submit an arbitrary forged CKD output for any pending `AppPublicKey` request, delivering an attacker-controlled confidential key to the user's TEE application without threshold authorization.

---

### Finding Description

In `respond_ckd`, after verifying the caller is an attested participant, the contract branches on the request's `app_public_key` variant:

```rust
match &request.app_public_key {
    dtos::CKDAppPublicKey::AppPublicKey(_) => {}   // ← no verification at all
    dtos::CKDAppPublicKey::AppPublicKeyPV(app_pk) => {
        if !ckd_output_check(&request.app_id, &response, app_pk, &public_key) {
            env::panic_str("CKD output check failed");
        }
    }
}
``` [1](#0-0) 

For `AppPublicKeyPV`, the contract enforces the pairing equation `e(big_c, G2) = e(big_y, app_pk2) · e(H(pk, app_id), pk)`, which cryptographically binds the response to the MPC network's master public key and the user's app public key: [2](#0-1) 

For `AppPublicKey`, **no analogous check exists**. The `AppPublicKey` variant is the legacy default, actively used in production (e.g., the e2e test `ckd_response__passes_cryptographic_verification` uses it): [3](#0-2) 

The `respond_ckd` function then unconditionally resolves the pending request with whatever `big_y` / `big_c` the caller supplied: [4](#0-3) 

The analog to the original report is exact: just as `reseedSiloDeposit` updates `stalk` but omits the corresponding `roots` update, `respond_ckd` resolves the CKD request (state update) but omits the corresponding output verification for the `AppPublicKey` branch (missing invariant enforcement).

---

### Impact Explanation

A single malicious attested participant can call `respond_ckd` with an arbitrary `CKDResponse{big_y, big_c}` for any pending `AppPublicKey` CKD request. The contract accepts it, resolves the yield, and delivers the forged `(Y, C)` pair to the requesting TEE application. The app then derives `sig = C + (-a)·Y` — a value entirely under attacker control — and uses it as its confidential key `s = HKDF(sig)`. This constitutes **unauthorized confidential key derivation output without the required threshold participant authorization**: the threshold MPC protocol is bypassed entirely; only one participant is needed to forge the result.

**Impact class:** Critical — confidential key derivation output without required participant authorization.

---

### Likelihood Explanation

- The `AppPublicKey` variant is the legacy default and is actively used in production.
- The attacker must be a single Byzantine attested participant (strictly below the signing threshold), which is an explicitly in-scope attacker model.
- No collusion is required. The attack is a single `respond_ckd` transaction.
- The attacker can race against honest nodes: whichever `respond_ckd` call is included first resolves the yield. A malicious participant can front-run honest nodes.

---

### Recommendation

Apply the same pairing-based output verification to the `AppPublicKey` variant. For the privately verifiable case, the check `e(H(pk, app_id), pk) = e(sig, G2)` (where `sig = big_c - a·big_y` is the recovered BLS signature) can be verified on-chain using only the MPC network public key and the `app_id`, without requiring the user's private scalar `a`. Alternatively, derive a `pk2 = a·G2` commitment from the stored `pk1 = a·G1` using the known generator relationship and apply `ckd_output_check` directly. At minimum, add a structural validity check (point-on-curve, non-identity) for `big_y` and `big_c` in the `AppPublicKey` branch.

---

### Proof of Concept

1. User submits `request_app_private_key` with `AppPublicKey(pk1)` — a valid G1 point — and `domain_id` pointing to the BLS12-381 CKD domain.
2. Attacker (a single attested participant) calls `respond_ckd(request, CKDResponse { big_y: [1u8;48], big_c: [2u8;48] })` — arbitrary garbage points.
3. The `AppPublicKey(_) => {}` branch executes with no check.
4. `resolve_yields_for` resolves the pending yield with the forged response.
5. The user's TEE app receives `(Y=[1u8;48], C=[2u8;48])` and derives `s = HKDF(C - a·Y)` — an attacker-controlled value — as its confidential key.

This is confirmed by the existing unit test at lines 4513–4521, which demonstrates that a participant can successfully call `respond_ckd` with `CKDResponse { big_y: [1u8;48], big_c: [2u8;48] }` on an `AppPublicKey` request and the call succeeds without any error: [5](#0-4)

### Citations

**File:** crates/contract/src/lib.rs (L675-682)
```rust
        match &request.app_public_key {
            dtos::CKDAppPublicKey::AppPublicKey(_) => {}
            dtos::CKDAppPublicKey::AppPublicKeyPV(app_pk) => {
                if !ckd_output_check(&request.app_id, &response, app_pk, &public_key) {
                    env::panic_str("CKD output check failed");
                }
            }
        }
```

**File:** crates/contract/src/lib.rs (L684-689)
```rust
        pending_requests::resolve_yields_for(
            &mut self.pending_ckd_requests,
            &request,
            serde_json::to_vec(&response).unwrap(),
        )
    }
```

**File:** crates/contract/src/lib.rs (L4513-4521)
```rust
        let valid_response = CKDResponse {
            big_y: dtos::Bls12381G1PublicKey([1u8; 48]),
            big_c: dtos::Bls12381G1PublicKey([2u8; 48]),
        };

        // This should succeed (attested participant)
        contract
            .respond_ckd(ckd_request.clone(), valid_response.clone())
            .expect("Participant should be allowed to respond_ckd");
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
