### Title
Per-instruction account serialization cost is unbounded by `loaded_accounts_data_size` charge, allowing CU-underpriced memcpy/alloc amplification - ([File: program-runtime/src/serialization.rs])

### Summary
`serialize_parameters_for_abiv1` allocates a fresh `AlignedMemory` buffer and copies `data_len + MAX_PERMITTED_DATA_INCREASE (+ alignment)` bytes for every non-duplicate instruction account, on *every* top-level instruction invocation (and every CPI) in a transaction. The compute-cost model, however, only charges `loaded_accounts_data_size` once per unique account for the whole transaction (`svm/src/account_loader.rs::load_transaction_accounts` / `LoadedTransactionDataSize::increase_calculated_data_size`), and prices actual program execution purely via the user-declared `compute_unit_limit`, which is independent of account size. An attacker can therefore reference the same large account across many cheap-CU top-level instructions in one transaction to multiply real memcpy/allocation work far beyond what is charged.

### Finding Description
`Serializer::write_account` in `program-runtime/src/serialization.rs` (lines 146-208) always reserves `MAX_PERMITTED_DATA_INCREASE` (10,240 bytes) of realloc padding plus alignment padding for every non-duplicate instruction account, and `serialize_parameters_for_abiv1` (lines 490-610) computes `size += data_len + MAX_PERMITTED_DATA_INCREASE + align_offset` per non-duplicate account before allocating the buffer with `AlignedMemory::with_capacity(size)` and performing `write_all`/`fill_write` memcpy operations. Deduplication (`SerializeAccount::Duplicate`, cheap `size += 7`/`size += 1`) only applies to accounts repeated *within a single instruction's* account list (`instruction_context.is_instruction_account_duplicate`); it does not apply across different top-level instructions in the same transaction.

Meanwhile, `svm/src/account_loader.rs::load_transaction_accounts` (lines 522-620) computes `loaded_accounts_data_size` by iterating the transaction's unique `account_keys` exactly once (`TRANSACTION_ACCOUNT_BASE_SIZE + account.data().len()` per unique account, via `collect_loaded_account`/`increase_calculated_data_size`, lines 542-589), regardless of how many instructions in the message reference that account. This value is what `CostModel::calculate_loaded_accounts_data_size_cost` (`cost-model/src/cost_model.rs` lines 196-201) prices, and it is charged only once per transaction, not once per instruction occurrence.

Separately, `programs_execution_cost` in the cost model (`get_estimated_execution_cost`, lines 158-178) is simply `config.compute_unit_limit` — a value the attacker fully controls via `ComputeBudgetInstruction::SetComputeUnitLimit` — and is completely decoupled from account data size or instruction count beyond the attacker's own declaration.

Consequently, an attacker can construct a single transaction with N top-level instructions (bounded mainly by the 1232-byte packet size, since each additional instruction needs only a few bytes: program-id index, one account index, minimal/zero instruction data), each instruction listing the *same* large, pre-existing account (which need not be writable — the `MAX_PERMITTED_DATA_INCREASE` padding and full data memcpy happen for read-only accounts too, since `write_account` does not branch on writability). Each of the N instructions invokes a trivial no-op-like program, so `programs_execution_cost` can be declared very low (e.g., far under `DEFAULT_INSTRUCTION_COMPUTE_UNIT_LIMIT`), while `loaded_accounts_data_size` is charged exactly once for that account regardless of N. Yet `serialize_parameters` is called once per top-level instruction execution (see call sites in `programs/bpf_loader/src/lib.rs` invoking `serialize_parameters`), performing a full `AlignedMemory` allocation and memcpy of the account's data + 10 KB padding N times. Real memcpy/alloc work thus scales as O(N × data_len), while the charged cost model components (`loaded_accounts_data_size_cost`, `programs_execution_cost`) scale as O(data_len) and O(N) independently but not O(N × data_len).

### Impact Explanation
This is materially underpriced execution: a validator/leader that includes such a transaction performs far more per-transaction CPU work (allocation + memcpy proportional to N × account size) than what the transaction's charged cost-model units (CU limit, loaded-accounts-data-size cost) represent. Packed across many transactions in a block, this can be used to inflate real per-block processing time relative to the cost-model-derived block capacity accounting, degrading validator/leader throughput — matching the "materially underpriced execution" / cost-model bypass bounty category referenced in the question (declared compute/loaded-accounts-data-size failing to upper-bound real work performed).

### Likelihood Explanation
This requires no special privilege: any user can submit an ordinary transaction with many instructions, each referencing an account they don't even need to own or write to (any existing sizable account works, including their own account created ahead of time via `CreateAccount`/`Allocate` up to `MAX_PERMITTED_DATA_LENGTH`). It requires no leader/validator control, no leaked keys, and no snapshot manipulation — only careful packing of a compact transaction to maximize `N` and minimize declared CU per instruction. The construction is fully reproducible and deterministic given the serialization code's known formula (`data_len + MAX_PERMITTED_DATA_INCREASE + align_offset` per account per instruction occurrence).

### Recommendation
Track and charge `loaded_accounts_data_size` (or an analogous "serialization work" cost) per instruction-account *occurrence* across the whole transaction (i.e., multiply by the number of times an account appears across the instruction list, not just once per unique account), or otherwise incorporate `MAX_ACCOUNTS_PER_INSTRUCTION`/instruction-count-weighted account-size cost into `CostModel::calculate_loaded_accounts_data_size_cost`/`get_estimated_execution_cost` so that repeatedly listing the same large account across many cheap instructions is priced proportionally to the real serialization work performed in `serialize_parameters_for_abiv1`.

### Proof of Concept
Integration/benchmark test plan (Rust, using `program-runtime`/`svm` test harnesses):
1. Create a large (e.g., 10 MB, near `MAX_PERMITTED_DATA_LENGTH`) account, `big_account`, owned by a trivial no-op BPF program (`programs/sbf/rust/noop`).
2. Build a transaction message with N top-level instructions (e.g., N ≈ 200, fitting within 1232-byte packet size), each invoking the no-op program with `big_account` as its sole (read-only) instruction account, and set `ComputeBudgetInstruction::SetComputeUnitLimit(N * small_constant)` so total `programs_execution_cost` and `loaded_accounts_data_size_cost` (computed once for `big_account`) remain small.
3. Instrument `serialize_parameters_for_abiv1` (or wrap `AlignedMemory::with_capacity`/`write_all`) to count total bytes allocated/copied across the whole transaction's execution.
4. Assert: `total_bytes_copied_across_all_instructions ≈ N * (data_len + MAX_PERMITTED_DATA_INCREASE)`, while `CostModel::calculate_cost(&tx, ...).loaded_accounts_data_size_cost() + programs_execution_cost()` remains bounded by a value computed from `data_len` and `N * small_constant` only — i.e., `charge < measured_work` for sufficiently large N, violating the "charge >= measured work" invariant.
5. Compare wall-clock time of executing this transaction versus a baseline transaction with equivalent `programs_execution_cost`/`loaded_accounts_data_size_cost` but only 1 instruction, confirming a near-linear-in-N blowup in wall time unaccounted for by cost-model charges. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** program-runtime/src/serialization.rs (L146-208)
```rust
    fn write_account(
        &mut self,
        account: &mut BorrowedInstructionAccount<'_, '_>,
    ) -> Result<u64, InstructionError> {
        if !self.virtual_address_space_adjustments {
            let vm_data_addr = self.vaddr.saturating_add(self.buffer.len() as u64);
            self.write_all(account.get_data());
            if !self.is_loader_v1 {
                let align_offset =
                    (account.get_data().len() as *const u8).align_offset(BPF_ALIGN_OF_U128);
                self.fill_write(MAX_PERMITTED_DATA_INCREASE + align_offset, 0)
                    .map_err(|_| InstructionError::InvalidArgument)?;
            }
            Ok(vm_data_addr)
        } else {
            self.push_region();
            let vm_data_addr = self.vaddr;
            if !self.account_data_direct_mapping {
                self.write_all(account.get_data());
                if !self.is_loader_v1 {
                    self.fill_write(MAX_PERMITTED_DATA_INCREASE, 0)
                        .map_err(|_| InstructionError::InvalidArgument)?;
                }
            }
            let address_space_reserved_for_account = if !self.is_loader_v1 {
                account
                    .get_data()
                    .len()
                    .saturating_add(MAX_PERMITTED_DATA_INCREASE)
            } else {
                account.get_data().len()
            };
            if address_space_reserved_for_account > 0 {
                if !self.account_data_direct_mapping {
                    self.push_region();
                    let region = self.regions.last_mut().unwrap();
                    modify_memory_region_of_account(account, region);
                } else {
                    let new_region = create_memory_region_of_account(account, self.vaddr)?;
                    self.vaddr += address_space_reserved_for_account as u64;
                    self.regions.push(new_region);
                }
            }
            if !self.is_loader_v1 {
                let align_offset =
                    (account.get_data().len() as *const u8).align_offset(BPF_ALIGN_OF_U128);
                if !self.account_data_direct_mapping {
                    self.fill_write(align_offset, 0)
                        .map_err(|_| InstructionError::InvalidArgument)?;
                } else {
                    // The deserialization code is going to align the vm_addr to
                    // BPF_ALIGN_OF_U128. Always add one BPF_ALIGN_OF_U128 worth of
                    // padding and shift the start of the next region, so that once
                    // vm_addr is aligned, the corresponding host_addr is aligned
                    // too.
                    self.fill_write(BPF_ALIGN_OF_U128, 0)
                        .map_err(|_| InstructionError::InvalidArgument)?;
                    self.region_start += BPF_ALIGN_OF_U128.saturating_sub(align_offset);
                }
            }
            Ok(vm_data_addr)
        }
    }
```

**File:** program-runtime/src/serialization.rs (L506-533)
```rust
    let mut accounts_metadata = Vec::with_capacity(accounts.len());
    // Calculate size in order to alloc once
    let mut size = size_of::<u64>();
    for account in &accounts {
        size += 1; // dup
        match account {
            SerializeAccount::Duplicate(_) => size += 7, // padding to 64-bit aligned
            SerializeAccount::Account(_, account) => {
                let data_len = account.get_data().len();
                size += size_of::<u8>() // is_signer
                + size_of::<u8>() // is_writable
                + size_of::<u8>() // executable
                + size_of::<u32>() // original_data_len
                + size_of::<Pubkey>()  // key
                + size_of::<Pubkey>() // owner
                + size_of::<u64>()  // lamports
                + size_of::<u64>()  // data len
                + size_of::<u64>(); // rent epoch
                if !(virtual_address_space_adjustments && account_data_direct_mapping) {
                    size += data_len
                        + MAX_PERMITTED_DATA_INCREASE
                        + (data_len as *const u8).align_offset(BPF_ALIGN_OF_U128);
                } else {
                    size += BPF_ALIGN_OF_U128;
                }
            }
        }
    }
```

**File:** svm/src/account_loader.rs (L480-520)
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
}

impl From<LoadedTransactionDataSize> for u32 {
    fn from(value: LoadedTransactionDataSize) -> Self {
        value
            .loaded_accounts_data_size
            .min(value.requested_loaded_accounts_data_size_limit)
    }
}
```

**File:** svm/src/account_loader.rs (L542-589)
```rust
    let mut collect_loaded_account =
        |account_loader: &mut AccountLoader<CB>, key: &Pubkey, loaded_account| -> Result<()> {
            let LoadedTransactionAccount {
                account,
                loaded_size,
            } = loaded_account;

            loaded_tx_data_size.increase_calculated_data_size(loaded_size, error_metrics)?;

            // This has been annotated branch-by-branch because collapsing the logic is infeasible.
            // Its purpose is to ensure programdata accounts are counted once and *only* once per
            // transaction. By checking account_keys, we never double-count a programdata account
            // that was explicitly included in the transaction. We also use a hashset to gracefully
            // handle cases that LoaderV3 presumably makes impossible, such as self-referential
            // program accounts or multiply-referenced programdata accounts, for added safety.
            //
            // If in the future LoaderV3 programs are migrated to LoaderV4, this entire code block
            // can be deleted.
            //
            // If this is a valid LoaderV3 program...
            if bpf_loader_upgradeable::check_id(account.owner())
                && let Ok(UpgradeableLoaderState::Program {
                    programdata_address,
                }) = bincode::deserialize(account.data())
            {
                // ...its programdata was not already counted and will not later be counted...
                if !account_keys.iter().any(|key| programdata_address == *key)
                    && !additional_loaded_accounts.contains(&programdata_address)
                {
                    // ...and the programdata account exists (if it doesn't, it is *not* a load failure)...
                    if let Some(programdata_account) =
                        account_loader.load_account(&programdata_address)
                    {
                        // ...count programdata toward this transaction's total size.
                        loaded_tx_data_size.increase_calculated_data_size(
                            TRANSACTION_ACCOUNT_BASE_SIZE
                                .saturating_add(programdata_account.data().len()),
                            error_metrics,
                        )?;
                        additional_loaded_accounts.insert(programdata_address);
                    }
                }
            }

            loaded_transaction_accounts.push((*key, account));

            Ok(())
        };
```

**File:** cost-model/src/cost_model.rs (L158-201)
```rust
    /// Return (programs_execution_cost, loaded_accounts_data_size_cost)
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

    /// Return the instruction data bytes cost.
    fn get_instructions_data_cost(transaction: &impl TransactionMeta) -> u16 {
        transaction.instruction_data_len() / (INSTRUCTION_DATA_BYTES_COST as u16)
    }

    /// Compute the number of pages needed to contain provided number of bytes.
    fn calculate_pages_for_bytes(bytes: u32) -> u64 {
        u64::from(bytes)
            .saturating_add(ACCOUNT_DATA_COST_PAGE_SIZE.saturating_sub(1))
            .saturating_div(ACCOUNT_DATA_COST_PAGE_SIZE)
    }

    pub fn calculate_pages_cost(num_pages: u64) -> u64 {
        num_pages.saturating_mul(DEFAULT_HEAP_COST)
    }

    pub fn calculate_loaded_accounts_data_size_cost(
        loaded_accounts_data_size: u32,
        _feature_set: &FeatureSet,
    ) -> u64 {
        Self::calculate_pages_cost(Self::calculate_pages_for_bytes(loaded_accounts_data_size))
    }
```
