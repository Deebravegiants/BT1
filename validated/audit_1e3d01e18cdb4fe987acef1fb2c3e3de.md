### Title
Gateway Admission Skips `max_l2_gas_amount` Bound for Declare Transactions, Allowing Unbounded L2 Gas Claims — (`File: crates/apollo_gateway/src/stateless_transaction_validator.rs`)

---

### Summary

The `StatelessTransactionValidator` enforces a `max_l2_gas_amount` ceiling on `l2_gas.max_amount` for Invoke and DeployAccount transactions, but **explicitly skips this check for Declare transactions**. Any user can submit a Declare transaction claiming `l2_gas.max_amount = u64::MAX`, bypassing the gateway's admission control. The gateway admits the transaction, the mempool queues it, and during execution the blockifier grants it an initial gas budget derived from the unchecked `max_amount` — up to the full block capacity — rather than the per-transaction ceiling the check was designed to enforce.

---

### Finding Description

In `validate_resource_bounds`, the check reads:

```rust
// TODO(Arni): Consider adding a validation for max_l2_gas_amount for declare.
if let RpcTransaction::Declare(_) = tx {
} else if resource_bounds.l2_gas.max_amount.0 > self.config.max_l2_gas_amount {
    return Err(StatelessTransactionValidatorError::MaxGasAmountTooHigh { ... });
}
``` [1](#0-0) 

The default `max_l2_gas_amount` is `1_210_000_000`: [2](#0-1) 

The block's `receipt_l2_gas` bouncer ceiling is `5_800_000_000`, which must stay in sync with `orchestrator_versioned_constants`' `max_block_size`: [3](#0-2) [4](#0-3) 

The `max_l2_gas_amount` check exists to prevent any single transaction from claiming more gas than a block can hold. For Invoke/DeployAccount, the ceiling is `1_210_000_000` (~20 % of block capacity). For Declare, there is **no ceiling at all**.

The stateful validator only checks that `l2_gas.max_price_per_unit` meets a minimum price threshold; it does not check whether `max_amount` is within the block capacity: [5](#0-4) 

The blockifier's `max_steps` computation derives the per-transaction step limit from `max_amount`: [6](#0-5) 

So a Declare transaction with `l2_gas.max_amount = 5_800_000_000` (or `u64::MAX`) is admitted by the gateway, queued in the mempool, and executed with an initial gas budget equal to the full block capacity rather than the `1_210_000_000` ceiling that applies to every other transaction type.

The test `valid_l2_gas_amount_on_declare` confirms this is the current (unguarded) behavior: [7](#0-6) 

---

### Impact Explanation

The `max_l2_gas_amount` admission check is the gateway's primary defense against transactions that claim more gas than a block can accommodate. Skipping it for Declare transactions means:

1. **Invalid transactions are admitted**: A Declare with `l2_gas.max_amount = u64::MAX` passes every gateway check and enters the mempool, violating the invariant that admitted transactions must satisfy `max_amount ≤ max_l2_gas_amount`.
2. **Execution receives an inflated gas budget**: The blockifier grants the transaction an initial gas equal to `min(max_amount, block_upper_bound)`. With `max_amount = 5_800_000_000`, the transaction receives the full block gas budget instead of the intended per-transaction ceiling.
3. **Block capacity can be monopolized**: If the Declare contract is large enough to consume gas up to the bouncer's `receipt_l2_gas` limit, a single Declare transaction can fill the entire block, starving all other pending transactions.

This matches the **High** impact: *Mempool/gateway/RPC admission accepts invalid transactions before sequencing.*

---

### Likelihood Explanation

The bypass requires no privilege. Any user can craft a Declare transaction with an arbitrarily large `l2_gas.max_amount`. The code path is unconditional — the `if let RpcTransaction::Declare(_) = tx {}` branch is always taken for Declare transactions, and the TODO comment confirms the gap is known but unresolved.

---

### Recommendation

Apply the same `max_l2_gas_amount` upper-bound check to Declare transactions. Remove the `if let RpcTransaction::Declare(_) = tx {}` early-return branch and resolve the TODO:

```rust
if resource_bounds.l2_gas.max_amount.0 > self.config.max_l2_gas_amount {
    return Err(StatelessTransactionValidatorError::MaxGasAmountTooHigh {
        gas_amount: resource_bounds.l2_gas.max_amount,
        max_gas_amount: self.config.max_l2_gas_amount,
    });
}
```

If Declare transactions legitimately require a higher ceiling (e.g., for large Sierra programs), introduce a separate `max_l2_gas_amount_declare` configuration parameter rather than removing the check entirely.

---

### Proof of Concept

1. Construct a valid `RpcDeclareTransactionV3` with:
   - `resource_bounds.l2_gas.max_amount = GasAmount(5_800_000_000)` (full block capacity)
   - `resource_bounds.l2_gas.max_price_per_unit = GasPrice(8_000_000_000)` (≥ `min_gas_price`)
   - Any valid Sierra class body within the `max_contract_bytecode_size` limit.
2. Submit to the gateway's `add_transaction` endpoint.
3. **Expected (correct) behavior**: rejected with `MaxGasAmountTooHigh { gas_amount: 5_800_000_000, max_gas_amount: 1_210_000_000 }`.
4. **Actual behavior**: the `validate_resource_bounds` function hits the `if let RpcTransaction::Declare(_) = tx {}` branch and returns `Ok(())`. The transaction passes all gateway checks and is admitted to the mempool.
5. When the batcher picks up the transaction, `max_steps` is computed from `max_amount = 5_800_000_000`, granting the transaction the full block gas budget. The bouncer caps actual gas consumed at the block limit, but the transaction has been incorrectly admitted and may consume resources up to the full block capacity. [8](#0-7) [9](#0-8)

### Citations

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

**File:** crates/apollo_gateway_config/src/config.rs (L188-204)
```rust
impl Default for StatelessTransactionValidatorConfig {
    fn default() -> Self {
        StatelessTransactionValidatorConfig {
            validate_resource_bounds: true,
            min_gas_price: 8_000_000_000,
            max_l2_gas_amount: 1_210_000_000,
            max_calldata_length: 5000,
            max_signature_length: 4000,
            max_contract_bytecode_size: 81920,
            max_contract_class_object_size: 4089446,
            min_sierra_version: VersionId::new(1, 1, 0),
            max_sierra_version: VersionId::new(1, 9, usize::MAX),
            allow_client_side_proving: true,
            max_proof_size: 480000,
        }
    }
}
```

**File:** crates/blockifier/src/bouncer.rs (L163-168)
```rust
    /// Receipt-based L2 gas, including execution gas + state allocation costs + DA costs.
    /// Used to close blocks on the economic gas metric. Diverges from sierra_gas because
    /// it includes allocation_cost for new storage keys and other non-execution costs.
    // NOTE: Must stay in sync with orchestrator_versioned_constants' max_block_size.
    pub receipt_l2_gas: GasAmount,
}
```

**File:** crates/apollo_versioned_constants/resources/orchestrator_versioned_constants_0_14_2.json (L1-9)
```json
{
    "fee_proposal_margin_ppt": 2,
    "fee_proposal_window_size": 10,
    "gas_price_max_change_denominator": 48,
    "gas_target": 1500000000,
    "max_block_size": 5800000000,
    "min_gas_price": "0x1dcd65000",
    "l1_gas_price_margin_percent": 10
}
```

**File:** crates/apollo_gateway/src/stateful_transaction_validator_test.rs (L288-327)
```rust
async fn validate_resource_bounds(
    #[case] prev_l2_gas_price: NonzeroGasPrice,
    #[case] min_gas_price_percentage: u8,
    #[case] tx_gas_price_per_unit: GasPrice,
    #[case] expected_result: Result<(), StarknetError>,
) {
    let resource_bounds = ValidResourceBounds::AllResources(AllResourceBounds {
        l2_gas: ResourceBounds { max_price_per_unit: tx_gas_price_per_unit, ..Default::default() },
        ..Default::default()
    });
    let executable_tx = executable_invoke_tx(invoke_tx_args!(resource_bounds));

    let mut mock_gateway_fixed_block = MockGatewayFixedBlockStateReader::new();
    mock_gateway_fixed_block.expect_get_block_info().return_once(move || {
        Ok(BlockInfo {
            gas_prices: GasPrices {
                strk_gas_prices: GasPriceVector {
                    l2_gas_price: prev_l2_gas_price,
                    ..Default::default()
                },
                ..Default::default()
            },
            ..Default::default()
        })
    });

    let stateful_validator: StatefulTransactionValidator<TestStateReader, _> =
        StatefulTransactionValidator {
            config: StatefulTransactionValidatorConfig {
                validate_resource_bounds: true,
                min_gas_price_percentage,
                ..Default::default()
            },
            chain_info: ChainInfo::create_for_testing(),
            state_reader_and_contract_manager: None,
            gateway_fixed_block_state_reader: mock_gateway_fixed_block,
        };

    let result = stateful_validator.validate_resource_bounds(&executable_tx).await;
    assert_eq!(result, expected_result);
```

**File:** crates/blockifier/src/execution/entry_point.rs (L451-461)
```rust
                ValidResourceBounds::AllResources(AllResourceBounds {
                    l2_gas: ResourceBounds { max_amount, .. },
                    ..
                }) => {
                    if l2_gas_per_step.is_zero() {
                        u64::MAX
                    } else {
                        max_amount.0.saturating_div(l2_gas_per_step)
                    }
                }
            },
```

**File:** crates/apollo_gateway/src/stateless_transaction_validator_test.rs (L173-201)
```rust
#[rstest]
#[case::l2_gas_amount_out_of_limit(
    StatelessTransactionValidatorConfig {
        validate_resource_bounds: true,
        max_l2_gas_amount: 100,
        ..*DEFAULT_VALIDATOR_CONFIG_FOR_TESTING
    },
    RpcTransactionArgs {
        resource_bounds: AllResourceBounds {
            l2_gas: ResourceBounds {
                max_amount: GasAmount(200),
                ..NON_EMPTY_RESOURCE_BOUNDS
            },
            ..Default::default()
        },
        ..Default::default()
    }
)]
fn valid_l2_gas_amount_on_declare(
    #[case] config: StatelessTransactionValidatorConfig,
    #[case] rpc_tx_args: RpcTransactionArgs,
) {
    let tx_type = TransactionType::Declare;
    let tx_validator = StatelessTransactionValidator { config };

    let tx = rpc_tx_for_testing(tx_type, rpc_tx_args);

    assert_matches!(tx_validator.validate(&tx), Ok(()));
}
```
