### Title
Expired TEE Attestation Not Checked at Signing Time Allows Unverified Node to Submit Signatures — (File: `crates/contract/src/tee/tee_state.rs`)

### Summary

The `is_caller_an_attested_participant` function, which gates all `respond()`, `respond_ckd()`, and `respond_verify_foreign_tx()` calls, checks that a stored attestation *exists* for the caller but never checks whether that attestation has *expired*. A node whose TEE attestation has lapsed can continue submitting signatures to the contract indefinitely, bypassing the TEE security invariant that only nodes running in a verified trusted-execution environment may participate in signing operations.

---

### Finding Description

`is_caller_an_attested_participant` in `crates/contract/src/tee/tee_state.rs` performs four checks:

1. Caller is in the active participant set.
2. A stored attestation entry exists for the caller's TLS key.
3. The stored `account_id` matches the caller.
4. The stored `account_public_key` matches the caller's signing key. [1](#0-0) 

It does **not** call `re_verify` or compare `expiry_timestamp_seconds` against the current block timestamp. The expiry check exists in `reverify_participants` and `clean_invalid_attestations`, but those are only invoked when `verify_tee()` is explicitly called as a separate transaction. [2](#0-1) 

`assert_caller_is_attested_participant_and_protocol_active`, which wraps `is_caller_an_attested_participant`, is the sole per-call TEE gate for all three `respond*` entry points: [3](#0-2) 

Called unconditionally inside `respond()`: [4](#0-3) 

And inside `respond_ckd()` and `respond_verify_foreign_tx()`: [5](#0-4) [6](#0-5) 

The `accept_requests` flag is a coarser guard: it is only set to `false` when `verify_tee()` determines that the *total* count of valid attestations falls below threshold. When the threshold is still met by other participants, `accept_requests` stays `true`, and the individual node with the expired attestation is never blocked at the per-call level.

The `expiry_timestamp_seconds` field in `ValidatedDstackAttestation` is the authoritative expiry value stored after initial verification: [7](#0-6) 

`re_verify` correctly checks it: [8](#0-7) 

But `is_caller_an_attested_participant` never calls `re_verify`.

---

### Impact Explanation

The TEE model's purpose is to guarantee that only nodes running *authorized, unmodified code* inside a hardware-isolated enclave can submit signatures. Once a node's attestation expires, the contract can no longer make that guarantee. Because `is_caller_an_attested_participant` does not enforce expiry, a node whose TEE certificate has lapsed — and which may now be running arbitrary code — can still call `respond()` and have its signature accepted by the contract. This breaks the production safety invariant that every signing participant must be continuously verified as running trusted code, constituting contract execution-flow manipulation that bypasses the TEE authorization layer.

**Allowed impact match:** Medium — participant-state and contract execution-flow manipulation that breaks production safety/accounting invariants.

---

### Likelihood Explanation

Attestations expire on a fixed schedule (default 7 days, `DEFAULT_EXPIRATION_DURATION_SECONDS`). `verify_tee()` is not called automatically on every `respond()` — it must be triggered as a separate transaction. In a network where the threshold is still met by other participants, `accept_requests` remains `true` after `verify_tee()` runs, so the expired-attestation node is never individually blocked. The window between expiry and cleanup is therefore routine and predictable, not exceptional.

---

### Recommendation

Add an expiry check inside `is_caller_an_attested_participant` immediately after retrieving the stored attestation:

```rust
// After retrieving `attestation` from `stored_attestations`:
let now = Self::current_time_seconds();
attestation
    .verified_attestation
    .re_verify(
        now,
        &self.get_allowed_mpc_docker_image_hashes(tee_upgrade_deadline_duration),
        &self.get_allowed_launcher_compose_hashes(),
        &self.get_accepted_measurements(),
    )
    .map_err(|_| AttestationCheckError::AttestationExpiredOrInvalid)?;
```

This mirrors the check already performed in `reverify_participants` and ensures that every `respond*` call is gated on a *currently valid* attestation, not merely a *historically stored* one.

---

### Proof of Concept

1. Deploy the contract with 3 participants (threshold = 2). All three submit valid attestations with `expiry_timestamp_seconds = T`.
2. Advance block time past `T`. Participant A's attestation is now expired.
3. Call `verify_tee()`. It finds 2 valid attestations (B and C); threshold is met; `accept_requests` remains `true`. Participant A is not removed from the participant set (no resharing triggered because threshold is still met).
4. Participant A calls `respond(request, valid_signature)`.
5. `assert_caller_is_attested_participant_and_protocol_active` calls `is_caller_an_attested_participant`, which finds A's stored attestation entry, matches account ID and public key, and returns `Ok(())` — **without checking `expiry_timestamp_seconds`**.
6. The contract accepts the signature. Participant A, whose TEE is no longer verified, has successfully submitted a signature as if it were still a trusted enclave participant. [1](#0-0) [9](#0-8)

### Citations

**File:** crates/contract/src/tee/tee_state.rs (L205-232)
```rust
    /// reverifies stored participant attestations.
    pub(crate) fn reverify_participants(
        &self,
        node_id: &NodeId,
        tee_upgrade_deadline_duration: Duration,
    ) -> TeeQuoteStatus {
        let allowed_mpc_docker_image_hashes =
            self.get_allowed_mpc_docker_image_hashes(tee_upgrade_deadline_duration);
        let allowed_launcher_compose_hashes = self.get_allowed_launcher_compose_hashes();
        let allowed_measurements = self.get_accepted_measurements();

        let participant_attestation = self.stored_attestations.get(&node_id.tls_public_key);
        let Some(participant_attestation) = participant_attestation else {
            return TeeQuoteStatus::Invalid("participant has no attestation".to_string());
        };

        // Verify the attestation quote
        let time_stamp_seconds = Self::current_time_seconds();
        match participant_attestation.verified_attestation.re_verify(
            time_stamp_seconds,
            &allowed_mpc_docker_image_hashes,
            &allowed_launcher_compose_hashes,
            &allowed_measurements,
        ) {
            Ok(()) => TeeQuoteStatus::Valid,
            Err(err) => TeeQuoteStatus::Invalid(err.to_string()),
        }
    }
```

**File:** crates/contract/src/tee/tee_state.rs (L466-498)
```rust
    /// whose TLS key matches an attested node belonging to the caller account.
    ///
    /// Handles multiple participants per account and supports legacy mock nodes.
    pub(crate) fn is_caller_an_attested_participant(
        &self,
        participants: &Participants,
    ) -> Result<(), AttestationCheckError> {
        let signer_account_pk = env::signer_account_pk();
        let signer_id = env::signer_account_id();

        let info = participants
            .info(&signer_id)
            .ok_or(AttestationCheckError::CallerNotParticipant)?;

        let attestation = self
            .stored_attestations
            .get(&info.tls_public_key)
            .ok_or(AttestationCheckError::AttestationNotFound)?;

        if attestation.node_id.account_id != signer_id {
            return Err(AttestationCheckError::AttestationOwnerMismatch);
        }

        // Stored account keys are Ed25519 by construction; a non-Ed25519
        // signer necessarily mismatches.
        let signer_ed25519 = Ed25519PublicKey::try_from(&signer_account_pk)
            .map_err(|_| AttestationCheckError::AttestationKeyMismatch)?;
        if attestation.node_id.account_public_key != signer_ed25519 {
            return Err(AttestationCheckError::AttestationKeyMismatch);
        }

        Ok(())
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

**File:** crates/contract/src/lib.rs (L2389-2402)
```rust
    fn assert_caller_is_attested_participant_and_protocol_active(&self) {
        let participants = self.protocol_state.active_participants();

        Self::assert_caller_is_signer();

        let attestation_check = self
            .tee_state
            .is_caller_an_attested_participant(participants);

        assert_matches::assert_matches!(
            attestation_check,
            Ok(()),
            "Caller must be an attested participant"
        );
```

**File:** crates/mpc-attestation/src/attestation.rs (L203-212)
```rust
pub struct ValidatedDstackAttestation {
    pub mpc_image_hash: NodeImageHash,
    pub launcher_compose_hash: LauncherDockerComposeHash,
    // TODO(#1639): This timestamp can not come from the contract,
    // but should be extracted from the certificate itself.
    pub expiry_timestamp_seconds: u64,
    /// The measurements that were verified during initial attestation.
    /// Stored so that re-verification can check they are still in the allowed set.
    pub measurements: ExpectedMeasurements,
}
```

**File:** crates/mpc-attestation/src/attestation.rs (L214-236)
```rust
impl VerifiedAttestation {
    pub fn re_verify(
        &self,
        timestamp_seconds: u64,
        allowed_mpc_docker_image_hashes: &[NodeImageHash],
        allowed_launcher_docker_compose_hashes: &[LauncherDockerComposeHash],
        allowed_measurements: &[ExpectedMeasurements],
    ) -> Result<(), VerificationError> {
        match self {
            Self::Dstack(ValidatedDstackAttestation {
                mpc_image_hash,
                launcher_compose_hash,
                expiry_timestamp_seconds: expiration_timestamp_seconds,
                measurements,
            }) => {
                let attestation_has_expired = *expiration_timestamp_seconds < timestamp_seconds;

                if attestation_has_expired {
                    return Err(VerificationError::Custom(format!(
                        "The attestation expired at t = {:?}, time_now = {:?}",
                        expiration_timestamp_seconds, timestamp_seconds
                    )));
                }
```
