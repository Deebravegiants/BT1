### Title
`is_caller_an_attested_participant` Does Not Re-Verify Attestation Validity, Allowing Revoked/Expired Nodes to Submit Signatures - (File: `crates/contract/src/tee/tee_state.rs`)

### Summary

The MPC contract has two distinct code paths for checking whether a participant's TEE attestation is acceptable. `reverify_participants` correctly re-validates the stored attestation against current allowed image hashes, launcher compose hashes, measurements, and expiry. `is_caller_an_attested_participant` — the gatekeeper used on every `respond`, `respond_ckd`, and `respond_verify_foreign_tx` call — only checks that an attestation record *exists* in storage and that the stored keys match the caller's identity. It never calls `reverify_participants` or any equivalent validity check. A participant whose image hash has been governance-revoked, or whose attestation certificate has expired, retains a stale-but-present entry in `stored_attestations` and can continue submitting signature responses until the next `verify_tee()` invocation removes them from the participant set.

### Finding Description

`reverify_participants` re-validates a stored attestation against the live contract state: [1](#0-0) 

It checks expiry timestamp, current allowed MPC docker image hashes, allowed launcher compose hashes, and accepted measurements. If any check fails it returns `TeeQuoteStatus::Invalid`.

`is_caller_an_attested_participant`, used as the sole attestation gate on every node-facing response endpoint, does none of this: [2](#0-1) 

It only verifies (a) the caller is in the participant list, (b) a `NodeAttestation` entry exists keyed by the participant's TLS public key, (c) the stored `account_id` matches the signer, and (d) the stored `account_public_key` matches the signer's key. Attestation validity — expiry, image hash, measurements — is never re-checked.

`assert_caller_is_attested_participant_and_protocol_active` wraps this check and is called unconditionally in `respond`, `respond_ckd`, and `respond_verify_foreign_tx`: [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) 

The only mechanism that eventually enforces validity is `verify_tee()`, which calls `reverify_and_cleanup_participants` and, if participants fail, triggers a resharing to remove them from the participant set: [7](#0-6) 

But `verify_tee()` is an explicit, permissioned call that the docs describe as happening on a ~2-day cadence. Between invocations, the stale attestation entry remains in `stored_attestations`, and `is_caller_an_attested_participant` continues to return `Ok(())` for the revoked node.

### Impact Explanation

A participant node whose MPC image hash has been governance-revoked (e.g., because a software vulnerability was discovered) or whose attestation certificate has expired retains its `NodeAttestation` entry in `stored_attestations`. During the window between the revocation/expiry event and the next successful `verify_tee()` call, that node can call `respond` and `respond_ckd` to deliver signature outputs to the contract. Because `respond` verifies the cryptographic signature against the derived public key, the node must have participated in the actual MPC signing round to produce a valid response — meaning a node running revoked/compromised software that already holds key shares can continue to contribute to and complete threshold signatures. This breaks the core TEE security invariant: that only nodes running currently-approved software inside genuine enclaves may participate in signing operations. The impact maps to **Medium** — participant-state manipulation that breaks a production safety invariant (TEE-gated signing) without requiring network-level DoS or operator misconfiguration.

### Likelihood Explanation

The trigger conditions are realistic and operator-initiated:

1. Governance votes to remove a compromised or outdated MPC image hash (a normal operational event).
2. The revoked node's `stored_attestations` entry is not immediately purged — it persists until `verify_tee()` is called.
3. The revoked node continues to participate in MPC signing rounds (it is still in the participant set until resharing completes) and can call `respond` with valid signatures.
4. `verify_tee()` is called on a ~2-day cadence, so the window can be up to 48 hours.

No special privileges are needed beyond being an existing participant with a stale-but-present attestation entry.

### Recommendation

`is_caller_an_attested_participant` should call `reverify_participants` on the caller's stored attestation and return an error if the result is `TeeQuoteStatus::Invalid`. This mirrors the fix suggested in the Hats report: replace the raw-storage existence check with the same validity logic used by the authoritative path (`reverify_participants`), so both code paths agree on what "attested" means.

Concretely, after confirming the attestation entry exists and the keys match, add:

```rust
let tee_status = self.reverify_participants(&attestation.node_id, tee_upgrade_deadline_duration);
if !matches!(tee_status, TeeQuoteStatus::Valid) {
    return Err(AttestationCheckError::AttestationExpiredOrRevoked);
}
```

This requires threading `tee_upgrade_deadline_duration` into `is_caller_an_attested_participant` (and by extension into `assert_caller_is_attested_participant_and_protocol_active`), which is already available on `self.config` in `MpcContract`.

### Proof of Concept

1. Deploy the contract with 3 participants (threshold 2). All submit valid attestations.
2. Governance votes to remove the MPC image hash that participant A's attestation references. The hash is removed from `allowed_docker_image_hashes`.
3. Participant A's `stored_attestations` entry still exists. `is_caller_an_attested_participant` called for participant A returns `Ok(())` — it never calls `reverify_participants`.
4. A user submits a `sign` request. The MPC network (including participant A) runs the signing protocol and produces a valid threshold signature.
5. Participant A calls `respond` with the valid signature. The call succeeds: `assert_caller_is_attested_participant_and_protocol_active` passes (stale entry present), `accept_requests` is still `true`, and the signature is cryptographically valid.
6. The signature is delivered to the user. Participant A — running software whose image hash governance has revoked — has contributed to and completed a threshold signature, violating the TEE attestation invariant.
7. Only after a participant calls `verify_tee()` does `reverify_and_cleanup_participants` detect the invalid attestation and trigger resharing to remove participant A. [8](#0-7) [2](#0-1)

### Citations

**File:** crates/contract/src/tee/tee_state.rs (L206-232)
```rust
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

**File:** crates/contract/src/lib.rs (L564-574)
```rust
    pub fn respond(
        &mut self,
        request: SignatureRequest,
        response: dtos::SignatureResponse,
    ) -> Result<(), Error> {
        let signer = Self::assert_caller_is_signer();

        log!("respond: signer={}, request={:?}", &signer, &request);

        self.assert_caller_is_attested_participant_and_protocol_active();

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

**File:** crates/contract/src/lib.rs (L691-706)
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

```

**File:** crates/contract/src/lib.rs (L1693-1770)
```rust
    pub fn verify_tee(&mut self) -> Result<bool, Error> {
        log!("verify_tee: signer={}", env::signer_account_id());
        // Caller must be a participant (node or operator).
        self.voter_or_panic();
        let ProtocolContractState::Running(running_state) = &mut self.protocol_state else {
            return Err(InvalidState::ProtocolStateNotRunning.into());
        };
        let current_params = running_state.parameters.clone();

        let tee_upgrade_deadline_duration =
            Duration::from_secs(self.config.tee_upgrade_deadline_duration_seconds);

        match self.tee_state.reverify_and_cleanup_participants(
            current_params.participants(),
            tee_upgrade_deadline_duration,
        ) {
            TeeValidationResult::Full => {
                self.accept_requests = true;
                log!("All participants have an accepted Tee status");
                Ok(true)
            }
            TeeValidationResult::Partial {
                participants_with_valid_attestation,
            } => {
                let remaining = participants_with_valid_attestation.len();
                // Defense in depth: the surviving participant set must keep the full
                // threshold relation intact — the GovernanceThreshold must still sit
                // within its bounds for the smaller set (in particular it must not
                // exceed the remaining participant count or the upper cap) and must
                // remain at least every domain's ReconstructionThreshold (the kickout
                // keeps the existing per-domain thresholds). Otherwise we refuse and
                // wait for manual intervention.
                let max_reconstruction_threshold =
                    max_reconstruction_threshold(running_state.domains.domains());
                if let Err(err) = ThresholdParameters::validate_governance_against_reconstruction(
                    u64::try_from(remaining).expect("participant count fits in u64"),
                    current_params.threshold(),
                    max_reconstruction_threshold,
                ) {
                    log!(
                        "Kicking out participants with an invalid TEE status would break the threshold relation ({:?}); {} participants remain with a valid TEE status. This requires manual intervention. We will not accept new signature requests as a safety precaution.",
                        err,
                        remaining,
                    );
                    self.accept_requests = false;
                    return Ok(false);
                }

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
            }
        }
    }
```

**File:** crates/contract/src/lib.rs (L2389-2403)
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
    }
```
