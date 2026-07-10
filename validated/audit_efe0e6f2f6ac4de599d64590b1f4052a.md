Let me look at the `resolve_yields_for` function and the `assert_caller_is_attested_participant_and_protocol_active` guard to fully understand the security model.

### Title
Single Attested Participant Can Deliver Forged CKD Output for `AppPublicKey` Requests — (`crates/contract/src/lib.rs`)

---

### Summary

`respond_ckd` performs no cryptographic verification of the `CKDResponse` when the request uses `CKDAppPublicKey::AppPublicKey`. A single attested MPC participant can call `respond_ckd` with arbitrary `big_y`/`big_c` bytes, and the contract will immediately resolve the victim's yield with the forged output. The `ckd_output_check` pairing guard is only reachable via the `AppPublicKeyPV` branch.

---

### Finding Description

In `respond_ckd`, the match on `request.app_public_key` has two arms: [1](#0-0) 

The `AppPublicKey(_) => {}` arm is a no-op — no check of any kind is performed on `response`. The `AppPublicKeyPV` arm calls `ckd_output_check`, which verifies the BLS pairing equation `e(big_c, g2) = e(big_y, app_pk2) · e(hash_point, public_key)`: [2](#0-1) 

After the match, `resolve_yields_for` is called unconditionally. It drains the entire pending queue for the request and resumes every waiting yield with the (unverified) serialized response: [3](#0-2) 

The only caller-side guard is `assert_caller_is_attested_participant_and_protocol_active()`: [4](#0-3) 

This check confirms the caller is a current participant with valid TEE attestation. It does **not** require threshold-many participants to agree, and it does not bind the response to the master secret in any way for the `AppPublicKey` branch.

For comparison, `respond` (signatures) always verifies the ECDSA/EdDSA signature against the derived public key before resolving: [5](#0-4) 

The `AppPublicKey` branch of `respond_ckd` has no equivalent binding.

---

### Impact Explanation

**Critical — Unauthorized confidential key derivation output without required participant authorization.**

The victim calls `request_app_private_key` with `AppPublicKey(app_pk)` where `app_pk = app_sk · G1`. The correct CKD output satisfies `big_c = big_s + app_pk · y` and `big_y = y · G1`, so the victim recovers `big_s = big_c − app_sk · big_y` (the BLS signature over the app ID under the master secret).

An attacker who controls one attested participant can instead submit `big_y = G1`, `big_c = T + app_pk` for any chosen point `T`. The victim then computes:

```
k = big_c − app_sk · big_y
  = T + app_pk − app_sk · G1
  = T + app_sk·G1 − app_sk·G1
  = T
```

The attacker chose `T`, so they know the victim's derived secret. `app_pk` is visible on-chain in the stored `CKDRequest`, so the attacker can craft the forged response before the legitimate nodes respond. Because `resolve_yields_for` accepts the first call that matches the request key and drains the queue, the forged response wins the race.

---

### Likelihood Explanation

Requires exactly one attested MPC participant to behave maliciously — well below the threshold. The threshold security model tolerates up to `threshold − 1` Byzantine participants; this attack requires only one. TEE attestation proves the node ran correct code at attestation time but does not prevent that node from making arbitrary subsequent contract calls. The `app_pk` needed to craft the forged `big_c` is stored in the on-chain `CKDRequest` and is publicly readable.

---

### Recommendation

Apply the same response-binding logic to `AppPublicKey` that already exists for `AppPublicKeyPV`. For the non-PV variant the G2 component of the app key is absent, so the exact pairing equation cannot be reused. Options:

1. **Require `AppPublicKeyPV` for all CKD requests** — deprecate the unverifiable `AppPublicKey` variant entirely.
2. **Add a threshold-aggregation layer at the contract level** — require `threshold` independent `respond_ckd` calls with matching responses before resolving the yield (analogous to how threshold signing works off-chain).
3. **Bind the response to the master public key** — require the node to include a BLS proof-of-knowledge or a Schnorr proof that `big_c` was computed using the network's master secret, verifiable against the stored `public_key`.

---

### Proof of Concept

```rust
// Sandbox unit test sketch (no TEE infrastructure needed):
// 1. Setup contract with Bls12381 domain.
// 2. Victim calls request_app_private_key with AppPublicKey(app_pk).
// 3. Attacker (attested participant) calls respond_ckd with:
//      big_y = G1 generator
//      big_c = T + app_pk   (T is any chosen point; app_pk is read from the stored CKDRequest)
// 4. Contract accepts (AppPublicKey arm is a no-op).
// 5. Victim's callback fires with the forged (big_y, big_c).
// 6. Victim computes k = big_c - app_sk * big_y = T.
// 7. Assert k == T  =>  attacker controls the derived key.
```

The existing test `respond_ckd__should_succeed_when_response_is_valid_and_request_exists` already demonstrates that `CKDResponse { big_y: [1u8;48], big_c: [2u8;48] }` (random bytes, not a valid protocol output) is accepted without error for an `AppPublicKey` request: [6](#0-5)

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

**File:** crates/contract/src/lib.rs (L3404-3441)
```rust
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

**File:** crates/contract/src/pending_requests.rs (L66-88)
```rust
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
