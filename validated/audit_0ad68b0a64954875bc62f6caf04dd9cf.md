### Title
Asymmetric `max_l2_gas_amount` Guard Skips `Declare` Transactions, Allowing Unbounded L2 Gas Claims at Gateway Admission — (`crates/apollo_gateway/src/stateless_transaction_validator.rs`)

### Summary

`StatelessTransactionValidator::validate_resource_bounds` enforces an upper bound on `l2_gas.max_amount` for `Invoke` and `DeployAccount` transactions but explicitly skips the same check for `Declare` transactions. Any user can submit a `Declare` transaction with an arbitrarily large `l2_gas.max_amount` (up to `u64::MAX`) and have it accepted by the gateway, while an identical value in an `Invoke` or `DeployAccount` transaction is rejected with `MaxGasAmountTooHigh`.

### Finding Description

In `validate_resource_bounds` (lines 78–85 of `stateless_transaction_validator.rs`):

```rust
// TODO(Arni): Consider adding a validation for max_l2_gas_amount for declare.
if let RpcTransaction::Declare(_) = tx {
    // ← empty branch: no check performed
} else if resource_bounds.l2_gas.max_amount.0 > self.config.max_l2_gas_amount {
    return Err(StatelessTransactionValidatorError::MaxGasAmountTooHigh {
        gas_amount: resource_bounds.l2_gas.max_amount,
        max_gas_amount: self.config.max_l2_gas_amount,
    });
}
```

The production `max_l2_gas_amount` is `1,210,000,000` (from `gateway_config.json` and `StatelessTransactionValidatorConfig::default()`). The check is applied to `Invoke` and `DeployAccount` but the `Declare` branch is a deliberate no-op. The test `valid_l2_gas_amount_on_declare` (lines 173–201 of `stateless_transaction_validator_test.rs`) explicitly asserts that a `Declare` with `l2_gas.max_amount = 200` passes when `max_l2_gas_amount = 100`, confirming the asymmetry is load-bearing.

The downstream execution path uses `l2_gas.max_amount` directly as the initial Sierra gas budget (`initial_sierra_gas()` in `context.rs`, line 70: `l2_gas.max_amount`). A `Declare` transaction with `l2_gas.max_amount = u64::MAX` therefore enters the mempool and batcher with a declared gas budget of `u64::MAX`, bypassing the gateway's admission policy that exists precisely to prevent this.

The `min_gas_price` check (line 71) still applies to `Declare`, so `l2_gas.max_price_per_unit` must be ≥ `8,000,000,000`. With `l2_gas.max_amount` set to a value just above `max_l2_gas_amount` (e.g., `1,210,000,001`) and `l2_gas.max_price_per_unit = min_gas_price`, the product `1,210,000,001 × 8,000,000,000 ≈ 9.68 × 10^18` fits within `u64::MAX`, so `max_possible_fee` does not saturate and `verify_can_pay_committed_bounds` passes for a sufficiently funded account. The transaction then reaches the batcher with a declared L2 gas budget exceeding the per-transaction limit enforced on every other transaction type.

### Impact Explanation

This is a **High** impact gateway/mempool admission issue. The gateway's `max_l2_gas_amount` guard is the sequencer's first line of defence against transactions that claim more L2 gas than the block can accommodate (`sierra_gas` block cap = `5,000,000,000`; `receipt_l2_gas` cap = `5,800,000,000`). Bypassing it for `Declare` transactions means:

1. A `Declare` transaction with `l2_gas.max_amount` far exceeding the per-transaction limit is admitted by the gateway and enters the mempool.
2. `initial_sierra_gas()` returns the attacker-controlled value as the initial gas budget for execution, which is only capped later by OS-level constants (`execute_max_sierra_gas = 1,110,000,000`). The gap between the declared value and the OS cap is invisible to the admission layer.
3. The asymmetry violates the uniform admission policy: the same `l2_gas.max_amount` value is rejected for `Invoke`/`DeployAccount` but accepted for `Declare`, producing inconsistent gateway behaviour observable by any external caller.

### Likelihood Explanation

Trivially reachable. Any user can craft a `Declare` transaction with `l2_gas.max_amount = max_l2_gas_amount + 1` and a funded account. No privileged access, no special peer relationship, and no race condition is required. The gateway is a public HTTP endpoint.

### Recommendation

Apply the same `max_l2_gas_amount` upper-bound check to `Declare` transactions. Remove the empty `if let RpcTransaction::Declare(_) = tx {}` branch and let the existing `else if` apply uniformly:

```rust
if resource_bounds.l2_gas.max_amount.0 > self.config.max_l2_gas_amount {
    return Err(StatelessTransactionValidatorError::MaxGasAmountTooHigh {
        gas_amount: resource_bounds.l2_gas.max_amount,
        max_gas_amount: self.config.max_l2_gas_amount,
    });
}
```

Update `valid_l2_gas_amount_on_declare` to expect a rejection, and add `TransactionType::Declare` to the `#[values(...)]` list in `test_invalid_max_l2_gas_amount`.

### Proof of Concept

```rust
// In stateless_transaction_validator_test.rs
#[test]
fn poc_declare_bypasses_max_l2_gas_amount() {
    let config = StatelessTransactionValidatorConfig {
        validate_resource_bounds: true,
        max_l2_gas_amount: 100,          // limit = 100
        min_gas_price: 1,
        ..*DEFAULT_VALIDATOR_CONFIG_FOR_TESTING
    };
    let validator = StatelessTransactionValidator { config };

    // Invoke with amount=200 → correctly rejected
    let invoke_tx = rpc_tx_for_testing(TransactionType::Invoke, RpcTransactionArgs {
        resource_bounds: AllResourceBounds {
            l2_gas: ResourceBounds {
                max_amount: GasAmount(200),   // > max_l2_gas_amount
                max_price_per_unit: GasPrice(1),
            },
            ..Default::default()
        },
        ..Default::default()
    });
    assert!(validator.validate(&invoke_tx).is_err());   // MaxGasAmountTooHigh

    // Declare with amount=200 → incorrectly accepted
    let declare_tx = rpc_tx_for_testing(TransactionType::Declare, RpcTransactionArgs {
        resource_bounds: AllResourceBounds {
            l2_gas: ResourceBounds {
                max_amount: GasAmount(200),   // same value, same limit
                max_price_per_unit: GasPrice(1),
            },
            ..Default::default()
        },
        ..Default::default()
    });
    assert!(validator.validate(&declare_tx).is_ok());   // BUG: should be Err
}
```

This mirrors the existing `valid_l2_gas_amount_on_declare` test (lines 173–201) which already documents the asymmetry as passing behaviour. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6)

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

**File:** crates/apollo_gateway/src/stateless_transaction_validator_test.rs (L243-271)
```rust
#[rstest]
#[case::max_l2_gas_amount_too_high(
    RpcTransactionArgs {
        resource_bounds: AllResourceBounds {
            l2_gas: ResourceBounds {
                max_amount: GasAmount(DEFAULT_VALIDATOR_CONFIG.max_l2_gas_amount + 1),
                max_price_per_unit: GasPrice(DEFAULT_VALIDATOR_CONFIG.min_gas_price),
            },
            ..Default::default()
        },
        ..Default::default()
    },
    StatelessTransactionValidatorError::MaxGasAmountTooHigh {
        gas_amount: GasAmount(DEFAULT_VALIDATOR_CONFIG.max_l2_gas_amount + 1),
        max_gas_amount: DEFAULT_VALIDATOR_CONFIG.max_l2_gas_amount
    },
)]
fn test_invalid_max_l2_gas_amount(
    #[case] rpc_tx_args: RpcTransactionArgs,
    #[case] expected_error: StatelessTransactionValidatorError,
    #[values(TransactionType::DeployAccount, TransactionType::Invoke)] tx_type: TransactionType,
) {
    let tx_validator =
        StatelessTransactionValidator { config: DEFAULT_VALIDATOR_CONFIG.to_owned() };

    let tx = rpc_tx_for_testing(tx_type, rpc_tx_args);

    assert_eq!(tx_validator.validate(&tx).unwrap_err(), expected_error);
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

**File:** crates/apollo_deployments/resources/app_configs/gateway_config.json (L25-25)
```json
  "gateway_config.static_config.stateless_tx_validator_config.max_l2_gas_amount": 1210000000,
```

**File:** crates/blockifier/src/context.rs (L55-73)
```rust
    pub fn initial_sierra_gas(&self) -> GasAmount {
        match &self.tx_info {
            TransactionInfo::Deprecated(_)
            | TransactionInfo::Current(CurrentTransactionInfo {
                resource_bounds: ValidResourceBounds::L1Gas(_),
                ..
            }) => self.block_context.versioned_constants.initial_gas_no_user_l2_bound(),
            TransactionInfo::Current(CurrentTransactionInfo {
                resource_bounds: ValidResourceBounds::AllResources(AllResourceBounds { l2_gas, .. }),
                ..
            }) => {
                #[cfg(feature = "reexecution")]
                if self.block_context.versioned_constants.ignore_user_l2_gas_bound {
                    return self.block_context.versioned_constants.initial_gas_no_user_l2_bound();
                }
                l2_gas.max_amount
            }
        }
    }
```
