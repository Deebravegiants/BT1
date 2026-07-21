### Title
Unbounded L2 Gas Amount Admitted for Declare Transactions via Missing `max_l2_gas_amount` Check — (`File: crates/apollo_gateway/src/stateless_transaction_validator.rs`)

### Summary

The `StatelessTransactionValidator` enforces a `max_l2_gas_amount` cap on L2 gas resource bounds for Invoke and DeployAccount transactions, but explicitly skips this check for Declare transactions. A user can submit a `RpcDeclareTransaction::V3` with `l2_gas.max_amount = u64::MAX` (18,446,744,073,709,551,615), which is ~15× the configured gateway limit of 1,210,000,000, and the transaction will pass all stateless validation and be admitted to the mempool.

### Finding Description

In `validate_resource_bounds`, the check for `max_l2_gas_amount` is guarded by an explicit early-return for Declare transactions:

```rust
// TODO(Arni): Consider adding a validation for max_l2_gas_amount for declare.
if let RpcTransaction::Declare(_) = tx {
} else if resource_bounds.l2_gas.max_amount.0 > self.config.max_l2_gas_amount {
    return Err(StatelessTransactionValidatorError::MaxGasAmountTooHigh { ... });
}
``` [1](#0-0) 

The `max_l2_gas_amount` is defined in `StatelessTransactionValidatorConfig` with a default of `1_210_000_000` and is deployed at that value in production: [2](#0-1) [3](#0-2) 

The TODO comment `// TODO(Arni): Consider adding a validation for max_l2_gas_amount for declare.` confirms this is an acknowledged gap, not an intentional design decision.

The `validate_resource_bounds` function is called unconditionally for all transaction types in the top-level `validate` method: [4](#0-3) 

The test suite explicitly documents and confirms this bypass — `valid_l2_gas_amount_on_declare` asserts that a Declare transaction with `l2_gas.max_amount = 200` passes even when `max_l2_gas_amount = 100`: [5](#0-4) 

### Impact Explanation

**Impact: High — Mempool/gateway admission accepts invalid transactions before sequencing.**

A Declare transaction with `l2_gas.max_amount = u64::MAX` passes the stateless validator and is admitted to the mempool. This is the exact analog of the external bug: a defined maximum (`max_l2_gas_amount = 1_210_000_000`) is bypassed in favor of an unbounded value for one transaction type.

Downstream effects:
- The admitted transaction carries `l2_gas.max_amount = u64::MAX`. During execution, `max_steps` in `EntryPointExecutionContext` is derived from this value via `max_amount.0.saturating_div(l2_gas_per_step)`, yielding a near-`u64::MAX` step count before being clamped to the block upper bound. [6](#0-5) 
- The fee check at post-execution compares actual gas used against `u64::MAX`, so the transaction never fails the gas-overdraft check regardless of actual consumption. [7](#0-6) 
- Mempool ordering and bouncer accounting treat the declared `max_amount` as the transaction's resource claim. Transactions with `u64::MAX` declared L2 gas can distort admission decisions for subsequent transactions.

### Likelihood Explanation

**Likelihood: High.** The bypass requires only a well-formed `RpcDeclareTransaction::V3` with an oversized `l2_gas.max_amount`. No privileged access, special keys, or network position is required. The TODO comment confirms the gap is known and unresolved. Any user interacting with the public gateway endpoint can trigger this.

### Recommendation

Remove the Declare-specific exemption and apply the same `max_l2_gas_amount` bound to all transaction types:

```rust
if resource_bounds.l2_gas.max_amount.0 > self.config.max_l2_gas_amount {
    return Err(StatelessTransactionValidatorError::MaxGasAmountTooHigh {
        gas_amount: resource_bounds.l2_gas.max_amount,
        max_gas_amount: self.config.max_l2_gas_amount,
    });
}
``` [1](#0-0) 

If Declare transactions legitimately require a higher L2 gas ceiling (e.g., for large Sierra programs), introduce a separate `max_l2_gas_amount_declare` config field with an explicit, bounded value rather than leaving the check absent entirely.

### Proof of Concept

1. Construct a valid `RpcDeclareTransaction::V3` with:
   - `resource_bounds.l2_gas.max_amount = GasAmount(u64::MAX)`
   - `resource_bounds.l2_gas.max_price_per_unit = GasPrice(min_gas_price)` (e.g., `8_000_000_000`)
   - All other fields valid (valid Sierra class, sorted entry points, etc.)
2. Submit to the gateway's `add_declare_transaction` endpoint.
3. Observe: `StatelessTransactionValidator::validate` returns `Ok(())` — the `MaxGasAmountTooHigh` error is never raised because the Declare branch short-circuits the check at line 79.
4. The transaction enters the mempool with `l2_gas.max_amount = u64::MAX`, bypassing the 1,210,000,000 limit enforced for all other transaction types. [8](#0-7)

### Citations

**File:** crates/apollo_gateway/src/stateless_transaction_validator.rs (L33-54)
```rust
    pub fn validate(&self, tx: &RpcTransaction) -> StatelessTransactionValidatorResult<()> {
        // TODO(Arni, 1/5/2024): Add a mechanism that validate the sender address is not blocked.
        // TODO(Arni, 1/5/2024): Validate transaction version.

        Self::validate_contract_address(tx)?;
        Self::validate_empty_account_deployment_data(tx)?;
        Self::validate_empty_paymaster_data(tx)?;
        self.validate_resource_bounds(tx)?;
        self.validate_tx_size(tx)?;
        self.validate_nonce_data_availability_mode(tx)?;
        self.validate_fee_data_availability_mode(tx)?;

        if let RpcTransaction::Invoke(invoke_tx) = tx {
            self.validate_client_side_proving_allowed(invoke_tx)?;
            self.validate_proof_facts_and_proof_consistency(invoke_tx)?;
        }

        if let RpcTransaction::Declare(declare_tx) = tx {
            self.validate_declare_tx(declare_tx)?;
        }
        Ok(())
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

**File:** crates/blockifier/src/fee/fee_checks.rs (L128-149)
```rust
    pub fn check_all_gas_amounts_within_bounds(
        max_amount_bounds: &GasVector,
        gas_vector: &GasVector,
    ) -> FeeCheckResult<()> {
        // TODO(Arni): Consider refactoring the returned error. The first failed check will hide
        // future checks.
        for (resource, max_amount, actual_amount) in [
            (L1Gas, max_amount_bounds.l1_gas, gas_vector.l1_gas),
            (L2Gas, max_amount_bounds.l2_gas, gas_vector.l2_gas),
            (L1DataGas, max_amount_bounds.l1_data_gas, gas_vector.l1_data_gas),
        ] {
            if max_amount < actual_amount {
                return Err(FeeCheckError::MaxGasAmountExceeded {
                    resource,
                    max_amount,
                    actual_amount,
                });
            }
        }

        Ok(())
    }
```
