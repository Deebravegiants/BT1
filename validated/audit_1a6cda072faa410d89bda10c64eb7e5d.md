### Title
Missing CKD Output Verification for `AppPublicKey` Variant Allows Malicious Participant to Inject Arbitrary Key Material - (File: crates/contract/src/lib.rs)

### Summary
`respond_ckd` conditionally skips cryptographic output verification when the request uses the `AppPublicKey` variant, mirroring the external report's pattern exactly: a special-case branch bypasses a required validation, allowing a single malicious attested participant to inject an arbitrary CKD response that the contract accepts without any correctness check.

### Finding Description

In `respond_ckd`, the `ckd_output_check` guard is wrapped in a match arm that fires only for `AppPublicKeyPV`:

```rust
// crates/contract/src/lib.rs  lines 675-682
match &request.app_public_key {
    dtos::CKDAppPublicKey::AppPublicKey(_) => {}          // ← no verification
    dtos::CKDAppPublicKey::AppPublicKeyPV(app_pk) => {
        if !ckd_output_check(&request.app_id, &response, app_pk, &public_key) {
            env::panic_str("CKD output check failed");
        }
    }
}
``` [1](#0-0) 

When the variant is `AppPublicKey`, the arm is a no-op: the response is passed directly to `resolve_yields_for` with zero cryptographic verification of its contents. [2](#0-1) 

The `respond` (ECDSA/EdDSA) path always verifies the signature against the derived public key before resolving the yield. [3](#0-2) 

The structural parallel to the external report is exact:

| External report (`ensureMaxLocking`) | This codebase (`respond_ckd`) |
|---|---|
| Check skipped when `requireExpiryTs == 0` | Check skipped when variant is `AppPublicKey` |
| Any vipLevel 1-6 gets infinite lock | Any attested participant injects arbitrary key material |
| Missing: `vipLevel == 7` guard | Missing: output correctness guard for `AppPublicKey` |

The caller is already gated by `assert_caller_is_attested_participant_and_protocol_active()`, so the attacker must be a legitimate (but Byzantine) participant — strictly below the signing threshold is sufficient because a single node can win the race to resolve the yield. [4](#0-3) 

### Impact Explanation

`pending_requests::resolve_yields_for` resolves the yield on the first valid call; subsequent calls for the same request fail. A single malicious attested participant who races honest nodes can therefore substitute an arbitrary `CKDResponse` for any `AppPublicKey`-variant request. The user's application receives fabricated key material instead of the genuine MPC-derived output. Depending on how the application uses the returned key (e.g., encrypting secrets, deriving wallet keys), this constitutes a confidential key derivation output produced without the required honest-majority authorization — matching the Critical/Medium allowed impacts for request-lifecycle and CKD integrity invariants.

### Likelihood Explanation

The attack requires one Byzantine attested participant who can submit a transaction slightly ahead of honest nodes. NEAR block times are ~1 second; a participant co-located with a validator or with a fast RPC connection can reliably win the race. No threshold collusion, no TEE break, and no privileged operator access is needed — a single compromised or malicious node suffices.

### Recommendation

Apply the output correctness check unconditionally for all CKD variants, or add an equivalent verification path for `AppPublicKey` that does not depend on the presence of `app_pk`. At minimum, document explicitly why `AppPublicKey` responses are intentionally unverified on-chain and what off-chain mechanism compensates, so the asymmetry is not silently inherited by future code.

### Proof of Concept

1. User calls `request_app_private_key` with `CKDRequestArgs { app_public_key: AppPublicKey(pk), … }`.
2. Contract stores the pending yield; honest MPC nodes begin computing the real CKD output.
3. Malicious attested participant constructs a `CKDResponse` containing arbitrary (attacker-chosen) key material.
4. Malicious participant calls `respond_ckd(request, fabricated_response)` before honest nodes.
5. Contract enters the `AppPublicKey(_) => {}` branch — no `ckd_output_check` is executed.
6. `resolve_yields_for` resolves the yield with the fabricated response; the user's callback receives attacker-controlled key material.
7. All subsequent honest `respond_ckd` calls for the same request fail because the yield is already resolved.

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

**File:** crates/contract/src/lib.rs (L684-688)
```rust
        pending_requests::resolve_yields_for(
            &mut self.pending_ckd_requests,
            &request,
            serde_json::to_vec(&response).unwrap(),
        )
```
