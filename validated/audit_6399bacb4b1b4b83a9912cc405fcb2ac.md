### Title
Unchecked `fee_proposal_fri` During Startup Window Allows Proposer to Permanently Skew L2 Gas Price Floor — (File: `crates/apollo_consensus_orchestrator/src/validate_proposal.rs`)

---

### Summary

`is_proposal_init_valid` unconditionally skips the `fee_proposal_fri` bounds check whenever `fee_actual` is `None`. `fee_actual` is `None` for the first `window_size` blocks (near genesis / after restart with an empty window). During that window any proposer can set `fee_proposal_fri` to an arbitrary value; every validator accepts it. The accepted value is stored in `fee_proposals_window`, becomes the median (`fee_actual`) after `window_size` blocks, and is then used as the effective minimum L2 gas price floor for all subsequent blocks.

---

### Finding Description

**Invariant broken**: `fee_proposal_fri` must always be bounded by an authoritative reference (the oracle-derived `fee_actual`, or the EIP-1559 `l2_gas_price` when the window is incomplete). The external DeFi bug used user-controlled pricing when supply was zero; the sequencer analog uses proposer-controlled pricing when the sliding window is empty.

**Root cause** — `is_proposal_init_valid` in `validate_proposal.rs`:

```rust
// Validate fee_proposal is within the configured margin of fee_actual.
// During initiation (fee_actual is None, <window_size blocks), bounds are not enforced.
if let (Some(fee_actual), Some(fee_proposal)) =
    (proposal_init_validation.fee_actual, init_proposed.fee_proposal_fri)
{
    // bounds check only runs when BOTH are Some
    ...
}
``` [1](#0-0) 

When `fee_actual` is `None` the entire `if let` body is skipped. No alternative reference (e.g. `l2_gas_price`) is used. The proposer's `fee_proposal_fri` is accepted verbatim.

**`fee_actual` is `None` during startup**: `compute_fee_actual` returns `None` whenever `height < window_size` or any entry in the window is missing. [2](#0-1) 

`ProposalInitValidation.fee_actual` is populated by `compute_fee_actual` at validation time: [3](#0-2) 

**Accepted value enters the window**: After consensus decides, `record_fee_proposal` stores `init.fee_proposal_fri` into `fee_proposals_window`: [4](#0-3) 

**Window median becomes the gas price floor**: `calculate_next_l2_gas_price_for_fin` uses `fee_actual` as `effective_min`:

```rust
let effective_min = match fee_actual {
    Some(fa) => GasPrice(max(config_min.0, fa.0)),
    None => config_min,
};
calculate_next_base_gas_price(current_l2_gas_price, l2_gas_used, gas_target, effective_min)
``` [5](#0-4) 

**Arbitrary value also enters the block commitment**: `proposal_commitment_from` hashes `fee_proposal_fri` into the `ProposalCommitment` that consensus signs over: [6](#0-5) 

The validator computes this commitment using the unchecked `init.fee_proposal_fri`: [7](#0-6) 

**Proposer's own fallback is `l2_gas_price`** — the honest proposer freezes at `l2_gas_price` when `fee_actual` is `None`, but the validator enforces no such constraint: [8](#0-7) 

---

### Impact Explanation

A malicious proposer during the first `window_size` blocks sets `fee_proposal_fri = u128::MAX` (or near-zero). Validators accept it. After `window_size` blocks the median `fee_actual` is skewed toward the injected value. `effective_min = max(config_min, fee_actual)` then forces all subsequent L2 gas prices to that extreme floor:

- **Inflated floor (`u128::MAX`)**: every user transaction is priced out; the network is effectively halted.
- **Deflated floor (0 or 1)**: the fee market floor is destroyed; the sequencer operates below cost indefinitely.

The corrupted `fee_proposal_fri` is also hashed into the `ProposalCommitment` that all validators sign, so the wrong value is permanently committed on-chain.

Impact category: **Critical — Incorrect fee/gas/resource accounting with economic impact.**

---

### Likelihood Explanation

- Triggerable by any validator that wins the proposer slot during the first `window_size` blocks (near genesis or after a chain restart with an empty window). Proposer selection is a normal, non-privileged part of BFT consensus.
- No special permissions, no external dependencies, no race conditions required.
- A single injected extreme value shifts the median if the attacker controls `⌊window_size/2⌋ + 1` startup slots; even a minority of injected values shifts the floor measurably.
- The window is also empty after a node restart that clears `fee_proposals_window` before `initialize_fee_proposals_window` completes, widening the attack surface beyond genesis.

---

### Recommendation

When `fee_actual` is `None`, fall back to `l2_gas_price` as the reference for the bounds check — exactly mirroring the proposer's own fallback:

```rust
let reference = proposal_init_validation.fee_actual
    .unwrap_or(proposal_init_validation.l2_gas_price_fri);

if let Some(fee_proposal) = init_proposed.fee_proposal_fri {
    let (lower_bound, upper_bound) = fee_proposal_bounds(
        reference,
        VersionedConstants::latest_constants().fee_proposal_margin_ppt,
    );
    if fee_proposal.0 < lower_bound || fee_proposal.0 > upper_bound {
        return Err(...);
    }
}
```

This closes the startup window: the proposer's `fee_proposal_fri` is always bounded by an authoritative local value, regardless of whether the sliding window has accumulated enough entries.

---

### Proof of Concept

1. Chain starts at height 0 (`window_size = N`).
2. Malicious validator wins the proposer slot at height 0.
3. It broadcasts `ProposalInit { fee_proposal_fri: Some(GasPrice(u128::MAX)), ... }`.
4. Every honest validator calls `is_proposal_init_valid`:
   - `fee_actual = compute_fee_actual(&window, BlockNumber(0), N)` → `None` (height 0 < N).
   - The `if let (Some(fee_actual), Some(fee_proposal))` arm is **not entered**.
   - Validation returns `Ok(())`.
5. Consensus decides the block; `record_fee_proposal(BlockNumber(0), Some(GasPrice(u128::MAX)))` is called on every node.
6. Repeat for heights 1 … N/2 (attacker wins enough slots to control the median).
7. At height N, `compute_fee_actual` returns `Some(GasPrice(u128::MAX))`.
8. `calculate_next_l2_gas_price_for_fin(..., fee_actual = Some(u128::MAX))` sets `effective_min = u128::MAX`.
9. All subsequent blocks have `l2_gas_price = u128::MAX`; every user transaction is rejected by the gateway's gas-price threshold check. [1](#0-0) [9](#0-8) [4](#0-3)

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

**File:** crates/apollo_consensus_orchestrator/src/dynamic_gas_price/mod.rs (L56-91)
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

**File:** crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs (L1193-1197)
```rust
            fee_actual: compute_fee_actual(
                &self.fee_proposals_window,
                init.height,
                VersionedConstants::latest_constants().fee_proposal_window_size,
            ),
```

**File:** crates/apollo_consensus_orchestrator/src/fee_market/mod.rs (L55-76)
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
```
