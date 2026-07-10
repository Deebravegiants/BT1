### Title
Single Byzantine Participant Can Deliver Unverified CKD Response for `AppPublicKey` Requests - (File: `crates/contract/src/lib.rs`)

### Summary

The `respond_ckd` function performs cryptographic output verification only for the `AppPublicKeyPV` (publicly verifiable) CKD variant. For the legacy `AppPublicKey` variant, the verification branch is entirely empty. A single attested participant — strictly below the signing threshold — can call `respond_ckd` with an arbitrary fabricated `CKDResponse` for any pending `AppPublicKey` request, and the contract will accept and deliver it to the user without any cryptographic check, bypassing the threshold requirement entirely.

### Finding Description

In `respond_ckd`, after retrieving the domain's BLS12-381 public key, the contract branches on the request's app public key type:

```rust
match &request.app_public_key {
    dtos::CKDAppPublicKey::AppPublicKey(_) => {}   // ← no verification
    dtos::CKDAppPublicKey::AppPublicKeyPV(app_pk) => {
        if !ckd_output_check(&request.app_id, &response, app_pk, &public_key) {
            env::panic_str("CKD output check failed");
        }
    }
}
``` [1](#0-0) 

For `AppPublicKeyPV`, `ckd_output_check` verifies that the encrypted response is consistent with the domain public key and the user's ephemeral key pair — a cryptographic proof that the output was legitimately derived. For `AppPublicKey`, the arm is a no-op: the response bytes are serialized and delivered to the user with zero verification.

Compare this with `respond` (for signatures), which always verifies the signature cryptographically before resolving the yield: [2](#0-1) 

The `respond_ckd` caller is only required to be an attested participant: [3](#0-2) 

Because all pending request parameters (`domain_id`, `app_public_key`, `predecessor`, `derivation_path`) are observable on-chain from the original `request_app_private_key` call, a single Byzantine participant can reconstruct the exact `CKDRequest` key, craft any `CKDResponse`, and call `respond_ckd`. The contract resolves the yield immediately via `resolve_yields_for`, delivering the attacker-controlled output to the user. [4](#0-3) 

The `AppPublicKey` variant is described as "privately verifiable" (legacy) — meaning only the user with their secret key can verify the output. However, this is a property of the *user-side* verification, not a reason to skip *contract-side* threshold enforcement. The threshold requirement exists to ensure that the response was computed by t-of-n participants; skipping verification for this variant means a single participant can unilaterally determine what key material the user receives.

### Impact Explanation

**Critical.** A single Byzantine attested participant (below the signing threshold) can substitute the legitimately derived confidential key with key material they control. The user decrypts the response with their ephemeral private key and receives a key that the attacker also knows, giving the attacker full access to the user's derived key material. This is unauthorized confidential key derivation output without the required participant authorization — the threshold requirement is bypassed entirely for all `AppPublicKey` CKD requests.

### Likelihood Explanation

**Medium.** The `AppPublicKey` variant is explicitly supported and documented as the legacy format. The contract README describes it as still accepted. Any single attested participant can exploit this without any collusion. The request parameters needed to construct the matching `CKDRequest` are all observable on-chain.

### Recommendation

Add cryptographic output verification for the `AppPublicKey` variant in `respond_ckd`. If the response cannot be publicly verified on-chain (by design of the privately-verifiable variant), the contract should at minimum require that the response is accompanied by a proof of threshold participation (e.g., a threshold signature over the response), or deprecate the `AppPublicKey` variant in favor of `AppPublicKeyPV` which supports on-chain verification via `ckd_output_check`.

### Proof of Concept

1. User submits `request_app_private_key` with `AppPublicKey` variant (legacy format), attaching 1 yoctoNEAR deposit. The request parameters are visible on-chain.
2. Malicious attested participant reconstructs the `CKDRequest` from on-chain data and crafts a `CKDResponse` containing key material they control (e.g., an encryption of a known key to the user's ephemeral public key).
3. Malicious participant calls `respond_ckd(request, fabricated_response)`. The contract checks only that the caller is an attested participant, then hits the empty `AppPublicKey` match arm — no `ckd_output_check` is called.
4. `resolve_yields_for` resumes the user's yield with the fabricated response bytes.
5. The user receives and decrypts the response, obtaining a key that the attacker also knows. The attacker now has access to the same derived key material as the user, without the required threshold of participants ever participating in the computation.

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

**File:** crates/contract/src/lib.rs (L654-667)
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

**File:** crates/contract/src/lib.rs (L684-689)
```rust
        pending_requests::resolve_yields_for(
            &mut self.pending_ckd_requests,
            &request,
            serde_json::to_vec(&response).unwrap(),
        )
    }
```
