### Title
Unbounded `fee_proposal_fri` Accepted During Startup Window Corrupts `fee_actual` and Inflates Minimum L2 Gas Price — (`crates/apollo_consensus_orchestrator/src/validate_proposal.rs`)

### Summary

During the first `fee_proposal_window_size` blocks ("startup window"), `is_proposal_init_valid` skips all bounds enforcement on `fee_proposal_fri` because `fee_actual` is `None`. A malicious proposer can set `fee_proposal_fri` to an arbitrarily large value (up to `u128::MAX`). That value is unconditionally recorded into `fee_proposals_window`, which feeds `compute_fee_actual`. Once the window fills, the inflated median becomes `fee_actual`, which `calculate_next_l2_gas_price_for_fin` uses as the hard floor for the L2 gas price — permanently pricing all transactions out of the network until the inflated entries age out of the window.

### Finding Description

In `is_proposal_init_valid`, the `fee_proposal_fri` range check is gated on `fee_actual` being `Some`:

```rust
// Validate fee_proposal is within the configured margin of fee_actual.
// During initiation (fee_actual is None, <window_size blocks), bounds are not enforced.
if let (Some(fee_actual), Some(fee_proposal)) =
    (proposal_init_validation.fee_actual, init_proposed.fee_proposal_fri)
{
    let (lower_bound, upper_bound) = fee_proposal_bounds(...);
    if fee_proposal.0 < lower_bound || fee_proposal.0 > upper_bound { ... }
}
``` [1](#0-0) 

When `fee_actual` is `None` (the first `window_size` blocks), the `if let` arm never fires and any `fee_proposal_fri` — including `u128::MAX` — passes validation. The accepted value is then committed to persistent state in two ways:

**1. Recorded into `fee_proposals_window`** at decision time:

```rust
self.record_fee_proposal(height, init.fee_proposal_fri);
``` [2](#0-1) 

**2. Stored in `BlockHeaderWithoutHash` and forwarded to state sync:**

```rust
fee_proposal_fri: init.fee_proposal_fri,
``` [3](#0-2) 

Once the window is full, `compute_fee_actual` returns the median of the stored values: [4](#0-3) 

That median is then used as the hard floor for the next L2 gas price:

```rust
let effective_min = match fee_actual {
    Some(fa) => GasPrice(max(config_min.0, fa.0)),
    None => config_min,
};
calculate_next_base_gas_price(current_l2_gas_price, l2_gas_used, gas_target, effective_min)
``` [5](#0-4) 

And `calculate_next_base_gas_price` enforces that the price never falls below `effective_min`: [6](#0-5) 

The analog to the JBX `reservedRate` bug is exact: a numeric field (`fee_proposal_fri` / `reservedRate`) is recorded without an upper-bound check during an admission phase, the stored value feeds a downstream aggregate (`compute_fee_actual` / `totalRedemptionWeight`), and the corrupted aggregate drives an economic calculation (`effective_min` L2 gas price / `reclaimAmount`) that harms every subsequent user.

### Impact Explanation

If a malicious proposer controls more than ⌊`window_size`/2⌋ proposals during the startup window and sets `fee_proposal_fri = u128::MAX` in each, `compute_fee_actual` returns `u128::MAX` once the window fills. `calculate_next_l2_gas_price_for_fin` then sets `effective_min = u128::MAX`, and `calculate_next_base_gas_price` ratchets the L2 gas price up to `u128::MAX`. Every subsequent transaction's `max_price_per_unit` check fails, making the network economically unusable until the inflated entries age out of the window — a window-sized number of blocks later. This is a **Critical** incorrect fee/gas accounting effect with direct economic impact.

### Likelihood Explanation

The startup window is the only period where `fee_actual` is `None`. Any consensus participant who is selected as proposer during those blocks can inject an arbitrary `fee_proposal_fri`. Controlling a majority of the startup-window proposals requires winning the proposer lottery more than ⌊`window_size`/2⌋ times, which is feasible for a validator with a proportionally large stake or in a small validator set. The attack is unprivileged (no special key or admin role required) and leaves no on-chain trace distinguishable from an honest proposal.

### Recommendation

Add an absolute upper-bound check on `fee_proposal_fri` that fires regardless of whether `fee_actual` is available. A natural ceiling is a small multiple of the current `l2_gas_price` (e.g., `l2_gas_price * MAX_STARTUP_FEE_PROPOSAL_MULTIPLIER`), mirroring the multiplicative margin used once the window is full. Alternatively, enforce that `fee_proposal_fri ≤ some_protocol_max_gas_price` constant, analogous to `JBConstants.MAX_RESERVED_RATE` in the JBX fix.

### Proof of Concept

1. Network launches; `fee_actual` is `None` for the first `window_size` blocks.
2. A malicious proposer (or coalition) wins the proposer role for more than half those blocks and sets `fee_proposal_fri = u128::MAX` in each `ProposalInit`.
3. `is_proposal_init_valid` skips the bounds check (`fee_actual` is `None`); each proposal passes.
4. `finalize_decision` calls `record_fee_proposal(height, Some(GasPrice(u128::MAX)))` for each winning block.
5. At height `window_size`, `compute_fee_actual` sorts the window and returns the median = `u128::MAX`.
6. `calculate_next_l2_gas_price_for_fin` sets `effective_min = max(config_

### Citations

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

**File:** crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs (L409-409)
```rust
            fee_proposal_fri: init.fee_proposal_fri,
```

**File:** crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs (L518-518)
```rust
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

**File:** crates/apollo_consensus_orchestrator/src/fee_market/mod.rs (L72-76)
```rust
    let effective_min = match fee_actual {
        Some(fa) => GasPrice(max(config_min.0, fa.0)),
        None => config_min,
    };
    calculate_next_base_gas_price(current_l2_gas_price, l2_gas_used, gas_target, effective_min)
```

**File:** crates/apollo_consensus_orchestrator/src/fee_market/mod.rs (L103-114)
```rust
    // If the current price is below the minimum, apply a gradual adjustment and return early.
    // This allows the price to increase by at most 1/MIN_GAS_PRICE_INCREASE_DENOMINATOR per block.
    if price < min_gas_price {
        let max_increase = price.0 / MIN_GAS_PRICE_INCREASE_DENOMINATOR;
        let adjusted = price.0 + max_increase;
        // Cap at min_gas_price to avoid overshooting
        let adjusted_price = adjusted.min(min_gas_price.0);
        info!(
            "Fee Market: Price {} below minimum gas price {}, adjusted price: {} )",
            price.0, min_gas_price.0, adjusted_price
        );
        return GasPrice(adjusted_price);
```
