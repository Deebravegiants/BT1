### Title
FeesOnlyTransaction under-reports loaded_accounts_data_size when define_ltds_fee_only_semantics is disabled, decoupling billed cost from actual account load work - ([File: svm/src/account_loader.rs])

### Summary
When `load_transaction_accounts` fails after already loading (and, for LoaderV3 programs, deserializing and reading) potentially large programdata accounts, the resulting `TransactionLoadResult::FeesOnly` reports `loaded_accounts_data_size` as `rollback_accounts.data_size()` instead of the actual `LoadedTransactionDataSize` accumulator that tracked real bytes touched, whenever `define_ltds_fee_only_semantics` is disabled. This lets a transaction that intentionally triggers a late failure in the loader force the node to perform real I/O/deserialization work on large accounts while the fee-only cost path reports only the (typically much smaller) fee-payer/nonce rollback account size.

### Finding Description
In `svm/src/account_loader.rs::load_transaction`, `load_transaction_accounts` is called with a `LoadedTransactionDataSize` accumulator (`loaded_transaction_data_size`) that is incremented for every account touched, including programdata accounts read via the `bpf_loader_upgradeable::check_id` branch (`account_loader.rs:562-584`), which performs an actual `account_loader.load_account(&programdata_address)` call and a `bincode::deserialize` of the owning program account's data.

If `load_transaction_accounts` returns `Err`, the code builds `TransactionLoadResult::FeesOnly(FeesOnlyTransaction { ... })` at `svm/src/account_loader.rs:456-468`:
```
loaded_accounts_data_size: if account_loader.feature_set.define_ltds_fee_only_semantics {
    loaded_transaction_data_size.into()
} else {
    tx_details.rollback_accounts.data_size() as u32
},
```
When the feature is disabled, the field is populated from `tx_details.rollback_accounts.data_size()` — a value derived purely from the fee-payer/nonce rollback bookkeeping — completely discarding `loaded_transaction_data_size`, which is the only value that reflects the actual bytes read/deserialized up to the point of failure (including any large programdata accounts loaded in the `bpf_loader_upgradeable` branch before the failing account caused an `Err`).

An attacker can therefore construct a transaction whose account list is ordered so that several large, valid LoaderV3 program accounts (with correspondingly large programdata accounts) are loaded and counted early, and then a later account in `account_keys` (or a later program in `program_instructions_iter`) deterministically fails to load (e.g., a nonexistent account referenced with `TransactionError::AccountNotFound`/`InvalidProgramForExecution` and other loader errors), causing the whole call to return `Err`. Because the failure is reached only after the loader has already performed the disk/cache reads and deserialization for the large programdata accounts, real I/O work has been done, but the reported `loaded_accounts_data_size` collapses to `rollback_accounts.data_size()`, which only accounts for the fee-payer/nonce accounts already loaded during validation — not the programdata bytes.

This value then flows into `cost-model/src/cost_model.rs` (`calculate_cost_for_executed_transaction`) and downstream fee/cost accounting, which uses `loaded_accounts_data_size` as the basis for the loaded-accounts-data-size cost component. Since the value is understated, the actual cost charged against block limits/fees does not reflect the real work performed.

No other check compensates for this: `load_transaction_accounts` performs no early accounting reconciliation on failure, and the branch is only taken when `define_ltds_fee_only_semantics` is false, i.e., precisely the precondition stated in the question.

### Impact Explanation
This is a cost-accounting integrity issue (SIMD-0186 loaded-accounts-data-size fee model): an unprivileged attacker can repeatedly submit transactions engineered to load several large LoaderV3 program/programdata accounts and then deterministically fail late in `load_transaction_accounts`, paying only the minimal FeesOnly cost (based on `rollback_accounts.data_size()`) while forcing the validator to perform the real account-load I/O/deserialization for the large programdata accounts. Repeated at scale, this allows cheap amplification of validator I/O/memory work relative to the fee/cost actually billed, undercharging execution and potentially allowing more such transactions to be packed per block than the true I/O cost should permit. This matches the "materially underpriced execution" / cost-model bypass category.

### Likelihood Explanation
Feasible and repeatable with a single unprivileged account: the attacker only needs to submit an ordinary transaction (via RPC/TPU) referencing several existing large LoaderV3 programs (and their programdata accounts, discoverable on-chain), plus one account/program reference designed to fail account loading later in `load_transaction_accounts` (e.g., a nonexistent program id triggers `TransactionError::ProgramAccountNotFound` in the `program_instructions_iter` loop at `account_loader.rs:606-617`, or a writable account referencing a deliberately-invalid state to hit `load_transaction_account`'s error paths). This requires no special privileges, staking, or leader control — only crafting an ordinary transaction and broadcasting it, and can be repeated across many transactions/blocks. The condition is gated specifically on `define_ltds_fee_only_semantics` being disabled, which is the stated precondition of the question.

### Recommendation
Always use the `loaded_transaction_data_size` accumulator (the same value used in the `Loaded` success path) for `FeesOnlyTransaction.loaded_accounts_data_size`, regardless of the `define_ltds_fee_only_semantics` feature flag, since it is the only value that reflects real bytes touched prior to failure. If the feature flag was intended to preserve legacy fee-computation semantics for backwards compatibility, ensure the legacy fallback (`rollback_accounts.data_size()`) is only reachable when no additional accounts (beyond fee-payer/nonce) were loaded, or otherwise reconcile the two by taking `max(loaded_transaction_data_size, rollback_accounts.data_size())` so the cost model never under-reports actual load work performed.

### Proof of Concept
Rust unit test plan (extending `svm/src/account_loader.rs` test module, similar to `test_load_transaction_accounts_program_success_complete`):
1. Set up an `AccountLoader` mock/test callback (`TestCallback` used elsewhere in that test module) with:
   - A fee payer account.
   - Several `bpf_loader_upgradeable`-owned "Program" accounts, each pointing to a large programdata account (e.g., 1 MB each), not directly included in `account_keys`.
   - A final account reference in the message that is guaranteed to fail loading (e.g., a program id not present in the account loader, hitting `TransactionError::ProgramAccountNotFound`).
2. Call `load_transaction_accounts` directly (or `load_transaction`) with `account_loader.feature_set.define_ltds_fee_only_semantics = false`.
3. Assert:
   - The function returns `Err(...)` (confirming a late failure after the large programdata accounts were already loaded).
   - Wrap the call in `load_transaction` and inspect the resulting `TransactionLoadResult::FeesOnly(fees_only).loaded_accounts_data_size`.
   - Compare it against a manually tracked sum of bytes actually read via a counting/wrapper `TransactionProcessingCallback::get_account_shared_data` (or by instrumenting `load_account` calls) for all accounts loaded prior to the failure, including the programdata accounts from the `bpf_loader_upgradeable::check_id` branch.
   - Expect: `fees_only.loaded_accounts_data_size` (from `rollback_accounts.data_size()`) is much smaller (e.g., only fee-payer bytes) than the actual bytes read (which include the large programdata accounts), demonstrating the under-reporting.
4. Repeat with `define_ltds_fee_only_semantics = true` and assert `loaded_accounts_data_size` now correctly reflects `loaded_transaction_data_size`, matching the real bytes read — showing the feature flag is the exact fix boundary and confirming the vulnerability is present only when the flag is disabled.