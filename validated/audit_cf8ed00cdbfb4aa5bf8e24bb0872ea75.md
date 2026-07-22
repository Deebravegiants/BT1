### Title
Unconstrained `fee_proposal_fri` During Startup Window Allows Arbitrary L2 Gas Price Manipulation — (`crates/apollo_consensus_orchestrator/src/validate_proposal.rs`)

---

### Summary

`is_proposal_init_valid` explicitly skips all bounds enforcement on the proposer-stated `fee_proposal_fri` when `fee_actual` is `None`. `fee_actual` is `None` for the first `fee_proposal_window_size` blocks (startup / near-genesis). During that window a proposer can publish any `fee_proposal_fri` value — including `0` or `u128::MAX` — and every validator will accept it. Those values are recorded in `fee_proposals_window` and become the median (`fee_actual`) that floors the EIP-1559 L2 gas price for all subsequent blocks.

---

### Finding Description

`is_proposal_init_valid` in `crates/apollo_consensus_orchestrator/src/validate_proposal.rs` validates the `ProposalInit` message received from a peer proposer. For Starknet ≥ V0_14_3 it requires `fee_proposal_fri` to be `Some`, but the only range check is:

```rust
// Validate fee_proposal is within the configured margin of fee_actual.
// During initiation (fee_actual is None, <window_size blocks), bounds are not enforced.
if let (Some(fee_actual), Some(fee_proposal)) =
    (proposal_init_validation.fee_actual, init_proposed.fee_proposal_fri)
{
    ...
}
``` [1](#0-0) 

The guard is a conjunctive `if let`: when `fee_actual` is `None` the entire block is skipped. `fee_actual` is `None` whenever `compute_fee_actual` cannot fill a complete window:

```rust
let Some(start) = height.0.checked_sub(window_size) else {
    warn!("Cannot compute fee_actual for height {height}: height is below window_size ...");
    return None;
};
``` [2](#0-1) 

`fee_actual` is passed into `ProposalInitValidation` at both call sites:

```rust
fee_actual: compute_fee_actual(
    &self.fee_proposals_window,
    init.height,
    VersionedConstants::latest_constants().fee_proposal_window_size,
),
``` [3](#0-2) 

After a proposal is decided, the proposer's `fee_proposal_fri` is stored verbatim in `fee_proposals_window`:

```rust
fn record_fee_proposal(&mut self, height: BlockNumber, fee_proposal_fri: Option<GasPrice>) {
    self.fee_proposals_window.insert(height, fee_proposal_fri);
}
``` [4](#0-3) 

Once the window fills, `fee_actual` (the median of those stored values) becomes the floor for the EIP-1559 L2 gas price:

```rust
let effective_min = match fee_actual {
    Some(fa) => GasPrice(max(config_min.0, fa.0)),
    None => config_min,
};
calculate_next_base_gas_price(current_l2_gas_price, l2_gas_used, gas_target, effective_min)
``` [5](#0-4) 

The `fee_proposal_fri` is also bound into the `ProposalCommitment` that consensus signs:

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
``` [6](#0-5) 

Because the validator computes the commitment using the proposer's stated `fee_proposal_fri` (line 584 of `validate_proposal.rs`), an arbitrary value passes the final `built_block == received_fin.proposal_commitment` check without triggering `ProposalFinMismatch`. [7](#0-6) 

---

### Impact Explanation

**Scenario A — Gas price inflation (DoS):** A malicious proposer submits `fee_proposal_fri = u128::MAX` for every block it proposes during the startup window. After `window_size` blocks, `fee_actual` (the median) becomes `u128::MAX`. `effective_min` is then `u128::MAX`, so `calculate_next_base_gas_price` returns `u128::MAX`. Every subsequent transaction's `max_price_per_unit` check fails, causing a complete transaction-processing DoS.

**Scenario B — Gas price deflation (undercharging):** A malicious proposer submits `fee_proposal_fri = 1` (the minimum non-zero value). After the window fills, `fee_actual` is `1`, collapsing the L2 gas price floor to `1 FRI`, allowing users to pay near-zero fees and draining sequencer revenue.

Both effects persist for all blocks until the manipulated values rotate out of the `fee_proposal_window_size`-block sliding window.

---

### Likelihood Explanation

The startup window is bounded to `fee_proposal_window_size` blocks (a versioned constant). In a multi-validator Tendermint deployment the proposer rotates each round, so a single malicious validator controls only a fraction of startup blocks. However:

- Near genesis or after a chain restart the window is always empty, making every new deployment vulnerable.
- A validator controlling more than half the startup-window slots can set the median to any value.
- No operator-visible alert fires when an extreme `fee_proposal_fri` is accepted; the only signal is a `warn!` log when `fee_actual` is unavailable, not when an unchecked value is accepted.

---

### Recommendation

Add an absolute range check on `fee_proposal_fri` that is enforced regardless of whether `fee_actual` is available. At minimum, reject values of `0` and values above a configurable ceiling (e.g., `max_l2_gas_price_fri` from `VersionedConstants`). This mirrors the existing `within_margin` guard applied to L1 gas prices, which is always enforced:

```rust
// Always enforce: fee_proposal must be within [min_fee_proposal, max_fee_proposal].
if let Some(fee_proposal) = init_proposed.fee_proposal_fri {
    if fee_proposal.0 == 0 || fee_proposal > max_allowed_fee_proposal {
        return Err(...);
    }
}
```

The bounds check against `fee_actual` can remain conditional on `fee_actual` being `Some`, but the absolute floor/ceiling must be unconditional.

---

### Proof of Concept

1. Deploy a fresh chain (height 0). `fee_proposals_window` is empty; `compute_fee_actual` returns `None` for all heights below `fee_proposal_window_size`.
2. As the proposer for block 0, construct a `ProposalInit` with `fee_proposal_fri = Some(GasPrice(u128::MAX))` and `starknet_version >= V0_14_3`.
3. Call `is_proposal_init_valid`. The check at lines 398–416 evaluates `if let (Some(_), Some(_)) = (None, Some(...))` — the pattern does not match; the bounds check is skipped entirely. The function returns `Ok(())`.
4. The proposal is accepted by consensus. `record_fee_proposal(height_0, Some(GasPrice(u128::MAX)))` stores the value.
5. Repeat for each block the malicious proposer controls during the startup window.
6. Once `fee_proposals_window` contains `window_size` entries, `compute_fee_actual` returns `Some(GasPrice(u128::MAX))` (or a very large median).
7. `calculate_next_l2_gas_price_for_fin` sets `effective_min = u128::MAX`; `calculate_next_base_gas_price` returns `u128::MAX`.
8. All subsequent transactions fail the `max_price_per_unit` pre-validation check — complete L2 DoS. [1](#0-0) [8](#0-7) [9](#0-8)

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

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L582-585)
```rust
            let batcher_block_commitment = proposal_commitment_from(
                finished_info.proposal_commitment.partial_block_hash,
                fee_proposal,
            );
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

**File:** crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs (L308-310)
```rust
    fn record_fee_proposal(&mut self, height: BlockNumber, fee_proposal_fri: Option<GasPrice>) {
        self.fee_proposals_window.insert(height, fee_proposal_fri);
    }
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

**File:** crates/apollo_consensus_orchestrator/src/fee_market/mod.rs (L62-77)
```rust
) -> GasPrice {
    if let Some(override_value) = override_l2_gas_price_fri {
        info!(
            "L2 gas price ({}) is not updated, remains on override value of {override_value} fri",
            current_l2_gas_price.0
        );
        return GasPrice(override_value);
    }
    let gas_target = VersionedConstants::latest_constants().gas_target;
    let config_min = get_min_gas_price_for_height(height, min_l2_gas_price_per_height);
    let effective_min = match fee_actual {
        Some(fa) => GasPrice(max(config_min.0, fa.0)),
        None => config_min,
    };
    calculate_next_base_gas_price(current_l2_gas_price, l2_gas_used, gas_target, effective_min)
}
```
