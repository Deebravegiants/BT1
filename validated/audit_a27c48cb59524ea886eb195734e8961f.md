### Title
Missing TEE Attestation Check in `vote_cancel_resharing` Allows Expired-TEE Participants to Block Their Own Removal - (File: crates/contract/src/lib.rs)

### Summary

The `vote_cancel_resharing` (and `vote_cancel_keygen`) contract methods check participant membership but skip the TEE attestation validation that all other governance state-transition methods enforce. This allows a participant whose TEE attestation has expired or been invalidated to vote to cancel a resharing that was initiated specifically to remove them, permanently blocking the protocol's ability to enforce its TEE security invariant.

### Finding Description

Every key-event and signing method in `MpcContract` that mutates protocol state calls `assert_caller_is_attested_participant_and_protocol_active()`, which verifies three things: (1) signer == predecessor, (2) the caller is in the active participant set, and (3) the caller has a valid stored TEE attestation. [1](#0-0) 

However, `vote_cancel_resharing` only calls `assert_caller_is_signer()` and then delegates to the state machine, which checks participant membership via `AuthenticatedAccountId::new(previous_running_participants)?` — with no TEE attestation check anywhere in the call path: [2](#0-1) [3](#0-2) 

The same omission exists in `vote_cancel_keygen`: [4](#0-3) [5](#0-4) 

By contrast, `vote_new_parameters` explicitly re-verifies TEE status for all proposed participants before accepting any vote: [6](#0-5) 

The `verify_tee()` function, when it detects that some participants have expired attestations, sets `accept_requests = true` (because threshold-many nodes still have valid attestations) and initiates a resharing to evict the invalid nodes: [7](#0-6) 

Because `vote_cancel_resharing` does not check TEE attestation, the nodes being evicted can immediately vote to cancel that resharing. If threshold-many nodes have expired attestations, they can collectively cancel the resharing, reverting to the previous `Running` state with `accept_requests = true` and themselves still in the participant set.

### Impact Explanation

**Medium.** This is a participant-state and contract execution-flow manipulation that breaks the production safety invariant that only TEE-attested nodes may participate in the MPC network. Nodes with expired or invalidated TEE attestations — which the protocol explicitly attempts to remove via `verify_tee()` → resharing — can prevent their own eviction by voting to cancel the resharing. After cancellation, the protocol reverts to the previous `Running` state with `accept_requests = true`, allowing the expired-TEE nodes to continue participating in threshold signing. This breaks the TEE security boundary without requiring any threshold-or-above collusion among honest nodes.

### Likelihood Explanation

Moderate. TEE attestations expire on a 7-day cycle per the design documentation. Any window between attestation expiry and successful resharing completion is an opportunity for the affected nodes to invoke `vote_cancel_resharing`. If threshold-many nodes' attestations expire simultaneously (e.g., after a coordinated image-hash rotation that invalidates old attestations), the attack becomes straightforward. The attacker-controlled entry path is a direct NEAR contract call requiring only a valid NEAR account key — no TEE access is needed to call `vote_cancel_resharing`.

### Recommendation

Apply the same TEE attestation gate to `vote_cancel_resharing` and `vote_cancel_keygen` that is applied to all other governance state-transition methods. Specifically, before counting a cancellation vote, verify that the caller's TEE attestation is still valid against the previous running state's participant set. If the caller's attestation has expired, the vote should be rejected. This mirrors the pattern already used in `vote_new_parameters` via `reverify_and_cleanup_participants`.

### Proof of Concept

1. Deploy the contract with N participants, all with valid TEE attestations.
2. Allow threshold-many participants' TEE attestations to expire (e.g., by advancing block timestamp past the attestation expiry).
3. Call `verify_tee()` — the contract detects the expired attestations, keeps `accept_requests = true` (threshold-many valid nodes remain), and transitions to `Resharing` to evict the expired-TEE nodes.
4. The expired-TEE nodes (still in the previous running state's participant set) each call `vote_cancel_resharing()`. No TEE check is performed; only `AuthenticatedAccountId::new(previous_running_participants)` is checked, which passes.
5. Once threshold cancellation votes are collected, the resharing is cancelled and the protocol reverts to the previous `Running` state.
6. The expired-TEE nodes remain in the participant set with `accept_requests = true` and can continue to participate in threshold signing, bypassing the TEE security invariant.

### Citations

**File:** crates/contract/src/lib.rs (L899-938)
```rust
        let tee_upgrade_deadline_duration =
            Duration::from_secs(self.config.tee_upgrade_deadline_duration_seconds);

        let validation_result = self.tee_state.reverify_and_cleanup_participants(
            proposal.participants(),
            tee_upgrade_deadline_duration,
        );

        let proposed_participants = proposal.participants();
        match validation_result {
            TeeValidationResult::Full => {
                if let Some(new_state) = self
                    .protocol_state
                    .vote_new_parameters(prospective_epoch_id, &proposal)?
                {
                    self.protocol_state = new_state;
                }
                Ok(())
            }
            TeeValidationResult::Partial {
                participants_with_valid_attestation,
            } => {
                let invalid_participants: Vec<_> = proposed_participants
                    .participants()
                    .iter()
                    .filter(|(account_id, _, _)| {
                        !participants_with_valid_attestation
                            .is_participant_given_account_id(account_id)
                    })
                    .collect();

                Err(InvalidParameters::InvalidTeeRemoteAttestation {
                    reason: format!(
                        "The following participants have invalid TEE status: {:?}",
                        invalid_participants
                    ),
                }
                .into())
            }
        }
```

**File:** crates/contract/src/lib.rs (L1254-1263)
```rust
    pub fn vote_cancel_resharing(&mut self) -> Result<(), Error> {
        Self::assert_caller_is_signer();
        log!("vote_cancel_resharing: signer={}", env::signer_account_id());

        if let Some(new_state) = self.protocol_state.vote_cancel_resharing()? {
            self.protocol_state = new_state;
        }

        Ok(())
    }
```

**File:** crates/contract/src/lib.rs (L1272-1280)
```rust
    pub fn vote_cancel_keygen(&mut self, next_domain_id: u64) -> Result<(), Error> {
        Self::assert_caller_is_signer();
        log!("vote_cancel_keygen: signer={}", env::signer_account_id());

        if let Some(new_state) = self.protocol_state.vote_cancel_keygen(next_domain_id)? {
            self.protocol_state = new_state;
        }
        Ok(())
    }
```

**File:** crates/contract/src/lib.rs (L1741-1765)
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

**File:** crates/contract/src/state/resharing.rs (L173-196)
```rust
    pub fn vote_cancel_resharing(&mut self) -> Result<Option<RunningContractState>, Error> {
        let previous_running_participants = self.previous_running_state.parameters.participants();
        let authenticated_candidate = AuthenticatedAccountId::new(previous_running_participants)?;
        self.cancellation_requests.insert(authenticated_candidate);

        let cancellation_votes_count = self.cancellation_requests.len() as u64;
        let previous_running_threshold = self.previous_running_state.parameters.threshold();

        let threshold_cancellation_votes_reached: bool =
            cancellation_votes_count >= previous_running_threshold.value();

        let running_state = if threshold_cancellation_votes_reached {
            let mut previous_running_state = self.previous_running_state.clone();
            let prospective_epoch_id = self.prospective_epoch_id();
            previous_running_state.previously_cancelled_resharing_epoch_id =
                Some(prospective_epoch_id);

            Some(previous_running_state)
        } else {
            None
        };

        Ok(running_state)
    }
```

**File:** crates/contract/src/state/initializing.rs (L117-143)
```rust
    pub fn vote_cancel(
        &mut self,
        next_domain_id: u64,
    ) -> Result<Option<RunningContractState>, Error> {
        if next_domain_id != self.domains.next_domain_id() {
            return Err(InvalidParameters::NextDomainIdMismatch.into());
        }
        let participant = AuthenticatedParticipantId::new(
            self.generating_key.proposed_parameters().participants(),
        )?;
        let required_threshold = self
            .generating_key
            .proposed_parameters()
            .threshold()
            .value() as usize;
        if self.cancel_votes.insert(participant) && self.cancel_votes.len() >= required_threshold {
            let mut domains = self.domains.clone();
            domains.retain_domains(self.generated_keys.len());
            return Ok(Some(RunningContractState::new(
                domains,
                Keyset::new(self.epoch_id, self.generated_keys.clone()),
                self.generating_key.proposed_parameters().clone(),
                AddDomainsVotes::default(),
            )));
        }
        Ok(None)
    }
```
