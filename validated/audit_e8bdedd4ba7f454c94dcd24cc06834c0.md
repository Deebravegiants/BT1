### Title
Identity-Point `app_public_key_check` Bypass Strips CKD-PV Blinding, Exposing Unblinded Key — (`crates/threshold-signatures/src/confidential_key_derivation/protocol_pv.rs`)

### Summary

`app_public_key_check` does not reject the G1/G2 identity (point-at-infinity). An unprivileged caller can submit a CKD-PV request with `pk1 = G1_identity`, `pk2 = G2_identity`. The check passes, the blinding term `y * pk1` collapses to zero in every node's share, the coordinator aggregates the fully unblinded key `C = msk * H(pk, app_id)`, the `aggregated_output_check` still verifies, and the caller receives the raw BLS key directly.

---

### Finding Description

**Root cause — `check_valid_point_g1` / `check_valid_point_g2` do not test `is_identity()`** [1](#0-0) 

```rust
pub(crate) fn check_valid_point_g1(p: G1Affine) -> bool {
    (p.is_on_curve() & p.is_torsion_free()).into()
}
pub(crate) fn check_valid_point_g2(p: G2Affine) -> bool {
    (p.is_on_curve() & p.is_torsion_free()).into()
}
```

The BLS12-381 identity point satisfies both `is_on_curve()` and `is_torsion_free()` (it is the neutral element of every subgroup), so both functions return `true` for the identity.

**Step 1 — `app_public_key_check` passes for `(G1_identity, G2_identity)`** [2](#0-1) 

```rust
fn app_public_key_check(app_pk: &PublicVerificationKey) -> bool {
    if !check_valid_point_g1(app_pk.pk1.into()) || !check_valid_point_g2(app_pk.pk2.into()) {
        return false;   // ← identity passes both checks
    }
    multi_miller_loop(&[
        (app_pk.pk1, -ElementG2::generator()),   // e(identity, -G2) = 1
        (ElementG1::generator(), app_pk.pk2),    // e(G1, identity)  = 1
    ])  // 1 · 1 = 1  → is_identity() → returns true
}
```

The pairing product `e(identity, -G2) · e(G1, identity) = 1 · 1 = 1`, so `multi_miller_loop` returns `true`.

**Step 2 — Blinding collapses to zero in every node** [3](#0-2) 

```rust
// C <- S + y . A
let big_c = big_s + app_pk.pk1 * y.0;
//                  ^^^^^^^^^^^^^^^^ = identity * y = identity
// → big_c = big_s = hash_point * private_share   (unblinded share)
```

With `pk1 = identity`, the blinding term `y · pk1` is the identity for every participant. Each node sends its raw key share `λi · xi · H(pk, app_id)`.

**Step 3 — `aggregated_output_check` still verifies** [4](#0-3) 

The check verifies `e(C, G2) = e(Y, pk2) · e(H, msk_pk)`. With `pk2 = identity`:

```
e(C, G2) = e(Y, identity) · e(H, msk_pk)
         = 1              · e(H, msk_pk)
         = e(H, msk_pk)
```

Since `C = msk · H`, we have `e(msk·H, G2) = e(H, msk·G2) = e(H, msk_pk)`. The check passes.

**Step 4 — Caller recovers the unblinded key** [5](#0-4) 

```rust
pub fn unmask(&self, secret_scalar: Scalar) -> Signature {
    self.big_c - self.big_y * secret_scalar
}
```

The caller's "secret" `a` satisfies `a · G1 = pk1 = identity`, so `a = 0`. Therefore `C - 0 · Y = C = msk · H(pk, app_id)` — the unblinded BLS key — is returned directly.

**Contrast with the existing identity guard in deserialization (not applied here)** [6](#0-5) 

The `BLS12381G1Group::deserialize` path already rejects identity elements, but `app_public_key_check` uses `check_valid_point_g1` which does not, creating an inconsistency.

---

### Impact Explanation

An unprivileged contract caller obtains `msk · H(msk_pk, app_id)` — the raw BLS confidential key — for any `app_id` of their choice, without possessing the corresponding app secret key. This is an unauthorized confidential key derivation output. The confidentiality invariant of the CKD-PV protocol (that no party without the app secret learns the key) is completely broken.

---

### Likelihood Explanation

The attack requires only a single malformed contract call with two identity-point field values. No threshold collusion, no privileged access, and no network-level capability is needed. The identity point is a standard, easily serializable curve point.

---

### Recommendation

Add an explicit identity-point rejection to `check_valid_point_g1` and `check_valid_point_g2`:

```rust
pub(crate) fn check_valid_point_g1(p: G1Affine) -> bool {
    !bool::from(p.is_identity()) && (p.is_on_curve() & p.is_torsion_free()).into()
}
pub(crate) fn check_valid_point_g2(p: G2Affine) -> bool {
    !bool::from(p.is_identity()) && (p.is_on_curve() & p.is_torsion_free()).into()
}
```

This mirrors the guard already present in `BLS12381G1Group::deserialize`.

---

### Proof of Concept

```rust
// In protocol_pv.rs test module:
#[test]
fn test_identity_pk_strips_blinding() {
    let mut rng = MockCryptoRng::seed_from_u64(42);
    let app_id = AppId::try_from(b"Near App").unwrap();

    // Construct identity public verification key
    let identity_pk = PublicVerificationKey::new(
        ElementG1::identity(),
        ElementG2::identity(),
    );

    // app_public_key_check must return true (demonstrating the bug)
    assert!(app_public_key_check(&identity_pk),
        "identity pk should be rejected but is accepted");

    let participants = generate_participants(3);
    let coordinator = participants[0];
    let (f, pk) = generate_test_keys(2, &mut rng);
    let msk = f.eval_at_zero().unwrap().0;

    let mut protocols = vec![];
    for p in &participants {
        let rng_p = MockCryptoRng::seed_from_u64(rng.next_u64());
        let key_pair = make_keygen_output(&f, &pk, *p);
        protocols.push((*p, Box::new(
            ckd(&participants, coordinator, *p, key_pair,
                app_id.clone(), identity_pk.clone(), rng_p).unwrap()
        ) as Box<dyn Protocol<Output = _>>));
    }

    let result = run_protocol(protocols).unwrap();
    let ckd_output = check_one_coordinator_output(result, coordinator).unwrap();

    // C should equal msk * H(pk, app_id) — unblinded
    let expected = hash_app_id_with_pk(&pk, &app_id) * msk;
    // unmask with a=0 gives C directly
    assert_eq!(ckd_output.unmask(Scalar::ZERO), expected,
        "unblinded key exposed without app secret");
}
```

### Citations

**File:** crates/threshold-signatures/src/confidential_key_derivation/ciphersuite.rs (L205-215)
```rust
    fn deserialize(buf: &Self::Serialization) -> Result<Self::Element, frost_core::GroupError> {
        Self::Element::from_compressed(buf).into_option().map_or(
            Err(frost_core::GroupError::MalformedElement),
            |point| {
                if point.is_identity().into() {
                    Err(frost_core::GroupError::InvalidIdentityElement)
                } else {
                    Ok(point)
                }
            },
        )
```

**File:** crates/threshold-signatures/src/confidential_key_derivation/ciphersuite.rs (L219-225)
```rust
pub(crate) fn check_valid_point_g1(p: G1Affine) -> bool {
    (p.is_on_curve() & p.is_torsion_free()).into()
}

pub(crate) fn check_valid_point_g2(p: G2Affine) -> bool {
    (p.is_on_curve() & p.is_torsion_free()).into()
}
```

**File:** crates/threshold-signatures/src/confidential_key_derivation/protocol_pv.rs (L207-211)
```rust
    // S <- x . H(app_id)
    let big_s = hash_point * private_share.to_scalar();

    // C <- S + y . A
    let big_c = big_s + app_pk.pk1 * y.0;
```

**File:** crates/threshold-signatures/src/confidential_key_derivation/protocol_pv.rs (L222-236)
```rust
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

**File:** crates/threshold-signatures/src/confidential_key_derivation/protocol_pv.rs (L239-247)
```rust
fn app_public_key_check(app_pk: &PublicVerificationKey) -> bool {
    if !check_valid_point_g1(app_pk.pk1.into()) || !check_valid_point_g2(app_pk.pk2.into()) {
        return false;
    }
    multi_miller_loop(&[
        (app_pk.pk1, -ElementG2::generator()),
        (ElementG1::generator(), app_pk.pk2),
    ])
}
```

**File:** crates/threshold-signatures/src/confidential_key_derivation.rs (L53-55)
```rust
    pub fn unmask(&self, secret_scalar: Scalar) -> Signature {
        self.big_c - self.big_y * secret_scalar
    }
```
