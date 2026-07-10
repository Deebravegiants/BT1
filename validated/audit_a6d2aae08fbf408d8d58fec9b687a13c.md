Looking at the external report's vulnerability class — **asymmetric safety check**: a protection mechanism applies to one code path but is absent from an equivalent code path — I need to find the same pattern in the NEAR MPC contract.

The key asymmetry I found is in `respond_ckd` vs `respond` in `crates/contract/src/lib.rs`.

---

### Title
Missing Cryptographic Output Verification in `respond_ckd` for `AppPublicKey` Variant Allows a Single Byzantine Participant to Forge CKD Responses - (File: `crates/contract/src/lib.rs`)

### Summary

`respond` (for threshold signatures) always cryptographically verifies the submitted signature against the derived public key before resolving the user's yield. `respond_ckd` (for Confidential Key Derivation) only verifies the output for the `AppPublicKeyPV` variant; for the `AppPublicKey` variant it performs **no output check at all**. A single Byzantine attested participant can therefore call `respond_ckd` with an arbitrary forged CKD output for the `AppPublicKey` variant and the contract will accept and deliver it to the user, bypassing the threshold requirement entirely.

### Finding Description

In `respond` the contract derives the expected public key from the stored root key and the request's tweak, then verifies the submitted signature against it:

```rust
// crates/contract/src/lib.rs  ~line 597-607
let expected_public_key =
    derive_key_secp256k1(&affine, &request.tweak).map_err(RespondError::from)?;
let payload_hash = request.payload.as_ecdsa().expect("Payload is not ECDSA");
near_mpc_signature_verifier::verify_ecdsa_signature(
    signature_response,
    payload_hash,
    &expected_public_key,
).is_ok()
```

This means even if a single Byzantine participant calls `respond` with a forged signature, the cryptographic check rejects it. The threshold is implicitly enforced because only a genuine t-of-n computation can produce a valid signature.

In `respond_ckd` the analogous check is **absent for the `AppPublicKey` variant**:

```rust
// crates/contract/src/lib.rs  ~line 675-682
match &request.app_public_key {
    dtos::CKDAppPublicKey::AppPublicKey(_) => {}          // ← NO CHECK
    dtos::CKDAppPublicKey::AppPublicKeyPV(app_pk) => {
        if !ckd_output_check(&request.app_id, &response, app_pk, &public_key) {
            env::panic_str("CKD output check failed");
        }
    }
}
```

After this match, the contract immediately calls `resolve_yields_for` to deliver whatever `response` was submitted. There is no threshold-agreement check anywhere in `respond_ckd`; any single attested participant can call it and win the race to deliver a response.

The `AppPublicKeyPV` ("publicly verifiable") variant is protected because its output is designed to be verifiable on-chain. The `AppPublicKey` ("private") variant is encrypted to the app's public key, so the contract cannot verify it — but this design gap means the threshold guarantee is silently dropped for that variant.

### Impact Explanation

A single Byzantine attested participant (strictly below the signing threshold) can:

1. Observe a pending `CKDRequest` with `AppPublicKey` in the contract's `pending_ckd_requests` map.
2. Construct an arbitrary `CKDResponse` — e.g., one whose ciphertext decrypts to a key the attacker controls.
3. Call `respond_ckd` before honest nodes do. The contract accepts the response without any cryptographic check and delivers it to the user via `resolve_yields_for`.

The user receives a derived key that does not correspond to the genuine MPC-controlled secret. Any assets sent to an address derived from this forged key are either unrecoverable (if the key is random) or stolen (if the attacker chose a key they control). This is **unauthorized confidential key derivation output without the required participant authorization**.

### Likelihood Explanation

The attacker only needs to be a single attested participant — well below the signing threshold. Attested participants are a known, bounded set, but the TEE attestation model assumes individual nodes may be Byzantine. The attack requires no collusion, no network-level interference, and no privileged operator access: the attacker simply submits a contract transaction before honest nodes do. During any period of network latency or node downtime, the window is open.

### Recommendation

For the `AppPublicKey` variant, the contract cannot verify the ciphertext directly. Two mitigations are possible:

1. **Require a threshold of matching responses before resolving.** Collect `respond_ckd` calls and only resolve the yield once `t` participants have submitted identical responses (as identified by a hash of the response). This mirrors how threshold signatures implicitly require t-of-n agreement.
2. **Deprecate the unverifiable `AppPublicKey` variant** in favour of `AppPublicKeyPV`, which can be verified on-chain and already has the `ckd_output_check` guard.

### Proof of Concept

1. User calls `request_app_private_key` with `AppPublicKey(attacker_controlled_pk)` — or with any `AppPublicKey`.
2. The contract stores the request in `pending_ckd_requests` and creates a yield.
3. Byzantine participant P (a single node) constructs `CKDResponse` whose ciphertext decrypts (under `attacker_controlled_pk`) to a key the attacker knows.
4. P calls `respond_ckd(request, forged_response)`.
5. The contract executes:
   - `assert_caller_is_signer()` — passes (P is a signer).
   - `is_running_or_resharing()` — passes.
   - `accept_requests` — passes.
   - `assert_caller_is_attested_participant_and_protocol_active()` — passes (P is attested).
   - `match &request.app_public_key { AppPublicKey(_) => {} … }` — **no check executed**.
   - `resolve_yields_for(…, serde_json::to_vec(&forged_response))` — delivers forged key to user.
6. User receives a derived key controlled by the attacker; any funds sent to the corresponding address are stolen. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

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

**File:** crates/contract/src/lib.rs (L646-651)
```rust
        pending_requests::resolve_yields_for(
            &mut self.pending_signature_requests,
            &request,
            serde_json::to_vec(&response).unwrap(),
        )
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
