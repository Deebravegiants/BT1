### Title
Missing Attestation Validity Re-Check in `is_caller_an_attested_participant` Allows Expired/Invalidated Nodes to Submit Signatures — (`File: crates/contract/src/tee/tee_state.rs`)

### Summary

`is_caller_an_attested_participant()` verifies that a stored attestation entry exists and that the stored keys match the caller, but never calls `re_verify()` on the stored `VerifiedAttestation`. The parallel function `reverify_participants()` — used by `verify_tee()` and `vote_new_parameters()` — does call `re_verify()`, which checks expiry and image-hash/launcher-hash/measurement allowlists. The missing re-verify call in the caller-authorization path is the direct analog of the missing `block.timestamp > 2 hours + baseTimeStamp` condition in `oracleCircuitBreaker()`.

### Finding Description

`is_caller_an_attested_participant()` is the gate that every node-facing write method (`respond()`, `respond_verify_foreign_tx()`, and others) passes through via `assert_caller_is_attested_participant_and_protocol_active()`. It performs three checks:

1. The signer is in the current participant set.
2. A stored attestation entry exists for that participant's TLS key.
3. The stored `account_id` and `account_public_key` match the transaction signer. [1](#0-0) 

What it does **not** do is call `re_verify()` on the stored `VerifiedAttestation`. `re_verify()` checks:

- `expiry_timestamp_seconds < timestamp_seconds` (attestation has not expired)
- The stored `mpc_image_hash` is still in the allowed image-hash list
- The stored `launcher_compose_hash` is still in the allowed launcher list
- The stored `measurements` are still in the allowed measurement list [2](#0-1) 

By contrast, `reverify_participants()` — called by `verify_tee()` and `vote_new_parameters()` — does perform the full `re_verify()` check: [3](#0-2) 

The asymmetry is exact: `reverify_participants` is to `is_caller_an_attested_participant` as `baseOracleCircuitBreaker` is to `oracleCircuitBreaker` in the reference report.

**Concrete attack path:**

1. Node A holds a valid attestation and is an active participant.
2. Node A's attestation expires **or** its image hash is removed from the allowed list (e.g., a vulnerability is found in that image and operators vote to remove it via `vote_code_hash`).
3. `verify_tee()` is called. Because the remaining participants still meet the threshold, `accept_requests` is set to `true` and resharing begins.
4. During the resharing period, Node A is still in the **old** participant set (resharing has not completed). `respond()` accepts calls from old participants (`is_running_or_resharing()` returns `true`).
5. Node A calls `respond()`. `assert_caller_is_attested_participant_and_protocol_active()` → `is_caller_an_attested_participant()` passes because the stored entry still exists and the keys still match. The expiry/image-hash check is never performed.
6. The contract accepts Node A's signature response and resolves the pending yield. [4](#0-3) 

### Impact Explanation

The TEE security model's core invariant is: **only nodes running an approved image inside a genuine TDX enclave may participate in threshold signing**. The `is_caller_an_attested_participant` gap breaks this invariant. A node whose image hash has been revoked (because a vulnerability was found in that image) can continue submitting valid signature responses for pending requests during the resharing window. The contract accepts those responses and resolves user yields with signatures produced by a node that the governance system has explicitly decided should no longer be trusted.

This maps to the allowed Medium impact: *"participant-state or contract execution-flow manipulation that breaks production safety/accounting invariants."*

### Likelihood Explanation

The window is bounded by the resharing duration (typically minutes to hours on a live network). The trigger condition — an image hash being removed while pending signature requests exist — is a realistic operational event (image rotation, security patch). Any node whose attestation has lapsed or whose image hash was removed can exploit this unilaterally, with no collusion required.

### Recommendation

Add a `re_verify()` call inside `is_caller_an_attested_participant()`, mirroring what `reverify_participants()` already does:

```rust
pub(crate) fn is_caller_an_attested_participant(
    &self,
    participants: &Participants,
    tee_upgrade_deadline_duration: Duration,   // add parameter
) -> Result<(), AttestationCheckError> {
    // ... existing key-match checks ...

    // ADD: re-verify the stored attestation is still valid right now
    let time_stamp_seconds = Self::current_time_seconds();
    let allowed_mpc_docker_image_hashes =
        self.get_allowed_mpc_docker_image_hashes(tee_upgrade_deadline_duration);
    let allowed_launcher_compose_hashes = self.get_allowed_launcher_compose_hashes();
    let allowed_measurements = self.get_accepted_measurements();

    attestation
        .verified_attestation
        .re_verify(
            time_stamp_seconds,
            &allowed_mpc_docker_image_hashes,
            &allowed_launcher_compose_hashes,
            &allowed_measurements,
        )
        .map_err(|_| AttestationCheckError::AttestationExpiredOrInvalid)?;

    Ok(())
}
```

Pass `tee_upgrade_deadline_duration` from `assert_caller_is_attested_participant_and_protocol_active`, which already reads it from `self.config`.

### Proof of Concept

1. Deploy the contract with 3 participants (threshold 2). All three submit valid attestations.
2. Remove participant A's image hash from the allowed list via `vote_code_hash` (simulating a security patch).
3. Call `verify_tee()`. Because 2 of 3 participants remain valid (≥ threshold), `accept_requests = true` and resharing begins.
4. While resharing is in progress, call `respond()` from participant A's account with a valid signature for a pending request.
5. Observe: `assert_caller_is_attested_participant_and_protocol_active()` passes (the stored entry exists, keys match), `accept_requests` is `true`, and the contract resolves the yield — despite participant A running a revoked image.

The existing unit test `test_verify_tee_triggers_resharing_and_kickout_on_expired_attestation` confirms that resharing is entered while `accept_requests = true`, establishing the window. [5](#0-4) [1](#0-0) [3](#0-2)

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

**File:** crates/contract/src/tee/tee_state.rs (L469-498)
```rust
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

**File:** crates/mpc-attestation/src/attestation.rs (L214-255)
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

                let () = verify_mpc_hash(mpc_image_hash, allowed_mpc_docker_image_hashes)?;
                let () = verify_launcher_compose_hash(
                    launcher_compose_hash,
                    allowed_launcher_docker_compose_hashes,
                )?;

                verify_measurements(measurements, allowed_measurements)?;

                Ok(())
            }
            Self::Mock(mock_attestation) => mock_attestation.verify_constraints(
                timestamp_seconds,
                allowed_mpc_docker_image_hashes,
                allowed_launcher_docker_compose_hashes,
                allowed_measurements,
            ),
        }
    }
```

**File:** crates/contract/src/lib.rs (L563-582)
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

**File:** crates/contract/src/lib.rs (L1740-1767)
```rust

                // here, we set it to true, because at this point, we have at least `threshold`
                // number of participants with an accepted Tee status.
                self.accept_requests = true;

                // do we want to adjust the threshold?
                //let n_participants_new = new_participants.len();
                //let new_threshold = (3 * n_participants_new + 4) / 5; // minimum 60%
                //let new_threshold = new_threshold.max(2); // but also minimum 2
                let new_threshold = usize::try_from(current_params.threshold().value())
                    .expect("threshold value fits in usize");

                let threshold_parameters = ThresholdParameters::new(
                    participants_with_valid_attestation,
                    Threshold::new(new_threshold as u64),
                )
                .expect("Require valid threshold parameters"); // this should never happen.
                current_params.validate_incoming_proposal(&threshold_parameters)?;
                // This resharing only changes the participant set, so the
                // per-domain reconstruction-threshold updates map is empty.
                let proposed_parameters =
                    ProposedThresholdParameters::new(threshold_parameters, BTreeMap::new());
                let res = running_state.transition_to_resharing_no_checks(&proposed_parameters);
                if let Some(resharing) = res {
                    self.protocol_state = ProtocolContractState::Resharing(resharing);
                }

                Ok(true)
```
