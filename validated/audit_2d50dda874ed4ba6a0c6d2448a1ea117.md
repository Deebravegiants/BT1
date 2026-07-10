### Title
Single Participant Can Permanently Abort Keygen/Resharing Attempts Without Threshold — (`crates/contract/src/state/key_event.rs`)

---

### Summary

The `vote_abort` function in `KeyEvent` allows **any single participant** (strictly below the signing threshold) to immediately nullify the active keygen or resharing instance by setting `self.instance = None`. Because this is a global state mutation shared across all participants for the current domain, a single Byzantine participant can repeatedly abort every attempt the leader starts, permanently preventing keygen or resharing from completing. This is the direct analog of the Derby M-15 bug: a shared state variable (`instance`) is mutated by one entity's action in a way that blocks all other entities from making progress.

---

### Finding Description

In `crates/contract/src/state/key_event.rs`, `vote_abort` is:

```rust
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
    self.instance = None;   // ← global state wiped by one participant
    Ok(())
}
``` [1](#0-0) 

The only guards are:
1. The signer must be a valid participant (`verify_vote` → `AuthenticatedParticipantId::new`).
2. The signer must not already appear in `completed` (i.e., must not have already cast a *success* vote).

There is **no threshold requirement**. A participant who has not yet voted success can call `vote_abort` at any time during an active instance and immediately destroy it.

The public entry point is:

```rust
pub fn vote_abort_key_event_instance(&mut self, key_event_id: KeyEventId) -> Result<(), Error> {
    self.assert_caller_is_attested_participant_and_protocol_active();
    self.protocol_state.vote_abort_key_event_instance(key_event_id)
}
``` [2](#0-1) 

which dispatches to both `InitializingContractState::vote_abort` and `ResharingContractState::vote_abort`: [3](#0-2) 

**Attack loop:**
1. Leader calls `start_keygen_instance` / `start_reshare_instance` → `instance` is set.
2. Byzantine participant immediately calls `vote_abort_key_event_instance` with the matching `key_event_id` (before casting any success vote).
3. `instance` is set to `None`; all other participants' in-flight `vote_pk` / `vote_reshared` calls now fail with `NoActiveKeyEvent`.
4. Leader must increment `next_attempt_id` and restart. Byzantine participant repeats from step 2.

This loop is unbounded. The `next_attempt_id` counter increments monotonically but there is no cap, no cooldown, and no penalty for repeated aborts. [4](#0-3) 

The Derby M-15 structural parallel is exact:

| Derby (M-15) | NEAR MPC |
|---|---|
| `lastTimeStamp` — global, updated by vault A's call | `instance` — global per domain, nullified by one participant's call |
| Vault B's `pushAllocationsToController` reverts | All other participants' `vote_pk`/`vote_reshared` revert with `NoActiveKeyEvent` |
| Fix: per-vault `lastTimeStamp` array | Fix: threshold-gated abort |

---

### Impact Explanation

If keygen cannot complete, the contract stays in `Initializing` state indefinitely: no new domain keys are ever published, and the MPC network cannot sign for those domains. If resharing cannot complete, the contract stays in `Resharing` state: the old key shares remain in use but the participant set cannot be updated, and any funds or signing capabilities gated on the new epoch are permanently inaccessible. Both outcomes constitute **permanent freezing of the MPC network's key-management capability**, matching the Critical/Medium allowed impacts (permanent freezing of funds controlled by the MPC network; contract execution-flow manipulation breaking production safety invariants).

---

### Likelihood Explanation

The attacker needs only one thing: to be an attested participant. Participants are not fully trusted in the Byzantine fault-tolerance model — the protocol is explicitly designed to tolerate up to `t-1` Byzantine participants. A single Byzantine participant (well below threshold) can execute this attack with a single on-chain transaction per attempt, requiring no coordination, no leaked keys, and no network-level interference.

---

### Recommendation

Gate `vote_abort` on a **threshold of abort votes** rather than a single vote, mirroring how `vote_cancel_resharing` already requires threshold votes from the previous running state: [5](#0-4) 

Concretely, `KeyEventInstance` should accumulate abort votes in a `BTreeSet` (analogous to `completed`) and only set `self.instance = None` once the abort-vote count reaches the governance threshold. This ensures a single Byzantine participant cannot unilaterally destroy an active attempt.

---

### Proof of Concept

```
// Setup: contract in Initializing state, 5 participants, threshold = 3.
// Attacker = participant[4] (Byzantine, below threshold).

1. Leader (participant[0]) calls start_keygen_instance(key_event_id).
   → instance is Some(KeyEventInstance { attempt_id: 0, ... })

2. Attacker calls vote_abort_key_event_instance(key_event_id).
   → verify_vote passes (attacker is a valid participant, instance is active,
     key_event_id matches).
   → completed.contains(attacker) == false (attacker never voted success).
   → self.instance = None.   ← global state destroyed

3. Participants [1,2,3] call vote_pk(key_event_id, pk).
   → verify_vote: cleanup_if_timed_out() is a no-op (instance is None, not timed out).
   → self.instance.as_ref() is None → Err(NoActiveKeyEvent).
   All three calls revert.

4. Leader calls start_keygen_instance(key_event_id.next_attempt()).
   → next_attempt_id increments to 1, new instance created.

5. Attacker repeats step 2 with the new key_event_id.
   → Loop continues indefinitely; keygen never completes.
``` [1](#0-0) [6](#0-5)

### Citations

**File:** crates/contract/src/state/key_event.rs (L65-79)
```rust
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

**File:** crates/contract/src/state/key_event.rs (L145-158)
```rust
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

**File:** crates/contract/src/state/key_event.rs (L171-189)
```rust
    /// Verifies that the signer is authorized to cast a vote and that the key event ID corresponds
    /// to the current generation attempt.
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

**File:** crates/contract/src/state/resharing.rs (L173-195)
```rust
    pub fn vote_cancel_resharing(&mut self) -> Result<Option<RunningContractState>, Error> {
        let previous_running_participants = self.previous_running_state.parameters.participants();
        let authenticated_candidate = AuthenticatedAccountId::new(previous_running_participants)?;
        self.cancellation_requests.insert(authenticated_candidate);

        let cancellation_votes_count = self.cancellation_requests.len() as u64;
        let previous_running_threshold = self.previous_running_state.parameters.threshold();

        let threshold_cancellation_votes_reached: bool =
            cancellation_votes_count >= previous_running_threshold.value();

        let running_state = if threshold_cancellation_votes_reached {
            let mut previous_running_state = self.previous_running_state.clone();
            let prospective_epoch_id = self.prospective_epoch_id();
            previous_running_state.previously_cancelled_resharing_epoch_id =
                Some(prospective_epoch_id);

            Some(previous_running_state)
        } else {
            None
        };

        Ok(running_state)
```
