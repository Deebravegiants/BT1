### Title
Unvalidated CKD Response for `AppPublicKey` Variant Allows Single Attested Participant to Forge Confidential Key Derivation Output - (File: crates/contract/src/lib.rs)

### Summary
`respond_ckd()` performs cryptographic output verification only for the `AppPublicKeyPV` variant of `CKDAppPublicKey`. For the `AppPublicKey` variant, the response is accepted with no validation whatsoever. A single attested participant (strictly below the signing threshold) can call `respond_ckd()` with an arbitrary, attacker-controlled `CKDResponse`, and the contract will resolve the pending yield and deliver forged key material to the requesting user.

### Finding Description
In `crates/contract/src/lib.rs`, `respond_ckd()` branches on the `app_public_key` variant of the incoming `CKDRequest`:

```rust
match &request.app_public_key {
    dtos::CKDAppPublicKey::AppPublicKey(_) => {}          // ← no check at all
    dtos::CKDAppPublicKey::AppPublicKeyPV(app_pk) => {
        if !ckd_output_check(&request.app_id, &response, app_pk, &public_key) {
            env::panic_str("CKD output check failed");
        }
    }
}
``` [1](#0-0) 

For `AppPublicKeyPV`, `ckd_output_check` verifies that the submitted `CKDResponse` (`big_y`, `big_c`) is cryptographically consistent with the master public key and the app's identity. For `AppPublicKey`, the arm is an empty block — the response values are never checked against anything. The function then unconditionally resolves all queued yields with the unverified response bytes:

```rust
pending_requests::resolve_yields_for(
    &mut self.pending_ckd_requests,
    &request,
    serde_json::to_vec(&response).unwrap(),
)
``` [2](#0-1) 

The only caller-side guards are `assert_caller_is_signer()` and `assert_caller_is_attested_participant_and_protocol_active()` — both of which are satisfied by any single active, attested participant. There is no threshold-signature requirement on the response itself. [3](#0-2) 

The analog to the original report is direct: just as `fetchAllTicketCommentsCount()` / `updateTicket()` / `parseTicketComments()` proceeded with undefined `apiKey`/`address` parameters without an early exit, `respond_ckd()` proceeds with completely unvalidated `CKDResponse` parameters for the `AppPublicKey` variant — the missing early-exit / validation guard is the root cause in both cases.

### Impact Explanation
A user who calls `request_app_private_key()` with `CKDAppPublicKey::AppPublicKey(pk)` expects to receive `(big_y, big_c)` such that `big_c = H(master_pk, app_id) * msk + pk * y` (the honest CKD protocol output). They use these values to derive an app-specific private key for a foreign-chain wallet.

A single Byzantine participant can instead submit `big_y = G * r` and `big_c = G * s` for arbitrary scalars `r, s` it chose. The contract accepts this, the user's yield resolves with the forged values, and the user derives a private key that the attacker already knows (because the attacker chose `r` and `s`). The attacker can then drain any funds the user deposits to the address derived from that key.

This is unauthorized confidential key derivation output delivered without the required threshold-participant authorization, matching the Critical impact tier: *"Unauthorized … confidential key derivation output without the required participant authorization."*

### Likelihood Explanation
The `AppPublicKey` variant is the simpler, non-privacy-preserving CKD path and is the one shown in the localnet example (`docs/localnet/args/ckd.json`). Any single attested participant — one node out of the full set, well below the signing threshold — can exploit this. The call requires no special privilege beyond being an active participant. The attack is silent: the user receives a response that looks structurally valid (two BLS12-381 G1 points) and has no way to detect the forgery on-chain. [4](#0-3) 

### Recommendation
Apply the same `ckd_output_check` (or an equivalent binding between the response and the master public key) to the `AppPublicKey` variant, or reject `AppPublicKey` requests in `respond_ckd()` with an explicit early-exit if no on-chain verification is possible for that variant. The fix mirrors the recommendation in the original report: add an early validation guard so the function exits immediately if the essential parameters (here, the CKD output) cannot be verified.

### Proof of Concept
1. User calls `request_app_private_key({ derivation_path: "x", app_public_key: AppPublicKey(honest_pk), domain_id: 0 })` with the required deposit. A `CKDRequest` is queued in `pending_ckd_requests`.
2. Attacker (a single attested participant) constructs `CKDResponse { big_y: G * 1, big_c: G * 2 }` — completely arbitrary values.
3. Attacker calls `respond_ckd(ckd_request, forged_response)`. The `AppPublicKey` branch is a no-op; `resolve_yields_for` fires `promise_yield_resume` with the forged bytes.
4. The user's promise resolves with `big_y = G, big_c = 2*G`. The user derives their "private key" from these values and funds a foreign-chain address. The attacker, who knows the discrete logs, controls that address and steals the funds. [5](#0-4)

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

**File:** docs/localnet/args/ckd.json (L1-7)
```json
{
  "request": {
    "derivation_path": "mykey",
    "app_public_key": "bls12381g1:6KtVVcAAGacrjNGePN8bp3KV6fYGrw1rFsyc7cVJCqR16Zc2ZFg3HX3hSZxSfv1oH6",
    "domain_id": 2
  }
}
```
