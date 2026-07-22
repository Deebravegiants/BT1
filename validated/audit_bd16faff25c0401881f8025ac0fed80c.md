### Title
Gateway L2 Gas Price Admission Check Uses Stale Previous-Block Price, Causing Valid Transactions to Be Rejected and Invalid Transactions to Be Admitted — (`crates/apollo_gateway/src/stateful_transaction_validator.rs`)

---

### Summary

`StatefulTransactionValidator::validate_resource_bounds` validates a transaction's `max_price_per_unit` against the **previous committed block's** L2 gas price. Because the EIP-1559 fee market adjusts the price every block, the price the transaction will actually face during execution (the *next* block's price) can differ by up to `price / gas_price_max_change_denominator` (~2% with the current constant of 48). This produces two admission errors that mirror the H-04 "max-borrow-without-safety-factor" pattern: the gateway either rejects a transaction that is valid for the next block (price decreasing) or admits a transaction whose `max_price` is below the next block's price (price increasing), causing it to fail pre-validation during execution.

---

### Finding Description

In `validate_resource_bounds`:

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

The threshold is then computed as:

```rust
let threshold = (gas_price_threshold_multiplier
    * previous_block_l2_gas_price.get().0)
    .to_integer();
if tx_l2_gas_price.0 < threshold {
    return Err(StarknetError { ... });
}
``` [2](#0-1) 

The `GatewayFixedBlockSyncStateClient` reads the **last committed block's** `l2_gas_price` field, not the `next_l2_gas_price` field that the block header explicitly stores for this purpose: [3](#0-2) 

The next block's price is computed by `calculate_next_base_gas_price` (EIP-1559):

```rust
let price_change = (price_u256 * gas_delta) / denominator;
let adjusted_price_u256 =
    if gas_used > gas_target { price_u256 + price_change }
    else { price_u256 - price_change };
``` [4](#0-3) 

With `gas_price_max_change_denominator = 48`, the price can shift by up to ~2.1% per block. The `next_l2_gas_price` is already stored in the block header: [5](#0-4) 

The TODO comment in the production code explicitly acknowledges the wrong value is being used: [6](#0-5) 

The same stale price is used in `run_validate_entry_point`, which builds the block context for the `__validate__` entry point with the previous block's gas prices but the next block number:

```rust
let mut block_info = self.gateway_fixed_block_state_reader.get_block_info().await?;
block_info.block_number = block_info.block_number.unchecked_next();
let block_context = BlockContext::new(block_info, ...);
``` [7](#0-6) 

---

### Impact Explanation

**Case A — Rejects valid transactions (price decreasing):**
When the previous block was lightly loaded (`gas_used < gas_target`), the next block's price `P_{N+1} < P_N`. A user who correctly sets `max_price = P_{N+1}` (the price they will actually face) is rejected by the gateway because `P_{N+1} < P_N = threshold`. The transaction is valid for the next block but is denied admission.

**Case B — Admits transactions that fail execution (price increasing):**
When the previous block was heavily loaded (`gas_used > gas_target`), `P_{N+1} > P_N`. A user sets `max_price = P_N` (exactly at the gateway threshold). The gateway admits the transaction. During execution in block N+1, the blockifier's pre-validation check `max_price_per_unit >= actual_gas_price` fails because `P_N < P_{N+1}`, causing the transaction to be rejected without fee collection. The mempool's `update_gas_price` call partially compensates by moving such transactions to the pending queue after block commit, but there is a race window between gateway admission and mempool threshold update.

Both cases match the allowed impact: **"High. Mempool/gateway/RPC admission accepts invalid transactions or rejects valid transactions before sequencing."**

---

### Likelihood Explanation

The EIP-1559 adjustment fires every block. On a live network with variable load, `gas_used` routinely diverges from `gas_target` (3.2 × 10⁹ gas), so `P_{N+1} ≠ P_N` is the normal case, not the exception. Any user who sets `max_price` to the current block's price (the natural thing to do, e.g., from `starknet_estimateFee`) is affected whenever the price moves between the estimation block and the execution block.

---

### Recommendation

Replace the `l2_gas_price` field read from the previous block with the `next_l2_gas_price` field that is already stored in the block header for exactly this purpose:

```rust
// In GatewayFixedBlockSyncStateClient::get_block_info_from_sync_client,
// expose next_l2_gas_price, or add a separate accessor.
// In validate_resource_bounds:
let next_block_l2_gas_price = self
    .gateway_fixed_block_state_reader
    .get_next_l2_gas_price()   // reads block_header.next_l2_gas_price
    .await?;
self.validate_tx_l2_gas_price_within_threshold(
    executable_tx.resource_bounds(),
    next_block_l2_gas_price,
)?;
```

The same fix should be applied to `run_validate_entry_point`, which should populate `block_info.gas_prices` with the next block's prices (derived from `next_l2_gas_price`) rather than the previous block's prices.

---

### Proof of Concept

**Scenario A (valid tx rejected):**

1. Block N: `l2_gas_price = 1000 fri`, `gas_used < gas_target` → `next_l2_gas_price = 979 fri`.
2. User queries `starknet_estimateFee` and receives `979 fri` as the next block price.
3. User submits tx with `max_l2_gas_price = 979`.
4. `validate_resource_bounds` computes `threshold = 100% × 1000 = 1000`.
5. `979 < 1000` → gateway returns `GAS_PRICE_TOO_LOW` and rejects the transaction.
6. The transaction would have executed successfully in block N+1 (price = 979).

**Scenario B (invalid tx admitted, fails in batcher):**

1. Block N: `l2_gas_price = 1000 fri`, `gas_used >> gas_target` → `next_l2_gas_price = 1021 fri`.
2. User submits tx with `max_l2_gas_price = 1000`.
3. `validate_resource_bounds` computes `threshold = 1000`; `1000 >= 1000` → gateway admits.
4. Mempool admits (threshold not yet updated).
5. Block N committed; mempool updates threshold to 1021; tx moves to pending queue.
   — *Or*, in the race window before the mempool update, the batcher fetches the tx:*
6. Batcher executes tx in block N+1 (price = 1021); blockifier pre-validation: `1000 < 1021` → `MaxGasPriceTooLow` → tx rejected, no fee charged, block space wasted.

### Citations

**File:** crates/apollo_gateway/src/stateful_transaction_validator.rs (L223-243)
```rust
    async fn validate_resource_bounds(
        &self,
        executable_tx: &ExecutableTransaction,
    ) -> StatefulTransactionValidatorResult<()> {
        // Skip this validation during the systems bootstrap phase.
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
        Ok(())
    }
```

**File:** crates/apollo_gateway/src/stateful_transaction_validator.rs (L323-330)
```rust
        let mut block_info = self.gateway_fixed_block_state_reader.get_block_info().await?;
        block_info.block_number = block_info.block_number.unchecked_next();
        let block_context = BlockContext::new(
            block_info,
            self.chain_info.clone(),
            versioned_constants,
            BouncerConfig::max(),
        );
```

**File:** crates/apollo_gateway/src/stateful_transaction_validator.rs (L358-390)
```rust
    // TODO(Arni): Consider running this validation for all gas prices.
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

**File:** crates/apollo_gateway/src/gateway_fixed_block_state_reader.rs (L30-57)
```rust
    async fn get_block_info_from_sync_client(&self) -> StarknetResult<BlockInfo> {
        let block = self.state_sync_client.get_block(self.block_number).await.map_err(|e| {
            StarknetError::internal_with_logging("Failed to get latest block info", e)
        })?;

        let block_header = block.block_header_without_hash;
        let block_info = BlockInfo {
            block_number: block_header.block_number,
            block_timestamp: block_header.timestamp,
            sequencer_address: block_header.sequencer.0,
            gas_prices: GasPrices {
                eth_gas_prices: GasPriceVector {
                    l1_gas_price: block_header.l1_gas_price.price_in_wei.try_into()?,
                    l1_data_gas_price: block_header.l1_data_gas_price.price_in_wei.try_into()?,
                    l2_gas_price: block_header.l2_gas_price.price_in_wei.try_into()?,
                },
                strk_gas_prices: GasPriceVector {
                    l1_gas_price: block_header.l1_gas_price.price_in_fri.try_into()?,
                    l1_data_gas_price: block_header.l1_data_gas_price.price_in_fri.try_into()?,
                    l2_gas_price: block_header.l2_gas_price.price_in_fri.try_into()?,
                },
            },
            use_kzg_da: block_header.l1_da_mode.is_use_kzg_da(),
            starknet_version: block_header.starknet_version,
        };

        Ok(block_info)
    }
```

**File:** crates/apollo_consensus_orchestrator/src/fee_market/mod.rs (L117-139)
```rust
    // Use U256 to avoid overflow, as multiplying a u128 by a u64 remains within U256 bounds.
    let gas_delta = U256::from(gas_used.0.abs_diff(gas_target.0));
    let gas_target_u256 = U256::from(gas_target.0);
    let price_u256 = U256::from(price.0);

    // Calculate price change by multiplying first, then dividing. This avoids the precision loss
    // that occurs when dividing before multiplying.
    let denominator =
        gas_target_u256 * U256::from(versioned_constants.gas_price_max_change_denominator);
    let price_change = (price_u256 * gas_delta) / denominator;

    let adjusted_price_u256 =
        if gas_used > gas_target { price_u256 + price_change } else { price_u256 - price_change };

    // Sanity check: ensure direction of change is correct
    assert!(
        gas_used > gas_target && adjusted_price_u256 >= price_u256
            || gas_used <= gas_target && adjusted_price_u256 <= price_u256
    );

    // Price should not realistically exceed u128::MAX, bound to avoid theoretical overflow.
    let adjusted_price = u128::try_from(adjusted_price_u256).unwrap_or(u128::MAX);
    GasPrice(max(adjusted_price, min_gas_price.0))
```

**File:** crates/apollo_storage/src/header.rs (L88-89)
```rust
    /// The next L2 gas price.
    pub next_l2_gas_price: GasPrice,
```
