### Title
Stale Measurement Votes from Removed Participants Satisfy Unanimity Check After Resharing — (`crates/contract/src/tee/measurements.rs`, `crates/contract/src/lib.rs`)

---

### Summary

`vote_remove_os_measurement` enforces unanimity by checking `votes >= threshold_parameters.participants().len()`. However, `count_votes` counts **all** entries in `vote_by_account` without filtering to current participants, and the stale-vote cleanup (`clean_tee_status`) is scheduled as a **detached promise** that executes asynchronously after resharing. In the window between resharing completion and `clean_tee_status` execution, stale votes from removed participants remain in storage and are counted toward the unanimity threshold, which has already shrunk to the new (smaller) participant set. A Byzantine participant who votes for removal before being removed can cause the unanimity check to pass with fewer than all current participants having consented.

---

### Finding Description

**Root cause — `count_votes` does not filter by current participants:** [1](#0-0) 

`count_votes` iterates over every entry in `vote_by_account` and counts those matching the action. There is no intersection with the live participant set.

**Root cause — `vote_remove_os_measurement` uses the new (smaller) participant count as the denominator:** [2](#0-1) 

After resharing, `threshold_parameters.participants().len()` reflects the new, smaller set. Stale votes from removed participants inflate the numerator while the denominator has already shrunk.

**Root cause — `clean_tee_status` is a detached promise, not an atomic cleanup:** [3](#0-2) 

The cleanup is `.detach()`ed — it is scheduled as a separate receipt and executes in a future block, not atomically with the resharing state transition. The actual stale-vote removal only happens when `clean_non_participant_votes` runs: [4](#0-3) 

**The race window:** Between the block that finalizes `vote_reshared` (updating `protocol_state` to the new participant set) and the block that processes the `clean_tee_status` receipt, any call to `vote_remove_os_measurement` operates with:
- Denominator = new (smaller) participant count
- Numerator = stale votes from removed participants + votes from current participants

---

### Impact Explanation

A Byzantine participant P votes to remove a legitimate OS measurement M1 before being removed via resharing. After resharing shrinks the participant set, P's stale vote persists in `vote_by_account`. If one or two current participants also vote for removal in the cleanup window, the stale vote from P makes up the difference to satisfy `votes >= total_participants`. The measurement is removed without unanimous consent from all current participants.

Nodes running M1 subsequently fail `re_verify` attestation checks, causing them to be rejected by the contract. If enough nodes are affected, the MPC network loses liveness. This breaks the production safety invariant that unanimity requires **all current participants** to consent to measurement removal.

Impact category: **Medium** — participant-state manipulation that breaks a production safety invariant (unanimity for measurement removal) without requiring network-level DoS or operator misconfiguration.

---

### Likelihood Explanation

The race window is narrow (one to a few blocks on NEAR), but it is real and deterministic — it exists on every resharing that shrinks the participant set. The attacker (P) does not need to act in the window; they only need to have voted before resharing. The trigger is any current participant voting for removal in the window, which can happen naturally or be coordinated. The scenario requires a Byzantine participant who is about to be removed, plus at least one other participant voting for the same removal — a realistic condition during governance disputes or coordinated attacks.

---

### Recommendation

Filter stale votes **at the point of counting**, not only at cleanup time. In `vote_remove_os_measurement`, replace the raw `count_votes` result with a filtered count that only considers votes from current participants:

```rust
// Instead of:
let votes = self.tee_state.vote_measurement(action, &participant);
let total_participants = threshold_parameters.participants().len() as u64;
if votes >= total_participants {

// Use:
let _ = self.tee_state.vote_measurement(action, &participant);
let current_participants = threshold_parameters.participants();
let votes = self.tee_state
    .measurement_votes
    .count_votes_for_current_participants(&action, current_participants);
let total_participants = current_participants.len() as u64;
if votes >= total_participants {
```

Alternatively, apply `get_remaining_votes` eagerly at the start of `vote_remove_os_measurement` (and its `vote_remove_launcher_hash` counterpart) to prune stale entries before counting. The existing `get_remaining_votes` method already implements the correct filtering logic: [5](#0-4) 

Note: the comment in `vote_reshared` acknowledges this pattern for `vote_update` — *"MpcContract::vote_update uses filtering to ensure correctness even if this cleanup fails"* — but the same defensive filtering was not applied to measurement votes. [6](#0-5) 

---

### Proof of Concept

```
Setup: N=5, old set = {P, A, B, C, D}, threshold=3, two measurements M1 and M2 in allowed list.

Step 1: P (Byzantine, knowing they will be removed) and A vote Remove(M1).
        vote_by_account = {P→Remove(M1), A→Remove(M1)}
        count_votes = 2, total = 5 → no removal.

Step 2: Resharing removes P, B, C, D; adds NEW1, NEW2.
        New participant set = {A, NEW1, NEW2} (size = 3).
        protocol_state updated atomically.
        clean_tee_status receipt scheduled but NOT yet executed.

Step 3: NEW1 calls vote_remove_os_measurement(M1) in the same or next block,
        before clean_tee_status executes.
        vote_by_account = {P→Remove(M1)[stale], A→Remove(M1), NEW1→Remove(M1)}
        count_votes = 3 (counts stale P entry)
        total_participants = 3 (new set size)
        3 >= 3 → removal triggers.

Result: M1 removed. NEW2 never voted. Unanimity invariant violated.
        Nodes running M1 fail re_verify; attestation failures ensue.
```

### Citations

**File:** crates/contract/src/tee/measurements.rs (L58-66)
```rust
    fn count_votes(&self, action: &MeasurementVoteAction) -> u64 {
        u64::try_from(
            self.vote_by_account
                .values()
                .filter(|a| *a == action)
                .count(),
        )
        .expect("participant count should not overflow u64")
    }
```

**File:** crates/contract/src/tee/measurements.rs (L74-86)
```rust
    pub fn get_remaining_votes(&self, participants: &Participants) -> Self {
        let remaining = self
            .vote_by_account
            .iter()
            .filter(|(participant_id, _)| {
                participants.is_participant_given_participant_id(&participant_id.get())
            })
            .map(|(participant_id, vote)| (participant_id.clone(), vote.clone()))
            .collect();
        MeasurementVotes {
            vote_by_account: remaining,
        }
    }
```

**File:** crates/contract/src/lib.rs (L1175-1177)
```rust
            // Spawn a promise to clean up votes from non-participants.
            // Note: MpcContract::vote_update uses filtering to ensure correctness even if this cleanup fails.
            Promise::new(env::current_account_id())
```

**File:** crates/contract/src/lib.rs (L1185-1193)
```rust
            // Spawn a promise to drop votes cast by non-participants.
            Promise::new(env::current_account_id())
                .function_call(
                    method_names::CLEAN_TEE_STATUS.to_string(),
                    vec![],
                    NearToken::from_yoctonear(0),
                    Gas::from_tgas(self.config.clean_tee_status_tera_gas),
                )
                .detach();
```

**File:** crates/contract/src/lib.rs (L1544-1546)
```rust
        // Removal requires ALL participants to vote
        let total_participants = threshold_parameters.participants().len() as u64;
        if votes >= total_participants {
```

**File:** crates/contract/src/tee/tee_state.rs (L396-400)
```rust
    pub fn clean_non_participant_votes(&mut self, participants: &Participants) {
        self.votes = self.votes.get_remaining_votes(participants);
        self.launcher_votes = self.launcher_votes.get_remaining_votes(participants);
        self.measurement_votes = self.measurement_votes.get_remaining_votes(participants);
    }
```
