### Title
Missing Cryptographic Output Verification for `AppPublicKey` CKD Responses Allows Byzantine Participant to Deliver Attacker-Controlled Key - (File: crates/contract/src/lib.rs)

### Summary

`respond_ckd` enforces a cryptographic output check (`ckd_output_check`) only for the `AppPublicKeyPV` variant of CKD requests, while the `AppPublicKey` (privately-verifiable, legacy) variant receives no on-chain verification. A single Byzantine attested participant — strictly below the signing threshold — can race the honest nodes and submit an arbitrary, attacker-controlled CKD response for any pending `AppPublicKey` request. The contract accepts it unconditionally, delivering a forged key to the user.

### Finding Description

`respond` (sign) and `respond_verify_foreign_tx` both verify the cryptographic correctness of the submitted response before resolving the pending yield queue: [1](#0-0) 

`respond_verify_foreign_tx` similarly verifies the ECDSA signature against the root public key before calling `resolve_yields_for`: [2](#0-1) 

`respond_ckd`, however, applies `ckd_output_check` **only** for the `AppPublicKeyPV` variant. The `AppPublicKey` arm is an explicit no-op: [3](#0-2) 

Because `resolve_yields_for` drains the entire fan-out queue and resumes every waiting yield with the supplied bytes, the first caller to invoke `respond_ckd` with a matching `CKDRequest` key wins unconditionally for `AppPublicKey` requests: [4](#0-3) 

The `AppPublicKey` variant is still a supported, production-facing path (described as "legacy" but not removed): [5](#0-4) 

### Impact Explanation

A single Byzantine attested participant can:
1. Observe a pending `AppPublicKey` CKD request in the contract's `pending_ckd_requests` map.
2. Construct a `CKDResponse` containing a `(big_y, big_c)` pair that encodes an attacker-controlled key.
3. Call `respond_ckd` before the honest leader node does. The contract performs no cryptographic check and calls `resolve_yields_for`, resuming every queued yield with the forged response.
4. The user's `request_app_private_key` promise resolves with the attacker-controlled key. The attacker can decrypt any ciphertext the user subsequently produces with that key.

This is **confidential key derivation output without the required participant authorization** — the threshold guarantee is bypassed for the entire `AppPublicKey` code path.

### Likelihood Explanation

- The attacker must be an attested participant (TEE attestation required), which is a meaningful barrier.
- However, a Byzantine participant that has passed attestation (e.g., running modified firmware that passes measurement checks, or a participant whose TEE is compromised) satisfies this condition and is explicitly within the stated threat model ("Byzantine participant strictly below the signing threshold").
- The race window is the block-time gap between the honest leader computing the response off-chain and submitting it on-chain. An adversarial participant with a network advantage or a faster submission path can reliably win this race.
- `AppPublicKey` is the legacy variant and may still be used by older integrations.

### Recommendation

Apply the same `ckd_output_check` (or an equivalent binding check) to the `AppPublicKey` arm of `respond_ckd`, or reject `AppPublicKey` responses on-chain entirely and require callers to migrate to `AppPublicKeyPV`. If on-chain verification is cryptographically impossible for `AppPublicKey` (because it requires the user's private key), the contract should document this explicitly and consider deprecating the variant in favour of the publicly-verifiable `AppPublicKeyPV` path, which already has the check.

### Proof of Concept

1. Alice calls `request_app_private_key` with `CKDAppPublicKey::AppPublicKey(pk)` and `domain_id` pointing to a BLS12-381 CKD domain. A `CKDRequest` is inserted into `pending_ckd_requests`.
2. Mallory (an attested participant, but Byzantine) observes the pending request on-chain.
3. Mallory constructs a `CKDResponse { big_y: attacker_y, big_c: attacker_c }` where `attacker_y` is a BLS point Mallory controls.
4. Mallory calls `respond_ckd(request, forged_response)`. The contract executes:
   - `assert_caller_is_signer()` — passes (Mallory is a signer).
   - `is_running_or_resharing()` — passes.
   - `accept_requests` — passes.
   - `assert_caller_is_attested_participant_and_protocol_active()` — passes (Mallory is attested).
   - `match &request.app_public_key { AppPublicKey(_) => {} ... }` — **no check performed**.
   - `resolve_yields_for(...)` — resumes Alice's yield with the forged response.
5. Alice's `request_app_private_key` promise resolves with Mallory's key. Mallory can decrypt any data Alice encrypts under it. [6](#0-5)

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

**File:** crates/contract/src/lib.rs (L718-753)
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

        pending_requests::resolve_yields_for(
            &mut self.pending_verify_foreign_tx_requests,
            &request,
            serde_json::to_vec(&response).unwrap(),
        )
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

**File:** crates/contract/README.md (L278-282)
```markdown
The `request_app_private_key` request takes the following arguments:

- `derivation_path` (String): the derivation path.
- `app_public_key`: the ephemeral public key to encrypt the generated confidential key. Accepts either a plain G1 point string (privately verifiable, legacy) or a tagged enum with `AppPublicKey` (single G1 point) or `AppPublicKeyPV` (a `{pk1, pk2}` pair for public verifiability).
- `domain_id` (integer): the domain ID that identifies the key and signature scheme to use to generate the confidential key
```
