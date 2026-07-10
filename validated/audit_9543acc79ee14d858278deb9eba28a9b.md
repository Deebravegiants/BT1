### Title
Single Byzantine Participant Can Deliver Unverified CKD Response for `AppPublicKey` Requests, Bypassing Threshold Authorization — (File: crates/contract/src/lib.rs)

---

### Summary

The `respond_ckd` function in the MPC contract performs no cryptographic output verification for the legacy `AppPublicKey` CKD variant. Any single attested participant can race the honest coordinator and submit an arbitrary `CKDResponse` for a pending `AppPublicKey` request. The contract accepts it unconditionally and resolves the user's yield with a fake confidential key derivation output — bypassing the threshold authorization that the MPC protocol is designed to enforce.

---

### Finding Description

In `respond_ckd` (`crates/contract/src/lib.rs`, lines 654–689), the contract branches on the request's `app_public_key` variant:

```rust
match &request.app_public_key {
    dtos::CKDAppPublicKey::AppPublicKey(_) => {}   // ← no check whatsoever
    dtos::CKDAppPublicKey::AppPublicKeyPV(app_pk) => {
        if !ckd_output_check(&request.app_id, &response, app_pk, &public_key) {
            env::panic_str("CKD output check failed");
        }
    }
}
``` [1](#0-0) 

For `AppPublicKeyPV`, `ckd_output_check` verifies the response against the app public key and the MPC public key. For the legacy `AppPublicKey` variant, the branch is empty — no verification is performed. The function then unconditionally calls `pending_requests::resolve_yields_for`, which resolves the user's pending yield with whatever `CKDResponse` was passed in. [2](#0-1) 

The only gate before this point is `assert_caller_is_attested_participant_and_protocol_active()`, which any current participant passes. [3](#0-2) 

There is no check that the response was produced by the threshold protocol, no signature over the output, and no binding to the MPC key. By contrast, `respond` for signatures always verifies the signature against the derived public key before resolving the yield: [4](#0-3) 

The `AppPublicKey` variant is described in the contract README as "privately verifiable (legacy)" — meaning the user is expected to verify the result themselves after receipt. However, the contract still resolves the yield and delivers whatever the first responding participant submits, with no on-chain guard. [5](#0-4) 

The analog to the external report is direct: MPC participants hold no financial stake in the contract (no bond, no slashable collateral), and for `AppPublicKey` CKD requests there is no cryptographic accountability mechanism — a participant can submit a fake response with zero on-chain consequence.

---

### Impact Explanation

A single Byzantine participant can monitor the NEAR blockchain for pending `AppPublicKey` CKD requests and call `respond_ckd` with arbitrary `big_y` / `big_c` BLS12-381 G1 points before the honest coordinator submits the real response. The contract resolves the yield with the fake output. The user's application receives a corrupted confidential key derivation result — a fake encrypted key that does not correspond to the MPC network's shared secret. This is a confidential key derivation output delivered without the required threshold participant authorization.

**Impact class**: Critical — "Unauthorized… confidential key derivation output without the required participant authorization."

---

### Likelihood Explanation

The attacker must be an attested participant (voted in by threshold participants, with a valid TEE attestation). Once inside the network, the attack requires only monitoring the NEAR blockchain for pending `AppPublicKey` CKD requests and submitting a `respond_ckd` transaction before the honest coordinator. This is a straightforward front-run / race condition with no additional cryptographic capability required. The `AppPublicKey` variant is still accepted by the contract and is the default legacy path for existing integrations.

---

### Recommendation

1. **Immediate**: Add cryptographic output verification for `AppPublicKey` CKD responses analogous to the `AppPublicKeyPV` path. Even a lightweight binding (e.g., verifying that `big_y` is consistent with the MPC public key and the request's `app_id`) would close the unguarded branch.
2. **Longer term**: Deprecate the `AppPublicKey` variant entirely and require all CKD requests to use `AppPublicKeyPV`, which has on-chain verifiable output via `ckd_output_check`.

---

### Proof of Concept

1. User calls `request_app_private_key` with the `AppPublicKey` variant, creating a pending CKD yield in `pending_ckd_requests`.
2. Byzantine participant monitors the NEAR blockchain and detects the pending request.
3. Byzantine participant calls:
   ```
   respond_ckd(request, CKDResponse { big_y: attacker_chosen_point, big_c: attacker_chosen_point })
   ```
4. Contract enters the `AppPublicKey` arm of the match — empty body, no check — then calls `resolve_yields_for`. [6](#0-5) 
5. The user's yield resolves with the attacker-supplied `CKDResponse`.
6. User's application receives a corrupted confidential key derivation output; the honest coordinator's subsequent `respond_ckd` call is rejected because the yield is already resolved.

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

**File:** crates/contract/src/lib.rs (L666-667)
```rust
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

**File:** crates/contract/README.md (L118-120)
```markdown
- `app_public_key`: the ephemeral public key for the CKD request. Two formats are supported:
  - **Privately verifiable** (legacy): a single G1 point, e.g. `"bls12381g1:<base58>"` or `{"AppPublicKey": "bls12381g1:<base58>"}`.
  - **Publicly verifiable**: a pair of points `(pk1, pk2) = (a·G1, a·G2)`, passed as `{"AppPublicKeyPV": {"pk1": "bls12381g1:<base58>", "pk2": "bls12381g2:<base58>"}}`. This allows anyone to verify the encrypted result on-chain without the app's secret key.
```
