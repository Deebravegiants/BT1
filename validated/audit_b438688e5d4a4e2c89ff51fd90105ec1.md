### Title
Proposal Stored in `valid_proposals` Before Commitment Mismatch Check Allows Invalid Proposal to Reach `decision_reached` - (File: `crates/apollo_consensus_orchestrator/src/validate_proposal.rs`)

### Summary

In `validate_proposal`, the call to `valid_proposals.insert_proposal(...)` is made **unconditionally before** the `ProposalFinMismatch` guard. This is the direct Sequencer analog of the MintbaseStore `nft_revoke` bug: an irreversible state mutation (storing the proposal as valid) occurs outside the conditional block that determines whether the action is warranted.

### Finding Description

In `crates/apollo_consensus_orchestrator/src/validate_proposal.rs`, the `validate_proposal` function performs the following sequence at lines 238–249:

```rust
// Update valid_proposals before sending fin to avoid a race condition
// with `repropose` being called before `valid_proposals` is updated.
let mut valid_proposals = args.valid_proposals.lock().unwrap();
valid_proposals.insert_proposal(args.init, content, &args.proposal_id, finished_info);  // line 241

// TODO(matan): Switch to signature validation.
if built_block != received_fin.proposal_commitment {                                      // line 244
    CONSENSUS_PROPOSAL_FIN_MISMATCH.increment(1);
    return Err(ValidateProposalError::ProposalFinMismatch);
}

Ok(built_block)
``` [1](#0-0) 

The `insert_proposal` call at line 241 stores the proposal — keyed by `(height, round)` with the batcher-computed commitment `C_batcher` — into the shared `valid_proposals` map **before** the check at line 244 that verifies `C_batcher == received_fin.proposal_commitment` (`C_network`). When `C_batcher ≠ C_network`, the function returns `Err(ProposalFinMismatch)` and the `fin_sender` is dropped (so consensus never receives a commitment to vote on), but the entry is already durably written into `valid_proposals`.

The `insert_proposal` function itself stores the batcher-derived commitment:

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
    // ...
    let previous = by_round.insert(round, (proposal_commitment, ...));
    assert!(previous.is_none(), ...);
}
``` [2](#0-1) 

The `decision_reached` path then looks up the proposal by the consensus-agreed commitment:

```rust
let (init, transactions, proposal_id, finished_info) = {
    let mut proposals = self.valid_proposals.lock().unwrap();
    let (init, transactions, proposal_id, finished_info) =
        proposals.get_proposal(&height, &round, &commitment).clone();
    ...
};
``` [3](#0-2) 

And `get_proposal` asserts the stored commitment matches the requested one:

```rust
assert_eq!(
    stored_commitment, commitment,
    "Proposal commitment mismatch for height {height} round {round}: ..."
);
``` [4](#0-3) 

### Impact Explanation

Two concrete broken invariants result from the unconditional insertion:

**1. Wrong block committed (High — wrong authoritative RPC/state view):**
A malicious proposer sends the same proposal to all validators but crafts the `ProposalFin` with `C_network ≠ C_batcher` only for a targeted validator. Other validators receive `C_batcher` in their `ProposalFin`, validate successfully, and vote for `C_batcher`. Quorum forms around `C_batcher`. `decision_reached` is called on the targeted validator with `C_batcher`. Because the targeted validator already stored the proposal under `C_batcher` (before returning `ProposalFinMismatch`), `get_proposal` succeeds and the validator commits the block — a block it explicitly rejected. The validator's consensus state is permanently inconsistent: it rejected the proposal but committed the block.

**2. Panic / node crash (High — liveness):**
A malicious proposer sends a proposal where the targeted validator's batcher computes `C_batcher`, but the `ProposalFin` carries `C_network ≠ C_batcher`. The targeted validator stores the entry under `C_batcher` and returns an error. Other validators compute `C_network` (because the proposer sent them different transaction content) and vote for `C_network`. Quorum forms around `C_network`. `decision_reached` is called with `C_network`. The targeted validator's `get_proposal` finds the entry stored under `C_batcher`, and the `assert_eq!(stored_commitment, commitment, ...)` fires — crashing the node.

### Likelihood Explanation

The trigger requires a proposer to send a `ProposalFin` whose `proposal_commitment` field does not match the batcher's computed `partial_block_hash`. This is reachable by:
- A Byzantine proposer deliberately crafting mismatched `ProposalFin` messages to different validators
- A software bug in the proposer's commitment computation path

The code comment at line 238 ("Update valid_proposals before sending fin to avoid a race condition") confirms the ordering was an intentional design choice, not an oversight, making it unlikely to be caught by code review.

### Recommendation

Move `valid_proposals.insert_proposal(...)` to **after** the `ProposalFinMismatch` guard:

```rust
// TODO(matan): Switch to signature validation.
if built_block != received_fin.proposal_commitment {
    CONSENSUS_PROPOSAL_FIN_MISMATCH.increment(1);
    return Err(ValidateProposalError::ProposalFinMismatch);
}

// Only store the proposal after all validation checks pass.
let mut valid_proposals = args.valid_proposals.lock().unwrap();
valid_proposals.insert_proposal(args.init, content, &args.proposal_id, finished_info);

Ok(built_block)
```

The race-condition concern cited in the comment (repropose racing with the insertion) is addressed by the fact that `repropose` is only called after consensus receives a commitment via `fin_sender`, which is only sent after `validate_proposal` returns `Ok`. Since `fin_sender` is sent in `validate_and_send` after `validate_proposal` returns, and `repropose` is triggered by the consensus state machine only after receiving that commitment, moving the insertion after the guard preserves the ordering guarantee.

### Proof of Concept

1. Validator receives a proposal for `(height=H, round=R)`.
2. Batcher executes the transactions and computes `C_batcher = hash(partial_block_hash, fee_proposal)`.
3. The received `ProposalFin` carries `C_network ≠ C_batcher`.
4. `validate_proposal` reaches line 241: `valid_proposals.insert_proposal(...)` stores the entry under `(H, R)` with commitment `C_batcher`.
5. Line 244: `built_block != received_fin.proposal_commitment` → `true` → returns `Err(ProposalFinMismatch)`.
6. `validate_and_send` propagates the error; `fin_sender` is dropped; consensus gets no commitment from this validator.
7. Other validators voted for `C_batcher`; quorum forms; `decision_reached(H, R, C_batcher)` is called.
8. `get_proposal(H, R, C_batcher)` finds the entry (stored in step 4) and returns it.
9. The validator commits the block — a block it explicitly rejected at step 5. [1](#0-0) [5](#0-4)

### Citations

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L238-249)
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
```

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
