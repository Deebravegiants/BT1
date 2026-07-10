### Title
Missing Cryptographic Output Verification for `AppPublicKey` CKD Variant Allows Byzantine Participant to Deliver Attacker-Controlled Key Material - (File: `crates/contract/src/lib.rs`)

---

### Summary

In `respond_ckd`, the contract enforces a cryptographic pairing-equation check (`ckd_output_check`) only for the `AppPublicKeyPV` variant of a CKD response. For the `AppPublicKey` (privately-verifiable, legacy) variant, the response `(big_y, big_c)` is accepted and delivered to the user with **no cryptographic verification whatsoever**. A single Byzantine attested participant — strictly below the signing threshold — can call `respond_ckd` with arbitrary `(big_y, big_c)` values and the contract will accept and forward them to the requesting user.

---

### Finding Description

In `crates/contract/src/lib.rs`, the `respond_ckd` function contains the following match block:

```rust
match &request.app_public_key {
    dtos::CKDAppPublicKey::AppPublicKey(_) => {}   // ← no check at all
    dtos::CKDAppPublicKey::AppPublicKeyPV(app_pk) => {
        if !ckd_output_check(&request.app_id, &response, app_pk, &public_key) {
            env::panic_str("CKD output check failed");
        }
    }
}
``` [1](#0-0) 

For `AppPublicKeyPV`, `ckd_output_check` verifies the BLS12-381 pairing equation `e(big_c, g2) = e(big_y, app_pk2) · e(hash_point, public_key)`, which cryptographically binds the response to the MPC master key and the user's app public key. [2](#0-1) 

For `AppPublicKey`, the arm is an empty block `{}`. Any `CKDResponse { big_y, big_c }` — including all-zero bytes, identity points, or attacker-chosen values — passes through unconditionally and is delivered to the user via `resolve_yields_for`. [3](#0-2) 

The analog to the external report is exact: just as `TridentNFT.permit` skips the `recoveredAddress != 0` check when `isApprovedForAll` is true, `respond_ckd` skips the output-validity check when the request variant is `AppPublicKey`. In both cases, a check that should be unconditional is gated on a condition that can be satisfied even when the skipped check would fail.

---

### Impact Explanation

The CKD protocol delivers an ElGamal-style encryption of derived key material under the user's app public key `app_pk = g1 * a`:

- Legitimate response: `big_c = big_s + app_pk * y`, `big_y = g1 * y`, where `big_s = H(app_id, pk) * msk`
- User decrypts: `big_s = big_c - a * big_y`

If an attacker submits `big_y = G1_identity` and `big_c = g1 * k` for an attacker-chosen scalar `k`, the user computes:

```
big_s' = big_c - a * G1_identity = big_c = g1 * k
```

The user's derived key material is now `g1 * k` — a value the attacker chose and knows. The attacker has effectively replaced the user's confidential derived key with an attacker-known value. This breaks the confidentiality guarantee of the CKD protocol: the user believes they hold a secret derived from the MPC master key, but the attacker knows it.

This maps to the allowed impact: **"Critical. Bypass of threshold-signature requirements or unauthorized access to MPC key shares, signing capability, or secret material that materially enables forgery or secret recovery"** — specifically, the attacker can force the user's derived key to be a value the attacker knows, enabling impersonation or forgery using that key.

---

### Likelihood Explanation

The attacker must be an attested participant (has submitted a valid `submit_participant_info` and passed TEE attestation). A single such participant — strictly below the signing threshold — can call `respond_ckd` for any pending `AppPublicKey` CKD request. The `AppPublicKey` variant is the legacy/default variant documented in the contract README and is the most commonly used form. [4](#0-3) 

The attacker does not need to collude with other participants, compromise any key, or perform any off-chain computation. They simply call `respond_ckd` with crafted `big_y` and `big_c` values before the honest nodes respond.

---

### Recommendation

Apply `ckd_output_check` unconditionally for both variants, or implement an equivalent binding check for the `AppPublicKey` variant. For `AppPublicKey`, the check should verify that `big_c - a * big_y` lies on the correct coset (i.e., is consistent with the MPC public key and the `app_id`). At minimum, the contract should verify that `big_y` is not the identity point and that `big_c` is a valid G1 point in the prime-order subgroup.

A simpler mitigation is to require that the `AppPublicKey` variant also carry a G2 component (upgrading it to `AppPublicKeyPV`) so that `ckd_output_check` can be applied uniformly. Alternatively, add a separate pairing check for the `AppPublicKey` case that verifies `e(big_c - big_s, g2) = e(big_y, app_pk_g2)` using a G2 lift of `app_pk`.

---

### Proof of Concept

1. User calls `request_app_private_key` with `AppPublicKey(pk1)` where `pk1 = g1 * a` for some private scalar `a`.
2. Attacker (an attested participant) observes the pending request in `pending_ckd_requests`.
3. Attacker calls `respond_ckd(request, CKDResponse { big_y: G1_identity_bytes, big_c: g1_times_k_bytes })` where `k` is any scalar the attacker chooses.
4. The match arm `AppPublicKey(_) => {}` executes with no check.
5. `resolve_yields_for` delivers `(big_y=identity, big_c=g1*k)` to the user.
6. User decrypts: `derived = big_c - a * big_y = g1*k - a*identity = g1*k`.
7. The user's derived key is `g1*k`, which the attacker knows. The attacker can now sign on behalf of the user for any protocol that uses this derived key. [5](#0-4) [6](#0-5)

### Citations

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

**File:** crates/contract/src/primitives/ckd.rs (L480-495)
```rust
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

**File:** crates/contract/README.md (L119-120)
```markdown
  - **Privately verifiable** (legacy): a single G1 point, e.g. `"bls12381g1:<base58>"` or `{"AppPublicKey": "bls12381g1:<base58>"}`.
  - **Publicly verifiable**: a pair of points `(pk1, pk2) = (a·G1, a·G2)`, passed as `{"AppPublicKeyPV": {"pk1": "bls12381g1:<base58>", "pk2": "bls12381g2:<base58>"}}`. This allows anyone to verify the encrypted result on-chain without the app's secret key.
```
