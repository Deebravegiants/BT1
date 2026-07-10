### Title
Stale Measurement Votes From Removed Participants Bypass Unanimity Requirement After Resharing - (`crates/contract/src/lib.rs`, `crates/contract/src/tee/measurements.rs`)

### Summary

After a resharing event reduces the participant set, `vote_remove_os_measurement` compares the raw vote count (which still includes stale votes from removed participants) against the new, smaller `total_participants`. Because the stale-vote cleanup (`clean_tee_status`) is dispatched as a **detached promise** and runs in a later block, there is a window in which the unanimity check can be satisfied without all current participants having voted.

### Finding Description

`vote_remove_os_measurement` enforces a unanimity rule: every current participant must vote before an OS measurement is removed from the allowed list. [1](#0-0) 

The vote count is computed by `MeasurementVotes::count_votes`, which iterates over **all** entries in `vote_by_account` without filtering for current participants: [2](#0-1) 

When resharing completes, `vote_reshared` transitions the contract to the new (smaller) participant set and then spawns `clean_tee_status` as a **detached** promise: [3](#0-2) 

`clean_tee_status` calls `tee_state.clean_non_participant_votes`, which removes stale votes: [4](#0-3) 

Because the detached promise runs in a **subsequent block**, there is a window between resharing completion and cleanup where:

- `total_participants` reflects the new, smaller count (denominator shrinks), and
- `vote_by_account` still contains votes from removed participants (numerator stays inflated).

### Impact Explanation

An OS measurement can be removed from the allowed list without unanimous consent of all current participants. Removed measurements cause nodes running those measurements to fail attestation re-verification (`clean_invalid_attestations` evicts them). If the removed measurement is the only one currently in use, all nodes lose their attested status, the network falls below signing threshold, and funds controlled by the MPC network are permanently frozen — matching the **Critical: permanent freezing of funds** impact class.

### Likelihood Explanation

The window is one block wide (the gap between `vote_reshared` finalizing and the detached `clean_tee_status` receipt executing). An attacker who is a current participant and who arranged for removed participants to have voted before resharing can exploit this deterministically by submitting their `vote_remove_os_measurement` call in the same block as `vote_reshared`. Resharing is a routine governance operation, making the precondition reachable without any privileged access beyond being a participant.

### Recommendation

Replace the deferred cleanup with an **inline** stale-vote purge inside `vote_remove_os_measurement` itself, before counting votes:

```rust
pub fn vote_remove_os_measurement(...) {
    // ...
    // Purge stale votes before counting
    self.tee_state.measurement_votes =
        self.tee_state.measurement_votes.get_remaining_votes(
            threshold_parameters.participants()
        );

    let votes = self.tee_state.vote_measurement(action, &participant);
    let total_participants = threshold_parameters.participants().len() as u64;
    if votes >= total_participants {
        ...
    }
}
```

Alternatively, `count_votes` should accept the current participant set and filter entries before counting, mirroring the pattern already used in `get_remaining_votes`. [5](#0-4) 

### Proof of Concept

1. Network has 5 participants {P1, P2, P3, P4, P5}, unanimity = 5.
2. P1, P3, P4 call `vote_remove_os_measurement(M)` — 3 votes, not enough.
3. Governance resharing removes P3, P4, P5 and adds P6; new set = {P1, P2, P6}, unanimity = 3.
4. `vote_reshared` completes; `clean_tee_status` is dispatched as a detached promise (not yet executed).
5. P1 calls `vote_remove_os_measurement(M)` again (idempotent re-vote).
6. `total_participants` = 3; `count_votes` returns 3 (P1 + P3 stale + P4 stale).
7. `3 >= 3` → measurement M is removed. P2 and P6 never voted.
8. All nodes attested under M fail re-verification; network falls below threshold; signing is permanently frozen. [6](#0-5) [7](#0-6)

### Citations

**File:** crates/contract/src/lib.rs (L1160-1193)
```rust
    #[handle_result]
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
            self.recompute_available_foreign_chains();

            // Spawn a promise to clean up votes from non-participants.
            // Note: MpcContract::vote_update uses filtering to ensure correctness even if this cleanup fails.
            Promise::new(env::current_account_id())
                .function_call(
                    method_names::REMOVE_NON_PARTICIPANT_UPDATE_VOTES.to_string(),
                    vec![],
                    NearToken::from_yoctonear(0),
                    Gas::from_tgas(self.config.remove_non_participant_update_votes_tera_gas),
                )
                .detach();
            // Spawn a promise to drop votes cast by non-participants.
            Promise::new(env::current_account_id())
                .function_call(
                    method_names::CLEAN_TEE_STATUS.to_string(),
                    vec![],
                    NearToken::from_yoctonear(0),
                    Gas::from_tgas(self.config.clean_tee_status_tera_gas),
                )
                .detach();
```

**File:** crates/contract/src/lib.rs (L1527-1552)
```rust
    pub fn vote_remove_os_measurement(
        &mut self,
        measurement: ContractExpectedMeasurements,
    ) -> Result<(), Error> {
        log!(
            "vote_remove_os_measurement: signer={}, measurement={:?}",
            env::signer_account_id(),
            measurement,
        );
        self.voter_or_panic();

        let threshold_parameters = self.protocol_state.threshold_parameters_or_panic();

        let participant = AuthenticatedParticipantId::new(threshold_parameters.participants())?;
        let action = MeasurementVoteAction::Remove(measurement.clone());
        let votes = self.tee_state.vote_measurement(action, &participant);

        // Removal requires ALL participants to vote
        let total_participants = threshold_parameters.participants().len() as u64;
        if votes >= total_participants {
            let removed = self.tee_state.remove_measurement(&measurement);
            log!("OS measurement remove result: {}", removed);
        }

        Ok(())
    }
```

**File:** crates/contract/src/tee/measurements.rs (L58-66)
```rust
    fn count_votes(&self, action: &MeasurementVoteAction) -> u64 {
        u64::try_from(
            self.vote_by_account
                .values()
                .filter(|a| *a == action)
                .count(),
        )
        .expect("participant count should not overflow u64")
    }
```

**File:** crates/contract/src/tee/measurements.rs (L73-86)
```rust
    /// Returns a new `MeasurementVotes` containing only votes from current participants.
    pub fn get_remaining_votes(&self, participants: &Participants) -> Self {
        let remaining = self
            .vote_by_account
            .iter()
            .filter(|(participant_id, _)| {
                participants.is_participant_given_participant_id(&participant_id.get())
            })
            .map(|(participant_id, vote)| (participant_id.clone(), vote.clone()))
            .collect();
        MeasurementVotes {
            vote_by_account: remaining,
        }
    }
```

**File:** crates/contract/src/tee/tee_state.rs (L396-400)
```rust
    pub fn clean_non_participant_votes(&mut self, participants: &Participants) {
        self.votes = self.votes.get_remaining_votes(participants);
        self.launcher_votes = self.launcher_votes.get_remaining_votes(participants);
        self.measurement_votes = self.measurement_votes.get_remaining_votes(participants);
    }
```
