### Title
Unbounded `fee_proposal_fri` During Startup Window Poisons the L2 Gas Price Floor — (`File: crates/apollo_consensus_orchestrator/src/validate_proposal.rs`)

### Summary

`is_proposal_init_valid` explicitly skips bounds enforcement on the proposer-supplied `fee_proposal_fri` field whenever `fee_actual` is `None` (i.e., during the first `fee_proposal_window_size` = 10 blocks). Because `fee_actual` is used as the **minimum gas-price floor** in `calculate_next_l2_gas_price_for_fin`, a malicious proposer who controls even a majority of the first 10 blocks can inject an arbitrarily large `fee_proposal_fri`, permanently raising the effective minimum L2 gas price for all subsequent blocks.

### Finding Description

**Invariant broken:** The `fee_proposal_fri` field in `ProposalInit` is proposer-supplied. After the startup window it is bounded to within `fee_proposal_margin_ppt` (2 ppt = 0.2%) of `fee_actual`. During the startup window that guard is explicitly absent.

**Root cause — `is_proposal_init_valid`:**

```rust
// Validate fee_proposal is within the configured margin of fee_actual.
// During initiation (fee_actual is None, <window_size blocks), bounds are not enforced.
if let (Some(fee_actual), Some(fee_proposal)) =
    (proposal_init_validation.fee_actual, init_proposed.fee_proposal_fri)
{
    // bounds check — SKIPPED when fee_actual is None
}
``` [1](#0-0) 

`fee_actual` is `None` whenever `height < fee_proposal_window_size` (10):

```rust
fee_actual: compute_fee_actual(
    &self.fee_proposals_window,
    init.height,
    VersionedConstants::latest_constants().fee_proposal_window_size,
),
``` [2](#0-1) 

`compute_fee_actual` returns `None` when `height < window_size`:

```rust
let Some(start) = height.0.checked_sub(window_size) else {
    warn!("Cannot compute fee_actual for height {height}: height is below window_size ...");
    return None;
};
``` [3](#0-2) 

**Propagation — `calculate_next_l2_gas_price_for_fin`:**

`fee_actual` is used directly as the minimum gas-price floor for the EIP-1559 calculation:

```rust
let effective_min = match fee_actual {
    Some(fa) => GasPrice(max(config_min.0, fa.0)),
    None => config_min,
};
calculate_next_base_gas_price(current_l2_gas_price, l2_gas_used, gas_target, effective_min)
``` [4](#0-3) 

If `fee_actual = u128::MAX`, then `effective_min = u128::MAX`, and `calculate_next_base_gas_price` returns `u128::MAX` as the next L2 gas price.

**Decision path — `finalize_decision`:**

At `decision_reached`, the accepted `init.fee_proposal_fri` is recorded unconditionally:

```rust
self.update_l2_gas_price(height, l2_gas_used);
self.record_fee_proposal(height, init.fee_proposal_fri);
``` [5](#0-4) 

`record_fee_proposal` inserts the value into `fee_proposals_window`:

```rust
fn record_fee_proposal(&mut self, height: BlockNumber, fee_proposal_fri: Option<GasPrice>) {
    self.fee_proposals_window.insert(height, fee_proposal_fri);
}
``` [6](#0-5) 

**Window size is 10 blocks:**

```json
{
    "fee_proposal_margin_ppt": 2,
    "fee_proposal_window_size": 10,
    ...
}
``` [7](#0-6) 

### Impact Explanation

A malicious proposer who controls a majority (≥ 6 of 10) of the first 10 blocks can set `fee_proposal_fri = u128::MAX` in each `ProposalInit`. All validators accept these values (no bounds check). After block 10, `compute_fee_actual` returns the median of the poisoned window — approximately `u128::MAX / 2` or higher. `calculate_next_l2_gas_price_for_fin` then uses this as `effective_min`, the hard floor for the EIP-1559 base fee. The base fee ratchets upward by ~0.3% per block (`MIN_GAS_PRICE_INCREASE_DENOMINATOR = 333`) until it reaches `u128::MAX`, at which point no user transaction can satisfy the fee requirement. This is a **wrong gas/fee accounting effect with direct economic impact** — matching the "Incorrect fee, gas, bouncer, resource accounting, refund, balance, or L1 gas price effect with economic impact" impact class.

The corrupted value is `self.l2_gas_price` (the authoritative next-block gas price stored in `SequencerConsensusContext`), which is then written into `BlockHeaderWithoutHash.next_l2_gas_price` and broadcast to state sync. [8](#0-7) 

### Likelihood Explanation

The attack window is the first 10 blocks of the network's life (genesis). In a Tendermint-style protocol the proposer rotates deterministically, so a validator with ≥ 50% stake can expect to propose a majority of those 10 blocks. The attack requires no special privilege beyond being a validator during genesis — an unprivileged but stake-holding participant can trigger it. The startup window is a known, documented design decision (the comment "During initiation (fee_actual is None, <window_size blocks), bounds are not enforced" confirms it), making it a predictable target.

### Recommendation

1. **Add an absolute upper bound on `fee_proposal_fri` during the startup window.** When `fee_actual` is `None`, enforce a cap derived from the configured maximum L2 gas price (e.g., `max_l2_gas_price` or a multiple of `min_gas_price`) rather than accepting any value.

2. **Alternatively, seed `fee_proposals_window` with `l2_gas_price` for all heights below `fee_proposal_window_size` before the first block is proposed**, so `fee_actual` is never `None` and the normal margin check always applies.

3. **Add a maximum bound in `calculate_next_l2_gas_price_for_fin`** so that `effective_min` is capped at a configurable ceiling, preventing a single poisoned `fee_actual` from driving the gas price to `u128::MAX`.

### Proof of Concept

1. Network launches at height 0 with `fee_proposal_window_size = 10`.
2. A malicious validator is selected as proposer for heights 0–9 (or controls ≥ 6 of them).
3. For each of those blocks, the proposer sends `ProposalInit { fee_proposal_fri: Some(GasPrice(u128::MAX)), ... }`.
4. `is_proposal_init_valid` is called; `proposal_init_validation.fee_actual` is `None` (height < 10), so the `if let (Some(fee_actual), Some(fee_proposal))` guard does not fire. The proposal passes validation.
5. At `decision_reached` for each height, `record_fee_proposal(height, Some(GasPrice(u128::MAX)))` inserts `u128::MAX` into `fee_proposals_window`.
6. At height 10, `compute_fee_actual` returns `Some(GasPrice(u128::MAX))` (median of 10 × `u128::MAX`).
7. `calculate_next_l2_gas_price_for_fin` sets `effective_min = u128::MAX`.
8. `calculate_next_base_gas_price` returns `u128::MAX` as the next L2 gas price.
9. `self.l2_gas_price = u128::MAX` is stored in context and written to `BlockHeaderWithoutHash.next_l2_gas_price`.
10. All subsequent transactions fail fee validation; the network is economically bricked.

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

**File:** crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs (L399-412)
```rust
        let block_header_without_hash = BlockHeaderWithoutHash {
            block_number: height,
            l1_gas_price,
            l1_data_gas_price,
            l2_gas_price,
            l2_gas_consumed: l2_gas_used,
            next_l2_gas_price: self.l2_gas_price,
            sequencer,
            timestamp: BlockTimestamp(init.timestamp),
            l1_da_mode: init.l1_da_mode,
            fee_proposal_fri: init.fee_proposal_fri,
            // TODO(guy.f): Figure out where/if to get the values below from and fill them.
            ..Default::default()
        };
```

**File:** crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs (L517-518)
```rust
        self.update_l2_gas_price(height, l2_gas_used);
        self.record_fee_proposal(height, init.fee_proposal_fri);
```

**File:** crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs (L1193-1197)
```rust
            fee_actual: compute_fee_actual(
                &self.fee_proposals_window,
                init.height,
                VersionedConstants::latest_constants().fee_proposal_window_size,
            ),
```

**File:** crates/apollo_consensus_orchestrator/src/dynamic_gas_price/mod.rs (L61-67)
```rust
    let Some(start) = height.0.checked_sub(window_size) else {
        warn!(
            "Cannot compute fee_actual for height {height}: height is below window_size \
             ({window_size})"
        );
        return None;
    };
```

**File:** crates/apollo_consensus_orchestrator/src/fee_market/mod.rs (L72-76)
```rust
    let effective_min = match fee_actual {
        Some(fa) => GasPrice(max(config_min.0, fa.0)),
        None => config_min,
    };
    calculate_next_base_gas_price(current_l2_gas_price, l2_gas_used, gas_target, effective_min)
```

**File:** crates/apollo_versioned_constants/resources/orchestrator_versioned_constants_0_14_0.json (L1-9)
```json
{
    "fee_proposal_margin_ppt": 2,
    "fee_proposal_window_size": 10,
    "gas_price_max_change_denominator": 48,
    "gas_target": 3200000000,
    "max_block_size": 4000000000,
    "min_gas_price": "0xb2d05e00",
    "l1_gas_price_margin_percent": 10
}
```
