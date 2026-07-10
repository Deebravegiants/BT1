### Title
Single Byzantine Participant Can Forge CKD Response for `AppPublicKey` Requests — (`crates/contract/src/lib.rs`)

---

### Summary

`respond_ckd` in `mpc-contract` performs **no on-chain verification** of the CKD response when the request uses the `AppPublicKey` (legacy, privately-verifiable) variant. Because any single attested participant can call `respond_ckd` — there is no leader-only guard — a single Byzantine participant below the signing threshold can race a pending `AppPublicKey` CKD request with an arbitrary forged response. The contract accepts it unconditionally, delivering a wrong confidential key derivation output to the requesting user and bypassing the threshold requirement entirely.

---

### Finding Description

In `respond_ckd`, after confirming the caller is an attested participant, the contract branches on the request's `app_public_key` variant: [1](#0-0) 

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

For `AppPublicKeyPV`, `ckd_output_check` cryptographically verifies the response against the public key pair on-chain. For `AppPublicKey`, the arm is empty — any `response` value passes. The function then unconditionally resolves all queued yields for that request: [2](#0-1) 

The access guard only requires the caller to be an attested participant: [3](#0-2) 

There is no check that the caller is the designated leader, nor any check that the response was produced by the threshold of participants. The `AppPublicKey` variant is still accepted in production as a supported legacy format: [4](#0-3) 

This is structurally identical to the external report's pattern: a security check (`ckd_output_check`) that is supposed to enforce threshold-authorized output is silently skipped for one code path, exactly as `blockDelay = 0` silently disabled the flash-protection check in USDV.

---

### Impact Explanation

A single Byzantine participant (strictly below the signing threshold) can:

1. Observe a pending `AppPublicKey` CKD request (participants have full visibility into the MPC computation).
2. Call `respond_ckd` with an arbitrary forged `CKDResponse` before the legitimate threshold computation completes.
3. The contract resolves all queued yields for that request with the forged output.
4. The requesting user receives a wrong confidential key derivation output.

This is **confidential key derivation output delivered without the required threshold-participant authorization** — the core security invariant of the MPC network is violated by a single actor. The user can detect the forgery off-chain (the `AppPublicKey` scheme is "privately verifiable"), but the contract has already committed the wrong output and the legitimate computation's response will be rejected as a duplicate.

---

### Likelihood Explanation

- Any single attested participant can call `respond_ckd` — no leader restriction exists.
- Participants observe pending CKD requests as part of normal MPC operation, so the attacker has all required request parameters.
- The attack is a simple race: submit the forged response before the honest threshold computation finishes.

### Citations

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

**File:** crates/contract/README.md (L119-120)
```markdown
  - **Privately verifiable** (legacy): a single G1 point, e.g. `"bls12381g1:<base58>"` or `{"AppPublicKey": "bls12381g1:<base58>"}`.
  - **Publicly verifiable**: a pair of points `(pk1, pk2) = (a·G1, a·G2)`, passed as `{"AppPublicKeyPV": {"pk1": "bls12381g1:<base58>", "pk2": "bls12381g2:<base58>"}}`. This allows anyone to verify the encrypted result on-chain without the app's secret key.
```
