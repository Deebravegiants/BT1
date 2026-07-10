### Title
Missing TEE Attestation Guard in `vote_cancel_keygen` Allows Non-Attested Participants to Abort Key Generation - (File: crates/contract/src/lib.rs)

### Summary

Every key-event mutation method in the MPC contract enforces TEE attestation via `assert_caller_is_attested_participant_and_protocol_active()`. The single exception is `vote_cancel_keygen`, which only calls `assert_caller_is_signer()`. This is a direct analog to the Booster.sol pattern: a guard that should block operations in an invalid participant state is absent from one code path, allowing the operation to proceed when it should be rejected.

### Finding Description

All key-event methods that mutate protocol state enforce the TEE attestation guard:

- `start_keygen_instance` — calls `assert_caller_is_attested_participant_and_protocol_active()` [1](#0-0) 
- `vote_pk` — calls `assert_caller_is_attested_participant_and_protocol_active()` [2](#0-1) 
- `start_reshare_instance` — calls `assert_caller_is_attested_participant_and_protocol_active()` [3](#0-2) 
- `vote_reshared` — calls `assert_caller_is_attested_participant_and_protocol_active()` [4](#0-3) 
- `vote_abort_key_event_instance` — calls `assert_caller_is_attested_participant_and_protocol_active()` [5](#0-4) 

`vote_cancel_keygen` is the sole outlier — it only calls `assert_caller_is_signer()` and then delegates directly to the state machine:

```rust
pub fn vote_cancel_keygen(&mut self, next_domain_id: u64) -> Result<(), Error> {
    Self::assert_caller_is_signer();
    log!("vote_cancel_keygen: signer={}", env::signer_account_id());
    if let Some(new_state) = self.protocol_state.vote_cancel_keygen(next_domain_id)? {
        self.protocol_state = new_state;
    }
    Ok(())
}
``` [6](#0-5) 

`assert_caller_is_attested_participant_and_protocol_active()` performs two checks that `assert_caller_is_signer()` does not: it verifies the caller is in the active participant set **and** that the caller holds a valid TEE attestation stored in `tee_state`:

```rust
fn assert_caller_is_attested_participant_and_protocol_active(&self) {
    let participants = self.protocol_state.active_participants();
    Self::assert_caller_is_signer();
    let attestation_check = self
        .tee_state
        .is_caller_an_attested_participant(participants);
    assert_matches::assert_matches!(
        attestation_check,
        Ok(()),
        "Caller must be an attested participant"
    );
}
``` [7](#0-6) 

The state-machine-level `vote_cancel_keygen` checks participant membership but does **not** check TEE attestation — that check is exclusively the contract's responsibility via the guard above. Because `vote_cancel_keygen` skips it, a participant whose attestation has expired, been revoked, or was never submitted can still cast a cancellation vote.

### Impact Explanation

`vote_cancel_keygen` reverts the contract from `Initializing` back to `Running`, discarding all in-progress key generation work. [8](#0-7) 

If the system is performing its **initial** domain key generation (the only path to a usable `Running` state with signing keys), a successful cancellation leaves the contract in `Running` with zero domains — permanently unable to process signature requests until a new `vote_add_domains` cycle completes. This breaks the request-lifecycle and contract execution-flow safety invariants. During a TEE image upgrade window, multiple participants may simultaneously hold expired attestations, making threshold cancellation achievable without any single node being fully compromised.

### Likelihood Explanation

The attack window is the TEE upgrade period: when the contract's allowed image hash list is updated, nodes running the old image have their attestations invalidated. [9](#0-8)  During this window, nodes with stale attestations are still registered participants and can call `vote_cancel_keygen`. If the threshold number of such nodes vote before they upgrade, key generation is aborted. This is a realistic operational condition, not a theoretical one.

### Recommendation

Add `self.assert_caller_is_attested_participant_and_protocol_active();` to `vote_cancel_keygen` immediately after `Self::assert_caller_is_signer()`, matching the pattern used by every other key-event method:

```rust
pub fn vote_cancel_keygen(&mut self, next_domain_id: u64) -> Result<(), Error> {
    Self::assert_caller_is_signer();
    self.assert_caller_is_attested_participant_and_protocol_active(); // add this
    log!("vote_cancel_keygen: signer={}", env::signer_account_id());
    if let Some(new_state) = self.protocol_state.vote_cancel_keygen(next_domain_id)? {
        self.protocol_state = new_state;
    }
    Ok(())
}
```

### Proof of Concept

1. Deploy the contract and start initial key generation (`vote_add_domains` → `Initializing`).
2. Simulate a TEE image hash rotation: update the allowed hash list so that `t` (threshold) existing participants now have expired/invalid attestations.
3. Each of those `t` participants calls `vote_cancel_keygen(next_domain_id)` directly. Because `assert_caller_is_attested_participant_and_protocol_active()` is absent, the call passes the signer check and the state-machine participant-membership check.
4. After `t` votes, the contract transitions back to `Running` with no domain keys.
5. Any subsequent `sign()` call panics at `domain_registry()` with `ProtocolStateNotRunningNorResharing` because there are no domains, permanently blocking signature service until operators manually restart key generation. [10](#0-9)

### Citations

**File:** crates/contract/src/lib.rs (L1081-1081)
```rust
        self.assert_caller_is_attested_participant_and_protocol_active();
```

**File:** crates/contract/src/lib.rs (L1115-1115)
```rust
        self.assert_caller_is_attested_participant_and_protocol_active();
```

**File:** crates/contract/src/lib.rs (L1142-1142)
```rust
        self.assert_caller_is_attested_participant_and_protocol_active();
```

**File:** crates/contract/src/lib.rs (L1168-1168)
```rust
        self.assert_caller_is_attested_participant_and_protocol_active();
```

**File:** crates/contract/src/lib.rs (L1272-1279)
```rust
    pub fn vote_cancel_keygen(&mut self, next_domain_id: u64) -> Result<(), Error> {
        Self::assert_caller_is_signer();
        log!("vote_cancel_keygen: signer={}", env::signer_account_id());

        if let Some(new_state) = self.protocol_state.vote_cancel_keygen(next_domain_id)? {
            self.protocol_state = new_state;
        }
        Ok(())
```

**File:** crates/contract/src/lib.rs (L1291-1291)
```rust
        self.assert_caller_is_attested_participant_and_protocol_active();
```

**File:** crates/contract/src/lib.rs (L2389-2403)
```rust
    fn assert_caller_is_attested_participant_and_protocol_active(&self) {
        let participants = self.protocol_state.active_participants();

        Self::assert_caller_is_signer();

        let attestation_check = self
            .tee_state
            .is_caller_an_attested_participant(participants);

        assert_matches::assert_matches!(
            attestation_check,
            Ok(()),
            "Caller must be an attested participant"
        );
    }
```

**File:** crates/contract/README.md (L249-254)
```markdown
    Running --> Resharing : vote_new_parameters
    Initializing --> Running : vote_pk
    Initializing --> Running : vote_cancel_keygen
    Resharing --> Running : vote_reshared
    Resharing --> Resharing : vote_new_parameters
```
```

**File:** crates/node/src/tee/allowed_image_hashes_watcher.rs (L179-183)
```rust
        let running_image_is_not_allowed = !allowed_hashes.iter().contains(&self.current_image);

        if running_image_is_not_allowed {
            tracing::error!("Currently running node image is NOT in the allowed hash list!");
        }
```

**File:** crates/contract/src/state.rs (L34-41)
```rust
    pub fn domain_registry(&self) -> Result<&DomainRegistry, Error> {
        let domain_registry = match self {
            ProtocolContractState::Running(state) => &state.domains,
            ProtocolContractState::Resharing(state) => &state.previous_running_state.domains,
            _ => return Err(InvalidState::ProtocolStateNotRunningNorResharing.into()),
        };

        Ok(domain_registry)
```
