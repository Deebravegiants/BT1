### Title
`vote_cancel_resharing()` Accepts No Epoch Identifier, Allowing Stale Votes to Cancel an Unintended Resharing - (File: `crates/contract/src/lib.rs`)

---

### Summary

`vote_cancel_resharing()` takes no parameter identifying which resharing epoch is being cancelled. If resharing epoch N+1 is cancelled and a new resharing epoch N+2 is started before a participant's in-flight `vote_cancel_resharing` transaction is executed, that transaction silently counts as a cancellation vote against N+2 — a resharing the participant never intended to cancel. The sibling function `vote_cancel_keygen` was already given a `next_domain_id` guard for exactly this reason, but `vote_cancel_resharing` was not.

---

### Finding Description

`vote_cancel_resharing` is defined with no discriminating parameter:

```rust
// crates/contract/src/lib.rs:1254
pub fn vote_cancel_resharing(&mut self) -> Result<(), Error> {
    Self::assert_caller_is_signer();
    if let Some(new_state) = self.protocol_state.vote_cancel_resharing()? {
        self.protocol_state = new_state;
    }
    Ok(())
}
``` [1](#0-0) 

The implementation simply inserts the caller into `cancellation_requests` of whatever `ResharingContractState` is currently live:

```rust
// crates/contract/src/state/resharing.rs:173-196
pub fn vote_cancel_resharing(&mut self) -> Result<Option<RunningContractState>, Error> {
    let previous_running_participants = self.previous_running_state.parameters.participants();
    let authenticated_candidate = AuthenticatedAccountId::new(previous_running_participants)?;
    self.cancellation_requests.insert(authenticated_candidate);
    ...
}
``` [2](#0-1) 

There is no check that the caller is voting to cancel the specific resharing epoch they observed. Compare this with `vote_cancel_keygen`, which explicitly takes `next_domain_id` and whose doc comment reads: *"A next_domain_id that matches that in the state's domains struct must be passed in. This is to prevent stale requests from accidentally cancelling a future key generation state."* [3](#0-2) 

**Attack / race scenario:**

1. Resharing epoch N+1 is in progress (participant set A, e.g., adding node X).
2. Participant P observes resharing N+1 and decides it is undesirable; P submits `vote_cancel_resharing()`.
3. Before P's transaction is included, the remaining threshold participants also vote to cancel N+1. The contract transitions back to `Running`.
4. The other participants immediately vote `vote_new_parameters` for a new resharing N+2 (different participant set B, e.g., adding node Y instead). The contract enters `Resharing` with a fresh `ResharingContractState` (empty `cancellation_requests`).
5. P's delayed transaction now executes. The contract is in `Resharing` state for epoch N+2. P's vote is inserted into N+2's `cancellation_requests`. P has now contributed a cancellation vote against a resharing they never reviewed or intended to cancel.

Because `cancellation_requests` is reset to an empty `HashSet` when a new `ResharingContractState` is created, there is no replay protection from the previous epoch's votes — but a new in-flight transaction from the same participant carries over perfectly. [4](#0-3) 

---

### Impact Explanation

A participant's `vote_cancel_resharing` transaction, submitted with the intent to cancel resharing N+1, silently counts as a cancellation vote against resharing N+2. If enough participants are in this situation simultaneously (e.g., all submitted cancel votes for N+1 in the same block window, N+1 was cancelled by a concurrent threshold, and N+2 started immediately), the threshold for cancellation of N+2 could be reached without any participant having deliberately voted to cancel N+2.

This breaks the participant-state safety invariant: participants must be able to make informed, epoch-specific decisions about which resharing to cancel. An unintended cancellation of a resharing disrupts the MPC network's key-management lifecycle and forces another resharing cycle, potentially stalling signing operations and delaying legitimate participant set changes.

**Allowed impact class:** Medium — participant-state and contract execution-flow manipulation that breaks production safety/accounting invariants.

---

### Likelihood Explanation

The race window exists whenever:
- A resharing is cancelled (threshold votes collected), AND
- A new resharing is proposed and accepted (all participants vote `vote_new_parameters`) within the same or adjacent blocks, AND
- One or more participants have in-flight `vote_cancel_resharing` transactions from the previous resharing.

On NEAR, block times are ~1 second and transactions can be delayed by network congestion or RPC retries. The `vote_new_parameters` call requires all proposed participants to vote, which can happen quickly in an automated node setup. The scenario is realistic in production, particularly during resharing retry flows (cancel → immediately re-propose), which is the documented operational pattern. [5](#0-4) 

---

### Recommendation

Add a `prospective_epoch_id: EpochId` parameter to `vote_cancel_resharing`, mirroring the guard already present in `vote_cancel_keygen` and `vote_new_parameters`. Inside the implementation, verify that the provided epoch ID matches `self.prospective_epoch_id()` before recording the vote; revert if they differ.

```rust
pub fn vote_cancel_resharing(
    &mut self,
    prospective_epoch_id: EpochId,
) -> Result<(), Error> {
    Self::assert_caller_is_signer();
    // Verify the caller is voting to cancel the resharing they observed.
    if let ProtocolContractState::Resharing(state) = &self.protocol_state {
        if state.prospective_epoch_id() != prospective_epoch_id {
            return Err(InvalidParameters::EpochMismatch { ... }.into());
        }
    }
    if let Some(new_state) = self.protocol_state.vote_cancel_resharing()? {
        self.protocol_state = new_state;
    }
    Ok(())
}
```

This is the same pattern used by `vote_cancel_keygen` (`next_domain_id`), `vote_reshared` (`key_event_id`), and `vote_new_parameters` (`prospective_epoch_id`). [6](#0-5) 

---

### Proof of Concept

**State:** Running, epoch 0. Participants: {A, B, C}, threshold 2.

1. All three participants vote `vote_new_parameters(epoch_id=1, proposal={A,B,C,D})`. Contract enters `Resharing(epoch=1)`.
2. Participant A decides to cancel. A submits `vote_cancel_resharing()`. Transaction is pending in the mempool.
3. Participants B and C also submit `vote_cancel_resharing()`. Their transactions execute first (threshold=2 reached). Contract returns to `Running(epoch=0, previously_cancelled=1)`.
4. Participants A, B, C immediately vote `vote_new_parameters(epoch_id=2, proposal={A,B,C,E})`. Contract enters `Resharing(epoch=2)` with empty `cancellation_requests`.
5. A's delayed `vote_cancel_resharing()` transaction now executes. The contract is in `Resharing(epoch=2)`. A's vote is inserted into epoch 2's `cancellation_requests`. A has now voted to cancel a resharing involving participant E — which A never reviewed.
6. If B or C also have delayed transactions, epoch 2 is cancelled without any participant having deliberately chosen to cancel it.

The `cancellation_requests` field is confirmed to be reset to `HashSet::new()` on every new `ResharingContractState` construction, providing no cross-epoch replay protection. [7](#0-6)

### Citations

**File:** crates/contract/src/lib.rs (L1254-1263)
```rust
    pub fn vote_cancel_resharing(&mut self) -> Result<(), Error> {
        Self::assert_caller_is_signer();
        log!("vote_cancel_resharing: signer={}", env::signer_account_id());

        if let Some(new_state) = self.protocol_state.vote_cancel_resharing()? {
            self.protocol_state = new_state;
        }

        Ok(())
    }
```

**File:** crates/contract/src/lib.rs (L1265-1280)
```rust
    /// Casts a vote to cancel key generation. Any keys that have already been generated
    /// are kept and we transition into Running state; remaining domains are permanently deleted.
    /// Deleted domain IDs cannot be reused again in future calls to vote_add_domains.
    ///
    /// A next_domain_id that matches that in the state's domains struct must be passed in. This is
    /// to prevent stale requests from accidentally cancelling a future key generation state.
    #[handle_result]
    pub fn vote_cancel_keygen(&mut self, next_domain_id: u64) -> Result<(), Error> {
        Self::assert_caller_is_signer();
        log!("vote_cancel_keygen: signer={}", env::signer_account_id());

        if let Some(new_state) = self.protocol_state.vote_cancel_keygen(next_domain_id)? {
            self.protocol_state = new_state;
        }
        Ok(())
    }
```

**File:** crates/contract/src/state/resharing.rs (L27-39)
```rust
#[near(serializers=[borsh, json])]
#[derive(Debug)]
#[cfg_attr(feature = "dev-utils", derive(Clone, PartialEq))]
pub struct ResharingContractState {
    pub previous_running_state: RunningContractState,
    pub reshared_keys: Vec<KeyForDomain>,
    pub resharing_key: KeyEvent,
    pub cancellation_requests: HashSet<AuthenticatedAccountId>,
    /// Per-domain `ReconstructionThreshold` updates carried from the accepted
    /// proposal. Applied to the [`DomainRegistry`](crate::primitives::domain::DomainRegistry)
    /// when resharing completes; empty means "keep current per-domain thresholds".
    pub per_domain_thresholds: BTreeMap<DomainId, ReconstructionThreshold>,
}
```

**File:** crates/contract/src/state/resharing.rs (L86-91)
```rust
                        .unwrap()
                        .clone(),
                    proposal.parameters().clone(),
                ),
                cancellation_requests: HashSet::new(),
                per_domain_thresholds: proposal.per_domain_thresholds().clone(),
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

**File:** crates/e2e-tests/tests/cancellation_of_resharing.rs (L110-116)
```rust
    // Retry resharing using node 5 (running since startup, fully synced)
    // instead of the killed node 4.
    tracing::info!("retrying resharing with node 5 instead of killed node 4");
    cluster
        .start_resharing_and_wait(&[0, 1, 2, 3, 5], 3)
        .await
        .expect("retry resharing failed");
```
