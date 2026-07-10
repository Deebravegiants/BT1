### Title
Single Attested Participant Can Deliver Arbitrary CKD Response for `AppPublicKey` Requests, Bypassing Threshold Authorization — (File: `crates/contract/src/lib.rs`)

---

### Summary

`respond_ckd` skips all cryptographic verification of the response payload for `AppPublicKey` (privately-verifiable, legacy) CKD requests. A single Byzantine attested participant — strictly below the signing threshold — can call `respond_ckd` with any arbitrary `big_y` / `big_c` values and the contract will accept and deliver the forged confidential-key-derivation output to the requesting user. This is the direct analog of the stFLUO `withdraw` bypass: just as `withdraw` was an inherited code path that skipped the unbonding-period constraint, the `AppPublicKey` branch in `respond_ckd` is a code path that skips the cryptographic constraint that `AppPublicKeyPV` enforces.

---

### Finding Description

In `respond_ckd`, after the caller-is-attested-participant check, the contract branches on the request's `app_public_key` variant:

```rust
match &request.app_public_key {
    dtos::CKDAppPublicKey::AppPublicKey(_) => {}          // ← no verification at all
    dtos::CKDAppPublicKey::AppPublicKeyPV(app_pk) => {
        if !ckd_output_check(&request.app_id, &response, app_pk, &public_key) {
            env::panic_str("CKD output check failed");
        }
    }
}
``` [1](#0-0) 

For `AppPublicKeyPV` requests the contract calls `ckd_output_check`, which verifies the BLS12-381 pairing relationship between `big_y`, `big_c`, the app public key, and the network master key — so a forged response is rejected on-chain. For `AppPublicKey` requests the branch is an empty no-op: the contract immediately proceeds to `resolve_yields_for` and delivers whatever `big_y` / `big_c` the caller supplied. [2](#0-1) 

For comparison, `respond` (signing) always verifies the submitted signature against the cryptographically derived public key before resolving the yield, so a single malicious participant cannot forge a valid ECDSA/EdDSA signature even though only one participant needs to call `respond`. [3](#0-2) 

For `AppPublicKey` CKD requests there is no equivalent on-chain guard. The contract's security for this path relies entirely on the off-chain MPC threshold protocol producing the correct output — but the contract itself imposes no check that enforces this.

---

### Impact Explanation

A single Byzantine attested participant (below the signing threshold) can:

1. Observe a pending `AppPublicKey` CKD request on-chain (the request details are public).
2. Race the honest MPC nodes by calling `respond_ckd` with the correct `CKDRequest` key but with attacker-chosen `big_y` and `big_c` values.
3. The contract accepts the call, resolves the yield, and delivers the forged output to the user.

The user receives a confidential key derivation output that was not produced by the threshold MPC protocol. Depending on how the user's application uses the derived key, this can result in:

- The user's application silently operating with an attacker-controlled key.
- Loss of assets or identity material controlled by the derived key on a foreign chain.

This maps to the allowed Critical impact: **"Unauthorized … confidential key derivation output without the required participant authorization."**

---

### Likelihood Explanation

`AppPublicKey` is the legacy (default) format documented in the README and used by existing integrations. [4](#0-3) 

Any single attested participant that turns Byzantine can exploit this. The attacker-controlled entry path is fully reachable from an unprivileged contract caller perspective: the attacker only needs to hold a valid TEE attestation as one of the current participants, which is the standard Byzantine-participant-below-threshold threat model explicitly listed in the scope.

---

### Recommendation

Apply the same pattern used for `AppPublicKeyPV`: either

1. **Disable `AppPublicKey` CKD requests** (analogous to disabling `withdraw` in the stFLUO fix) and require all callers to use `AppPublicKeyPV`, which supports on-chain verification via `ckd_output_check`; or
2. **Add a threshold-vote mechanism** for `AppPublicKey` responses so that the contract only resolves the yield after a quorum of attested participants have submitted matching `(big_y, big_c)` values.

Option 1 is the simpler fix and directly mirrors the stFLUO remediation.

---

### Proof of Concept

```
1. Alice calls request_app_private_key({
       derivation_path: "mykey",
       app_public_key: "bls12381g1:<alice_pk>",   // AppPublicKey variant
       domain_id: 2
   })
   → pending CKDRequest R is stored on-chain.

2. Malicious attested participant Eve observes R on-chain.

3. Eve calls respond_ckd(R, CKDResponse { big_y: <garbage>, big_c: <garbage> }).
   → assert_caller_is_attested_participant_and_protocol_active() passes (Eve is attested).
   → AppPublicKey branch: empty no-op, no ckd_output_check called.
   → resolve_yields_for delivers <garbage> to Alice's pending yield.

4. Alice's transaction resolves with the forged CKDResponse.
   Alice's application decrypts big_y with her app secret key and obtains
   an attacker-controlled or meaningless key — not the MPC-derived key.
``` [5](#0-4)

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

**File:** crates/contract/README.md (L118-121)
```markdown
- `app_public_key`: the ephemeral public key for the CKD request. Two formats are supported:
  - **Privately verifiable** (legacy): a single G1 point, e.g. `"bls12381g1:<base58>"` or `{"AppPublicKey": "bls12381g1:<base58>"}`.
  - **Publicly verifiable**: a pair of points `(pk1, pk2) = (a·G1, a·G2)`, passed as `{"AppPublicKeyPV": {"pk1": "bls12381g1:<base58>", "pk2": "bls12381g2:<base58>"}}`. This allows anyone to verify the encrypted result on-chain without the app's secret key.
- `domain_id` (integer): identifies the master key to use for deriving the ckd, and must correspond to bls12381.
```
