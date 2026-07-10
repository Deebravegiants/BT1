### Title
`vote_reshared()` Fails to Reset `accept_requests` After Resharing Completes — (File: `crates/contract/src/lib.rs`)

---

### Summary

When `verify_tee()` detects that kicking out expired-attestation participants would break the governance-vs-reconstruction threshold relation, it sets `accept_requests = false` and returns without triggering resharing. If participants subsequently trigger resharing manually via `vote_new_parameters()` and complete it via `vote_reshared()`, the `accept_requests` flag is never reset to `true`. The contract ends up in a valid `Running` state that permanently refuses all user signature requests — a broken execution-flow invariant reachable by a Byzantine participant below the signing threshold.

---

### Finding Description

`verify_tee()` contains two distinct `TeeValidationResult::Partial` branches:

**Branch A (valid threshold — normal path):** sets `accept_requests = true`, then triggers resharing. [1](#0-0) 

**Branch B (broken threshold — manual-intervention path):** sets `accept_requests = false` and returns `Ok(false)` with no resharing triggered. [2](#0-1) 

After Branch B fires, participants can still call `vote_new_parameters()` (which does not check `accept_requests`) to manually trigger resharing, then drive it to completion with `vote_reshared()`. The `vote_reshared()` handler transitions the protocol state to `Running` and spawns several cleanup promises, but **never writes `self.accept_requests = true`**: [3](#0-2) 

The `accept_requests` field therefore remains `false` after a successful resharing, and every subsequent call to `sign()`, `request_app_private_key()`, or `verify_foreign_transaction()` is rejected by the precondition guard: [4](#0-3) 

The only recovery path is for participants to call `verify_tee()` again — an undocumented, non-enforced requirement that is easy to miss in an incident-response scenario.

---

### Impact Explanation

After a successful resharing the contract is in `ProtocolContractState::Running` — the state that is supposed to accept requests — yet `accept_requests = false` causes every user-facing endpoint to panic with `TeeValidationFailed`. All pending yield-resume promises already in flight continue to time out normally, but no new signature, CKD, or foreign-chain verification requests can be submitted. This breaks the core production safety invariant that a `Running` contract accepts requests, without any theft or key-share exposure.

**Allowed impact category matched:** *Medium — contract execution-flow manipulation that breaks production safety/accounting invariants.*

---

### Likelihood Explanation

The broken-threshold branch is reachable whenever the number of participants whose attestations are still valid drops below the governance threshold. A single Byzantine participant (strictly below the signing threshold) can deliberately allow their TEE attestation to expire, pushing the surviving set below the governance threshold and triggering Branch B. Once `accept_requests = false` is set and resharing is completed manually, the contract is silently locked. No privileged access, no key leakage, and no network-level DoS is required — only a participant refusing to renew their attestation.

---

### Recommendation

In `vote_reshared()`, unconditionally set `self.accept_requests = true` when resharing concludes and the state transitions to `Running`:

```rust
if let Some(new_state) = self.protocol_state.vote_reshared(key_event_id)? {
    self.protocol_state = ProtocolContractState::Running(new_state);
    self.accept_requests = true;   // ← add this
    self.recompute_available_foreign_chains();
    // ... cleanup promises ...
}
```

This mirrors the pattern already used in `verify_tee()` Branch A, where `accept_requests = true` is set before resharing is triggered, ensuring the flag is always consistent with the `Running` state.

---

### Proof of Concept

1. Deploy contract with 5 participants, governance threshold 3.
2. Let 3 participants' TEE attestations expire.
3. Any participant calls `verify_tee()` → `TeeValidationResult::Partial` with 2 surviving participants → `validate_governance_against_reconstruction` fails (2 < 3) → `accept_requests = false`, no resharing.
4. The 2 surviving participants call `vote_new_parameters()` with a 2-of-2 proposal (threshold relation now valid for 2 participants).
5. Both participants drive resharing to completion via `start_reshare_instance()` + `vote_reshared()`.
6. Contract is now `ProtocolContractState::Running` with a valid 2-of-2 keyset.
7. Any user calls `sign(...)` → panics with `TeeValidationFailed` because `accept_requests` is still `false`.
8. The MPC network is fully operational off-chain but the on-chain contract silently rejects every request indefinitely.

### Citations

**File:** crates/contract/src/lib.rs (L298-302)
```rust
        // 4. Refuse the request if the contract is not currently accepting requests
        //    (e.g. because TEE validation has failed).
        if !self.accept_requests {
            env::panic_str(&TeeError::TeeValidationFailed.to_string())
        }
```

**File:** crates/contract/src/lib.rs (L1161-1239)
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
        }

        Ok(())
    }
```

**File:** crates/contract/src/lib.rs (L1727-1738)
```rust
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
```

**File:** crates/contract/src/lib.rs (L1741-1767)
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

                Ok(true)
```
