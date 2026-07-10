### Title
Single Attested Participant Can Forge Privately-Verifiable CKD Response, Bypassing Threshold Requirement - (File: `crates/contract/src/lib.rs`)

### Summary

The `respond_ckd` function in the MPC contract performs **zero cryptographic verification** of the response when the CKD request uses the `AppPublicKey` (privately-verifiable) variant. Any single attested participant can submit arbitrary BLS12-381 G1 points as `(big_y, big_c)` and the contract will accept them, resolve the pending yield, and deliver the forged output to the requesting user — bypassing the threshold computation entirely.

### Finding Description

The `respond_ckd` function at `crates/contract/src/lib.rs` lines 675–682 branches on the request's `app_public_key` variant:

```rust
match &request.app_public_key {
    dtos::CKDAppPublicKey::AppPublicKey(_) => {}   // ← NO CHECK WHATSOEVER
    dtos::CKDAppPublicKey::AppPublicKeyPV(app_pk) => {
        if !ckd_output_check(&request.app_id, &response, app_pk, &public_key) {
            env::panic_str("CKD output check failed");
        }
    }
}
``` [1](#0-0) 

For the `AppPublicKeyPV` (publicly-verifiable) variant, the contract calls `ckd_output_check`, which performs a BLS pairing check to confirm the response is a valid encryption of `msk · H(pk, app_id)`. For the `AppPublicKey` (privately-verifiable) variant, the arm is a no-op — the contract accepts any `CKDResponse { big_y, big_c }` unconditionally.

The existing unit test at line 3403 confirms this: it passes completely bogus byte arrays `[1u8; 48]` and `[2u8; 48]` as `big_y` and `big_c` and the test asserts the call **succeeds**: [2](#0-1) 

The CKD protocol requires a threshold of participants to each contribute a share `(λ_i · Y_i, λ_i · C_i)` that are summed to produce the correct `(Y, C)`. The contract enforces no such multi-party requirement for the `AppPublicKey` variant — a single attested participant can call `respond_ckd` with any two G1 points and the contract resolves the pending yield with those forged values. [3](#0-2) 

The `AppPublicKey` variant is documented as the "legacy" and default path: [4](#0-3) 

### Impact Explanation

**Critical — Unauthorized confidential key derivation output without required participant authorization.**

A single attested participant (strictly below the signing threshold) can:

1. Observe a pending `CKDRequest` with `AppPublicKey` variant on-chain.
2. Call `respond_ckd(request, CKDResponse { big_y: attacker_chosen, big_c: attacker_chosen })`.
3. The contract passes all checks (signer, attestation, protocol state) and resolves the yield with the forged data.
4. The requesting user's NEAR transaction receives `(big_y, big_c)` that does **not** equal `msk · H(pk, app_id)`.
5. The user computes `sig = big_c − a · big_y`, which is not the correct deterministic secret.
6. The pending request is consumed — legitimate MPC nodes can no longer respond.

If the user's application does not verify the decrypted result (or if verification is skipped), the user derives and uses a wrong key that the attacker fully controls. Even if the user verifies and detects the forgery, the request is permanently consumed, denying the user their correct key.

The CKD feature is specifically designed to give TEE applications a **deterministic, confidential** secret. Forging the response breaks both properties: the secret is neither correct nor confidential.

### Likelihood Explanation

**Medium.** The attacker must be an attested participant (must have passed TEE attestation). However:

- Only a **single** participant is required — no collusion needed.
- The attack is reachable from any attested participant account calling `respond_ckd` directly on-chain.
- The `AppPublicKey` variant is the legacy/default path used by most existing integrations.
- The attack window is the time between a CKD request appearing on-chain and a legitimate node responding — a race condition any participant can win.

### Recommendation

Apply the same cryptographic output check to the `AppPublicKey` variant that is already applied to `AppPublicKeyPV`. For the privately-verifiable variant, the contract cannot verify the decryption directly (it lacks the user's private key `a`), but it **can** verify that `(big_y, big_c)` is a valid BLS encryption relative to the network public key and `app_id` using the pairing equation:

```
e(big_c, G2) = e(H(pk, app_id), pk) · e(big_y, A2)
```

where `A2` is a G2 representation of the user's public key. If the `AppPublicKey` variant cannot support this check (because only a G1 point is provided), the variant should be deprecated in favor of `AppPublicKeyPV`, or the contract should require a threshold-signed attestation over the response hash before accepting it.

### Proof of Concept

1. User submits `request_app_private_key` with `AppPublicKey` variant.
2. Attacker (any single attested participant) calls:
   ```json
   respond_ckd(
     request = <observed pending CKDRequest>,
     response = { "big_y": "bls12381g1:<any_valid_point>", "big_c": "bls12381g1:<any_valid_point>" }
   )
   ```
3. Contract executes lines 675–688: the `AppPublicKey` arm is a no-op, `resolve_yields_for` is called, and the forged response is delivered to the user.
4. The unit test at line 3403 already demonstrates this: `[1u8; 48]` / `[2u8; 48]` (invalid BLS points) are accepted without error. [5](#0-4)

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

**File:** crates/contract/src/lib.rs (L3424-3440)
```rust
        let response = CKDResponse {
            big_y: dtos::Bls12381G1PublicKey([1u8; 48]),
            big_c: dtos::Bls12381G1PublicKey([2u8; 48]),
        };

        with_active_participant_and_attested_context(&contract);

        match contract.respond_ckd(ckd_request.clone(), response.clone()) {
            Ok(_) => {
                contract
                    .return_ck_and_clean_state_on_success(ckd_request.clone(), Ok(response))
                    .detach();

                assert!(contract.get_pending_ckd_request(&ckd_request).is_none(),);
            }
            Err(_) => panic!("respond_ckd should not fail"),
        }
```

**File:** crates/contract/README.md (L119-121)
```markdown
  - **Privately verifiable** (legacy): a single G1 point, e.g. `"bls12381g1:<base58>"` or `{"AppPublicKey": "bls12381g1:<base58>"}`.
  - **Publicly verifiable**: a pair of points `(pk1, pk2) = (a·G1, a·G2)`, passed as `{"AppPublicKeyPV": {"pk1": "bls12381g1:<base58>", "pk2": "bls12381g2:<base58>"}}`. This allows anyone to verify the encrypted result on-chain without the app's secret key.
- `domain_id` (integer): identifies the master key to use for deriving the ckd, and must correspond to bls12381.
```
