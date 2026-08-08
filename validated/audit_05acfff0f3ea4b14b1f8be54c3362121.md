### Title
V1 transaction message format bypasses `InvalidLoadedAccountsDataSizeLimit` and default compute-unit-limit safety checks enforced on Legacy/V0 transactions - ([File: runtime-transaction/src/transaction_meta.rs])

### Summary
`VersionedTransactionConfiguration::try_into_config` computes the same logical `TransactionConfiguration` (heap size, compute unit limit, priority fee, loaded-accounts-data-size limit) via two different code paths depending on message version. For Legacy/V0 messages, the path goes through `ComputeBudgetInstructionDetails::sanitize_and_convert_to_compute_budget_limits`, which explicitly rejects a `loaded_accounts_data_size_limit` of `0` with `TransactionError::InvalidLoadedAccountsDataSizeLimit` [1](#0-0) . For V1 messages, the same field is instead taken directly from `TransactionConfig` and only clamped with `.min(MAX_LOADED_ACCOUNTS_DATA_SIZE_BYTES.get())`, with no rejection of `0` [2](#0-1) . When the field is unset it even defaults to `0` via `config.loaded_accounts_data_size_limit.unwrap_or(0)` [3](#0-2) .

### Finding Description
This mirrors the reported 0x bug class: one enforcement path (`MixinParams.setParams`) let a privileged caller set values that a different, "proper" path (`StakingProxy`'s init/attach flow) would have rejected as invalid. Here, two internal code paths compute the same transaction configuration value, but only one of them enforces the "must be non-zero" invariant on `loaded_accounts_data_size_limit`:

- Legacy/V0 path (`Self::LegacyAndV0` branch): explicit `NonZeroU32::new(...).ok_or(TransactionError::InvalidLoadedAccountsDataSizeLimit)?` [1](#0-0) .
- V1 path (`Self::V1` branch): only clamps to the max, with no zero-check, before returning `loaded_accounts_data_size_limit` as a plain `u32` [4](#0-3) .

The `TransactionConfiguration` struct stores this as a plain `u32` (not `NonZeroU32`) [5](#0-4) , so nothing at the type level prevents a `0` from flowing downstream. That value becomes the `requested_loaded_accounts_data_size_limit` used by `LoadedTransactionDataSize::with_max_size`, which fails any account loading the instant any data is counted (`self.loaded_accounts_data_size > self.requested_loaded_accounts_data_size_limit`) [6](#0-5) . A V1 message omitting the loaded-accounts-data-size config (or explicitly setting it to `0`) therefore reaches account loading with a `0` limit instead of being rejected up front with `InvalidLoadedAccountsDataSizeLimit`, unlike an equivalent Legacy/V0 transaction.

Additionally, `compute_unit_limit` similarly defaults to `0` in the V1 path via `unwrap_or(0)` [3](#0-2) , whereas the Legacy/V0 path computes a meaningful default via `calculate_default_compute_unit_limit` based on instruction count when unset [7](#0-6) .

### Impact Explanation
This is a validation/consistency bug reachable by any unprivileged transaction sender using the (message-format-gated) V1 transaction type: instead of being cleanly rejected before fee charging/account loading (as Legacy/V0 transactions are, via `InvalidLoadedAccountsDataSizeLimit`), a V1 transaction with a `0` loaded-accounts-data-size limit proceeds further into the pipeline and fails later (at account-load time) with `MaxLoadedAccountsDataSizeExceeded` once the very first account/lookup-table byte is counted. This changes transaction classification/error semantics between otherwise-equivalent transaction versions and can affect fee-only vs. full-processing outcomes, cost-model accounting, and downstream client/tooling expectations that rely on `InvalidLoadedAccountsDataSizeLimit` being surfaced pre-execution for a `0` limit. It does not appear to allow unbounded loading (the `0` limit is *more* restrictive, not less), so the concrete value-loss/creation/double-settlement impact is limited; the primary issue is inconsistent enforcement between two supposedly-equivalent instruction-configuration paths, an early-detection/error-surfacing bypass rather than a resource-limit bypass.

### Likelihood Explanation
Reachable by any unprivileged user able to construct a V1 transaction (this message format's mainnet availability/feature-gating could not be fully confirmed from the index — see below), simply by omitting/zeroing `loaded_accounts_data_size_limit` in `TransactionConfig`. No special privileges are required; it only requires forming a V1 message, which is a standard (if newer) transaction-construction path in this codebase.

### Recommendation
Make the V1 branch of `VersionedTransactionConfiguration::try_into_config` enforce the same non-zero requirement on `loaded_accounts_data_size_limit` as the Legacy/V0 branch (e.g., return `TransactionError::InvalidLoadedAccountsDataSizeLimit` when the value is `0`), and consider using `NonZeroU32` for `TransactionConfiguration::loaded_accounts_data_size_limit` so the invariant is enforced at the type level for both paths, exactly as recommended in the analog report ("ensure calls... check that the provided values are within the same range currently enforced").

### Proof of Concept
1. Construct a `SanitizedMessage::V1` transaction with `TransactionConfig { loaded_accounts_data_size_limit: None, .. }` (or explicitly `Some(0)`).
2. Call `TransactionConfiguration::try_from_sanitized_message` → `VersionedTransactionConfiguration::try_into_config`.
3. Observe the `Self::V1` branch returns `Ok(TransactionConfiguration { loaded_accounts_data_size_limit: 0, .. })` instead of `Err(TransactionError::InvalidLoadedAccountsDataSizeLimit)`, as demonstrated by the existing unit test `test_try_into_config_v1_no_clamping`/`test_try_into_config_v1_clamps_loaded_accounts_data_size_limit`, which show no zero-rejection path exists for `Self::V1` [8](#0-7) , contrasted with the `LegacyAndV0` behavior enforced in `compute_budget_instruction_details.rs` (`Err(TransactionError::InvalidLoadedAccountsDataSizeLimit)` on zero) [9](#0-8) .

*Note: I could not fully verify from the available index whether the V1 message/`TransactionConfig` format is currently activated/reachable on mainnet-beta or gated behind a not-yet-active feature; this affects the immediate exploitability/likelihood assessment and would need confirmation via a full checkout (e.g., searching for the feature gate controlling `SanitizedMessage::V1` acceptance) in a Devin session with complete repository access.*

### Citations

**File:** compute-budget-instruction/src/compute_budget_instruction_details.rs (L121-128)
```rust
        // Calculate compute unit limit
        let compute_unit_limit = self
            .requested_compute_unit_limit
            .map_or_else(
                || self.calculate_default_compute_unit_limit(feature_set),
                |(_index, requested_compute_unit_limit)| requested_compute_unit_limit,
            )
            .min(MAX_COMPUTE_UNIT_LIMIT);
```

**File:** compute-budget-instruction/src/compute_budget_instruction_details.rs (L136-145)
```rust
        let loaded_accounts_bytes =
            if let Some((_index, requested_loaded_accounts_data_size_limit)) =
                self.requested_loaded_accounts_data_size_limit
            {
                NonZeroU32::new(requested_loaded_accounts_data_size_limit)
                    .ok_or(TransactionError::InvalidLoadedAccountsDataSizeLimit)?
            } else {
                MAX_LOADED_ACCOUNTS_DATA_SIZE_BYTES
            }
            .min(MAX_LOADED_ACCOUNTS_DATA_SIZE_BYTES);
```

**File:** compute-budget-instruction/src/compute_budget_instruction_details.rs (L481-492)
```rust
        // invalid: loaded_account_data_size can't be zero
        let instruction_details = ComputeBudgetInstructionDetails {
            requested_compute_unit_limit: Some((1, 0)),
            requested_compute_unit_price: Some((2, 0)),
            requested_heap_size: Some((3, 40 * 1024)),
            requested_loaded_accounts_data_size_limit: Some((4, 0)),
            ..ComputeBudgetInstructionDetails::default()
        };
        assert_eq!(
            instruction_details.sanitize_and_convert_to_compute_budget_limits(&feature_set),
            Err(TransactionError::InvalidLoadedAccountsDataSizeLimit)
        );
```

**File:** runtime-transaction/src/transaction_meta.rs (L55-60)
```rust
pub struct TransactionConfiguration {
    pub updated_heap_bytes: u32,
    pub compute_unit_limit: u32,
    pub priority_fee_lamports: u64,
    pub loaded_accounts_data_size_limit: u32,
}
```

**File:** runtime-transaction/src/transaction_meta.rs (L122-129)
```rust
    fn from_v1_config(config: &TransactionConfig) -> Self {
        Self::V1(TransactionConfiguration {
            priority_fee_lamports: config.priority_fee.unwrap_or(0),
            compute_unit_limit: config.compute_unit_limit.unwrap_or(0),
            loaded_accounts_data_size_limit: config.loaded_accounts_data_size_limit.unwrap_or(0),
            updated_heap_bytes: config.heap_size.unwrap_or(HEAP_LENGTH as u32),
        })
    }
```

**File:** runtime-transaction/src/transaction_meta.rs (L156-176)
```rust
            Self::V1(transaction_configuration) => {
                if !(MIN_HEAP_FRAME_BYTES..=MAX_HEAP_FRAME_BYTES)
                    .contains(&transaction_configuration.updated_heap_bytes)
                    || !transaction_configuration
                        .updated_heap_bytes
                        .is_multiple_of(1024)
                {
                    return Err(TransactionError::SanitizeFailure);
                }

                Ok(TransactionConfiguration {
                    updated_heap_bytes: transaction_configuration.updated_heap_bytes,
                    compute_unit_limit: transaction_configuration
                        .compute_unit_limit
                        .min(MAX_COMPUTE_UNIT_LIMIT),
                    priority_fee_lamports: transaction_configuration.priority_fee_lamports,
                    loaded_accounts_data_size_limit: transaction_configuration
                        .loaded_accounts_data_size_limit
                        .min(MAX_LOADED_ACCOUNTS_DATA_SIZE_BYTES.get()),
                })
            }
```

**File:** runtime-transaction/src/transaction_meta.rs (L230-296)
```rust
    #[test]
    fn test_try_into_config_v1_no_clamping() {
        let feature_set = FeatureSet::all_enabled();

        let input = TransactionConfiguration {
            updated_heap_bytes: 65_536,
            compute_unit_limit: 123_456,
            priority_fee_lamports: 42,
            loaded_accounts_data_size_limit: 789_012,
        };

        let config = VersionedTransactionConfiguration::V1(input)
            .try_into_config(&feature_set)
            .unwrap();

        assert_eq!(config.updated_heap_bytes, 65_536);
        assert_eq!(config.compute_unit_limit, 123_456);
        assert_eq!(config.priority_fee_lamports, 42);
        assert_eq!(config.loaded_accounts_data_size_limit, 789_012);
    }

    #[test]
    fn test_try_into_config_v1_clamps_compute_unit_limit() {
        let feature_set = FeatureSet::all_enabled();

        let input = TransactionConfiguration {
            updated_heap_bytes: 65_536,
            compute_unit_limit: MAX_COMPUTE_UNIT_LIMIT.saturating_add(1),
            priority_fee_lamports: 42,
            loaded_accounts_data_size_limit: 1,
        };

        let config = VersionedTransactionConfiguration::V1(input)
            .try_into_config(&feature_set)
            .unwrap();

        assert_eq!(config.compute_unit_limit, MAX_COMPUTE_UNIT_LIMIT);
        assert_eq!(config.updated_heap_bytes, 65_536);
        assert_eq!(config.priority_fee_lamports, 42);
        assert_eq!(config.loaded_accounts_data_size_limit, 1);
    }

    #[test]
    fn test_try_into_config_v1_clamps_loaded_accounts_data_size_limit() {
        let feature_set = FeatureSet::all_enabled();

        let max_loaded_accounts_data_size = MAX_LOADED_ACCOUNTS_DATA_SIZE_BYTES.get();

        let input = TransactionConfiguration {
            updated_heap_bytes: 65_536,
            compute_unit_limit: 123_456,
            priority_fee_lamports: 42,
            loaded_accounts_data_size_limit: max_loaded_accounts_data_size.saturating_add(1),
        };

        let config = VersionedTransactionConfiguration::V1(input)
            .try_into_config(&feature_set)
            .unwrap();

        assert_eq!(
            config.loaded_accounts_data_size_limit,
            max_loaded_accounts_data_size
        );
        assert_eq!(config.updated_heap_bytes, 65_536);
        assert_eq!(config.compute_unit_limit, 123_456);
        assert_eq!(config.priority_fee_lamports, 42);
    }
```

**File:** svm/src/account_loader.rs (L480-511)
```rust
impl LoadedTransactionDataSize {
    fn with_max_size(requested_loaded_accounts_data_size_limit: u32) -> Self {
        Self {
            loaded_accounts_data_size: 0,
            requested_loaded_accounts_data_size_limit,
        }
    }

    fn increase_calculated_data_size(
        &mut self,
        data_size_delta: usize,
        error_metrics: &mut TransactionErrorMetrics,
    ) -> Result<()> {
        // this branch is unreachable in practice (though not by construction),
        // since it would imply an account >4gb in size
        let Ok(data_size_delta) = u32::try_from(data_size_delta) else {
            self.loaded_accounts_data_size = u32::MAX;
            error_metrics.max_loaded_accounts_data_size_exceeded += 1;
            return Err(TransactionError::MaxLoadedAccountsDataSizeExceeded);
        };

        self.loaded_accounts_data_size = self
            .loaded_accounts_data_size
            .saturating_add(data_size_delta);

        if self.loaded_accounts_data_size > self.requested_loaded_accounts_data_size_limit {
            error_metrics.max_loaded_accounts_data_size_exceeded += 1;
            Err(TransactionError::MaxLoadedAccountsDataSizeExceeded)
        } else {
            Ok(())
        }
    }
```
