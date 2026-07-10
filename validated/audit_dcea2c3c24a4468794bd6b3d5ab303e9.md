### Title
Stale TEE Governance Votes from Removed Participants Persist After Resharing, Enabling Threshold Bypass — (`crates/contract/src/lib.rs`)

### Summary

After a resharing event removes participants, their previously cast TEE governance votes (`vote_code_hash`, `vote_add_launcher_hash`, `vote_add_os_measurement`) remain in contract storage if the post-resharing `clean_tee_status` detached promise fails. Unlike `vote_update`, which explicitly filters non-participant votes at counting time, these TEE governance functions count all stored votes — including stale ones from removed participants — toward the threshold. A removed participant's pre-resharing vote can therefore substitute for a missing current-participant vote, causing a TEE image hash to be whitelisted with fewer current-participant votes than the governance threshold requires.

---

### Finding Description

When resharing completes in `vote_reshared`, the contract spawns several detached cleanup promises: [1](#0-0) 

The comment on the `remove_non_participant_update_votes` promise explicitly acknowledges that cleanup can fail and that `vote_update` has a compensating filter: [2](#0-1) 

No equivalent filter exists in `vote_code_hash`, `vote_add_launcher_hash`, or `vote_add_os_measurement`. Each of these functions calls `self.tee_state.vote(...)` (or `vote_launcher`/`vote_measurement`) and compares the raw returned count against the threshold: [3](#0-2) [4](#0-3) 

The returned vote count is the total number of entries stored in `tee_state.votes.proposal_by_account` for that hash — it is **not** filtered to current participants. The project's own unit test documents this exact risk: [5](#0-4) 

The test verifies that `clean_non_participant_votes` removes stale entries and that a fresh vote counts as 1, not 3. But the test does not cover the case where the cleanup promise fails — in which case the stale entries remain and the vote count is inflated.

The `clean_tee_status` promise is detached with a fixed gas budget (`self.config.clean_tee_status_tera_gas`). If that budget is exhausted (e.g., with a large participant set or storage pressure), the promise silently fails and stale votes persist indefinitely. There is no retry mechanism and no on-chain record of the failure.

---

### Impact Explanation

If stale votes persist, a removed participant's pre-resharing vote for a TEE image hash counts toward the post-resharing threshold. This means a malicious TEE image hash can be whitelisted with fewer current-participant votes than the governance threshold requires. A node running that image can then submit a valid attestation, pass `is_caller_an_attested_participant`, and become an active participant in signing and key resharing — a direct participant/attestation authorization bypass. [6](#0-5) 

**Impact class:** Medium — breaks the production safety invariant that threshold votes from *current* participants are required to whitelist TEE image hashes, without requiring network-level DoS or operator misconfiguration.

---

### Likelihood Explanation

The attack requires:
1. A participant who is about to be removed casts a vote for a target code/launcher hash before resharing.
2. The `clean_tee_status` detached promise fails (gas budget too low for the current participant-set size, or storage contention).
3. Enough current participants vote for the same hash post-resharing to reach `threshold - 1` (the stale vote supplies the final count).

Step 1 is trivially achievable by any participant who learns they will be removed. Step 2 is realistic: the gas budget is a static config value and is not adjusted as the participant set grows. Step 3 requires only `threshold - 1` colluding current participants, which is below the signing threshold and therefore not disqualified by the collusion criterion.

---

### Recommendation

1. **Apply the same filter used by `vote_update` to all TEE governance vote-counting paths.** Before comparing the vote count against the threshold, filter `tee_state.votes.proposal_by_account` to only entries whose participant ID belongs to the current participant set.

2. **Make `clean_tee_status` bounded and retriable**, similar to `clean_invalid_attestations` which accepts a `max_scan` parameter, so that cleanup can be retried if it runs out of gas.

3. **Add an explicit invariant check** in `vote_code_hash` / `vote_add_launcher_hash` / `vote_add_os_measurement` that the signer is a current participant (analogous to `assert_caller_is_attested_participant_and_protocol_active`) before recording or counting the vote.

---

### Proof of Concept

**Setup:** 5 participants P1–P5, governance threshold = 4.

1. **Before resharing:** P1 calls `vote_code_hash(malicious_hash)`. One vote stored; threshold not reached.
2. **Resharing:** P1 is removed; P6 is added. Contract transitions to Running with participants {P2, P3, P4, P5, P6}, threshold = 4.
3. **Cleanup fails:** `clean_tee_status` promise runs out of gas. P1's vote entry remains in `tee_state.votes.proposal_by_account`.
4. **Post-resharing:** P2, P3, P4 each call `vote_code_hash(malicious_hash)`.
5. **Threshold check in `vote_code_hash`:** `self.tee_state.vote(malicious_hash, &participant)` returns 4 (P1 stale + P2 + P3 + P4). `4 >= threshold (4)` → `whitelist_tee_proposal` is called.
6. **Result:** `malicious_hash` is whitelisted with only 3 current-participant votes (P2, P3, P4) instead of the required 4. A node running the malicious image can now pass `submit_participant_info` attestation checks and become an active MPC participant. [7](#0-6) [8](#0-7)

### Citations

**File:** crates/contract/src/lib.rs (L1175-1184)
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
```

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

**File:** crates/contract/src/tee/tee_state.rs (L466-498)
```rust
    /// whose TLS key matches an attested node belonging to the caller account.
    ///
    /// Handles multiple participants per account and supports legacy mock nodes.
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
