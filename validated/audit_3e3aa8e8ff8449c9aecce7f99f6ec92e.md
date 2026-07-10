### Title
Single Byzantine Node Can Deliver Forged CKD Key Material to Any User via Unverified `respond_ckd` for `AppPublicKey` Requests - (File: `crates/contract/src/lib.rs`)

### Summary

The `respond_ckd` contract method enforces a cryptographic output check only for `AppPublicKeyPV` requests. For the `AppPublicKey` variant, no verification of the returned key material is performed. A single attested participant — a Byzantine node strictly below the signing threshold — can race to call `respond_ckd` with attacker-controlled key material for any pending `AppPublicKey` CKD request, delivering a forged app private key to the victim. Because the attacker chose the forged key, they also possess it and can use it to drain the victim's assets on any foreign chain the derived key controls.

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
```

For `AppPublicKeyPV`, `ckd_output_check` verifies that the response is cryptographically consistent with the user-supplied proof and the network's BLS12-381 root key. For `AppPublicKey`, the arm is a no-op: any `CKDResponse` value is accepted and forwarded to the user via `pending_requests::resolve_yields_for`.

The only guards on `respond_ckd` are `assert_caller_is_signer` (signer == predecessor) and `assert_caller_is_attested_participant_and_protocol_active`. Both are satisfied by any single attested participant — a role that is, by definition, strictly below the signing threshold.

**Attack path:**

1. Victim calls `request_app_private_key` with `AppPublicKey(victim_app_pk)`. The request is stored in `pending_ckd_requests` keyed by `CKDRequest { app_public_key, domain_id, app_id, … }`.
2. The Byzantine node observes the pending request on-chain (the NEAR indexer exposes all receipts).
3. The Byzantine node generates an arbitrary key pair `(forged_sk, forged_pk)` and encrypts `forged_sk` to `victim_app_pk`, producing a well-formed `CKDResponse`.
4. The Byzantine node calls `respond_ckd(request, forged_response)` before honest nodes respond. The contract performs no output check and resolves the yield, delivering `forged_response` to the victim's callback.
5. The victim decrypts the response with their app private key and obtains `forged_sk` — a key the attacker also knows.
6. The attacker uses `forged_sk` to sign transactions on any foreign chain the derived key controls, draining the victim's assets.

The contrast with `respond` (ECDSA/EdDSA signing) is instructive: there, the contract verifies the submitted signature against the expected derived public key, so a single Byzantine node cannot forge a valid response. No equivalent guard exists for `AppPublicKey` CKD responses.

### Impact Explanation

A single Byzantine attested participant — one node, below the signing threshold — can silently replace the honest CKD output for **any** pending `AppPublicKey` request with attacker-controlled key material. Because the attacker chose the forged private key, they possess it and can unilaterally control every foreign-chain account derived from it. This constitutes direct theft of funds controlled by the chain-signature flow, matching the Critical impact tier: *"Theft, direct loss, or permanent freezing of funds controlled by the MPC network, chain-signature contract, or verified foreign-chain flow."*

### Likelihood Explanation

The attacker must be an attested participant (TEE-attested node accepted into the network). This is a realistic role for a Byzantine participant below threshold. Once in that role, the attack requires only observing a pending `AppPublicKey` CKD request on-chain and submitting a forged `respond_ckd` call before honest nodes respond — a straightforward race on a public blockchain where all pending receipts are visible.

### Recommendation

Apply the same output-verification discipline to `AppPublicKey` responses as is already applied to `AppPublicKeyPV`. Options:

1. **Require threshold participation**: Do not resolve a CKD yield from a single `respond_ckd` call; instead, collect threshold-many consistent partial responses before resolving, mirroring the off-chain signing protocol.
2. **Bind the response to the network key**: Derive a verifiable commitment from the BLS12-381 root key and the `app_id`/`derivation_path` that any honest observer can check, and verify it in the `AppPublicKey` arm before resolving the yield.
3. **Reject `AppPublicKey` without a verifiable proof**: Require callers to always use `AppPublicKeyPV` so the existing `ckd_output_check` path is always exercised.

### Proof of Concept

```
// 1. Victim submits CKD request
request_app_private_key({
    app_public_key: AppPublicKey(victim_app_pk),
    domain_id: bls_domain_id,
    derivation_path: "m/0/1",
})
// → stored in pending_ckd_requests

// 2. Byzantine node (single attested participant) observes the request on-chain

// 3. Byzantine node constructs forged response
let (forged_sk, _forged_pk) = generate_keypair();
let forged_response = encrypt(forged_sk, victim_app_pk);  // well-formed CKDResponse

// 4. Byzantine node calls respond_ckd — no output check for AppPublicKey
respond_ckd(request, forged_response)
// → contract: AppPublicKey arm is a no-op, yield resolved immediately

// 5. Victim's callback receives forged_response, decrypts → obtains forged_sk

// 6. Attacker (who knows forged_sk) signs foreign-chain txs, drains victim's assets
``` [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** crates/contract/src/lib.rs (L563-651)
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

        if !self.protocol_state.is_running_or_resharing() {
            return Err(InvalidState::ProtocolStateNotRunning.into());
        }

        if !self.accept_requests {
            return Err(TeeError::TeeValidationFailed.into());
        }

        let domain = request.domain_id;
        let public_key = self.public_key_extended(domain)?;

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

**File:** crates/contract/src/lib.rs (L2389-2403)
```rust
    fn assert_caller_is_attested_participant_and_protocol_active(&self) {
        let participants = self.protocol_state.active_participants();

        Self::assert_caller_is_signer();

        let attestation_check = self
            .tee_state
            .is_caller_an_attested_participant(participants);

        assert_matches::assert_matches!(
            attestation_check,
            Ok(()),
            "Caller must be an attested participant"
        );
    }
```
