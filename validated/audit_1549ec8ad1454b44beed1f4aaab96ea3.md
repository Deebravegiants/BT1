Looking at the contract's `respond_ckd()` method, I can identify a clear structural analog to the EIP2981 inconsistency: one variant of the CKD response path implements a cryptographic output check while the other does not, allowing a Byzantine participant to forge derived-key outputs.

---

### Title
Missing CKD Response Verification for `AppPublicKey` Variant Allows Byzantine Participant to Forge Derived Key Output — (File: `crates/contract/src/lib.rs`)

### Summary
`respond_ckd()` applies a cryptographic correctness check (`ckd_output_check`) only for `AppPublicKeyPV` CKD responses. The `AppPublicKey` variant receives **no response verification**. A single Byzantine TEE-attested participant (below signing threshold) can race to submit a forged `CKDResponse` for any pending `AppPublicKey` request, causing the user to receive an incorrect derived key and potentially lose funds.

### Finding Description
In `respond_ckd()`, the contract branches on the request's `app_public_key` variant:

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

For `AppPublicKeyPV`, the contract cryptographically verifies that the response is the correct derived key for the given inputs. For `AppPublicKey`, the contract unconditionally accepts whatever `CKDResponse` the calling node provides — no correctness check is performed.

This is structurally identical to the EIP2981 finding: `AppPublicKeyPV` implements the verification standard; `AppPublicKey` does not.

`respond_ckd()` is a public contract method gated only by `assert_caller_is_signer()` and `assert_caller_is_attested_participant_and_protocol_active()`. [2](#0-1) 

Any TEE-attested participant can call it for **any** pending CKD request. The yield-resume mechanism resolves on the **first** successful call: [3](#0-2) 

A Byzantine participant therefore only needs to submit their forged call before the honest leader does. There is no quorum or threshold requirement on the respond path — a single attested node wins the race.

The same inconsistency is absent from the regular signing path: `respond()` verifies the signature against the **derived** key using `derive_key_secp256k1` and the request's tweak, providing a cryptographic guarantee that the MPC output is correct. [4](#0-3) 

No equivalent guarantee exists for `AppPublicKey` CKD responses.

### Impact Explanation
**Critical.** The CKD protocol is designed to deliver a user-specific derived private key. A forged `CKDResponse` for an `AppPublicKey` request delivers an attacker-chosen key to the user. If the user subsequently uses that key to receive or control assets on a foreign chain (the primary use-case for CKD), those assets are permanently inaccessible or directly stolen by whoever controls the forged key. This constitutes direct, permanent loss of funds controlled by the MPC network's key-derivation flow.

### Likelihood Explanation
**Medium.** The attacker must be a single TEE-attested participant (Byzantine participant strictly below the signing threshold — an explicitly allowed attacker model). No threshold collusion is required. The attack is a straightforward race: monitor the NEAR chain for pending `AppPublicKey` CKD yields and submit a forged `respond_ckd()` call before the honest leader. Network latency is the only practical barrier.

### Recommendation
Apply a cryptographic correctness check to `AppPublicKey` responses analogous to `ckd_output_check` for `AppPublicKeyPV`. If the derived key is deterministic given the on-chain inputs (app public key, domain, predecessor, derivation path, root BLS key), the contract can independently verify the response without relying on node honesty. At minimum, the `AppPublicKey` arm should not be a silent no-op.

### Proof of Concept
1. User calls `request_app_private_key()` with `CKDAppPublicKey::AppPublicKey(pk)` → a yield is created and stored in `pending_ckd_requests`.
2. Byzantine TEE-attested participant observes the pending yield on-chain.
3. Byzantine participant calls `respond_ckd(request, forged_response)` where `forged_response` contains an attacker-controlled derived key.
4. The contract executes the `AppPublicKey` arm — an empty match arm — and performs **no verification**.
5. `resolve_yields_for` resolves the yield with the forged response; the honest leader's subsequent call finds no pending yield and is a no-op.
6. The user's callback receives the attacker-chosen key material.
7. The user derives a foreign-chain address from the forged key and deposits funds; the attacker, who knows the corresponding private key, drains them.

### Citations

**File:** crates/contract/src/lib.rs (L596-608)
```rust
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
```

**File:** crates/contract/src/lib.rs (L653-666)
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
