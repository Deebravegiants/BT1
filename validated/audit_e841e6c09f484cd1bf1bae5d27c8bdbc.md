### Title
Zero-price trap in `calculate_next_base_gas_price` permanently locks L2 gas price at zero — (File: `crates/apollo_consensus_orchestrator/src/fee_market/mod.rs`)

---

### Summary

`calculate_next_base_gas_price` uses a multiplicative step `price + price / MIN_GAS_PRICE_INCREASE_DENOMINATOR` to gradually raise a below-minimum price toward `min_gas_price`. When `price == 0` the step is `0 + 0/333 = 0`, and the subsequent `adjusted.min(min_gas_price.0)` call returns `0` (not `min_gas_price`), permanently trapping the L2 gas price at zero. This is the direct sequencer analog of the external report's "zero-total precision loss" bug class: a multiplicative formula that produces zero when its base value is zero, with no additive floor to escape.

---

### Finding Description

In `calculate_next_base_gas_price`:

```rust
if price < min_gas_price {
    let max_increase = price.0 / MIN_GAS_PRICE_INCREASE_DENOMINATOR; // 0 / 333 = 0
    let adjusted = price.0 + max_increase;                            // 0 + 0 = 0
    // Cap at min_gas_price to avoid overshooting
    let adjusted_price = adjusted.min(min_gas_price.0);               // 0.min(X) = 0
    return GasPrice(adjusted_price);                                   // returns 0
}
``` [1](#0-0) 

When `price.0 == 0` and `min_gas_price.0 > 0`:
- `max_increase = 0 / 333 = 0`
- `adjusted = 0`
- `adjusted.min(min_gas_price.0)` evaluates to `0` (Rust `u128::min` returns the smaller value; `0 < min_gas_price.0`)
- The function returns `GasPrice(0)` — identical to its input

Every subsequent call to `update_l2_gas_price` feeds the returned `0` back as `current_l2_gas_price`, so the price never escapes zero. The normal EIP-1559 path (lines 117–139) is never reached because `0 < min_gas_price` is always true. [2](#0-1) 

The `calculate_next_l2_gas_price_for_fin` wrapper, called from both the proposer (`build_proposal.rs`) and the validator (`update_l2_gas_price`), passes `current_l2_gas_price` directly into this function without a zero-guard: [3](#0-2) 

`update_l2_gas_price` then stores the returned zero back into `self.l2_gas_price`: [4](#0-3) 

---

### Impact Explanation

If `l2_gas_price` reaches zero, every subsequent block produced by this node carries `l2_gas_price_fri = 0`. Two consequences follow:

1. **Economic**: All transactions in those blocks pay zero L2 gas fees — a direct "Incorrect fee … with economic impact" (Critical).
2. **Liveness**: `convert_to_sn_api_block_info` calls `NonzeroGasPrice::new(init.l2_gas_price_fri)?`, which returns an error on zero, causing the proposal build to fail and consensus to stall. [5](#0-4) 

---

### Likelihood Explanation

**Low.** In normal startup the bootstrap in `set_height_and_round` (first height only) enforces `l2_gas_price = max(l2_gas_price, min_gas_price_for_height)`, preventing zero at launch: [6](#0-5) 

After the first height, `l2_gas_price` is only updated via `update_l2_gas_price` → `calculate_next_base_gas_price`, whose normal EIP-1559 path always returns `max(adjusted, min_gas_price) ≥ min_gas_price > 0`. However, the `try_sync` path can overwrite `l2_gas_price` directly from a synced block's `next_l2_gas_price` field (which defaults to `GasPrice(0)`). If `try_sync` is invoked after the first height with a block whose `next_l2_gas_price == 0`, the trap is set and the price never recovers.

---

### Recommendation

Replace the multiplicative-only step with an additive floor of at least 1 so the price can always escape zero:

```rust
if price < min_gas_price {
    let max_increase = price.0 / MIN_GAS_PRICE_INCREASE_DENOMINATOR;
    let adjusted = price.0.saturating_add(max_increase).max(1); // additive floor
    let adjusted_price = adjusted.min(min_gas_price.0);
    return GasPrice(adjusted_price);
}
```

Alternatively, add an explicit guard at the entry of `calculate_next_base_gas_price` (or in `calculate_next_l2_gas_price_for_fin`) that clamps `price` to at least 1 before the below-minimum branch is evaluated.

---

### Proof of Concept

```
price = GasPrice(0), min_gas_price = GasPrice(30_000_000_000)  // versioned-constants default

Block N:
  max_increase = 0 / 333 = 0
  adjusted     = 0 + 0   = 0
  adjusted_price = 0.min(30_000_000_000) = 0
  → returns GasPrice(0)

Block N+1: same inputs, same result.
Block N+k: GasPrice(0) forever.

Downstream: ProposalInit.l2_gas_price_fri = 0
  → NonzeroGasPrice::new(0) returns Err(ZeroGasPrice)
  → proposal build fails
  → consensus stalls, or (if guard is bypassed) all transactions execute at zero L2 gas cost.
``` [7](#0-6) [8](#0-7)

### Citations

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

**File:** crates/apollo_consensus_orchestrator/src/fee_market/mod.rs (L86-115)
```rust
pub fn calculate_next_base_gas_price(
    price: GasPrice,
    gas_used: GasAmount,
    gas_target: GasAmount,
    min_gas_price: GasPrice,
) -> GasPrice {
    let versioned_constants = VersionedConstants::latest_constants();
    assert!(
        gas_target < versioned_constants.max_block_size,
        "Gas target must be lower than max block size."
    );
    assert!(gas_target.0 > 0, "Gas target must be greater than zero.");
    assert!(
        versioned_constants.gas_price_max_change_denominator > 0,
        "Denominator constant must be greater than zero."
    );

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
    }
```

**File:** crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs (L496-500)
```rust
    fn update_l2_gas_price(&mut self, height: BlockNumber, l2_gas_used: GasAmount) {
        self.l2_gas_price = self.calculate_next_l2_gas_price(height, l2_gas_used);
        let gas_price_u64 = u64::try_from(self.l2_gas_price.0).unwrap_or(u64::MAX);
        CONSENSUS_L2_GAS_PRICE.set_lossy(gas_price_u64);
    }
```

**File:** crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs (L1119-1127)
```rust
            if self.current_height.is_none() {
                let min_gas_price_for_height = get_min_gas_price_for_height(
                    height,
                    &self.config.dynamic_config.min_l2_gas_price_per_height,
                );
                self.l2_gas_price = max(self.l2_gas_price, min_gas_price_for_height);
                let gas_price_u64 = u64::try_from(self.l2_gas_price.0).unwrap_or(u64::MAX);
                CONSENSUS_L2_GAS_PRICE.set_lossy(gas_price_u64);
            }
```

**File:** crates/apollo_consensus_orchestrator/src/utils.rs (L304-317)
```rust
    if init.l1_gas_price_fri.0 == 0
        || init.l1_gas_price_wei.0 == 0
        || init.l1_data_gas_price_fri.0 == 0
        || init.l1_data_gas_price_wei.0 == 0
        || init.l2_gas_price_fri.0 == 0
    {
        warn!("Zero gas price detected in block info: {:?}", init);
    }

    let l1_gas_price_fri = NonzeroGasPrice::new(init.l1_gas_price_fri)?;
    let l1_data_gas_price_fri = NonzeroGasPrice::new(init.l1_data_gas_price_fri)?;
    let l1_gas_price_wei = NonzeroGasPrice::new(init.l1_gas_price_wei)?;
    let l1_data_gas_price_wei = NonzeroGasPrice::new(init.l1_data_gas_price_wei)?;
    let l2_gas_price_fri = NonzeroGasPrice::new(init.l2_gas_price_fri)?;
```

**File:** crates/starknet_api/src/block.rs (L529-534)
```rust
    pub fn new(price: GasPrice) -> Result<Self, StarknetApiError> {
        if price.0 == 0 {
            return Err(StarknetApiError::ZeroGasPrice);
        }
        Ok(Self(price))
    }
```
