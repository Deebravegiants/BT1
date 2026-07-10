### Title
Stale `tee_state.votes` from Removed Participants Count Toward Node-Image-Hash Approval Threshold After Resharing - (File: `crates/contract/src/tee/tee_state.rs`, `crates/contract/src/lib.rs`)

---

### Summary

When resharing completes and participants are removed, their prior votes in `tee_state.votes` (the `CodeHashesVotes` map used to approve MPC docker image hashes) are **not atomically cleared**. Cleanup is delegated to a detached, fire-and-forget promise (`CLEAN_TEE_STATUS`). If that promise fails, stale votes from removed participants persist and are counted by `CodeHashesVotes::vote` without any current-participant filter, allowing a malicious image hash to reach the approval threshold with fewer legitimate post-resharing votes than required.

---

### Finding Description

**Root cause — stale votes not reset atomically on participant removal:**

In `vote_reshared`, once resharing concludes, the contract transitions to the new `RunningContractState` and then spawns six independent detached cleanup promises: [1](#0-0) 

The promise responsible for clearing stale image-hash votes is: [2](#0-1) 

`clean_tee_status` is marked `#[private]` — only the contract itself (predecessor == current account) can call it: [3](#0-2) 

If this detached promise runs out of gas (controlled by `self.config.clean_tee_status_tera_gas`) or fails for any runtime reason, **there is no public participant-callable fallback** to retry it (unlike `remove_non_participant_update_votes`, which explicitly allows participants to call it directly).

**The vote-counting function does not filter for current participants:**

The `CodeHashesVotes::vote` function returns a raw count of all entries in `proposal_by_account`, regardless of whether those voters are still in the active participant set. The test that documents this exact hazard states: [4](#0-3) 

The comment `"Only the fresh vote from P2 should count"` and the assertion `assert_eq!(vote_count, 1)` confirm that **without cleanup, the count would be 3** (P0 + P1 stale + P2 fresh), not 1. The test only passes because `clean_non_participant_votes` is called first — but in production this cleanup is not atomic.

**Contrast with the safe pattern used elsewhere:**

`vote_update` explicitly re-filters votes against the current participant set inline, so stale votes never count even if cleanup fails: [5](#0-4) 

`add_domains_votes` is filtered atomically inside `RunningContractState::new`: [6](#0-5) 

`tee_state.votes` has no equivalent inline filter.

---

### Impact Explanation

The `tee_state.votes` map controls which MPC docker image hashes are whitelisted. Approving a malicious image hash allows a node running adversarial code to submit a valid TEE attestation and be admitted to the MPC network. Once admitted, such a node participates in threshold signing rounds and has access to its key share. A malicious image designed to exfiltrate key material or produce biased nonces can undermine the threshold security model.

**Impact class:** Critical — unauthorized access to MPC key shares / bypass of TEE-enforced participant integrity.

---

### Likelihood Explanation

The `CLEAN_TEE_STATUS` promise is allocated gas via `self.config.clean_tee_status_tera_gas`. If the participant set is large or the `proposal_by_account` map is large, the cleanup can exceed the allocated gas and silently fail. Because the promise is detached and `clean_tee_status` is `#[private]`, there is no participant-callable retry path. An adversary who controls T−1 participants (just below the governance threshold) can:

1. Vote for a malicious image hash while still participants.
2. Trigger or wait for a resharing that removes them.
3. Ensure the cleanup promise fails (e.g., by front-running with storage writes that inflate gas cost, or simply relying on a misconfigured gas budget).
4. Cast one additional vote from a remaining participant to cross the threshold.

---

### Recommendation

Apply the same inline-filter pattern used by `vote_update` and `add_domains_votes`:

- In the function that calls `tee_state.votes.vote(...)` and checks the returned count against the threshold, filter the count to only include votes from accounts that are in the current `participants` set before comparing against the threshold.
- Alternatively, make `clean_tee_status` callable by any current participant (not just `#[private]`), matching the access model of `remove_non_participant_update_votes`.

---

### Proof of Concept

```
Pre-condition: N=5 participants, governance threshold T=3.
               Participants: {P0, P1, P2, P3, P4}.

Step 1: P0 and P1 call vote_node_image_hash(malicious_hash).
        tee_state.votes.proposal_by_account = {P0: malicious_hash, P1: malicious_hash}
        count = 2  (< threshold 3, hash not yet approved)

Step 2: Resharing removes P0 and P1. New set: {P2, P3, P4}, threshold 3.
        vote_reshared() transitions state and spawns CLEAN_TEE_STATUS as a detached promise.

Step 3: CLEAN_TEE_STATUS promise fails (out of gas / misconfigured budget).
        tee_state.votes.proposal_by_account still contains {P0: malicious_hash, P1: malicious_hash}.

Step 4: P2 calls vote_node_image_hash(malicious_hash).
        CodeHashesVotes::vote counts P0 + P1 + P2 = 3 votes.
        3 >= threshold 3 → malicious_hash is approved.

Result: A node running the malicious image can now submit a valid TEE attestation,
        be admitted to the MPC network, and participate in threshold signing rounds
        with access to its key share — bypassing the TEE integrity guarantee with
        only 1 legitimate post-resharing vote instead of the required 3.
```

### Citations

**File:** crates/contract/src/lib.rs (L1170-1235)
```rust
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
            // Spawn a bounded sweep over stored attestations to prune invalid / expired entries.
            Promise::new(env::current_account_id())
                .function_call(
                    method_names::CLEAN_INVALID_ATTESTATIONS.to_string(),
                    serde_json::to_vec(&serde_json::json!({
                        "max_scan": RESHARE_CLEAN_INVALID_ATTESTATIONS_MAX_SCAN
                    }))
                    .unwrap(),
                    NearToken::from_yoctonear(0),
                    Gas::from_tgas(self.config.clean_invalid_attestations_tera_gas),
                )
                .detach();
            // Spawn a promise to clean up orphaned node migrations for non-participants
            Promise::new(env::current_account_id())
                .function_call(
                    method_names::CLEANUP_ORPHANED_NODE_MIGRATIONS.to_string(),
                    vec![],
                    NearToken::from_yoctonear(0),
                    Gas::from_tgas(self.config.cleanup_orphaned_node_migrations_tera_gas),
                )
                .detach();
            // Spawn a promise to clean up foreign chain data for non-participants
            Promise::new(env::current_account_id())
                .function_call(
                    method_names::CLEAN_FOREIGN_CHAIN_DATA.to_string(),
                    vec![],
                    NearToken::from_yoctonear(0),
                    Gas::from_tgas(self.config.clean_foreign_chain_data_tera_gas),
                )
                .detach();
            // Spawn a promise to drop verifier-change votes cast by non-participants
            Promise::new(env::current_account_id())
                .function_call(
                    method_names::REMOVE_NON_PARTICIPANT_TEE_VERIFIER_VOTES.to_string(),
                    vec![],
                    NearToken::from_yoctonear(0),
                    Gas::from_tgas(
                        self.config
                            .remove_non_participant_tee_verifier_votes_tera_gas,
                    ),
                )
                .detach();
```

**File:** crates/contract/src/lib.rs (L1361-1374)
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
```

**File:** crates/contract/src/lib.rs (L1805-1818)
```rust
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

**File:** crates/contract/src/state/running.rs (L48-64)
```rust
    pub fn new(
        domains: DomainRegistry,
        keyset: Keyset,
        parameters: ThresholdParameters,
        add_domains_votes: AddDomainsVotes,
    ) -> Self {
        let remaining_add_domain_votes =
            add_domains_votes.get_remaining_votes(parameters.participants());
        RunningContractState {
            domains,
            keyset,
            parameters,
            parameters_votes: ThresholdParametersVotes::default(),
            add_domains_votes: remaining_add_domain_votes,
            previously_cancelled_resharing_epoch_id: None,
        }
    }
```
