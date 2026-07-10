### Title
Stale Attestation Existence Check in `is_caller_an_attested_participant` Allows Expired-TEE Participants to Submit Signatures - (File: `crates/contract/src/tee/tee_state.rs`)

### Summary

`is_caller_an_attested_participant` only verifies that a stored attestation *exists* for the calling participant; it never re-verifies whether that attestation is still valid (i.e., not expired, image hash still approved). Attestation expiry is only checked inside `verify_tee` → `reverify_and_cleanup_participants`, which is called on a periodic schedule by nodes. During the window between attestation expiry and the next `verify_tee` call, a participant whose TEE attestation has expired can still successfully call `respond`, `respond_ckd`, or `respond_verify_foreign_tx`, bypassing the TEE attestation requirement.

### Finding Description

**Root cause — `is_caller_an_attested_participant` (tee_state.rs:469–498):**

```rust
pub(crate) fn is_caller_an_attested_participant(
    &self,
    participants: &Participants,
) -> Result<(), AttestationCheckError> {
    ...
    let attestation = self
        .stored_attestations
        .get(&info.tls_public_key)
        .ok_or(AttestationCheckError::AttestationNotFound)?;   // ← only checks existence

    // account_id and account_public_key match checks follow
    // NO expiry / re_verify call is made here
    Ok(())
}
```

The function checks four things: (1) caller is in the participant list, (2) a stored attestation exists for the caller's TLS key, (3) the attestation's `account_id` matches the caller, (4) the attestation's `account_public_key` matches the signer. It does **not** call `re_verify` or check the attestation's expiry timestamp.

**Where expiry IS checked — `reverify_participants` (tee_state.rs:206–231):**

```rust
match participant_attestation.verified_attestation.re_verify(
    time_stamp_seconds,
    &allowed_mpc_docker_image_hashes,
    ...
) {
    Ok(()) => TeeQuoteStatus::Valid,
    Err(err) => TeeQuoteStatus::Invalid(err.to_string()),
}
```

This is only reachable via `reverify_and_cleanup_participants` → `verify_tee` (lib.rs:1705), which is called on a schedule by nodes, not inline during `respond`.

**The gating check in `respond` (lib.rs:2389–2402):**

```rust
fn assert_caller_is_attested_participant_and_protocol_active(&self) {
    let participants = self.protocol_state.active_participants();
    Self::assert_caller_is_signer();
    let attestation_check = self
        .tee_state
        .is_caller_an_attested_participant(participants);  // ← stale check
    assert_matches!(attestation_check, Ok(()), "Caller must be an attested participant");
}
```

All three respond endpoints (`respond`, `respond_ckd`, `respond_verify_foreign_tx`) call this function, which delegates to the stale existence-only check.

**Attack scenario:**

1. Participant P has a valid TEE attestation stored in `tee_state.stored_attestations`. The last `verify_tee` call set `accept_requests = true`.
2. Time advances past P's attestation expiry (or the governance removes P's approved image hash). P is now running in an untrusted/unapproved TEE environment.
3. `verify_tee` has not yet been called again (it runs on a schedule).
4. P calls `respond` with a valid cryptographic signature for a pending request.
5. `is_caller_an_attested_participant` passes — the attestation record still exists in storage.
6. `accept_requests` is still `true` — the last `verify_tee` call approved it.
7. The response is accepted and the pending yield is resolved.

This is structurally identical to the Carapace M-2 bug: the pool/participant status is cached and not refreshed at the point of the security-critical action.

### Impact Explanation

A participant whose TEE attestation has expired — meaning the governance has revoked trust in their running image, or their certificate has lapsed — can continue to participate in threshold signing without a valid TEE guarantee. This breaks the core safety invariant that every signing participant must be running in an approved, attested TEE environment. In the worst case, a participant running a governance-revoked image (e.g., one with a known key-extraction vulnerability) can continue contributing signing shares, undermining the confidentiality guarantee of the MPC key material.

**Impact: Medium** — participant-state invariant broken (all active signers must hold valid TEE attestations); does not by itself enable direct fund theft since the contract still verifies the cryptographic signature, but it breaks the production safety accounting that TEE attestation provides.

### Likelihood Explanation

Every deployment has a scheduled `verify_tee` interval. Any attestation that expires between two consecutive `verify_tee` calls creates this window. A Byzantine participant who knows their attestation is about to expire (or whose image hash was just revoked by governance) can front-run the next `verify_tee` call and submit responses during the gap. This is a realistic, low-effort exploit requiring no collusion.

### Recommendation

In `is_caller_an_attested_participant`, after confirming the attestation exists, call `reverify_participants` (or an equivalent inline expiry check) to confirm the stored attestation is still valid at the current block timestamp and against the current allowed image/measurement sets. This mirrors the recommendation in the Carapace report: update/re-assess state at the point of the security-critical action rather than relying on a cached value set by a separate scheduled call.

```rust
// After confirming existence and key match:
let tee_status = self.reverify_participants(&attestation.node_id, tee_upgrade_deadline_duration);
if !matches!(tee_status, TeeQuoteStatus::Valid) {
    return Err(AttestationCheckError::AttestationExpiredOrInvalid);
}
```

### Proof of Concept

1. Deploy contract with 3 participants (threshold = 2). All submit valid attestations with `expiry_timestamp_seconds = T`.
2. Advance block timestamp past `T` without calling `verify_tee`.
3. Participant 3 (expired attestation) calls `respond` with a valid signature for a pending request.
4. `is_caller_an_attested_participant` returns `Ok(())` — the attestation record still exists in `stored_attestations`.
5. `accept_requests` is still `true` — the last `verify_tee` call approved it.
6. `respond` succeeds and resolves the pending yield.
7. Now call `verify_tee` — it detects the expired attestation and triggers resharing/kickout.

The gap between steps 2 and 7 is the exploitable window, directly analogous to the Carapace pool-status caching window.