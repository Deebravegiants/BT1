### Title
`accept_requests` Guard Applied Unconditionally to `respond*` Functions Freezes All In-Flight Signature Requests on TEE Validation Failure - (File: `crates/contract/src/lib.rs`)

### Summary

The `accept_requests` flag, intended to gate **new** user-facing request submissions, is also checked unconditionally inside every `respond*` node callback (`respond`, `respond_ckd`, `respond_verify_foreign_tx`). When TEE validation fails and `accept_requests` is set to `false`, MPC nodes are blocked from delivering signatures for requests that were already accepted and queued before the failure. Those in-flight requests are permanently stuck until the NEAR yield-resume timeout fires, at which point they fail with a timeout error — even though the nodes computed a valid signature and are ready to deliver it.

---

### Finding Description

`check_request_preconditions` — the shared guard for all user-facing entry points — correctly rejects new submissions when `accept_requests` is `false`: [1](#0-0) 

The same guard is then duplicated, unconditionally, inside every node-facing `respond*` function:

**`respond` (signature delivery):** [2](#0-1) 

**`respond_ckd` (CKD delivery):** [3](#0-2) 

**`respond_verify_foreign_tx` (foreign-tx delivery):** [4](#0-3) 

`accept_requests` is set to `false` by `verify_tee()` when fewer than `threshold` participants hold valid TEE attestations: [5](#0-4) 

The `respond*` functions are the **delivery** side of the yield-resume flow — they resolve promises that were created by already-accepted `sign` / `request_app_private_key` / `verify_foreign_transaction` calls. Blocking delivery with the same flag that blocks new submissions is the direct analog of the BadgerDAO finding: a guard that is only relevant to one code path (`sign` accepting new requests) is applied unconditionally to an unrelated code path (`respond` delivering already-queued results).

The `accept_requests` check in `respond*` is not needed for any security property: the signature is independently verified against the on-chain public key before `resolve_yields_for` is called, so a malicious response is rejected regardless of the flag. [6](#0-5) 

---

### Impact Explanation

When `accept_requests` flips to `false` (a legitimate protocol event, not an attack):

1. All `pending_signature_requests`, `pending_ckd_requests`, and `pending_verify_foreign_tx_requests` that were queued before the flip are permanently unresolvable until the NEAR yield-resume timeout fires.
2. The timeout handler `fail_on_timeout` panics with a `RequestError::Timeout`, causing every waiting caller's cross-chain transaction to fail.
3. Users who submitted bridge or signing requests lose the gas cost and the cross-chain operation fails — a request-lifecycle invariant violation: *accepted requests must be fulfillable*.

This matches the **Medium** allowed impact: "Balance, request-lifecycle, participant-state, or contract execution-flow manipulation that breaks production safety/accounting invariants without relying on network-level DoS or operator misconfiguration." [7](#0-6) 

---

### Likelihood Explanation

TEE attestations have a finite validity window. Any time enough participants' attestations expire simultaneously (a routine operational event, not an attack), `verify_tee()` sets `accept_requests = false`. At that moment, every in-flight request is silently doomed. The window between attestation expiry and re-attestation is a normal part of the protocol lifecycle, making this a realistic production scenario. [8](#0-7) 

---

### Recommendation

Remove the `accept_requests` guard from all three `respond*` functions. The flag's purpose is to stop the contract from accepting **new** work when the TEE quorum is degraded; it has no security role in the delivery of already-accepted work. The existing per-response signature verification is sufficient to reject invalid responses.

```rust
// REMOVE from respond(), respond_ckd(), respond_verify_foreign_tx():
if !self.accept_requests {
    return Err(TeeError::TeeValidationFailed.into());
}
```

The `accept_requests` check should remain only inside `check_request_preconditions`, which guards the user-facing submission entry points.

---

### Proof of Concept

1. User calls `sign(request)` — request is queued in `pending_signature_requests`, a yield-resume promise is created.
2. Attestations for `threshold - 1` participants expire; a participant calls `verify_tee()`.
3. `verify_tee()` finds fewer than `threshold` valid attestations → sets `accept_requests = false`.
4. MPC nodes finish computing the signature and call `respond(request, valid_signature)`.
5. `respond` hits `if !self.accept_requests { return Err(TeeValidationFailed) }` at line 579 — the call fails.
6. Nodes retry; the flag is still `false`; retries keep failing.
7. The NEAR yield-resume timeout fires → `fail_on_timeout` panics → the user's cross-chain transaction fails with `RequestError::Timeout`.
8. The valid signature is discarded; the user's bridge operation is permanently lost. [9](#0-8) [10](#0-9) [11](#0-10)

### Citations

**File:** crates/contract/src/lib.rs (L298-302)
```rust
        // 4. Refuse the request if the contract is not currently accepting requests
        //    (e.g. because TEE validation has failed).
        if !self.accept_requests {
            env::panic_str(&TeeError::TeeValidationFailed.to_string())
        }
```

**File:** crates/contract/src/lib.rs (L563-581)
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
```

**File:** crates/contract/src/lib.rs (L642-650)
```rust
        if !signature_is_valid {
            return Err(RespondError::InvalidSignature.into());
        }

        pending_requests::resolve_yields_for(
            &mut self.pending_signature_requests,
            &request,
            serde_json::to_vec(&response).unwrap(),
        )
```

**File:** crates/contract/src/lib.rs (L653-664)
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
```

**File:** crates/contract/src/lib.rs (L691-713)
```rust
    #[handle_result]
    pub fn respond_verify_foreign_tx(
        &mut self,
        request: VerifyForeignTransactionRequest,
        response: VerifyForeignTransactionResponse,
    ) -> Result<(), Error> {
        let signer = Self::assert_caller_is_signer();

        log!(
            "respond_verify_foreign_tx: signer={}, request={:?}",
            &signer,
            &request
        );

        self.assert_caller_is_attested_participant_and_protocol_active();

        if !self.protocol_state.is_running_or_resharing() {
            return Err(InvalidState::ProtocolStateNotRunning.into());
        }

        if !self.accept_requests {
            return Err(TeeError::TeeValidationFailed.into());
        }
```

**File:** crates/contract/src/lib.rs (L2341-2344)
```rust
    pub fn fail_on_timeout() {
        // To stay consistent with the old version of the timeout error
        env::panic_str(&RequestError::Timeout.to_string());
    }
```

**File:** crates/contract/tests/sandbox/tee.rs (L838-841)
```rust
/// 4. Call `verify_tee()`, which returns `false` and does NOT enter resharing.
/// 5. Verify the contract stays Running with all 3 participants (no kickout).
/// 6. Verify a `sign` request is now refused with the TEE-validation-failed error.
#[tokio::test]
```

**File:** crates/contract/tests/sandbox/tee.rs (L842-845)
```rust
async fn verify_tee__should_keep_participants_and_stop_signing_when_kickout_drops_below_threshold()
-> Result<()> {
    // Given
    const PARTICIPANT_COUNT: usize = 3;
```
