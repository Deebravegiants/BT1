### Title
`vote_cancel_resharing` Can Be Front-Run by `vote_reshared` Completing Before Cancellation Threshold Is Reached — (File: `crates/contract/src/state/resharing.rs`)

---

### Summary

The `ResharingContractState` exposes two concurrent, mutually unguarded state-transition paths: `vote_cancel_resharing` (old participants aborting the resharing) and `vote_reshared` (new participants completing it). Neither path checks whether the other is in progress. If the new participant set becomes untrusted after resharing is initiated, the old participants may broadcast `vote_cancel_resharing` transactions, but the new participants can race to finalize resharing via `vote_reshared` before the cancellation threshold is reached — permanently transferring key-share control to the untrusted set.

---

### Finding Description

During the `Resharing` state, two independent vote paths can run simultaneously:

**Path A — Cancellation** (`vote_cancel_resharing`):
Old participants call this to revert to the previous `RunningContractState`. It requires `previous_running_threshold` votes from the **old** participant set. [1](#0-0) 

**Path B — Completion** (`vote_reshared`):
New (prospective) participants call this to confirm they received new key shares. It requires **all** new participants to vote. [2](#0-1) 

The completion threshold check in `KeyEvent::vote_success` is `count == self.parameters.participants().len()` — i.e., unanimous among the new set. [3](#0-2) 

Neither function checks whether the other path has accumulated votes. There is no "cancellation pending" flag that would block `vote_reshared`, and there is no "resharing in progress" guard that would block `vote_cancel_resharing`. The two paths race to their respective thresholds independently.

**Attack scenario:**

1. Governance threshold of old participants votes `vote_new_parameters`, transitioning the contract to `Resharing` with a new participant set.
2. Before resharing completes, the old participants discover the new participant set is no longer trusted (e.g., key material of a new node is suspected compromised).
3. Old participants begin broadcasting `vote_cancel_resharing` transactions.
4. The new participants — who are all online and motivated — have already completed the off-chain resharing protocol and immediately submit `vote_reshared` for each domain in rapid succession (potentially within the same block).
5. `vote_reshared` reaches unanimity among the new set before the old participants accumulate `previous_running_threshold` cancellation votes.
6. The contract transitions to `Running` with the new (untrusted) participant set holding the key shares. [4](#0-3) 

The `ResharingContractState` stores `cancellation_requests` as a plain `HashSet` with no effect on the `resharing_key` vote path. [5](#0-4) 

---

### Impact Explanation

Once `vote_reshared` completes for all domains, the contract irreversibly transitions to `Running` with the new participant set's `Keyset` and `ThresholdParameters`. [6](#0-5) 

The new (untrusted) participants now hold the only valid key shares for every domain. They can collectively produce threshold signatures for any payload submitted via `sign`, `request_app_private_key`, or `verify_foreign_transaction` — constituting **unauthorized threshold signature issuance**. The old participants' key shares are rendered obsolete by the epoch change encoded in the new `Keyset`. [7](#0-6) 

**Impact class:** Critical — unauthorized signing capability transferred to an untrusted participant set; equivalent to key-share compromise of the entire MPC network.

---

### Likelihood Explanation

- The new participants are a known, enumerable set; they can coordinate off-chain to submit `vote_reshared` transactions simultaneously.
- NEAR processes transactions within a block in submission order; all new participants submitting in the same block can complete resharing in a single block height.
- The old participants must coordinate across potentially geographically distributed nodes and submit at least `threshold` separate transactions — a slower process.
- The scenario is realistic whenever a governance resharing is initiated and a subset of new participants later becomes adversarial or is coerced before the resharing finalizes.

**Likelihood:** Medium — requires the new participant set to act adversarially and be fully online, but no privileged access or cryptographic break is needed beyond what the new participants already legitimately possess during the resharing window.

---

### Recommendation

1. **Cancellation lock:** Once any `vote_cancel_resharing` vote is recorded, set a boolean flag (e.g., `cancellation_initiated: bool`) on `ResharingContractState`. In `vote_reshared`, check this flag and return an error if it is set, preventing completion while cancellation is pending.

2. **Alternatively — priority for cancellation:** Require that `vote_reshared` can only finalize if `cancellation_requests` is empty, giving old participants a veto window.

3. **Document intentionality:** If this race is considered acceptable by design (analogous to the original report's resolution), add an explicit code comment to `vote_cancel_resharing` and `vote_reshared` stating that the two paths can race and that the first to reach its threshold wins, so operators must act quickly.

---

### Proof of Concept

```
State: Resharing
  previous_running_state.parameters.threshold = T  (e.g., 3 of 5 old participants)
  resharing_key.parameters.participants.len()  = N  (e.g., 4 new participants, all online)

Block B:
  new_participant_1 → vote_reshared(key_event_id)   [1/4 votes]
  new_participant_2 → vote_reshared(key_event_id)   [2/4 votes]
  new_participant_3 → vote_reshared(key_event_id)   [3/4 votes]
  new_participant_4 → vote_reshared(key_event_id)   [4/4 votes → resharing COMPLETE]
  
  old_participant_1 → vote_cancel_resharing()       [1/3 votes — TOO LATE]
  old_participant_2 → vote_cancel_resharing()       [2/3 votes — TOO LATE]
  old_participant_3 → vote_cancel_resharing()       [3/3 votes — TOO LATE]

Result: contract is now Running with new (untrusted) participant set.
        vote_cancel_resharing returns Err(ProtocolStateNotResharing) — state already changed.
```

The `vote_cancel_resharing` path has no effect once `vote_reshared` has already transitioned the state to `Running`. [8](#0-7) [9](#0-8)

### Citations

**File:** crates/contract/src/state/resharing.rs (L30-39)
```rust
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

**File:** crates/contract/src/state/resharing.rs (L121-164)
```rust
    pub fn vote_reshared(
        &mut self,
        key_event_id: KeyEventId,
    ) -> Result<Option<RunningContractState>, Error> {
        let previous_key = self.previous_keyset().domains[self.reshared_keys.len()].clone();
        if self
            .resharing_key
            .vote_success(&key_event_id, previous_key.key.clone())?
        {
            let new_key = KeyForDomain {
                domain_id: key_event_id.domain_id,
                attempt: key_event_id.attempt_id,
                key: previous_key.key,
            };
            self.reshared_keys.push(new_key);
            if let Some(next_domain) = self
                .previous_running_state
                .domains
                .get_domain_by_index(self.reshared_keys.len())
            {
                self.resharing_key = KeyEvent::new(
                    self.prospective_epoch_id(),
                    next_domain.clone(),
                    self.resharing_key.proposed_parameters().clone(),
                );
            } else {
                // Resharing complete: fold the per-domain threshold updates into
                // the registry and store the proposed parameters. The updates live
                // only on this resharing state, so they are structurally dropped
                // here rather than scrubbed off the stored parameters.
                let new_domains = self
                    .previous_running_state
                    .domains
                    .with_threshold_updates(&self.per_domain_thresholds)?;
                return Ok(Some(RunningContractState::new(
                    new_domains,
                    Keyset::new(self.prospective_epoch_id(), self.reshared_keys.clone()),
                    self.resharing_key.proposed_parameters().clone(),
                    self.previous_running_state.add_domains_votes.clone(),
                )));
            }
        }
        Ok(None)
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

**File:** crates/contract/src/state/key_event.rs (L128-133)
```rust
            VoteSuccessResult::Voted(count) => {
                if count == self.parameters.participants().len() {
                    Ok(true)
                } else {
                    Ok(false)
                }
```

**File:** crates/contract/src/state.rs (L87-97)
```rust
    pub fn vote_reshared(
        &mut self,
        key_event_id: KeyEventId,
    ) -> Result<Option<ProtocolContractState>, Error> {
        let ProtocolContractState::Resharing(state) = self else {
            return Err(InvalidState::ProtocolStateNotResharing.into());
        };
        state
            .vote_reshared(key_event_id)
            .map(|x| x.map(ProtocolContractState::Running))
    }
```

**File:** crates/contract/src/state.rs (L99-106)
```rust
    pub fn vote_cancel_resharing(&mut self) -> Result<Option<ProtocolContractState>, Error> {
        let ProtocolContractState::Resharing(state) = self else {
            return Err(InvalidState::ProtocolStateNotResharing.into());
        };
        state
            .vote_cancel_resharing()
            .map(|x| x.map(ProtocolContractState::Running))
    }
```
