### Title
Single Participant Can Unilaterally Trigger Resharing and Override `accept_requests` Safety Flag via `verify_tee()` — (File: crates/contract/src/lib.rs)

---

### Summary

The `verify_tee()` function is callable by any single participant without threshold consensus. It can unilaterally: (1) set `accept_requests = true`, re-enabling signing after a safety pause set by another participant's `verify_tee()` call; and (2) trigger a resharing that changes the participant set via `transition_to_resharing_no_checks()`, bypassing the normal threshold-vote requirement enforced by `vote_new_parameters()`. This is the direct analog of the external report's finding that a single admin can unpause a protocol paused by another admin.

---

### Finding Description

`verify_tee()` is gated only by `self.voter_or_panic()`, which requires the caller to be any single current participant — no threshold vote is required. [1](#0-0) 

When called, it evaluates the TEE attestation state and then unilaterally writes to two safety-critical contract fields:

**Path 1 — Re-enables signing (`accept_requests = true`):** [2](#0-1) 

**Path 2 — Disables signing (`accept_requests = false`):** [3](#0-2) 

**Path 3 — Triggers resharing without threshold checks:** [4](#0-3) 

The function name `transition_to_resharing_no_checks` is explicit: it bypasses the validation enforced by the normal governance path (`vote_new_parameters()`), which requires threshold-many participants to agree before the participant set changes. [5](#0-4) 

By contrast, the normal resharing path requires threshold votes: [6](#0-5) 

The `accept_requests` flag gates all three response endpoints (`respond`, `respond_ckd`, `respond_verify_foreign_tx`): [7](#0-6) [8](#0-7) [9](#0-8) 

---

### Impact Explanation

**Unauthorized participant-set change (Medium):** A single Byzantine participant (strictly below signing threshold) can call `verify_tee()` when one or more other participants have expired TEE attestations. This triggers `transition_to_resharing_no_checks()`, kicking out those participants and shrinking the active set — a participant-state change that normally requires threshold consensus via `vote_new_parameters()`. In a network of N=5, T=3, if two participants have expired attestations, the attacker reduces the set to 3 participants with threshold 3, concentrating signing power.

**Safety-flag override (Medium):** If Participant A calls `verify_tee()` and the result is `accept_requests = false` (too few valid attestations), Participant B can call `verify_tee()` again after submitting a fresh attestation for themselves. If the resulting TEE state now satisfies `TeeValidationResult::Full`, `accept_requests` is set back to `true` — a unilateral override of the safety pause, without threshold agreement. This is the direct analog of "an admin can unpause the protocol paused by another admin."

Both impacts fall under: *"participant-state or contract execution-flow manipulation that breaks production safety/accounting invariants."*

---

### Likelihood Explanation

**Medium.** The attacker must be a current participant (below signing threshold). The TEE attestation expiry is a realistic condition — attestations expire on a fixed schedule (every 7 days per the design), and the window between expiry and renewal is a predictable attack surface. No physical TEE attack, key leak, or threshold collusion is required. The attacker only needs their own valid attestation and knowledge of when other participants' attestations expire. [10](#0-9) 

---

### Recommendation

1. **Require threshold consensus to re-enable `accept_requests`.** Introduce a vote-based mechanism (analogous to `vote_new_parameters`) so that re-enabling signing after a safety pause requires threshold-many participants to agree, not just one.

2. **Separate the TEE-kickout resharing path from the single-caller path.** The `transition_to_resharing_no_checks()` call inside `verify_tee()` bypasses all governance checks. Either require threshold votes to confirm the kickout before transitioning, or at minimum require that the resharing proposal be countersigned by threshold-many participants before it takes effect.

3. **Emit an on-chain event when `accept_requests` changes**, so that the change is observable and auditable by all participants.

---

### Proof of Concept

**Scenario — Safety-flag override:**

1. Network: 5 participants, threshold 3. Two participants (P4, P5) have expired TEE attestations.
2. P1 calls `verify_tee()` → `TeeValidationResult::Partial` with only 3 valid → `accept_requests = false` (safety pause).
3. P4 and P5 renew their attestations via `submit_participant_info()`.
4. P2 (a compromised participant) calls `verify_tee()` → `TeeValidationResult::Full` → `accept_requests = true`.
5. The safety pause is overridden by a single participant, without threshold agreement.

**Scenario — Unauthorized resharing:**

1. Network: 5 participants, threshold 3. P4 and P5 have expired attestations.
2. P1 (compromised) calls `verify_tee()` → `TeeValidationResult::Partial` → `transition_to_resharing_no_checks()` fires.
3. Contract enters `Resharing` state, kicking out P4 and P5.
4. Remaining set: {P1, P2, P3}, threshold 3. P1 now holds 1/3 of signing power (up from 1/5), without any threshold vote authorizing this participant-set change. [11](#0-10)

### Citations

**File:** crates/contract/src/lib.rs (L298-302)
```rust
        // 4. Refuse the request if the contract is not currently accepting requests
        //    (e.g. because TEE validation has failed).
        if !self.accept_requests {
            env::panic_str(&TeeError::TeeValidationFailed.to_string())
        }
```

**File:** crates/contract/src/lib.rs (L579-581)
```rust
        if !self.accept_requests {
            return Err(TeeError::TeeValidationFailed.into());
        }
```

**File:** crates/contract/src/lib.rs (L662-664)
```rust
        if !self.accept_requests {
            return Err(TeeError::TeeValidationFailed.into());
        }
```

**File:** crates/contract/src/lib.rs (L711-713)
```rust
        if !self.accept_requests {
            return Err(TeeError::TeeValidationFailed.into());
        }
```

**File:** crates/contract/src/lib.rs (L1692-1696)
```rust
    #[handle_result]
    pub fn verify_tee(&mut self) -> Result<bool, Error> {
        log!("verify_tee: signer={}", env::signer_account_id());
        // Caller must be a participant (node or operator).
        self.voter_or_panic();
```

**File:** crates/contract/src/lib.rs (L1705-1765)
```rust
        match self.tee_state.reverify_and_cleanup_participants(
            current_params.participants(),
            tee_upgrade_deadline_duration,
        ) {
            TeeValidationResult::Full => {
                self.accept_requests = true;
                log!("All participants have an accepted Tee status");
                Ok(true)
            }
            TeeValidationResult::Partial {
                participants_with_valid_attestation,
            } => {
                let remaining = participants_with_valid_attestation.len();
                // Defense in depth: the surviving participant set must keep the full
                // threshold relation intact — the GovernanceThreshold must still sit
                // within its bounds for the smaller set (in particular it must not
                // exceed the remaining participant count or the upper cap) and must
                // remain at least every domain's ReconstructionThreshold (the kickout
                // keeps the existing per-domain thresholds). Otherwise we refuse and
                // wait for manual intervention.
                let max_reconstruction_threshold =
                    max_reconstruction_threshold(running_state.domains.domains());
                if let Err(err) = ThresholdParameters::validate_governance_against_reconstruction(
                    u64::try_from(remaining).expect("participant count fits in u64"),
                    current_params.threshold(),
                    max_reconstruction_threshold,
                ) {
                    log!(
                        "Kicking out participants with an invalid TEE status would break the threshold relation ({:?}); {} participants remain with a valid TEE status. This requires manual intervention. We will not accept new signature requests as a safety precaution.",
                        err,
                        remaining,
                    );
                    self.accept_requests = false;
                    return Ok(false);
                }

                // here, we set it to true, because at this point, we have at least `threshold`
                // number of participants with an accepted Tee status.
                self.accept_requests = true;

                // do we want to adjust the threshold?
                //let n_participants_new = new_participants.len();
                //let new_threshold = (3 * n_participants_new + 4) / 5; // minimum 60%
                //let new_threshold = new_threshold.max(2); // but also minimum 2
                let new_threshold = usize::try_from(current_params.threshold().value())
                    .expect("threshold value fits in usize");

                let threshold_parameters = ThresholdParameters::new(
                    participants_with_valid_attestation,
                    Threshold::new(new_threshold as u64),
                )
                .expect("Require valid threshold parameters"); // this should never happen.
                current_params.validate_incoming_proposal(&threshold_parameters)?;
                // This resharing only changes the participant set, so the
                // per-domain reconstruction-threshold updates map is empty.
                let proposed_parameters =
                    ProposedThresholdParameters::new(threshold_parameters, BTreeMap::new());
                let res = running_state.transition_to_resharing_no_checks(&proposed_parameters);
                if let Some(resharing) = res {
                    self.protocol_state = ProtocolContractState::Resharing(resharing);
                }
```
