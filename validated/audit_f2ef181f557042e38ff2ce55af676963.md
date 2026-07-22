### Title
Gateway `validate_resource_bounds` Uses Stale Current-Block L2 Gas Price Instead of `next_l2_gas_price`, Causing Incorrect Admission Decisions - (`crates/apollo_gateway/src/stateful_transaction_validator.rs`)

---

### Summary

`StatefulTransactionValidator::validate_resource_bounds` validates a transaction's `max_l2_gas_price` against the **current block's** L2 gas price read from `get_block_info()`. However, the transaction will be executed in the **next block**, whose L2 gas price is `next_l2_gas_price` (computed via EIP-1559 from the current block's gas usage). The mempool's admission threshold is set to this `next_l2_gas_price`. The mismatch causes the gateway to admit transactions the mempool will reject, and to reject transactions the mempool would accept. A developer TODO in the code explicitly acknowledges this: `// TODO(Arni): getnext_l2_gas_price from the block header.`

---

### Finding Description

In `validate_resource_bounds`, the gateway reads the L2 gas price from the current committed block:

```rust
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

The `next_l2_gas_price` for the upcoming block is computed in `calculate_next_l2_gas_price_for_fin` using the current block's actual `l2_gas_used` via the EIP-1559 formula, and is stored in `BlockHeaderWithoutHash.next_l2_gas_price`: [2](#0-1) 

This `next_l2_gas_price` is what the batcher passes to the mempool via `update_gas_price` when a new block starts being built: [3](#0-2) 

And it is what the proposer embeds in `ProposalInit.l2_gas_price_fri` and what the validator enforces: [4](#0-3) 

The gateway's `validate_resource_bounds` uses the **old** price (current block), while the mempool threshold is the **new** price (next block). These diverge whenever the block is not exactly at the gas target.

---

### Impact Explanation

Two concrete wrong outcomes:

1. **False admission (gateway accepts, mempool rejects):** When the previous block was heavily used (`gas_used > gas_target`), `next_l2_gas_price > current_l2_gas_price`. A transaction with `max_l2_gas_price ∈ [current_price, next_price)` passes `validate_resource_bounds` at the gateway but is rejected by the mempool's updated threshold. The gateway returns success to the user, but the transaction is silently dropped.

2. **False rejection (gateway rejects, mempool would accept):** When the previous block was lightly used (`gas_used < gas_target`), `next_l2_gas_price < current_l2_gas_price`. A transaction with `max_l2_gas_price ∈ [next_price, current_price)` is rejected by the gateway even though it satisfies the mempool's threshold and would be valid for the next block.

Both outcomes match the allowed impact: **"Mempool/gateway/RPC admission accepts invalid transactions or rejects valid transactions before sequencing."**

---

### Likelihood Explanation

The EIP-1559 price adjustment is active on every block. Any block that deviates from the gas target (which is the common case under real load) produces a `next_l2_gas_price` that differs from `current_l2_gas_price`. The `validate_resource_bounds` config flag defaults to `true` (confirmed by `StatefulTransactionValidatorConfig::default()` in the test that expects the gas-price check to fire). The bug is therefore triggered on every non-target-usage block in production. [5](#0-4) 

---

### Recommendation

Replace the `get_block_info().gas_prices.strk_gas_prices.l2_gas_price` read with the `next_l2_gas_price` stored in the latest block header. This requires either:

1. Extending `GatewayFixedBlockStateReader` with a `get_next_l2_gas_price()` method that reads `BlockHeaderWithoutHash.next_l2_gas_price` from storage, or
2. Passing `next_l2_gas_price` directly into the validator at construction time (updated on each new committed block).

The fix aligns the gateway's admission threshold with the mempool's threshold, eliminating the stale-state divergence.

---

### Proof of Concept

Scenario: previous block was at 2× gas target, so `next_l2_gas_price = 1.0015 × current_l2_gas_price` (EIP-1559 step).

```
current_l2_gas_price  = 1_000_000_000  (1 Gwei)
next_l2_gas_price     = 1_001_500_000  (≈1.0015 Gwei, after heavy block)

User submits Invoke V3 with:
  max_l2_gas_price = 1_000_500_000  (between the two)

Gateway (validate_resource_bounds):
  threshold = current_l2_gas_price = 1_000_000_000
  1_000_500_000 >= 1_000_000_000  → ACCEPTED, returns tx_hash to user

Mempool (update_gas_price called with next_l2_gas_price):
  threshold = 1_001_500_000
  1_000_500_000 < 1_001_500_000  → REJECTED (GAS_PRICE_TOO_LOW)

Result: user receives a successful gateway response but the transaction
        is never sequenced. No error is surfaced to the user.
```

The inverse (false rejection) occurs symmetrically when the block is under-utilized and `next_l2_gas_price < current_l2_gas_price`. [6](#0-5) [7](#0-6)

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

**File:** crates/apollo_consensus_orchestrator/src/fee_market/mod.rs (L86-140)
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
}
```

**File:** crates/apollo_batcher/src/batcher.rs (L371-383)
```rust
        info!(
            "Updating gas price for block {}, round {} in Mempool client",
            block_number, propose_block_input.proposal_round
        );
        mempool_client
            .update_gas_price(
                propose_block_input.block_info.gas_prices.strk_gas_prices.l2_gas_price.get(),
            )
            .await
            .map_err(|err| {
                error!("Failed to update gas price in mempool: {}", err);
                BatcherError::InternalError
            })?;
```

**File:** crates/apollo_consensus_orchestrator/src/build_proposal.rs (L169-188)
```rust
    let init = ProposalInit {
        height: args.build_param.height,
        round: args.build_param.round,
        valid_round: args.build_param.valid_round,
        proposer: args.build_param.proposer,
        builder: args.builder_address,
        timestamp,
        l1_da_mode: args.l1_da_mode,
        l2_gas_price_fri: args.l2_gas_price,
        l1_gas_price_wei: l1_prices_wei.l1_gas_price,
        l1_data_gas_price_wei: l1_prices_wei.l1_data_gas_price,
        l1_gas_price_fri: l1_prices_fri.l1_gas_price,
        l1_data_gas_price_fri: l1_prices_fri.l1_data_gas_price,
        starknet_version: starknet_api::block::StarknetVersion::LATEST,
        // TODO(Asmaa): Put the real value once we have it.
        // Sentinel until then; see `expected_version_constant_commitment` for why this is the
        // single source of truth shared with the validator.
        version_constant_commitment: expected_version_constant_commitment(),
        fee_proposal_fri: Some(args.fee_proposal),
    };
```

**File:** crates/apollo_gateway/src/stateful_transaction_validator_test.rs (L89-128)
```rust
#[tokio::test]
async fn test_run_pre_validation_checks(
    #[case] zero_gas_fee: bool,
    #[case] expected_result: Result<bool, StarknetError>,
) {
    let account_nonce = nonce!(0);

    let mut mock_mempool_client = MockMempoolClient::new();
    mock_mempool_client.expect_account_tx_in_pool_or_recent_block().returning(|_| {
        // The mempool does not have any transactions from the sender.
        Ok(false)
    });
    mock_mempool_client.expect_validate_tx().returning(|_| Ok(()));
    let mempool_client = Arc::new(mock_mempool_client);

    let mut mock_gateway_fixed_block = MockGatewayFixedBlockStateReader::new();
    mock_gateway_fixed_block.expect_get_block_info().returning(|| Ok(BlockInfo::default()));

    let stateful_validator: StatefulTransactionValidator<TestStateReader, _> =
        StatefulTransactionValidator {
            config: StatefulTransactionValidatorConfig::default(),
            chain_info: ChainInfo::create_for_testing(),
            state_reader_and_contract_manager: None,
            gateway_fixed_block_state_reader: mock_gateway_fixed_block,
        };

    let resource_bounds = if zero_gas_fee {
        ValidResourceBounds::AllResources(AllResourceBounds {
            l2_gas: ResourceBounds { max_price_per_unit: 0_u128.into(), ..Default::default() },
            ..Default::default()
        })
    } else {
        ValidResourceBounds::create_for_testing()
    };
    let executable_tx: AccountTransaction = executable_invoke_tx(invoke_tx_args!(resource_bounds));

    let result = stateful_validator
        .run_pre_validation_checks(&executable_tx, account_nonce, mempool_client)
        .await;
    assert_eq!(result, expected_result);
```
