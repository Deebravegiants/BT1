### Title
Missing Response Validation for `AppPublicKey` CKD Requests Allows Single Byzantine Participant to Forge Derived Key Output - (File: crates/contract/src/lib.rs)

### Summary

The `respond_ckd` contract method validates the CKD response only when the request uses the `AppPublicKeyPV` variant. When the `AppPublicKey` variant is used, **no cryptographic check is performed on the response**, allowing any single attested participant to submit an arbitrary CKD response that is immediately accepted and delivered to the requesting user.

### Finding Description

In `respond_ckd`, the contract branches on the `app_public_key` field of the request:

```rust
match &request.app_public_key {
    dtos::CKDAppPublicKey::AppPublicKey(_) => {}   // ← no validation at all
    dtos::CKDAppPublicKey::AppPublicKeyPV(app_pk) => {
        if !ckd_output_check(&request.app_id, &response, app_pk, &public_key) {
            env::panic_str("CKD output check failed");
        }
    }
}
```

For `AppPublicKeyPV`, `ckd_output_check` cryptographically verifies that the returned derived key is consistent with the BLS12-381 root public key and the request parameters. For `AppPublicKey`, the arm is a no-op — the response is accepted unconditionally and immediately forwarded to all waiting callers via `resolve_yields_for`. [1](#0-0) 

This is structurally identical to the GMX ADL issue: just as ADL orders set `acceptablePrice = 0` and `minOutputAmount = 0` with no post-execution bounds check, `respond_ckd` for `AppPublicKey` sets no lower or upper bound on what the response may contain.

Contrast with `respond` for threshold signatures, which always validates the produced signature against the expected derived public key before resolving yields: [2](#0-1) 

The threshold property for signatures is enforced *cryptographically*: a single node cannot produce a valid ECDSA/EdDSA signature without threshold cooperation, so the on-chain check acts as a final gate. For `AppPublicKey` CKD there is no equivalent gate — the response is an opaque blob that the contract accepts without any structural or cryptographic constraint.

### Impact Explanation

A single Byzantine attested participant (strictly below the signing threshold) can call `respond_ckd` with a fabricated `CKDResponse` for any pending `AppPublicKey` CKD request. The contract will:

1. Accept the response without any validation.
2. Immediately resolve all queued yield-resume promises for that request key, delivering the forged derived key to every waiting caller.

The user receives a derived key that was not produced by the honest MPC network. If the user subsequently uses that key to receive assets on a foreign chain (the primary use-case of CKD), those assets are permanently inaccessible or controlled by the attacker. This constitutes a **critical bypass of the threshold-signature requirement** for CKD operations and a direct path to permanent loss of funds. [3](#0-2) 

### Likelihood Explanation

Any single attested participant can exploit this. Attestation is a prerequisite, but it is a reachable condition for a Byzantine node that has legitimately joined the network. The attacker does not need to collude with other participants or compromise any threshold of nodes. The attack is triggered by a standard contract call to `respond_ckd` with a crafted response, which is a normal participant operation. The window is any time a `AppPublicKey` CKD request is pending. [4](#0-3) 

### Recommendation

Apply the same response-validation discipline to `AppPublicKey` that already exists for `AppPublicKeyPV`. If `AppPublicKey` lacks the cryptographic structure needed for `ckd_output_check`, introduce an equivalent verifiable commitment at request time (analogous to `AppPublicKeyPV`) so the contract can always verify the response before resolving yields. At minimum, document why `AppPublicKey` is safe to skip validation for, or remove the variant if it cannot be made safe. [5](#0-4) 

### Proof of Concept

1. Honest user calls `request_app_private_key` with `AppPublicKey` variant and attaches the required deposit. A `CKDRequest` is enqueued and a yield promise is created.
2. A Byzantine attested participant calls `respond_ckd(request, forged_response)` where `forged_response` contains an attacker-controlled BLS12-381 public key.
3. The contract executes the `AppPublicKey` arm (no-op), skips all validation, and calls `resolve_yields_for`, which resumes the user's yield with the forged key.
4. The user's callback receives the forged derived key. Any assets sent to the address derived from that key are under the attacker's control or permanently lost. [6](#0-5)

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

**File:** crates/contract/src/lib.rs (L563-573)
```rust
    #[handle_result]
    pub fn respond(
        &mut self,
        request: SignatureRequest,
        response: dtos::SignatureResponse,
    ) -> Result<(), Error> {
        let signer = Self::assert_caller_is_signer();

        log!("respond: signer={}, request={:?}", &signer, &request);

        self.assert_caller_is_attested_participant_and_protocol_active();
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

**File:** crates/contract/src/lib.rs (L654-689)
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
