I have found the analog. Let me confirm the exact code ordering before writing the final output.### Title
`insert_proposal` Persists a Commitment-Mismatched Proposal into `valid_proposals` Before the `ProposalFinMismatch` Guard Fires — (`crates/apollo_consensus_orchestrator/src/validate_proposal.rs`)

---

### Summary

In `validate_proposal`, the call to `valid_proposals.insert_proposal(...)` at line 241 executes **before** the `ProposalFinMismatch` check at line 244. A proposal whose batcher-computed commitment (`built_block`) diverges from the network-received `received_fin.proposal_commitment` is therefore permanently written into the `valid_proposals` cache under the batcher's commitment key, even though the function subsequently returns `Err(ProposalFinMismatch)`. Because `decision_reached` looks up proposals from that same cache by `(height, round, commitment)`, the orphaned entry is reachable by the consensus finalization path, allowing a block that was locally rejected to be committed to storage.

---

### Finding Description

`validate_proposal` in `crates/apollo_consensus_orchestrator/src/validate_proposal.rs` ends with the following sequence:

```rust
// line 240-241 — insert happens unconditionally
let mut valid_proposals = args.valid_proposals.lock().unwrap();
valid_proposals.insert_proposal(args.init, content, &args.proposal_id, finished_info);

// line 244-247 — guard fires AFTER the insert
if built_block != received_fin.proposal_commitment {
    CONSENSUS_PROPOSAL_FIN_MISMATCH.increment(1);
    return Err(ValidateProposalError::ProposalFinMismatch);
}
```

`insert_proposal` stores the entry keyed by `(height, round)` with the **batcher-computed** `proposal_commitment` derived from `finished_info.proposal_commitment.partial_block_hash`:

```rust
// sequencer_consensus_context.rs line 187-197
let proposal_commitment = proposal_commitment_from(
    finished_info.proposal_commitment.partial_block_hash,
    init.fee_proposal_fri,
);
// ...
by_round.insert(round, (proposal_commitment, (init, transactions, *proposal_id, finished_info)));
```

When `ProposalFinMismatch` fires, `validate_and_send` propagates the error and drops `fin_sender` without sending — so the local node never casts a vote for this proposal. However, the entry under the batcher's commitment is already live in `valid_proposals`.

`decision_reached` retrieves proposals from that same map:

```rust
// sequencer_consensus_context.rs line 1001-1002
let (init, transactions, proposal_id, finished_info) =
    proposals.get_proposal(&height, &round, &commitment).clone();
```

If the Tendermint state machine subsequently fires `decision_reached` with the batcher's commitment (because ≥ 2/3 of other validators voted for it), the local node will find the orphaned entry, call `batcher.decision_reached(...)`, and commit the block to storage — a block the local node had explicitly rejected as invalid.

---

### Impact Explanation

The corrupted value is the **committed block state**: a validator node commits a block whose `ProposalFin` commitment the local node had already flagged as mismatched and rejected. After `batcher.decision_reached` is called, the code comment at line 1010 itself marks the point of no return:

> "CRITICAL: The block is now committed. This function must not fail beyond this point unless the state is fully reverted."

The committed state diff, nonces, L1 handler consumption records, and mempool updates all derive from the orphaned `BlockExecutionArtifacts`. If the batcher's commitment diverges from the honest network commitment (e.g., due to a non-deterministic execution path, a class-hash substitution, or a targeted batcher-side manipulation), the local node's storage root, transaction receipts, and event commitments will differ from the rest of the network while appearing locally committed and final.

This maps to the impact category: **Wrong state, receipt, event, L1 message, class hash, storage value, or revert result from blockifier/syscall/execution logic for accepted input** and **Incorrect fee, gas, bouncer, resource accounting, refund, balance, or L1 gas price effect with economic impact**.

---

### Likelihood Explanation

The trigger requires two concurrent conditions:

1. A proposer (Byzantine or network-split) sends a `ProposalFin` whose `proposal_commitment` field does not match the batcher's locally computed `partial_block_hash`. This is an unprivileged network message — any node that controls the proposer slot for a round can craft it.
2. ≥ 2/3 of other validators vote for the batcher's commitment (i.e., they received a `ProposalFin` with the correct commitment, or they computed the same batcher commitment independently).

Condition 1 is trivially achievable by a Byzantine proposer. Condition 2 is the normal case when the proposer sends different `ProposalFin` values to different subsets of validators (equivocation on the `fin_payload`). The local node is the only one that sees the wrong commitment; the rest of the network reaches quorum on the correct one; `decision_reached` fires locally with the batcher's commitment; the orphaned entry is found and committed.

---

### Recommendation

Move the `ProposalFinMismatch` guard **before** `insert_proposal`. Only insert the proposal into `valid_proposals` after confirming the batcher's commitment matches the network's claimed commitment:

```rust
// Correct ordering
if built_block != received_fin.proposal_commitment {
    CONSENSUS_PROPOSAL_FIN_MISMATCH.increment(1);
    return Err(ValidateProposalError::ProposalFinMismatch);
}

let mut valid_proposals = args.valid_proposals.lock().unwrap();
valid_proposals.insert_proposal(args.init, content, &args.proposal_id, finished_info);

Ok(built_block)
```

The comment at line 238 ("Update valid_proposals before sending fin to avoid a race condition with `repropose`") describes a race between `insert_proposal` and `repropose`. That race is irrelevant when the proposal is being rejected — a rejected proposal must never be reproposed — so the guard can safely precede the insert without reintroducing the race.

---

### Proof of Concept

1. Byzantine proposer P holds the proposer slot for `(height=H, round=R)`.
2. P sends the full proposal stream (valid transactions) to all validators.
3. P sends `ProposalFin { proposal_commitment: C_wrong, executed_transaction_count: N }` to target validator V, where `C_wrong ≠ C_batcher` (the commitment the batcher will compute).
4. P sends `ProposalFin { proposal_commitment: C_batcher, executed_transaction_count: N }` to all other validators.
5. On V: `handle_proposal_part` returns `HandledProposalPart::Finished(C_batcher, fin_with_C_wrong, finished_info)`. `validate_proposal` calls `insert_proposal` storing `(H, R) → C_batcher`, then detects `C_batcher ≠ C_wrong`, returns `Err(ProposalFinMismatch)`. `fin_sender` is dropped; V never votes.
6. On all other validators: `ProposalFinMismatch` does not fire; they vote for `C_batcher`. Quorum is reached.
7. Tendermint state machine on V fires `decision_reached(H, R, C_batcher)`.
8. `get_proposal(&H, &R, &C_batcher)` succeeds (orphaned entry from step 5). `batcher.decision_reached(proposal_id)` is called. The block is committed to storage on V despite V having returned `ProposalFinMismatch` for this proposal. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L238-247)
```rust
    // Update valid_proposals before sending fin to avoid a race condition
    // with `repropose` being called before `valid_proposals` is updated.
    let mut valid_proposals = args.valid_proposals.lock().unwrap();
    valid_proposals.insert_proposal(args.init, content, &args.proposal_id, finished_info);

    // TODO(matan): Switch to signature validation.
    if built_block != received_fin.proposal_commitment {
        CONSENSUS_PROPOSAL_FIN_MISMATCH.increment(1);
        return Err(ValidateProposalError::ProposalFinMismatch);
    }
```

**File:** crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs (L180-203)
```rust
    pub(crate) fn insert_proposal(
        &mut self,
        init: ProposalInit,
        transactions: Vec<Vec<InternalConsensusTransaction>>,
        proposal_id: &ProposalId,
        finished_info: FinishedProposalInfo,
    ) {
        let proposal_commitment = proposal_commitment_from(
            finished_info.proposal_commitment.partial_block_hash,
            init.fee_proposal_fri,
        );

        let height = init.height;
        let round = init.round;
        let by_round = self.data.entry(height).or_default();
        let previous = by_round.insert(
            round,
            (proposal_commitment, (init, transactions, *proposal_id, finished_info)),
        );
        assert!(
            previous.is_none(),
            "Overwriting existing proposal for height {height} round {round}; at most one \
             proposal per (height, round) is allowed"
        );
```

**File:** crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs (L999-1008)
```rust
        let (init, transactions, proposal_id, finished_info) = {
            let mut proposals = self.valid_proposals.lock().unwrap();
            let (init, transactions, proposal_id, finished_info) =
                proposals.get_proposal(&height, &round, &commitment).clone();
            proposals.remove_proposals_below_or_at_height(&height);
            (init, transactions, proposal_id, finished_info)
        };

        let decision_reached_response =
            self.deps.batcher.decision_reached(DecisionReachedInput { proposal_id }).await?;
```

**File:** crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs (L1292-1301)
```rust
async fn validate_and_send(
    args: ProposalValidateArguments,
    fin_sender: oneshot::Sender<ProposalCommitment>,
) -> Result<ProposalCommitment, ValidateProposalError> {
    let proposal_commitment = validate_proposal(args).await?;
    fin_sender
        .send(proposal_commitment)
        .map_err(|_| ValidateProposalError::SendError(proposal_commitment))?;
    Ok(proposal_commitment)
}
```
