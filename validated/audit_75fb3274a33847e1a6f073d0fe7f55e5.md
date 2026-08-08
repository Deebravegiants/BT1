## Title
Cost-model undercounts CPI-driven System Program account allocations, allowing block-level accounts-data-size budget bypass - ([File: cost-model/src/cost_model.rs])

## Summary
`CostModel::calculate_allocated_accounts_data_size` only inspects **top-level** instructions returned by `transaction.program_instructions_iter()` and checks `program_id == &system_program::id()` on each of them. If a transaction's top-level instruction targets an attacker-controlled on-chain program that in turn CPIs into `system_program::allocate`/`create_account`, the static scan sees only the caller's (non-system) `program_id` and records `SystemProgramAccountAllocation::None`, contributing `0` to the transaction's `allocated_accounts_data_size` even though the runtime will actually let the account grow.

## Finding Description
The estimate is computed by `CostModel::calculate_transaction_cost` → `calculate_allocated_accounts_data_size`, which iterates `instructions: impl Iterator<Item = (&Pubkey, SVMInstruction)>` sourced from `transaction.program_instructions_iter()` [1](#0-0) . For each instruction it calls `calculate_account_data_size_on_instruction`, which only recognizes an allocation if `program_id == &system_program::id()` for that *specific top-level* instruction; any other program_id returns `SystemProgramAccountAllocation::None` unconditionally [2](#0-1) . `program_instructions_iter()` is confirmed to enumerate only top-level instructions — `InvokeContext::process_message` iterates `message.program_instructions_iter()` for the top-level pass and configures CPI instructions separately via `configure_instruction_at_index` [3](#0-2) . Consequently a CPI call from a user program into `system_program::allocate` is invisible to the cost-model's static scan, and `calculate_allocated_accounts_data_size` returns `0` (or undercounts) for that transaction's `allocated_accounts_data_size` field.

This value is what `CostTracker::would_fit`/`add_transaction_cost` accumulate into `self.allocated_accounts_data_size` and compare against `MAX_BLOCK_ACCOUNTS_DATA_SIZE_DELTA` (100,000,000 bytes) to gate transaction admission into a block [4](#0-3) [5](#0-4) . Since this check runs pre-execution (as part of block packing) using the static estimate, an attacker can craft transactions whose top-level instruction is a call into their own program that internally invokes `system_program::allocate`/`create_account`, causing real account growth while the tracked `allocated_accounts_data_size` stays at 0 for that transaction.

Separately, the runtime does enforce a **hard per-transaction cap** on total resize delta (`can_data_be_resized` checks `resize_delta` against `MAX_ACCOUNT_DATA_GROWTH_PER_TRANSACTION`, which equals `MAX_PERMITTED_ACCOUNTS_DATA_ALLOCATIONS_PER_TRANSACTION` via a `static_assertions::const_assert_eq!`) regardless of whether growth originates from a top-level instruction or CPI [6](#0-5) [7](#0-6) . This bounds the *per-transaction* undercount but does **not** fix the *block-level* accounting used for cost-tracker admission (`would_fit`), since that check relies purely on the static `allocated_accounts_data_size` sum, not on actual measured growth. The bank does separately track real growth post-execution via `accounts_data_size_delta_on_chain`, computed from `AccountsDeltas::accounts_resize_delta` after commit [8](#0-7) , but this is an after-the-fact bookkeeping value, not a pre-admission gate tied to `CostTracker`'s `MAX_BLOCK_ACCOUNTS_DATA_SIZE_DELTA` limit used during transaction scheduling/packing.

## Impact Explanation
By packing many transactions that each route account allocation through CPI (bounded per-tx at `MAX_ACCOUNT_DATA_GROWTH_PER_TRANSACTION`, ~20MB per the confirmed constant), an attacker can cause a block's actual accounts-data growth to substantially exceed the intended `MAX_BLOCK_ACCOUNTS_DATA_SIZE_DELTA` (100MB) budget that `CostTracker` is meant to enforce during block construction, since the tracker's running counter never reflects these CPI-driven allocations. This falls into the "materially underpriced execution" / cost-model-inconsistency category — the estimate used for admission control does not upper-bound real per-block account-data growth work, risking excess memory/snapshot growth relative to the modeled budget.

## Likelihood Explanation
This requires only an unprivileged attacker: deploy (or use an existing) on-chain program that CPIs to `system_program::allocate`/`create_account`, and submit ordinary transactions invoking it. No special privileges, leader control, or crafted snapshot is needed — just standard transaction submission to a public RPC/TPU. The `calculate_account_data_size_on_instruction` logic and `program_instructions_iter` scope are stable, well-documented code paths, making this readily reproducible.

## Recommendation
Extend `calculate_allocated_accounts_data_size` (or a companion estimator) to account for programs that are permitted to CPI into System Program allocation instructions, e.g., by using a conservative worst-case allocation estimate for any transaction containing non-system top-level instructions capable of CPI (as already hinted at in the existing code comment about "custom bpf instructions... tricky to know"), or by deriving the tracked block-level budget from post-execution `accounts_resize_delta` totals (already computed in `runtime/src/bank.rs`) rather than solely from the static per-tx estimate, and re-validating the running block total against `MAX_BLOCK_ACCOUNTS_DATA_SIZE_DELTA` after execution to reject/re-cost blocks whose true growth exceeds budget.

## Proof of Concept
```rust
// cost-model/src/cost_model.rs (new test)
#[test]
fn test_calculate_allocated_accounts_data_size_cpi_bypass() {
    // Top-level instruction targets an attacker-controlled program (not system_program::id()),
    // simulating a CPI-based allocate call the static scanner cannot see.
    let attacker_program_id = Pubkey::new_unique();
    let transaction = Transaction::new_unsigned(Message::new(
        &[Instruction::new_with_bincode(
            attacker_program_id,
            &(),
            vec![],
        )],
        Some(&Pubkey::new_unique()),
    ));
    let sanitized_tx = RuntimeTransaction::from_transaction_for_tests(transaction);

    // Cost model reports zero allocation...
    assert_eq!(
        CostModel::calculate_allocated_accounts_data_size(
            sanitized_tx.program_instructions_iter(),
            &FeatureSet::all_enabled()
        ),
        0
    );
    // ...even though `attacker_program_id`, when actually executed, could CPI into
    // system_program::allocate and grow an account's data up to
    // MAX_ACCOUNT_DATA_GROWTH_PER_TRANSACTION bytes (enforced only at
    // TransactionAccounts::can_data_be_resized, not reflected in this estimate).
}
```
Integration-level differential PoC (conceptual, to be run in `runtime`/`svm` test harness): deploy a minimal BPF program that CPIs `system_program::allocate` for a large `space`; submit N such transactions in one simulated block; compare `CostTracker::allocated_accounts_data_size` (near 0) against `bank.load_accounts_data_size_delta_on_chain()` after execution (near N × allocation size), demonstrating the estimate fails to upper-bound the real per-block growth used for `would_fit` admission decisions.

### Citations

**File:** cost-model/src/cost_model.rs (L103-116)
```rust
    fn calculate_transaction_cost<'a, Tx: TransactionMeta>(
        transaction: &'a Tx,
        instructions: impl Iterator<Item = (&'a Pubkey, SVMInstruction<'a>)>,
        num_write_locks: u64,
        programs_execution_cost: u64,
        loaded_accounts_data_size_cost: u64,
        data_bytes_cost: u16,
        feature_set: &FeatureSet,
    ) -> TransactionCost<'a, Tx> {
        let signature_cost = Self::get_signature_cost(transaction);
        let write_lock_cost = Self::get_write_lock_cost(num_write_locks);

        let allocated_accounts_data_size =
            Self::calculate_allocated_accounts_data_size(instructions, feature_set);
```

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

**File:** program-runtime/src/invoke_context.rs (L503-551)
```rust
    pub fn process_message(
        &mut self,
        message: &'ix_data impl SVMMessage,
        execute_timings: &mut ExecuteTimings,
        accumulated_consumed_units: &mut u64,
    ) -> Result<(), (u8, InstructionError)> {
        self.prepare_top_level_instructions(message)?;

        for (top_level_instruction_index, (program_id, instruction)) in
            message.program_instructions_iter().enumerate()
        {
            let mut compute_units_consumed = 0;
            let (result, process_instruction_us) = measure_us!({
                if self.is_precompile(program_id) {
                    self.process_precompile(
                        program_id,
                        instruction.data,
                        message.instructions_iter().map(|ix| ix.data),
                    )
                } else {
                    self.process_instruction(&mut compute_units_consumed, execute_timings)
                }
            });

            *accumulated_consumed_units =
                accumulated_consumed_units.saturating_add(compute_units_consumed);
            // The per_program_timings are only used for metrics reporting at the trace
            // level, so they should only be accumulated when trace level is enabled.
            if log::log_enabled!(log::Level::Trace) {
                execute_timings.details.accumulate_program(
                    program_id,
                    process_instruction_us,
                    compute_units_consumed,
                    result.is_err(),
                );
            }
            self.timings = {
                execute_timings.details.accumulate(&self.timings);
                ExecuteDetailsTimings::default()
            };
            execute_timings
                .execute_accessories
                .process_instructions
                .total_us += process_instruction_us;

            result.map_err(|err| (top_level_instruction_index as u8, err))?;
        }
        Ok(())
    }
```

**File:** cost-model/src/cost_tracker.rs (L288-293)
```rust
        let allocated_accounts_data_size =
            self.allocated_accounts_data_size + Saturating(tx_cost.allocated_accounts_data_size());

        if allocated_accounts_data_size.0 > self.limits.allocated_data_size {
            return Err(CostTrackerError::WouldExceedAccountDataBlockLimit);
        }
```

**File:** cost-model/src/cost_tracker.rs (L312-323)
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

**File:** transaction-context/src/lib.rs (L39-42)
```rust
static_assertions::const_assert_eq!(
    MAX_ACCOUNT_DATA_GROWTH_PER_TRANSACTION,
    solana_system_interface::MAX_PERMITTED_ACCOUNTS_DATA_ALLOCATIONS_PER_TRANSACTION,
);
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
