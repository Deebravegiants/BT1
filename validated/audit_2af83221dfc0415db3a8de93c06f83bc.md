### Title
Single-Participant Unrestricted Key Event Abortion Enables Indefinite Protocol Liveness Disruption - (File: `crates/contract/src/state/key_event.rs`)

---

### Summary

`vote_abort_key_event_instance` allows any **single** attested participant to immediately clear an active key event instance with no minimum time restriction between successive aborts. This is the direct analog of the external report's `gulp_emissions` pattern: just as anyone could call `gulp_emissions` repeatedly with no cooldown to dilute rewards indefinitely, any single Byzantine participant (strictly below the signing threshold) can call `vote_abort_key_event_instance` repeatedly — once per new instance — to indefinitely block key generation or resharing.

---

### Finding Description

**Entry point** — `crates/contract/src/lib.rs`, `vote_abort_key_event_instance`:

```rust
pub fn vote_abort_key_event_instance(&mut self, key_event_id: KeyEventId) -> Result<(), Error> {
    self.assert_caller_is_attested_participant_and_protocol_active();
    self.protocol_state.vote_abort_key_event_instance(key_event_id)
}
```

The only gate is `assert_caller_is_attested_participant_and_protocol_active` — any single attested participant in the active set passes. [1](#0-0) 

**Root cause** — `crates/contract/src/state/key_event.rs`, `KeyEvent::vote_abort`:

```rust
pub fn vote_abort(&mut self, key_event_id: KeyEventId) -> Result<(), Error> {
    let candidate = self.verify_vote(&key_event_id)?;
    if self.instance.as_ref().unwrap().completed.contains(&candidate) {
        return Err(VoteError::VoteAlreadySubmitted.into());
    }
    self.instance = None;   // ← entire instance cleared by one participant
    Ok(())
}
```

The `completed.contains(&candidate)` guard only prevents the same participant from aborting the **same** instance twice. Once the leader restarts with a new `attempt_id`, the guard resets and the same participant can abort again immediately. There is no:
- Threshold requirement for abort (contrast: `vote_cancel_resharing` requires threshold votes)
- Minimum block height gap between successive aborts
- Per-participant abort quota per epoch [2](#0-1) 

**New instance creation** — `KeyEventInstance::new` stamps `expires_on = block_height + 1 + timeout_blocks`. The leader can restart immediately after an abort, and the Byzantine participant can abort the new instance in the very next block: [3](#0-2) 

**Default timeout** is only 30 blocks (`DEFAULT_KEY_EVENT_TIMEOUT_BLOCKS = 30`), so even without the abort mechanism the window is short. With it, the attacker collapses the effective window to zero by aborting before any honest votes accumulate. [4](#0-3) 

---

### Impact Explanation

A single Byzantine participant (1 < threshold) can:

1. **During `Initializing` state** — block all key generation for new domains. New signing domains (ECDSA, EdDSA, CKD) can never be activated, permanently degrading the network's capabilities.
2. **During `Resharing` state** — block all participant-set changes. Because `active_participants()` returns the **proposed** new set during resharing, any participant retained in the new set can abort resharing indefinitely, preventing the network from adding or removing participants.

Both cases break the production safety invariant that the protocol can complete key events within a bounded time. This matches the allowed Medium impact: *"contract execution-flow manipulation that breaks production safety/accounting invariants."* [5](#0-4) 

---

### Likelihood Explanation

The attacker must be an attested participant in the active set — a realistic role for any of the ~10 production MPC nodes. The attack requires only:
1. A valid TEE attestation (renewed hourly by honest nodes; a Byzantine node can do the same).
2. Watching the contract state for a new `KeyEventInstance` (trivially done via the NEAR indexer).
3. Calling `vote_abort_key_event_instance` with the current `key_event_id` — a single cheap transaction.

No threshold collusion, no leaked keys, no network-level DoS is required. A single participant acting alone suffices.

---

### Recommendation

Require a **threshold** of abort votes before clearing an instance (mirroring `vote_cancel_resharing`), or enforce a **minimum block gap** between successive aborts by the same participant, or introduce a **per-epoch abort quota** per participant. Any of these would prevent a single actor from looping the abort/restart cycle indefinitely.

---

### Proof of Concept

```
State: Resharing (or Initializing)

Block B:
  Leader → start_reshare_instance(key_event_id = {epoch=1, domain=0, attempt=0})
  Byzantine participant → vote_abort_key_event_instance({epoch=1, domain=0, attempt=0})
  → instance cleared; attempt_id advances to 1

Block B+1:
  Leader → start_reshare_instance(key_event_id = {epoch=1, domain=0, attempt=1})
  Byzantine participant → vote_abort_key_event_instance({epoch=1, domain=0, attempt=1})
  → instance cleared; attempt_id advances to 2

... repeat indefinitely at ~1 NEAR block per cycle (~1 second) ...
```

The `completed` set is fresh for each new `attempt_id`, so the per-instance double-vote guard never triggers. The resharing (or keygen) never completes as long as the Byzantine participant remains attested. [6](#0-5) [7](#0-6)

### Citations

**File:** crates/contract/src/lib.rs (L1285-1295)
```rust
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

**File:** crates/contract/src/config.rs (L4-5)
```rust
/// Default for `key_event_timeout_blocks`.
const DEFAULT_KEY_EVENT_TIMEOUT_BLOCKS: u64 = 30;
```

**File:** crates/contract/src/state.rs (L255-270)
```rust
    pub fn active_participants(&self) -> &Participants {
        match self {
            ProtocolContractState::Initializing(state) => {
                state.generating_key.proposed_parameters().participants()
            }
            ProtocolContractState::Running(state) => state.parameters.participants(),
            ProtocolContractState::Resharing(state) => {
                state.resharing_key.proposed_parameters().participants()
            }
            ProtocolContractState::NotInitialized => {
                panic!(
                    "Protocol must be Initializing, Running, or Resharing to access active participants"
                );
            }
        }
    }
```

**File:** crates/contract/src/state/resharing.rs (L97-106)
```rust
    /// Starts a new attempt to reshare the key for the current domain.
    /// Returns an Error if the signer is not the leader (the participant with the lowest ID).
    pub fn start(
        &mut self,
        key_event_id: KeyEventId,
        key_event_timeout_blocks: u64,
    ) -> Result<(), Error> {
        self.resharing_key
            .start(key_event_id, key_event_timeout_blocks)
    }
```
