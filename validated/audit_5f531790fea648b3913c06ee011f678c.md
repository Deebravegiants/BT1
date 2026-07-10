### Title
Single Attested Participant Can Deliver Fabricated CKD Response for `AppPublicKey` Requests Without Threshold Authorization - (File: crates/contract/src/lib.rs)

### Summary

`respond_ckd` in `MpcContract` performs **no cryptographic verification** of the `CKDResponse` when the pending request uses the `CKDAppPublicKey::AppPublicKey` variant. A single attested participant (strictly below the signing threshold) can call `respond_ckd` with an entirely fabricated `(big_y, big_c)` pair and the contract will accept it, resolve all queued yields for that request, and deliver the attacker-controlled output to every waiting caller as if it were a genuine threshold-computed confidential key.

### Finding Description

In `respond_ckd`, the contract branches on the request's `app_public_key` variant:

```rust
match &request.app_public_key {
    dtos::CKDAppPublicKey::AppPublicKey(_) => {}          // ← no check at all
    dtos::CKDAppPublicKey::AppPublicKeyPV(app_pk) => {
        if !ckd_output_check(&request.app_id, &response, app_pk, &public_key) {
            env::panic_str("CKD output check failed");
        }
    }
}
``` [1](#0-0) 

When the variant is `AppPublicKey` (the legacy, non-publicly-verifiable mode), the arm is an empty no-op. The response is immediately forwarded to `resolve_yields_for`, which drains every queued yield for that request key and delivers the raw `CKDResponse` bytes to all waiting callers. [2](#0-1) 

By contrast:
- `respond` (ECDSA/EdDSA) always verifies the signature cryptographically against the derived public key before resolving.
- `respond_ckd` with `AppPublicKeyPV` runs a BLS12-381 pairing check (`ckd_output_check`) that proves the response is consistent with the MPC public key and the app's ephemeral key pair.
- `respond_ckd` with `AppPublicKey` does nothing. [3](#0-2) [4](#0-3) 

The `AppPublicKey` variant is the documented legacy mode and is actively used in production tooling: [5](#0-4) 

### Impact Explanation

A single attested participant (one node, strictly below the reconstruction threshold) can:

1. Observe any pending `AppPublicKey`-type CKD request on-chain.
2. Call `respond_ckd` with an arbitrary `CKDResponse { big_y: <attacker_value>, big_c: <attacker_value> }`.
3. The contract resolves all queued yields for that request with the fabricated output.
4. Every caller waiting on that request receives an attacker-controlled confidential key instead of the genuine threshold-derived one.

This is **unauthorized confidential key derivation output without the required participant authorization**: the threshold protocol is bypassed entirely — one participant's unilateral action substitutes for the collective threshold computation. The user's derived application key is fully under the attacker's control, enabling the attacker to know or dictate the secret the user believes is confidentially derived.

This matches the allowed impact: **Critical — confidential key derivation output without the required participant authorization.**

### Likelihood Explanation

- The attacker must be a single attested participant in the current epoch — a realistic threat in the explicit Byzantine-below-threshold model.
- `AppPublicKey` (legacy mode) is the default path in the example CLI and is likely the dominant usage pattern until `AppPublicKeyPV` is universally adopted.
- No threshold collusion is required; one node acting alone is sufficient.
- The attack is silent: the contract emits no error, the request is cleaned up normally, and the victim receives a well-formed (but fabricated) response struct.

### Recommendation

Apply the same cryptographic binding to `AppPublicKey` responses that `AppPublicKeyPV` already enforces. Since `AppPublicKey` provides only a single G1 point (no G2 component for a pairing check), the contract cannot verify the response in zero-knowledge. The options are:

1. **Deprecate `AppPublicKey` entirely** and require all callers to use `AppPublicKeyPV`, which supports the on-chain pairing check.
2. **Require threshold-many identical responses** before resolving, so a single participant cannot unilaterally determine the output (analogous to how the signing protocol requires threshold agreement before `respond` is called).
3. **Reject `AppPublicKey` requests at `respond_ckd`** with an explicit error until a verifiable alternative is in place.

### Proof of Concept

```
1. Alice calls request_app_private_key({
       derivation_path: "m/0",
       app_public_key: AppPublicKey(<alice_g1_point>),
       domain_id: 0
   }) with 1 yoctoNEAR attached.
   → Contract stores the pending CKD request and queues Alice's yield.

2. Mallory (a single attested participant, account: mallory.near) calls:
   respond_ckd(
       request = <the CKDRequest matching Alice's submission>,
       response = CKDResponse {
           big_y: Bls12381G1PublicKey([0xde, 0xad, ...]),  // attacker-chosen
           big_c: Bls12381G1PublicKey([0xbe, 0xef, ...]),  // attacker-chosen
       }
   )

3. Contract execution path (lib.rs:675-688):
   - assert_caller_is_attested_participant_and_protocol_active() → passes (Mallory is a participant)
   - match AppPublicKey(_) => {}  ← NO CHECK
   - resolve_yields_for(...) → Alice's yield is resumed with Mallory's fabricated bytes

4. Alice's promise resolves with the attacker-controlled CKDResponse.
   Alice decrypts big_c using her ephemeral private key and obtains
   a key that Mallory chose, not the genuine MPC-derived secret.
``` [6](#0-5) [7](#0-6) [8](#0-7)

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

**File:** crates/contract/src/primitives/ckd.rs (L80-101)
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
```

**File:** crates/ckd-example-cli/src/ckd.rs (L31-34)
```rust
    } else {
        let (scalar, pk) = generate_ephemeral_key(&mut OsRng);
        (scalar, CKDAppPublicKey::AppPublicKey(pk))
    };
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
