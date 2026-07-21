### Title
Unbounded `fee_proposal_fri` During Startup Window Permanently Inflates L2 Gas Price — (File: `crates/apollo_consensus_orchestrator/src/validate_proposal.rs`)

---

### Summary

During the first `fee_proposal_window_size` (10) blocks, the `fee_proposal_fri` field in `ProposalInit` has **no upper bound enforced** by validators. A proposer controlling a majority of the startup window can set `fee_proposal_fri` to `u128::MAX`. After the window fills, `fee_actual` becomes `u128::MAX`, permanently driving the L2 gas price floor toward `u128::MAX` for all subsequent blocks, making every V3 transaction fail pre-validation and breaking gateway admission.

---

### Finding Description

In `is_proposal_init_valid`, the bounds check on `fee_proposal_fri` is gated on `proposal_init_validation.fee_actual` being `Some`:

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
        return Err(...);
    }
}
``` [1](#0-0) 

`fee_actual` is computed by `compute_fee_actual`, which returns `None` whenever the `fee_proposals_window` does not contain all `window_size` (10) entries for the required range:

```rust
let Some(start) = height.0.checked_sub(window_size) else {
    warn!("Cannot compute fee_actual for height {height}: height is below window_size ({window_size})");
    return None;
};
...
Some(None) | None => {
    warn!("Cannot compute fee_actual for height {height}: ...");
    return None;
}
``` [2](#0-1) 

This means for the first 10 blocks of a new chain (or after a restart where the window is empty), **any value of `fee_proposal_fri` passes validation without bounds checking**, including `u128::MAX`.

The accepted `fee_proposal_fri` is then recorded into `fee_proposals_window` at decision time:

```rust
self.update_l2_gas_price(height, l2_gas_used);
self.record_fee_proposal(height, init.fee_proposal_fri);
``` [3](#0-2) 

After `window_size` blocks, `fee_actual` is the median of those recorded values. This `fee_actual` is then used as the **floor** for the next block's L2 gas price:

```rust
let effective_min = match fee_actual {
    Some(fa) => GasPrice(max(config_min.0, fa.0)),
    None => config_min,
};
calculate_next_base_gas_price(current_l2_gas_price, l2_gas_used, gas_target, effective_min)
``` [4](#0-3) 

The `fee_proposal_fri` is bound into the `ProposalCommitment` via Poseidon hash, but this only prevents equivocation — it does not cap the value:

```rust
pub(crate) fn proposal_commitment_from(partial: PartialBlockHash, fee_proposal: Option<GasPrice>) -> ProposalCommitment {
    let Some(fee_proposal) = fee_proposal else { return ProposalCommitment(partial.0); };
    ProposalCommitment(Poseidon::hash_array(&[partial.0, Felt::from(fee_proposal.0)]))
}
``` [5](#0-4) 

There is no `MAX_FEE_PROPOSAL` constant anywhere in the codebase. The `fee_proposal_margin_ppt = 2` (0.2% per block) only applies once `fee_actual` is `Some`. [6](#0-5) 

---

### Impact Explanation

The `l2_gas_price_fri` in `ProposalInit` is the price used by the blockifier to execute transactions. With `l2_gas_price = u128::MAX`:

- All V3 (`AllResources`) transactions fail pre-validation at `check_resource_bounds` with `MaxGasPriceTooLow` for the L2 gas resource.
- The gateway's `validate_tx_l2_gas_price_within_threshold` rejects all incoming V3 transactions using the previous block's inflated L2 gas price. [7](#0-6) 

This permanently breaks the chain's fee market and denies service to all users. The corrupted value (`l2_gas_price = u128::MAX`) propagates into every subsequent block's `ProposalInit.l2_gas_price_fri`, which validators check for exact equality — so all validators agree on the inflated price and the chain cannot self-correct.

**Impact category**: Critical — Incorrect fee, gas, resource accounting with economic impact; High — Mempool/gateway admission rejects valid transactions.

---

### Likelihood Explanation

- Requires controlling **>50% of proposer slots** in the first `window_size` (10) blocks (to control the median).
- On a new chain (genesis), `fee_proposals_window` starts empty. `initialize_fee_proposals_window` reads from state_sync, but for a fresh chain there are no prior blocks to read.
- In a Tendermint-style rotation, a validator with >50% stake controls the majority of early proposer slots.
- The attack is permanent: once `fee_actual` is inflated, the tight 0.2%/block margin prevents recovery.

---

### Recommendation

Add a hardcoded `MAX_FEE_PROPOSAL_FRI` cap enforced unconditionally in `is_proposal_init_valid`, regardless of whether `fee_actual` is `Some` or `None`:

```rust
// Enforce absolute cap on fee_proposal regardless of window state.
const MAX_FEE_PROPOSAL_FRI: u128 = /* e.g., 10 * min_gas_price or a protocol constant */;
if let Some(fee_proposal) = init_proposed.fee_proposal_fri {
    if fee_proposal.0 > MAX_FEE_PROPOSAL_FRI {
        return Err(ValidateProposalError::InvalidProposalInit(..., "fee_proposal exceeds MAX_FEE_PROPOSAL_FRI"));
    }
}
```

This mirrors the judge's recommendation in M-03: "I believe protocol users could get stronger security guarantees by having a MAX_FEE hardcoded variable to ensure fees can never go above a certain threshold."

---

### Proof of Concept

1. Start a new chain at genesis. `fee_proposals_window` is empty; `compute_fee_actual` returns `None` for all heights `< window_size` (10).
2. For blocks 0–9, the proposer sets `fee_proposal_fri = Some(GasPrice(u128::MAX))` in `ProposalInit`.
3. Validators call `is_proposal_init_valid`. The check at line 398 evaluates `(None, Some(u128::MAX))` — the `if let` does not match, so **no bounds check is performed**. The proposal is accepted.
4. At `decision_reached` for each block, `record_fee_proposal(height, Some(u128::MAX))` inserts `u128::MAX` into `fee_proposals_window`.
5. At block 10, `compute_fee_actual` returns `Some(u128::MAX)` (median of ten `u128::MAX` values).
6. `calculate_next_l2_gas_price_for_fin` sets `effective_min = u128::MAX`. `calculate_next_base_gas_price` with `min_gas_price = u128::MAX` returns `u128::MAX` (or approaches it via the gradual increase path).
7. Block 11's `ProposalInit.l2_gas_price_fri = u128::MAX`. All validators agree (they computed the same `fee_actual`).
8. Every V3 transaction submitted to the gateway is rejected: `tx.l2_gas.max_price_per_unit < u128::MAX` → `GAS_PRICE_TOO_LOW`. The chain is permanently broken for user transactions. [1](#0-0) [8](#0-7) [9](#0-8)

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

**File:** crates/apollo_consensus_orchestrator/src/dynamic_gas_price/mod.rs (L61-80)
```rust
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

**File:** crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs (L517-518)
```rust
        self.update_l2_gas_price(height, l2_gas_used);
        self.record_fee_proposal(height, init.fee_proposal_fri);
```

**File:** crates/apollo_consensus_orchestrator/src/fee_market/mod.rs (L54-77)
```rust
/// Compute the next L2 gas price (for the fin or for updating state). Respects override when set.
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

**File:** crates/apollo_gateway/src/stateful_transaction_validator.rs (L359-390)
```rust
    fn validate_tx_l2_gas_price_within_threshold(
        &self,
        tx_resource_bounds: ValidResourceBounds,
        previous_block_l2_gas_price: NonzeroGasPrice,
    ) -> StatefulTransactionValidatorResult<()> {
        match tx_resource_bounds {
            ValidResourceBounds::AllResources(tx_resource_bounds) => {
                let tx_l2_gas_price = tx_resource_bounds.l2_gas.max_price_per_unit;
                let gas_price_threshold_multiplier =
                    Ratio::new(self.config.min_gas_price_percentage.into(), 100_u128);
                let threshold = (gas_price_threshold_multiplier
                    * previous_block_l2_gas_price.get().0)
                    .to_integer();
                if tx_l2_gas_price.0 < threshold {
                    return Err(StarknetError {
                        // We didn't have this kind of an error.
                        code: StarknetErrorCode::UnknownErrorCode(
                            "StarknetErrorCode.GAS_PRICE_TOO_LOW".to_string(),
                        ),
                        message: format!(
                            "Transaction L2 gas price {tx_l2_gas_price} is below the required \
                             threshold {threshold}.",
                        ),
                    });
                }
            }
            ValidResourceBounds::L1Gas(_) => {
                // No validation required for legacy transactions.
            }
        }
        Ok(())
    }
```
