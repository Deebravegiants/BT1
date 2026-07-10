### Title
`accept_requests` Flag Not Reset After Successful Resharing Permanently Blocks Signing - (File: `crates/contract/src/lib.rs`)

### Summary

The `accept_requests` boolean flag, which gates all signing, CKD, and foreign-transaction-verification requests, is set to `false` inside `verify_tee()` when the threshold relation is broken. When operators subsequently trigger a resharing via `vote_new_parameters()` and the resharing completes successfully via `vote_reshared()`, the flag is never reset to `true`. The contract returns to `Running` state with a fully valid new participant set but continues to reject every user request indefinitely.

### Finding Description

`verify_tee()` contains two branches:

**Branch A – `TeeValidationResult::Full`**: sets `accept_requests = true`.

**Branch B – `TeeValidationResult::Partial` with threshold intact**: sets `accept_requests = true`, then triggers an automatic resharing.

**Branch C – `TeeValidationResult::Partial` with threshold broken** (the vulnerable path): [1](#0-0) 

```rust
if let Err(err) = ThresholdParameters::validate_governance_against_reconstruction(...) {
    log!("...This requires manual intervention. We will not accept new signature requests...");
    self.accept_requests = false;
    return Ok(false);
}
```

After this, operators must manually call `vote_new_parameters()` to start a resharing, then each new participant calls `vote_reshared()`. When the final vote crosses the threshold, `vote_reshared()` transitions the contract back to `Running` and spawns several cleanup promises — but it never touches `accept_requests`: [2](#0-1) 

The four assignments to `accept_requests` in the entire contract are:
- `init()` → `true` (initialization)
- `verify_tee()` Full branch → `true`
- `verify_tee()` Partial-threshold-intact branch → `true`
- `verify_tee()` Partial-threshold-broken branch → `false`

`vote_reshared()` is absent from this list. After resharing completes, `accept_requests` remains `false`.

Every user-facing entry point checks this flag and panics: [3](#0-2) 

```rust
if !self.accept_requests {
    env::panic_str(&TeeError::TeeValidationFailed.to_string())
}
```

The same guard appears in `respond()`, `respond_ckd()`, and `respond_verify_foreign_tx()`: [4](#0-3) 

Recovery requires an explicit call to `verify_tee()` after resharing, which is not automatic, not documented as a required post-resharing step, and not obvious to operators.

### Impact Explanation

After a successful resharing that was triggered specifically to resolve a TEE validation failure, the contract is permanently stuck refusing all signing requests, CKD requests, and foreign-transaction verifications. This is a complete, indefinite freeze of the MPC network's signing capability — matching the **Medium** allowed impact: *"request-lifecycle or contract execution-flow manipulation that breaks production safety/accounting invariants."*

### Likelihood Explanation

TEE attestation certificates have finite validity periods. As certificates expire or when a new MPC Docker image is whitelisted (invalidating old attestations), `verify_tee()` will naturally reach Branch C if enough participants have stale attestations. This is an expected operational event, not a contrived scenario. The resharing path is the documented recovery mechanism, making the missing flag reset a realistic production hazard.

### Recommendation

In `vote_reshared()`, reset `accept_requests = true` when resharing concludes successfully:

```rust
if let Some(new_state) = self.protocol_state.vote_reshared(key_event_id)? {
    self.protocol_state = new_state;
+   self.accept_requests = true;  // resharing with valid participants completed
    self.recompute_available_foreign_chains();
    // ... cleanup promises ...
}
```

Optionally, do the same in `vote_cancel_resharing()` if the reverted Running state is known to have had valid participants, or require a `verify_tee()` call explicitly and document it as a mandatory post-resharing step.

### Proof of Concept

1. Network is Running with N participants; some participants' TEE certificates expire.
2. Any participant calls `verify_tee()`. `reverify_and_cleanup_participants` returns `Partial` with fewer than threshold valid participants.
3. `accept_requests` is set to `false`. All `sign()`, `request_app_private_key()`, and `verify_foreign_transaction()` calls now panic with `TeeValidationFailed`.
4. Operators call `vote_new_parameters()` with a new valid participant set → contract enters `Resharing`.
5. New participants call `vote_reshared()` until threshold is reached → contract transitions back to `Running` with a fully valid participant set.
6. `accept_requests` is still `false`. Every `sign()` call continues to panic with `TeeValidationFailed` despite the contract being in a healthy Running state with valid participants.
7. The MPC network is effectively frozen for all user-facing operations until an operator discovers they must call `verify_tee()` again.

### Citations

**File:** crates/contract/src/lib.rs (L299-302)
```rust
        //    (e.g. because TEE validation has failed).
        if !self.accept_requests {
            env::panic_str(&TeeError::TeeValidationFailed.to_string())
        }
```

**File:** crates/contract/src/lib.rs (L579-581)
```rust
        if !self.accept_requests {
            return Err(TeeError::TeeValidationFailed.into());
        }
```

**File:** crates/contract/src/lib.rs (L1170-1236)
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
