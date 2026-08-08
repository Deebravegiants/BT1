### Title
Cost model charges stale pre-execution `loaded_accounts_data_size`, ignoring in-execution account growth up to 20 MiB - ([File: svm/src/transaction_processor.rs])

### Summary
`LoadedTransaction.loaded_accounts_data_size` is computed once during account loading in `load_transaction_accounts`/`LoadedTransactionDataSize::increase_calculated_data_size` [1](#0-0)  and is never recalculated after execution. `execute_loaded_transaction` only overwrites `loaded_transaction.accounts` and `touched_flags` post-execution, leaving `loaded_accounts_data_size` untouched [2](#0-1) . Meanwhile, account growth during execution is bounded by the independent, transaction-agnostic constant `MAX_ACCOUNT_DATA_GROWTH_PER_TRANSACTION` (20 MiB) rather than by `loaded_accounts_data_size_limit`, so a program can grow accounts far beyond what was charged for loading.

### Finding Description
During account loading, `load_transaction_accounts` accumulates the size of every account touched into a `LoadedTransactionDataSize` accumulator, checked against `requested_loaded_accounts_data_size_limit` (the transaction's `loaded_accounts_data_size_limit` set via `ComputeBudgetInstruction::set_loaded_accounts_data_size_limit`) [3](#0-2) . This produces `LoadedTransaction.loaded_accounts_data_size`, a `u32` reflecting only the sizes of accounts as they existed *before* execution [4](#0-3) .

During execution, `TransactionContext::access_violation_handler` can grow a writable account's data in place whenever a program writes past the current buffer end (e.g., via realloc syscalls or direct memory writes under `virtual_address_space_adjustments`) [5](#0-4) . The growth check that gates this is `TransactionAccounts::can_data_be_resized`, which only compares the account's own `resize_delta` against the global constant `MAX_ACCOUNT_DATA_GROWTH_PER_TRANSACTION` (20 MiB — `MAX_ACCOUNT_DATA_LEN * 2`) [6](#0-5) [7](#0-6) . This resize check is entirely independent of the transaction's `loaded_accounts_data_size_limit`/`requested_loaded_accounts_data_size_limit`, so an attacker can set a low `loaded_accounts_data_size_limit` (just enough to load small accounts) while still growing those accounts by up to ~20 MiB during execution.

After `process_message` completes, `execute_loaded_transaction` builds the `ExecutedTransaction` by writing back `loaded_transaction.accounts = accounts;` and `loaded_transaction.touched_flags = touched_flags;`, but never updates `loaded_transaction.loaded_accounts_data_size` to reflect the new, larger account sizes [8](#0-7) . `ProcessedTransaction::loaded_accounts_data_size()` simply returns this stale field for `Executed` transactions [9](#0-8) .

This stale value is what feeds the cost model post-execution in both banking-stage and replay paths:
- `runtime/src/transaction_execution.rs::get_transaction_costs` uses `committed_tx.loaded_account_stats.loaded_accounts_data_size` (itself derived from the same stale `LoadedTransaction.loaded_accounts_data_size`, see `create_commit_results`) to call `CostModel::calculate_cost_for_executed_transaction` [10](#0-9) [11](#0-10) .
- `core/src/banking_stage/consumer.rs::calculate_processed_transaction_costs` does the same via `processed_tx.loaded_accounts_data_size()` [12](#0-11) .

`CostModel::calculate_cost_for_executed_transaction` charges `loaded_accounts_data_size_cost` purely as a function of this passed-in byte count, rounded up to pages of `ACCOUNT_DATA_COST_PAGE_SIZE` at `DEFAULT_HEAP_COST` per page [13](#0-12) [14](#0-13) . Since the byte count fed in is the pre-execution figure, the resulting cost systematically undercounts transactions whose accounts were substantially grown mid-execution.

No existing check closes this gap: the `loaded_accounts_data_size_limit` enforcement in `LoadedTransactionDataSize::increase_calculated_data_size` only runs during loading (before growth happens), and account growth enforcement (`can_data_be_resized`) is deliberately decoupled from that limit, tracking only the global `MAX_ACCOUNT_DATA_GROWTH_PER_TRANSACTION` cap.

### Impact Explanation
This falls under underpriced/underbilled execution — the cost model (used for both the CU-based block cost limit via `CostTracker::try_add` in `cost-model/src/cost_tracker.rs` and for compute budget accounting) systematically undercounts the memory footprint of transactions that grow accounts during execution. Because `check_block_cost_limits`/`try_add_processed_transaction_costs` compare the *actual* charge against block limits using this understated figure, more such transactions can be packed into a block than the true memory/CPU cost justifies, degrading validator performance/replay time relative to the accounted cost — a cost-model / resource-exhaustion class issue, not a funds-loss issue.

### Likelihood Explanation
This is trivially reachable by any unprivileged transaction sender:
- Include accounts that are small/nonexistent at load time (keeping `loaded_accounts_data_size` and the requested `loaded_accounts_data_size_limit` low, e.g., a few hundred bytes).
- Include a program instruction (deployed by the attacker, no special privilege needed) that reallocates/writes into a writable account, growing it via the `access_violation_handler`/`set_data_length` path up to just under `MAX_ACCOUNT_DATA_GROWTH_PER_TRANSACTION` (20 MiB), which is legal regardless of the small `loaded_accounts_data_size_limit`.
- Submit via any public RPC/TPU endpoint; no leader/validator control, no staking, no cluster-specific config needed. Repeatable per transaction, requiring only compute budget to cover the realloc CUs.

### Recommendation
After execution, recompute (or add the tracked `accounts_resize_delta`/final account sizes to) `LoadedTransaction.loaded_accounts_data_size` in `execute_loaded_transaction` before constructing `ExecutedTransaction`, so `ProcessedTransaction::loaded_accounts_data_size()` reflects the actual post-execution byte footprint (e.g., sum `TRANSACTION_ACCOUNT_BASE_SIZE + account.data().len()` over final `accounts`, or add `accounts_resize_delta` from `AccountsDeltas` to the pre-execution figure) and feed that corrected value into `CostModel::calculate_cost_for_executed_transaction` in both `runtime/src/transaction_execution.rs::get_transaction_costs` and `core/src/banking_stage/consumer.rs::calculate_processed_transaction_costs`.

### Proof of Concept
Rust integration test plan (in `runtime/src/transaction_execution.rs` or `svm/src/transaction_processor.rs` test modules):
1. Deploy a BPF/SBF test program that, given a writable account, calls `set_data_length`/realloc syscall to grow that account's data close to `MAX_ACCOUNT_DATA_GROWTH_PER_TRANSACTION` (e.g., 19 MiB) in a single instruction (analogous to existing tests around `programs/sbf/tests/programs.rs` realloc access-violation tests).
2. Construct a transaction that references this account with an initial tiny size (e.g., 0 or a few bytes) and sets `ComputeBudgetInstruction::set_loaded_accounts_data_size_limit` to a value just above the small pre-execution `loaded_accounts_data_size` (e.g., 2 KiB).
3. Execute via `bank.load_execute_and_commit_transactions` and capture `CommittedTransaction.loaded_account_stats.loaded_accounts_data_size`.
4. Assert:
   - The transaction succeeds (growth allowed since it's under `MAX_ACCOUNT_DATA_GROWTH_PER_TRANSACTION`, unrelated to the 2 KiB limit).
   - `committed.loaded_account_stats.loaded_accounts_data_size` equals (or is close to) the pre-execution figure (~2 KiB), not the actual final in-memory account size (~19 MiB).
   - `CostModel::calculate_cost_for_executed_transaction(...)` (as invoked in `get_transaction_costs`) yields `loaded_accounts_data_size_cost` computed from the small pre-execution figure via `CostModel::calculate_pages_for_bytes`/`calculate_pages_cost`, demonstrating the charged cost is far smaller than a cost computed from the true ~19 MiB footprint.
This directly demonstrates the invariant violation: the cost-model estimate for loaded-accounts-data-size fails to upper-bound the real account-load/resize work performed by the runtime.

### Citations

**File:** svm/src/account_loader.rs (L152-161)
```rust
pub struct LoadedTransaction {
    pub accounts: Vec<KeyedAccountSharedData>,
    /// Parallel to `accounts`: whether each account must be written back. Empty
    /// until execution.
    pub touched_flags: Box<[bool]>,
    pub fee_details: FeeDetails,
    pub rollback_accounts: RollbackAccounts,
    pub(crate) compute_budget: SVMTransactionExecutionBudget,
    pub loaded_accounts_data_size: u32,
}
```

**File:** svm/src/account_loader.rs (L488-511)
```rust
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

**File:** svm/src/account_loader.rs (L522-549)
```rust
fn load_transaction_accounts<CB: TransactionProcessingCallback>(
    account_loader: &mut AccountLoader<CB>,
    message: &impl SVMMessage,
    loaded_fee_payer_account: LoadedTransactionAccount,
    loaded_tx_data_size: &mut LoadedTransactionDataSize,
    error_metrics: &mut TransactionErrorMetrics,
    rent: &Rent,
) -> Result<Vec<KeyedAccountSharedData>> {
    let account_keys = message.account_keys();
    let mut loaded_transaction_accounts = Vec::with_capacity(account_keys.len());
    let mut additional_loaded_accounts: AHashSet<Pubkey> = AHashSet::new();

    // Transactions pay a base fee per address lookup table.
    loaded_tx_data_size.increase_calculated_data_size(
        message
            .num_lookup_tables()
            .saturating_mul(ADDRESS_LOOKUP_TABLE_BASE_SIZE),
        error_metrics,
    )?;

    let mut collect_loaded_account =
        |account_loader: &mut AccountLoader<CB>, key: &Pubkey, loaded_account| -> Result<()> {
            let LoadedTransactionAccount {
                account,
                loaded_size,
            } = loaded_account;

            loaded_tx_data_size.increase_calculated_data_size(loaded_size, error_metrics)?;
```

**File:** svm/src/transaction_processor.rs (L1207-1232)
```rust
        loaded_transaction.accounts = accounts;
        loaded_transaction.touched_flags = touched_flags;
        execute_timings.details.total_account_count += loaded_transaction.accounts.len() as u64;
        execute_timings.details.changed_account_count += touched_account_count as u64;

        let return_data = if config.recording_config.enable_return_data_recording
            && !return_data.data.is_empty()
        {
            Some(return_data)
        } else {
            None
        };

        ExecutedTransaction {
            execution_details: TransactionExecutionDetails {
                status,
                log_messages,
                inner_instructions,
                return_data,
                executed_units,
                accounts_deltas,
            },
            loaded_transaction,
            programs_modified_by_tx: program_cache_for_tx_batch.drain_modified_entries(),
        }
    }
```

**File:** transaction-context/src/transaction.rs (L559-614)
```rust
                let remaining_allowed_growth = MAX_ACCOUNT_DATA_GROWTH_PER_TRANSACTION
                    .saturating_sub(accounts.resize_delta())
                    .max(0) as usize;

                if requested_length > region.len() {
                    // Realloc immediately here to fit the requested access,
                    // then later in CPI or deserialization realloc again to the
                    // account length the program stored in AccountInfo.
                    let old_len = account.data().len();
                    let new_len = (address_space_reserved_for_account as usize)
                        .min(MAX_ACCOUNT_DATA_LEN as usize)
                        .min(old_len.saturating_add(remaining_allowed_growth));
                    // The last two min operations ensure the following:
                    debug_assert!(accounts.can_data_be_resized(old_len, new_len).is_ok());
                    if accounts
                        .update_accounts_resize_delta(old_len, new_len)
                        .is_err()
                    {
                        return;
                    }

                    account.resize(new_len, 0);
                    let data_ptr = region.host_buffer().ptr() as *mut u8;
                    let new_buffer = std::ptr::slice_from_raw_parts_mut(data_ptr, new_len);
                    unsafe {
                        // SAFETY:
                        //
                        // Contract from `MemoryRegion::redirect`: MemoryRegion must point to a
                        // valid object live for the duration of this `MemoryMapping`.
                        //
                        // Evidence: There are two distinct cases, when the account buffer is
                        // serialized and when the account buffer is directly mapped.
                        // * In the serialization case we continue pointing at the same buffer as
                        // before, and the original buffer must have satisfied the liveness
                        // condition before.
                        // * In the direct mapping case `account.resize` invalidates the buffer this
                        // region has been pointing at, but this is fixed up later in the "unshare"
                        // branch later.
                        // * In the serialization case the section of serialized buffer has the
                        // necessary padding after the account payload proper for resize. This
                        // padding is a part of the originally constructed `MemoryRegion` and is
                        // only later subsliced to not expose it before the first access to the
                        // area (which invokes this handler.)
                        //
                        // Contract from `MemoryRegion::redirect`: For `MemoryRegion`s marked
                        // writable, the host buffer must accept arbitrary bytes being overwritten
                        // without it resulting in unsoundness.
                        //
                        // Evidence: The account payloads dont have any internal soundness
                        // invariants. The buffer in the serialization case starts off and remains
                        // writable (even though the HostBuffer might have been initially created as
                        // immutable.) In the direct mapping case we redirect the region to the
                        // buffer stored in the account later on.
                        region.redirect(new_buffer);
                    }
                }
```

**File:** transaction-context/src/transaction_accounts.rs (L309-326)
```rust
    pub(crate) fn can_data_be_resized(
        &self,
        old_len: usize,
        new_len: usize,
    ) -> Result<(), InstructionError> {
        // The new length can not exceed the maximum permitted length
        if new_len > MAX_ACCOUNT_DATA_LEN as usize {
            return Err(InstructionError::InvalidRealloc);
        }
        // The resize can not exceed the per-transaction maximum
        let length_delta = (new_len as i64).saturating_sub(old_len as i64);
        if self.resize_delta.get().saturating_add(length_delta)
            > MAX_ACCOUNT_DATA_GROWTH_PER_TRANSACTION
        {
            return Err(InstructionError::MaxAccountsDataAllocationsExceeded);
        }
        Ok(())
    }
```

**File:** transaction-context/src/lib.rs (L19-24)
```rust
pub const MAX_ACCOUNT_DATA_LEN: u64 = 10 * 1024 * 1024;
// Note: With virtual_address_space_adjustments programs can grow accounts
// faster than they intend to, because the AccessViolationHandler might grow
// an account up to MAX_ACCOUNT_DATA_GROWTH_PER_INSTRUCTION at once.
pub const MAX_ACCOUNT_DATA_GROWTH_PER_TRANSACTION: i64 = MAX_ACCOUNT_DATA_LEN as i64 * 2;
pub const MAX_ACCOUNT_DATA_GROWTH_PER_INSTRUCTION: usize = 10 * 1_024;
```

**File:** svm/src/transaction_processing_result.rs (L100-106)
```rust
    pub fn loaded_accounts_data_size(&self) -> u32 {
        match self {
            Self::Executed(context) => context.loaded_transaction.loaded_accounts_data_size,
            Self::FeesOnly(details) => details.loaded_accounts_data_size,
            Self::NoOp(details) => details.loaded_accounts_bytes_limit,
        }
    }
```

**File:** runtime/src/transaction_execution.rs (L171-195)
```rust
// Get actual transaction execution costs from transaction commit results
fn get_transaction_costs<'a, Tx: TransactionWithMeta>(
    bank: &Bank,
    commit_results: &[TransactionCommitResult],
    sanitized_transactions: &'a [Tx],
) -> Vec<Option<TransactionCost<'a, Tx>>> {
    assert_eq!(sanitized_transactions.len(), commit_results.len());

    commit_results
        .iter()
        .zip(sanitized_transactions)
        .map(|(commit_result, tx)| {
            if let Ok(committed_tx) = commit_result {
                Some(CostModel::calculate_cost_for_executed_transaction(
                    tx,
                    committed_tx.executed_units,
                    committed_tx.loaded_account_stats.loaded_accounts_data_size,
                    &bank.feature_set,
                ))
            } else {
                None
            }
        })
        .collect()
}
```

**File:** runtime/src/bank.rs (L4479-4489)
```rust
                        Ok(CommittedTransaction {
                            status: execution_details.status,
                            log_messages: execution_details.log_messages,
                            inner_instructions: execution_details.inner_instructions,
                            return_data: execution_details.return_data,
                            executed_units,
                            fee_details,
                            loaded_account_stats: TransactionLoadedAccountsStats {
                                loaded_accounts_count: loaded_accounts.len(),
                                loaded_accounts_data_size,
                            },
```

**File:** core/src/banking_stage/consumer.rs (L490-517)
```rust
    fn calculate_processed_transaction_costs<'a, Tx: TransactionWithMeta>(
        bank: &Bank,
        transactions: &'a [Tx],
        processing_results: &[TransactionProcessingResult],
    ) -> Vec<Option<TransactionCost<'a, Tx>>> {
        let mut transaction_costs = Vec::with_capacity(processing_results.len());

        for (tx, processing_result) in transactions.iter().zip(processing_results) {
            let Some((executed_units, loaded_accounts_data_size)) = processing_result
                .processed_transaction()
                .map(|processed_tx| {
                    (
                        processed_tx.executed_units(),
                        processed_tx.loaded_accounts_data_size(),
                    )
                })
            else {
                transaction_costs.push(None);
                continue;
            };

            transaction_costs.push(Some(CostModel::calculate_cost_for_executed_transaction(
                tx,
                executed_units,
                loaded_accounts_data_size,
                &bank.feature_set,
            )));
        }
```

**File:** cost-model/src/cost_model.rs (L56-77)
```rust
    pub fn calculate_cost_for_executed_transaction<'a, Tx: TransactionMeta + SVMStaticMessage>(
        transaction: &'a Tx,
        actual_programs_execution_cost: u64,
        actual_loaded_accounts_data_size_bytes: u32,
        feature_set: &FeatureSet,
    ) -> TransactionCost<'a, Tx> {
        let loaded_accounts_data_size_cost = Self::calculate_loaded_accounts_data_size_cost(
            actual_loaded_accounts_data_size_bytes,
            feature_set,
        );
        let instructions_data_cost = Self::get_instructions_data_cost(transaction);

        Self::calculate_transaction_cost(
            transaction,
            transaction.program_instructions_iter(),
            transaction.num_write_locks(),
            actual_programs_execution_cost,
            loaded_accounts_data_size_cost,
            instructions_data_cost,
            feature_set,
        )
    }
```

**File:** cost-model/src/cost_model.rs (L196-201)
```rust
    pub fn calculate_loaded_accounts_data_size_cost(
        loaded_accounts_data_size: u32,
        _feature_set: &FeatureSet,
    ) -> u64 {
        Self::calculate_pages_cost(Self::calculate_pages_for_bytes(loaded_accounts_data_size))
    }
```
