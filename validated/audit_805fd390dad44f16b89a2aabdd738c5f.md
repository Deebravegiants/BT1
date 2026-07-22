### Title
Uninitialized `fee_proposals_window` Bypasses `fee_proposal_fri` Bounds Enforcement During Chain Bootstrap, Allowing Permanent Fee Poisoning - (File: `crates/apollo_consensus_orchestrator/src/validate_proposal.rs`)

---

### Summary

During the first `fee_proposal_window_size` (10) blocks of the chain, `compute_fee_actual` returns `None` because the sliding window is empty. The validator's `is_proposal_init_valid` function uses an `if let (Some(fee_actual), Some(fee_proposal))` pattern that silently skips the entire `fee_proposal_fri` bounds check when `fee_actual` is `None`. A malicious proposer selected during this bootstrap window can set `fee_proposal_fri = u128::MAX` in `ProposalInit`, which all validators accept without any range enforcement. The poisoned value is then committed to `fee_proposals_window`, and once the window fills, `compute_fee_actual` returns `u128::MAX` as the median, which `calculate_next_l2_gas_price_for_fin` uses as the `effective_min` floor for all future blocks, permanently setting `l2_gas_price = u128::MAX` and making the chain economically unusable.

---

### Finding Description

**Root cause — `is_proposal_init_valid` in `validate_proposal.rs`:**

```rust
// Validate fee_proposal is within the configured margin of fee_actual.
// During initiation (fee_actual is None, <window_size blocks), bounds are not enforced.
if let (Some(fee_actual), Some(fee_proposal)) =
    (proposal_init_validation.fee_actual, init_proposed.fee_proposal_fri)
{
    // bounds check only runs when BOTH are Some
}
``` [1](#0-0) 

When `fee_actual` is `None` (the `if let` pattern fails to match), the entire bounds check is skipped. `fee_actual` is `None` whenever `compute_fee_actual` cannot fill a complete window of `window_size` prior blocks:

```rust
pub fn compute_fee_actual(...) -> Option<GasPrice> {
    let Some(start) = height.0.checked_sub(window_size) else {
        return None;  // height < window_size
    };
    for source_height in (start..height.0).map(BlockNumber) {
        match fee_proposals_window.get(&source_height) {
            Some(Some(price)) => window.push(*price),
            Some(None) | None => { return None; }  // any gap → None
        }
    }
    ...
}
``` [2](#0-1) 

`fee_actual` is `None` for all heights `0..window_size` (= 0..10 with current config). [3](#0-2) 

**Proposer always sets `fee_proposal_fri = Some(...)`:**

The honest proposer path in `initiate_build` unconditionally sets `fee_proposal_fri: Some(args.fee_proposal)` regardless of version or window state:

```rust
let init = ProposalInit {
    starknet_version: starknet_api::block::StarknetVersion::LATEST,
    fee_proposal_fri: Some(args.fee_proposal),  // always Some
    ...
};
``` [4](#0-3) 

The validator enforces `fee_proposal_fri` is `Some` when `starknet_version >= V0_14_3` (which is always true since `LATEST >= V0_14_3`), but does **not** enforce any value range when `fee_actual` is `None`. [5](#0-4) 

**Poisoned value is committed and propagates:**

At `decision_reached` → `finalize_decision`, the accepted `fee_proposal_fri` is unconditionally recorded into the sliding window:

```rust
self.update_l2_gas_price(height, l2_gas_used);
self.record_fee_proposal(height, init.fee_proposal_fri);
``` [6](#0-5) 

`record_fee_proposal` inserts directly into `fee_proposals_window`:

```rust
fn record_fee_proposal(&mut self, height: BlockNumber, fee_proposal_fri: Option<GasPrice>) {
    self.fee_proposals_window.insert(height, fee_proposal_fri);
}
``` [7](#0-6) 

Once the window fills with poisoned values, `compute_fee_actual` returns `u128::MAX`. This feeds into `calculate_next_l2_gas_price_for_fin` as the `effective_min` floor:

```rust
let effective_min = match fee_actual {
    Some(fa) => GasPrice(max(config_min.0, fa.0)),  // fa = u128::MAX
    None => config_min,
};
calculate_next_base_gas_price(current_l2_gas_price, l2_gas_used, gas_target, effective_min)
``` [8](#0-7) 

`calculate_next_base_gas_price` enforces `max(adjusted_price, min_gas_price.0)`, so `l2_gas_price` is permanently locked at `u128::MAX`. [9](#0-8) 

The poisoned `fee_proposal_fri` is also forwarded to the cende pipeline and stored in `BlockHeaderWithoutHash.fee_proposal_fri` in state sync, making the corruption durable across restarts. [10](#0-9) 

---

### Impact Explanation

**Critical. Incorrect fee, gas, bouncer, resource accounting, refund, balance, or L1 gas price effect with economic impact.**

A single malicious proposer during the first 10 blocks can permanently set `l2_gas_price = u128::MAX` for all future blocks. Every transaction that pays L2 gas would require `u128::MAX` FRI per gas unit, making the chain economically unusable. The corruption is committed to storage and propagated to state sync and the cende pipeline, surviving node restarts. The `ProposalCommitment` hash is also corrupted since it is computed as `Poseidon(partial_block_hash, fee_proposal_fri)`. [11](#0-10) 

---

### Likelihood Explanation

**High.** The window is empty at genesis and after any restart that begins below `window_size`. Any validator selected as proposer during blocks `0..window_size` can trigger this with no preconditions. The proposer role rotates among validators, so a single Byzantine validator in the committee has a non-negligible probability of being selected during the 10-block bootstrap window. No special privileges beyond being a consensus participant are required.

---

### Recommendation

When `fee_actual` is `None` (window not yet full), do not skip the bounds check entirely. Instead, bound `fee_proposal_fri` against the locally-known `l2_gas_price` (the same fallback the honest proposer uses):

```rust
// When fee_actual is None, bound against l2_gas_price fallback instead of skipping.
let reference = proposal_init_validation.fee_actual
    .unwrap_or(proposal_init_validation.l2_gas_price_fri);
let (lower_bound, upper_bound) = fee_proposal_bounds(
    reference,
    VersionedConstants::latest_constants().fee_proposal_margin_ppt,
);
if let Some(fee_proposal) = init_proposed.fee_proposal_fri {
    if fee_proposal.0 < lower_bound || fee_proposal.0 > upper_bound {
        return Err(...);
    }
}
```

This preserves the honest proposer's behavior (which already freezes at `l2_gas_price` when `fee_actual` is `None`) while preventing a malicious proposer from injecting an out-of-range value. `ProposalInitValidation` already carries `l2_gas_price_fri`, so no new fields are needed. [12](#0-11) 

---

### Proof of Concept

**Setup:** Fresh chain, `fee_proposal_window_size = 10`, `starknet_version = LATEST` (≥ V0_14_3). Malicious validator is selected as proposer for block 0.

**Step 1 — Craft malicious `ProposalInit`:**
```
ProposalInit {
    height: BlockNumber(0),
    starknet_version: StarknetVersion::LATEST,
    fee_proposal_fri: Some(GasPrice(u128::MAX)),
    // all other fields set to honest values
}
```

**Step 2 — Validator calls `is_proposal_init_valid`:**
- `fee_proposal_required = true` (LATEST ≥ V0_14_3) → `Some(u128::MAX)` passes presence check
- `fee_actual = compute_fee_actual(&empty_window, BlockNumber(0), 10)` → `None` (height 0 < window_size 10)
- `if let (Some(fee_actual), Some(fee_proposal)) = (None, Some(u128::MAX))` → **pattern does not match, bounds check is skipped entirely**
- `is_proposal_init_valid` returns `Ok(())` [1](#0-0) 

**Step 3 — Proposal accepted, `decision_reached` called:**
- `record_fee_proposal(BlockNumber(0), Some(GasPrice(u128::MAX)))` inserts into `fee_proposals_window`

**Step 4 — Repeat for blocks 1–9** (malicious proposer or colluding validators):
- `fee_proposals_window` now contains `{0: u128::MAX, 1: u128::MAX, ..., 9: u128::MAX}`

**Step 5 — Block 10 is proposed:**
- `compute_fee_actual(&window, BlockNumber(10), 10)` → median of 10 × `u128::MAX` = `GasPrice(u128::MAX)`
- `calculate_next_l2_gas_price_for_fin(..., fee_actual = Some(u128::MAX))`:
  - `effective_min = max(config_min, u128::MAX) = u128::MAX`
  - `calculate_next_base_gas_price(..., min_gas_price = u128::MAX)` → `GasPrice(u128::MAX)`
- `self.l2_gas_price = u128::MAX` permanently [13](#0-12) 

**Result:** All future blocks have `l2_gas_price = u128::MAX`. Every transaction requiring L2 gas is rejected or requires `u128::MAX` FRI per gas unit. The chain is economically unusable. The corruption is stored in `BlockHeaderWithoutHash.fee_proposal_fri` and survives restarts.

### Citations

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L75-85)
```rust
pub(crate) struct ProposalInitValidation {
    pub height: BlockNumber,
    pub block_timestamp_window_seconds: u64,
    pub previous_proposal_init: Option<PreviousProposalInitInfo>,
    pub l1_da_mode: L1DataAvailabilityMode,
    pub l2_gas_price_fri: GasPrice,
    pub starknet_version: StarknetVersion,
    /// fee_actual from the sliding window. `None` until the window has accumulated
    /// `fee_proposal_window_size` entries (startup / near-genesis).
    pub fee_actual: Option<GasPrice>,
}
```

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

**File:** crates/apollo_consensus_orchestrator/src/dynamic_gas_price/mod.rs (L163-170)
```rust
pub(crate) fn proposal_commitment_from(
    partial: PartialBlockHash,
    fee_proposal: Option<GasPrice>,
) -> ProposalCommitment {
    let Some(fee_proposal) = fee_proposal else {
        return ProposalCommitment(partial.0);
    };
    ProposalCommitment(Poseidon::hash_array(&[partial.0, Felt::from(fee_proposal.0)]))
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

**File:** crates/apollo_consensus_orchestrator/src/build_proposal.rs (L182-188)
```rust
        starknet_version: starknet_api::block::StarknetVersion::LATEST,
        // TODO(Asmaa): Put the real value once we have it.
        // Sentinel until then; see `expected_version_constant_commitment` for why this is the
        // single source of truth shared with the validator.
        version_constant_commitment: expected_version_constant_commitment(),
        fee_proposal_fri: Some(args.fee_proposal),
    };
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

**File:** crates/apollo_consensus_orchestrator/src/fee_market/mod.rs (L137-139)
```rust
    // Price should not realistically exceed u128::MAX, bound to avoid theoretical overflow.
    let adjusted_price = u128::try_from(adjusted_price_u256).unwrap_or(u128::MAX);
    GasPrice(max(adjusted_price, min_gas_price.0))
```
