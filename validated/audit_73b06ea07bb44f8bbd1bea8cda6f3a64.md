### Title
Stale Pre-Resharing `vote_code_hash` Votes Count Toward TEE Image Whitelisting Threshold in the Post-Resharing Window — (File: `crates/contract/src/lib.rs`)

### Summary

After a resharing completes, `vote_reshared` transitions the contract to `Running` and spawns `clean_tee_status` as a **detached** (fire-and-forget) promise. Because detached promises execute in a subsequent NEAR receipt, there is a one-block window in which stale `CodeHashesVotes` entries from removed participants are still present in `TeeState`. During this window, a single current participant calling `vote_code_hash` can push the raw vote count to the signing threshold, causing a malicious Docker image hash to be whitelisted with far fewer current-participant votes than the threshold requires.

---

### Finding Description

`vote_code_hash` counts votes by calling `self.tee_state.vote(code_hash, &participant)`, which returns the raw count of all stored votes for that hash — including votes cast by participants who were removed in the just-completed resharing:

```rust
// crates/contract/src/lib.rs  ~line 1418
let votes = self.tee_state.vote(code_hash, &participant);
if votes >= self.threshold()?.value() {
    self.tee_state.whitelist_tee_proposal(code_hash, tee_upgrade_deadline_duration);
}
``` [1](#0-0) 

The cleanup that removes stale votes is `clean_tee_status`, spawned as a detached promise inside `vote_reshared`:

```rust
// crates/contract/src/lib.rs  ~line 1186
Promise::new(env::current_account_id())
    .function_call(method_names::CLEAN_TEE_STATUS.to_string(), ...)
    .detach();
``` [2](#0-1) 

`clean_tee_status` calls `self.tee_state.clean_non_participant_votes(participants)`, which is the only path that removes stale entries from `CodeHashesVotes.proposal_by_account`: [3](#0-2) 

The test `test_clean_non_participant_votes_removes_stale_votes` explicitly documents that before cleanup the stale votes are still counted: [4](#0-3) 

Contrast this with `vote_update`, which was explicitly hardened to filter votes inline and does **not** rely on the cleanup promise:

```rust
// crates/contract/src/lib.rs  ~line 1362
// Filter votes to only count current participants voting for this specific update.
// This ensures correctness even if the cleanup promise in MpcContract::vote_reshared() fails.
let valid_votes_count = running_state.parameters.participants().participants().iter()
    .filter(|(account_id, _, _)| { ... })
    .count();
``` [5](#0-4) 

`vote_code_hash` has no equivalent inline filter.

---

### Impact Explanation

A malicious Docker image hash can be whitelisted with only **1** current-participant vote instead of the required threshold `T`. Once whitelisted, nodes running the malicious image pass `verify_tee` and `submit_participant_info` checks. If operators upgrade to the whitelisted image, those nodes run attacker-controlled code inside the TEE, enabling key-share exfiltration and unauthorized threshold signatures. This breaks the production safety invariant that `T` independent participants must agree before a new node image is trusted.

Impact classification: **Medium** (participant-state manipulation breaking production safety invariants) with potential escalation to **Critical** (key-share compromise) if operators act on the whitelisted hash.

---

### Likelihood Explanation

**Requirements:**
1. `T−1` participants (strictly below threshold, so collusion is not disqualified) vote for a malicious hash `H` before resharing.
2. Those `T−1` participants are removed in a resharing (e.g., via `verify_tee` kicking out nodes with expired attestations, or a governance-driven participant-set change).
3. One current participant submits `vote_code_hash(H)` in the one-block window between resharing completion and `clean_tee_status` execution.

For a typical deployment with `T=6`, this requires 5 colluding participants to be removed — a high bar. For smaller deployments (`T=3`), only 2 colluding participants are needed. The one-block timing window is tight but deterministically exploitable by an attacker who monitors the chain and pre-signs the `vote_code_hash` transaction.

---

### Recommendation

Apply the same inline-filtering defense already used in `vote_update`: when counting votes in `vote_code_hash`, filter `CodeHashesVotes.proposal_by_account` to only count entries whose `AuthenticatedParticipantId` is still in the current participant set, rather than relying on the detached cleanup promise. Alternatively, expose a `count_for_participants` method on `CodeHashesVotes` analogous to the `count_for` predicate already used in `TeeVerifierVotes.vote`: [6](#0-5) 

The same fix should be applied to `vote_add_launcher_hash`, `vote_remove_launcher_hash`, and `vote_remove_os_measurement`, all of which use raw vote counts from `TeeState` without inline participant filtering.

---

### Proof of Concept

Setup: `N=5`, `T=3`.

1. Participants `P1`, `P2` call `vote_code_hash(malicious_hash)` — 2 votes stored, below threshold 3.
2. A governance vote removes `P1` and `P2` from the participant set; resharing completes via `vote_reshared`. Contract transitions to `Running({P3,P4,P5})`. `clean_tee_status` is spawned as a detached promise (executes next block).
3. In the same block, `P3` calls `vote_code_hash(malicious_hash)`. Inside `TeeState::vote`, `CodeHashesVotes` counts all stored entries for `malicious_hash`: `P1`'s vote + `P2`'s vote + `P3`'s vote = **3 = threshold**. `whitelist_tee_proposal` executes.
4. `malicious_hash` is now in `allowed_docker_image_hashes`. When `clean_tee_status` runs in the next block, it removes `P1`/`P2`'s vote entries — but the hash is already whitelisted and `whitelist_tee_proposal` is not reversed.
5. A node running the malicious image calls `submit_participant_info` with a valid attestation for `malicious_hash`; `verify_tee` accepts it. [7](#0-6) [8](#0-7)

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

**File:** crates/contract/src/lib.rs (L1417-1428)
```rust
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
```

**File:** crates/contract/src/lib.rs (L1807-1818)
```rust
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

**File:** crates/contract/src/tee/tee_state.rs (L305-316)
```rust
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
```

**File:** crates/contract/src/tee/tee_state.rs (L1496-1545)
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
    }
```

**File:** crates/contract/src/tee/verifier_votes.rs (L74-77)
```rust
        let count_usize = {
            let voter_set = self.pending.vote(participant, proposal_hash);
            voter_set.count_for(|p| participants.is_participant_given_participant_id(&p.get()))
        };
```
