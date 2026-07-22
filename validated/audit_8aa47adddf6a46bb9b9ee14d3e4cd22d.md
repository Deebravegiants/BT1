### Title
Unconstrained `fee_proposal_fri` During Bootstrap Inflates L2 Gas Price Floor — (`crates/apollo_consensus_orchestrator/src/validate_proposal.rs`)

---

### Summary

During the first `window_size` (10) blocks of the chain, the `fee_proposal_fri` field in `ProposalInit` is accepted by validators without any bounds check. Any proposer selected during this bootstrap window can set `fee_proposal_fri` to an arbitrarily large value. Those values are recorded in `fee_proposals_window`, become the median `fee_actual` once the window fills, and then act as the floor for the EIP-1559 L2 gas price for all subsequent blocks. Because the per-block adjustment cap is only ±0.2% (2 ppt), an inflated bootstrap value persists for hundreds of blocks, causing every user to pay inflated fees.

---

### Finding Description

`is_proposal_init_valid` in `validate_proposal.rs` enforces that a proposer's `fee_proposal_fri` lies within a geometric margin of `fee_actual`:

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

The guard fires only when `fee_actual` is `Some`. `fee_actual` is computed by `compute_fee_actual`, which returns `None` whenever `height < window_size`:

```rust
let Some(start) = height.0.checked_sub(window_size) else {
    warn!("Cannot compute fee_actual for height {height}: height is below window_size ({window_size})");
    return None;
};
``` [2](#0-1) 

`window_size` is 10 blocks in every deployed versioned-constants file: [3](#0-2) 

So for blocks 0–9, `fee_actual` is always `None`, the `if let` pattern never matches, and any value of `fee_proposal_fri` passes validation. Validators accept the proposal, consensus commits it, and `record_fee_proposal` stores the arbitrary value:

```rust
fn record_fee_proposal(&mut self, height: BlockNumber, fee_proposal_fri: Option<GasPrice>) {
    self.fee_proposals_window.insert(height, fee_proposal_fri);
}
``` [4](#0-3) 

Once 10 blocks have been committed, `fee_actual` becomes the median of those 10 stored values. If all 10 were set to an inflated value `X`, `fee_actual = X`. Subsequent proposers' `fee_proposal` is then clamped to `[X/(1+0.002), X*(1+0.002)]`, so the inflated value propagates forward. `calculate_next_l2_gas_price` passes `fee_actual` as the floor to `calculate_next_l2_gas_price_for_fin`, anchoring the EIP-1559 gas price at the inflated level:

```rust
fn calculate_next_l2_gas_price(&self, height: BlockNumber, l2_gas_used: GasAmount) -> GasPrice {
    let fee_actual = compute_fee_actual(
        &self.fee_proposals_window,
        height,
        VersionedConstants::latest_constants().fee_proposal_window_size,
    );
    calculate_next_l2_gas_price_for_fin(
        self.l2_gas_price,
        height,
        l2_gas_used,
        self.config.dynamic_config.override_l2_gas_price_fri,
        &self.config.dynamic_config.min_l2_gas_price_per_height,
        fee_actual,
    )
}
``` [5](#0-4) 

The `fee_proposal_fri` is also hashed into the `ProposalCommitment` via `Poseidon(partial_block_hash, fee_proposal_fri)`, so the inflated value is permanently committed on-chain:

```rust
ProposalCommitment(Poseidon::hash_array(&[partial.0, Felt::from(fee_proposal.0)]))
``` [6](#0-5) 

---

### Impact Explanation

Any validator who is selected as proposer during blocks 0–9 can set `fee_proposal_fri` to an arbitrarily large value (e.g., `u128::MAX`). Once the window fills, `fee_actual` equals the median of those inflated values. Because the per-block adjustment cap is ±0.2%, it takes approximately `ln(X/min_price) / ln(1.002) ≈ 350 * ln(X/min_price)` blocks to return to the minimum price. An inflation of 10× the minimum requires ~1,150 blocks (~50 minutes at 2.6 s/block) to decay back. During that entire period every user pays inflated L2 gas fees. This is a direct economic impact on all network participants.

The impact falls under: **Critical — Incorrect fee/gas/resource accounting with economic impact.**

---

### Likelihood Explanation

The proposer for each block is selected by weighted random selection from the validator committee. Any validator with non-zero stake has a non-zero probability of being selected as proposer during the first 10 blocks. A validator with a large stake share (e.g., the initial deployer or a dominant staker) has a high probability of being selected for multiple consecutive bootstrap blocks, allowing them to set all 10 window values. Even a minority validator who is selected for a single bootstrap block can contribute one inflated value to the median. The exploit requires no special privilege beyond being a committee member — a normal proposer action.

---

### Recommendation

**Short term:** Enforce a hard upper bound on `fee_proposal_fri` during bootstrap even when `fee_actual` is `None`. The natural bound is `min_gas_price * (1 + margin)^height` — i.e., the maximum value reachable from `min_gas_price` after `height` steps of the ±0.2% per-block cap. Alternatively, seed the `fee_proposals_window` with `min_gas_price` for all heights below `window_size` before consensus starts (the `initialize_fee_proposals_window` function already handles the normal case; extend it to fill missing genesis heights with `min_gas_price`).

**Long term:** Document the bootstrap invariant explicitly. Consider initializing `fee_proposals_window` with `min_gas_price` for all heights `[0, window_size)` at genesis so that `fee_actual` is always `Some` and the bounds check is always enforced from block 0.

---

### Proof of Concept

1. Attacker is a validator with any non-zero stake.
2. Attacker is selected as proposer for block 0 (or any block in `[0, 9]`).
3. Attacker constructs `ProposalInit` with `fee_proposal_fri = GasPrice(u128::MAX)`.
4. `is_proposal_init_valid` is called; `proposal_init_validation.fee_actual` is `None` (height 0 < window_size 10); the `if let` guard does not fire; the proposal passes validation.
5. Consensus commits the block; `record_fee_proposal(BlockNumber(0), Some(GasPrice(u128::MAX)))` is called.
6. Attacker repeats for blocks 1–9 (if selected as proposer, or colluding validators do the same).
7. At block 10, `compute_fee_actual` returns `Some(GasPrice(u128::MAX))` (median of 10 `u128::MAX` values).
8. `calculate_next_l2_gas_price_for_fin` uses `fee_actual = u128::MAX` as the floor; `l2_gas_price` is set to `u128::MAX` (or saturates).
9. All subsequent transactions require `max_price_per_unit >= u128::MAX` to pass pre-validation, effectively blocking all user transactions or forcing them to pay maximum fees. [1](#0-0) [7](#0-6) [8](#0-7)

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

**File:** crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs (L308-319)
```rust
    fn record_fee_proposal(&mut self, height: BlockNumber, fee_proposal_fri: Option<GasPrice>) {
        self.fee_proposals_window.insert(height, fee_proposal_fri);
    }

    fn prune_fee_proposals_window(&mut self, current_height: BlockNumber) {
        let window_size = VersionedConstants::latest_constants().fee_proposal_window_size;
        let cutoff = BlockNumber(current_height.0.saturating_sub(window_size));
        // Per `BTreeMap::split_off` docs: "Splits the collection into two at the given key.
        // Returns everything after the given key, including the key." Reassigning the returned
        // half back keeps `[cutoff, ..)` and drops everything below.
        self.fee_proposals_window = self.fee_proposals_window.split_off(&cutoff);
    }
```

**File:** crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs (L425-441)
```rust
    /// Returns the next L2 gas price without mutating context. Used when building the fin and when
    /// updating at decision time.
    fn calculate_next_l2_gas_price(&self, height: BlockNumber, l2_gas_used: GasAmount) -> GasPrice {
        let fee_actual = compute_fee_actual(
            &self.fee_proposals_window,
            height,
            VersionedConstants::latest_constants().fee_proposal_window_size,
        );
        calculate_next_l2_gas_price_for_fin(
            self.l2_gas_price,
            height,
            l2_gas_used,
            self.config.dynamic_config.override_l2_gas_price_fri,
            &self.config.dynamic_config.min_l2_gas_price_per_height,
            fee_actual,
        )
    }
```
