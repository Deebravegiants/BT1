### Title
Gateway Stateful Validator Skips L1 Gas and L1 Data Gas Price Threshold Checks, Admitting Transactions That Will Fail During Execution - (File: `crates/apollo_gateway/src/stateful_transaction_validator.rs`)

---

### Summary

The `StatefulTransactionValidator::validate_resource_bounds` function only validates the transaction's `l2_gas.max_price_per_unit` against the previous block's L2 gas price. It never checks `l1_gas.max_price_per_unit` or `l1_data_gas.max_price_per_unit` against the actual L1 gas prices. A transaction with these fields set to zero (or any value below the current L1/L1-data gas price) passes gateway admission and enters the mempool, but is guaranteed to be rejected by the blockifier's pre-validation during block execution.

---

### Finding Description

`validate_resource_bounds` in `StatefulTransactionValidator` calls only `validate_tx_l2_gas_price_within_threshold`, which is explicitly annotated with a TODO acknowledging the gap:

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
            // ... checks only l2_gas price ...
        }
        ValidResourceBounds::L1Gas(_) => {
            // No validation required for legacy transactions.
        }
    }
    Ok(())
}
``` [1](#0-0) 

The `validate_resource_bounds` wrapper reads only `strk_gas_prices.l2_gas_price` from the previous block and passes it to the single-resource check, leaving `l1_gas_price` and `l1_data_gas_price` entirely unchecked at the gateway layer: [2](#0-1) 

In contrast, the blockifier's `check_fee_bounds` (called during actual block execution) validates **all three** gas prices for `AllResources` transactions — L1 gas, L1 data gas, and L2 gas — against the actual block gas prices: [3](#0-2) 

The `StatelessTransactionValidator` only checks that at least one resource bound is non-zero and that `l2_gas.max_price_per_unit >= min_gas_price` (a static floor), not that L1 prices are sufficient: [4](#0-3) 

---

### Impact Explanation

A transaction submitted with `AllResources` bounds where `l1_gas.max_price_per_unit = 0` and/or `l1_data_gas.max_price_per_unit = 0` (below the actual block L1 gas price):

1. Passes `StatelessTransactionValidator` — the zero-bounds check only requires at least one non-zero bound across all three resources; a non-zero `l2_gas` bound satisfies it.
2. Passes `StatefulTransactionValidator::validate_resource_bounds` — only L2 gas price is compared to the threshold.
3. Is admitted to the mempool.
4. When the batcher pulls it for block execution, the blockifier's `check_fee_bounds` fires `TransactionFeeError::InsufficientResourceBounds` for `L1Gas` or `L1DataGas`, and the transaction is rejected.

This matches the **High** impact: **Mempool/gateway/RPC admission accepts invalid transactions before sequencing.** The gateway invariant — that admitted transactions have resource bounds sufficient to cover actual execution costs — is broken for the L1 and L1 data gas dimensions.

---

### Likelihood Explanation

Any user (no privilege required) can craft a v3 `AllResources` transaction with `l1_gas.max_price_per_unit = 0` and `l1_data_gas.max_price_per_unit = 0` while setting `l2_gas.max_price_per_unit` high enough to pass the L2 threshold check. This is a straightforward, unprivileged, single-transaction trigger. The gap is acknowledged in the codebase itself via the TODO comment, confirming it is a known incomplete check.

---

### Recommendation

Extend `validate_tx_l2_gas_price_within_threshold` (or create a parallel function) to also compare `tx_resource_bounds.l1_gas.max_price_per_unit` and `tx_resource_bounds.l1_data_gas.max_price_per_unit` against the previous block's `strk_gas_prices.l1_gas_price` and `strk_gas_prices.l1_data_gas_price` respectively, applying the same `min_gas_price_percentage` threshold logic already used for L2 gas.

The `validate_resource_bounds` function already fetches the full `BlockInfo` (which contains all three STRK gas prices); the fix requires reading the two additional price fields and adding the same threshold comparison for each. [5](#0-4) 

---

### Proof of Concept

1. Observe that `BlockInfo.gas_prices.strk_gas_prices` contains `l1_gas_price`, `l1_data_gas_price`, and `l2_gas_price`.
2. Submit an `AllResources` invoke transaction with:
   - `l2_gas.max_price_per_unit` = `previous_block_l2_gas_price` (passes the only gateway check)
   - `l1_gas.max_price_per_unit` = `0`
   - `l1_data_gas.max_price_per_unit` = `0`
3. The transaction passes `validate_resource_bounds` because only L2 gas price is checked.
4. The transaction is admitted to the mempool.
5. When the batcher executes it, `account_transaction.rs::check_fee_bounds` compares `l1_gas.max_price_per_unit (0)` against `block_info.gas_prices.l1_gas_price (non-zero)` and returns `ResourceBoundsError::MaxGasPriceTooLow { resource: L1Gas, ... }`, causing the transaction to fail with `TransactionFeeError::InsufficientResourceBounds`. [6](#0-5)

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

**File:** crates/blockifier/src/transaction/account_transaction.rs (L398-458)
```rust
                    ValidResourceBounds::AllResources(AllResourceBounds {
                        l1_gas: l1_gas_resource_bounds,
                        l2_gas: l2_gas_resource_bounds,
                        l1_data_gas: l1_data_gas_resource_bounds,
                    }) => {
                        let GasPriceVector { l1_gas_price, l1_data_gas_price, l2_gas_price } =
                            block_info.gas_prices.gas_price_vector(fee_type);
                        vec![
                            (
                                L1Gas,
                                l1_gas_resource_bounds,
                                minimal_gas_amount_vector.l1_gas,
                                *l1_gas_price,
                            ),
                            (
                                L1DataGas,
                                l1_data_gas_resource_bounds,
                                minimal_gas_amount_vector.l1_data_gas,
                                *l1_data_gas_price,
                            ),
                            (
                                L2Gas,
                                l2_gas_resource_bounds,
                                minimal_gas_amount_vector.l2_gas,
                                *l2_gas_price,
                            ),
                        ]
                    }
                };
                let insufficiencies = resources_amount_tuple
                    .iter()
                    .flat_map(
                        |(resource, resource_bounds, minimal_gas_amount, actual_gas_price)| {
                            let mut insufficiencies_resource = vec![];
                            if minimal_gas_amount > &resource_bounds.max_amount {
                                insufficiencies_resource.push(
                                    ResourceBoundsError::MaxGasAmountTooLow {
                                        resource: *resource,
                                        max_gas_amount: resource_bounds.max_amount,
                                        minimal_gas_amount: *minimal_gas_amount,
                                    },
                                );
                            }
                            if resource_bounds.max_price_per_unit < actual_gas_price.get() {
                                insufficiencies_resource.push(
                                    ResourceBoundsError::MaxGasPriceTooLow {
                                        resource: *resource,
                                        max_gas_price: resource_bounds.max_price_per_unit,
                                        actual_gas_price: (*actual_gas_price).into(),
                                    },
                                );
                            }
                            insufficiencies_resource
                        },
                    )
                    .collect::<Vec<_>>();
                if !insufficiencies.is_empty() {
                    return Err(Box::new(TransactionFeeError::InsufficientResourceBounds {
                        errors: insufficiencies,
                    }))?;
                }
```

**File:** crates/apollo_gateway/src/stateless_transaction_validator.rs (L56-88)
```rust
    fn validate_resource_bounds(
        &self,
        tx: &RpcTransaction,
    ) -> StatelessTransactionValidatorResult<()> {
        if !self.config.validate_resource_bounds {
            return Ok(());
        }

        let resource_bounds = *tx.resource_bounds();
        // The resource bounds should be positive even without the tip.
        if ValidResourceBounds::AllResources(resource_bounds).max_possible_fee(Tip::ZERO) == Fee(0)
        {
            return Err(StatelessTransactionValidatorError::ZeroResourceBounds { resource_bounds });
        }

        if resource_bounds.l2_gas.max_price_per_unit.0 < self.config.min_gas_price {
            return Err(StatelessTransactionValidatorError::MaxGasPriceTooLow {
                gas_price: resource_bounds.l2_gas.max_price_per_unit,
                min_gas_price: self.config.min_gas_price,
            });
        }

        // TODO(Arni): Consider adding a validation for max_l2_gas_amount for declare.
        if let RpcTransaction::Declare(_) = tx {
        } else if resource_bounds.l2_gas.max_amount.0 > self.config.max_l2_gas_amount {
            return Err(StatelessTransactionValidatorError::MaxGasAmountTooHigh {
                gas_amount: resource_bounds.l2_gas.max_amount,
                max_gas_amount: self.config.max_l2_gas_amount,
            });
        }

        Ok(())
    }
```
