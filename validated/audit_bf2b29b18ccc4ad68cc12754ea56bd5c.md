### Title
Single Participant Can Permanently Abort Key Generation / Resharing Instances via `vote_abort_key_event_instance` — (File: `crates/contract/src/state/key_event.rs`)

---

### Summary

The `vote_abort` function in `KeyEvent` allows **any single attested participant** to immediately nullify the active key-event instance with no threshold requirement. A Byzantine participant strictly below the signing threshold can call `vote_abort_key_event_instance` in a tight loop — once per attempt the leader starts — permanently preventing DKG or resharing from completing.

---

### Finding Description

In `crates/contract/src/state/key_event.rs`, `vote_abort` unconditionally sets `self.instance = None` as soon as one participant's call passes `verify_vote`:

```rust
pub fn vote_abort(&mut self, key_event_id: KeyEventId) -> Result<(), Error> {
    let candidate = self.verify_vote(&key_event_id)?;
    if self.instance.as_ref().unwrap().completed.contains(&candidate) {
        return Err(VoteError::VoteAlreadySubmitted.into());
    }
    self.instance = None;   // ← single-vote abort, no threshold
    Ok(())
}
``` [1](#0-0) 

The public entry point in `lib.rs` only checks that the caller is an attested participant; it imposes no threshold:

```rust
pub fn vote_abort_key_event_instance(&mut self, key_event_id: KeyEventId) -> Result<(), Error> {
    self.assert_caller_is_attested_participant_and_protocol_active();
    self.protocol_state.vote_abort_key_event_instance(key_event_id)
}
``` [2](#0-1) 

The dispatch layer routes this to both `Initializing` and `Resharing` states:

```rust
pub fn vote_abort_key_event_instance(&mut self, key_event_id: KeyEventId) -> Result<(), Error> {
    match self {
        ProtocolContractState::Resharing(state) => state.vote_abort(key_event_id),
        ProtocolContractState::Initializing(state) => state.vote_abort(key_event_id),
        _ => Err(InvalidState::ProtocolStateNotRunningNorResharing.into()),
    }
}
``` [3](#0-2) 

This is structurally inconsistent with every other destructive governance action in the contract. `vote_cancel_resharing` requires threshold votes before reverting state:

```rust
let threshold_cancellation_votes_reached: bool =
    cancellation_votes_count >= previous_running_threshold.value();
``` [4](#0-3) 

And `vote_cancel` (keygen) likewise requires threshold votes:

```rust
if self.cancel_votes.insert(participant) && self.cancel_votes.len() >= required_threshold {
``` [5](#0-4) 

`vote_abort` is the only instance-terminating action that requires **zero** threshold consensus.

---

### Impact Explanation

**Critical — permanent freezing of the MPC network's signing capability.**

During initial key generation (`Initializing` state), the MPC network has no usable key shares yet. If a single Byzantine participant repeatedly aborts every attempt, the system can never transition to `Running`, meaning no threshold signatures can ever be produced. All funds whose spending paths depend on the MPC-derived key are permanently frozen.

During resharing (`Resharing` state), the old keys remain usable, but the resharing can be permanently blocked, preventing participant-set rotation or key refresh — a High-severity liveness failure.

---

### Likelihood Explanation

- The attacker only needs to be **one** attested participant — strictly below the signing threshold.
- The attack is cheap: one NEAR transaction per attempt the leader starts.
- The leader's retry loop (`resharing_leader` / `keygen_leader`) will keep issuing new `start_*_instance` calls; the attacker simply matches each new `key_event_id` and calls `vote_abort_key_event_instance`.
- No collusion, no leaked keys, no network-level DoS required. [6](#0-5) 

---

### Recommendation

Require threshold votes to abort a key-event instance, mirroring the pattern already used for `vote_cancel_resharing` and `vote_cancel`:

```rust
pub fn vote_abort(&mut self, key_event_id: KeyEventId) -> Result<(), Error> {
    let candidate = self.verify_vote(&key_event_id)?;
    let instance = self.instance.as_mut().unwrap();
    if instance.abort_votes.contains(&candidate) {
        return Err(VoteError::VoteAlreadySubmitted.into());
    }
    instance.abort_votes.insert(candidate);
    if instance.abort_votes.len() >= self.parameters.threshold().value() as usize {
        self.instance = None;
    }
    Ok(())
}
```

Alternatively, remove `vote_abort` entirely and rely on the existing block-height timeout (`expires_on`) to naturally expire failed attempts — the leader already retries after timeout. [7](#0-6) 

---

### Proof of Concept

1. System enters `Initializing` state (initial DKG) or `Resharing` state.
2. The leader (lowest participant ID) calls `start_keygen_instance` / `start_reshare_instance` with `key_event_id = {epoch, domain, attempt=0}`. A `KeyEventInstance` is created.
3. Byzantine participant (any single attested participant) calls `vote_abort_key_event_instance({epoch, domain, attempt=0})`. `verify_vote` passes (they are a valid participant); `self.instance` is set to `None`.
4. The leader observes no active instance and calls `start_*_instance` again with `attempt=1`.
5. Byzantine participant calls `vote_abort_key_event_instance({epoch, domain, attempt=1})`.
6. Steps 4–5 repeat indefinitely. `next_attempt_id` increments without bound; the key is never generated; the system never reaches `Running` state. [8](#0-7) [2](#0-1)

### Citations

**File:** crates/contract/src/state/key_event.rs (L63-79)
```rust
    /// Start a new key event instance as the leader, if one isn't already active.
    /// The leader is always the participant with the lowest participant ID.
    pub fn start(&mut self, key_event_id: KeyEventId, timeout_blocks: u64) -> Result<(), Error> {
        self.cleanup_if_timed_out();
        if self.instance.is_some() {
            return Err(KeyEventError::ActiveKeyEvent.into());
        }
        let expected_key_event_id =
            KeyEventId::new(self.epoch_id, self.domain.id, self.next_attempt_id);
        if key_event_id != expected_key_event_id {
            return Err(KeyEventError::KeyEventIdMismatch.into());
        }
        self.verify_leader()?;
        self.instance = Some(KeyEventInstance::new(self.next_attempt_id, timeout_blocks));
        self.next_attempt_id = self.next_attempt_id.next();
        Ok(())
    }
```

**File:** crates/contract/src/state/key_event.rs (L143-158)
```rust
    /// Casts a vote to abort the current keygen instance.
    /// A new instance needs to be started later to start a new keygen attempt.
    pub fn vote_abort(&mut self, key_event_id: KeyEventId) -> Result<(), Error> {
        let candidate = self.verify_vote(&key_event_id)?;
        if self
            .instance
            .as_ref()
            .unwrap()
            .completed
            .contains(&candidate)
        {
            return Err(VoteError::VoteAlreadySubmitted.into());
        }
        self.instance = None;
        Ok(())
    }
```

**File:** crates/contract/src/state/key_event.rs (L256-264)
```rust
    pub fn new(attempt_id: AttemptId, timeout_blocks: u64) -> Self {
        KeyEventInstance {
            attempt_id,
            started_in: env::block_height(),
            expires_on: env::block_height() + 1 + timeout_blocks,
            completed: BTreeSet::new(),
            public_key: None,
        }
    }
```

**File:** crates/contract/src/lib.rs (L1284-1295)
```rust
    #[handle_result]
    pub fn vote_abort_key_event_instance(&mut self, key_event_id: KeyEventId) -> Result<(), Error> {
        log!(
            "vote_abort_key_event_instance: signer={}",
            env::signer_account_id()
        );

        self.assert_caller_is_attested_participant_and_protocol_active();

        self.protocol_state
            .vote_abort_key_event_instance(key_event_id)
    }
```

**File:** crates/contract/src/state.rs (L154-160)
```rust
    pub fn vote_abort_key_event_instance(&mut self, key_event_id: KeyEventId) -> Result<(), Error> {
        match self {
            ProtocolContractState::Resharing(state) => state.vote_abort(key_event_id),
            ProtocolContractState::Initializing(state) => state.vote_abort(key_event_id),
            _ => Err(InvalidState::ProtocolStateNotRunningNorResharing.into()),
        }
    }
```

**File:** crates/contract/src/state/resharing.rs (L181-182)
```rust
        let threshold_cancellation_votes_reached: bool =
            cancellation_votes_count >= previous_running_threshold.value();
```

**File:** crates/contract/src/state/initializing.rs (L132-132)
```rust
        if self.cancel_votes.insert(participant) && self.cancel_votes.len() >= required_threshold {
```
