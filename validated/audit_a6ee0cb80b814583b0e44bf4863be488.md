### Title
Validator Inserts Proposal into `valid_proposals` Before Commitment Comparison, Leaving a Mismatched Proposal Permanently Cached - (`crates/apollo_consensus_orchestrator/src/validate_proposal.rs`)

### Summary

In `validate_proposal`, the validator unconditionally calls `valid_proposals.insert_proposal(...)` **before** checking whether the batcher-computed commitment matches the network-received `ProposalFin.proposal_commitment`. When the check fails and `ProposalFinMismatch` is returned, the proposal is already stored in the `valid_proposals` cache under the batcher's commitment key. This is the direct analog of the M-01 pattern: an irreversible side-effect (insertion into the shared cache) is performed before a downstream integrity check, and the error path does not undo it.

### Finding Description

In `validate_proposal` in `crates/apollo_consensus_orchestrator/src/validate_proposal.rs`, lines 238–247:

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

The comment acknowledges the ordering is intentional to avoid a race with `repropose`. However, the consequence is that when `built_block != received_fin.proposal_commitment`, the function returns `Err(ProposalFinMismatch)` **after** the proposal has already been inserted into `valid_proposals` under the batcher-derived commitment key.

`insert_proposal` computes the stored key as:

```rust
let proposal_commitment = proposal_commitment_from(
    finished_info.proposal_commitment.partial_block_hash,
    init.fee_proposal_fri,
);
``` [1](#0-0) 

This is the **batcher's** commitment, not the network's `received_fin.proposal_commitment`. So when they diverge, the cache holds a proposal keyed by the batcher's commitment, while the network voted on a different commitment. The `validate_and_send` caller returns the error to the spawned task, which logs a warning and exits — no cleanup of `valid_proposals` occurs. [2](#0-1) [3](#0-2) 

### Impact Explanation

**High — RPC/consensus view returns wrong value; wrong block committed.**

If consensus subsequently calls `decision_reached` with the network's commitment (the one that achieved quorum), `get_proposal` will panic because the stored key is the batcher's commitment, not the network's:

```rust
assert_eq!(
    stored_commitment, commitment,
    "Proposal commitment mismatch for height {height} round {round}: ..."
);
``` [4](#0-3) 

Alternatively, if the batcher's commitment is what consensus voted on (i.e., the network `Fin` was spoofed/corrupted), the proposal is cached and `decision_reached` will proceed to commit a block whose `ProposalFin` commitment was rejected by the validator's own check — meaning the committed block's state root, transaction commitment, event commitment, and receipt commitment are those of the batcher's execution, not what the network agreed upon. This is a wrong state commitment delivered to `state_sync_client.add_new_block` and the cende blob pipeline. [5](#0-4) 

### Likelihood Explanation

The `ProposalFinMismatch` path is reachable whenever a proposer sends a `ProposalFin` whose `proposal_commitment` field does not match what the validator's batcher computed. This can occur:

1. **Naturally** during a Byzantine or buggy proposer that sends a mismatched commitment.
2. **Via network manipulation** — a man-in-the-middle that replaces the `ProposalFin.proposal_commitment` field in transit (the field is not yet signature-protected; the code comment `// TODO(matan): Switch to signature validation` confirms this).
3. **Via a crafted `executed_transaction_count`** — the `Fin` count is used to truncate content before calling `finish_proposal`, so a carefully chosen count can cause the batcher to produce a different commitment than the proposer intended.

No privileged access is required; any peer on the consensus network can send a `ProposalFin` with an arbitrary `proposal_commitment`. [6](#0-5) 

### Recommendation

Move `valid_proposals.insert_proposal(...)` to **after** the commitment comparison succeeds, so the cache is only populated with proposals that passed all integrity checks:

```rust
// TODO(matan): Switch to signature validation.
if built_block != received_fin.proposal_commitment {
    CONSENSUS_PROPOSAL_FIN_MISMATCH.increment(1);
    return Err(ValidateProposalError::ProposalFinMismatch);
}

// Only insert after the commitment check passes.
let mut valid_proposals = args.valid_proposals.lock().unwrap();
valid_proposals.insert_proposal(args.init, content, &args.proposal_id, finished_info);
```

To address the race condition with `repropose` that motivated the original ordering, note that `repropose` is only called after `decision_reached`, which only fires after consensus has a quorum on a commitment. A proposal that fails `ProposalFinMismatch` will never achieve quorum, so it will never be reproposed. The race condition comment does not apply to the mismatch path. [7](#0-6) 

### Proof of Concept

1. A Byzantine proposer (or network attacker) streams a valid `ProposalInit` and transaction batches to a validator node.
2. The batcher executes the transactions and produces `partial_block_hash = H_batcher`.
3. The attacker sends `ProposalFin { proposal_commitment: H_network ≠ Poseidon(H_batcher, fee_proposal), executed_transaction_count: N }`.
4. `handle_proposal_part` returns `HandledProposalPart::Finished(batcher_commitment, fin, finished_info)` where `batcher_commitment ≠ fin.proposal_commitment`.
5. `validate_proposal` reaches line 241: `valid_proposals.insert_proposal(args.init, content, &args.proposal_id, finished_info)` — the proposal is stored under `batcher_commitment`.
6. Line 244: `built_block != received_fin.proposal_commitment` is `true`; `ProposalFinMismatch` is returned.
7. The spawned task logs a warning. `valid_proposals` now contains a stale entry for `(height, round) → batcher_commitment` with the full execution artifacts.
8. If the same `(height, round)` later reaches `decision_reached` with `batcher_commitment` (e.g., because enough validators computed the same batcher hash and the attacker's `H_network` was the correct one that consensus voted on), `get_proposal` finds the entry and `decision_reached` proceeds to commit the block — but the `ProposalFin` that consensus signed over was `H_network`, not `batcher_commitment`, so the committed block's state is inconsistent with what the network agreed upon. [7](#0-6) [8](#0-7) [9](#0-8)

### Citations

**File:** crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs (L168-172)
```rust
        assert_eq!(
            stored_commitment, commitment,
            "Proposal commitment mismatch for height {height} round {round}: \
             stored={stored_commitment}, requested={commitment}"
        );
```

**File:** crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs (L180-204)
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
    }
```

**File:** crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs (L989-1024)
```rust
    async fn decision_reached(
        &mut self,
        height: BlockNumber,
        round: Round,
        commitment: ProposalCommitment,
        wait_for_last_commitment: bool,
    ) -> Result<(), ConsensusError> {
        info!("Finished consensus for height: {height}. Agreed on block: {:#066x}", commitment.0);

        self.interrupt_active_proposal().await;
        let (init, transactions, proposal_id, finished_info) = {
            let mut proposals = self.valid_proposals.lock().unwrap();
            let (init, transactions, proposal_id, finished_info) =
                proposals.get_proposal(&height, &round, &commitment).clone();
            proposals.remove_proposals_below_or_at_height(&height);
            (init, transactions, proposal_id, finished_info)
        };

        let decision_reached_response =
            self.deps.batcher.decision_reached(DecisionReachedInput { proposal_id }).await?;

        // CRITICAL: The block is now committed. This function must not fail beyond this point
        // unless the state is fully reverted, otherwise the node will be left in an
        // inconsistent state.

        self.finalize_decision(
            height,
            &init,
            commitment,
            transactions,
            decision_reached_response,
            finished_info.block_header_commitments.clone(),
            finished_info.l2_gas_used,
            wait_for_last_commitment,
        )
        .await;
```

**File:** crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs (L1246-1262)
```rust
        let handle = tokio::spawn(
            async move {
                match validate_and_send(args, fin_sender).await {
                    Ok(proposal_commitment) => {
                        info!(?proposal_id, ?proposal_commitment, "Proposal succeeded.");
                    }
                    Err(e) => {
                        warn!("PROPOSAL_FAILED: Proposal failed as validator. Error: {e:?}");
                        record_validate_proposal_failure(e.into());
                    }
                }
            }
            .instrument(
                error_span!("consensus_validate_proposal", %proposal_id, round=self.current_round),
            ),
        );
        self.active_proposal = Some((cancel_token, handle));
```

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L238-250)
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

    Ok(built_block)
}
```

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L519-530)
```rust
            // `executed_transaction_count` comes straight off the wire, so a dishonest or
            // spoofed `Fin` can claim more transactions than were actually streamed. Reject
            // that here instead of trusting the count downstream.
            let n_received_txs = content.iter().map(Vec::len).sum::<usize>();
            if executed_txs_count > n_received_txs {
                return HandledProposalPart::Failed(format!(
                    "Fin claims {executed_txs_count} executed transactions but only \
                     {n_received_txs} were received in the proposal."
                ));
            }

            *content = truncate_to_executed_txs(content, executed_txs_count);
```
