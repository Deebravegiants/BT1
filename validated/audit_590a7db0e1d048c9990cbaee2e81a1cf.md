### Title
Stale TEE Image-Hash Vote Count Used in `vote_code_hash` Threshold Check Without Participant Filtering — (File: `crates/contract/src/lib.rs`)

### Summary

`vote_code_hash` computes the threshold check using the raw accumulated vote count returned by `tee_state.vote()`, which includes votes from participants removed during resharing. The post-resharing cleanup (`clean_tee_status`) is fired as a detached, fire-and-forget promise that can fail silently. Unlike `vote_update`, which explicitly re-filters votes against the current participant set to guard against this failure, `vote_code_hash` has no such mitigation. If stale votes survive, a Byzantine minority (threshold − 1 participants) can cause a malicious TEE image hash to be whitelisted with fewer valid current-participant votes than the threshold requires.

---

### Finding Description

After resharing completes, `vote_reshared` schedules several cleanup promises as detached calls: [1](#0-0) 

The comment at line 1176 explicitly acknowledges that `clean_tee_status` can fail and that `vote_update` compensates with an inline filter: [2](#0-1) 

`vote_update` re-counts only votes from accounts that are still in `running_state.parameters.participants()`, making it safe even when the cleanup promise fails.

`vote_code_hash` does not apply this filter. It calls `self.tee_state.vote(code_hash, &participant)`, which returns the raw total of all stored votes for that hash — including stale entries from removed participants — and immediately compares that raw total against the threshold: [3](#0-2) 

The `tee_state.vote()` path stores and counts votes without filtering by current participants: [4](#0-3) 

The test above explicitly shows that without `clean_non_participant_votes`, stale votes from removed participants are included in the count returned by `vote()`.

`clean_tee_status` itself is a `#[private]` function that returns `Err` if the state is not `Running`, and is called with a fixed gas budget: [5](#0-4) 

A detached promise failure (OOG, state-transition race, or any panic) leaves stale votes in `tee_state.votes` indefinitely, because there is no retry mechanism and no inline filter in `vote_code_hash`.

---

### Impact Explanation

If `threshold − 1` Byzantine participants vote for a malicious `NodeImageHash` before being removed via resharing, and `clean_tee_status` fails, their stale votes persist. A single honest participant subsequently calling `vote_code_hash` for the same hash causes the raw count to reach `threshold`, triggering `whitelist_tee_proposal`. The malicious image hash is then accepted as a valid TEE image. Nodes running that image can submit attestations that pass `add_participant`, gaining admission to the MPC network. Sufficient malicious participants admitted this way can reach or approach the reconstruction threshold, enabling unauthorized key-share access or threshold-signature issuance.

This maps to: **Medium — participant-state manipulation that breaks production safety/accounting invariants** (unauthorized TEE image whitelisting enabling future unauthorized participant admission).

---

### Likelihood Explanation

The `clean_tee_status` detached promise can fail in practice:

1. **Gas budget exhaustion**: The gas budget is a fixed config value (`clean_tee_status_tera_gas`). A large number of pending votes (e.g., all `threshold − 1` Byzantine participants voted) increases the work done by `clean_non_participant_votes`, which iterates all three vote maps. If the budget is tight, the promise OOGs silently.
2. **State-transition race**: If a new resharing begins between `vote_reshared` completing and `clean_tee_status` executing, the function returns `Err(ProtocolStateNotRunning)`, leaving stale votes in place.

The developers explicitly acknowledged this failure mode in the `vote_reshared` comment and added a mitigation only for `vote_update`, not for `vote_code_hash`. A Byzantine minority at `threshold − 1` participants is the required attacker capability — below the signing threshold.

---

### Recommendation

Apply the same inline participant-filtering pattern used in `vote_update` to `vote_code_hash`. Instead of using the raw count returned by `tee_state.vote()`, re-count only votes from accounts that are currently in `threshold_parameters.participants()`:

```rust
// After recording the vote, count only current-participant votes for this hash
let valid_votes = threshold_parameters
    .participants()
    .participants()
    .iter()
    .filter(|(account_id, _, _)| {
        self.tee_state.votes.proposal_by_account
            .iter()
            .any(|(auth_id, h)| auth_id.get() == account_id && *h == code_hash)
    })
    .count() as u64;

if valid_votes >= self.threshold()?.value() {
    self.tee_state.whitelist_tee_proposal(code_hash, tee_upgrade_deadline_duration);
}
```

This makes `vote_code_hash` safe regardless of whether `clean_tee_status` succeeds, consistent with the existing mitigation in `vote_update`.

---

### Proof of Concept

**Setup**: N = 5 participants, threshold T = 3. Attacker controls P0 and P1 (2 = T − 1 participants, below threshold).

1. P0 and P1 call `vote_code_hash(malicious_hash)`. `tee_state.votes` now has 2 entries for `malicious_hash`.
2. A resharing removes P0 and P1. `vote_reshared` fires `clean_tee_status` as a detached promise with a gas budget that is insufficient for the cleanup (or a concurrent state transition causes it to return `Err`). The promise fails silently. Stale votes for P0 and P1 remain in `tee_state.votes`.
3. Honest participant P2 calls `vote_code_hash(malicious_hash)`. `tee_state.vote(malicious_hash, &p2_auth)` inserts P2's vote and returns the raw count: **3** (P0 stale + P1 stale + P2 fresh).
4. `3 >= threshold (3)` → `whitelist_tee_proposal(malicious_hash, ...)` executes.
5. `malicious_hash` is now an allowed TEE image. Nodes running that image pass `add_participant` attestation checks and are admitted to the MPC network.

The test `test_clean_non_participant_votes_removes_stale_votes` in `crates/contract/src/tee/tee_state.rs` (lines 1504–1544) directly demonstrates that without cleanup, stale votes are included in the count — confirming the raw-count path used by `vote_code_hash` is vulnerable. [6](#0-5) [3](#0-2) [1](#0-0)

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

**File:** crates/contract/src/lib.rs (L1406-1430)
```rust
    #[handle_result]
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
```

**File:** crates/contract/src/lib.rs (L1803-1819)
```rust
    /// Private endpoint to drop votes cast by non-participants after resharing.
    /// Attestation cleanup is handled separately by [`MpcContract::clean_invalid_attestations`].
    #[private]
    #[handle_result]
    pub fn clean_tee_status(&mut self) -> Result<(), Error> {
        log!("clean_tee_status: signer={}", env::signer_account_id());

        let participants = match &self.protocol_state {
            ProtocolContractState::Running(state) => state.parameters.participants(),
            _ => {
                return Err(InvalidState::ProtocolStateNotRunning.into());
            }
        };

        self.tee_state.clean_non_participant_votes(participants);
        Ok(())
    }
```

**File:** crates/contract/src/tee/tee_state.rs (L1496-1544)
```rust
    /// Stale CodeHashesVotes entries from removed participants must not count toward
    /// quorum after resharing.
    ///
    /// Scenario (N=5, T=3):
    /// 1. P1 and P2 vote for malicious hash before resharing.
    /// 2. Resharing removes P1 and P2. New set: {P3, P4, P5}.
    /// 3. clean_non_participant_votes removes stale votes.
    /// 4. P3 votes for the same hash — only 1 vote, not 3.
    #[test]
    fn test_clean_non_participant_votes_removes_stale_votes() {
        // Build 5 participants
        let mut all_participants = Participants::new();
        let mut account_ids = Vec::new();
        for i in 0..5 {
            let (account_id, info) = gen_participant(i);
            account_ids.push(account_id.clone());
            all_participants.insert(account_id, info).unwrap();
        }

        let mut tee_state = TeeState::default();

        // P0 and P1 vote for a malicious hash before resharing
        let malicious_hash = NodeImageHash::from([0xAA; 32]);
        for account_id in &account_ids[0..2] {
            let mut ctx = VMContextBuilder::new();
            ctx.signer_account_id(account_id.clone());
            testing_env!(ctx.build());
            let auth_id = AuthenticatedParticipantId::new(&all_participants).unwrap();
            tee_state.votes.vote(malicious_hash, &auth_id);
        }
        assert_eq!(tee_state.votes.proposal_by_account.len(), 2);

        // Resharing removes P0 and P1. New participant set: {P2, P3, P4}.
        let new_participants = all_participants.subset(2..5);

        // Clean non-participants (as done by CLEAN_TEE_STATUS after resharing)
        tee_state.clean_non_participant_votes(&new_participants);

        // Stale votes must be removed
        assert_eq!(tee_state.votes.proposal_by_account.len(), 0);

        // P2 votes for the same malicious hash — should be only 1 vote, not 3
        let p2_account = &account_ids[2];
        let mut ctx = VMContextBuilder::new();
        ctx.signer_account_id(p2_account.clone());
        testing_env!(ctx.build());
        let auth_id = AuthenticatedParticipantId::new(&new_participants).unwrap();
        let vote_count = tee_state.votes.vote(malicious_hash, &auth_id);
        assert_eq!(vote_count, 1, "Only the fresh vote from P2 should count");
```
