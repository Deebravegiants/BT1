I need to trace the full attack path through the actual code before rendering a verdict.

**Step 1 — Pairing equation in `ckd_output_check`**

The check at lines 80-102 of `crates/contract/src/primitives/ckd.rs` verifies:

```
e(big_c, -g2) · e(big_y, pk2) · e(hash_point, pk) = 1
```

i.e., `e(big_c, g2) = e(big_y, pk2) · e(hash_point, pk)`.

There is **no guard** that `big_y ≠ O`. [1](#0-0) 

**Step 2 — NEAR host accepts identity points in pairing checks**

The test `bls12381_pairing_check__should_accept_pairs_containing_identity_points` (lines 355-376) explicitly documents and asserts that the NEAR host function returns `true` when identity points appear in the pairing input. `e(O, pk2) = 1` by definition, so the equation collapses to `e(big_c, g2) = e(hash_point, pk)`, which holds exactly when `big_c = hash_point * msk`. [2](#0-1) 

**Step 3 — `respond_ckd` requires only one attested participant**

`respond_ckd` calls `assert_caller_is_attested_participant_and_protocol_active()` — a single-participant check — and then immediately calls `ckd_output_check`. There is no threshold-of-participants requirement on the response submission itself. A single attested participant who acts as coordinator (and has therefore legitimately aggregated threshold-many shares during the off-chain protocol) can submit any response that passes the on-chain check. [3](#0-2) 

**Step 4 — The "intentionally public" comment does not cover this case**

The comment at line 464-466 of `lib.rs` says identity points are accepted in `AppPublicKeyPV` "to support use cases where the derived key is intentionally public." That comment refers to the *user's* request-side key check (`app_public_key_check`), not to the *response-side* `ckd_output_check`. A user who submits a valid non-identity `(pk1, pk2)` pair intends confidential delivery; the Byzantine coordinator can still set `big_y = O` in the response and bypass the blinding. [4](#0-3) 

**Step 5 — Mathematical soundness of the attack**

Normal protocol: `big_c = hash_point·msk + app_pk1·s`, `big_y = s·g1`. User recovers `hash_point·msk = big_c − app_sk·big_y`, requiring knowledge of `app_sk`.

Attack: `big_y = O`, `big_c = hash_point·msk`. Check: `e(hash_point·msk, g2) = e(O, pk2)·e(hash_point, pk) = 1·e(hash_point, msk·g2) = e(hash_point·msk, g2)` ✓. The pairing check passes, and `big_c` is the raw derived key with no blinding — readable by anyone on-chain. [5](#0-4) 

---

### Title
Missing `big_y ≠ O` guard in `ckd_output_check` allows Byzantine coordinator to deliver unblinded CKD output — (`crates/contract/src/primitives/ckd.rs`)

### Summary
`ckd_output_check` verifies a BLS12-381 pairing equation but does not reject the G1 identity point as `big_y`. A single Byzantine TEE-attested coordinator can set `big_y = O` and `big_c = hash_point * msk`, causing the pairing check to pass while delivering the derived key in plaintext on-chain, bypassing the confidentiality guarantee of the PV CKD scheme.

### Finding Description
`ckd_output_check` in `crates/contract/src/primitives/ckd.rs` (lines 80-102) checks:

```
e(big_c, g2) = e(big_y, pk2) · e(hash_point, pk)
```

When `big_y = O` (the G1 identity), `e(O, pk2) = 1`, so the equation reduces to `e(big_c, g2) = e(hash_point, pk)`, which is satisfied by `big_c = hash_point * msk` — the raw, unblinded derived key. The NEAR host function explicitly accepts identity points in pairing inputs (confirmed by the existing test at lines 355-376 of the same file). There is no check anywhere in `ckd_output_check` or in `respond_ckd` that `big_y` must be a non-identity point.

`respond_ckd` (lines 654-689 of `crates/contract/src/lib.rs`) requires only that the caller is a single attested participant; it imposes no threshold on response submission. A Byzantine coordinator who has legitimately aggregated threshold-many shares during the off-chain protocol can compute `hash_point * msk` and submit it as `big_c` with `big_y = O`.

### Impact Explanation
The PV CKD scheme's confidentiality invariant is that `hash_point * msk` is delivered encrypted under the user's ephemeral key `(pk1, pk2)`, so only the holder of `app_sk` can recover it. With `big_y = O`, `big_c = hash_point * msk` is written directly into the resolved yield and is visible to any observer of the NEAR chain. The derived key material — which the user intends to keep private — is exposed without their consent and without any indication that the response was malformed.

Impact: **confidential key derivation output exposed without encryption despite the publicly-verifiable check passing**, matching the Critical scope item "confidential key derivation output without the required participant authorization."

### Likelihood Explanation
Requires exactly one Byzantine TEE-attested coordinator. The coordinator role is a normal part of the off-chain CKD protocol; any participant can occupy it. No threshold collusion is needed beyond what the coordinator already receives from honest participants during normal protocol execution. The attack is a single `respond_ckd` call with two crafted field values.

### Recommendation
Add an explicit non-identity check for `big_y` inside `ckd_output_check`:

```rust
// Reject the identity point: big_y = O means no blinding was applied.
if big_y == G1Projective::identity().to_uncompressed().as_slice() {
    return false;
}
```

Alternatively, enforce this at the `respond_ckd` call site before invoking `ckd_output_check`. The check must be applied to the *decompressed* point so that non-canonical encodings of the identity cannot bypass it.

### Proof of Concept
```rust
// In a unit test environment with mock NEAR host:
let msk = Scalar::random(&mut rng);
let network_pk = G2Projective::generator() * msk;
let app_scalar = Scalar::random(&mut rng);
let app_pk = CKDAppPublicKeyPV {
    pk1: Bls12381G1PublicKey((G1Projective::generator() * app_scalar).to_compressed()),
    pk2: Bls12381G2PublicKey((G2Projective::generator() * app_scalar).to_compressed()),
};
let app_id = derive_app_id(&"alice.near".parse().unwrap(), "path");
let hash_point = G1Projective::hash_to_curve(
    &[network_pk.to_compressed().as_slice(), app_id.as_ref()].concat(),
    NEAR_CKD_DOMAIN, &[],
);

// Attack: big_y = identity, big_c = hash_point * msk (unblinded)
let big_s = hash_point * msk;
let response = CKDResponse {
    big_y: Bls12381G1PublicKey(G1Projective::identity().to_compressed()),
    big_c: Bls12381G1PublicKey(big_s.to_compressed()),
};

let network_pk_dto = Bls12381G2PublicKey(network_pk.to_compressed());
// This returns true — the check passes with no blinding
assert!(ckd_output_check(&app_id, &response, &app_pk, &network_pk_dto));

// User recovers big_s directly from big_c without knowing app_scalar
// big_c IS hash_point * msk — no private scalar needed
``` [1](#0-0) [6](#0-5) [2](#0-1)

### Citations

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

**File:** crates/contract/src/primitives/ckd.rs (L355-376)
```rust
    #[test]
    #[expect(non_snake_case)]
    fn bls12381_pairing_check__should_accept_pairs_containing_identity_points() {
        // Given: e(g1, identity) * e(identity, g2) = 1
        let g1 = G1Projective::generator().to_uncompressed();
        let g1_identity = G1Projective::identity().to_uncompressed();
        let g2 = G2Projective::generator().to_uncompressed();
        let g2_identity = G2Projective::identity().to_uncompressed();
        let pairing_input = [
            g1.as_slice(),
            g2_identity.as_slice(),
            g1_identity.as_slice(),
            g2.as_slice(),
        ]
        .concat();

        // When
        let accepted = env::bls12381_pairing_check(&pairing_input);

        // Then
        assert!(accepted);
    }
```

**File:** crates/contract/src/lib.rs (L463-491)
```rust
    /// we ask for a small deposit for each ckd request.
    ///
    /// Note: identity points are accepted in `AppPublicKeyPV` to support use cases
    /// where the derived key is intentionally public (no encryption).
    #[handle_result]
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
```

**File:** crates/contract/src/lib.rs (L654-689)
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
