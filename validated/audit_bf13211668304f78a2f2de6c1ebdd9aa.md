### Title
Single Participant Can Force Resharing or Halt Signing via `verify_tee` Without Threshold Authorization - (File: `crates/contract/src/lib.rs`)

---

### Summary
The `verify_tee` function is callable by any single current participant and can unilaterally halt all signature-request acceptance or force a participant resharing — both critical protocol-state mutations — without requiring a threshold vote. This is the direct analog of the "overprivileged owner" pattern: a single privileged actor can make changes that should require multi-party authorization.

---

### Finding Description

`verify_tee` (lib.rs line 1692) is guarded only by `voter_or_panic()`, which requires the caller to be **any one** current participant — not a threshold of them. [1](#0-0) 

When called, it invokes `reverify_and_cleanup_participants` on the stored TEE state. If the result is `TeeValidationResult::Partial` (one or more participants have expired or invalid attestations — a routine operational condition), the function takes two unilateral actions:

**Action 1 — Halt all signing** (if the remaining valid-attestation set would break the threshold relation): [2](#0-1) 

**Action 2 — Force a resharing that removes participants**, bypassing the normal `vote_new_parameters` threshold-vote path: [3](#0-2) 

The function name `transition_to_resharing_no_checks` is explicit: the normal vote-accumulation gate is skipped entirely. The ordinary governance path for changing the participant set requires threshold votes via `vote_new_parameters`: [4](#0-3) 

No equivalent threshold gate exists on the `verify_tee` path.

---

### Impact Explanation

**Medium — participant-state and contract execution-flow manipulation that breaks production safety/accounting invariants.**

- A single participant can force a resharing that permanently removes other participants from the active set, without any other participant consenting. This changes who holds key shares and who can authorize future signatures.
- A single participant can set `accept_requests = false`, blocking all pending and future signature requests across every foreign chain the MPC network serves, until a subsequent `verify_tee` call (or manual intervention) restores the flag.
- Both outcomes are irreversible in the short term: a resharing cannot be undone without another full resharing cycle; a halted network cannot resume until a participant calls `verify_tee` again and the TEE state has recovered.

---

### Likelihood Explanation

**Medium.**

- TEE attestation expiry is a routine operational event (governed by `tee_upgrade_deadline_duration_seconds` in the config). Any participant can observe on-chain TEE state and time a `verify_tee` call to coincide with another participant's attestation expiring.
- The call requires no special setup beyond being a current participant — no deposit, no cross-contract call, no elevated key.
- A participant who is being voted out (e.g., via `vote_new_parameters`) has an incentive to call `verify_tee` first to force a resharing on their own terms, potentially removing the participants who were voting against them.

---

### Recommendation

1. **Require threshold votes to trigger resharing via `verify_tee`.** Accumulate `verify_tee` calls from multiple participants before acting; only proceed when at least `threshold` participants agree the TEE state is invalid.
2. **Separate the read (TEE status check) from the write (resharing trigger).** Let `verify_tee` return the validation result without mutating protocol state; require a separate threshold-gated call to act on it.
3. **Apply a timelock** between detecting invalid TEE state and executing the resharing, giving other participants time to renew attestations or contest the action.

---

### Proof of Concept

1. Participant A's TEE attestation expires (normal operational event after `tee_upgrade_deadline_duration_seconds`).
2. Malicious participant B calls `verify_tee()` — a single transaction, no deposit, no co-signers.
3. `reverify_and_cleanup_participants` returns `TeeValidationResult::Partial` with only participants who still have valid attestations.
4. `verify_tee` constructs new `ThresholdParameters` excluding participant A and calls `transition_to_resharing_no_checks` — bypassing the `vote_new_parameters` threshold gate entirely.
5. The contract transitions to `ProtocolContractState::Resharing`, removing participant A from the active set without any other participant's consent.
6. If the remaining valid-attestation count is insufficient to satisfy the threshold relation, `accept_requests` is additionally set to `false`, halting all signing for all users. [5](#0-4)

### Citations

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

**File:** crates/contract/src/lib.rs (L1886-1891)
```rust
            .get_mut()
            .remove_stale_configs(&active_tls_keys);

        self.foreign_chains
            .get_mut()
            .rpc_whitelist
```
