### Title
Asymmetric Quorum Requirements Across Governance Operations Permanently Blocks Domain Addition and Resharing - (File: crates/contract/src/state/running.rs)

### Summary

The NEAR MPC contract defines a governance threshold of at least 60% of participants for approving proposals, but two critical governance operations — `vote_add_domains` and `vote_new_parameters` — require **100% of participants** to vote before any state transition occurs. A single participant below the signing threshold can permanently block domain additions and key resharing by simply not voting, while the governance threshold is never applied to these operations.

### Finding Description

The contract defines a `GovernanceThreshold` that must be at least 60% of the participant count: [1](#0-0) 

This threshold is correctly applied in `vote_update` for contract/config upgrades: [2](#0-1) 

However, `vote_add_domains` uses a completely different quorum — it requires **all** current participants to vote: [3](#0-2) 

Similarly, `process_new_parameters_proposal` (called by `vote_new_parameters`) requires **all** proposed participants to vote: [4](#0-3) 

The `ThresholdParametersVotes::vote()` function counts all stored votes for a proposal without filtering to any specific participant subset: [5](#0-4) 

The result is a direct analog to the AuraLocker M-03 bug: the denominator used for the transition check (`num_participants` or `new_num_participants`, i.e., 100%) is systematically larger than the governance threshold (60%), making these governance operations far harder to complete than the protocol's own security model requires.

### Impact Explanation

- **`vote_add_domains`**: Adding new signature domains (e.g., a new FROST/EdDSA domain) requires every single current participant to vote. If any one participant is offline, compromised, or adversarial, no new domain can ever be added.
- **`vote_new_parameters`**: Resharing keys to a new participant set requires every single proposed participant to vote. A single non-cooperating participant permanently blocks participant set changes.
- **Deadlock**: Since removing a non-cooperating participant also requires `vote_new_parameters` (which itself requires 100% participation), the network enters an unrecoverable governance deadlock if any participant stops cooperating.
- **`vote_update`** (contract/config upgrades) correctly uses the 60% governance threshold and is unaffected.

This breaks the production safety invariant that governance requires only the defined threshold (≥60%) of participants, not unanimous consent.

### Likelihood Explanation

Any single participant strictly below the signing threshold can trigger this condition by simply not calling `vote_add_domains` or `vote_new_parameters`. No key material, TEE access, or collusion is required. The attacker's entry path is the public `vote_add_domains` and `vote_new_parameters` contract methods — by abstaining from calling them, a participant blocks all other participants from completing the operation. This is reachable in production whenever the network needs to evolve (add a domain, rotate participants, or change thresholds).

### Recommendation

Replace the 100%-participation transition conditions with the governance threshold:

In `vote_add_domains`:
```rust
// Replace:
if self.parameters.participants().len() as u64 == n_votes {
// With:
if n_votes >= self.parameters.threshold().value() {
```

In `process_new_parameters_proposal`:
```rust
// Replace:
Ok(new_num_participants == n_votes)
// With:
Ok(n_votes >= self.parameters.threshold().value())
```

The `n_votes` count should also be filtered to only count votes from current participants (analogous to how `vote_update` filters `valid_votes_count` against `running_state.parameters.participants()`), to prevent stale or non-participant votes from contributing to quorum.

### Proof of Concept

Consider a network with 10 participants and a governance threshold of 6 (60%):

1. 9 participants call `vote_add_domains` with an identical domain proposal.
2. `n_votes` = 9, but `self.parameters.participants().len()` = 10.
3. The condition `10 == 9` is false; no transition occurs.
4. The 10th participant refuses to vote (or is offline).
5. The domain can never be added, despite 90% agreement — well above the 60% governance threshold.
6. The same participant's refusal to call `vote_new_parameters` also blocks any attempt to remove them from the participant set, creating a permanent deadlock.

The asymmetry is directly observable by comparing:
- `vote_update` transition: `valid_votes_count >= threshold.value()` (governance threshold) [6](#0-5) 
- `vote_add_domains` transition: `participants().len() == n_votes` (100%) [7](#0-6) 
- `vote_new_parameters` transition: `new_num_participants == n_votes` (100%) [8](#0-7)

### Citations

**File:** crates/contract/src/primitives/thresholds.rs (L13-17)
```rust
/// Lower bound on the GovernanceThreshold for `n` participants: 60% rounded up.
/// Single source of truth shared by validation and test fixtures.
pub(crate) fn governance_threshold_lower_relative_bound(n: u64) -> u64 {
    3_u64.saturating_mul(n).div_ceil(5)
}
```

**File:** crates/contract/src/lib.rs (L1363-1378)
```rust
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
```

**File:** crates/contract/src/state/running.rs (L205-207)
```rust
        // finally, vote.
        let n_votes = self.parameters_votes.vote(proposal, candidate);
        Ok(new_num_participants == n_votes)
```

**File:** crates/contract/src/state/running.rs (L236-237)
```rust
        let n_votes = self.add_domains_votes.vote(domains.clone(), &participant);
        if self.parameters.participants().len() as u64 == n_votes {
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
