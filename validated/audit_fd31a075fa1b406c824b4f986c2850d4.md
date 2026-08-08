Confirmed root cause: `runtime_config.compute_budget` is a validator-configured, static `ComputeBudget` (typically set at node startup / via `RuntimeConfig`, e.g. by test/tooling harnesses that pass `Some(ComputeBudget)`), which is a *separate* copy of compute limit state from the per-transaction `ComputeBudgetInstructionDetails` derived from the transaction's own `ComputeBudgetInstruction::set_compute_unit_limit`/`set_loaded_accounts_data_size_limit` instructions. In `Bank::check_age_and_compute_budget_limits`, when `self.compute_budget` (i.e. `Bank.compute_budget: Option<ComputeBudget>`) is `Some`, the code discards the transaction-derived `compute_unit_limit`/`heap_size` entirely and substitutes the Bank-wide static `ComputeBudget.compute_unit_limit`/`heap_size` instead via `ComputeBudget::get_compute_budget_and_limits`, only threading through `loaded_accounts_data_size_limit` and `fee_details` from the real per-tx config. [1](#0-0) [2](#0-1) [3](#0-2) 

The comment in the code itself flags this as legacy/duplicated state that should be removed: [4](#0-3) 

### Title
Bank-configured `compute_budget` override silently replaces per-transaction compute unit limit, enabling underpriced/overpriced execution divergence - (File: runtime/src/bank/check_transactions.rs)

### Summary
`Bank::check_age_and_compute_budget_limits` maintains two independent sources of truth for a transaction's compute unit limit and heap size: (1) the transaction's own `ComputeBudgetInstruction` (`set_compute_unit_limit`, `request_heap_frame`, etc.), parsed into `ComputeBudgetInstructionDetails`/`TransactionConfiguration`, and (2) an optional static `Bank.compute_budget: Option<ComputeBudget>` sourced from `RuntimeConfig.compute_budget`. When the static override is present, the code unconditionally substitutes its `compute_unit_limit`/`heap_size` for whatever the transaction actually requested, while still computing `fee_details` from the transaction's real `compute_unit_price`/`compute_unit_limit`. This is structurally identical to the reported DInterest bug class: two logically-linked pieces of state (`moneyMarket` vs `interestOracle.moneyMarket()`) that must agree but are never cross-validated, so one can silently diverge from the other and corrupt a value/pricing calculation.

### Finding Description
`check_age_and_compute_budget_limits` builds `CheckedTransactionDetails.compute_budget_and_limits` from the transaction's parsed `TransactionConfiguration` (via `tx.transaction_configuration(feature_set)`), which reflects the actual `ComputeBudgetInstruction`s included by the user. Fee details are computed from this same, faithful per-tx configuration: [5](#0-4) 

However, if `self.compute_budget` is `Some(..)` (a Bank-wide static override coming from `RuntimeConfig::compute_budget`, itself just an `Option<ComputeBudget>` with no linkage back to per-transaction instructions), the code branches to `compute_budget.get_compute_budget_and_limits(...)`, which builds the final `SVMTransactionExecutionAndFeeBudgetLimits.budget` purely from the static `ComputeBudget`'s own `compute_unit_limit`/`heap_size` fields — completely ignoring the transaction-requested `config.compute_unit_limit`/`config.updated_heap_bytes` for the *execution budget*, even though `fee_details` (computed just above) was priced using the transaction's real request: [6](#0-5) [2](#0-1) 

This is the same "duplicated state, unvalidated at construction" bug class as the DInterest report: the Bank never asserts that `self.compute_budget`'s `compute_unit_limit`/`heap_size` is consistent with (or derived from) the transaction's own compute-budget instructions before using it to override the SVM execution budget. Whenever the override differs from the transaction's actual request, the runtime enforces a compute-unit ceiling that is disconnected from what the payer priced/paid for.

### Impact Explanation
If the static override's `compute_unit_limit` is *higher* than what the transaction requested and paid compute-unit-price fees for, the runtime under-prices execution: the transaction gets to consume/execute against a larger compute budget than the fee it paid corresponds to, which is materially underpriced execution relative to the fee/cost model that assumes execution cost tracks the requested (and paid-for) compute unit limit. Conversely, if the override is *lower*, correctly-priced transactions can be forced to fail with `ComputationalBudgetExceeded` despite having paid for a larger, valid limit. Both cases break the invariant that fee_details and the enforced execution budget derive from the same requested limit, which the cost model, cost tracker, and block cost accounting all assume hold together (see `cost-model/src/cost_model.rs` which computes execution cost strictly from the transaction's own requested `compute_unit_limit`). [7](#0-6) 

### Likelihood Explanation
Reachability is gated on `Bank.compute_budget` (populated from `RuntimeConfig.compute_budget`) being `Some`. This is not something an ordinary transaction sender controls; it is validator/runtime configuration. This significantly limits it as an "unprivileged-user-reachable" issue: the divergence is only exercised when an operator (or test/tooling harness) configures a non-default `RuntimeConfig::compute_budget`, which the code comments themselves describe as "legacy behavior... retained" and slated for removal. Without a code path where an unprivileged user can set or influence `self.compute_budget`, this issue is primarily an internal/operator-configuration inconsistency, not a directly user-triggerable value-loss bug in the sense required by the validation rubric (concrete, unprivileged-reachable, non-config-only impact).

### Recommendation
Remove the legacy `self.compute_budget` override path in `check_age_and_compute_budget_limits`/`Bank`, always deriving the execution budget's `compute_unit_limit` and `heap_size` from the transaction's own parsed `TransactionConfiguration`/`ComputeBudgetInstructionDetails`, exactly as `fee_details` already does. If backward compatibility with `RuntimeConfig::compute_budget` for non-limit fields (e.g., cost tables) is still required, restrict the override to fields that are not derived from user-supplied compute-budget instructions, and assert/validate that any residual override cannot diverge from the fee calculation basis.

### Proof of Concept
Not applicable as a directly unprivileged-user-exploitable PoC: reproducing the divergence requires configuring the validator's `RuntimeConfig::compute_budget` (an operator/test-harness action) to a `ComputeBudget` whose `compute_unit_limit`/`heap_size` differs from a submitted transaction's own `ComputeBudgetInstruction::set_compute_unit_limit`/`request_heap_frame` values, then observing that `check_age_and_compute_budget_limits` returns `SVMTransactionExecutionAndFeeBudgetLimits.budget.compute_unit_limit` equal to the configured override rather than the transaction's requested limit, while `fee_details` is still computed from the transaction's requested limit/price: [8](#0-7)

### Citations

**File:** runtime/src/bank/check_transactions.rs (L171-207)
```rust
                Ok(()) => {
                    let compute_budget_and_limits = tx
                        .borrow()
                        .transaction_configuration(feature_set)
                        .map(|config| {
                            let fee_details = calculate_fee_details(
                                tx.borrow(),
                                self.fee_structure.lamports_per_signature,
                                config.priority_fee_lamports,
                                fee_features,
                            );
                            if let Some(compute_budget) = self.compute_budget {
                                // This block of code is only necessary to retain legacy behavior of the code.
                                // It should be removed along with the change to favor transaction's compute budget limits
                                // over configured compute budget in Bank.
                                compute_budget.get_compute_budget_and_limits(
                                    config.loaded_accounts_data_size_limit,
                                    fee_details,
                                )
                            } else {
                                SVMTransactionExecutionAndFeeBudgetLimits {
                                    budget: SVMTransactionExecutionBudget {
                                        compute_unit_limit: u64::from(config.compute_unit_limit),
                                        heap_size: config.updated_heap_bytes,
                                        ..SVMTransactionExecutionBudget::new_with_defaults(
                                            raise_cpi_limit,
                                        )
                                    },
                                    loaded_accounts_data_size_limit: config
                                        .loaded_accounts_data_size_limit,
                                    fee_details,
                                }
                            }
                        })
                        .inspect_err(|_err| {
                            error_counters.invalid_compute_budget += 1;
                        })?;
```

**File:** compute-budget/src/compute_budget.rs (L306-316)
```rust
    pub fn get_compute_budget_and_limits(
        &self,
        loaded_accounts_data_size_limit: u32,
        fee_details: FeeDetails,
    ) -> SVMTransactionExecutionAndFeeBudgetLimits {
        SVMTransactionExecutionAndFeeBudgetLimits {
            budget: self.to_budget(),
            loaded_accounts_data_size_limit,
            fee_details,
        }
    }
```

**File:** runtime/src/runtime_config.rs (L1-12)
```rust
use solana_compute_budget::compute_budget::ComputeBudget;

/// Encapsulates flags that can be used to tweak the runtime behavior.
#[derive(Debug, Default, Clone)]
pub struct RuntimeConfig {
    pub compute_budget: Option<ComputeBudget>,
    pub log_messages_bytes_limit: Option<usize>,
    pub transaction_account_lock_limit: Option<usize>,
    /// When true, skip storing transaction signature keys in the status cache.
    /// Message hash keys are still stored for duplicate transaction detection.
    pub skip_transaction_signatures_in_status_cache: bool,
}
```

**File:** cost-model/src/cost_model.rs (L159-178)
```rust
    fn get_estimated_execution_cost(
        transaction: &impl TransactionMeta,
        feature_set: &FeatureSet,
    ) -> (u64, u64) {
        // if failed to process compute_budget instructions, the transaction will not be executed
        // by `bank`, therefore it should be considered as no execution cost by cost model.
        let (programs_execution_costs, loaded_accounts_data_size_cost) =
            match transaction.transaction_configuration(feature_set) {
                Ok(config) => (
                    u64::from(config.compute_unit_limit),
                    Self::calculate_loaded_accounts_data_size_cost(
                        config.loaded_accounts_data_size_limit,
                        feature_set,
                    ),
                ),
                Err(_) => (0, 0),
            };

        (programs_execution_costs, loaded_accounts_data_size_cost)
    }
```
