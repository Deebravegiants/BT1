### Title
`respond_ckd` Skips Cryptographic Output Verification for Legacy `AppPublicKey` CKD Requests, Enabling Single-Participant Forgery - (File: `crates/contract/src/lib.rs`)

---

### Summary

The `respond_ckd` function in `mpc-contract` performs cryptographic output verification only for the `AppPublicKeyPV` variant of CKD requests, but silently skips all verification for the legacy `AppPublicKey` variant. Every other response path (`respond`, `respond_verify_foreign_tx`, and `respond_ckd` with `AppPublicKeyPV`) verifies the cryptographic correctness of the submitted response before resolving pending yields. The missing check in the `AppPublicKey` branch means a single malicious attested participant — strictly below the signing threshold — can submit an arbitrary forged `CKDResponse` for any pending legacy CKD request, and the contract will accept and deliver it to the user without any verification.

---

### Finding Description

The three node-facing response methods enforce the following security checks:

**`respond`** (ECDSA/EdDSA signing):
- Calls `assert_caller_is_attested_participant_and_protocol_active()`
- Checks `accept_requests`
- **Cryptographically verifies** the submitted signature against the derived public key before calling `resolve_yields_for` [1](#0-0) 

**`respond_verify_foreign_tx`** (foreign-chain signing):
- Calls `assert_caller_is_attested_participant_and_protocol_active()`
- Checks `accept_requests`
- **Cryptographically verifies** the submitted signature against the root public key before calling `resolve_yields_for` [2](#0-1) 

**`respond_ckd`** (Confidential Key Derivation):
- Calls `assert_caller_is_attested_participant_and_protocol_active()`
- Checks `accept_requests`
- For `AppPublicKeyPV`: calls `ckd_output_check(...)` — **cryptographic verification present**
- For `AppPublicKey`: **empty match arm — no verification whatsoever**

```rust
match &request.app_public_key {
    dtos::CKDAppPublicKey::AppPublicKey(_) => {}   // ← no check
    dtos::CKDAppPublicKey::AppPublicKeyPV(app_pk) => {
        if !ckd_output_check(&request.app_id, &response, app_pk, &public_key) {
            env::panic_str("CKD output check failed");
        }
    }
}
``` [3](#0-2) 

After this match, `resolve_yields_for` is called unconditionally, resolving **all** pending yields for the request with whatever `CKDResponse` the caller supplied: [4](#0-3) 

The `AppPublicKey` variant is the legacy default path. The `AppPublicKeyPV` variant was introduced specifically to add public verifiability. The contract README documents this distinction: [5](#0-4) 

---

### Impact Explanation

A single malicious attested participant (strictly below the signing threshold) can:

1. Observe a pending `AppPublicKey` CKD request in `pending_ckd_requests`.
2. Craft a `CKDResponse { big_y, big_c }` where `big_y` encrypts a key the attacker already knows to the user's BLS12-381 public key.
3. Call `respond_ckd` with this forged response. The contract performs no cryptographic check on the `AppPublicKey` branch and calls `resolve_yields_for`, delivering the forged response to the user.
4. The user decrypts `big_y` with their private key and receives a key the attacker controls.
5. The attacker uses the same key to sign transactions on behalf of the user, stealing funds.

This constitutes **unauthorized confidential key derivation output without the required participant authorization** — a single participant below threshold can unilaterally determine the output of a CKD operation, bypassing the threshold requirement entirely for the legacy variant.

---

### Likelihood Explanation

- The `AppPublicKey` variant is the legacy default and is explicitly listed first in the enum. Existing integrations and users are likely using it.
- Any single attested participant (not threshold-many) can execute the attack. The attacker only needs to be faster than the honest nodes in submitting a `respond_ckd` call.
- The attack requires no special privileges beyond being an attested participant, which is a realistic adversary model for a Byzantine participant strictly below the signing threshold.

---

### Recommendation

Add cryptographic output verification for the `AppPublicKey` variant in `respond_ckd`, or — if on-chain verification is not feasible for the legacy variant — reject `AppPublicKey` CKD requests at the contract level and require migration to `AppPublicKeyPV`. At minimum, document that `AppPublicKey` CKD responses carry no on-chain integrity guarantee and are vulnerable to single-participant forgery.

---

### Proof of Concept

```
1. User calls request_app_private_key({ app_public_key: AppPublicKey(user_bls_pk), ... })
   → pending_ckd_requests[request] = [yield_id_0]

2. Attacker (single attested participant) computes:
     forged_big_y = BLS_encrypt(attacker_known_key, user_bls_pk)
     forged_big_c = arbitrary_point

3. Attacker calls respond_ckd(request, CKDResponse { big_y: forged_big_y, big_c: forged_big_c })
   → match arm AppPublicKey(_) => {}  // no check
   → resolve_yields_for resolves yield_id_0 with forged response

4. User's promise resolves with forged CKDResponse.
   User decrypts big_y → receives attacker_known_key.

5. Attacker signs transactions with attacker_known_key → steals user funds.
``` [6](#0-5)

### Citations

**File:** crates/contract/src/lib.rs (L573-650)
```rust
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

**File:** crates/contract/src/lib.rs (L705-753)
```rust
        self.assert_caller_is_attested_participant_and_protocol_active();

        if !self.protocol_state.is_running_or_resharing() {
            return Err(InvalidState::ProtocolStateNotRunning.into());
        }

        if !self.accept_requests {
            return Err(TeeError::TeeValidationFailed.into());
        }

        let domain = request.domain_id;
        let public_key = self.public_key_extended(domain.0.into())?;

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

**File:** crates/contract/README.md (L280-282)
```markdown
- `derivation_path` (String): the derivation path.
- `app_public_key`: the ephemeral public key to encrypt the generated confidential key. Accepts either a plain G1 point string (privately verifiable, legacy) or a tagged enum with `AppPublicKey` (single G1 point) or `AppPublicKeyPV` (a `{pk1, pk2}` pair for public verifiability).
- `domain_id` (integer): the domain ID that identifies the key and signature scheme to use to generate the confidential key
```
