### Title
Participants with Expired TEE Attestations Have No On-Chain Incentive to Renew, Creating a Permanent Network Halt When Valid Participants Fall Below Threshold - (File: `crates/contract/src/lib.rs`)

---

### Summary

When `verify_tee()` is called and the count of participants with valid TEE attestations falls strictly below the governance threshold, the contract sets `accept_requests = false` and logs that "manual intervention" is required. However, the participants whose expired/invalid attestations caused the halt have no on-chain incentive to renew them: renewing triggers their removal via an automatic resharing. Meanwhile, the remaining valid participants cannot unilaterally reach the governance threshold to execute a `vote_update` contract upgrade or initiate `vote_new_parameters` resharing without the invalid participants' cooperation. This creates a governance deadlock structurally identical to the sNOTE finding: the parties who control the recovery mechanism are the same parties who would be harmed by executing it.

---

### Finding Description

**Step 1 — How the halt is triggered**

`verify_tee()` re-evaluates all current participants' TEE attestations. When the result is `TeeValidationResult::Partial` and the surviving valid count is fewer than the governance threshold, `validate_governance_against_reconstruction` fails and the contract sets `accept_requests = false`: [1](#0-0) 

The log message explicitly acknowledges the problem: *"This requires manual intervention."*

**Step 2 — The only on-chain recovery path**

The only way to restore `accept_requests = true` is to call `verify_tee()` again after enough participants have renewed their attestations (via `submit_participant_info`), so that the valid count reaches or exceeds the threshold. At that point `verify_tee()` either returns `TeeValidationResult::Full` (all valid → `accept_requests = true`) or `TeeValidationResult::Partial` with enough survivors to trigger resharing. [2](#0-1) [3](#0-2) 

**Step 3 — The incentive misalignment**

Renewing an attestation via `submit_participant_info` causes the participant to appear valid again. The next `verify_tee()` call then triggers resharing that *excludes* the previously-invalid participants from the new epoch. So the invalid participants face a binary choice:

- **Renew** → valid again → `verify_tee()` triggers resharing → they are kicked out of the participant set permanently.
- **Do not renew** → network stays halted → they remain in the participant set (even though signing is frozen).

Participants who believe they can be re-admitted in a future `vote_new_parameters` round will rationally choose not to renew.

**Step 4 — Valid participants cannot force recovery**

The valid participants (count = `V < T`, where `T` is the governance threshold) cannot bypass the invalid participants because:

1. **`vote_update` (contract upgrade)** requires `T` votes from current participants. With only `V < T` valid participants willing to vote, the threshold is unreachable unless the invalid participants cooperate. [4](#0-3) 

2. **`vote_new_parameters` (resharing)** requires ALL proposed new participants to vote, and `validate_incoming_proposal` enforces that the new set must contain at least `T` participants from the current epoch. With only `V < T` valid participants, this check fails with `InsufficientOldParticipants`. [5](#0-4) 

3. **`verify_tee()` itself** cannot help: with `V < T` valid participants, it simply re-sets `accept_requests = false` on every call. [6](#0-5) 

---

### Impact Explanation

Once `accept_requests = false` is set and the deadlock condition holds (`V < T`), the MPC network is permanently halted:

- All new `sign`, `request_app_private_key`, and `verify_foreign_transaction` calls are rejected with `TeeValidationFailed`.
- All `respond` / `respond_ckd` / `respond_verify_foreign_tx` calls are also rejected, so any in-flight yield-resume requests are permanently unresolvable.
- Users whose cross-chain transactions depend on MPC signatures cannot complete them, effectively freezing any funds gated behind those signatures.

This matches the **Medium** allowed impact: *"request-lifecycle or contract execution-flow manipulation that breaks production safety/accounting invariants."*

---

### Likelihood Explanation

TEE attestations expire naturally (governed by `tee_upgrade_deadline_duration_seconds`). If a coordinated or coincidental wave of attestation expiries leaves fewer than `T` valid participants before any of them renew, a single call to `verify_tee()` by any participant triggers the halt. Because the governance threshold is at least 60% of participants, only ~40%+ of participants need to have expired attestations simultaneously. A single Byzantine participant below the signing threshold can also deliberately delay renewal to extend the halted period once the condition is met.

---

### Recommendation

1. **Decouple recovery from removal**: Introduce a time-bounded "grace window" during which participants with expired attestations can renew without immediately triggering resharing. Only after the grace window expires should they be removed.

2. **Allow valid-participant-only resharing below threshold**: Add a special `emergency_reshare` path that requires only `V` votes (the surviving valid count) when `accept_requests = false`, bypassing the `InsufficientOldParticipants` guard. This removes the invalid participants' veto over recovery.

3. **Programmatic attestation renewal incentive**: Consider slashing or fee-withholding mechanisms that penalize participants who fail to renew attestations within the grace window, aligning their incentives with network health.

---

### Proof of Concept

**Scenario**: 5 participants, governance threshold = 3 (60%).

1. Participants P4 and P5 allow their TEE attestations to expire (or deliberately do not renew).
2. Any participant calls `verify_tee()`.
3. `reverify_and_cleanup_participants` returns `Partial { participants_with_valid_attestation: [P1, P2, P3] }` — count = 3 = threshold.

   → This case *does* trigger resharing (3 ≥ 3). The deadlock requires count < threshold.

**Adjusted scenario**: 5 participants, threshold = 4 (80%, valid under the ≤100% upper cap).

1. P3, P4, P5 let attestations expire. Valid count = 2 < 4.
2. Any participant calls `verify_tee()`.
3. `validate_governance_against_reconstruction(2, 4, ...)` fails → `accept_requests = false`.
4. P1 and P2 propose a `vote_update` contract fix. They cast 2 votes. Threshold = 4. Update never executes.
5. P1 and P2 call `vote_new_parameters` proposing {P1, P2}. `validate_incoming_proposal` requires ≥ 4 old participants in the new set. Fails with `InsufficientOldParticipants`.
6. P3/P4/P5 refuse to renew (renewal → removal via resharing).
7. Network is permanently halted. [7](#0-6) [8](#0-7) [5](#0-4)

### Citations

**File:** crates/contract/src/lib.rs (L1343-1388)
```rust
    pub fn vote_update(&mut self, id: UpdateId) -> Result<bool, Error> {
        log!(
            "vote_update: signer={}, id={:?}",
            env::signer_account_id(),
            id,
        );

        let ProtocolContractState::Running(running_state) = &self.protocol_state else {
            env::panic_str("protocol must be in running state");
        };

        let threshold = self.threshold()?;

        let voter = self.voter_or_panic();
        if self.proposed_updates.vote(&id, voter).is_none() {
            return Err(InvalidParameters::UpdateNotFound.into());
        }

        // Filter votes to only count current participants voting for this specific update.
        // This ensures correctness even if the cleanup promise in MpcContract::vote_reshared() fails.
        let valid_votes_count = running_state
            .parameters
            .participants()
            .participants()
            .iter()
            .filter(|(account_id, _, _)| {
                self.proposed_updates
                    .vote_by_participant
                    .get(account_id)
                    .is_some_and(|voted_id| *voted_id == id)
            })
            .count();

        // Not enough votes from current participants, wait for more.
        if (valid_votes_count as u64) < threshold.value() {
            return Ok(false);
        }

        let update_gas_deposit = Gas::from_tgas(self.config.contract_upgrade_deposit_tera_gas);

        let Some(_promise) = self.proposed_updates.do_update(&id, update_gas_deposit) else {
            return Err(InvalidParameters::UpdateNotFound.into());
        };

        Ok(true)
    }
```

**File:** crates/contract/src/lib.rs (L1693-1770)
```rust
    pub fn verify_tee(&mut self) -> Result<bool, Error> {
        log!("verify_tee: signer={}", env::signer_account_id());
        // Caller must be a participant (node or operator).
        self.voter_or_panic();
        let ProtocolContractState::Running(running_state) = &mut self.protocol_state else {
            return Err(InvalidState::ProtocolStateNotRunning.into());
        };
        let current_params = running_state.parameters.clone();

        let tee_upgrade_deadline_duration =
            Duration::from_secs(self.config.tee_upgrade_deadline_duration_seconds);

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

                Ok(true)
            }
        }
    }
```

**File:** crates/contract/src/state/running.rs (L143-207)
```rust
    pub(super) fn process_new_parameters_proposal(
        &mut self,
        proposal: &ProposedThresholdParameters,
    ) -> Result<bool, Error> {
        // ensure the proposal is valid against the current parameters
        self.parameters
            .validate_incoming_proposal(proposal.parameters())?;

        // Validate effective per-domain thresholds (updates override, absent
        // domains keep theirs) against the proposed participant count.
        let new_num_participants =
            u64::try_from(proposal.participants().len()).expect("participant count fits in u64");
        let threshold_updates = proposal.per_domain_thresholds();
        // Reject unknown domain IDs: the loop below iterates existing domains, so
        // an unknown ID would otherwise be silently ignored here (it's caught at
        // the resharing transition, but we fail fast at vote acceptance).
        for id in threshold_updates.keys() {
            if self.domains.get_domain_by_domain_id(*id).is_none() {
                return Err(DomainError::UnknownDomainInProposal { domain_id: *id }.into());
            }
        }
        let effective_domains: Vec<DomainConfig> = self
            .domains
            .domains()
            .iter()
            .map(|domain| {
                let effective_threshold = threshold_updates
                    .get(&domain.id)
                    .copied()
                    .unwrap_or(domain.reconstruction_threshold);
                DomainConfig {
                    reconstruction_threshold: effective_threshold,
                    ..domain.clone()
                }
            })
            .collect();
        for domain in &effective_domains {
            validate_domain_threshold(domain, new_num_participants)?;
        }

        // The GovernanceThreshold must dominate every domain's effective ReconstructionThreshold;
        // enforced here so the state transition is self-contained (single source of truth).
        ThresholdParameters::validate_governance_against_reconstruction(
            new_num_participants,
            proposal.threshold(),
            max_reconstruction_threshold(&effective_domains),
        )?;

        // ensure the signer is a proposed participant
        let candidate = AuthenticatedAccountId::new(proposal.participants())?;

        // If the signer is not a participant of the current epoch, they can only vote after
        // `threshold` participant of the current epoch have casted their vote to admit them.
        if AuthenticatedAccountId::new(self.parameters.participants()).is_err() {
            let n_votes = self
                .parameters_votes
                .n_votes(proposal, self.parameters.participants());
            if n_votes < self.parameters.threshold().value() {
                return Err(VoteError::VoterPending.into());
            }
        }

        // finally, vote.
        let n_votes = self.parameters_votes.vote(proposal, candidate);
        Ok(new_num_participants == n_votes)
```
