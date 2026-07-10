### Title
Missing CKD Output Verification for `AppPublicKey` Variant Allows Single Malicious Participant to Forge Confidential Key Derivation Responses - (File: `crates/contract/src/lib.rs`)

---

### Summary

`respond_ckd()` applies a cryptographic pairing check (`ckd_output_check`) only for the `AppPublicKeyPV` variant of `CKDAppPublicKey`, while the `AppPublicKey` variant receives **no on-chain verification** of the response. This is inconsistent with `respond()` and `respond_verify_foreign_tx()`, which both cryptographically verify their responses before resolving yields. A single malicious attested participant (below threshold) can call `respond_ckd()` with an arbitrary forged `CKDResponse` for any pending `AppPublicKey` request, and the contract will accept and deliver it to the user.

---

### Finding Description

The three node-facing `respond*` callbacks enforce different levels of output integrity:

**`respond()`** — always verifies the signature cryptographically before resolving: [1](#0-0) 

**`respond_verify_foreign_tx()`** — always verifies the signature cryptographically before resolving: [2](#0-1) 

**`respond_ckd()`** — applies `ckd_output_check` only for `AppPublicKeyPV`, and does **nothing** for `AppPublicKey`:

```rust
match &request.app_public_key {
    dtos::CKDAppPublicKey::AppPublicKey(_) => {}          // ← no check
    dtos::CKDAppPublicKey::AppPublicKeyPV(app_pk) => {
        if !ckd_output_check(&request.app_id, &response, app_pk, &public_key) {
            env::panic_str("CKD output check failed");
        }
    }
}
``` [3](#0-2) 

`ckd_output_check` performs a BLS12-381 pairing check `e(big_c, g2) = e(big_y, app_pk2) · e(hash_point, public_key)` that cryptographically binds the response to the MPC network's public key and the user's app public key: [4](#0-3) 

No equivalent binding check exists for `AppPublicKey`. The existing unit test for this path confirms this — it passes with completely invalid byte arrays `[1u8; 48]` and `[2u8; 48]` as the response: [5](#0-4) 

---

### Impact Explanation

A single malicious attested participant can call `respond_ckd()` for any pending `AppPublicKey` CKD request and supply an arbitrary `CKDResponse { big_y, big_c }`. The contract resolves the yield and delivers the forged output to the waiting user via `resolve_yields_for`: [6](#0-5) 

The user receives `(big_y, big_c)` that is not a valid encryption of their derived key under their app public key. They cannot decrypt it to recover the intended derived secret. This breaks the core security invariant of the CKD service — that the output is the result of a threshold computation by at least `t` honest participants — for all `AppPublicKey` requests, using only a single compromised node.

**Impact: Medium** — request-lifecycle and contract execution-flow manipulation that breaks the production CKD safety invariant without requiring threshold collusion.

---

### Likelihood Explanation

The attacker must be a single attested participant in the MPC network. This is a realistic adversary model: the system is explicitly designed to tolerate up to `t-1` Byzantine participants. A single compromised TEE node satisfies `assert_caller_is_attested_participant_and_protocol_active()`: [7](#0-6) 

No threshold collusion is required. The attacker only needs to observe a pending `AppPublicKey` CKD request (visible on-chain) and race to call `respond_ckd` before the honest leader does.

**Likelihood: Medium** — requires one compromised attested participant; no threshold collusion needed.

---

### Recommendation

Apply a cryptographic binding check for the `AppPublicKey` variant analogous to `ckd_output_check` for `AppPublicKeyPV`. Since `AppPublicKey` is not publicly verifiable (the user's private key is needed to decrypt), the contract cannot perform a full pairing check. However, the contract should at minimum verify that `big_c` and `big_y` are valid BLS12-381 G1 points (subgroup membership), and consider whether the protocol design should require the `AppPublicKeyPV` variant for all on-chain-settled CKD requests to enable full output integrity verification. Alternatively, document explicitly that `AppPublicKey` CKD security relies entirely on the off-chain threshold assumption and that a single compromised node can forge responses.

---

### Proof of Concept

1. User calls `request_app_private_key()` with `CKDAppPublicKey::AppPublicKey(pk)` and attaches the required deposit. A pending CKD request is stored in `pending_ckd_requests`.

2. A single malicious attested participant (one compromised MPC node) calls `respond_ckd()` with the matching `CKDRequest` and an arbitrary forged response:
   ```rust
   contract.respond_ckd(
       ckd_request,
       CKDResponse {
           big_y: dtos::Bls12381G1PublicKey([0xAB; 48]), // arbitrary garbage
           big_c: dtos::Bls12381G1PublicKey([0xCD; 48]), // arbitrary garbage
       }
   )
   ```

3. The `match` arm for `AppPublicKey` executes no check. `resolve_yields_for` resolves the yield and delivers the forged `(big_y, big_c)` to the user. [8](#0-7) 

4. The user attempts to decrypt `big_c` using their private key and `big_y`, but the result is garbage — the derived key is unrecoverable. The honest MPC nodes' computation is never used.

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

**File:** crates/contract/src/lib.rs (L718-747)
```rust
        let signature_is_valid = match (&response.signature, public_key) {
            (
                dtos::SignatureResponse::Secp256k1(signature_response),
                PublicKeyExtended::Secp256k1 { near_public_key },
            ) => {
                let secp_pk = dtos::Secp256k1PublicKey::try_from(&near_public_key)
                    .expect("Secp256k1 variant always has a secp256k1 key");

                let payload_hash: [u8; 32] = response.payload_hash.0;

                // Check the signature is correct against the root public key
                near_mpc_signature_verifier::verify_ecdsa_signature(
                    signature_response,
                    &payload_hash,
                    &secp_pk,
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

**File:** crates/contract/src/lib.rs (L3424-3441)
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
