### Title
`valid_proposals` mutated before `ProposalFinMismatch` check enables panic-induced consensus crash on reproposal — (`File: crates/apollo_consensus_orchestrator/src/validate_proposal.rs`)

---

### Summary

In `validate_proposal`, `valid_proposals.insert_proposal(...)` is called **before** the `built_block != received_fin.proposal_commitment` check. If that check fails, the proposal is permanently stored in `valid_proposals` keyed by the batcher's commitment (`built_block`), even though validation returned `Err(ProposalFinMismatch)`. When a later `repropose` call arrives with a different commitment (the one that actually reached prevote quorum), `get_proposal` hits a hard `assert_eq!` on the stored vs. requested commitment, panics, and poisons the shared `Mutex<BuiltProposals>`. Every subsequent lock attempt then panics with "Lock was poisoned due to a previous panic", crashing the consensus orchestrator.

---

### Finding Description

In `validate_proposal.rs`, the final two operations are ordered as follows:

```rust
// Update valid_proposals before sending fin to avoid a race condition
// with `repropose` being called before `valid_proposals` is updated.
let mut valid_proposals = args.valid_proposals.lock().unwrap();
valid_proposals.insert_proposal(args.init, content, &args.proposal_id, finished_info); // ← state mutated here

// TODO(matan): Switch to signature validation.
if built_block != received_fin.proposal_commitment {          // ← check happens AFTER
    CONSENSUS_PROPOSAL_FIN_MISMATCH.increment(1);
    return Err(ValidateProposalError::ProposalFinMismatch);   // ← too late; slot already occupied
}
``` [1](#0-0) 

`insert_proposal` derives the stored commitment from `finished_info.proposal_commitment.partial_block_hash` (the batcher's output) and inserts it under `(height, round)` with a hard `assert!(previous.is_none())` guard: [2](#0-1) 

When `ProposalFinMismatch` fires, the slot for `(height, round)` is already occupied with the batcher's commitment `Y`. The function returns an error, `fin_sender` is never sent, and the validator does not vote. But `valid_proposals` now permanently holds `Y` for that `(height, round)`.

Later, when the consensus state machine requests `Repropose(commitment=X, valid_round=r)` (where `X` is the commitment that reached prevote quorum on other validators), `repropose` calls `update_for_reproposal`, which calls `get_proposal`:

```rust
let (init, txs, finished_info) = self
    .valid_proposals
    .lock()
    .expect("Lock on active proposals was poisoned due to a previous panic")
    .update_for_reproposal(&height, &proposal_commitment, &build_param);
``` [3](#0-2) 

`get_proposal` asserts the stored commitment equals the requested one:

```rust
assert_eq!(
    stored_commitment, commitment,
    "Proposal commitment mismatch for height {height} round {round}: \
     stored={stored_commitment}, requested={commitment}"
);
``` [4](#0-3) 

`stored_commitment = Y`, `commitment = X`, `Y ≠ X` → **hard panic**. Because `update_for_reproposal` is called while holding the `MutexGuard`, the panic poisons the mutex. Every subsequent `valid_proposals.lock().expect(...)` call panics, making the consensus orchestrator unrecoverable without a restart.

---

### Impact Explanation

A Byzantine proposer can crash the consensus orchestrator of any targeted validator that is scheduled to be the proposer in a subsequent round. The crash is permanent (mutex poisoned) until the node is restarted. During the outage, the affected validator cannot participate in consensus, reducing the effective validator set and potentially stalling finality if the affected node holds critical voting weight.

This maps to **High** impact: the consensus admission path accepts a structurally invalid proposal (mismatched commitment) into `valid_proposals`, and the resulting state corruption causes a deterministic crash on the next reproposal attempt.

---

### Likelihood Explanation

The attack requires a Byzantine proposer who:
1. Streams different transaction batches to different validators (so their batchers compute different commitments).
2. Sends `ProposalFin.proposal_commitment = X` (matching the majority's batcher output) to all validators, but sends different transactions to the targeted validator so its batcher computes `Y ≠ X`.
3. Knows (or guesses) which validator will be the proposer in the next round (deterministic in Tendermint from the validator set and round number).

This is a targeted, multi-step Byzantine attack. It is not triggerable by an honest-but-faulty proposer. Likelihood is **Low-Medium**.

---

### Recommendation

Move `insert_proposal` to after the `ProposalFinMismatch` check so that the shared state is only mutated when validation fully succeeds:

```rust
// TODO(matan): Switch to signature validation.
if built_block != received_fin.proposal_commitment {
    CONSENSUS_PROPOSAL_FIN_MISMATCH.increment(1);
    return Err(ValidateProposalError::ProposalFinMismatch);
}

// Only insert after all checks pass.
let mut valid_proposals = args.valid_proposals.lock().unwrap();
valid_proposals.insert_proposal(args.init, content, &args.proposal_id, finished_info);
Ok(built_block)
```

The comment explaining the race condition with `repropose` should be re-evaluated: `repropose` is only called by the consensus state machine after a prevote quorum is reached, which cannot happen before `validate_proposal` returns `Ok` and sends the commitment via `fin_sender`. Therefore, the race condition the comment describes does not exist for the `ProposalFinMismatch` path, and the insertion can safely be deferred.

Additionally, replace the `assert_eq!` in `get_proposal` with a recoverable error to prevent a single bad state entry from poisoning the mutex and crashing the entire orchestrator.

---

### Proof of Concept

1. **Setup**: 4-validator network. Validators: A (proposer in round 1), B, C, D. Proposer in round 0: B (Byzantine).

2. **Round 0 — Byzantine proposal**:
   - B streams transaction batch `T1` to validators B, C, D → their batchers compute commitment `X`.
   - B streams transaction batch `T2` (different) to validator A → A's batcher computes commitment `Y ≠ X`.
   - B sends `ProposalFin { proposal_commitment: X, ... }` to all validators.

3. **Validator A processes the proposal**:
   - `handle_proposal_part` receives `Fin`, calls `batcher.finish_proposal(...)` → returns `partial_block_hash` for `T2` → `built_block = Y`.
   - `validate_proposal` reaches line 241: `valid_proposals.insert_proposal(init, content, &proposal_id, finished_info)` → inserts `(height=H, round=0) → Y`.
   - Line 244: `Y != X` → returns `Err(ProposalFinMismatch)`. Validator A does not vote. [1](#0-0) 

4. **Round 0 ends**: B, C, D prevote for `X`. Prevote quorum reached for `X`. No precommit quorum → round 0 times out.

5. **Round 1 — Validator A is proposer**:
   - Consensus state machine emits `SMRequest::Repropose(commitment=X, valid_round=0)`.
   - `repropose(X, BuildParam { valid_round: Some(0), round: 1, ... })` is called.
   - `update_for_reproposal(H, X, ...)` → `get_proposal(H, 0, X)`.
   - Stored commitment for `(H, 0)` is `Y`. `assert_eq!(Y, X)` → **PANIC**. [3](#0-2) 

6. **Mutex poisoned**: The `MutexGuard` is dropped during the panic. All subsequent `valid_proposals.lock().expect("Lock on active proposals was poisoned due to a previous panic")` calls panic. Consensus orchestrator on validator A is permanently crashed until restart. [5](#0-4)

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

**File:** crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs (L928-932)
```rust
        let (init, txs, finished_info) = self
            .valid_proposals
            .lock()
            .expect("Lock on active proposals was poisoned due to a previous panic")
            .update_for_reproposal(&height, &proposal_commitment, &build_param);
```
