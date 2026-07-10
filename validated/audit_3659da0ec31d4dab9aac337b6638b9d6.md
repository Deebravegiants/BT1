### Title
Single Attested Participant Can Indefinitely Abort Key Generation and Resharing Instances - (File: `crates/contract/src/state/key_event.rs`)

### Summary
The `vote_abort` function in `KeyEvent` immediately nullifies the active key-generation or resharing instance upon a single participant's call, with no threshold requirement. A single Byzantine participant (strictly below the signing threshold) can repeatedly abort every attempt, permanently preventing the network from completing key generation (`Initializing` state) or key resharing (`Resharing` state).

### Finding Description

The external report describes a DoS pattern where a single unprivileged actor can front-run a legitimate operation with a minimal state-mutating call, causing the legitimate operation to fail. The analog here is that a single attested participant — strictly below the signing threshold — can call `vote_abort_key_event_instance` to immediately destroy the active key-event instance, forcing the leader to restart from scratch, and can repeat this indefinitely.

The root cause is in `KeyEvent::vote_abort`:

```rust
pub fn vote_abort(&mut self, key_event_id: KeyEventId) -> Result<(), Error> {
    let candidate = self.verify_vote(&key_event_id)?;
    if self.instance.as_ref().unwrap().completed.contains(&candidate) {
        return Err(VoteError::VoteAlreadySubmitted.into());
    }
    self.instance = None;   // ← single vote destroys the entire instance
    Ok(())
}
``` [1](#0-0) 

`verify_vote` only checks that the signer is an attested participant and that the `key_event_id` matches the current attempt. It does **not** require threshold-many votes to abort. [2](#0-1) 

The public contract entry point `vote_abort_key_event_instance` gates on `assert_caller_is_attested_participant_and_protocol_active`, which requires only that the caller is a single attested participant — not a threshold of them. [3](#0-2) 

The `VoteAlreadySubmitted` guard only fires if the aborting participant is already in the `completed` set (i.e., already voted success). A participant who has not yet voted success can always abort, even immediately after the leader starts the instance. [4](#0-3) 

The same `vote_abort` path is shared by both `InitializingContractState` and `ResharingContractState`: [5](#0-4) 

After each abort, the leader must call `start_keygen_instance` / `start_reshare_instance` with the next `attempt_id`. The Byzantine participant can immediately abort the new instance as well, since `next_attempt_id` is predictable from on-chain state. [6](#0-5) 

### Impact Explanation

**Medium.** A single Byzantine participant (below the signing threshold) can permanently prevent the MPC network from completing key generation or key resharing. This breaks the production safety invariant that the protocol should make progress whenever at least `threshold` honest participants are present. Concretely:

- **Key generation blocked**: The network stays in `Initializing` state indefinitely, never producing a usable key. No signing requests can be served.
- **Resharing blocked**: The network stays in `Resharing` state indefinitely, preventing participant-set updates (e.g., removing the Byzantine participant itself via `vote_new_parameters`).

This matches the allowed impact: *"Balance, request-lifecycle, participant-state, or contract execution-flow manipulation that breaks production safety/accounting invariants without relying on network-level DoS or operator misconfiguration."*

### Likelihood Explanation

**Medium.** The attacker must be an attested participant (voted in by governance). However, once admitted, a single participant can execute this attack with a trivially cheap on-chain transaction. The `key_event_id` of the next attempt is fully predictable from public contract state, so the attacker can front-run the leader's `start_keygen_instance` / `start_reshare_instance` call or abort immediately after it lands. Governance removal of the Byzantine participant via `vote_new_parameters` itself requires a resharing to complete — which the attacker can also abort — creating a deadlock.

### Recommendation

Require a **threshold** of abort votes before nullifying the instance, mirroring the threshold requirement for success votes. Alternatively, restrict `vote_abort_key_event_instance` so that only the leader (the participant with the lowest ID) can abort an instance unilaterally, while other participants must reach threshold to override. A simpler mitigation is to track per-participant abort votes and only set `self.instance = None` once `abort_votes.len() >= threshold`.

### Proof of Concept

1. The network enters `Initializing` state (key generation) or `Resharing` state (key resharing).
2. The leader (lowest-ID participant) calls `start_keygen_instance` / `start_reshare_instance` with `key_event_id = KeyEventId { epoch_id, domain_id, attempt_id: 0 }`.
3. The Byzantine participant (any single attested participant) immediately calls `vote_abort_key_event_instance(key_event_id)`. `vote_abort` sets `self.instance = None` after a single vote.
4. The leader observes the instance is gone and calls `start_keygen_instance` with `attempt_id: 1`.
5. The Byzantine participant calls `vote_abort_key_event_instance` with `attempt_id: 1`. Instance destroyed again.
6. Steps 4–5 repeat indefinitely. The network never completes key generation or resharing.
7. Because resharing is blocked, the governance cannot remove the Byzantine participant (resharing is required to change the participant set), creating a permanent deadlock. [1](#0-0) [3](#0-2) [7](#0-6)

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

**File:** crates/contract/src/state/key_event.rs (L173-189)
```rust
    fn verify_vote(
        &mut self,
        key_event_id: &KeyEventId,
    ) -> Result<AuthenticatedParticipantId, Error> {
        let candidate = AuthenticatedParticipantId::new(self.parameters.participants())?;
        self.cleanup_if_timed_out();
        let Some(instance) = self.instance.as_ref() else {
            return Err(KeyEventError::NoActiveKeyEvent.into());
        };
        if key_event_id.epoch_id != self.epoch_id
            || key_event_id.domain_id != self.domain.id
            || key_event_id.attempt_id != instance.attempt_id
        {
            return Err(KeyEventError::KeyEventIdMismatch.into());
        }
        Ok(candidate)
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

**File:** crates/contract/src/state/resharing.rs (L166-171)
```rust
    /// Casts a vote to abort the current key resharing attempt.
    /// After aborting, another call to start() is necessary to start a new attempt.
    /// Returns error if there is no active attempt, or if the signer is not a proposed participant.
    pub fn vote_abort(&mut self, key_event_id: KeyEventId) -> Result<(), Error> {
        self.resharing_key.vote_abort(key_event_id)
    }
```
