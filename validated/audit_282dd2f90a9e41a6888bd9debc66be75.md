### Title
Missing Aggregated Output Verification in Non-PV CKD Coordinator Allows Single Byzantine Participant to Corrupt Derived Key — (`crates/threshold-signatures/src/confidential_key_derivation/protocol.rs`)

---

### Summary

The non-PV CKD coordinator (`do_ckd_coordinator` in `protocol.rs`) aggregates participant shares with no post-aggregation pairing check. The PV variant (`protocol_pv.rs`) has an explicit `aggregated_output_check` after aggregation; the non-PV variant does not. The NEAR contract's `respond_ckd` also skips output verification for the `AppPublicKey` variant. A single Byzantine participant can send any crafted `CKDOutput` to the coordinator, causing the client to silently receive a wrong derived key.

---

### Finding Description

**Layer 1 — Protocol (node-to-node)**

`do_ckd_coordinator` in `protocol.rs` aggregates shares from all participants:

```rust
for (_, participant_output) in
    recv_from_others::<CKDOutput>(&chan, waitpoint, &participants, me).await?
{
    norm_big_y += participant_output.big_y();
    norm_big_c += participant_output.big_c();
}
let ckd_output = CKDOutput::new(norm_big_y, norm_big_c);
Ok(Some(ckd_output))   // returned with no check
``` [1](#0-0) 

There is no verification that the aggregated `(big_y, big_c)` satisfies any algebraic relation. Compare with the PV variant, which calls `aggregated_output_check` immediately after the same aggregation loop:

```rust
if !aggregated_output_check(&ckd_output, app_pk, &key_pair.public_key, &hash_point) {
    return Err(ProtocolError::AssertionFailed(
        "CKD output failed to verify".to_string(),
    ));
}
``` [2](#0-1) 

`aggregated_output_check` verifies `e(big_c, g2) = e(big_y, app_pk2) · e(H(pk‖app_id), network_pk)`, which is the exact relation that must hold for the output to be correct. [3](#0-2) 

**Layer 2 — Contract**

`respond_ckd` in `lib.rs` explicitly skips output verification for the `AppPublicKey` variant:

```rust
match &request.app_public_key {
    dtos::CKDAppPublicKey::AppPublicKey(_) => {}          // no check
    dtos::CKDAppPublicKey::AppPublicKeyPV(app_pk) => {
        if !ckd_output_check(...) { env::panic_str("CKD output check failed"); }
    }
}
``` [4](#0-3) 

**Layer 3 — Node dispatch**

The node routes `AppPublicKey` requests to the unprotected `ckd` function from `protocol.rs`, and `AppPublicKeyPV` requests to the protected `ckd_pv` from `protocol_pv.rs`: [5](#0-4) 

---

### Impact Explanation

A Byzantine participant sends a crafted `CKDOutput` — e.g., `(delta_y, delta_c)` instead of their honest Lagrange-weighted share. The coordinator adds these values to the running sum without any check. The resulting `(big_y, big_c)` is shifted by `(delta_y - honest_y_i, delta_c - honest_c_i)`. The client calls:

```
unmask(app_sk) = big_c - app_sk * big_y
``` [6](#0-5) 

The result is not `msk · H(pk‖app_id)`. The client receives a silently wrong derived key with no way to detect the corruption (the `AppPublicKey` variant has no G2 component to run a pairing check against). This breaks the determinism guarantee of CKD: the client cannot re-derive the same key, and any data encrypted or authenticated under the expected key becomes inaccessible or forged.

---

### Likelihood Explanation

- The attacker must be a legitimate, TEE-attested MPC participant — a high bar, but explicitly within the Byzantine-below-threshold threat model.
- The CKD session selects `threshold` participants at random; a single Byzantine node among them suffices.
- The `AppPublicKey` variant is the default/legacy variant (it is the one used in the e2e test `ckd_response__passes_cryptographic_verification`). [7](#0-6) 
- No ZKP, no MAC, and no post-aggregation check exists in the non-PV path to detect the manipulation.

---

### Recommendation

Add the same `aggregated_output_check` that `protocol_pv.rs` already uses to `do_ckd_coordinator` in `protocol.rs`. Because the non-PV variant uses only `pk1` (G1), the check must be adapted: verify `big_c - app_sk * big_y == msk * H(pk‖app_id)` is not directly possible without `app_sk`, but the coordinator can verify the structural relation using the network public key and the known `app_pk` (G1 only). Alternatively, deprecate the `AppPublicKey` variant in favour of `AppPublicKeyPV`, which already has both protocol-level and contract-level verification.

---

### Proof of Concept

```rust
// In a 3-participant CKD session (threshold=2), participant[1] is Byzantine.
// participant[1] sends a crafted output instead of its honest share:
chan.send_private(waitpoint, coordinator, &CKDOutput::new(
    ElementG1::generator() * Scalar::from(999u64),  // arbitrary delta_y
    ElementG1::generator() * Scalar::from(888u64),  // arbitrary delta_c
))?;

// The coordinator aggregates without checking and submits to the contract.
// The contract accepts it (AppPublicKey branch has no check).
// The client calls unmask(app_sk) and gets a value ≠ msk * H(pk‖app_id).
// assert_ne!(ckd_output.unmask(app_sk), hash_app_id_with_pk(&pk, &app_id) * msk);
```

### Citations

**File:** crates/threshold-signatures/src/confidential_key_derivation/protocol.rs (L54-61)
```rust
    for (_, participant_output) in
        recv_from_others::<CKDOutput>(&chan, waitpoint, &participants, me).await?
    {
        norm_big_y += participant_output.big_y();
        norm_big_c += participant_output.big_c();
    }
    let ckd_output = CKDOutput::new(norm_big_y, norm_big_c);
    Ok(Some(ckd_output))
```

**File:** crates/threshold-signatures/src/confidential_key_derivation/protocol_pv.rs (L66-70)
```rust
    if !aggregated_output_check(&ckd_output, app_pk, &key_pair.public_key, &hash_point) {
        return Err(ProtocolError::AssertionFailed(
            "CKD output failed to verify".to_string(),
        ));
    }
```

**File:** crates/threshold-signatures/src/confidential_key_derivation/protocol_pv.rs (L221-236)
```rust
/// Check that `e(big_c, g2) = e(big_y, app_pk2) . e(hash_point, public_key)`
fn aggregated_output_check(
    output: &CKDOutput,
    app_pk: &PublicVerificationKey,
    public_key: &VerifyingKey,
    hash_point: &ElementG1,
) -> bool {
    if !check_valid_point_g1(output.big_c.into()) || !check_valid_point_g1(output.big_y.into()) {
        return false;
    }
    multi_miller_loop(&[
        (output.big_c, -ElementG2::generator()),
        (output.big_y, app_pk.pk2),
        (*hash_point, public_key.to_element()),
    ])
}
```

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

**File:** crates/node/src/providers/ckd/sign.rs (L151-177)
```rust
        let result = match self.app_public_key {
            dtos::CKDAppPublicKey::AppPublicKey(pk) => {
                let protocol = ckd(
                    cs_participants.as_slice(),
                    leader,
                    my_id,
                    self.keygen_output,
                    app_id,
                    ElementG1::try_from(&pk)?,
                    OsRng,
                )?;
                run_protocol("ckd", channel, protocol).await?
            }
            dtos::CKDAppPublicKey::AppPublicKeyPV(pv) => {
                let pk1 = ElementG1::try_from(&pv.pk1)?;
                let pk2 = ElementG2::try_from(&pv.pk2)?;
                let protocol = ckd_pv(
                    cs_participants.as_slice(),
                    leader,
                    my_id,
                    self.keygen_output,
                    app_id,
                    PublicVerificationKey::new(pk1, pk2),
                    OsRng,
                )?;
                run_protocol("ckd_pv", channel, protocol).await?
            }
```

**File:** crates/threshold-signatures/src/confidential_key_derivation.rs (L53-55)
```rust
    pub fn unmask(&self, secret_scalar: Scalar) -> Signature {
        self.big_c - self.big_y * secret_scalar
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
