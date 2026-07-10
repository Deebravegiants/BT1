### Title
Missing CKD Response Verification for `AppPublicKey` Variant Allows Single Byzantine Node to Forge Confidential Key Derivation Output — (`File: crates/contract/src/lib.rs`)

---

### Summary

In `respond_ckd`, the contract performs a cryptographic output check (`ckd_output_check`) only when the request used the `AppPublicKeyPV` variant. For the `AppPublicKey` (legacy, "privately verifiable") variant, no on-chain verification of the response is performed. A single attested MPC participant — strictly below the signing threshold — can call `respond_ckd` with an arbitrary forged `CKDResponse` for any pending `AppPublicKey` request, and the contract will accept and deliver it to the user.

---

### Finding Description

In `respond_ckd` (`crates/contract/src/lib.rs`, lines 675–682):

```rust
match &request.app_public_key {
    dtos::CKDAppPublicKey::AppPublicKey(_) => {}          // ← no check
    dtos::CKDAppPublicKey::AppPublicKeyPV(app_pk) => {
        if !ckd_output_check(&request.app_id, &response, app_pk, &public_key) {
            env::panic_str("CKD output check failed");
        }
    }
}
``` [1](#0-0) 

The `ckd_output_check` function verifies the BLS12-381 pairing equation `e(big_c, g2) = e(big_y, app_pk2) · e(hash_point, public_key)`, which cryptographically proves the response is the correct threshold computation result. [2](#0-1) 

For `AppPublicKeyPV`, this check is enforced. For `AppPublicKey`, the `match` arm is an empty no-op — the contract unconditionally proceeds to `resolve_yields_for`, delivering whatever `big_c` and `big_y` the caller supplied. [3](#0-2) 

By contrast, `respond` (for ECDSA/EdDSA signatures) always verifies the signature against the network public key regardless of request type — there is no analogous class-based bypass. [4](#0-3) 

---

### Impact Explanation

**Critical — Unauthorized confidential key derivation output without required participant authorization.**

A single Byzantine attested participant calls `respond_ckd` with a crafted `CKDResponse{big_c, big_y}` of their choosing. The contract accepts it and resolves all pending yields for that `CKDRequest` with the forged bytes. The user's `request_app_private_key` callback receives the attacker-controlled ciphertext. Because the attacker chose `big_c` and `big_y`, they know the scalar relationship between them and can compute the same "derived key" the user will extract — breaking the confidentiality guarantee of the CKD protocol entirely. This bypasses the threshold computation requirement with a single-node action.

---

### Likelihood Explanation

Any single attested MPC participant can exploit this. The attacker only needs:
1. A valid TEE attestation (passes `assert_caller_is_attested_participant_and_protocol_active`).
2. Knowledge of a pending `AppPublicKey` CKD request (observable on-chain). [5](#0-4) 

No threshold collusion is required. The `AppPublicKey` variant is the legacy default format accepted by the contract. [6](#0-5) 

---

### Recommendation

Apply the same response-validity check to `AppPublicKey` requests. Since `AppPublicKey` provides only a G1 point (`pk1`) without a corresponding G2 point (`pk2`), the existing `ckd_output_check` (which requires `pk2` for the pairing) cannot be applied directly. The fix is one of:

1. **Deprecate `AppPublicKey` for new requests** and require `AppPublicKeyPV` for all new `request_app_private_key` calls, so every response is verifiable on-chain.
2. **Add a G2 companion check at request time**: require callers using `AppPublicKey` to also supply a `pk2` (making it equivalent to `AppPublicKeyPV`), enabling `ckd_output_check` in `respond_ckd` for all variants.

The `respond` function's unconditional signature verification is the correct model to follow. [4](#0-3) 

---

### Proof of Concept

1. User submits `request_app_private_key` with `AppPublicKey("bls12381g1:<some_pk1>")` and `derivation_path = "mykey"`. Contract stores the pending yield.
2. Attacker (single attested participant) picks arbitrary scalars `r` and constructs:
   - `big_y = G1 * r`
   - `big_c = G1 * r` (or any point; attacker knows the relationship)
3. Attacker calls `respond_ckd(request, CKDResponse { big_c, big_y })`.
4. `respond_ckd` passes `assert_caller_is_attested_participant_and_protocol_active`, enters the `AppPublicKey(_) => {}` arm (no check), and calls `resolve_yields_for` — delivering the forged response. [7](#0-6) 

5. User's callback receives `big_c` and `big_y` chosen by the attacker. The user computes their "derived key" from these values. The attacker, knowing `r`, can compute the identical value — the confidential key derivation is compromised by a single below-threshold Byzantine node.

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

**File:** crates/contract/src/lib.rs (L666-666)
```rust
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

**File:** crates/near-mpc-crypto-types/src/ckd.rs (L15-17)
```rust
pub enum CKDAppPublicKey {
    AppPublicKey(Bls12381G1PublicKey),
    AppPublicKeyPV(CKDAppPublicKeyPV),
```
