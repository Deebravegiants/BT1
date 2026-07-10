Now I have enough information to make a definitive assessment. Let me trace the exact code path.

### Title
Stale `add_domains_votes` carry-over after resharing allows threshold-many participants to trigger unauthorized domain addition — (`crates/contract/src/state/resharing.rs`)

---

### Summary

When resharing completes, `vote_reshared` passes the previous running state's `add_domains_votes` directly into `RunningContractState::new`. That constructor only filters votes by current participant membership — it does not reset them. If the resharing was specifically designed to remove the non-voters, the surviving vote count equals the new (smaller) participant count, and a single subsequent `vote_add_domains` call satisfies the all-participants quorum and transitions to `Initializing`.

---

### Finding Description

**Root cause — `vote_reshared` in `resharing.rs`:** [1](#0-0) 

The call passes `self.previous_running_state.add_domains_votes.clone()` verbatim into `RunningContractState::new`.

**`RunningContractState::new` only filters, never resets:** [2](#0-1) 

`get_remaining_votes` keeps every vote whose `ParticipantId` still exists in the new participant set: [3](#0-2) 

**`vote_add_domains` quorum check requires ALL participants:** [4](#0-3) 

The quorum is `participants().len() == n_votes`, not `threshold <= n_votes`. After resharing shrinks the participant set to exactly the threshold-many voters, the carried-over votes already equal `len()`.

**`AddDomainsVotes::vote` replaces an existing vote and re-counts:** [5](#0-4) 

When a remaining participant re-submits the same proposal, their old vote is replaced with the identical value, the total for that proposal is still `threshold`, and `threshold == new_participant_count` triggers the transition.

---

### Impact Explanation

Threshold-many participants can add a new domain without the unanimous consent of all current participants. The all-participants quorum for `vote_add_domains` is explicitly designed to be stronger than the governance threshold; this attack reduces it to the governance threshold by engineering the participant set. The result is an unauthorized `Initializing` state transition that generates keys for a domain that was never unanimously approved under the post-resharing participant set.

---

### Likelihood Explanation

The attack requires exactly threshold-many participants to coordinate two sequential on-chain actions (pre-vote `vote_add_domains`, then vote `vote_new_parameters` to remove the non-voters). No off-chain capability, leaked key, or network-level access is needed. The entire sequence is executable through normal contract calls.

---

### Recommendation

Reset `add_domains_votes` to `AddDomainsVotes::default()` whenever the participant set changes, rather than carrying over filtered votes. The correct fix is in `RunningContractState::new`: ignore the `add_domains_votes` argument (or remove it) and always initialize `add_domains_votes` to `Default::default()`. Votes cast under a previous participant set must never count toward the quorum of a new participant set. [6](#0-5) 

---

### Proof of Concept

```
Setup: 5 participants P0–P4, threshold = 3.

1. P0, P1, P2 call vote_add_domains(X).
   → add_domains_votes = {id:0→X, id:1→X, id:2→X}
   → n_votes=3, num_participants=5 → no transition.

2. P0, P1, P2 call vote_new_parameters({P0,P1,P2}, threshold=3).
   → All 3 proposed participants voted → resharing starts.
   → transition_to_resharing_no_checks calls RunningContractState::new
     with add_domains_votes={id:0→X, id:1→X, id:2→X}.
   → get_remaining_votes keeps all 3 (P0,P1,P2 are in the new set).
   → previous_running_state.add_domains_votes = {id:0→X, id:1→X, id:2→X}.

3. P0, P1, P2 complete resharing (vote_reshared for each domain).
   → RunningContractState::new called with add_domains_votes={id:0→X,id:1→X,id:2→X}.
   → get_remaining_votes keeps all 3.
   → New RunningContractState: participants={P0,P1,P2}, add_domains_votes={3 votes for X}.

4. P0 calls vote_add_domains(X).
   → AuthenticatedParticipantId::new succeeds (P0 still has id:0 in new set).
   → vote() replaces P0's existing vote with X (same value) → total=3.
   → n_votes=3, num_participants=3 → 3==3 → transition to Initializing. ✓
```

The existing sandbox test `add_domain_votes_from_kicked_out_participants_are_cleared_after_resharing` only verifies that removed participants' votes are filtered out; it does not cover the case where the surviving vote count equals the new participant count. [7](#0-6)

### Citations

**File:** crates/contract/src/state/resharing.rs (L155-160)
```rust
                return Ok(Some(RunningContractState::new(
                    new_domains,
                    Keyset::new(self.prospective_epoch_id(), self.reshared_keys.clone()),
                    self.resharing_key.proposed_parameters().clone(),
                    self.previous_running_state.add_domains_votes.clone(),
                )));
```

**File:** crates/contract/src/state/running.rs (L48-64)
```rust
    pub fn new(
        domains: DomainRegistry,
        keyset: Keyset,
        parameters: ThresholdParameters,
        add_domains_votes: AddDomainsVotes,
    ) -> Self {
        let remaining_add_domain_votes =
            add_domains_votes.get_remaining_votes(parameters.participants());
        RunningContractState {
            domains,
            keyset,
            parameters,
            parameters_votes: ThresholdParametersVotes::default(),
            add_domains_votes: remaining_add_domain_votes,
            previously_cancelled_resharing_epoch_id: None,
        }
    }
```

**File:** crates/contract/src/state/running.rs (L237-237)
```rust
        if self.parameters.participants().len() as u64 == n_votes {
```

**File:** crates/contract/src/primitives/domain.rs (L252-265)
```rust
        if self
            .proposal_by_account
            .insert(participant.clone(), proposal.clone())
            .is_some()
        {
            log!("removed old vote for signer");
        }
        let total = self
            .proposal_by_account
            .values()
            .filter(|&prop| prop == &proposal)
            .count() as u64;
        log!("total votes for proposal: {}", total);
        total
```

**File:** crates/contract/src/primitives/domain.rs (L269-281)
```rust
    pub fn get_remaining_votes(&self, participants: &Participants) -> Self {
        let remaining_votes = self
            .proposal_by_account
            .iter()
            .filter(|&(participant_id, _vote)| {
                participants.is_participant_given_participant_id(&participant_id.get())
            })
            .map(|(participant_id, vote)| (participant_id.clone(), vote.clone()))
            .collect();
        AddDomainsVotes {
            proposal_by_account: remaining_votes,
        }
    }
```

**File:** crates/contract/tests/sandbox/update_votes_cleanup_after_resharing.rs (L150-246)
```rust
#[tokio::test]
async fn add_domain_votes_from_kicked_out_participants_are_cleared_after_resharing() -> Result<()> {
    // Given
    let SandboxTestSetup {
        contract,
        mpc_signer_accounts,
        ..
    } = SandboxTestSetup::builder()
        .with_protocols(&[Protocol::CaitSith])
        .build()
        .await;

    let initial_participants = assert_running_return_participants(&contract).await?;
    let threshold = assert_running_return_threshold(&contract).await;

    let next_domain_id = {
        let state: dtos::ProtocolContractState = get_state(&contract).await;
        let dtos::ProtocolContractState::Running(running) = &state else {
            panic!("Expected running state");
        };
        running.domains.next_domain_id
    };
    let domains_to_add = vec![DomainConfig {
        id: DomainId(next_domain_id),
        protocol: Protocol::Frost,
        reconstruction_threshold: ReconstructionThreshold::new(6),
        purpose: DomainPurpose::Sign,
    }];
    execute_async_transactions(
        &mpc_signer_accounts[0..2],
        &contract,
        method_names::VOTE_ADD_DOMAINS,
        &json!({"domains": domains_to_add}),
        GAS_FOR_VOTE_NEW_DOMAIN,
    )
    .await?;

    let state: dtos::ProtocolContractState = get_state(&contract).await;
    let dtos::ProtocolContractState::Running(running) = &state else {
        panic!("Expected running state");
    };
    assert_eq!(running.add_domains_votes.proposal_by_account.len(), 2);

    // When
    let mut new_participants = Participants::new();
    for (account_id, participant_id, participant_info) in initial_participants
        .participants
        .iter()
        .skip(1)
        .take(threshold.0 as usize)
    {
        new_participants
            .insert_with_id(
                account_id.clone(),
                mpc_contract::primitives::participants::ParticipantInfo {
                    url: participant_info.url.clone(),
                    tls_public_key: participant_info.tls_public_key.clone(),
                },
                mpc_contract::primitives::participants::ParticipantId((*participant_id).into()),
            )
            .map_err(|e| anyhow::anyhow!("Failed to insert participant: {}", e))?;
    }

    let new_threshold_parameters = ThresholdParameters::new(
        new_participants,
        mpc_contract::primitives::thresholds::Threshold::new(threshold.0),
    )
    .map_err(|e| anyhow::anyhow!("{}", e))?;
    let prospective_epoch_id = dtos::EpochId(6);

    do_resharing(
        &mpc_signer_accounts[1..threshold.0 as usize + 1],
        &contract,
        new_threshold_parameters,
        prospective_epoch_id,
    )
    .await?;

    // Then
    let final_state: dtos::ProtocolContractState = get_state(&contract).await;
    let dtos::ProtocolContractState::Running(final_running) = &final_state else {
        panic!("Expected running state after resharing");
    };

    assert_eq!(final_running.add_domains_votes.proposal_by_account.len(), 1);

    let expected_remaining_voter_id = &initial_participants.participants[1].1;
    let remaining_voter_id = &final_running
        .add_domains_votes
        .proposal_by_account
        .keys()
        .next()
        .expect("Expected one remaining vote")
        .0;
    assert_eq!(remaining_voter_id, expected_remaining_voter_id);

    Ok(())
```
