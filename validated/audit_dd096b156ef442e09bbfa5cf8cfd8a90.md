### Title
CostTracker's per-block `allocated_accounts_data_size` budget is bypassed by ALT `ExtendLookupTable` realloc growth - (File: cost-model/src/cost_model.rs)

### Summary
`CostModel::calculate_account_data_size_on_deserialized_system_instruction` and its caller `calculate_account_data_size_on_instruction` only attribute account-data growth to `SystemInstruction::{CreateAccount, CreateAccountWithSeed, Allocate, AllocateWithSeed, CreateAccountAllowPrefund}` when `program_id == system_program::id()`; every other program, including the Address Lookup Table (ALT) native program, is unconditionally mapped to `SystemProgramAccountAllocation::None` [1](#0-0) . `ExtendLookupTable` (parsed by `parse_address_lookup_table`/`ProgramInstruction::ExtendLookupTable{new_addresses}`) grows the lookup table's real account data via a `realloc` performed by the ALT builtin, but because it is not a System Program instruction, `CostModel::calculate_allocated_accounts_data_size` counts 0 bytes for it [2](#0-1) . This zero-valued estimate feeds directly into `CostTracker::try_add`, which checks it against the block-wide `MAX_BLOCK_ACCOUNTS_DATA_SIZE_DELTA` (100,000,000 bytes) admission limit [3](#0-2) , so an attacker can drive real per-block account-data growth past that intended cap while the tracker still reports low/zero usage.

### Finding Description
`CostModel::calculate_allocated_accounts_data_size` is the sole source of `TransactionCost::allocated_accounts_data_size` [4](#0-3) , which `CostTracker::try_add` accumulates and gates against `self.limits.allocated_data_size` (default `MAX_BLOCK_ACCOUNTS_DATA_SIZE_DELTA`, documented as "the maximum allowed size … that accounts data can grow, per block") [5](#0-4) [6](#0-5) .

The estimator, however, only inspects instructions targeting the System Program:
```
fn calculate_account_data_size_on_instruction(...) -> SystemProgramAccountAllocation {
    if program_id == &system_program::id() { ... } else { SystemProgramAccountAllocation::None }
}
``` [1](#0-0) 

An unprivileged attacker who authors a lookup table (`CreateLookupTable`) can repeatedly call `ExtendLookupTable` (up to 20 addresses = 640 bytes per call, as parsed in `transaction-status/src/parse_address_lookup_table.rs`) [7](#0-6) . The ALT program's `program_id` is `address_lookup_table::program::id()`, not `system_program::id()`, so every such instruction returns `SystemProgramAccountAllocation::None`, contributing 0 to `allocated_accounts_data_size` regardless of how much real realloc growth occurs. By packing many `ExtendLookupTable` transactions (or several extend instructions per transaction) into a single block, the attacker can cause real account-data growth to exceed `MAX_BLOCK_ACCOUNTS_DATA_SIZE_DELTA` while `CostTracker::allocated_accounts_data_size` still reports well under the limit, so `try_add` never returns `WouldExceedAccountDataBlockLimit` for this cause.

Scope note: this does not bypass consensus-level safety limits. Real per-transaction growth is independently bounded by `TransactionAccounts::can_data_be_resized`, which enforces `MAX_ACCOUNT_DATA_GROWTH_PER_TRANSACTION` (20 MiB) against the actual `resize_delta`, irrespective of which program performs the resize [8](#0-7) , and the Bank tracks true on-chain accounts-data-size delta from the *actual* `accounts_resize_delta` recorded during execution (not the cost-model estimate) via `Bank::update_accounts_data_size_delta_on_chain` [9](#0-8) . So the vulnerability is scoped specifically to the `CostTracker`'s block-packing/admission heuristic (`MAX_BLOCK_ACCOUNTS_DATA_SIZE_DELTA`), not to a hard consensus/state-integrity invariant.

### Impact Explanation
This is a real underpricing of declared vs. actual work in the leader's block-building admission control: the `MAX_BLOCK_ACCOUNTS_DATA_SIZE_DELTA` heuristic exists specifically to bound "the maximum size of new allocations per block" for performance/DoS-avoidance reasons (e.g., limiting per-slot realloc/memcpy and AccountsDB write-amplification work). Because ALT-driven growth is invisible to the cost model, a leader packing transactions based on this budget can unknowingly (or an attacker deliberately spamming `ExtendLookupTable`) admit far more real account-data growth per block than the model believes, undermining the intended cap on per-block realloc work. This matches the "cost/fee underpricing" bounty category (declared cost-model estimates fail to upper-bound real work performed), though its blast radius is bounded by the hard per-transaction `MAX_ACCOUNT_DATA_GROWTH_PER_TRANSACTION` check and by the true `accounts_data_size` tracking in `Bank`, which are unaffected by this bug.

### Likelihood Explanation
Fully attacker-reachable with no special privileges: `CreateLookupTable` and `ExtendLookupTable` are permissionless (subject to the attacker being their own lookup-table authority), can be submitted repeatedly across many transactions within a single slot, and each call can add up to 20 new addresses (640 bytes) of real growth per instruction. This is trivially and repeatably reproducible via ordinary RPC/TPU submission, matching the described preconditions exactly.

### Recommendation
Extend `CostModel::calculate_account_data_size_on_instruction` (and `calculate_account_data_size_on_deserialized_system_instruction`) to also recognize allocation-causing instructions from other builtin programs that perform `realloc`, in particular `address_lookup_table::instruction::ProgramInstruction::ExtendLookupTable`, attributing `new_addresses.len() * size_of::<Pubkey>()` bytes to `allocated_accounts_data_size`. More generally, consider deriving the per-block "allocated data size" admission-control budget from a program-agnostic mechanism (e.g., a per-instruction declared max resize supplied by all builtin programs, or from the actually-observed `accounts_resize_delta` bookkeeping used by `TransactionAccounts`) rather than a hardcoded match on System Program variants, so that new allocation-capable builtins don't silently escape the estimate.

### Proof of Concept
```rust
// cost-model/src/cost_model.rs (new test)
#[test]
fn test_calculate_allocated_accounts_data_size_ignores_alt_extend() {
    use solana_address_lookup_table_interface::instruction::extend_lookup_table;

    let payer = Pubkey::new_unique();
    let lookup_table = Pubkey::new_unique();
    let authority = Keypair::new();
    let new_addresses: Vec<Pubkey> = (0..20).map(|_| Pubkey::new_unique()).collect();
    let expected_growth = (new_addresses.len() * std::mem::size_of::<Pubkey>()) as u64; // 640 bytes

    let ix = extend_lookup_table(
        lookup_table,
        authority.pubkey(),
        Some(payer),
        new_addresses,
    );
    let transaction = Transaction::new_unsigned(Message::new(&[ix], Some(&payer)));
    let sanitized_tx = RuntimeTransaction::from_transaction_for_tests(transaction);

    let allocated = CostModel::calculate_allocated_accounts_data_size(
        sanitized_tx.program_instructions_iter(),
        &FeatureSet::all_enabled(),
    );

    // BUG: cost model attributes zero bytes to a real 640-byte ALT realloc growth.
    assert_eq!(allocated, 0);
    assert!(
        allocated < expected_growth,
        "cost model underprices real ALT account growth: estimated {allocated}, actual {expected_growth}"
    );
}
```
Extended integration-level PoC: execute the transaction against a `Bank`, measure `bank.load_accounts_data_size_delta_on_chain()` before/after (real growth, ~640 bytes per call), and compare against `CostModel::calculate_cost(&tx, ...).allocated_accounts_data_size()` (0) summed across N repeated `ExtendLookupTable` transactions within one simulated block; assert that `CostTracker::try_add` never rejects with `WouldExceedAccountDataBlockLimit` even once cumulative real growth (`N * 640`) exceeds `MAX_BLOCK_ACCOUNTS_DATA_SIZE_DELTA`, demonstrating the tracked estimate diverges from real per-block account growth.

### Citations

**File:** cost-model/src/cost_model.rs (L103-127)
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

        TransactionCost {
            transaction,
            signature_cost,
            write_lock_cost,
            data_bytes_cost,
            programs_execution_cost,
            loaded_accounts_data_size_cost,
            allocated_accounts_data_size,
        }
    }
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

**File:** cost-model/src/cost_model.rs (L263-301)
```rust
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

**File:** cost-model/src/cost_tracker.rs (L85-94)
```rust
impl Default for CostTrackerLimits {
    fn default() -> Self {
        const _: () = assert!(MAX_WRITABLE_ACCOUNT_UNITS <= MAX_BLOCK_UNITS);
        Self {
            account_cost: MAX_WRITABLE_ACCOUNT_UNITS,
            block_cost: MAX_BLOCK_UNITS,
            allocated_data_size: MAX_BLOCK_ACCOUNTS_DATA_SIZE_DELTA,
        }
    }
}
```

**File:** cost-model/src/cost_tracker.rs (L186-193)
```rust
        }

        let allocated_accounts_data_size =
            self.allocated_accounts_data_size + Saturating(tx_cost.allocated_accounts_data_size());

        if allocated_accounts_data_size.0 > self.limits.allocated_data_size {
            return Err(CostTrackerError::WouldExceedAccountDataBlockLimit);
        }
```

**File:** cost-model/src/block_cost_limits.rs (L35-37)
```rust
/// The maximum allowed size, in bytes, that accounts data can grow, per block.
/// This can also be thought of as the maximum size of new allocations per block.
pub const MAX_BLOCK_ACCOUNTS_DATA_SIZE_DELTA: u64 = 100_000_000;
```

**File:** transaction-status/src/parse_address_lookup_table.rs (L56-82)
```rust
        ProgramInstruction::ExtendLookupTable { new_addresses } => {
            check_num_address_lookup_table_accounts(&instruction.accounts, 2)?;
            let new_addresses: Vec<String> = new_addresses
                .into_iter()
                .map(|address| address.to_string())
                .collect();
            let mut value = json!({
                "lookupTableAccount": account_keys[instruction.accounts[0] as usize].to_string(),
                "lookupTableAuthority": account_keys[instruction.accounts[1] as usize].to_string(),
                "newAddresses": new_addresses,
            });
            let map = value.as_object_mut().unwrap();
            if instruction.accounts.len() >= 4 {
                map.insert(
                    "payerAccount".to_string(),
                    json!(account_keys[instruction.accounts[2] as usize].to_string()),
                );
                map.insert(
                    "systemProgram".to_string(),
                    json!(account_keys[instruction.accounts[3] as usize].to_string()),
                );
            }
            Ok(ParsedInstructionEnum {
                instruction_type: "extendLookupTable".to_string(),
                info: value,
            })
        }
```

**File:** transaction-context/src/transaction_accounts.rs (L297-326)
```rust
    pub(crate) fn update_accounts_resize_delta(
        &self,
        old_len: usize,
        new_len: usize,
    ) -> Result<(), InstructionError> {
        let accounts_resize_delta = self.resize_delta.get();
        self.resize_delta.set(
            accounts_resize_delta.saturating_add((new_len as i64).saturating_sub(old_len as i64)),
        );
        Ok(())
    }

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
