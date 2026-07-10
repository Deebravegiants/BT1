Looking at the exact code paths:

**`ProviderVotes::vote`** (foreign_chain_rpc.rs:172-200): uses the `threshold_parameters` passed at call time — both the participant membership check and the threshold comparison use the current snapshot.

**`ProviderVotes::retain`** (foreign_chain_rpc.rs:163-166): only removes votes from accounts that are no longer participants. Votes from accounts that remain participants after resharing are preserved.

**`clean_foreign_chain_data`** (lib.rs:1885-1893): calls `retain(participants)` — same logic, only prunes non-participants.

The scenario is fully reachable:

1. N participants, threshold=T_old. A Byzantine coalition of size K (K < T_old, K >= T_new) votes for malicious chain X. Not applied (K < T_old).
2. A legitimate resharing reduces threshold to T_new (approved by honest majority of old participants). All K Byzantine voters remain participants.
3. `clean_foreign_chain_data` runs: K voters are still participants → their votes are **retained**.
4. Any one of the K Byzantine participants calls `vote_update_foreign_chain_providers` for chain X again. `Votes::vote` removes their old vote and re-inserts it. `count_for` now counts K votes (all current participants) against T_new. K >= T_new → chain X is applied.

The existing test `vote__should_not_count_stale_non_participant_votes` (foreign_chain_rpc.rs:711-747) only covers the case where voters are **removed** from the participant set. It does not cover the case where voters remain participants but the threshold drops.

---

### Title
Stale pre-resharing votes counted against reduced threshold enables below-old-threshold coalition to whitelist a foreign chain — (`crates/contract/src/foreign_chain_rpc.rs`)

### Summary
`ProviderVotes::vote` evaluates the threshold crossing using the `ThresholdParameters` snapshot passed at call time. After a resharing that reduces the signing threshold, votes cast by participants who remain in the new set are preserved by `clean_foreign_chain_data`. A Byzantine coalition that was below the old threshold but at or above the new threshold can re-vote after resharing and cross the new threshold, whitelisting a chain that was never approved by the old threshold.

### Finding Description
`ProviderVotes::vote` records a vote and immediately evaluates whether the accumulated votes for that chain cross the protocol threshold: [1](#0-0) 

Both the participant membership filter (`participants.is_participant_given_participant_id`) and the threshold comparison (`count >= protocol_threshold`) use the `ThresholdParameters` value passed at call time — the **current** post-resharing parameters. There is no record of which threshold was active when each vote was originally cast.

`clean_foreign_chain_data` prunes only votes from accounts that are no longer participants: [2](#0-1) 

`ProviderVotes::retain` enforces the same predicate: [3](#0-2) 

Votes from participants who survive the resharing are therefore preserved in storage. When any of those participants re-votes after resharing, `Votes::vote` removes and re-inserts their entry, triggering a fresh `count_for` evaluation against the new (lower) threshold. If the accumulated count of current-participant votes now meets or exceeds the new threshold, the chain is applied.

### Impact Explanation
An attacker-controlled foreign chain is added to the whitelist. Nodes then treat observations for that chain as valid and will sign transactions on it. This enables unauthorized cross-chain transaction execution — a Critical-scope impact under "Unauthorized transaction execution … without the required participant authorization."

### Likelihood Explanation
Threshold reductions are a normal protocol operation (e.g., participants voluntarily leaving). A Byzantine coalition below the old threshold can pre-vote for a malicious chain at any time before resharing at zero cost. After any legitimate threshold reduction that keeps them as participants, they re-vote and the chain is applied. No external dependency, no network-level attack, and no threshold-or-above collusion is required.

### Recommendation
When evaluating whether accumulated votes cross the threshold, only count votes cast **at or after** the current epoch. The simplest fix is to clear all pending foreign-chain provider votes on every resharing (in `clean_foreign_chain_data` or in the resharing completion path), rather than only pruning non-participant votes. Alternatively, tag each stored vote with the epoch in which it was cast and reject votes from prior epochs in `count_for`.

### Proof of Concept
```
Setup: 5 participants {p0..p4}, threshold = 3.

Step 1 – pre-resharing votes (count = 2 < threshold = 3, not applied):
  p0.vote_update_foreign_chain_providers({Ethereum: malicious_entry})  // tp=(5 participants, t=3)
  p1.vote_update_foreign_chain_providers({Ethereum: malicious_entry})  // tp=(5 participants, t=3)
  assert!(stored_entry(Ethereum).is_none());

Step 2 – legitimate resharing reduces threshold to 2, all 5 remain participants.
  clean_foreign_chain_data() runs → p0 and p1 are still participants → votes retained.

Step 3 – p0 re-votes (or p2 votes for the first time):
  p0.vote_update_foreign_chain_providers({Ethereum: malicious_entry})  // tp=(5 participants, t=2)
  // count_for returns 2 (p0 + p1, both current participants), 2 >= 2 → applied.
  assert!(stored_entry(Ethereum).is_some());  // malicious chain whitelisted
```

This matches the structure of the existing unit test harness in `foreign_chain_rpc.rs` and can be reproduced with `gen_authenticated_participants` and `ThresholdParameters::new_unvalidated`. [4](#0-3) [5](#0-4)

### Citations

**File:** crates/contract/src/foreign_chain_rpc.rs (L163-166)
```rust
    pub fn retain(&mut self, current: &Participants) {
        self.pending
            .retain_votes(|(p, _)| current.is_participant_given_participant_id(&p.get()));
    }
```

**File:** crates/contract/src/foreign_chain_rpc.rs (L179-196)
```rust
        let protocol_threshold = threshold_parameters.threshold().value();
        let participants = threshold_parameters.participants();
        // Scope the borrow on `self.pending.vote` so we can mutate `self.pending`
        // after `count_for`.
        let count_usize = {
            let voter_set = self.pending.vote((participant, chain), hash);
            voter_set.count_for(|(p, c)| {
                *c == chain && participants.is_participant_given_participant_id(&p.get())
            })
        };
        let count = u64::try_from(count_usize).map_err(|e| ConversionError::DataConversion {
            reason: format!("vote count {count_usize} does not fit in u64: {e}"),
        })?;
        if count >= protocol_threshold {
            // Drop ALL pending rows for this chain regardless of which proposal
            // they held — matches the previous `clear_chain` semantics.
            self.pending.retain_votes(|(_, c)| *c != chain);
            Ok(true)
```

**File:** crates/contract/src/lib.rs (L1847-1895)
```rust
    pub fn clean_foreign_chain_data(&mut self) -> Result<(), Error> {
        log!(
            "clean_foreign_chain_data: signer={}",
            env::signer_account_id()
        );

        let participants = match &self.protocol_state {
            ProtocolContractState::Running(state) => state.parameters.participants(),
            _ => {
                return Err(InvalidState::ProtocolStateNotRunning.into());
            }
        };

        let participant_accounts: std::collections::HashSet<dtos::AccountId> = participants
            .participants()
            .iter()
            .map(|(account_id, _, _)| account_id.clone())
            .collect();

        let active_tls_keys: std::collections::BTreeSet<dtos::Ed25519PublicKey> = participants
            .participants()
            .iter()
            .map(|(_, _, info)| info.tls_public_key.clone())
            .collect();

        let non_participant_configs: Vec<dtos::AccountId> = self
            .node_foreign_chain_support
            .foreign_chain_support_by_node
            .keys()
            .filter(|account| !participant_accounts.contains(*account))
            .cloned()
            .collect();
        for account in &non_participant_configs {
            self.node_foreign_chain_support
                .foreign_chain_support_by_node
                .remove(account);
        }

        self.foreign_chains
            .get_mut()
            .remove_stale_configs(&active_tls_keys);

        self.foreign_chains
            .get_mut()
            .rpc_whitelist
            .votes
            .retain(participants);

        Ok(())
```
