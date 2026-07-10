### Title
Single Attested Participant Can Deliver Fraudulent CKD Response Without Threshold Authorization - (`File: crates/contract/src/lib.rs`)

### Summary

The `respond_ckd` function in the MPC contract allows a single attested participant to unilaterally deliver any arbitrary Confidential Key Derivation (CKD) response when the request uses the `AppPublicKey` variant. No cryptographic verification of the response is performed in this code path. This is directly analogous to the Convex_AMO_V2 custodian issue: a role that should be constrained to participating in a threshold protocol can instead unilaterally perform a sensitive operation (delivering a derived key) that should require threshold-many participants.

### Finding Description

The `respond_ckd` function at `crates/contract/src/lib.rs` performs a conditional verification of the CKD response based on the `app_public_key` variant in the request:

```rust
pub fn respond_ckd(&mut self, request: CKDRequest, response: CKDResponse) -> Result<(), Error> {
    let signer = Self::assert_caller_is_signer();
    // ...
    self.assert_caller_is_attested_participant_and_protocol_active();
    // ...
    match &request.app_public_key {
        dtos::CKDAppPublicKey::AppPublicKey(_) => {}   // ← NO VERIFICATION
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

When `app_public_key` is the `AppPublicKey` variant, the `match` arm is an empty block — the response is accepted and delivered to the user with zero cryptographic validation. The `AppPublicKeyPV` variant correctly calls `ckd_output_check`, but `AppPublicKey` has no equivalent guard.

The access control (`assert_caller_is_attested_participant_and_protocol_active`) only requires that the caller is a single attested participant — it does not enforce that threshold-many participants agreed on the response. The entire threshold security model is bypassed for this code path. [1](#0-0) 

The contrast with `respond` (for regular signatures) is instructive: that function always verifies the submitted signature against the cryptographically derived public key before resolving the yield, making forgery computationally infeasible. [2](#0-1) 

The `assert_caller_is_attested_participant_and_protocol_active` guard only checks that the signer's account key matches a stored TEE attestation and that the signer is in the active participant set — it does not require threshold agreement. [3](#0-2) 

### Impact Explanation

A malicious participant who calls `respond_ckd` with a crafted `CKDResponse` for an `AppPublicKey` request delivers a derived key that the attacker fully controls (they chose the key material). The victim user, expecting a key derived from the MPC threshold secret, instead receives a key whose private component is known only to the attacker. If the user subsequently uses this key to receive funds on a foreign chain (Bitcoin, Ethereum, etc.), the attacker can drain those funds. This constitutes **confidential key derivation output without the required participant authorization** — a Critical impact under the allowed scope.

### Likelihood Explanation

The attack requires a single Byzantine participant below the signing threshold. All pending `CKDRequest` entries are stored on-chain in `pending_ckd_requests` and are publicly readable. The attacker can observe any `AppPublicKey`-variant CKD request, construct a `CKDResponse` containing a key they control, and call `respond_ckd` directly using their NEAR account key (which is registered in their TEE attestation). No TEE compromise is needed — the operator's NEAR account key is used to call the contract method directly, which is the documented and intended mechanism for submitting responses. [4](#0-3) 

The node key is explicitly granted access to all contract methods, including `respond_ckd`. [5](#0-4) 

### Recommendation

Apply `ckd_output_check` unconditionally for all `CKDRequest` variants, or reject `AppPublicKey` requests at the `respond_ckd` entry point if no verifiable public key is present. The `AppPublicKeyPV` variant already demonstrates the correct pattern. If `AppPublicKey` must remain supported for legacy reasons, the contract should require that threshold-many distinct attested participants submit matching responses before resolving the yield, mirroring the off-chain threshold requirement.

### Proof of Concept

1. Attacker is a legitimate attested participant (account `attacker.near`, valid TEE attestation on-chain).
2. User calls `request_app_private_key` with `app_public_key: AppPublicKey(some_key)`, attaching 1 yoctoNEAR deposit. The request is stored in `pending_ckd_requests`.
3. Attacker reads the pending `CKDRequest` from chain state.
4. Attacker constructs a `CKDResponse` containing key material they generated locally (a key they fully control).
5. Attacker calls `respond_ckd(request, fake_response)` directly from `attacker.near`.
6. The contract passes `assert_caller_is_attested_participant_and_protocol_active`, enters the `AppPublicKey` match arm (empty body — no check), and calls `resolve_yields_for`, delivering the fake response to the user.
7. User receives a "derived" app key whose private component is known to the attacker.
8. User deposits funds to an address derived from this key on a foreign chain; attacker sweeps the funds. [1](#0-0)

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

**File:** crates/contract/src/lib.rs (L2423-2434)
```rust
    fn assert_caller_is_signer() -> AccountId {
        let signer_id = env::signer_account_id();
        let predecessor_id = env::predecessor_account_id();

        assert_eq!(
            signer_id, predecessor_id,
            "Caller must be the signer account (signer: {}, predecessor: {})",
            signer_id, predecessor_id
        );

        signer_id
    }
```

**File:** crates/contract/src/tee/tee_state.rs (L469-498)
```rust
    pub(crate) fn is_caller_an_attested_participant(
        &self,
        participants: &Participants,
    ) -> Result<(), AttestationCheckError> {
        let signer_account_pk = env::signer_account_pk();
        let signer_id = env::signer_account_id();

        let info = participants
            .info(&signer_id)
            .ok_or(AttestationCheckError::CallerNotParticipant)?;

        let attestation = self
            .stored_attestations
            .get(&info.tls_public_key)
            .ok_or(AttestationCheckError::AttestationNotFound)?;

        if attestation.node_id.account_id != signer_id {
            return Err(AttestationCheckError::AttestationOwnerMismatch);
        }

        // Stored account keys are Ed25519 by construction; a non-Ed25519
        // signer necessarily mismatches.
        let signer_ed25519 = Ed25519PublicKey::try_from(&signer_account_pk)
            .map_err(|_| AttestationCheckError::AttestationKeyMismatch)?;
        if attestation.node_id.account_public_key != signer_ed25519 {
            return Err(AttestationCheckError::AttestationKeyMismatch);
        }

        Ok(())
    }
```

**File:** docs/securing-mpc-with-tee-design-doc.md (L413-416)
```markdown

The Operator will then register the node's account key as an additional **function-call access key** on the node's NEAR account, scoped to the MPC signer contract (`--contract-account-id`) with an `unlimited` allowance and an **empty method-names list**. An empty list grants the key access to **all** methods on the MPC contract, while keeping it unable to transfer funds or call any other contract.

We grant access to all contract methods rather than an explicit allow-list because the set of methods a node must call changes across releases (for example, `register_foreign_chain_config` was added for foreign-chain support). A hand-maintained list silently drifts out of date, after which the node fails — with no obvious error — on any newly added method the key was never granted. See the operator guide ([running-an-mpc-node-in-tdx-external-guide.md](running-an-mpc-node-in-tdx-external-guide.md#updating-an-existing-key-to-allow-all-methods)) for the exact `near` CLI commands, and for rotating an existing restricted key (access-key permissions are immutable in NEAR, so the key must be deleted and re-added).
```
