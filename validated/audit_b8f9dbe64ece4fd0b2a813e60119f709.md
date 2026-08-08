### Title
`CostModel::calculate_allocated_accounts_data_size` under-counts account growth performed via CPI, causing block-level `allocated_accounts_data_size` (`MAX_BLOCK_ACCOUNTS_DATA_SIZE_DELTA`) admission control to be blind to CPI-driven `CreateAccount`/`Allocate` calls - ([File: cost-model/src/cost_model.rs])

### Summary
`CostModel::calculate_allocated_accounts_data_size` is fed only `transaction.program_instructions_iter()`, i.e., only top-level instructions, both for the pre-execution estimate (`calculate_cost`) and for the post-execution "actual" recomputation (`calculate_cost_for_executed_transaction`). A BPF program that itself CPIs into the System program to `CreateAccount`/`Allocate` large `space` therefore contributes `0` to `allocated_accounts_data_size` even though the account is really created/resized. This causes `CostTracker::would_fit`'s `WouldExceedAccountDataBlockLimit` check to systematically under-estimate real per-slot account-data growth for any transaction whose allocation happens purely inside CPI.

### Finding Description
`CostModel::calculate_cost` computes `allocated_accounts_data_size` via `calculate_transaction_cost(transaction, transaction.program_instructions_iter(), ...)` [1](#0-0) , and `calculate_allocated_accounts_data_size` only inspects `(program_id, instruction)` pairs from that top-level iterator, matching `SystemInstruction::CreateAccount/Allocate/...` when `program_id == system_program::id()` [2](#0-1) . Any `CreateAccount`/`Allocate` issued as an inner (CPI) instruction is invisible to this scan because it never appears as a top-level `(program_id, instruction)` pair.

Crucially, this is *not* fixed after execution: `calculate_cost_for_executed_transaction`, which is used by `get_transaction_costs` in `runtime/src/transaction_execution.rs` to recompute the "actual" cost that gets folded into the cost tracker after commit, still calls `Self::calculate_allocated_accounts_data_size(transaction.program_instructions_iter(), ...)` — it only substitutes the *actual* `programs_execution_cost` and `loaded_accounts_data_size_cost`, not `allocated_accounts_data_size` [3](#0-2) . The real execution result carries `accounts_resize_delta`/`AccountsDeltas` reflecting true account growth [4](#0-3) [5](#0-4) , but this actual delta is never plumbed into `allocated_accounts_data_size`/`CostTracker`; it is only used to update the bank-wide `accounts_data_size_delta_on_chain` counter, a separate mechanism.

`CostTracker::would_fit` uses this (mis-)computed `allocated_accounts_data_size` to enforce a **block-wide** budget, `MAX_BLOCK_ACCOUNTS_DATA_SIZE_DELTA` (100,000,000 bytes) [6](#0-5) , rejecting new transactions with `CostTrackerError::WouldExceedAccountDataBlockLimit` once the tracked sum would exceed the limit [7](#0-6) . Since CPI-driven allocations contribute `0` to this running sum, an attacker can pack many transactions that each CPI-allocate large accounts (up to `MAX_PERMITTED_DATA_LENGTH` per allocation, capped in the runtime by `MAX_ACCOUNT_DATA_GROWTH_PER_TRANSACTION` per transaction) into a block without the tracker's `allocated_accounts_data_size` budget ever reflecting that growth, defeating the intended block-level cap on total per-slot account-data growth.

Note that this does **not** bypass the **per-transaction** hard limit: `TransactionAccounts::can_data_be_resized` independently enforces `MAX_ACCOUNT_DATA_GROWTH_PER_TRANSACTION` at actual resize time regardless of CPI depth [8](#0-7) , so a single transaction cannot allocate unbounded space. The vulnerability is scoped strictly to the **block-level admission accounting** (`MAX_BLOCK_ACCOUNTS_DATA_SIZE_DELTA`) being blind to CPI-originated allocations, letting the cost model/cost tracker under-price and over-admit such transactions relative to the real work performed.

### Impact Explanation
This matches the "cost model / compute-budget underpricing" bounty category: the cost-tracker's block-wide `allocated_accounts_data_size` (`MAX_BLOCK_ACCOUNTS_DATA_SIZE_DELTA`) admission gate can be bypassed for CPI-triggered allocations, allowing a leader/validator to admit more real account-growth work into a slot than the declared budget models, undermining the invariant that "declared compute units / loaded-accounts-data-size / cost-model estimates must upper-bound the real work performed." This is a resource-accounting/DoS-adjacent issue (excess real per-slot account-data growth work), not a fund-loss or consensus-halt bug, since the per-transaction data-growth ceiling (`MAX_ACCOUNT_DATA_GROWTH_PER_TRANSACTION`) still bounds worst-case damage per transaction.

### Likelihood Explanation
Highly feasible for any unprivileged attacker: deploy (or reuse) any BPF program that CPIs a `SystemInstruction::CreateAccount`/`Allocate` with large `space`, submit ordinary transactions invoking it as the sole top-level instruction. No special privileges, keys, or validator control are required, and the flaw is deterministic and repeatable across every transaction shaped this way.

### Recommendation
Compute `allocated_accounts_data_size` from the transaction's real execution-time `AccountsDeltas`/`accounts_resize_delta` (already collected in `TransactionExecutionDetails`) when finalizing/recomputing "actual" cost in `calculate_cost_for_executed_transaction`, instead of re-scanning only `program_instructions_iter()`. At minimum, feed the actual post-execution resize delta into the cost-tracker update path (`get_transaction_costs` in `runtime/src/transaction_execution.rs`) so the block-level `allocated_data_size` budget reflects CPI-driven growth, not just top-level System Program instructions.

### Proof of Concept
```rust
// cost-model/src/cost_model.rs (illustrative integration test)
#[test]
fn test_cpi_allocation_undercounted_by_cost_model() {
    // 1. Deploy a helper BPF program (e.g. programs/sbf/rust/realloc_invoke or a
    //    custom program) whose single instruction CPIs
    //    SystemInstruction::CreateAccount { space: MAX_PERMITTED_DATA_LENGTH, .. }.
    // 2. Build a transaction with ONE top-level instruction calling that program
    //    (no top-level System Program instruction).
    let sanitized_tx = /* RuntimeTransaction wrapping the single CPI-invoking instruction */;

    // Pre-execution cost-model estimate:
    let pre_cost = CostModel::calculate_cost(&sanitized_tx, &FeatureSet::all_enabled());
    assert_eq!(pre_cost.allocated_accounts_data_size(), 0); // BUG: should be MAX_PERMITTED_DATA_LENGTH

    // 3. Execute the transaction against a real Bank (bank.load_execute_and_commit_transactions)
    //    and capture accounts_resize_delta from TransactionExecutionDetails.
    let actual_allocated_bytes = /* execution_details.accounts_deltas.accounts_resize_delta */;
    assert!(actual_allocated_bytes > 0); // account really grew

    // 4. Recompute "actual" cost as the runtime does:
    let post_cost = CostModel::calculate_cost_for_executed_transaction(
        &sanitized_tx,
        executed_units,
        loaded_accounts_data_size,
        &FeatureSet::all_enabled(),
    );
    // BUG: still 0, even though execution shows real allocation.
    assert_eq!(post_cost.allocated_accounts_data_size(), 0);

    // Invariant violated: pre/post estimate should be >= actual bytes allocated.
    assert!(pre_cost.allocated_accounts_data_size() < actual_allocated_bytes as u64);
}
```
Expected result with current code: both assertions of `allocated_accounts_data_size() == 0` pass while `actual_allocated_bytes > 0`, demonstrating the cost model estimate does not upper-bound the real per-transaction account allocation, and that this gap is never corrected in the "actual" cost path used to update `CostTracker`'s block-wide `allocated_accounts_data_size` accounting.

### Citations

**File:** cost-model/src/cost_model.rs (L36-52)
```rust
    pub fn calculate_cost<'a, Tx: TransactionMeta + SVMStaticMessage>(
        transaction: &'a Tx,
        feature_set: &FeatureSet,
    ) -> TransactionCost<'a, Tx> {
        let (programs_execution_cost, loaded_accounts_data_size_cost) =
            Self::get_estimated_execution_cost(transaction, feature_set);
        let data_bytes_cost = Self::get_instructions_data_cost(transaction);
        Self::calculate_transaction_cost(
            transaction,
            transaction.program_instructions_iter(),
            transaction.num_write_locks(),
            programs_execution_cost,
            loaded_accounts_data_size_cost,
            data_bytes_cost,
            feature_set,
        )
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

**File:** cost-model/src/cost_model.rs (L242-301)
```rust
    fn calculate_account_data_size_on_instruction(
        program_id: &Pubkey,
        instruction: SVMInstruction,
        feature_set: &FeatureSet,
    ) -> SystemProgramAccountAllocation {
        if program_id == &system_program::id() {
            if let Ok(instruction) =
                limited_deserialize(instruction.data, solana_packet::PACKET_DATA_SIZE as u64)
            {
                Self::calculate_account_data_size_on_deserialized_system_instruction(
                    instruction,
                    feature_set,
                )
            } else {
                SystemProgramAccountAllocation::Failed
            }
        } else {
            SystemProgramAccountAllocation::None
        }
    }

    /// eventually, potentially determine account data size of all writable accounts
    /// at the moment, calculate account data size of account creation
    fn calculate_allocated_accounts_data_size<'a>(
        instructions: impl Iterator<Item = (&'a Pubkey, SVMInstruction<'a>)>,
        feature_set: &FeatureSet,
    ) -> u64 {
        let mut tx_attempted_allocation_size = Saturating(0u64);
        for (program_id, instruction) in instructions {
            match Self::calculate_account_data_size_on_instruction(
                program_id,
                instruction,
                feature_set,
            ) {
                SystemProgramAccountAllocation::Failed => {
                    // If any system program instructions can be statically
                    // determined to fail, no allocations will actually be
                    // persisted by the transaction. So return 0 here so that no
                    // account allocation budget is used for this failed
                    // transaction.
                    return 0;
                }
                SystemProgramAccountAllocation::None => continue,
                SystemProgramAccountAllocation::Some(ix_attempted_allocation_size) => {
                    tx_attempted_allocation_size += ix_attempted_allocation_size;
                }
            }
        }

        // The runtime prevents transactions from allocating too much account
        // data so clamp the attempted allocation size to the max amount.
        //
        // Note that if there are any custom bpf instructions in the transaction
        // it's tricky to know whether a newly allocated account will be freed
        // or not during an intermediate instruction in the transaction so we
        // shouldn't assume that a large sum of allocations will necessarily
        // lead to transaction failure.
        (MAX_PERMITTED_ACCOUNTS_DATA_ALLOCATIONS_PER_TRANSACTION as u64)
            .min(tx_attempted_allocation_size.0)
    }
```

**File:** svm/src/transaction_execution_result.rs (L48-54)
```rust
#[derive(Clone, Debug, Eq, PartialEq)]
pub struct AccountsDeltas {
    /// aggregate resize delta across all accounts touched by the transaction
    pub accounts_resize_delta: i64,
    /// aggregate size of all accounts that were uninitialized by this transaction
    pub accounts_uninitialized_size: u64,
}
```

**File:** runtime/src/bank.rs (L4419-4430)
```rust
        let accounts_data_len_delta = processing_results
            .iter()
            .filter_map(|processing_result| processing_result.processed_transaction())
            .filter_map(|processed_tx| processed_tx.execution_details())
            .filter_map(|details| details.accounts_deltas.as_ref())
            .map(|deltas| {
                deltas
                    .accounts_resize_delta
                    .saturating_sub_unsigned(deltas.accounts_uninitialized_size)
            })
            .sum();
        self.update_accounts_data_size_delta_on_chain(accounts_data_len_delta);
```

**File:** cost-model/src/block_cost_limits.rs (L35-37)
```rust
/// The maximum allowed size, in bytes, that accounts data can grow, per block.
/// This can also be thought of as the maximum size of new allocations per block.
pub const MAX_BLOCK_ACCOUNTS_DATA_SIZE_DELTA: u64 = 100_000_000;
```

**File:** cost-model/src/cost_tracker.rs (L288-293)
```rust
        let allocated_accounts_data_size =
            self.allocated_accounts_data_size + Saturating(tx_cost.allocated_accounts_data_size());

        if allocated_accounts_data_size.0 > self.limits.allocated_data_size {
            return Err(CostTrackerError::WouldExceedAccountDataBlockLimit);
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
