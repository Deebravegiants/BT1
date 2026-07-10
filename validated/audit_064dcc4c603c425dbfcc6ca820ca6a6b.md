### Title
Stale TEE-image-hash votes from removed participants count toward whitelisting threshold — (`crates/contract/src/lib.rs`)

### Summary

After a resharing that changes the participant set, votes cast by removed participants for TEE image hashes, launcher hashes, and OS measurements are not synchronously cleared. Cleanup is deferred to detached promises that can fail. Unlike `vote_update`, which explicitly re-filters votes against the current participant set to guard against this failure, `vote_code_hash`, `vote_add_launcher_hash`, and `vote_add_os_measurement` count all stored votes including stale ones from removed participants. A single current participant voting for the same proposal as removed participants can push the combined tally over the governance threshold, whitelisting a TEE image without the required number of current-participant approvals.

### Finding Description

When resharing completes in `vote_reshared`, the contract spawns several **detached** cleanup promises: [1](#0-0) 

One of these (`CLEAN_TEE_STATUS`) eventually calls `TeeState::clean_non_participant_votes`, which removes stale votes: [2](#0-1) 

Because this cleanup is **asynchronous and detached**, it can fail (e.g., insufficient gas allocation). The developers explicitly acknowledged this risk in `vote_update`, which re-filters votes against the live participant set before counting: [3](#0-2) 

However, `vote_code_hash` applies no such filter — it counts the raw total returned by `TeeState::vote`: [4](#0-3) 

The same pattern appears in `vote_add_launcher_hash`: [5](#0-4) 

And `vote_add_os_measurement` follows the same structure. In all three cases the raw vote count — which may include votes from participants removed during resharing — is compared directly against the current threshold.

**Step-by-step attack path:**

1. Before resharing, one or more participants (honest or malicious) vote for a specific `code_hash` / `launcher_hash` / `measurement`. The count stays below the old threshold, so nothing is whitelisted.
2. A resharing occurs that removes those participants from the active set.
3. The `CLEAN_TEE_STATUS` detached promise fails (out-of-gas, or the attacker acts within the single-block window before cleanup executes).
4. Stale votes from the removed participants remain in `TeeState::votes` / `launcher_votes` / `measurement_votes`.
5. A single current participant calls `vote_code_hash` for the same hash. The raw tally is now `(stale votes) + 1`.
6. If `(stale votes) + 1 >= new_threshold`, `whitelist_tee_proposal` fires, whitelisting the image without the required number of current-participant approvals.

### Impact Explanation

Whitelisting a TEE image hash is the gate that determines which node images are accepted for attestation. An image whitelisted with fewer current-participant votes than the governance threshold requires breaks the core invariant that threshold-many active participants must agree before any new image is trusted. A node running a malicious or compromised image that was improperly whitelisted can submit a passing attestation, be voted into the participant set, and participate in threshold signing — ultimately enabling unauthorized signature issuance. This maps to the **Medium** allowed impact: participant-state and contract execution-flow manipulation that breaks production safety/accounting invariants.

### Likelihood Explanation

The developers explicitly documented the cleanup-failure risk in the `vote_update` comment and added a compensating filter there. The same risk applies to the TEE-hash voting paths but no compensating filter was added. The attack window exists in every resharing: the cleanup promise runs one block after resharing completes, and any participant can call `vote_code_hash` in that same block. Additionally, if the gas budget for `CLEAN_TEE_STATUS` is ever insufficient, stale votes persist indefinitely. No privileged access or threshold collusion is required beyond the pre-resharing votes already cast by participants who were subsequently removed.

### Recommendation

Apply the same participant-filtering pattern used in `vote_update` to `vote_code_hash`, `vote_add_launcher_hash`, and `vote_add_os_measurement`. After recording the new vote, re-count only votes whose voter is still a member of the current participant set before comparing against the threshold:

```rust
// After self.tee_state.vote(code_hash, &participant):
let valid_votes = count_votes_for_current_participants(
    &self.tee_state.votes,
    code_hash,
    threshold_parameters.participants(),
);
if valid_votes >= self.threshold()?.value() {
    self.tee_state.whitelist_tee_proposal(...);
}
```

This makes correctness independent of whether the detached cleanup promise succeeds, mirroring the explicit design choice already made for `vote_update`.

### Proof of Concept

```
Epoch N  (participants: {A, B, C}, threshold: 2)
  A calls vote_code_hash(HASH_X)  → stored votes for HASH_X: {A}  (count=1 < 2, no whitelist)

Resharing: participant set changes to {B, C, D}, threshold: 2
  CLEAN_TEE_STATUS promise fails → A's vote for HASH_X remains in TeeState::votes

Epoch N+1 (participants: {B, C, D}, threshold: 2)
  B calls vote_code_hash(HASH_X)
    → TeeState::vote returns raw count = 2  ({A (stale), B})
    → 2 >= threshold(2)  → whitelist_tee_proposal(HASH_X) fires

Result: HASH_X whitelisted with only 1 current-participant vote instead of 2.
``` [6](#0-5) [7](#0-6) [8](#0-7)

### Citations

**File:** crates/contract/src/lib.rs (L1175-1193)
```rust
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

**File:** crates/contract/src/lib.rs (L1361-1378)
```rust
        // Filter votes to only count current participants voting for this specific update.
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

**File:** crates/contract/src/lib.rs (L1452-1465)
```rust
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
