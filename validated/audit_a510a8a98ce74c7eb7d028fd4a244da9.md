### Title
`accept_requests` Not Reset on `vote_reshared` Transition — Permanent Signing DoS After Resharing - (File: crates/contract/src/lib.rs)

### Summary
`verify_tee()` can set `accept_requests = false` when fewer than threshold participants have valid TEE attestations. When participants subsequently fix the TEE issue and complete a resharing via `vote_reshared()`, the `accept_requests` flag is never reset to `true`. The contract transitions back to Running state with all signing, CKD, and foreign-chain verification requests permanently blocked until `verify_tee()` is manually called again.

### Finding Description
Both `init()` and `init_running()` set `accept_requests: true` as part of contract initialization. [1](#0-0) [2](#0-1) 

The `verify_tee()` function can set `accept_requests = false` when kicking out participants with invalid attestations would drop the surviving set below the threshold relation — in that case it refuses to reshare, stays Running, and stops accepting requests: [3](#0-2) 

However, `vote_reshared()`, which transitions the contract from Resharing back to Running state, never resets `accept_requests = true`: [4](#0-3) 

The entire `vote_reshared()` transition block spawns cleanup promises but contains no `self.accept_requests = true` assignment: [5](#0-4) 

This is the direct analog of the StakedEXA pattern: `init()` sets up necessary state (`accept_requests = true`), but the "setter" function (`vote_reshared()`) that installs a new Running state does not replicate that initialization step.

Every user-facing request method (`sign`, `request_app_private_key`, `verify_foreign_transaction`) and every node response method (`respond`, `respond_ckd`, `respond_verify_foreign_tx`) gates on `accept_requests`: [6](#0-5) [7](#0-6) 

### Impact Explanation
After `verify_tee()` sets `accept_requests = false` (the "kickout would break threshold" branch), participants can fix the TEE issue by submitting fresh attestations via `submit_participant_info()` and then trigger a resharing via `vote_new_parameters()`. Once the resharing completes via `vote_reshared()`, the contract is in a valid Running state with a corrected participant set, but `accept_requests` remains `false`. All `sign()`, `request_app_private_key()`, and `verify_foreign_transaction()` calls panic with `TeeError::TeeValidationFailed`, and all `respond*` calls return that error. The entire MPC signing capability is frozen — no threshold signatures can be issued or completed — until `verify_tee()` is called again and returns `Full` or a `Partial` with enough survivors.

This matches the **Medium** allowed impact: *"request-lifecycle, participant-state, or contract execution-flow manipulation that breaks production safety/accounting invariants without relying on network-level DoS or operator misconfiguration."*

### Likelihood Explanation
Nodes call `verify_tee()` every 7 days as part of normal operation (documented in `docs/securing-mpc-with-tee-design-doc.md`). If attestations expire for enough participants to drop the surviving set below the threshold relation, `accept_requests = false` is set. Participants would then naturally fix the issue and trigger a resharing via `vote_new_parameters()`. After the resharing completes, `accept_requests` is still `false`. This is a realistic operational scenario requiring no adversarial action — only the normal TEE attestation lifecycle.

### Recommendation
In `vote_reshared()`, reset `accept_requests = true` when transitioning to Running state, mirroring what `init()` and `init_running()` do:

```rust
if let Some(new_state) = self.protocol_state.vote_reshared(key_event_id)? {
    self.protocol_state = new_state;
    self.accept_requests = true; // restore after resharing resolves the TEE issue
    self.recompute_available_foreign_chains();
    // ... existing cleanup promises ...
}
```

The same fix should be applied to `vote_cancel_resharing` if it also transitions back to Running state without resetting the flag.

### Proof of Concept
1. Initialize contract with 3 participants, threshold 2.
2. Expire attestations for 2 of the 3 participants so only 1 valid attestation remains (below threshold 2).
3. Call `verify_tee()` — returns `false`, sets `accept_requests = false`, stays Running (kickout would break threshold relation).
4. Participants submit fresh attestations via `submit_participant_info()`.
5. Participants call `vote_new_parameters()` with a corrected participant set to trigger resharing.
6. All participants call `start_reshare_instance()` then `vote_reshared()` until resharing completes.
7. Contract is now Running with a valid participant set, but `accept_requests` is still `false`.
8. Any call to `sign()` panics: `"TEE validation failed: the contract is not accepting new requests"`.

### Citations

**File:** crates/contract/src/lib.rs (L298-302)
```rust
        // 4. Refuse the request if the contract is not currently accepting requests
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

**File:** crates/contract/src/lib.rs (L1962-1962)
```rust
            accept_requests: true,
```

**File:** crates/contract/src/lib.rs (L2041-2041)
```rust
            accept_requests: true,
```
