### Title
Stale Votes from Removed Participants Count Toward Threshold in TEE Hash Governance — (`File: crates/contract/src/lib.rs`)

---

### Summary

The TEE governance voting functions (`vote_code_hash`, `vote_add_launcher_hash`, `vote_remove_launcher_hash`, `vote_add_os_measurement`, `vote_remove_os_measurement`) use raw, unfiltered vote counts that include votes from participants who have since been removed via resharing. Unlike `vote_update`, which explicitly filters votes to only count current participants as a defense-in-depth measure, these functions operate on stale state. This allows a removed participant's prior vote to count toward the governance threshold, enabling a code hash to be whitelisted with fewer current-participant votes than the threshold requires.

---

### Finding Description

After a resharing completes, `vote_reshared` transitions the contract to `Running` and spawns several detached cleanup promises, including `CLEAN_TEE_STATUS`, which calls `clean_non_participant_votes` to remove stale votes from the `CodeHashesVotes`, `LauncherHashVotes`, and `MeasurementVotes` maps. [1](#0-0) 

Because these cleanup promises are **detached** (fire-and-forget), they execute in a separate NEAR transaction after the resharing transaction. This creates a window — and a permanent gap if the promise fails — where stale votes from removed participants remain in the vote maps.

The `vote_code_hash` function reads the raw vote count returned by `self.tee_state.vote(...)` and compares it directly against the threshold: [2](#0-1) 

The `tee_state.vote()` call returns the total count of all stored votes for the hash, including those from participants no longer in the active set: [3](#0-2) 

By contrast, `vote_update` explicitly filters votes to only count current participants, with a comment acknowledging exactly this failure mode: [4](#0-3) 

The same unfiltered pattern applies to `vote_add_launcher_hash`, `vote_remove_launcher_hash`, `vote_add_os_measurement`, and `vote_remove_os_measurement`. [5](#0-4) [6](#0-5) 

---

### Impact Explanation

An adversary can cause a TEE image hash (or launcher/OS measurement) to be whitelisted with fewer current-participant votes than the governance threshold requires. Concretely:

- If threshold is T and a removed participant had already voted for hash X, only T−1 current participants need to vote for X to whitelist it.
- A whitelisted malicious image hash allows nodes running that image to submit valid TEE attestations, enabling them to be proposed as new participants in a future resharing.

This breaks the production safety invariant that threshold votes from the **current** participant set are required for any governance action affecting the TEE trust boundary. It maps to the **Medium** allowed impact: *participant-state or contract execution-flow manipulation that breaks production safety/accounting invariants*.

---

### Likelihood Explanation

Two realistic triggering conditions exist:

1. **Race window (always present):** Between the `vote_reshared` transaction completing and the `CLEAN_TEE_STATUS` detached promise executing, stale votes are live. Any `vote_code_hash` call in this window uses the stale count.

2. **Cleanup promise failure:** If `CLEAN_TEE_STATUS` runs out of gas or panics, stale votes persist indefinitely. The function is `#[private]` and can only be re-triggered by another resharing.

A removed participant who voted for a hash before resharing, combined with a single new participant voting for the same hash in the window above, is sufficient to cross the threshold. No threshold-level collusion is required — only one removed participant's prior vote plus one new participant's vote.

---

### Recommendation

Apply the same defense-in-depth filter used in `vote_update` to all TEE governance voting functions. After recording the caller's vote, recount only votes belonging to the current active participant set before comparing against the threshold:

```rust
// In vote_code_hash (and analogously in vote_add_launcher_hash, etc.)
let threshold_parameters = self.protocol_state.threshold_parameters_or_panic();
let participant = AuthenticatedParticipantId::new(threshold_parameters.participants())?;
self.tee_state.vote(code_hash, &participant); // record vote

// Filter: only count votes from current participants
let valid_votes = threshold_parameters
    .participants()
    .participants()
    .iter()
    .filter(|(account_id, _, _)| {
        self.tee_state.votes.proposal_by_account
            .get(*account_id)
            .is_some_and(|h| *h == code_hash)
    })
    .count() as u64;

if valid_votes >= self.threshold()?.value() {
    self.tee_state.whitelist_tee_proposal(code_hash, tee_upgrade_deadline_duration);
}
```

---

### Proof of Concept

1. Contract is Running with participants {A, B, C, D, E}, threshold = 3.
2. Participant A calls `vote_code_hash(malicious_hash)`. Vote map: `{A: malicious_hash}`, count = 1.
3. Participants B, C, D, E call `vote_new_parameters` to remove A; resharing completes. New set: {B, C, D, E}.
4. `CLEAN_TEE_STATUS` detached promise is queued but not yet executed (or fails).
5. Participant B calls `vote_code_hash(malicious_hash)`. Vote map: `{A: malicious_hash, B: malicious_hash}`, raw count = 2.
6. Participant C calls `vote_code_hash(malicious_hash)`. Raw count = 3 ≥ threshold(3). `whitelist_tee_proposal` executes.
7. `malicious_hash` is now whitelisted with only 2 current-participant votes (B and C), not the required 3. [2](#0-1) [7](#0-6)

### Citations

**File:** crates/contract/src/lib.rs (L1185-1193)
```rust
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

**File:** crates/contract/src/lib.rs (L1362-1378)
```rust
        // This ensures correctness even if the cleanup promise in MpcContract::vote_reshared() fails.
        let valid_votes_count = running_state
            .parameters
            .participants()
            .participants()
            .iter()
            .filter(|(account_id, _, _)| {
                self.proposed_updates
                    .vote_by_participant
                    .get(account_id)
                    .is_some_and(|voted_id| *voted_id == id)
            })
            .count();

        // Not enough votes from current participants, wait for more.
        if (valid_votes_count as u64) < threshold.value() {
            return Ok(false);
```

**File:** crates/contract/src/lib.rs (L1407-1431)
```rust
    pub fn vote_code_hash(&mut self, code_hash: NodeImageHash) -> Result<(), Error> {
        log!(
            "vote_code_hash: signer={}, code_hash={:?}",
            env::signer_account_id(),
            code_hash,
        );
        self.voter_or_panic();

        let threshold_parameters = self.protocol_state.threshold_parameters_or_panic();

        let participant = AuthenticatedParticipantId::new(threshold_parameters.participants())?;
        let votes = self.tee_state.vote(code_hash, &participant);

        let tee_upgrade_deadline_duration =
            Duration::from_secs(self.config.tee_upgrade_deadline_duration_seconds);

        // If the vote threshold is met and the new Docker hash is allowed by the TEE's RTMR3,
        // update the state
        if votes >= self.threshold()?.value() {
            self.tee_state
                .whitelist_tee_proposal(code_hash, tee_upgrade_deadline_duration);
        }

        Ok(())
    }
```

**File:** crates/contract/src/lib.rs (L1437-1465)
```rust
    pub fn vote_add_launcher_hash(
        &mut self,
        launcher_hash: LauncherImageHash,
    ) -> Result<(), Error> {
        log!(
            "vote_add_launcher_hash: signer={}, launcher_hash={:?}",
            env::signer_account_id(),
            launcher_hash,
        );
        self.voter_or_panic();

        let threshold_parameters = self.protocol_state.threshold_parameters_or_panic();

        let participant = AuthenticatedParticipantId::new(threshold_parameters.participants())?;
        let action = LauncherVoteAction::Add(launcher_hash);
        let votes = self.tee_state.vote_launcher(action, &participant);

        let tee_upgrade_deadline_duration =
            Duration::from_secs(self.config.tee_upgrade_deadline_duration_seconds);

        if votes >= self.threshold()?.value() {
            let added = self
                .tee_state
                .add_launcher_image(launcher_hash, tee_upgrade_deadline_duration);
            log!("launcher hash add result: {}", added);
        }

        Ok(())
    }
```

**File:** crates/contract/src/lib.rs (L1497-1552)
```rust
    /// Vote to add a new OS measurement set to the allowed list. Requires threshold votes.
    #[handle_result]
    pub fn vote_add_os_measurement(
        &mut self,
        measurement: ContractExpectedMeasurements,
    ) -> Result<(), Error> {
        log!(
            "vote_add_os_measurement: signer={}, measurement={:?}",
            env::signer_account_id(),
            measurement,
        );
        self.voter_or_panic();

        let threshold_parameters = self.protocol_state.threshold_parameters_or_panic();

        let participant = AuthenticatedParticipantId::new(threshold_parameters.participants())?;
        let action = MeasurementVoteAction::Add(measurement.clone());
        let votes = self.tee_state.vote_measurement(action, &participant);

        if votes >= self.threshold()?.value() {
            let added = self.tee_state.add_measurement(measurement);
            log!("OS measurement add result: {}", added);
        }

        Ok(())
    }

    /// Vote to remove an OS measurement set from the allowed list. Requires ALL participants
    /// to vote for removal.
    #[handle_result]
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

**File:** crates/contract/src/tee/tee_state.rs (L279-285)
```rust
    pub fn vote(
        &mut self,
        code_hash: NodeImageHash,
        participant: &AuthenticatedParticipantId,
    ) -> u64 {
        self.votes.vote(code_hash, participant)
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
