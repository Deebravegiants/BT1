### Title
Missing CKD Response Authenticity Check for `AppPublicKey` Variant Allows Single Byzantine Participant to Forge Derived Key Output - (File: `crates/contract/src/lib.rs`)

---

### Summary

In `respond_ckd`, the contract verifies the CKD (Confidential Key Derivation) response cryptographically only when the request uses `CKDAppPublicKey::AppPublicKeyPV`. When the request uses `CKDAppPublicKey::AppPublicKey`, **no verification of the response is performed**. Any single attested participant can call `respond_ckd` with an arbitrary fabricated `CKDResponse` for a pending `AppPublicKey` request, and the contract will accept and return it to the user as a legitimate MPC-derived key — without threshold agreement.

---

### Finding Description

The `respond_ckd` function in `crates/contract/src/lib.rs` contains an asymmetric verification branch:

```rust
match &request.app_public_key {
    dtos::CKDAppPublicKey::AppPublicKey(_) => {}   // ← NO CHECK
    dtos::CKDAppPublicKey::AppPublicKeyPV(app_pk) => {
        if !ckd_output_check(&request.app_id, &response, app_pk, &public_key) {
            env::panic_str("CKD output check failed");
        }
    }
}
``` [1](#0-0) 

For `AppPublicKeyPV`, `ckd_output_check` cryptographically verifies the derived key output against the domain's BLS12-381 public key and the `app_id`. For `AppPublicKey`, the arm is a no-op — the response is accepted unconditionally.

The only guards before this branch are:
- `assert_caller_is_signer()` — signer == predecessor
- `is_running_or_resharing()` — protocol state check
- `accept_requests` — TEE flag
- `assert_caller_is_attested_participant_and_protocol_active()` — caller holds a valid TEE attestation [2](#0-1) 

None of these guards verify that the `CKDResponse` is the output of a genuine threshold computation. There is no check that threshold-many nodes agreed on the response, no signature over the response, and no binding between the response and the pending request's parameters.

This is directly analogous to the reference report: just as `master_edition` was unused for non-pNFTs (leaving no proof the mint is non-fungible), `ckd_output_check` is skipped for `AppPublicKey` (leaving no proof the derived key is the genuine MPC output).

---

### Impact Explanation

**Critical — Confidential key derivation output without required participant authorization.**

A single Byzantine attested participant (strictly below the signing threshold) can:

1. Monitor the chain for a pending `request_app_private_key` call using `CKDAppPublicKey::AppPublicKey`.
2. Construct an arbitrary `CKDResponse` — e.g., one whose encrypted payload decrypts to a key the attacker controls.
3. Call `respond_ckd(request, fabricated_response)` before the honest leader does.
4. The contract resolves the yield and returns the fabricated key to the user.

The user receives a derived key that does not correspond to the MPC network's actual key share. If the attacker crafts the response to encrypt a key they know, they can impersonate the user's derived key on any application that trusts the CKD output. The honest leader's subsequent `respond_ckd` call fails silently (the yield is already resolved).

---

### Likelihood Explanation

**Medium-High.** The attacker must be a legitimate attested participant (running a real TDX node in production). However, a single participant below the signing threshold suffices — no collusion is required. The attack is a simple front-run: the attacker watches the NEAR chain for `request_app_private_key` transactions with `AppPublicKey`, then races to call `respond_ckd` with a fabricated response. NEAR's transaction ordering is deterministic and observable, making the race feasible. The `AppPublicKey` variant is the legacy/simpler path and is likely used by existing integrations.

---

### Recommendation

Apply `ckd_output_check` (or an equivalent binding check) unconditionally for both `AppPublicKey` and `AppPublicKeyPV` variants. If `AppPublicKey` is privately verifiable only by the user, the contract should at minimum verify a threshold signature over the response (analogous to how `respond` verifies the ECDSA/EdDSA signature). Alternatively, deprecate `AppPublicKey` in favor of `AppPublicKeyPV` which already has the check.

```rust
match &request.app_public_key {
    dtos::CKDAppPublicKey::AppPublicKey(app_pk) => {
        // Add equivalent binding check here
        if !ckd_output_check_basic(&request.app_id, &response, app_pk, &public_key) {
            env::panic_str("CKD output check failed");
        }
    }
    dtos::CKDAppPublicKey::AppPublicKeyPV(app_pk) => {
        if !ckd_output_check(&request.app_id, &response, app_pk, &public_key) {
            env::panic_str("CKD output check failed");
        }
    }
}
```

---

### Proof of Concept

1. Deploy the contract in Running state with a BLS12-381 CKD domain.
2. User calls `request_app_private_key` with `app_public_key: AppPublicKey(some_g1_point)`.
3. Attacker (any single attested participant) observes the pending request on-chain.
4. Attacker calls:
   ```
   respond_ckd(
     request = <the pending CKDRequest>,
     response = <arbitrary fabricated CKDResponse>
   )
   ```
5. The contract passes all guards, skips the empty `AppPublicKey` arm, and calls `resolve_yields_for` — resolving the user's yield with the fabricated response.
6. The user's `request_app_private_key` promise resolves with the attacker-controlled key material.
7. The honest leader's subsequent `respond_ckd` call returns an error (no pending request found). [2](#0-1) [1](#0-0)

### Citations

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
