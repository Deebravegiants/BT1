### Title
Single Attested Participant Can Forge Non-PV CKD Response, Bypassing Threshold Requirement - (File: `crates/contract/src/lib.rs`)

---

### Summary

`respond_ckd` accepts a `CKDResponse` for `AppPublicKey` (non-publicly-verifiable) requests with **zero cryptographic verification** of the response content. A single Byzantine attested participant — strictly below the signing threshold — can submit an arbitrary forged `CKDResponse` for any pending non-PV CKD request, race the honest nodes, and deliver a wrong derived key to the user. This bypasses the threshold requirement entirely for the legacy CKD path.

---

### Finding Description

In `respond_ckd`, the contract branches on the request's `app_public_key` variant: [1](#0-0) 

For `AppPublicKeyPV` (publicly verifiable), `ckd_output_check` is called against the master BLS12-381 public key, cryptographically binding the response to the correct threshold computation. For `AppPublicKey` (privately verifiable / legacy), the branch body is **empty** — no check whatsoever is performed on `big_y` or `big_c`. [2](#0-1) 

After the empty branch, `resolve_yields_for` immediately removes the pending request from the map and resumes every queued yield with whatever bytes were passed in. The first call wins; all subsequent honest responses receive `RequestNotFound`.

Compare this with `respond` for ECDSA/EdDSA signatures, where the contract verifies the signature against the derived public key before accepting it: [3](#0-2) 

The asymmetry is clear: signatures are verified on-chain (a forged signature is rejected), PV-CKD responses are verified on-chain, but non-PV CKD responses are accepted unconditionally from any single attested participant.

The `resolve_yields_for` helper that drains the entire fan-out queue on first call: [4](#0-3) 

---

### Impact Explanation

A single Byzantine attested participant can:

1. Monitor the contract for pending `AppPublicKey` CKD requests.
2. Call `respond_ckd(request, CKDResponse { big_y: <arbitrary>, big_c: <arbitrary> })` before the honest MPC nodes.
3. The contract accepts the forged response — no verification is performed.
4. `resolve_yields_for` removes the request from `pending_ckd_requests` and resumes the user's yield with the forged bytes.
5. Subsequent honest responses fail with `RequestNotFound` — the forged response is the only one delivered.
6. The user receives a wrong derived key. Any data encrypted to the correct derived key becomes permanently undecryptable; any address derived from the wrong key and funded by the user results in permanent loss of those funds.

This is **confidential key derivation output without the required participant authorization** — a single participant (1-of-n, where the threshold t ≥ 2 is enforced by the contract) forges the CKD output, bypassing the threshold protocol entirely.

---

### Likelihood Explanation

The attacker must be an attested participant (valid TEE attestation and membership in the current epoch). Once that bar is cleared — which is the normal operating condition for any node in the MPC network — exploitation requires only:

- Watching the NEAR chain for `request_app_private_key` calls that use the `AppPublicKey` variant.
- Submitting `respond_ckd` with forged `big_y`/`big_c` before the honest nodes respond.

No collusion, no key leakage, no network-level attack is needed. A single Byzantine node in the participant set can exploit this against every non-PV CKD request.

---

### Recommendation

Add cryptographic verification for `AppPublicKey` (non-PV) responses analogous to what `AppPublicKeyPV` already does. If the contract cannot verify the response without the user's secret key, consider one of:

1. **Require threshold-many identical responses** before accepting: accumulate responses from multiple participants and only resolve the yield once t participants have submitted the same `(big_y, big_c)` pair.
2. **Deprecate `AppPublicKey`** in favor of `AppPublicKeyPV`, which is already verifiable on-chain.
3. **Add a BLS commitment** that allows the contract to verify the response against the master public key without the user's secret.

The minimal diff mirrors the existing PV path:

```rust
match &request.app_public_key {
    dtos::CKDAppPublicKey::AppPublicKey(_) => {
-       // no check
+       // require threshold accumulation or reject
+       return Err(RespondError::UnverifiableLegacyCKDResponse.into());
    }
    dtos::CKDAppPublicKey::AppPublicKeyPV(app_pk) => {
        if !ckd_output_check(&request.app_id, &response, app_pk, &public_key) {
            env::panic_str("CKD output check failed");
        }
    }
}
```

---

### Proof of Concept

1. Alice calls `request_app_private_key({ app_public_key: AppPublicKey(pk), domain_id: 4, derivation_path: "m/0" })` with 1 yoctoNEAR deposit. The request is stored in `pending_ckd_requests`.

2. Byzantine participant Bob observes the pending request on-chain and immediately calls:
   ```
   respond_ckd(
     request = CKDRequest { app_public_key: AppPublicKey(pk), domain_id: 4, ... },
     response = CKDResponse { big_y: [0u8; 48], big_c: [0u8; 48] }
   )
   ```

3. `respond_ckd` reaches the `AppPublicKey` branch — the body is empty, no check is performed.

4. `resolve_yields_for` removes the request from `pending_ckd_requests` and resumes Alice's yield with the forged bytes.

5. When the honest MPC nodes later call `respond_ckd` with the correct response, they receive `Err(RequestNotFound)` — the request is already gone.

6. Alice's callback fires with `CKDResponse { big_y: [0u8; 48], big_c: [0u8; 48] }`. She cannot reconstruct her derived private key. Any funds sent to an address derived from this wrong key are permanently lost. [5](#0-4)

### Citations

**File:** crates/contract/src/lib.rs (L586-650)
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

        pending_requests::resolve_yields_for(
            &mut self.pending_signature_requests,
            &request,
            serde_json::to_vec(&response).unwrap(),
        )
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
