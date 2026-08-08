### Title
Flat, size-independent builtin compute cost for BPF Loader v3 deployment underprices ELF loading/verification/JIT compilation - (File: `programs/bpf_loader/src/lib.rs`, `program-runtime/src/deploy.rs`)

### Summary
The external report describes an Ethereum-side scaling issue: `TokenFactory` deployment (17.1M gas) exceeds the mainnet block gas limit (15M), because Ethereum meters and charges gas proportional to the actual computational/storage cost of contract deployment (bytecode parsing, storage writes), and it was fixed by shrinking the constructor's real gas usage below the 15M cap. The Solana/agave analog concerns whether the equivalent "cost of deployment" — the CPU work spent loading, verifying, and JIT-compiling a program's ELF — is actually metered and charged proportionally to the work performed, the way EVM gas is. It is not: the BPF Loader v3 `DeployWithMaxDataLen`/`Upgrade`/`ExtendProgramData` instructions charge a fixed builtin compute cost regardless of the size of the ELF being loaded/verified/JIT-compiled.

### Finding Description
In `programs/bpf_loader/src/lib.rs`, the compute cost for BPF Upgradeable Loader instructions (including `DeployWithMaxDataLen`) is a hardcoded constant: [1](#0-0) 

This fixed cost (2,370 CU) is charged as the "builtin instruction" cost independent of the size of the program being deployed, confirmed by the cost-adjustment test harness which hardcodes `UPGRADEABLE_LOADER_COMPUTE_UNITS` as the expected total execution cost for a `deploy_with_max_data_len` instruction: [2](#0-1) 

However, the actual work performed by this instruction inside `deploy_program!` (`program-runtime/src/deploy.rs`) is proportional to the size of the program: it registers syscalls, loads the ELF (`Executable::load`), runs the full `RequisiteVerifier` over the bytecode, and (via `ProgramCacheEntry::reload`) JIT-compiles the executable — all operations whose cost scales with ELF/program size, up to `MAX_PERMITTED_DATA_LENGTH` (10 MiB): [3](#0-2) [4](#0-3) 

The instruction itself (`DeployWithMaxDataLen`) validates `programdata_len <= MAX_PERMITTED_DATA_LENGTH` but does not scale the charged compute cost with `max_data_len`/`buffer_data_len`: [5](#0-4) 

Separately, the cost model's `loaded_accounts_data_size_cost` is derived from the transaction's *requested* `loaded_accounts_data_size_limit` (a user-supplied `ComputeBudgetInstruction`), not from the actual size of the buffer/programdata account being verified: [6](#0-5) [7](#0-6) 

This mirrors the reported bug class exactly: just as Ethereum's fixed block gas limit failed to reflect (and thus cap) the true resource cost of a large deployment, agave's BPF Loader v3 charges a flat, size-independent compute-unit fee for deployment while the real CPU cost of ELF parsing, `RequisiteVerifier` verification, and JIT compilation grows with program size (up to 10 MiB). Because compute-unit price/limit determine transaction priority fees and scheduling cost, an attacker can submit maximum-size program deployments (already staged into a buffer account via prior `Write` instructions) for the same fixed 2,370 CU (or whatever small `SetComputeUnitLimit` is set) as a trivial deployment, causing validators to spend disproportionate wall-clock time loading/verifying/JIT-compiling large ELFs relative to the CU fee collected and relative to the cost-model's estimate used for block-packing/scheduling.

### Impact Explanation
This is a cost-model/compute-budget underpricing issue in the SVM loading path reachable by any unprivileged user who can afford rent for a ~10 MiB buffer account and the associated `Write` transactions. Because the compute cost charged for the final deploy/upgrade instruction does not scale with program size, the transaction-scheduler/cost-model materially underestimates and undercharges the CPU cost of large-program verification and JIT compilation, which can be used to consume disproportionate leader/validator processing time per unit of declared/paid compute, degrading the fairness and predictability of the cost model that block-packing and CU-based fee/priority mechanisms rely on.

### Likelihood Explanation
Reaching this path requires no special privileges — any signer with sufficient lamports for rent-exempt buffer/program-data accounts and transaction fees can create a buffer up to `MAX_PERMITTED_DATA_LENGTH`, write it via ordinary `Write` instructions, and issue a single `DeployWithMaxDataLen`/`Upgrade`/`ExtendProgramData` instruction that is charged the fixed builtin cost shown above. The relevant code paths (`programs/bpf_loader/src/lib.rs`, `program-runtime/src/deploy.rs`) are unprivileged, production, in-scope SVM/cost-model code, not sBPF-interpreter or Loader V4 internals excluded by SECURITY.md.

### Recommendation
Scale the compute-unit cost charged for BPF Loader v3 `DeployWithMaxDataLen`/`Upgrade`/`ExtendProgramData` (and the cost-model's static/dynamic execution-cost estimate for these instructions) proportionally to the size of the program data being loaded, verified, and JIT-compiled, similar to how `loaded_accounts_data_size_cost` scales with account data size elsewhere in the cost model (`cost-model/src/cost_model.rs`). This ensures compute-unit pricing reflects the true, size-dependent CPU cost of deployment, analogous to how the reported Ethereum fix reduced `TokenFactory`'s real gas cost to fit within the metered/enforced block gas limit.

### Proof of Concept
1. Build (or reuse) an ELF close to `MAX_PERMITTED_DATA_LENGTH` (10 MiB) that passes `RequisiteVerifier` but is maximally complex to verify/JIT-compile (e.g., densely packed valid instructions maximizing verifier and JIT work).
2. Fund a payer account and create a `Buffer` account sized to hold the ELF (rent-exempt), then submit the required chain of `Write` instructions to populate it (standard CLI deploy flow, as in `cli/src/program.rs::do_process_program_deploy`) — see chunked writes at `cli/src/program.rs` lines 2605-2654.
3. Submit a final `DeployWithMaxDataLen` transaction with `compute_unit_limit` set at or near `UPGRADEABLE_LOADER_COMPUTE_UNITS` (2,370) plus minor CPI overhead, as validated by `core/tests/scheduler_cost_adjustment.rs::test_builtin_ix_cost_adjustment_with_bpf_v3_no_cu_limit` (lines 318-334), which asserts the entire deploy instruction — regardless of program size — costs exactly `UPGRADEABLE_LOADER_COMPUTE_UNITS` (2,370 CU) plus the CPI'd `system_processor::DEFAULT_COMPUTE_UNITS`.
4. Measure wall-clock time spent inside `deploy_program` (`program-runtime/src/deploy.rs` lines 46-128) for the large ELF versus a minimal ELF at the same fixed CU cost, demonstrating the disparity between charged compute units and actual CPU work performed (ELF load + `RequisiteVerifier` + JIT compile in `ProgramCacheEntry::new_internal`, `program-runtime/src/program_cache_entry.rs` lines 241-279).

Note: I was unable to directly verify from the index whether any additional, size-scaled cost is applied elsewhere in the scheduler/cost model specifically for BPF Loader v3 deploy instructions beyond `loaded_accounts_data_size_cost` (which depends on the user-declared limit, not actual verified bytes) — a Devin session with full repo access would be needed to confirm there is no other size-proportional charge applied at commit/scheduling time before treating the underpricing as fully unmitigated in production.

### Citations

**File:** programs/bpf_loader/src/lib.rs (L32-37)
```rust
#[cfg_attr(feature = "svm-internal", qualifiers(pub))]
const DEFAULT_LOADER_COMPUTE_UNITS: u64 = 570;
#[cfg_attr(feature = "svm-internal", qualifiers(pub))]
const DEPRECATED_LOADER_COMPUTE_UNITS: u64 = 1_140;
#[cfg_attr(feature = "svm-internal", qualifiers(pub))]
const UPGRADEABLE_LOADER_COMPUTE_UNITS: u64 = 2_370;
```

**File:** programs/bpf_loader/src/lib.rs (L256-277)
```rust
            let buffer_data_offset = UpgradeableLoaderState::size_of_buffer_metadata();
            let buffer_data_len = buffer.get_data().len().saturating_sub(buffer_data_offset);
            let programdata_data_offset = UpgradeableLoaderState::size_of_programdata_metadata();
            let programdata_len = UpgradeableLoaderState::size_of_programdata(max_data_len);
            if buffer.get_data().len() < UpgradeableLoaderState::size_of_buffer_metadata()
                || buffer_data_len == 0
            {
                ic_logger_msg!(log_collector, "Buffer account too small");
                return Err(InstructionError::InvalidAccountData);
            }
            drop(buffer);
            if max_data_len < buffer_data_len {
                ic_logger_msg!(
                    log_collector,
                    "Max data length is too small to hold Buffer data"
                );
                return Err(InstructionError::AccountDataTooSmall);
            }
            if programdata_len > MAX_PERMITTED_DATA_LENGTH as usize {
                ic_logger_msg!(log_collector, "Max data length is too large");
                return Err(InstructionError::InvalidArgument);
            }
```

**File:** core/tests/scheduler_cost_adjustment.rs (L318-334)
```rust
#[test]
fn test_builtin_ix_cost_adjustment_with_bpf_v3_no_cu_limit() {
    // A System & BPF Loader v3 ix. The latter CPIs into System.
    // Cost model & Compute budget: reserve/allocate default CU for 1 builtin
    // VM Execution: consume CUs for 1 BPF_L and 1 System (CPI-ed 1 time), then succeed
    // Result: adjustment = 3_000 - 2_370 - 150 = 480
    let expected = TestResult {
        cost_adjustment: MAX_BUILTIN_ALLOCATION_COMPUTE_UNIT_LIMIT as i64
            - solana_bpf_loader_program::UPGRADEABLE_LOADER_COMPUTE_UNITS as i64
            - solana_system_program::system_processor::DEFAULT_COMPUTE_UNITS as i64,
        execution_status: Ok(()),
    };

    let mut test_setup = TestSetup::new();
    let ix = test_setup.deploy_with_max_data_len_ix();
    assert_eq!(expected, test_setup.execute_test_transaction(&[ix]));
}
```

**File:** program-runtime/src/deploy.rs (L46-128)
```rust
/// Directly deploy a program using a provided invoke context.
/// This function should only be invoked from the runtime, since it does not
/// provide any account loads or checks.
#[allow(clippy::too_many_arguments)]
pub fn deploy_program(
    log_collector: Option<Rc<RefCell<LogCollector>>>,
    #[cfg(feature = "metrics")] load_program_metrics: &mut LoadProgramMetrics,
    program_cache_for_tx_batch: &mut ProgramCacheForTxBatch,
    program_runtime_environment: ProgramRuntimeEnvironment,
    disable_sbpf_v0_v1_v2_deployment: bool,
    program_id: &Pubkey,
    loader_key: &Pubkey,
    programdata: &[u8],
    deployment_slot: Slot,
) -> Result<(), InstructionError> {
    #[cfg(feature = "metrics")]
    let mut register_syscalls_time = Measure::start("register_syscalls_time");
    let deployment_program_runtime_environment = morph_into_deployment_environment(
        ProgramRuntimeEnvironment::clone(&program_runtime_environment),
        disable_sbpf_v0_v1_v2_deployment,
    )
    .map_err(|e| {
        ic_logger_msg!(log_collector, "Failed to register syscalls: {}", e);
        InstructionError::ProgramEnvironmentSetupFailure
    })?;
    #[cfg(feature = "metrics")]
    {
        register_syscalls_time.stop();
        load_program_metrics.register_syscalls_us = register_syscalls_time.as_us();
    }
    // Verify using stricter deployment_program_runtime_environment
    #[cfg(feature = "metrics")]
    let mut load_elf_time = Measure::start("load_elf_time");
    let executable = Executable::<InvokeContext>::load(
        programdata,
        Arc::new(deployment_program_runtime_environment),
    )
    .map_err(|err| {
        ic_logger_msg!(log_collector, "{}", err);
        InstructionError::InvalidAccountData
    })?;
    #[cfg(feature = "metrics")]
    {
        load_elf_time.stop();
        load_program_metrics.load_elf_us = load_elf_time.as_us();
    }
    #[cfg(feature = "metrics")]
    let mut verify_code_time = Measure::start("verify_code_time");
    executable.verify::<RequisiteVerifier>().map_err(|err| {
        ic_logger_msg!(log_collector, "{}", err);
        InstructionError::InvalidAccountData
    })?;
    #[cfg(feature = "metrics")]
    {
        verify_code_time.stop();
        load_program_metrics.verify_code_us = verify_code_time.as_us();
    }
    // Reload but with program_runtime_environment
    let executor = unsafe {
        // SAFETY: The executable has been verified just above.
        ProgramCacheEntry::reload(
            loader_key,
            program_runtime_environment,
            deployment_slot,
            programdata,
            #[cfg(feature = "metrics")]
            load_program_metrics,
        )
    }
    .map_err(|err| {
        ic_logger_msg!(log_collector, "{}", err);
        InstructionError::InvalidAccountData
    })?;
    if let Some(old_entry) = program_cache_for_tx_batch.find(program_id) {
        executor.stats.merge_from(&old_entry.stats);
    }
    #[cfg(feature = "metrics")]
    {
        load_program_metrics.program_id = program_id.to_string();
    }
    program_cache_for_tx_batch.store_modified_entry(*program_id, Arc::new(executor));
    Ok(())
}
```

**File:** program-runtime/src/program_cache_entry.rs (L241-279)
```rust
    fn new_internal(
        loader_key: &Pubkey,
        program_runtime_environment: ProgramRuntimeEnvironment,
        deployment_slot: Slot,
        elf_bytes: &[u8],
        #[cfg(feature = "metrics")] metrics: &mut LoadProgramMetrics,
        reloading: bool,
    ) -> Result<Self, Box<dyn std::error::Error>> {
        let entry_stats = ProgramStatistics::default();
        #[cfg(feature = "metrics")]
        let load_elf_time = solana_svm_measure::measure::Measure::start("load_elf_time");
        let executable = Executable::load(elf_bytes, Arc::clone(&*program_runtime_environment))?;

        #[cfg(feature = "metrics")]
        {
            metrics.load_elf_us = load_elf_time.end_as_us();
        }

        if !reloading {
            #[cfg(feature = "metrics")]
            let verify_code_time = solana_svm_measure::measure::Measure::start("verify_code_time");
            executable.verify::<RequisiteVerifier>()?;
            #[cfg(feature = "metrics")]
            {
                metrics.verify_code_us = verify_code_time.end_as_us();
            }
        }

        #[cfg(all(not(target_os = "windows"), target_arch = "x86_64"))]
        {
            let jit_compile_time = solana_svm_measure::measure::Measure::start("jit_compile_time");
            executable.jit_compile()?;
            let jit_compile_time = jit_compile_time.end_as_us();
            entry_stats.jit_compiled(jit_compile_time);
            #[cfg(feature = "metrics")]
            {
                metrics.jit_compile_us = jit_compile_time;
            }
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

**File:** cost-model/src/cost_model.rs (L196-201)
```rust
    pub fn calculate_loaded_accounts_data_size_cost(
        loaded_accounts_data_size: u32,
        _feature_set: &FeatureSet,
    ) -> u64 {
        Self::calculate_pages_cost(Self::calculate_pages_for_bytes(loaded_accounts_data_size))
    }
```
