### Title
`respond_ckd` Accepts Unverified Response for `AppPublicKey` Variant, Permanently Consuming Pending CKD Request - (File: `crates/contract/src/lib.rs`)

---

### Summary

`respond_ckd` in the MPC contract performs no cryptographic verification of the `CKDResponse` when the request uses the `AppPublicKey` (privately verifiable) variant. A single Byzantine attested participant — strictly below the signing threshold — can call `respond_ckd` with an arbitrary garbage `CKDResponse`, which irreversibly removes the pending CKD request from contract state and delivers the garbage key to the user. The user's confidential key derivation is permanently corrupted and the request cannot be re-served by the honest MPC network.

---

### Finding Description

The `respond_ckd` function in `crates/contract/src/lib.rs` handles two variants of CKD app public keys:

```rust
match &request.app_public_key {
    dtos::CKDAppPublicKey::AppPublicKey(_) => {}          // NO CHECK — falls through
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
``` [1](#0-0) 

For `AppPublicKeyPV` (publicly verifiable), the contract calls `ckd_output_check`, which verifies the BLS12-381 pairing equation `e(big_c, g2) = e(big_y, app_pk2) · e(hash_point, public_key)` on-chain. [2](#0-1) 

For `AppPublicKey` (privately verifiable), the match arm is **empty** — no verification of any kind is performed. The function immediately proceeds to `resolve_yields_for`, which:

1. Removes the pending CKD request entry from `pending_ckd_requests` (irreversible)
2. Calls `env::promise_yield_resume` for every queued yield with the attacker-supplied garbage bytes [3](#0-2) 

By contrast, `respond` (for signatures) always verifies the ECDSA or EdDSA signature cryptographically before calling `resolve_yields_for`, and `respond_verify_foreign_tx` similarly verifies the signature before resolving. [4](#0-3) 

The analog to the original report is exact: just as `redeem` in Redeemer.sol burns iPT tokens even when `holdings[u][m]` is zero (prerequisite state not set up), `respond_ckd` permanently consumes the pending CKD request even when the response is cryptographically invalid (prerequisite — a valid MPC-computed response — has not been established).

---

### Impact Explanation

**Medium.** A single Byzantine attested participant (below the signing threshold) can:

1. Observe any pending `AppPublicKey` CKD request in contract state.
2. Call `respond_ckd` with an arbitrary `CKDResponse { big_y: <garbage>, big_c: <garbage> }`.
3. The contract accepts it unconditionally, removes the pending request from `pending_ckd_requests`, and resumes all queued yields with the garbage bytes.
4. The user's `request_app_private_key` transaction completes with a garbage confidential key.
5. Because the `AppPublicKey` variant is privately verifiable, the user cannot distinguish a garbage response from a valid one without attempting to use the key — and the contract provides no on-chain signal of invalidity.
6. The pending request is permanently gone; the honest MPC network cannot re-serve it.

This breaks the request-lifecycle and execution-flow safety invariant: a pending CKD request should only be resolved with a cryptographically valid MPC-computed response. [5](#0-4) 

---

### Likelihood Explanation

**Medium.** The attacker must be an attested participant (registered in the MPC network with a valid TEE attestation). This is a meaningful barrier, but it requires only **one** Byzantine participant — not a threshold-sized coalition. In a network with `n` participants, any single compromised or malicious node can execute this attack against any user's privately verifiable CKD request at any time the contract is in Running or Resharing state. [6](#0-5) 

---

### Recommendation

Apply the same pattern used for `AppPublicKeyPV`: require a verifiable proof that the response is correctly formed before calling `resolve_yields_for`. Since the `AppPublicKey` variant is privately verifiable (the app holds the ephemeral secret `a`), on-chain verification is not possible with only `pk1 = a·G1`. The recommended mitigations are:

1. **Deprecate the `AppPublicKey` variant** in favor of `AppPublicKeyPV`, which supports on-chain verification via the BLS12-381 pairing check. The `ckd-example-cli` already supports `--publicly-verifiable`.
2. **If `AppPublicKey` must be retained**, require that `respond_ckd` for this variant be called by a threshold-quorum of participants (e.g., require `t` matching responses before resolving), so a single Byzantine node cannot corrupt the output unilaterally.
3. At minimum, add a guard that rejects `respond_ckd` calls for `AppPublicKey` requests unless the response passes a basic structural validity check (e.g., both `big_y` and `big_c` are valid BLS12-381 G1 points in the prime-order subgroup).

---

### Proof of Concept

1. User calls `request_app_private_key` with `AppPublicKey` variant. A pending entry is created in `pending_ckd_requests`. [7](#0-6) 

2. Byzantine attested participant calls `respond_ckd(ckd_request, CKDResponse { big_y: [0u8;48], big_c: [0u8;48] })`.

3. The contract reaches the match at line 675. The `AppPublicKey(_) => {}` arm executes — no check, no panic. [8](#0-7) 

4. `resolve_yields_for` removes the entry from `pending_ckd_requests` and resumes the user's yield with the garbage bytes. [9](#0-8) 

5. The user's `request_app_private_key` transaction resolves with `CKDResponse { big_y: [0;48], big_c: [0;48] }`. The user decrypts a garbage key. The honest MPC network's response, when it eventually arrives, finds `RequestNotFound` and returns an error — the request has already been consumed.

The existing unit test `respond_ckd__should_succeed_when_response_is_valid_and_request_exists` demonstrates that `respond_ckd` with `AppPublicKey` and an arbitrary `CKDResponse { big_y: [1u8;48], big_c: [2u8;48] }` succeeds without any verification, confirming the root cause. [10](#0-9)

### Citations

**File:** crates/contract/src/lib.rs (L469-511)
```rust
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

        let request = CKDRequest::new(
            request.app_public_key,
            domain_id,
            &predecessor,
            &request.derivation_path,
        );

        let callback_gas = Gas::from_tgas(
            self.config
                .return_ck_and_clean_state_on_success_call_tera_gas,
        );

        let callback_args = serde_json::to_vec(&(&request,)).unwrap();
        self.enqueue_yield_request(
            method_names::RETURN_CK_AND_CLEAN_STATE_ON_SUCCESS,
            callback_args,
            callback_gas,
            move |this, id| this.add_ckd_request(request, id),
        );
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

**File:** crates/contract/src/lib.rs (L653-689)
```rust
    #[handle_result]
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
