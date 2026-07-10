### Title
Stale `add_domains_votes` Carried Across Resharing Epoch Allows Unanimous-Consent Bypass in `vote_add_domains` — (File: `crates/contract/src/state/running.rs`)

---

### Summary

After a resharing epoch transition, `add_domains_votes` from the previous `RunningContractState` is carried over verbatim into the new `RunningContractState`. The `AddDomainsVotes::vote` function counts **all** stored votes for a matching proposal without filtering by the current participant set. Because `vote_add_domains` checks `participants.len() == n_votes` (unanimous consent), stale votes from removed participants are silently counted toward that threshold, allowing a strict minority of current participants to satisfy the unanimous-consent requirement and trigger unauthorized domain addition (key generation).

---

### Finding Description

`ResharingContractState::vote_reshared` constructs the new `RunningContractState` by explicitly cloning the previous epoch's `add_domains_votes`: [1](#0-0) 

No filtering of stale participant votes is applied at this point. None of the post-resharing cleanup promises (`remove_non_participant_update_votes`, `clean_tee_status`, `clean_invalid_attestations`, `cleanup_orphaned_node_migrations`, `clean_foreign_chain_data`, `remove_non_participant_tee_verifier_votes`) touch `add_domains_votes`. [2](#0-1) 

Inside `vote_add_domains`, the threshold check is: [3](#0-2) 

The `AddDomainsVotes::vote` function that produces `n_votes` counts **every** entry in `proposal_by_account` whose value matches the proposal, with no participant-set filter: [4](#0-3) 

A `get_remaining_votes` helper exists that does filter correctly: [5](#0-4) 

But it is never called during or after the resharing transition.

The analog to the external report's bug is exact: `vote_add_domains` uses `self.parameters.participants().len()` (the **current** global participant count) as the denominator, while `AddDomainsVotes::vote` counts votes using the **stale per-entry** participant IDs from the previous epoch — the same "current global vs. last-applied per-entry" mismatch described in the report.

---

### Impact Explanation

**Medium.** The unanimous-consent invariant for `vote_add_domains` is broken. A single current participant (or a strict minority) can trigger a domain-addition state transition — launching key generation for a new cryptographic domain — without the required agreement of all current participants. This corrupts the contract's execution-flow accounting: the `Initializing` state is entered and a `KeyEvent` is created under false consensus. While the MPC key-generation protocol itself still requires all participants to cooperate (so the key may not actually be produced), the contract state is corrupted and resources are consumed without proper authorization.

---

### Likelihood Explanation

**Low-to-Medium.** The preconditions are:
1. At least one participant votes for a domain proposal before a resharing.
2. That participant is removed in the resharing.
3. After resharing, the remaining/new participants vote for the **exact same** `Vec<DomainConfig>` (same domain IDs, protocols, thresholds).

Domain IDs are sequential from `next_domain_id`, which does not reset on resharing, so the same proposal is structurally reproducible. A Byzantine participant below the signing threshold who is about to be removed can pre-vote for a domain proposal, then after being removed, their stale vote persists and can be combined with a single colluding current participant's vote to satisfy the unanimous threshold.

---

### Recommendation

Apply `get_remaining_votes` to filter `add_domains_votes` during the resharing-to-running transition, before constructing the new `RunningContractState`:

```rust
// In ResharingContractState::vote_reshared, replace:
self.previous_running_state.add_domains_votes.clone(),
// with:
self.previous_running_state
    .add_domains_votes
    .get_remaining_votes(self.resharing_key.proposed_parameters().participants()),
```

Additionally, `AddDomainsVotes::vote` should filter its count by the current participant set (mirroring `ThresholdParametersVotes::n_votes`) so that stale entries can never be counted even if cleanup is delayed.

---

### Proof of Concept

**Setup:** 5 participants `{P1, P2, P3, P4, P5}`, unanimous threshold = 5.

1. **Epoch N:** P1, P2, P3 call `vote_add_domains([DomainConfig { id: DomainId(1), protocol: CaitSith, ... }])`. Three votes stored in `add_domains_votes`. Threshold not yet reached (3 ≠ 5).
2. **Resharing:** P1, P2, P3 are removed; P6, P7, P8 are added. New set: `{P4, P5, P6, P7, P8}` (5 participants). `add_domains_votes` is cloned verbatim into the new `RunningContractState` — stale votes from P1, P2, P3 remain.
3. **Epoch N+1:** P4 calls `vote_add_domains([DomainConfig { id: DomainId(1), protocol: CaitSith, ... }])`. `AddDomainsVotes::vote` counts P1+P2+P3+P4 = 4 votes. Still 4 ≠ 5.
4. P5 calls `vote_add_domains` with the same proposal. Count = P1+P2+P3+P4+P5 = 5 = `participants.len()`. **Threshold satisfied.** Contract transitions to `Initializing` with only 2 actual current-epoch votes (P4, P5) instead of the required 5. [6](#0-5) [7](#0-6) [8](#0-7)

### Citations

**File:** crates/contract/src/state/resharing.rs (L146-161)
```rust
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
```

**File:** crates/contract/src/lib.rs (L1175-1235)
```rust
            // Spawn a promise to clean up votes from non-participants.
            // Note: MpcContract::vote_update uses filtering to ensure correctness even if this cleanup fails.
            Promise::new(env::current_account_id())
                .function_call(
                    method_names::REMOVE_NON_PARTICIPANT_UPDATE_VOTES.to_string(),
                    vec![],
                    NearToken::from_yoctonear(0),
                    Gas::from_tgas(self.config.remove_non_participant_update_votes_tera_gas),
                )
                .detach();
            // Spawn a promise to drop votes cast by non-participants.
            Promise::new(env::current_account_id())
                .function_call(
                    method_names::CLEAN_TEE_STATUS.to_string(),
                    vec![],
                    NearToken::from_yoctonear(0),
                    Gas::from_tgas(self.config.clean_tee_status_tera_gas),
                )
                .detach();
            // Spawn a bounded sweep over stored attestations to prune invalid / expired entries.
            Promise::new(env::current_account_id())
                .function_call(
                    method_names::CLEAN_INVALID_ATTESTATIONS.to_string(),
                    serde_json::to_vec(&serde_json::json!({
                        "max_scan": RESHARE_CLEAN_INVALID_ATTESTATIONS_MAX_SCAN
                    }))
                    .unwrap(),
                    NearToken::from_yoctonear(0),
                    Gas::from_tgas(self.config.clean_invalid_attestations_tera_gas),
                )
                .detach();
            // Spawn a promise to clean up orphaned node migrations for non-participants
            Promise::new(env::current_account_id())
                .function_call(
                    method_names::CLEANUP_ORPHANED_NODE_MIGRATIONS.to_string(),
                    vec![],
                    NearToken::from_yoctonear(0),
                    Gas::from_tgas(self.config.cleanup_orphaned_node_migrations_tera_gas),
                )
                .detach();
            // Spawn a promise to clean up foreign chain data for non-participants
            Promise::new(env::current_account_id())
                .function_call(
                    method_names::CLEAN_FOREIGN_CHAIN_DATA.to_string(),
                    vec![],
                    NearToken::from_yoctonear(0),
                    Gas::from_tgas(self.config.clean_foreign_chain_data_tera_gas),
                )
                .detach();
            // Spawn a promise to drop verifier-change votes cast by non-participants
            Promise::new(env::current_account_id())
                .function_call(
                    method_names::REMOVE_NON_PARTICIPANT_TEE_VERIFIER_VOTES.to_string(),
                    vec![],
                    NearToken::from_yoctonear(0),
                    Gas::from_tgas(
                        self.config
                            .remove_non_participant_tee_verifier_votes_tera_gas,
                    ),
                )
                .detach();
```

**File:** crates/contract/src/state/running.rs (L214-252)
```rust
    pub fn vote_add_domains(
        &mut self,
        domains: Vec<DomainConfig>,
    ) -> Result<Option<InitializingContractState>, Error> {
        if domains.is_empty() {
            return Err(DomainError::AddDomainsMustAddAtLeastOneDomain.into());
        }
        let num_participants = u64::try_from(self.parameters.participants().len())
            .expect("participant count fits in u64");
        for domain in &domains {
            validate_domain_purpose(domain)?;
            validate_domain_threshold(domain, num_participants)?;
        }
        // Keep trust assumptions consistent: a domain must never require more shares to
        // reconstruct than the GovernanceThreshold demands to govern. Route through the
        // canonical helper so the cross-domain invariant has a single source of truth.
        ThresholdParameters::validate_governance_against_reconstruction(
            num_participants,
            self.parameters.threshold(),
            max_reconstruction_threshold(&domains),
        )?;
        let participant = AuthenticatedParticipantId::new(self.parameters.participants())?;
        let n_votes = self.add_domains_votes.vote(domains.clone(), &participant);
        if self.parameters.participants().len() as u64 == n_votes {
            let new_domains = self.domains.add_domains(domains.clone())?;
            Ok(Some(InitializingContractState {
                generated_keys: self.keyset.domains.clone(),
                domains: new_domains,
                epoch_id: self.keyset.epoch_id,
                generating_key: KeyEvent::new(
                    self.keyset.epoch_id,
                    domains[0].clone(),
                    self.parameters.clone(),
                ),
                cancel_votes: BTreeSet::new(),
            }))
        } else {
            Ok(None)
        }
```

**File:** crates/contract/src/primitives/domain.rs (L243-266)
```rust
impl AddDomainsVotes {
    /// Votes for the proposal, returning the total number of voters so far who
    /// have proposed the exact same domains to add.
    /// If the participant had voted already, this replaces the existing vote.
    pub fn vote(
        &mut self,
        proposal: Vec<DomainConfig>,
        participant: &AuthenticatedParticipantId,
    ) -> u64 {
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
    }
```

**File:** crates/contract/src/primitives/domain.rs (L268-281)
```rust
    /// Filters out existing votes no longer in the participant set
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
