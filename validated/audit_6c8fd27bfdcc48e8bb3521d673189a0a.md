### Title
`respond_ckd` Missing Response Validation for `AppPublicKey` Variant Allows Single Byzantine Participant to Deliver Fake CKD Output - (File: crates/contract/src/lib.rs)

---

### Summary

`respond_ckd` validates the CKD response only when the request uses `AppPublicKeyPV`, but performs **no validation** when the request uses `AppPublicKey`. A single malicious attested participant (strictly below the signing threshold) can call `respond_ckd` with a fabricated `CKDResponse` for any pending `AppPublicKey` request, and the contract will unconditionally resolve all waiting yields with the fake output.

---

### Finding Description

In `crates/contract/src/lib.rs`, `respond_ckd` contains the following conditional branch:

```rust
match &request.app_public_key {
    dtos::CKDAppPublicKey::AppPublicKey(_) => {}          // ← no validation at all
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
``` [1](#0-0) 

For `AppPublicKeyPV`, `ckd_output_check` performs a pairing-based on-chain proof that the response is correctly derived. For `AppPublicKey`, the arm is an empty block — the contract proceeds directly to `resolve_yields_for` with whatever `big_y` / `big_c` the caller supplied.

The function's only caller-authentication requirement is `assert_caller_is_attested_participant_and_protocol_active()`, which requires **one** attested participant — not a threshold. [2](#0-1) 

This is structurally identical to the reported Periphery bug: the code checks one condition (`AppPublicKeyPV` vs `AppPublicKey`) to decide whether to validate, but omits the validation entirely for the `AppPublicKey` branch, always taking the "no-check" path regardless of whether the response is correct.

---

### Impact Explanation

A single Byzantine attested participant (below the signing threshold) can:

1. Observe a pending `AppPublicKey` CKD request on-chain.
2. Call `respond_ckd` with arbitrary `CKDResponse { big_y: attacker_y, big_c: attacker_c }`.
3. The contract accepts the response without any check and calls `resolve_yields_for`, delivering the attacker-controlled key material to **all** callers waiting on that request.

Users receive an attacker-controlled confidential key instead of the legitimately threshold-derived one. This is unauthorized confidential key derivation output without the required participant authorization — a direct match for the Critical impact class. [3](#0-2) 

---

### Likelihood Explanation

- Any single attested participant who turns malicious can exploit this; no threshold collusion is required.
- All MPC nodes observe the on-chain request simultaneously. The attacker races to submit `respond_ckd` before the honest nodes. Because the attacker is a full MPC node with the same network visibility, this race is realistic.
- The `AppPublicKey` variant is still accepted by the contract (described as "privately verifiable, legacy" but not gated or deprecated). [4](#0-3) 

---

### Recommendation

1. **Require threshold agreement before resolving yields for `AppPublicKey` requests**: collect responses from multiple participants and only call `resolve_yields_for` once a threshold of identical responses has been received. This mirrors how the off-chain MPC protocol enforces threshold agreement.
2. **Deprecate and remove `AppPublicKey`** in favor of `AppPublicKeyPV`, which supports on-chain pairing verification and is immune to single-participant forgery.
3. If `AppPublicKey` must remain, add a prominent on-chain warning or reject it outright, since the contract cannot protect users from a single malicious node in this mode.

---

### Proof of Concept

1. User calls `request_app_private_key` with `CKDAppPublicKey::AppPublicKey(user_pk)`.
2. Malicious attested participant observes the pending `CKDRequest` on-chain.
3. Malicious participant calls:
   ```
   respond_ckd(
       request = <the pending CKDRequest>,
       response = CKDResponse { big_y: attacker_g1_point, big_c: attacker_g1_point }
   )
   ```
4. `respond_ckd` passes `assert_caller_is_attested_participant_and_protocol_active()`, enters the `AppPublicKey` arm (empty body), and calls `resolve_yields_for` with the fake response.
5. All callers waiting on that yield receive `CKDResponse { big_y: attacker_g1_point, big_c: attacker_g1_point }` — an attacker-controlled confidential key — before the honest nodes can respond. [5](#0-4)

### Citations

**File:** crates/contract/src/lib.rs (L653-688)
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
```
