### Title
Gateway L2 Gas Price Admission Uses Stale `l2_gas_price` Instead of `next_l2_gas_price`, Causing Incorrect Transaction Admission Decisions - (`crates/apollo_gateway/src/stateful_transaction_validator.rs`)

---

### Summary

The gateway's `validate_resource_bounds` check compares a transaction's `max_price_per_unit` against `block_N.l2_gas_price` — the price that was **already used** in the last committed block. The next block (N+1) will actually execute at `block_N.next_l2_gas_price`, which is a distinct, EIP-1559-adjusted value. Because the "pending" price change is never applied to the admission threshold, the gateway either accepts transactions that will be rejected by the batcher (price rising) or rejects transactions that would be valid in the next block (price falling). A `TODO` comment in the source code explicitly acknowledges this gap.

---

### Finding Description

`StatefulTransactionValidator::validate_resource_bounds` reads the L2 gas price for threshold computation from `GatewayFixedBlockStateReader::get_block_info()`:

```rust
// TODO(Arni): getnext_l2_gas_price from the block header.
let previous_block_l2_gas_price = self
    .gateway_fixed_block_state_reader
    .get_block_info()
    .await?
    .gas_prices
    .strk_gas_prices
    .l2_gas_price;
self.validate_tx_l2_gas_price_within_threshold(
    executable_tx.resource_bounds(),
    previous_block_l2_gas_price,
)?;
``` [1](#0-0) 

`GatewayFixedBlockSyncStateClient::get_block_info_from_sync_client` populates this from `block_header.l2_gas_price`:

```rust
l2_gas_price: block_header.l2_gas_price.price_in_fri.try_into()?,
``` [2](#0-1) 

`BlockHeaderWithoutHash` carries **two** distinct fields:

```rust
pub l2_gas_price: GasPricePerToken,   // price used in block N
pub next_l2_gas_price: GasPrice,      // price that will be used in block N+1
``` [3](#0-2) 

After block N is decided, `SequencerConsensusContext::update_l2_gas_price` advances the context's `l2_gas_price` to `next_l2_gas_price` from block N, and this updated value is embedded in the next `ProposalInit.l2_gas_price_fri`:

```rust
fn update_l2_gas_price(&mut self, height: BlockNumber, l2_gas_used: GasAmount) {
    self.l2_gas_price = self.calculate_next_l2_gas_price(height, l2_gas_used);
``` [4](#0-3) 

The validator enforces that `ProposalInit.l2_gas_price_fri` equals this updated price:

```rust
&& init_proposed.l2_gas_price_fri == proposal_init_validation.l2_gas_price_fri
``` [5](#0-4) 

So block N+1 executes at `block_N.next_l2_gas_price`, but the gateway threshold is computed from `block_N.l2_gas_price`. The "pending" EIP-1559 price adjustment is never reflected in the admission decision.

`validate_tx_l2_gas_price_within_threshold` rejects any transaction whose `max_price_per_unit` falls below `min_gas_price_percentage% × previous_block_l2_gas_price`:

```rust
let threshold = (gas_price_threshold_multiplier
    * previous_block_l2_gas_price.get().0)
    .to_integer();
if tx_l2_gas_price.0 < threshold {
    return Err(StarknetError { ... });
}
``` [6](#0-5) 

---

### Impact Explanation

**Price-rising scenario** (`next_l2_gas_price > l2_gas_price`): A transaction with `max_price_per_unit` in the range `[min_gas_price_percentage% × l2_gas_price, min_gas_price_percentage% × next_l2_gas_price)` passes the gateway check but is below the correct threshold for the next block. It enters the mempool and is later rejected by the batcher at pre-validation, wasting mempool slots and user-facing round-trips. **Gateway accepts invalid transactions.**

**Price-falling scenario** (`next_l2_gas_price < l2_gas_price`): A transaction with `max_price_per_unit` in the range `[min_gas_price_percentage% × next_l2_gas_price, min_gas_price_percentage% × l2_gas_price)` is rejected by the gateway with `GAS_PRICE_TOO_LOW` even though it would be valid in the next block. **Gateway rejects valid transactions.**

Both cases match the allowed impact: *"High. Mempool/gateway/RPC admission accepts invalid transactions or rejects valid transactions before sequencing."*

---

### Likelihood Explanation

The EIP-1559 mechanism adjusts `next_l2_gas_price` every block based on utilization. With `MIN_GAS_PRICE_INCREASE_DENOMINATOR = 333`, the price can shift by ~0.3% per block:

```rust
const MIN_GAS_PRICE_INCREASE_DENOMINATOR: u128 = 333;
``` [7](#0-6) 

Under sustained high or low utilization, `next_l2_gas_price` diverges from `l2_gas_price` continuously. The discrepancy is permanent (not transient), affects every transaction validated while `validate_resource_bounds` is enabled, and is explicitly acknowledged by the in-code `TODO`. The `SyncStateReaderFactory` always supplies the latest committed block's `l2_gas_price` field, never `next_l2_gas_price`:

```rust
let gateway_fixed_block_sync_state_client = GatewayFixedBlockSyncStateClient::new(
    self.shared_state_sync_client.clone(),
    latest_block_number,
);
``` [8](#0-7) 

---

### Recommendation

In `GatewayFixedBlockSyncStateClient::get_block_info_from_sync_client` (or in a new dedicated accessor), expose `block_header.next_l2_gas_price` and use it as the threshold base in `validate_resource_bounds` instead of `block_header.l2_gas_price`. The `BlockInfo` struct may need a `next_l2_gas_price` field, or `validate_resource_bounds` can call a separate `get_next_l2_gas_price()` method on `GatewayFixedBlockStateReader`. This directly resolves the acknowledged `TODO(Arni)`.

---

### Proof of Concept

1. Block N is committed with `l2_gas_price = 10 gwei` and `next_l2_gas_price = 10.03 gwei` (one block of high utilization).
2. A user submits a V3 transaction with `l2_gas.max_price_per_unit = 5.01 gwei` and `min_gas_price_percentage = 50`.
3. Gateway threshold = `50% × 10 gwei = 5 gwei`. Transaction passes: `5.01 >= 5`. ✓
4. Batcher builds block N+1 at `l2_gas_price = 10.03 gwei`. Correct threshold = `50% × 10.03 gwei = 5.015 gwei`. Transaction should fail: `5.01 < 5.015`. ✗
5. Transaction is accepted into the mempool but rejected by the batcher — incorrect admission decision caused by the stale price.

Conversely, with `next_l2_gas_price = 9.97 gwei` (falling price), a transaction with `max_price_per_unit = 4.99 gwei` is rejected by the gateway (`4.99 < 5`) but would be valid in block N+1 (`4.99 >= 50% × 9.97 = 4.985`).

### Citations

**File:** crates/apollo_gateway/src/stateful_transaction_validator.rs (L228-241)
```rust
        if self.config.validate_resource_bounds {
            // TODO(Arni): getnext_l2_gas_price from the block header.
            let previous_block_l2_gas_price = self
                .gateway_fixed_block_state_reader
                .get_block_info()
                .await?
                .gas_prices
                .strk_gas_prices
                .l2_gas_price;
            self.validate_tx_l2_gas_price_within_threshold(
                executable_tx.resource_bounds(),
                previous_block_l2_gas_price,
            )?;
        }
```

**File:** crates/apollo_gateway/src/stateful_transaction_validator.rs (L367-383)
```rust
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
```

**File:** crates/apollo_gateway/src/gateway_fixed_block_state_reader.rs (L48-49)
```rust
                    l1_data_gas_price: block_header.l1_data_gas_price.price_in_fri.try_into()?,
                    l2_gas_price: block_header.l2_gas_price.price_in_fri.try_into()?,
```

**File:** crates/starknet_api/src/block.rs (L237-239)
```rust
    pub l2_gas_price: GasPricePerToken,
    pub l2_gas_consumed: GasAmount,
    pub next_l2_gas_price: GasPrice,
```

**File:** crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs (L496-497)
```rust
    fn update_l2_gas_price(&mut self, height: BlockNumber, l2_gas_used: GasAmount) {
        self.l2_gas_price = self.calculate_next_l2_gas_price(height, l2_gas_used);
```

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L312-314)
```rust
    if !(init_proposed.height == proposal_init_validation.height
        && init_proposed.l1_da_mode == proposal_init_validation.l1_da_mode
        && init_proposed.l2_gas_price_fri == proposal_init_validation.l2_gas_price_fri)
```

**File:** crates/apollo_consensus_orchestrator/src/fee_market/mod.rs (L21-21)
```rust
const MIN_GAS_PRICE_INCREASE_DENOMINATOR: u128 = 333;
```

**File:** crates/apollo_gateway/src/sync_state_reader.rs (L545-548)
```rust
        let gateway_fixed_block_sync_state_client = GatewayFixedBlockSyncStateClient::new(
            self.shared_state_sync_client.clone(),
            latest_block_number,
        );
```
