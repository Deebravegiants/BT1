### Title
Unverified CKD Response for `AppPublicKey` Variant Allows Single Attested Participant to Forge Confidential Key Derivation Output - (File: `crates/contract/src/lib.rs`)

---

### Summary

`respond_ckd` in the MPC contract applies a cryptographic output check (`ckd_output_check`) only when the request uses the `AppPublicKeyPV` variant. When the request uses the legacy `AppPublicKey` variant, the response is accepted with **no cryptographic verification**. A single attested participant — well below the signing threshold — can call `respond_ckd` with an arbitrary forged `CKDResponse` (`big_y`, `big_c`) for any pending `AppPublicKey` request, and the contract will deliver the forged output to the user as if it were the legitimate threshold-computed result.

---

### Finding Description

In `respond_ckd` (`crates/contract/src/lib.rs`, lines 675–682), the output check is gated on the `AppPublicKeyPV` variant:

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

The `ckd_output_check` function (`crates/contract/src/primitives/ckd.rs`, lines 80–102) verifies the pairing equation `e(big_c, g2) = e(big_y, app_pk2) · e(hash_point, public_key)`, which cryptographically binds the response to the MPC network's master secret key and the user's app identity. Without this check, any `(big_y, big_c)` pair is accepted. [2](#0-1) 

For `respond` (ECDSA/EdDSA), the contract verifies the signature against the derived public key before accepting it, ensuring threshold cooperation was required to produce the response: [3](#0-2) 

No equivalent protection exists for `respond_ckd` with `AppPublicKey`. The only guards are:
- `assert_caller_is_signer()` — caller must be a NEAR signer
- `assert_caller_is_attested_participant_and_protocol_active()` — caller must be an attested participant [4](#0-3) 

Neither guard requires threshold cooperation. A single attested participant satisfies both.

**Attack path:**
1. User calls `request_app_private_key` with `AppPublicKey` variant; request is stored in `pending_ckd_requests`.
2. Malicious single attested participant calls `respond_ckd(request, CKDResponse { big_y: attacker_point, big_c: attacker_point })`.
3. The `AppPublicKey` branch executes with no check; `resolve_yields_for` drains the queue and resumes all waiting yields with the forged response bytes.
4. The user's yield-callback fires with the attacker-controlled `(big_y, big_c)` pair.
5. The user derives a confidential key from the forged output — a key the attacker knows or controls. [5](#0-4) 

The `AppPublicKey` variant is the **default/legacy** format accepted by `request_app_private_key`, meaning the majority of real-world CKD requests are vulnerable. [6](#0-5) 

---

### Impact Explanation

**Critical.** A single attested MPC participant — strictly below the signing threshold — can forge the confidential key derivation output for any pending `AppPublicKey` CKD request. The user receives attacker-controlled key material `(big_y, big_c)` and derives a confidential key from it. Because the `AppPublicKey` variant is privately verifiable only (the user cannot check the output on-chain), the forgery is undetectable at the contract level. The attacker who supplies `big_y = r·G1` for a known scalar `r` can compute the resulting confidential key, gaining full knowledge of the user's derived secret. This constitutes unauthorized confidential key derivation output without the required threshold participant authorization.

---

### Likelihood Explanation

Any single attested participant in the MPC network can exploit this. Attestation is a TEE-based check, but the TEE only proves the node is running the correct software — it does not prevent a compromised or malicious operator from submitting an off-spec `respond_ckd` call directly to the contract. The `AppPublicKey` variant is the legacy default, so the vast majority of production CKD requests are affected. The attack requires no special timing, no collusion, and no cryptographic break — only a valid NEAR account with an active attestation.

---

### Recommendation

Apply `ckd_output_check` unconditionally for all CKD responses, regardless of the `app_public_key` variant. For the `AppPublicKey` variant, the check can be performed using `pk1` as the G2 component is not available, but the coordinator node already performs `aggregated_output_check` off-chain. The simplest fix is to require `AppPublicKeyPV` for all new requests and reject `AppPublicKey` in `respond_ckd`, or to derive a synthetic `pk2` from `pk1` for the check. At minimum, add a comment and a tracking issue; the immediate mitigation is to require `AppPublicKeyPV` for all new `request_app_private_key` submissions and reject `AppPublicKey` responses in `respond_ckd`. [7](#0-6) 

---

### Proof of Concept

```rust
// Attacker is an attested participant. User submitted:
//   request_app_private_key({ app_public_key: AppPublicKey(user_pk1), ... })
// Attacker calls respond_ckd with forged output:

let forged_response = CKDResponse {
    big_y: Bls12381G1PublicKey::from(&(G1Projective::generator() * attacker_scalar)),
    big_c: Bls12381G1PublicKey::from(&(G1Projective::generator() * attacker_scalar)),
};

// No ckd_output_check is called for AppPublicKey variant.
// resolve_yields_for drains the queue and resumes the user's yield
// with the forged (big_y, big_c) bytes.
contract.respond_ckd(ckd_request, forged_response).unwrap();

// User's yield-callback fires with attacker-controlled key material.
// User computes: confidential_key = big_c + (-app_scalar) * big_y
// Since attacker chose big_y and big_c, attacker knows the result.
```

The existing unit test `respond_ckd__should_succeed_when_response_is_valid_and_request_exists` already demonstrates that an arbitrary `CKDResponse { big_y: [1u8;48], big_c: [2u8;48] }` is accepted without error for the `AppPublicKey` variant, confirming the missing check. [8](#0-7)

### Citations

**File:** crates/contract/src/lib.rs (L484-491)
```rust
        match &request.app_public_key {
            dtos::CKDAppPublicKey::AppPublicKey(_) => {}
            dtos::CKDAppPublicKey::AppPublicKeyPV(pk) => {
                if !app_public_key_check(pk) {
                    env::panic_str("app public key check failed")
                }
            }
        }
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

**File:** crates/contract/src/lib.rs (L3403-3441)
```rust
    #[test]
    fn respond_ckd__should_succeed_when_response_is_valid_and_request_exists() {
        let (context, mut contract, _secret_key) = basic_setup(Curve::Bls12381, &mut OsRng);
        let app_public_key: dtos::Bls12381G1PublicKey =
            "bls12381g1:6KtVVcAAGacrjNGePN8bp3KV6fYGrw1rFsyc7cVJCqR16Zc2ZFg3HX3hSZxSfv1oH6"
                .parse()
                .unwrap();
        let request = CKDRequestArgs {
            derivation_path: "".to_string(),
            app_public_key: CKDAppPublicKey::AppPublicKey(app_public_key.clone()),
            domain_id: dtos::DomainId::default(),
        };
        let ckd_request = CKDRequest::new(
            CKDAppPublicKey::AppPublicKey(app_public_key),
            request.domain_id,
            &context.predecessor_account_id,
            &request.derivation_path,
        );
        contract.request_app_private_key(request);
        contract.get_pending_ckd_request(&ckd_request).unwrap();

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

**File:** crates/contract/src/pending_requests.rs (L62-88)
```rust
/// Resume every yield queued for `request` with `response_bytes`, draining the
/// fan-out map in one pass. Returns `Err(RequestNotFound)` if the map held no entry.
///
/// Resuming a yield that has already timed out is a no-op at the SDK level.
pub(crate) fn resolve_yields_for<K>(
    requests: &mut LookupMap<K, Vec<YieldIndex>>,
    request: &K,
    response_bytes: Vec<u8>,
) -> Result<(), Error>
where
    K: BorshSerialize + BorshDeserialize + Clone + Ord,
{
    let resumed = requests
        .remove(request)
        .unwrap_or_default()
        .into_iter()
        .map(|YieldIndex { data_id }| {
            env::promise_yield_resume(&data_id, response_bytes.clone());
        })
        .count();

    if resumed > 0 {
        Ok(())
    } else {
        Err(InvalidParameters::RequestNotFound.into())
    }
}
```
