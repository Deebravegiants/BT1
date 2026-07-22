### Title
Unbounded `fee_proposal_fri` During Startup/Upgrade Window Allows Proposer to Corrupt L2 Gas Price Floor — (`crates/apollo_consensus_orchestrator/src/validate_proposal.rs`)

---

### Summary

In `is_proposal_init_valid`, the `fee_proposal_fri` field of `ProposalInit` is bounds-checked against `fee_actual` only when `fee_actual` is `Some`. When `fee_actual` is `None` — which occurs for the first `window_size` (10) blocks after genesis **and** for the first 10 blocks after a V0_14_3 protocol upgrade (because pre-upgrade blocks are stored as `None` in the window) — the check is silently skipped. An honest proposer freezes at `l2_gas_price` during this period, but the validator enforces no such constraint. A malicious proposer can therefore publish an arbitrary `fee_proposal_fri` (e.g., `u128::MAX`) that every validator accepts, permanently storing it in the sliding window. Once the window fills with V0_14_3 blocks, `compute_fee_actual` returns the median of those stored values, and `calculate_next_l2_gas_price_for_fin` uses that median as the `effective_min` floor for the EIP-1559 L2 gas price — potentially locking the network into a prohibitively high gas price.

---

### Finding Description

**Root cause — missing fallback bound in `is_proposal_init_valid`:** [1](#0-0) 

The guard is an `if let (Some(fee_actual), Some(fee_proposal)) = ...` pattern. When `fee_actual` is `None`, the entire body is skipped — no lower bound, no upper bound, no fallback comparison.

**Honest proposer's fallback (not mirrored in the validator):** [2](#0-1) 

The proposer freezes at `l2_gas_price` when `fee_actual` is `None`. The validator does not enforce this.

**`fee_actual` becomes `None` after a protocol upgrade:** [3](#0-2) 

Any `None` entry in the window (pre-V0_14_3 block) causes `compute_fee_actual` to return `None`, so the entire first `window_size` blocks after the upgrade are unguarded.

**Accepted `fee_proposal_fri` is stored permanently in the window:** [4](#0-3) 

**Stored window values feed directly into the L2 gas price floor:** [5](#0-4) 

`fee_actual` is used as `effective_min` — the hard floor passed to `calculate_next_base_gas_price`. If `fee_actual = u128::MAX`, the floor is `u128::MAX`.

**`fee_proposal_fri` is also bound into the `ProposalCommitment`:** [6](#0-5) 

The extreme value is cryptographically committed and cannot be retroactively corrected.

---

### Impact Explanation

Once the malicious proposer controls ≥ 5 of the 10 unguarded startup/upgrade blocks and sets `fee_proposal_fri = u128::MAX` in each, the median of the window after those 10 blocks is `u128::MAX`. `calculate_next_l2_gas_price_for_fin` then sets `effective_min = u128::MAX`, which propagates into every subsequent block's L2 gas price via `update_l2_gas_price`. All L2 transactions become economically impossible to execute, constituting a permanent, on-chain fee manipulation with direct economic impact — matching the "Incorrect fee, gas, bouncer, resource accounting, refund, balance, or L1 gas price effect with economic impact" criterion.

---

### Likelihood Explanation

The attack window is narrow (10 blocks) but recurs at every V0_14_3 protocol upgrade. The proposer must control ≥ 5 of those 10 blocks (majority of the window) to shift the median to an extreme value. In a Tendermint-style rotation this requires ≥ 50% of voting power, which is a significant barrier. However, the vulnerability is structurally present and exploitable by any entity that achieves proposer majority during the transition window — a realistic scenario in early-stage or permissioned deployments.

---

### Recommendation

When `fee_actual` is `None`, apply a fallback bound using `l2_gas_price` as the reference, mirroring the honest proposer's behavior. For example, in `is_proposal_init_valid`:

```rust
// When fee_actual is unavailable, bound fee_proposal against l2_gas_price.
let reference = proposal_init_validation.fee_actual
    .unwrap_or(proposal_init_validation.l2_gas_price_fri);
let (lower_bound, upper_bound) = fee_proposal_bounds(
    reference,
    VersionedConstants::latest_constants().fee_proposal_margin_ppt,
);
if fee_proposal.0 < lower_bound || fee_proposal.0 > upper_bound {
    return Err(...);
}
```

This closes the asymmetry between proposer and validator during the startup/upgrade window.

---

### Proof of Concept

1. Network upgrades to Starknet V0_14_3. The `fee_proposals_window` contains 10 `None` entries (pre-upgrade blocks), so `compute_fee_actual` returns `None` for the next 10 blocks.
2. A malicious proposer (controlling ≥ 5 of those 10 blocks) broadcasts `ProposalInit` with `fee_proposal_fri = Some(GasPrice(u128::MAX))`.
3. Each validator calls `is_proposal_init_valid`. Because `proposal_init_validation.fee_actual = None`, the `if let (Some(fee_actual), Some(fee_proposal))` guard does not fire. The proposal is accepted.
4. `finalize_decision` calls `self.record_fee_proposal(height, Some(GasPrice(u128::MAX)))`, storing the extreme value in `fee_proposals_window`.
5. After 10 V0_14_3 blocks, `compute_fee_actual` returns `GasPrice(u128::MAX)` (median of the window).
6. `calculate_next_l2_gas_price_for_fin` computes `effective_min = max(config_min, u128::MAX) = u128::MAX` and returns `GasPrice(u128::MAX)`.
7. `update_l2_gas_price` sets `self.l2_gas_price = u128::MAX`. Every subsequent block's `l2_gas_price_fri` is `u128::MAX`, making all L2 transactions economically impossible. [1](#0-0) [7](#0-6) [8](#0-7) [9](#0-8)

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

**File:** crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs (L478-482)
```rust
        let Some(fee_actual) = fee_actual else {
            warn!("fee_actual unavailable, freezing fee_proposal at l2_gas_price");
            SNIP35_FEE_PROPOSAL_FRI.set_lossy(self.l2_gas_price.0);
            return self.l2_gas_price;
        };
```

**File:** crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs (L515-518)
```rust
        let DecisionReachedResponse { state_diff, central_objects } = decision_reached_response;

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

**File:** crates/apollo_consensus_orchestrator/src/fee_market/mod.rs (L55-77)
```rust
pub fn calculate_next_l2_gas_price_for_fin(
    current_l2_gas_price: GasPrice,
    height: BlockNumber,
    l2_gas_used: GasAmount,
    override_l2_gas_price_fri: Option<u128>,
    min_l2_gas_price_per_height: &[PricePerHeight],
    fee_actual: Option<GasPrice>,
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
