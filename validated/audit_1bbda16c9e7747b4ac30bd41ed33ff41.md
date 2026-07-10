### Title
Stale Removed-Participant Vote Counted Toward Measurement Threshold During Resharing Window — (`crates/contract/src/tee/measurements.rs`, `crates/contract/src/lib.rs`)

---

### Summary

`MeasurementVotes::count_votes` counts every entry in `vote_by_account` without filtering by the current participant set. After resharing removes a participant, their vote persists in storage until the detached `clean_tee_status` promise executes in a separate NEAR transaction. During that window, T-1 Byzantine current participants can vote for a malicious measurement, and the stale ex-participant vote inflates the count to T, causing the threshold check to pass with only T-1 legitimate current-participant votes.

---

### Finding Description

**Root cause — `count_votes` is participant-unaware:** [1](#0-0) 

`count_votes` iterates `vote_by_account.values()` and counts all entries matching the action. It has no knowledge of who is currently a participant.

**`vote_add_os_measurement` authenticates only the *current* caller, not existing votes:** [2](#0-1) 

`AuthenticatedParticipantId::new(threshold_parameters.participants())` verifies that the *signer of the current call* is in the post-resharing participant set. It does not purge or re-validate votes already stored in `measurement_votes.vote_by_account` from participants who were removed.

**Cleanup is deferred and detached — not atomic with the state transition:** [3](#0-2) 

`clean_tee_status` is spawned as a `.detach()`-ed promise. On NEAR, detached promises execute in a separate receipt/transaction. Between the `vote_reshared` transaction completing and the `clean_tee_status` receipt executing, the contract is in Running state with the new participant set, but `measurement_votes.vote_by_account` still contains the removed participant's vote.

**`clean_tee_status` / `clean_non_participant_votes` is the intended fix — but it runs too late:** [4](#0-3) 

`get_remaining_votes` correctly filters to current participants, but it only runs after the detached promise is scheduled and executed, leaving a window of at least one block.

---

### Impact Explanation

An attacker who controls a participant being removed (P0) plus T-1 current participants (below the signing threshold T) can add an arbitrary `ContractExpectedMeasurements` to `AllowedMeasurements`. Once a malicious measurement is whitelisted, a node running unapproved OS/firmware passes attestation, is accepted as a participant, and can participate in MPC signing rounds. This is an **attestation authorization bypass** enabling unauthorized threshold signature issuance.

---

### Likelihood Explanation

- Requires 1 participant being removed + T-1 Byzantine current participants (total Byzantine count = T-1, strictly below signing threshold).
- The window is at least one NEAR block (the detached promise receipt is scheduled after the `vote_reshared` transaction). Resharing is a known, observable on-chain event, so the attacker can time their votes precisely.
- No special privileges, no validator collusion, no key leakage required — only contract calls.

---

### Recommendation

Replace the deferred cleanup with an **inline filter** at vote-counting time. In `vote_add_os_measurement`, pass the current `Participants` into the vote/count logic and use `get_remaining_votes` (or an equivalent inline filter) before comparing against the threshold:

```rust
// In vote_add_os_measurement, after getting threshold_parameters:
let participants = threshold_parameters.participants();
let participant = AuthenticatedParticipantId::new(participants)?;
let action = MeasurementVoteAction::Add(measurement.clone());
self.tee_state.vote_measurement(action.clone(), &participant);

// Count only current-participant votes:
let current_votes = self.tee_state
    .measurement_votes
    .get_remaining_votes(participants)
    .count_votes(&action);

if current_votes >= self.threshold()?.value() { ... }
```

Alternatively, synchronously call `clean_non_participant_votes` inside `vote_reshared` before returning, rather than relying on a detached promise.

---

### Proof of Concept

Deterministic unit test (no sandbox needed):

1. Initialize contract: N=5, T=3, participants P0–P4.
2. P0 calls `vote_add_os_measurement(malicious_M)` → `count_votes` = 1, below threshold, nothing added.
3. Simulate resharing: mutate `protocol_state` to Running with new participant set {P1, P2, P3, P4}, T=3. Do **not** call `clean_tee_status` (simulating the detached-promise window).
4. P1 calls `vote_add_os_measurement(malicious_M)` → `count_votes` = 2 (P0 stale + P1).
5. P2 calls `vote_add_os_measurement(malicious_M)` → `count_votes` = 3 (P0 stale + P1 + P2) ≥ T=3 → `malicious_M` added to `AllowedMeasurements`.
6. Assert `allowed_os_measurements()` contains `malicious_M` despite only 2 current-participant votes.

The invariant "only current participants' votes count toward threshold" is broken.

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

**File:** crates/contract/src/lib.rs (L1510-1516)
```rust
        let threshold_parameters = self.protocol_state.threshold_parameters_or_panic();

        let participant = AuthenticatedParticipantId::new(threshold_parameters.participants())?;
        let action = MeasurementVoteAction::Add(measurement.clone());
        let votes = self.tee_state.vote_measurement(action, &participant);

        if votes >= self.threshold()?.value() {
```

**File:** crates/contract/src/tee/tee_state.rs (L396-400)
```rust
    pub fn clean_non_participant_votes(&mut self, participants: &Participants) {
        self.votes = self.votes.get_remaining_votes(participants);
        self.launcher_votes = self.launcher_votes.get_remaining_votes(participants);
        self.measurement_votes = self.measurement_votes.get_remaining_votes(participants);
    }
```
