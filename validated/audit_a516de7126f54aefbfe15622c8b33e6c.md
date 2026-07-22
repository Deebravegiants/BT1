### Title
`fee_proposal_fri` Bounds Check Skipped During Startup Window Allows Proposer to Inflate Future L2 Gas Prices — (`crates/apollo_consensus_orchestrator/src/validate_proposal.rs`)

### Summary

`is_proposal_init_valid` enforces a margin-bounded check on `fee_proposal_fri` only when `fee_actual` is `Some`. During the startup window (first `fee_proposal_window_size` blocks), `fee_actual` is `None` and the bounds check is silently skipped. An elected proposer during this window can set `fee_proposal_fri` to any value — including `u128::MAX` — with no validator rejection. The inflated value is committed into `ProposalCommitment`, stored in `fee_proposals_window`, and propagates into future `fee_actual` and `l2_gas_price_fri` for all subsequent blocks.

### Finding Description

`is_proposal_init_valid` applies two checks to `fee_proposal_fri`:

**Check 1 — Presence (always enforced):** [1](#0-0) 

**Check 2 — Bounds (conditionally enforced):** [2](#0-1) 

The bounds check is gated on `if let (Some(fee_actual), Some(fee_proposal)) = ...`. `fee_actual` is computed by `compute_fee_actual` from `fee_proposals_window`: [3](#0-2) 

`compute_fee_actual` returns `None` until the window accumulates `fee_proposal_window_size` entries. During those startup blocks, the `if let` arm never fires and **any** `fee_proposal_fri` value passes validation.

The proposer always sets `fee_proposal_fri = Some(args.fee_proposal)` in `ProposalInit`: [4](#0-3) 

The validator then uses the proposer-supplied `init.fee_proposal_fri` to compute the `ProposalCommitment` it votes on: [5](#0-4) 

And stores it in `valid_proposals` keyed by that commitment: [6](#0-5) 

After consensus decides, `init.fee_proposal_fri` is recorded into `fee_proposals_window` and forwarded to the cende pipeline: [7](#0-6) 

Once the window fills with inflated values, `fee_actual` becomes inflated. The bounds check then permits `fee_proposal_fri` within `fee_actual * (1 ± margin_ppt/PPT_DENOMINATOR)` — anchored to the inflated reference — so the proposer can sustain the inflation indefinitely. `fee_actual` is then passed to `calculate_next_l2_gas_price_for_fin`: [8](#0-7) 

which uses it to compute the next block's `l2_gas_price_fri` — the actual gas price charged to users.

The asymmetry mirrors the ArmadaGovernor bug exactly: `distribute` has the 5% threshold check applied; `stewardSpend` does not. Here, `fee_proposal_fri` has the margin bounds check applied during normal operation; during startup it does not.

### Impact Explanation

A malicious proposer elected during the startup window sets `fee_proposal_fri = u128::MAX`. All validators accept it (bounds check skipped). After `fee_proposal_window_size` blocks, `fee_actual` saturates near `u128::MAX`. The `fee_proposal_bounds` helper saturates the upper bound to `u128::MAX`: [9](#0-8) 

Future `fee_proposal_fri` can remain at `u128::MAX` indefinitely. `calculate_next_l2_gas_price_for_fin` derives the next `l2_gas_price_fri` from this inflated `fee_actual`, causing every subsequent block to charge users an arbitrarily inflated L2 gas price. This is a direct economic impact: **incorrect fee/gas accounting with economic consequence** matching the Critical impact tier.

Additionally, the `ProposalCommitment` voted on by consensus is `Poseidon(partial_block_hash, fee_proposal_fri)` — an authoritative wrong value committed into the chain's consensus record and forwarded to the cende pipeline as `fee_proposal_info`.

### Likelihood Explanation

The trigger requires being the elected proposer for at least one block during the startup window (first `fee_proposal_window_size` blocks after genesis or a protocol upgrade). In a decentralized BFT validator set, any validator can be elected proposer by the committee rotation. The startup window is a predictable, bounded period. A single inflated block is sufficient to seed the window; the effect compounds as the window fills.

### Recommendation

Add an absolute floor/ceiling on `fee_proposal_fri` independent of `fee_actual`, enforced even when `fee_actual` is `None`. For example, require `fee_proposal_fri` to lie within `[min_l2_gas_price, max_l2_gas_price]` at all times. This mirrors the existing `min_l2_gas_price_per_height` guard already applied to `l2_gas_price_fri` and closes the startup-window bypass without breaking the intentional "no relative bounds during initiation" design.

### Proof of Concept

```
1. Network launches; fee_proposals_window is empty → compute_fee_actual returns None.
2. Malicious proposer is elected for block N (N < fee_proposal_window_size).
3. Proposer constructs ProposalInit { fee_proposal_fri: Some(GasPrice(u128::MAX)), ... }.
4. is_proposal_init_valid:
     - presence check: (Some(u128::MAX), true) → arm `_ => {}` → OK
     - bounds check:   if let (Some(fee_actual), Some(_)) = (None, Some(u128::MAX))
                       → arm does not fire → OK
5. All validators accept; consensus decides; ProposalCommitment = Poseidon(partial, u128::MAX).
6. decision_reached records fee_proposals_window[N] = Some(u128::MAX).
7. After fee_proposal_window_size blocks, compute_fee_actual returns Some(≈u128::MAX).
8. fee_proposal_bounds(u128::MAX, margin_ppt) → (lower≈u128::MAX, upper=u128::MAX).
9. Proposer continues setting fee_proposal_fri = u128::MAX; bounds check passes.
10. calculate_next_l2_gas_price_for_fin(l2_gas_price, height, l2_gas_used, None, [], Some(u128::MAX))
    → next_l2_gas_price ≈ u128::MAX.
11. All subsequent blocks charge l2_gas_price_fri ≈ u128::MAX; users cannot afford transactions.
```

### Citations

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L370-394)
```rust
    // fee_proposal is required iff Starknet version >= V0_14_3.
    let fee_proposal_required = init_proposed.starknet_version >= StarknetVersion::V0_14_3;
    match (init_proposed.fee_proposal_fri, fee_proposal_required) {
        (Some(_), false) => {
            return Err(ValidateProposalError::InvalidProposalInit(
                init_proposed.clone(),
                proposal_init_validation.clone(),
                format!(
                    "fee_proposal must be absent before V0_14_3, got Some at version {}",
                    init_proposed.starknet_version
                ),
            ));
        }
        (None, true) => {
            return Err(ValidateProposalError::InvalidProposalInit(
                init_proposed.clone(),
                proposal_init_validation.clone(),
                format!(
                    "fee_proposal is required at V0_14_3+, got None at version {}",
                    init_proposed.starknet_version
                ),
            ));
        }
        _ => {}
    }
```

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L396-416)
```rust
    // Validate fee_proposal is within the configured margin of fee_actual.
    // During initiation (fee_actual is None, <window_size blocks), bounds are not enforced.
    if let (Some(fee_actual), Some(fee_proposal)) =
        (proposal_init_validation.fee_actual, init_proposed.fee_proposal_fri)
    {
        let (lower_bound, upper_bound) = fee_proposal_bounds(
            fee_actual,
            VersionedConstants::latest_constants().fee_proposal_margin_ppt,
        );
        if fee_proposal.0 < lower_bound || fee_proposal.0 > upper_bound {
            return Err(ValidateProposalError::InvalidProposalInit(
                init_proposed.clone(),
                proposal_init_validation.clone(),
                format!(
                    "Fee proposal out of bounds: fee_actual={}, fee_proposal={}, allowed \
                     range=[{lower_bound}, {upper_bound}]",
                    fee_actual.0, fee_proposal.0
                ),
            ));
        }
    }
```

**File:** crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs (L187-190)
```rust
        let proposal_commitment = proposal_commitment_from(
            finished_info.proposal_commitment.partial_block_hash,
            init.fee_proposal_fri,
        );
```

**File:** crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs (L607-611)
```rust
                // Forward the proposer's stated fee_proposal_fri (from ProposalInit)
                // to the centralized cende pipeline. The centralized side persists this in
                // its own storage namespace, separate from FeeMarketInfo. Pre-V0_14_3 blocks
                // have `init.fee_proposal_fri == None`.
                fee_proposal_info: FeeProposalInfo { fee_proposal_fri: init.fee_proposal_fri },
```

**File:** crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs (L895-900)
```rust
                    fee_actual: compute_fee_actual(
                        &self.fee_proposals_window,
                        init.height,
                        VersionedConstants::latest_constants().fee_proposal_window_size,
                    ),
                };
```

**File:** crates/apollo_consensus_orchestrator/src/build_proposal.rs (L187-188)
```rust
        fee_proposal_fri: Some(args.fee_proposal),
    };
```

**File:** crates/apollo_consensus_orchestrator/src/build_proposal.rs (L326-333)
```rust
                let next_l2_gas_price = calculate_next_l2_gas_price_for_fin(
                    args.l2_gas_price,
                    args.build_param.height,
                    info.l2_gas_used,
                    args.override_l2_gas_price_fri,
                    &args.min_l2_gas_price_per_height,
                    args.fee_actual,
                );
```

**File:** crates/apollo_consensus_orchestrator/src/dynamic_gas_price/mod.rs (L144-151)
```rust
pub(crate) fn fee_proposal_bounds(fee_actual: GasPrice, margin_ppt: u128) -> (u128, u128) {
    let denom = U256::from(PPT_DENOMINATOR);
    let scaled = denom + U256::from(margin_ppt);
    let fee_actual_u256 = U256::from(fee_actual.0);
    let upper = u128::try_from(fee_actual_u256 * scaled / denom).unwrap_or(u128::MAX);
    let lower = u128::try_from(fee_actual_u256 * denom / scaled).unwrap_or(0);
    (lower, upper)
}
```

**File:** crates/apollo_consensus_orchestrator/src/dynamic_gas_price/mod.rs (L163-171)
```rust
pub(crate) fn proposal_commitment_from(
    partial: PartialBlockHash,
    fee_proposal: Option<GasPrice>,
) -> ProposalCommitment {
    let Some(fee_proposal) = fee_proposal else {
        return ProposalCommitment(partial.0);
    };
    ProposalCommitment(Poseidon::hash_array(&[partial.0, Felt::from(fee_proposal.0)]))
}
```
