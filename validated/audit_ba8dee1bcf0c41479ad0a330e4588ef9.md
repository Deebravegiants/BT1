### Title
Panics inside builtin/native programs are not caught during transaction execution, allowing an unprivileged transaction to crash the validator process instead of failing gracefully - (File: program-runtime/src/invoke_context.rs)

### Summary
The reported Kakarot issue is that a call into an external contract that panics is not turned into a recoverable error, so the panic propagates and aborts the whole transaction/RPC call. Agave has a structural analog: builtin ("native") programs (System, Vote, Stake, Config, Compute Budget, Address Lookup Table, BPF Loader management instructions) and precompiles are invoked directly through Rust function calls from `InvokeContext::process_executable_chain` / `InvokeContext::native_invoke_signed`, with **no `catch_unwind` boundary** anywhere in the production transaction-processing path. If any of these Rust functions panics (e.g. via `unwrap()`/`expect()`/`panic!`/index-out-of-bounds/debug-mode arithmetic overflow) on attacker-controlled input, the panic unwinds through the entire call stack (`InvokeContext::process_instruction` → `TransactionBatchProcessor` → `Bank::load_execute_and_commit_transactions` → the banking/replay worker thread), rather than being converted into an `InstructionError` for just that one transaction.

### Finding Description
`InvokeContext::process_executable_chain` (the real, non-test dispatch path for builtin programs) calls the builtin's Rust entrypoint directly through the sBPF VM's function dispatch and inspects only the returned `ProgramResult`: [1](#0-0) 

Similarly, `InvokeContext::native_invoke_signed`, the entrypoint used for a builtin program to CPI into another builtin, calls `self.process_instruction(...)` with no panic guard: [2](#0-1) 

`process_instruction` itself is a thin wrapper with push/pop bookkeeping and no error-boundary for panics: [3](#0-2) 

By contrast, the *test-only* `program-test` crate explicitly wraps builtin invocation in `std::panic::catch_unwind` and converts any panic into `InstructionError::ProgramFailedToComplete`: [4](#0-3) 

This is proven to matter by the crate's own test, `program-test/tests/panic.rs`, which shows that *only* under the mock harness does a panicking program get downgraded to a graceful `InstructionError`: [5](#0-4) 

A repo-wide search confirms `catch_unwind` is used in exactly three places (`unified-scheduler-logic`, `gossip/cluster_info`, `program-test`) and never in the `program-runtime`, `programs/*`, `runtime/src/bank*`, or `runtime/src/transaction_execution.rs` production execution paths that actually process on-chain transactions (`Bank::load_execute_and_commit_transactions`, `execute_batch`, `Consumer::execute_and_commit_transactions_locked`), which simply propagate `Result` values and never guard against a `panic!` unwinding out of a builtin/native program: [6](#0-5) [7](#0-6) 

So, exactly like the Kakarot finding — where a called contract's panic escapes the "graceful failure" interface that `execute_starknet_call` was supposed to provide — Agave's builtin/native-program dispatch offers no equivalent "graceful failure" boundary for Rust-level panics; only `Result`-returning errors are handled gracefully, while an actual `panic!` in a builtin is a hard, unguarded fault in the production path.

### Impact Explanation
If any code path in a builtin program (System, Vote, Stake, Config, Compute Budget, Address Lookup Table program, or the BPF loader management instruction handler) that is reachable with attacker-supplied instruction data/accounts can panic (via `unwrap`, `expect`, indexing, or unchecked arithmetic that overflows in a debug/rust-panic-on-overflow build), the panic will not be converted to a per-transaction `InstructionError`. Instead it will unwind through `InvokeContext`, through `Bank`'s transaction execution/commit path, and into whichever thread is executing the transaction (a banking-stage worker or the replay stage). Depending on panic strategy, this either kills that worker thread (stalling that pipeline, an availability/halt impact for that node) or — if the process is compiled/configured with `panic = "abort"` — aborts the entire validator process. Because this can be triggered by an ordinary, unprivileged transaction, it is a materially different (and more severe) manifestation of the same "does not gracefully handle panics in called contracts" bug class than the referenced report, since Agave's builtin programs are the direct analog of Kakarot's `DualVmToken`/target contract, and there is no `AccountContract`-style graceful-failure boundary around them in production.

### Likelihood Explanation
Likelihood depends entirely on whether any currently-shipped builtin program contains a panic-reachable code path from unprivileged, attacker-controlled instruction data. Agave's builtins are generally written defensively (checked/saturating arithmetic, `Result`-returning helpers), so this is primarily an architectural gap rather than a demonstrated concrete panic today. It should be treated as a systemic weakness: any future or currently-undiscovered `unwrap()`/`expect()`/panicking arithmetic in a builtin instruction handler is a validator crash / DoS, not merely a failed transaction, because there is no `catch_unwind` boundary in the real execution path to contain it (unlike the `program-test` mock harness).

### Recommendation
Add a `catch_unwind` boundary (mirroring what `program-test::invoke_builtin_function` already does for tests) around the invocation of builtin/native program entrypoints in `InvokeContext::process_executable_chain` and `InvokeContext::native_invoke_signed`, converting any caught panic into `InstructionError::ProgramFailedToComplete` so a bug in one builtin program degrades to a single failed transaction rather than crashing a validator thread/process. Alternatively, treat this as an explicit invariant that must be maintained by code review/fuzzing of every builtin program's Rust entrypoint (no panicking code path reachable from instruction data), and add fuzzing/property tests asserting builtins never panic on arbitrary instruction data.

### Proof of Concept
No concrete panic-reachable code path in a currently shipped builtin was found in this review (this is an architectural finding). The `program-test` crate's own regression test demonstrates the underlying mechanism precisely: `program-test/tests/panic.rs` shows that a builtin program that calls `panic!("I panicked")` is only downgraded to `TransactionError::InstructionError(0, InstructionError::ProgramFailedToComplete)` because the *test harness* (`program-test/src/lib.rs::invoke_builtin_function`) wraps the call in `std::panic::catch_unwind`. The equivalent wrapper is absent from the real `InvokeContext::process_executable_chain` / `native_invoke_signed` paths used by `Bank`/`TransactionBatchProcessor` in production, so the same `panic!` inside a real builtin program executed via those paths would not be downgraded and would instead unwind into the calling thread. [5](#0-4) [8](#0-7)

### Citations

**File:** program-runtime/src/invoke_context.rs (L325-345)
```rust
    pub fn native_invoke_signed(
        &mut self,
        instruction: Instruction,
        signer_seeds: &[&[&[u8]]],
    ) -> Result<(), InstructionError> {
        let caller_program_id = *self
            .transaction_context
            .get_current_instruction_context()?
            .get_program_key()?;
        // The conversion from `PubkeyError` to `InstructionError` through
        // num-traits is incorrect, but it's the existing behavior.
        let signers = signer_seeds
            .iter()
            .map(|seeds| Pubkey::create_program_address(seeds, &caller_program_id))
            .collect::<Result<Vec<Pubkey>, solana_pubkey::PubkeyError>>()
            .map_err(|e| e as u64)?;
        self.prepare_next_cpi_instruction(instruction, &signers)?;
        let mut compute_units_consumed = 0;
        self.process_instruction(&mut compute_units_consumed, &mut ExecuteTimings::default())?;
        Ok(())
    }
```

**File:** program-runtime/src/invoke_context.rs (L601-614)
```rust
    /// Processes an instruction and returns how many compute units were used
    #[cfg_attr(feature = "dev-context-only-utils", qualifiers(pub))]
    pub(crate) fn process_instruction(
        &mut self,
        compute_units_consumed: &mut u64,
        timings: &mut ExecuteTimings,
    ) -> Result<(), InstructionError> {
        *compute_units_consumed = 0;
        self.push()?;
        self.process_executable_chain(compute_units_consumed, timings)
            // MUST pop if and only if `push` succeeded, independent of `result`.
            // Thus, the `.and()` instead of an `.and_then()`.
            .and(self.pop())
    }
```

**File:** program-runtime/src/invoke_context.rs (L638-723)
```rust
    ) -> Result<(), InstructionError> {
        let instruction_context = self.transaction_context.get_current_instruction_context()?;
        let process_executable_chain_time = Measure::start("process_executable_chain_time");

        let builtin_id = {
            let owner_id = instruction_context.get_program_owner()?;
            if native_loader::check_id(&owner_id) {
                *instruction_context.get_program_key()?
            } else if bpf_loader_deprecated::check_id(&owner_id)
                || bpf_loader::check_id(&owner_id)
                || bpf_loader_upgradeable::check_id(&owner_id)
                || loader_v4::check_id(&owner_id)
            {
                owner_id
            } else {
                return Err(InstructionError::UnsupportedProgramId);
            }
        };

        // The Murmur3 hash value (used by RBPF) of the string "entrypoint"
        const ENTRYPOINT_KEY: u32 = 0x71E3CF81;
        let entry = self
            .program_cache_for_tx_batch
            .find(&builtin_id)
            .ok_or(InstructionError::UnsupportedProgramId)?;
        let function = match &entry.program {
            ProgramCacheEntryType::Builtin(program) => program
                .get_function_registry()
                .lookup_by_key(ENTRYPOINT_KEY)
                .map(|(_name, (function, _codegen))| function),
            _ => None,
        }
        .ok_or(InstructionError::UnsupportedProgramId)?;

        let program_id = *instruction_context.get_program_key()?;
        self.transaction_context
            .set_return_data(program_id, Vec::new())?;
        let logger = self.get_log_collector();
        stable_log::program_invoke(&logger, &program_id, self.get_stack_height());
        let pre_remaining_units = self.get_remaining();
        // For now, only built-ins are invoked from here, so the VM and its Config are irrelevant.
        self.memory_contexts
            .set_memory_context_abi_v1(MemoryContext::new(
                BpfAllocator::new(0),
                Vec::new(),
                // SAFETY:
                // This path invokes a builtin program, so this mapping is never used.
                unsafe {
                    MemoryMapping::new(Vec::new(), &Config::default(), SBPFVersion::Reserved)
                        .unwrap()
                },
            ))?;
        let mut vm = EbpfVm::new(
            Arc::clone(
                &**self
                    .environment_config
                    .program_runtime_environments
                    .get_env_for_execution(),
            ),
            SBPFVersion::V0,
            // Removes lifetime tracking
            unsafe { std::mem::transmute::<&mut InvokeContext, &mut InvokeContext>(self) },
            0,
        );
        vm.invoke_function(function);
        let result = match vm.program_result {
            ProgramResult::Ok(_) => {
                stable_log::program_success(&logger, &program_id);
                Ok(())
            }
            ProgramResult::Err(ref err) => {
                if let EbpfError::SyscallError(syscall_error) = err {
                    if let Some(instruction_err) = syscall_error.downcast_ref::<InstructionError>()
                    {
                        stable_log::program_failure(&logger, &program_id, instruction_err);
                        Err(instruction_err.clone())
                    } else {
                        stable_log::program_failure(&logger, &program_id, syscall_error);
                        Err(InstructionError::ProgramFailedToComplete)
                    }
                } else {
                    stable_log::program_failure(&logger, &program_id, err);
                    Err(InstructionError::ProgramFailedToComplete)
                }
            }
        };
```

**File:** program-test/src/lib.rs (L154-172)
```rust
    // Execute the program
    match std::panic::catch_unwind(AssertUnwindSafe(|| {
        builtin_function(program_id, &account_infos, input)
    })) {
        Ok(program_result) => {
            program_result.map_err(|program_error| {
                let err = InstructionError::from(u64::from(program_error));
                stable_log::program_failure(&log_collector, program_id, &err);
                let err: Box<dyn std::error::Error> = Box::new(err);
                err
            })?;
        }
        Err(_panic_error) => {
            let err = InstructionError::ProgramFailedToComplete;
            stable_log::program_failure(&log_collector, program_id, &err);
            let err: Box<dyn std::error::Error> = Box::new(err);
            Err(err)?;
        }
    };
```

**File:** program-test/tests/panic.rs (L12-40)
```rust
fn panic(_program_id: &Pubkey, _accounts: &[AccountInfo], _input: &[u8]) -> ProgramResult {
    panic!("I panicked");
}

#[tokio::test]
async fn panic_test() {
    let program_id = Pubkey::new_unique();

    let program_test = ProgramTest::new("panic", program_id, processor!(panic));

    let context = program_test.start_with_context().await;

    let instruction = Instruction::new_with_bytes(program_id, &[], vec![]);

    let transaction = Transaction::new_signed_with_payer(
        &[instruction],
        Some(&context.payer.pubkey()),
        &[&context.payer],
        context.last_blockhash,
    );
    assert_eq!(
        context
            .banks_client
            .process_transaction(transaction)
            .await
            .unwrap_err()
            .unwrap(),
        TransactionError::InstructionError(0, InstructionError::ProgramFailedToComplete)
    );
```

**File:** runtime/src/transaction_execution.rs (L57-87)
```rust
pub fn execute_batch<'a>(
    batch: &'a TransactionBatchWithIndexes<impl TransactionWithMeta>,
    bank: &'a Arc<Bank>,
    transaction_status_sender: Option<&'a TransactionStatusSender>,
    replay_vote_sender: Option<&'a ReplayVoteSender>,
    replay_vote_send_type: ReplayVoteSendType,
    timings: &'a mut ExecuteTimings,
    log_messages_bytes_limit: Option<usize>,
    prioritization_fee_cache: Option<&'a PrioritizationFeeCache>,
) -> TransactionResult<()> {
    let TransactionBatchWithIndexes {
        batch,
        transaction_indexes,
    } = batch;

    let transaction_indexes = Cow::from(transaction_indexes);

    let pre_commit_callback = |processing_results: &_| -> TransactionResult<()> {
        // We're entering into one of the block-verification methods.
        get_first_error(batch, processing_results)
    };

    let (commit_results, balance_collector) = batch
        .bank()
        .load_execute_and_commit_transactions_with_pre_commit_callback(
            batch,
            ExecutionRecordingConfig::new_single_setting(transaction_status_sender.is_some()),
            timings,
            log_messages_bytes_limit,
            pre_commit_callback,
        )?;
```

**File:** core/src/banking_stage/consumer.rs (L268-287)
```rust
        let (load_and_execute_transactions_output, load_execute_us) =
            measure_us!(bank.load_and_execute_transactions(
                batch,
                bank.max_processing_age(),
                &mut execute_and_commit_timings.execute_timings,
                &mut error_counters,
                TransactionProcessingConfig {
                    account_overrides: None,
                    check_program_deployment_slot: bank.check_program_deployment_slot(),
                    log_messages_bytes_limit: self.log_messages_bytes_limit,
                    limit_to_load_programs: true,
                    recording_config: ExecutionRecordingConfig::new_single_setting(
                        transaction_status_sender_enabled
                    ),
                    drop_on_failure: flags.drop_on_failure,
                    all_or_nothing: flags.all_or_nothing,
                    strict_nonce_size_check: true,
                    drop_noop_transactions: true,
                }
            ));
```
