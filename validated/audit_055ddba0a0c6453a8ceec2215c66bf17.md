### Title
Unconstrained `fee_proposal_fri` During Startup Window Poisons Fee Market and `l2_gas_price` - (File: crates/apollo_consensus_orchestrator/src/validate_proposal.rs)

### Summary

During the first `fee_proposal_window_size` blocks after Starknet V0_14_3 activation, the validator unconditionally skips all bounds enforcement on the proposer-supplied `fee_proposal_fri` field. Any validator selected as proposer during this window can broadcast an arbitrary `fee_proposal_fri` value (e.g., `u128::MAX`), have it accepted by every honest validator, and permanently poison the `fee_proposals_window` that drives `fee_actual` and therefore `l2_gas_price` for all subsequent blocks.

### Finding Description

`is_proposal_init_valid` in `validate_proposal.rs` enforces that `fee_proposal_fri` lies within a geometric band around `fee_actual`:

```rust
// Validate fee_proposal is within the configured margin of fee_actual.
// During initiation (fee_actual is None, <window_size blocks), bounds are not enforced.
if let (Some(fee_actual), Some(fee_proposal)) =
    (proposal_init_validation.fee_actual, init_proposed.fee_proposal_fri)
{
    let (lower_bound, upper_bound) = fee_proposal_bounds(...);
    if fee_proposal.0 < lower_bound || fee_proposal.0 > upper_bound {
        return Err(ValidateProposalError::InvalidProposalInit(...));
    }
}
``` [1](#0-0) 

When `fee_actual` is `None` — which is the case for every block in the first `window_size` heights — the entire `if let` body is skipped. No lower or upper bound is applied to the proposer-supplied value. The only check that runs is the presence/absence check (must be `Some` for V0_14_3+): [2](#0-1) 

The proposer's honest fallback is to freeze at `l2_gas_price`: [3](#0-2) 

But the validator never checks that the received value equals or is close to `l2_gas_price`. Any `GasPrice(u128::MAX)` passes.

After the proposal is decided, `finalize_decision` records the proposer-supplied value verbatim: [4](#0-3) 

`compute_fee_actual` then computes the median of the window: [5](#0-4) 

If the attacker controls the majority of proposals during the startup window, the median becomes the attacker's chosen value. `calculate_next_l2_gas_price_for_fin` then propagates this into `l2_gas_price` for every subsequent block.

### Impact Explanation

`l2_gas_price` is the per-unit price charged to every transaction. Setting it to `u128::MAX` makes every transaction's fee overflow or exceed any `max_price_per_unit` bound, causing all user transactions to be rejected by the mempool's gas-price threshold check and by blockifier fee enforcement. The network's transaction throughput drops to zero for all account transactions. This is a direct, quantifiable economic impact: "Incorrect fee, gas, bouncer, resource accounting, refund, balance, or L1 gas price effect with economic impact."

The corrupted value is `fee_proposals_window[h] = u128::MAX` for each poisoned height `h`, which propagates to `fee_actual = u128::MAX` and then to `l2_gas_price = u128::MAX` for all blocks after the window closes.

### Likelihood Explanation

The attack window is bounded to the first `fee_proposal_window_size` blocks after V0_14_3 activation. Within that window, the attacker needs to be selected as proposer for a majority of blocks (to dominate the median). In a small validator set or at network genesis this is feasible for a single Byzantine validator. The trigger is a standard consensus proposer role — no out-of-band privilege is required. The attack is permanent: once the window closes with poisoned values, `fee_actual` is fixed and the bounds check that would normally correct drift is anchored to the poisoned median.

### Recommendation

During the startup window, bound `fee_proposal_fri` against the local `l2_gas_price` rather than leaving it unconstrained. For example, apply the same geometric margin used post-window but anchored to `l2_gas_price` as the reference:

```rust
// Startup fallback: bound against l2_gas_price when fee_actual is unavailable.
if let Some(fee_proposal) = init_proposed.fee_proposal_fri {
    let reference = proposal_init_validation.fee_actual
        .unwrap_or(proposal_init_validation.l2_gas_price_fri);
    let (lower, upper) = fee_proposal_bounds(
        reference,
        VersionedConstants::latest_constants().fee_proposal_margin_ppt,
    );
    if fee_proposal.0 < lower || fee_proposal.0 > upper {
        return Err(ValidateProposalError::InvalidProposalInit(...));
    }
}
```

This closes the unconstrained window without breaking the honest proposer path (which already freezes at `l2_gas_price`).

### Proof of Concept

1. Network activates V0_14_3. `fee_proposals_window` is empty; `compute_fee_actual` returns `None` for all heights below `window_size`.
2. Attacker is selected as proposer for height 0. Attacker broadcasts `ProposalInit { fee_proposal_fri: Some(GasPrice(u128::MAX)), starknet_version: V0_14_3, ... }`.
3. Every honest validator calls `is_proposal_init_valid`. `proposal_init_validation.fee_actual` is `None`. The `if let (Some(fee_actual), Some(fee_proposal))` arm

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

**File:** crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs (L478-482)
```rust
        let Some(fee_actual) = fee_actual else {
            warn!("fee_actual unavailable, freezing fee_proposal at l2_gas_price");
            SNIP35_FEE_PROPOSAL_FRI.set_lossy(self.l2_gas_price.0);
            return self.l2_gas_price;
        };
```

**File:** crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs (L517-519)
```rust
        self.update_l2_gas_price(height, l2_gas_used);
        self.record_fee_proposal(height, init.fee_proposal_fri);

```

**File:** crates/apollo_consensus_orchestrator/src/dynamic_gas_price/mod.rs (L56-92)
```rust
pub fn compute_fee_actual(
    fee_proposals_window: &BTreeMap<BlockNumber, Option<GasPrice>>,
    height: BlockNumber,
    window_size: u64,
) -> Option<GasPrice> {
    let Some(start) = height.0.checked_sub(window_size) else {
        warn!(
            "Cannot compute fee_actual for height {height}: height is below window_size \
             ({window_size})"
        );
        return None;
    };
    let window_size_usize = usize::try_from(window_size).expect("window_size fits in usize");
    let mut window = Vec::with_capacity(window_size_usize);
    for source_height in (start..height.0).map(BlockNumber) {
        match fee_proposals_window.get(&source_height) {
            Some(Some(price)) => window.push(*price),
            Some(None) | None => {
                warn!(
                    "Cannot compute fee_actual for height {height}: fee_proposals_window has no \
                     recorded fee_proposal for height {source_height}"
                );
                return None;
            }
        }
    }
    window.sort();
    let mid = window_size_usize / 2;
    let median = if window_size_usize.is_multiple_of(2) {
        // Even: average of the two middle values, rounded down.
        // Overflow-safe averaging: a + (b - a) / 2 (safe because sorted, so b >= a).
        GasPrice(window[mid - 1].0 + (window[mid].0 - window[mid - 1].0) / 2)
    } else {
        window[mid]
    };
    Some(median)
}
```
