### Title
Unconstrained `fee_proposal_fri` During Startup Window Allows Malicious Proposer to Permanently Poison the SNIP-35 Fee Market — (File: `crates/apollo_consensus_orchestrator/src/validate_proposal.rs`)

---

### Summary

`is_proposal_init_valid` enforces a geometric margin on the proposer-stated `fee_proposal_fri` only when `fee_actual` is `Some`. During the startup window — the first `window_size` blocks, when `fee_actual` is always `None` — the bounds check is silently skipped. A malicious proposer selected during this window can broadcast any `fee_proposal_fri` value (including `u128::MAX`) and every honest validator will accept it, bind it into the `ProposalCommitment`, and persist it in the `fee_proposals_window`. Once the window fills, the poisoned median becomes the permanent `fee_actual` floor, locking the SNIP-35 fee market at an attacker-chosen price for all subsequent blocks.

---

### Finding Description

In `is_proposal_init_valid` the fee-proposal range check is guarded by an `if let` that fires only when both `fee_actual` and `fee_proposal` are `Some`:

```rust
// Validate fee_proposal is within the configured margin of fee_actual.
// During initiation (fee_actual is None, <window_size blocks), bounds are not enforced.
if let (Some(fee_actual), Some(fee_proposal)) =
    (proposal_init_validation.fee_actual, init_proposed.fee_proposal_fri)
{
    ...
    if fee_proposal.0 < lower_bound || fee_proposal.0 > upper_bound {
        return Err(...);