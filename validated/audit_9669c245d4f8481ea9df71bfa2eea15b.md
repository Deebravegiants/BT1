### Title
Stale Re-Proposal Votes Persist After Resharing Cancellation, Enabling Governance Threshold Bypass - (File: `crates/contract/src/state/resharing.rs`)

### Summary

When a resharing is cancelled via `vote_cancel_resharing`, the `previous_running_state` is returned directly to the `Running` phase. If participants had cast re-proposal votes (via `vote_new_parameters` on the resharing state) before cancellation, those votes remain in `previous_running_state.parameters_votes`. Back in the `Running` state, these stale votes count toward the consensus check for a new resharing proposal, allowing resharing to be triggered with fewer fresh participant votes than the protocol requires.

---

### Finding Description

The vulnerability class from H-06 is **accumulated state not settled before a parameter update takes effect when an entity is removed and re-added**. The NEAR MPC analog is: **accumulated vote state from a cancelled resharing's re-proposal is not cleared before the contract returns to the Running state**, allowing a subsequent resharing to be triggered without requiring all proposed participants to freshly consent.

**Root cause — `vote_cancel_resharing` does not clear `parameters_votes`:** [1](#0-0) 

```rust
let running_state = if threshold_cancellation_votes_reached {
    let mut previous_running_state = self.previous_running_state.clone();
    let prospective_epoch_id = self.prospective_epoch_id();
    previous_running_state.previously_cancelled_resharing_epoch_id =
        Some(prospective_epoch_id);
    Some(previous_running_state)
} else {
    None
};
```

Only `previously_cancelled_resharing_epoch_id` is updated. The `parameters_votes` field — a `ThresholdParametersVotes` — is returned as-is.

**How `parameters_votes` gets populated during resharing:**

When participants call `vote_new_parameters` on the resharing state, it delegates directly to `self.previous_running_state.process_new_parameters_proposal(proposal)`: [2](#0-1) 

This mutates `previous_running_state.parameters_votes` in place. Those votes survive the cancellation.

**How stale votes count in the restored Running state:**

Back in `RunningContractState`, `process_new_parameters_proposal` tallies votes with: [3](#0-2) 

```rust
let n_votes = self.parameters_votes.vote(proposal, candidate);
Ok(new_num_participants == n_votes)
```

`ThresholdParametersVotes::vote` counts **all** stored entries matching the proposal, with no epoch guard: [4](#0-3) 

Stale votes from the resharing re-proposal are indistinguishable from fresh votes.

**The "pending voter" admission check is also bypassed by stale votes:** [5](#0-4) 

```rust
if AuthenticatedAccountId::new(self.parameters.participants()).is_err() {
    let n_votes = self
        .parameters_votes
        .n_votes(proposal, self.parameters.participants());
    if n_votes < self.parameters.threshold().value() {
        return Err(VoteError::VoterPending.into());
    }
}
```

A new participant `E` (not in the current epoch) must wait for `threshold` current-participant votes before voting. Stale votes from current participants A and B (cast during resharing re-proposal) satisfy this check immediately, letting E vote without any fresh endorsement.

---

### Impact Explanation

The governance invariant is that **all** proposed participants must independently and freshly vote to trigger resharing. With stale votes persisting after cancellation, a single new participant `E` can trigger resharing to a proposal `P2` that includes `E`, using only their own fresh vote plus the stale votes of current participants who may have since changed their intent (e.g., they voted to cancel the resharing). This breaks the participant-state and contract execution-flow safety invariant without requiring any network-level DoS or privileged access.

**Impact: Medium** — participant-state and governance-flow manipulation that breaks the production safety invariant requiring unanimous fresh consent for resharing.

---

### Likelihood Explanation

The scenario requires: (1) a resharing to be initiated, (2) at least one re-proposal vote cast during resharing, and (3) the resharing to be subsequently cancelled. All three steps are normal protocol operations reachable by unprivileged participants. A malicious prospective participant `E` included in a re-proposal `P2` can monitor on-chain state and exploit the stale votes immediately after cancellation by casting a single vote. No collusion above the signing threshold is required.

---

### Recommendation

In `vote_cancel_resharing`, clear `parameters_votes` before returning the restored running state:

```rust
let mut previous_running_state = self.previous_running_state.clone();
previous_running_state.parameters_votes = ThresholdParametersVotes::default(); // add this
previous_running_state.previously_cancelled_resharing_epoch_id = Some(prospective_epoch_id);
Some(previous_running_state)
```

This mirrors the pattern already used in `RunningContractState::new`, which always initialises `parameters_votes` to `default()`: [6](#0-5) 

---

### Proof of Concept

1. Running state: participants `{A, B, C}`, governance threshold `2`, proposed participants for P2 = `{A, B, E}`.
2. All three vote for proposal P1 → resharing starts. `previous_running_state.parameters_votes` is empty (created via `RunningContractState::new`).
3. During resharing, A and B call `vote_new_parameters` with re-proposal P2. `previous_running_state.parameters_votes` now contains A→P2 and B→P2.
4. A and B (or any two current participants) call `vote_cancel_resharing`. Threshold (2) is reached; `vote_cancel_resharing` returns `previous_running_state` with A→P2 and B→P2 still in `parameters_votes`.
5. Contract is now in Running state with stale votes `{A→P2, B→P2}` in `parameters_votes`.
6. E (not a current participant) calls `vote_new_parameters` with P2. The pending-voter check queries `n_votes(P2, {A,B,C})` = 2 ≥ threshold 2 → E is admitted immediately.
7. E's vote is recorded; total count = 3 = `len(P2.participants)` → resharing to P2 is triggered.

Resharing to P2 was triggered with only **one fresh vote** (E's), bypassing the requirement for fresh consent from A and B, who had already voted to cancel the resharing. [7](#0-6) [8](#0-7) [4](#0-3)

### Citations

**File:** crates/contract/src/state/resharing.rs (L56-94)
```rust
    pub fn vote_new_parameters(
        &mut self,
        prospective_epoch_id: EpochId,
        proposal: &ProposedThresholdParameters,
    ) -> Result<Option<ResharingContractState>, Error> {
        let expected_prospective_epoch_id = self.prospective_epoch_id().next();
        if prospective_epoch_id != expected_prospective_epoch_id {
            return Err(InvalidParameters::EpochMismatch {
                expected: expected_prospective_epoch_id,
                provided: prospective_epoch_id,
            }
            .into());
        }
        if self
            .previous_running_state
            .process_new_parameters_proposal(proposal)?
        {
            return Ok(Some(ResharingContractState {
                previous_running_state: RunningContractState::new(
                    self.previous_running_state.domains.clone(),
                    self.previous_running_state.keyset.clone(),
                    self.previous_running_state.parameters.clone(),
                    self.previous_running_state.add_domains_votes.clone(),
                ),
                reshared_keys: Vec::new(),
                resharing_key: KeyEvent::new(
                    self.prospective_epoch_id().next(),
                    self.previous_running_state
                        .domains
                        .get_domain_by_index(0)
                        .unwrap()
                        .clone(),
                    proposal.parameters().clone(),
                ),
                cancellation_requests: HashSet::new(),
                per_domain_thresholds: proposal.per_domain_thresholds().clone(),
            }));
        }
        Ok(None)
```

**File:** crates/contract/src/state/resharing.rs (L184-193)
```rust
        let running_state = if threshold_cancellation_votes_reached {
            let mut previous_running_state = self.previous_running_state.clone();
            let prospective_epoch_id = self.prospective_epoch_id();
            previous_running_state.previously_cancelled_resharing_epoch_id =
                Some(prospective_epoch_id);

            Some(previous_running_state)
        } else {
            None
        };
```

**File:** crates/contract/src/state/running.rs (L56-63)
```rust
        RunningContractState {
            domains,
            keyset,
            parameters,
            parameters_votes: ThresholdParametersVotes::default(),
            add_domains_votes: remaining_add_domain_votes,
            previously_cancelled_resharing_epoch_id: None,
        }
```

**File:** crates/contract/src/state/running.rs (L143-208)
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
    }
```

**File:** crates/contract/src/primitives/threshold_votes.rs (L41-60)
```rust
    pub fn vote(
        &mut self,
        proposal: &ProposedThresholdParameters,
        participant: AuthenticatedAccountId,
    ) -> u64 {
        if self
            .proposal_by_account
            .insert(participant, proposal.clone())
            .is_some()
        {
            log!("removed one vote for signer");
        }
        u64::try_from(
            self.proposal_by_account
                .values()
                .filter(|&prop| prop == proposal)
                .count(),
        )
        .expect("usize should never fail to convert on u64 on wasm32")
    }
```
