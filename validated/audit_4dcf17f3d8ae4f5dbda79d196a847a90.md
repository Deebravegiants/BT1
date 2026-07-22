### Title
Unbounded `fee_proposal_fri` Accepted During Startup Window When `fee_actual` Is `None` - (File: `crates/apollo_consensus_orchestrator/src/validate_proposal.rs`)

### Summary

`is_proposal_init_valid` only enforces the `fee_proposal_fri` margin bound when `proposal_init_validation.fee_actual` is `Some`. When `fee_actual` is `None` — which occurs for the first `fee_proposal_window_size` (10) blocks after genesis or after the V0_14_3 protocol upgrade — any arbitrary `fee_proposal_fri` value in a `ProposalInit` passes validation unchecked. The injected value is then committed to the block header, stored in the `fee_proposals_window`, and later used to compute `fee_actual` (the median of the window), which directly sets the `l2_gas_price` for all subsequent blocks.

### Finding Description

In `is_proposal_init_valid`, the bounds check on `fee_proposal_fri` is guarded by a double-`Some` pattern:

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
        return Err(ValidateProposalError::InvalidProposalInit(...));
    }
}
``` [1](#0-0) 

When `fee_actual` is `None`, the entire block is skipped. No lower bound, no upper bound, no zero-check, no absolute cap. A `ProposalInit` carrying `fee_proposal_fri = GasPrice(u128::MAX)` or `GasPrice(0)` passes this function without error.

The honest proposer path, by contrast, freezes at `l2_gas_price` when `fee_actual` is `None`:

```rust
let Some(fee_actual) = fee_actual else {
    warn!("fee_actual unavailable, freezing fee_proposal at l2_gas_price");
    return self.l2_gas_price;
};
``` [2](#0-1) 

But the validator never checks that the received `fee_proposal_fri` equals `l2_gas_price` (or any other bounded value) during this period.

`fee_actual` is `None` whenever `compute_fee_actual` returns `None`, which happens for the first `fee_proposal_window_size` blocks (currently 10): [3](#0-2) 

The `fee_actual` field in `ProposalInitValidation` is populated from `compute_fee_actual` at both validation call sites: [4](#0-3) 

Once a block is decided, `finalize_decision` calls `record_fee_proposal(height, init.fee_proposal_fri)`, storing the unchecked value into the window: [5](#0-4) 

After `window_size` blocks, `compute_fee_actual` computes the median of these stored values and returns it as `fee_actual`, which then drives `l2_gas_price` for all subsequent blocks. [6](#0-5) 

The `fee_proposal_fri` is also hashed into the `ProposalCommitment` that validators sign: [7](#0-6) 

So validators sign over an unchecked, attacker-controlled value.

### Impact Explanation

A malicious block proposer who controls one or more of the first 10 blocks (or the first 10 V0_14_3 blocks after the protocol upgrade) can set `fee_proposal_fri` to any value — e.g., `u128::MAX` or `0`. These values are:

1. Accepted by all validators (no bounds check when `fee_actual` is `None`).
2. Committed to the block header and stored in `fee_proposals_window`.
3. Used to compute `fee_actual` (median) once the window fills.
4. `fee_actual` then sets `l2_gas_price` for all subsequent blocks.

If the attacker injects `u128::MAX` into enough window slots to dominate the median, `fee_actual` becomes `u128::MAX`, making all transactions unaffordable (economic DoS). If the attacker injects `0`, `fee_actual` collapses to `0` or `min_gas_price`, enabling near-free transactions and undermining the fee market.

This matches the "Incorrect fee, gas, bouncer, resource accounting, refund, balance, or L1 gas price effect with economic impact" impact class.

### Likelihood Explanation

The attack window is the first `fee_proposal_window_size` = 10 blocks after genesis or after the V0_14_3 upgrade. In a small or permissioned validator set (as is typical for Starknet's current sequencer topology), a single node may propose multiple of these blocks. The attack requires no special privileges beyond being selected as proposer — a normal consensus role. The attacker does not need to break cryptography or exploit any external dependency. [8](#0-7) 

### Recommendation

When `fee_actual` is `None`, the validator should enforce that `fee_proposal_fri` equals the expected frozen value (`l2_gas_price`), mirroring the proposer's own behavior:

```rust
// Validate fee_proposal is within the configured margin of fee_actual.
// During initiation (fee_actual is None, <window_size blocks), enforce the freeze value.
match (proposal_init_validation.fee_actual, init_proposed.fee_proposal_fri) {
    (Some(fee_actual), Some(fee_proposal)) => {
        let (lower_bound, upper_bound) = fee_proposal_bounds(
            fee_actual,
            VersionedConstants::latest_constants().fee_proposal_margin_ppt,
        );
        if fee_proposal.0 < lower_bound || fee_proposal.0 > upper_bound {
            return Err(ValidateProposalError::InvalidProposalInit(...));
        }
    }
    (None, Some(fee_proposal)) => {
        // Proposer must freeze at l2_gas_price when window is incomplete.
        if fee_proposal != proposal_init_validation.l2_gas_price_fri {
            return Err(ValidateProposalError::InvalidProposalInit(
                ...,
                format!(
                    "fee_proposal must equal l2_gas_price during startup window: \
                     expected={}, got={}",
                    proposal_init_validation.l2_gas_price_fri.0, fee_proposal.0
                ),
            ));
        }
    }
    _ => {}
}
```

### Proof of Concept

1. Network starts at genesis (height 0). `fee_proposal_window_size = 10`.
2. For heights 0–9, `compute_fee_actual` returns `None` (window not yet full).
3. A malicious proposer at height 0 sends `ProposalInit { fee_proposal_fri: Some(GasPrice(u128::MAX)), ... }`.
4. `is_proposal_init_valid` reaches the fee-proposal check. `proposal_init_validation.fee_actual` is `None`. The `if let (Some(_), Some(_))` pattern does not match. No error is returned.
5. The proposal is accepted. `finalize_decision` calls `record_fee_proposal(BlockNumber(0), Some(GasPrice(u128::MAX)))`.
6. The attacker repeats for heights 1–9 (or as many as they can propose), injecting `u128::MAX` each time.
7. At height 10, `compute_fee_actual` computes the median of `[u128::MAX, u128::MAX, ...]` = `u128::MAX`.
8. `calculate_next_l2_gas_price_for_fin` receives `fee_actual = Some(GasPrice(u128::MAX))` and sets `l2_gas_price` to an extreme value.
9. All subsequent transactions require fees proportional to `u128::MAX`, making the network unusable. [1](#0-0) [9](#0-8)

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

**File:** crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs (L308-310)
```rust
    fn record_fee_proposal(&mut self, height: BlockNumber, fee_proposal_fri: Option<GasPrice>) {
        self.fee_proposals_window.insert(height, fee_proposal_fri);
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

**File:** crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs (L895-900)
```rust
                    fee_actual: compute_fee_actual(
                        &self.fee_proposals_window,
                        init.height,
                        VersionedConstants::latest_constants().fee_proposal_window_size,
                    ),
                };
```

**File:** crates/apollo_consensus_orchestrator/src/dynamic_gas_price/mod.rs (L56-67)
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
```

**File:** crates/apollo_consensus_orchestrator/src/dynamic_gas_price/mod.rs (L82-91)
```rust
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

**File:** crates/apollo_versioned_constants/resources/orchestrator_versioned_constants_0_14_4.json (L1-9)
```json
{
    "fee_proposal_margin_ppt": 2,
    "fee_proposal_window_size": 10,
    "gas_price_max_change_denominator": 48,
    "gas_target": 1040000000,
    "max_block_size": 5800000000,
    "min_gas_price": "0x1dcd65000",
    "l1_gas_price_margin_percent": 10
}
```
