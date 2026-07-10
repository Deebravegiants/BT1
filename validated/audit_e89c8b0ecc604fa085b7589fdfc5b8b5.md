### Title
Single Participant Can Indefinitely Block Key Generation and Resharing via Unilateral `vote_abort_key_event_instance` — (File: `crates/contract/src/state/key_event.rs`)

---

### Summary

The `vote_abort` function in `KeyEvent` immediately destroys the active key event instance upon a **single** participant's call, requiring no threshold of votes. Any attested participant who has not yet voted success can unilaterally abort the current DKG or resharing attempt. By repeatedly aborting each new instance as soon as the leader restarts it, a single malicious participant strictly below the signing threshold can permanently block key generation or resharing from ever completing.

---

### Finding Description

In `crates/contract/src/state/key_event.rs`, `vote_abort` is implemented as:

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
    self.instance = None;   // ← entire instance destroyed on one vote
    Ok(())
}
``` [1](#0-0) 

The only guard is that a participant who already cast a **success** vote cannot also abort. Any other participant — a single one — can call this and immediately set `self.instance = None`, wiping all accumulated success votes and the running timeout.

This is exposed publicly via `vote_abort_key_event_instance` in `lib.rs`, which only requires `assert_caller_is_attested_participant_and_protocol_active()`: [2](#0-1) 

After the abort, the leader must call `start()` again to create a fresh `KeyEventInstance` with a new `expires_on` block height: [3](#0-2) 

The malicious participant can immediately abort the new instance as well, because the `completed.contains` guard is reset with each new instance. This cycle repeats indefinitely.

The same `vote_abort` path is shared by both `InitializingContractState::vote_abort` (DKG) and `ResharingContractState::vote_abort` (resharing): [4](#0-3) [5](#0-4) 

Contrast this with `vote_cancel_resharing`, which correctly requires a **threshold** of votes before acting: [6](#0-5) 

And `vote_cancel_keygen`, which also requires threshold votes via `BTreeSet::insert` idempotency: [7](#0-6) 

`vote_abort` is the only instance-level action that takes immediate irreversible effect on a single vote.

---

### Impact Explanation

**Blocking DKG (Initializing state):** A single malicious participant prevents new cryptographic domains from ever completing key generation. New signing capabilities (e.g., new chains) can never be activated.

**Blocking Resharing (Resharing state):** A single malicious participant prevents the participant set from ever changing. This is the more severe case:

- The MPC network cannot remove a compromised node.
- TEE attestations have a finite validity window (`tee_upgrade_deadline_duration`). If resharing is permanently blocked, the current participant set's attestations will eventually expire, causing `accept_requests` to be set to `false` and halting all signing. Funds controlled by the MPC network would be permanently frozen.

This matches: **Critical — permanent freezing of funds controlled by the MPC network.**

---

### Likelihood Explanation

- Requires exactly **one** compromised or malicious attested participant — strictly below the signing threshold.
- The attacker needs no special privilege beyond being a current participant with a valid TEE attestation.
- The attack is cheap: each abort is a single on-chain call. The attacker can front-run the leader's `start()` call or simply monitor the chain and abort each new instance as it appears.
- There is no on-chain mechanism to remove a participant without completing a resharing, creating a circular dependency: the malicious participant blocks resharing, and resharing is the only way to remove them.

---

### Recommendation

Require a **threshold** of votes to abort a key event instance, mirroring the design of `vote_cancel_resharing`. Accumulate abort votes in a `BTreeSet` (as `cancel_votes` does in `InitializingContractState`) and only set `self.instance = None` once the threshold is reached:

```rust
// In KeyEventInstance, add:
abort_votes: BTreeSet<AuthenticatedParticipantId>,

// In vote_abort:
self.instance.as_mut().unwrap().abort_votes.insert(candidate);
if self.instance.as_ref().unwrap().abort_votes.len() >= threshold {
    self.instance = None;
}
```

This ensures that aborting a key event instance requires the same level of consensus as other governance actions, preventing a single Byzantine participant from blocking the protocol indefinitely.

---

### Proof of Concept

**Setup:** 5-of-9 MPC network in `InitializingContractState` (or `ResharingContractState`). Participant `P_evil` is one of the 9.

1. Leader `P_leader` calls `start_keygen_instance(key_event_id_0)` → `KeyEventInstance` created with `expires_on = block + timeout`.
2. `P_evil` immediately calls `vote_abort_key_event_instance(key_event_id_0)` → `self.instance = None`. All progress lost.
3. `P_leader` calls `start_keygen_instance(key_event_id_1)` (next `attempt_id`) → new instance created.
4. `P_evil` calls `vote_abort_key_event_instance(key_event_id_1)` → destroyed again.
5. Steps 3–4 repeat indefinitely. `P_evil` is never removed because removal requires completing a resharing, which is also blocked by the same mechanism.

The `completed.contains` guard does not protect against this because each new instance starts with an empty `completed` set: [3](#0-2)

### Citations

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

**File:** crates/contract/src/state/initializing.rs (L107-109)
```rust
    pub fn vote_abort(&mut self, key_event_id: KeyEventId) -> Result<(), Error> {
        self.generating_key.vote_abort(key_event_id)
    }
```

**File:** crates/contract/src/state/initializing.rs (L117-143)
```rust
    pub fn vote_cancel(
        &mut self,
        next_domain_id: u64,
    ) -> Result<Option<RunningContractState>, Error> {
        if next_domain_id != self.domains.next_domain_id() {
            return Err(InvalidParameters::NextDomainIdMismatch.into());
        }
        let participant = AuthenticatedParticipantId::new(
            self.generating_key.proposed_parameters().participants(),
        )?;
        let required_threshold = self
            .generating_key
            .proposed_parameters()
            .threshold()
            .value() as usize;
        if self.cancel_votes.insert(participant) && self.cancel_votes.len() >= required_threshold {
            let mut domains = self.domains.clone();
            domains.retain_domains(self.generated_keys.len());
            return Ok(Some(RunningContractState::new(
                domains,
                Keyset::new(self.epoch_id, self.generated_keys.clone()),
                self.generating_key.proposed_parameters().clone(),
                AddDomainsVotes::default(),
            )));
        }
        Ok(None)
    }
```

**File:** crates/contract/src/state/resharing.rs (L169-171)
```rust
    pub fn vote_abort(&mut self, key_event_id: KeyEventId) -> Result<(), Error> {
        self.resharing_key.vote_abort(key_event_id)
    }
```

**File:** crates/contract/src/state/resharing.rs (L173-196)
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
    }
```
