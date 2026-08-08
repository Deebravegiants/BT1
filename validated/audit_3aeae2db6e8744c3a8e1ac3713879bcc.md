### Title
Cost model's account-data-allocation admission control is scoped only to System Program instructions and never priced into CU-based fees, allowing custom-program account growth to bypass the per-block data-size throttle - ([File: cost-model/src/cost_model.rs])

### Summary
`CostModel::calculate_allocated_accounts_data_size` (the only mechanism that gates aggregate account-data growth per block) only inspects top-level `system_program::id()` instructions for `CreateAccount`/`Allocate`/etc.; any instruction routed through a different (attacker-controlled) program returns `SystemProgramAccountAllocation::None` and contributes zero to the tracked allocation size. Separately, `TransactionCost::sum()` — the value used for CU-based block/account cost limits and priority-fee pricing — never includes `allocated_accounts_data_size` at all, only `signature_cost + write_lock_cost + data_bytes_cost + programs_execution_cost + loaded_accounts_data_size_cost`. This means real account-data growth achieved via a custom BPF program's own resize/realloc path is both unpriced in the CU cost model and untracked by the dedicated data-size admission control, while `TransactionExecutionDetails.accounts_deltas.accounts_resize_delta` (used later purely for bank-level `accounts_data_size` accounting) is tracked completely independently and never feeds back into either mechanism.

### Finding Description
`CostModel::calculate_transaction_cost` computes `allocated_accounts_data_size` via `calculate_allocated_accounts_data_size`, which iterates the transaction's top-level instructions and calls `calculate_account_data_size_on_instruction`: [1](#0-0) 

This function only counts a size when `program_id == &system_program::id()` and the deserialized instruction is one of `CreateAccount`/`CreateAccountWithSeed`/`Allocate`/`AllocateWithSeed`/`CreateAccountAllowPrefund`. For any instruction targeting a different program (i.e., a program the attacker deploys and controls), it unconditionally returns `SystemProgramAccountAllocation::None`: [1](#0-0) 

`allocated_accounts_data_size` is the sole input used by `CostTracker::would_fit`/`add_transaction_cost` to enforce the per-block `MAX_BLOCK_ACCOUNTS_DATA_SIZE_DELTA` limit: [2](#0-1) [3](#0-2) 

Meanwhile, `TransactionCost::sum()` — which is what actually gets checked against block/account CU cost limits and used to compute the priority fee reward ratio — never references `allocated_accounts_data_size`: [4](#0-3) 

Separately, the real account-data growth caused by execution is tracked as `accounts_resize_delta` in `TransactionExecutionDetails.accounts_deltas`, set inside `svm/src/transaction_processor.rs`, and only used afterward to update the bank's `accounts_data_size_delta_on_chain` bookkeeping counter — never fed back into `CostModel` or `CostTracker`: [5](#0-4) [6](#0-5) [7](#0-6) 

`ProcessedTransaction::executed_units()`/`loaded_accounts_data_size()` are what feed `CostModel::calculate_cost_for_executed_transaction` after commit, and again this path only surfaces CU and loaded-account-size, not resize delta: [8](#0-7) [9](#0-8) 

An attacker deploying an ordinary (unprivileged) BPF program that grows its own owned account via `AccountInfo::realloc`/`account.resize()` — rather than via a System Program `CreateAccount`/`Allocate` instruction — causes real per-transaction data growth (bounded per transaction by `MAX_ACCOUNT_DATA_GROWTH_PER_TRANSACTION`, enforced independently in `transaction-context/src/transaction_accounts.rs::can_data_be_resized`), but that growth is invisible to `calculate_allocated_accounts_data_size` because the resizing instruction's `program_id` is not `system_program::id()`. The transaction therefore consumes none of the block's `MAX_BLOCK_ACCOUNTS_DATA_SIZE_DELTA` budget even though it performs equivalent (or larger, since it isn't capped to `MAX_PERMITTED_ACCOUNTS_DATA_ALLOCATIONS_PER_TRANSACTION` in the cost-estimation path) account-data-growth work at commit time, while its priced CU cost (`sum()`) is unaffected by growth in either case since `allocated_accounts_data_size` isn't part of `sum()` regardless.

### Impact Explanation
This falls under systematic underpricing / resource-exhaustion: transactions that grow account data through a custom program bypass the one mechanism (`MAX_BLOCK_ACCOUNTS_DATA_SIZE_DELTA` admission control) specifically designed to bound aggregate account-data growth (and hence write/allocation I/O) per block, and the fee/CU cost model never prices this work in the first place. Repeated submission of such transactions by an unprivileged party can drive real accounts-db write/allocation I/O per block well above the value the cost model and cost tracker believe is being consumed, since the dedicated `allocated_accounts_data_size` counter reads as zero for these transactions. This matches the "resource exhaustion via underpriced execution" bounty category (CU/cost-model correctness), scoped to account-data-growth admission control, not the sBPF interpreter or metrics paths excluded by SECURITY.md.

### Likelihood Explanation
No special privileges are required — any user can deploy a program and submit ordinary transactions that call `resize`/`realloc` on accounts owned by that program. The bypass is deterministic and reproducible on every transaction that avoids the System Program's `CreateAccount`/`Allocate` family of instructions for its data-growth operations, which is the common pattern for programs managing their own dynamically-sized accounts (e.g. via CPI extend/realloc helpers, as exercised by `programs/sbf/rust/realloc*` test programs already in the repo). The precise achievable magnitude per transaction (bounded to `MAX_ACCOUNT_DATA_GROWTH_PER_TRANSACTION` and by how many realloc calls/instructions can be packed under the transaction size and instruction-trace limits) was not fully explored in this session — confirming the exact per-call realloc CU cost and its cap (`MAX_PERMITTED_DATA_INCREASE` per CPI call) would require reading the realloc syscall implementation, which I was not able to fully locate before the iteration budget was exhausted. This limits the precision of the "how much real I/O can be hidden per transaction/block" quantification but does not affect the validity of the underlying gap: `calculate_account_data_size_on_instruction`'s hard restriction to `system_program::id()` is unconditional and unambiguous.

### Recommendation
Extend the account-data-allocation accounting in `CostModel::calculate_allocated_accounts_data_size` (or a companion mechanism) to also account for the actual/estimated resize performed by non-System-Program instructions, e.g. by folding the executed `accounts_resize_delta` (already computed per transaction in `TransactionExecutionDetails.accounts_deltas`) into the post-execution `CostTracker::allocated_accounts_data_size` accounting (mirroring how `executed_units`/`loaded_accounts_data_size` are substituted with real values via `calculate_cost_for_executed_transaction` after commit), so that the per-block `MAX_BLOCK_ACCOUNTS_DATA_SIZE_DELTA` limit reflects real account growth regardless of which program performed it.

### Proof of Concept
```rust
// Integration-test-style plan (cost-model/src/cost_tracker.rs and svm integration harness):
//
// 1. Build transaction A: uses `system_instruction::create_account` with `space = N`.
//    assert CostModel::calculate_allocated_accounts_data_size(...) == N
//    (confirms system-program growth IS tracked).
//
// 2. Build transaction B: invokes a custom program instruction (e.g. the existing
//    `realloc`/`realloc_invoke` test programs under programs/sbf/rust/realloc*) that calls
//    `account.resize(N)` on an account owned by that custom program, achieving the same
//    or larger data growth than transaction A, with no System Program instruction present.
//    assert CostModel::calculate_allocated_accounts_data_size(tx_B.program_instructions_iter(), ..) == 0
//    (demonstrates the growth is invisible to the cost model / cost tracker input).
//
// 3. Feed both tx_A_cost and tx_B_cost through a CostTracker with
//    limits.allocated_data_size = N (i.e., only enough room for ONE such allocation):
//    - testee.try_add(&tx_A_cost) -> Ok
//    - testee.try_add(&tx_A_cost again) -> Err(WouldExceedAccountDataBlockLimit)  [correct throttling]
//    - reset tracker; testee.try_add(&tx_B_cost) repeated N/growth_per_tx times -> all Ok,
//      never triggers WouldExceedAccountDataBlockLimit despite equivalent real account growth,
//      because tx_B_cost.allocated_accounts_data_size() == 0.
//
// Expected assertion demonstrating the bug: unlimited repetitions of tx_B are accepted by
// CostTracker::would_fit under a data-size limit that would reject an equivalent number of
// System-Program-based allocations (tx_A), proving the admission control and CU cost model
// (TransactionCost::sum(), which also excludes allocated_accounts_data_size) do not bound
// custom-program-driven account-data growth.
```

### Citations

**File:** cost-model/src/cost_model.rs (L242-261)
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
```

**File:** cost-model/src/cost_tracker.rs (L272-293)
```rust
    fn would_fit(
        &self,
        tx_cost: &TransactionCost<impl TransactionWithMeta>,
    ) -> Result<(), CostTrackerError> {
        let cost: u64 = tx_cost.sum();

        if self.block_cost().saturating_add(cost) > self.limits.block_cost {
            // check against the total package cost
            return Err(CostTrackerError::WouldExceedBlockMaxLimit);
        }

        // check if the transaction itself is more costly than the account_cost_limit
        if cost > self.limits.account_cost {
            return Err(CostTrackerError::WouldExceedAccountMaxLimit);
        }

        let allocated_accounts_data_size =
            self.allocated_accounts_data_size + Saturating(tx_cost.allocated_accounts_data_size());

        if allocated_accounts_data_size.0 > self.limits.allocated_data_size {
            return Err(CostTrackerError::WouldExceedAccountDataBlockLimit);
        }
```

**File:** cost-model/src/cost_tracker.rs (L312-322)
```rust
    // Returns the highest account cost for all write-lock accounts `TransactionCost` updated
    fn add_transaction_cost(&mut self, tx_cost: &TransactionCost<impl TransactionWithMeta>) -> u64 {
        self.allocated_accounts_data_size += tx_cost.allocated_accounts_data_size();
        self.transaction_count += 1;
        self.transaction_signature_count += tx_cost.num_transaction_signatures();
        self.secp256k1_instruction_signature_count +=
            tx_cost.num_secp256k1_instruction_signatures();
        self.ed25519_instruction_signature_count += tx_cost.num_ed25519_instruction_signatures();
        self.secp256r1_instruction_signature_count +=
            tx_cost.num_secp256r1_instruction_signatures();
        self.add_transaction_execution_cost(tx_cost, tx_cost.sum())
```

**File:** cost-model/src/transaction_cost.rs (L18-25)
```rust
impl<'a, Tx> TransactionCost<'a, Tx> {
    pub fn sum(&self) -> u64 {
        self.signature_cost
            .saturating_add(self.write_lock_cost)
            .saturating_add(u64::from(self.data_bytes_cost))
            .saturating_add(self.programs_execution_cost)
            .saturating_add(self.loaded_accounts_data_size_cost)
    }
```

**File:** svm/src/transaction_execution_result.rs (L30-54)
```rust
#[derive(Clone, Debug, Eq, PartialEq)]
pub struct TransactionExecutionDetails {
    pub status: TransactionResult<()>,
    pub log_messages: Option<Vec<String>>,
    pub inner_instructions: Option<InnerInstructionsList>,
    pub return_data: Option<TransactionReturnData>,
    pub executed_units: u64,
    /// deltas related to total account data size changes for this transaction.
    /// NOTE: set to None IFF `status` is not `Ok`.
    pub accounts_deltas: Option<AccountsDeltas>,
}

impl TransactionExecutionDetails {
    pub fn was_successful(&self) -> bool {
        self.status.is_ok()
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct AccountsDeltas {
    /// aggregate resize delta across all accounts touched by the transaction
    pub accounts_resize_delta: i64,
    /// aggregate size of all accounts that were uninitialized by this transaction
    pub accounts_uninitialized_size: u64,
}
```

**File:** svm/src/transaction_processor.rs (L1191-1232)
```rust
        // accounts_resize_delta and accounts_uninitialized_size must be set to None
        // in the result if status is an error
        let (status, accounts_deltas) = post_account_state_info_result
            .map(|post_state_info| {
                (
                    Ok(()),
                    Some(AccountsDeltas {
                        accounts_resize_delta,
                        accounts_uninitialized_size: get_uninitialized_accounts_size(
                            &post_state_info,
                        ),
                    }),
                )
            })
            .unwrap_or_else(|err| (Err(err), None));

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

**File:** svm/src/transaction_processing_result.rs (L92-106)
```rust
    pub fn executed_units(&self) -> u64 {
        match self {
            Self::Executed(context) => context.execution_details.executed_units,
            Self::FeesOnly(_) => 0,
            Self::NoOp(details) => details.compute_unit_limit,
        }
    }

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
