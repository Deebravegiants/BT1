### Title
Expired TEE Attestation Not Checked in Per-Call Participant Guard, Allowing Untrusted Nodes to Participate in Signing and Key Events - (File: crates/contract/src/tee/tee_state.rs)

### Summary

`is_caller_an_attested_participant` — the per-call guard used to gate every signing response and key-event vote — verifies that a stored attestation *exists* for the caller but never checks whether that attestation has *expired* or whether the node's image hash is still in the allowed whitelist. A node whose TEE certificate has lapsed, or that is running a revoked MPC image, can therefore continue to call `respond`, `vote_pk`, `vote_reshared`, and related methods until an operator manually invokes `verify_tee`.

### Finding Description

`TeeState::is_caller_an_attested_participant` performs four checks:

1. Caller is in the active participants list.
2. A `NodeAttestation` entry exists for the caller's TLS key.
3. The stored `account_id` matches the signer.
4. The stored `account_public_key` matches the signer's Ed25519 key. [1](#0-0) 

It does **not** call `VerifiedAttestation::re_verify`, which is the function that checks:

- `expiry_timestamp_seconds < timestamp_seconds` (certificate expiry)
- MPC image hash still in the allowed whitelist
- Launcher compose hash still in the allowed whitelist
- TEE measurements still in the allowed set [2](#0-1) 

`assert_caller_is_attested_participant_and_protocol_active` wraps `is_caller_an_attested_participant` and is the sole attestation gate for all of the following public methods:

- `respond` — submits a threshold signature
- `respond_ckd` — submits a CKD response
- `respond_verify_foreign_tx` — submits a foreign-tx verification response
- `vote_pk` — votes for a public key during key generation
- `vote_reshared` — votes for successful key resharing
- `vote_abort_key_event_instance` — aborts a key event
- `start_keygen_instance` / `start_reshare_instance` — starts a key event as leader [3](#0-2) 

The separate `verify_tee` function *does* call `reverify_and_cleanup_participants`, which internally calls `re_verify` and checks expiry. However, `verify_tee` is a periodic, operator-triggered call — it is not invoked on every transaction. [4](#0-3) 

The analog to the reported loan-liquidation bug is exact: the loan function checked the expiration *buffer* but not the loan *duration*; here, `is_caller_an_attested_participant` checks that an attestation *exists* but not whether it has *expired* — the second, equally necessary condition.

### Impact Explanation

Between successive `verify_tee` calls, a node whose TEE certificate has expired (or whose image hash has been revoked) retains full ability to:

1. Submit threshold signatures via `respond` — bypassing the TEE-validity invariant that only nodes running authorized, unexpired enclaves may contribute signing shares.
2. Cast `vote_pk` and `vote_reshared` votes — allowing a potentially compromised node to participate in key generation and resharing ceremonies.

The `accept_requests` flag set by `verify_tee` partially mitigates `respond` for *new* sign requests, but `vote_pk` and `vote_reshared` have no such guard: [5](#0-4) 

This breaks the production safety invariant that only nodes with currently valid TEE attestations may participate in protocol operations.

**Impact class:** Medium — participant-state manipulation that breaks production safety/accounting invariants.

### Likelihood Explanation

TEE certificates expire naturally on a fixed schedule (`expiry_timestamp_seconds` is embedded in every `ValidatedDstackAttestation`). The default `tee_upgrade_deadline_duration_seconds` is 7 days. Any window between certificate expiry and the next `verify_tee` invocation is an open window. Because `verify_tee` is not called automatically on every block, this window can be arbitrarily long if operators are slow to act or if the network is under stress. No privileged access is required — the expired node itself triggers the bypass simply by continuing to call contract methods.

### Recommendation

Add an expiry check inside `is_caller_an_attested_participant`. After retrieving the stored `NodeAttestation`, call `verified_attestation.re_verify(...)` with the current block timestamp and the current allowed-hash lists. Return an `AttestationCheckError` variant (e.g., `AttestationExpired`) if re-verification fails. This mirrors the check already performed in `reverify_participants` and closes the gap between the per-call guard and the periodic `verify_tee` sweep. [6](#0-5) 

### Proof of Concept

1. Node A is a legitimate participant with a valid attestation at time T=0.
2. At T=expiry, node A's TEE certificate expires. `verify_tee` has not been called yet.
3. Node A calls `vote_reshared(key_event_id)`.
4. `assert_caller_is_attested_participant_and_protocol_active` is invoked.
5. `is_caller_an_attested_participant` finds node A's entry in `stored_attestations`, confirms account ID and public key match — and returns `Ok(())` without checking expiry.
6. Node A's vote is accepted and counted toward the resharing threshold, despite running an expired (potentially unauthorized) enclave.

The same path applies to `vote_pk` during key generation and to `respond` during the window before `verify_tee` sets `accept_requests = false`. [1](#0-0) [3](#0-2)

### Citations

**File:** crates/contract/src/tee/tee_state.rs (L280-340)
```rust
        &mut self,
        code_hash: NodeImageHash,
        participant: &AuthenticatedParticipantId,
    ) -> u64 {
        self.votes.vote(code_hash, participant)
    }

    pub fn get_allowed_mpc_docker_image_hashes(
        &self,
        tee_upgrade_deadline_duration: Duration,
    ) -> Vec<NodeImageHash> {
        self.get_allowed_mpc_docker_images(tee_upgrade_deadline_duration)
            .into_iter()
            .map(|entry| entry.image_hash)
            .collect()
    }

    pub fn get_allowed_mpc_docker_images(
        &self,
        tee_upgrade_deadline_duration: Duration,
    ) -> Vec<AllowedMpcDockerImage> {
        self.allowed_docker_image_hashes
            .get(tee_upgrade_deadline_duration)
    }

    pub fn whitelist_tee_proposal(
        &mut self,
        tee_proposal: NodeImageHash,
        tee_upgrade_deadline_duration: Duration,
    ) {
        self.votes.clear_votes();
        // Add compose hashes for the new MPC image across all allowed launcher images
        self.allowed_launcher_images
            .add_mpc_image_compose_hashes(&tee_proposal);
        self.allowed_docker_image_hashes
            .insert(tee_proposal, tee_upgrade_deadline_duration);
    }

    /// Returns all allowed launcher compose hashes (flattened from all allowed launcher images).
    pub fn get_allowed_launcher_compose_hashes(&self) -> Vec<LauncherDockerComposeHash> {
        self.allowed_launcher_images.all_compose_hashes()
    }

    /// Casts a vote for adding or removing a launcher image hash.
    /// Returns the total number of votes for the same action.
    pub fn vote_launcher(
        &mut self,
        action: LauncherVoteAction,
        participant: &AuthenticatedParticipantId,
    ) -> u64 {
        self.launcher_votes.vote(action, participant)
    }

    /// Adds a new launcher image to the allowed set, computing compose hashes
    /// for all currently allowed MPC images. Clears launcher votes.
    pub fn add_launcher_image(
        &mut self,
        launcher_hash: LauncherImageHash,
        tee_upgrade_deadline_duration: Duration,
    ) -> bool {
        self.launcher_votes.clear_votes();
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

**File:** crates/mpc-attestation/src/attestation.rs (L215-255)
```rust
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

**File:** crates/contract/src/lib.rs (L1161-1172)
```rust
    pub fn vote_reshared(&mut self, key_event_id: KeyEventId) -> Result<(), Error> {
        log!(
            "vote_reshared: signer={}, resharing_id={:?}",
            env::signer_account_id(),
            key_event_id,
        );

        self.assert_caller_is_attested_participant_and_protocol_active();

        if let Some(new_state) = self.protocol_state.vote_reshared(key_event_id)? {
            // Resharing has concluded, transition to running state
            self.protocol_state = new_state;
```

**File:** crates/contract/src/lib.rs (L1693-1712)
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
