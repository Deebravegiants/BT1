### Title
Contract-loading gas is silently discarded on `MethodNotFound`/`MethodInvalidSignature` under the pre-`FixContractLoadingCost` protocol (current stable), enabling free large-contract-loading DoS - (File: `runtime/near-vm-runner/src/logic/logic.rs`)

### Summary
On the currently active `STABLE_PROTOCOL_VERSION` (86), which is below the `FixContractLoadingCost` protocol feature version (129, still nightly-only), the WASM runtime charges the contract-loading fee into the gas counter during preparation, but then discards it via `VMOutcome::nop_outcome` whenever the called method does not resolve (empty/garbage/invalid method name). This lets an attacker force validators to repeatedly deserialize/instantiate a large deployed contract while the transaction is refunded almost all prepaid gas, since the finalized receipt reports `burnt_gas: 0`.

### Finding Description
In `gas_counter.rs`, `after_loading_executable` unconditionally charges `add_contract_loading_fee` (base + per-byte) whenever `!config.fix_contract_loading_cost` (i.e., on the currently active stable protocol, since `FixContractLoadingCost` is gated to protocol version 129 which is still "Nightly" per `core/primitives-core/src/version.rs`, while `STABLE_PROTOCOL_VERSION = 86`): [1](#0-0) 

This charge happens before the runtime knows whether the requested exported method actually exists. In `wasmtime_runner/mod.rs`, after this fee is charged, the runtime checks whether the target export (`method`) resolves; if not, or if the signature doesn't match, it produces `PreparationResult::OutcomeAbortButNopInOldProtocol`, not a normal `OutcomeAbort`: [2](#0-1) 

The same NOP path is also reached when the exported function cannot be found at call time (`RunOutcome::AbortNop`): [3](#0-2) [4](#0-3) 

Finally, `VMOutcome::abort_but_nop_outcome_in_old_protocol` checks the same feature flag and, when it's inactive (current stable), zeroes out `burnt_gas`/`used_gas`/`storage_usage`/`balance` entirely via `nop_outcome`, discarding the already-charged loading fee and all other gas burnt for that call: [5](#0-4) 

Crucially, the heavy work — cache lookup, `Module::deserialize`, `Linker::instantiate_pre` (and, on cache-miss, full compilation) — is performed in `with_compiled_and_loaded` *before* the method-resolution check even runs, so the CPU cost is incurred by every validator/chunk-producer re-validating the chunk, regardless of the final NOP outcome: [6](#0-5) 

This is confirmed by an existing regression test that explicitly documents pre-fix zero-gas behavior against post-fix charged behavior for `MethodNotFound`: [7](#0-6) 
and by the dedicated preparation-failure test showing `burnt gas 0 used gas 0` pre-fix vs. a large non-zero charge post-fix for identical failures: [8](#0-7) 

The version registry confirms `FixContractLoadingCost` is pinned to protocol version 129 and is only reachable under "Nightly features", while the current stable mainnet protocol version is 86 — so this NOP-refund behavior is the live, currently-active behavior, not a hypothetical legacy corner case: [9](#0-8) [10](#0-9) 

### Impact Explanation
This is a gas-metering-bypass / free-execution bug: an ordinary account can deploy a large contract and repeatedly invoke it with a nonexistent/mismatched method name. Each call forces every block/chunk producer re-validating the chunk to perform expensive module deserialization and instantiation, while the sender is refunded essentially all prepaid gas because the finalized outcome reports zero burnt/used gas. This matches the NEAR bounty impact class of "gas metering bypass" / "free or underpriced execution", and can be weaponized as a low-cost compute-exhaustion DoS vector against block producers/validators.

### Likelihood Explanation
Fully feasible with an unprivileged attacker: deploy any large WASM contract (`DeployContract` action, no special permission needed), then send `FunctionCall` transactions/receipts with an empty or garbage `method_name`. No special preconditions beyond running under the currently deployed stable protocol version (86), which is below the `FixContractLoadingCost` activation version (129). The attack is trivially repeatable at scale since the same contract can be re-invoked indefinitely with negligible net gas cost to the attacker.

### Recommendation
Stabilize/activate `ProtocolFeature::FixContractLoadingCost` on mainnet so that `VMOutcome::abort_but_nop_outcome_in_old_protocol` always calls `Self::abort` (retaining burnt gas) instead of `Self::nop_outcome`, ensuring the contract-loading fee already charged in `after_loading_executable` is never discarded regardless of whether the target method resolves.

### Proof of Concept
Extend the existing `runtime/near-vm-runner/src/tests/runtime_errors.rs::test_infinite_initializer_export_not_found`-style test into an integration test (similar to `integration-tests/src/tests/features/fix_contract_loading_cost.rs`) that:
1. Deploys a large contract (e.g. hundreds of KB) on the current stable protocol version (86, pre-`FixContractLoadingCost`).
2. Calls it repeatedly with a nonexistent method name via `FunctionCall`.
3. Asserts that `receipts_outcome[0].outcome.gas_burnt == 0` (or near-zero) for every call despite the validator performing real module deserialization/instantiation work each time.
4. Compares against the post-`FixContractLoadingCost` protocol version, asserting `gas_burnt` reflects the actual `contract_loading_base + contract_loading_bytes * len` charge (as already validated by `preparation_error_gas_cost` in `fix_contract_loading_cost.rs`), demonstrating the cost-to-attacker/cost-to-validator asymmetry only exists pre-fix.

### Citations

**File:** runtime/near-vm-runner/src/logic/gas_counter.rs (L250-265)
```rust
    /// Legacy code to preserve old gas charging behaviour in old protocol versions.
    #[cfg(feature = "wasmtime_vm")]
    pub(crate) fn after_loading_executable(
        &mut self,
        config: &near_parameters::vm::Config,
        wasm_code_bytes: u64,
    ) -> std::result::Result<(), super::errors::FunctionCallError> {
        if !config.fix_contract_loading_cost {
            if self.add_contract_loading_fee(wasm_code_bytes).is_err() {
                return Err(super::errors::FunctionCallError::HostError(
                    super::HostError::GasExceeded,
                ));
            }
        }
        Ok(())
    }
```

**File:** runtime/near-vm-runner/src/wasmtime_runner/mod.rs (L688-836)
```rust
    fn with_compiled_and_loaded(
        &self,
        cache: &dyn ContractRuntimeCache,
        contract: &dyn Contract,
        mut gas_counter: GasCounter,
        method: &str,
        closure: impl FnOnce(
            GasCounter,
            Result<PreparedModule, FunctionCallError>,
        ) -> VMResult<PreparedContract>,
    ) -> VMResult<PreparedContract> {
        type MemoryCacheType =
            (u64, Result<Result<PreparedModule, FunctionCallError>, CompilationError>);
        let to_any = |v: MemoryCacheType| -> Box<dyn std::any::Any + Send> { Box::new(v) };
        let mut is_cache_hit = true;
        let mut is_memory_hit = true;
        let key = get_contract_cache_key(contract.hash(), &self.config, self.vm_hash());
        cache.touch(&key);
        let (wasm_bytes, pre_result) = cache.memory_cache().try_lookup(
            key,
            || {
                is_memory_hit = false;
                let cache_record = cache.get(&key).map_err(CacheError::ReadError)?;
                let (wasm_bytes, module) =
                    if let Some(CompiledContractInfo { wasm_bytes, compiled }) = cache_record {
                        match compiled {
                            CompiledContract::CompileModuleError(err) => {
                                return Ok((
                                    err.size_bytes_approximate() as u64,
                                    to_any((wasm_bytes, Err(err))),
                                ));
                            }
                            CompiledContract::Code(module) => (wasm_bytes, module),
                        }
                    } else {
                        is_cache_hit = false;
                        let Some(code) = contract.get_code() else {
                            return Err(VMRunnerError::ContractCodeNotPresent);
                        };
                        let wasm_bytes = code.code().len() as u64;
                        match self.compile_and_cache(&code, cache)? {
                            Err(err) => {
                                return Ok((
                                    err.size_bytes_approximate() as u64,
                                    to_any((wasm_bytes, Err(err))),
                                ));
                            }
                            Ok(module) => (wasm_bytes, module),
                        }
                    };
                // (UN-)SAFETY: the `module` must have been produced by
                // a prior call to `serialize`.
                //
                // In practice this is not necessarily true. One could have
                // forgotten to change the cache key when upgrading the version of
                // the near_vm library or the database could have had its data
                // corrupted while at rest.
                //
                // There should definitely be some validation in near_vm to ensure
                // we load what we think we load.
                let compiled_size = module.len();
                let module = match unsafe { Module::deserialize(&self.engine, &module) } {
                    Ok(module) => module,
                    Err(err) => {
                        // Propagate failed contract loading as a cached `FunctionCallError`, mirroring
                        // the memory-export check below, so it flows through the fee-charge points
                        // and finalizes as a gas-bearing abort.
                        if self.config.fix_contract_loading_error {
                            let err = FunctionCallError::LoadingError { msg: err.to_string() };
                            return Ok((
                                err.size_bytes_approximate() as u64,
                                to_any((wasm_bytes, Ok(Err(err)))),
                            ));
                        }
                        return Err(VMRunnerError::LoadingError(err.to_string()));
                    }
                };
                let Some(memory) = module.get_export_index(MEMORY_EXPORT) else {
                    let err = FunctionCallError::LinkError { msg: "memory export missing".into() };
                    return Ok((
                        err.size_bytes_approximate() as u64,
                        to_any((wasm_bytes, Ok(Err(err)))),
                    ));
                };
                let remaining_gas = module.get_export_index(REMAINING_GAS_EXPORT);
                let start = module.get_export_index(START_EXPORT);
                let mut linker = Linker::new(&self.engine);
                link(&mut linker, &self.config);
                match linker.instantiate_pre(&module) {
                    Err(err) => {
                        let err = err.into_vm_error()?;
                        Ok((
                            err.size_bytes_approximate() as u64,
                            to_any((wasm_bytes, Ok(Err(err)))),
                        ))
                    }
                    Ok(pre) => {
                        let ResourcesRequired { num_tables, .. } = module.resources_required();
                        // The module `weight` is estimated as its serialized size. This is a
                        // rough approximation as the runtime metadata size is not included.
                        // Should be sufficient for our purposes.
                        Ok((
                            compiled_size as u64,
                            to_any((
                                wasm_bytes,
                                Ok(Ok(PreparedModule {
                                    pre,
                                    memory,
                                    remaining_gas,
                                    start,
                                    num_tables,
                                })),
                            )),
                        ))
                    }
                }
            },
            move |value| {
                let &(wasm_bytes, ref downcast) = value
                    .downcast_ref::<MemoryCacheType>()
                    .expect("downcast should always succeed");

                (wasm_bytes, downcast.clone())
            },
        )?;

        crate::metrics::record_compiled_contract_cache_lookup(is_cache_hit, is_memory_hit);
        let config = Arc::clone(&self.config);
        let result = gas_counter.before_loading_executable(&config, &method, wasm_bytes);
        if let Err(e) = result {
            let result = PreparationResult::OutcomeAbort(e);
            return Ok(PreparedContract { config, gas_counter, result });
        }
        match pre_result {
            Ok(res) => {
                let result = gas_counter.after_loading_executable(&config, wasm_bytes);
                if let Err(e) = result {
                    let result = PreparationResult::OutcomeAbort(e);
                    return Ok(PreparedContract { config, gas_counter, result });
                }
                closure(gas_counter, res)
            }
            Err(e) => {
                let result =
                    PreparationResult::OutcomeAbort(FunctionCallError::CompilationError(e));
                return Ok(PreparedContract { config, gas_counter, result });
            }
        }
    }
```

**File:** runtime/near-vm-runner/src/wasmtime_runner/mod.rs (L905-921)
```rust
                    Ok(PreparedModule { pre, memory, remaining_gas, start, num_tables }) => {
                        let method = format!("{EXPORT_PREFIX}{method}");
                        let Some(ExternType::Func(func_type)) = pre.module().get_export(&method)
                        else {
                            let e = FunctionCallError::MethodResolveError(
                                MethodResolveError::MethodNotFound,
                            );
                            let result = PreparationResult::OutcomeAbortButNopInOldProtocol(e);
                            return Ok(PreparedContract { config, gas_counter, result });
                        };
                        if func_type.params().len() != 0 || func_type.results().len() != 0 {
                            let e = FunctionCallError::MethodResolveError(
                                MethodResolveError::MethodInvalidSignature,
                            );
                            let result = PreparationResult::OutcomeAbortButNopInOldProtocol(e);
                            return Ok(PreparedContract { config, gas_counter, result });
                        }
```

**File:** runtime/near-vm-runner/src/wasmtime_runner/mod.rs (L982-991)
```rust
fn call(
    mut store: &mut Store<Ctx>,
    instance: Instance,
    method: &str,
) -> Result<RunOutcome, VMRunnerError> {
    let Some(func) = instance.get_func(&mut store, method) else {
        return Ok(RunOutcome::AbortNop(FunctionCallError::MethodResolveError(
            MethodResolveError::MethodNotFound,
        )));
    };
```

**File:** runtime/near-vm-runner/src/wasmtime_runner/mod.rs (L1103-1109)
```rust
        let res = call(&mut store, instance, &method);
        let Ctx { result_state, .. } = store.into_data();
        match res? {
            RunOutcome::Ok => Ok(VMOutcome::ok(result_state)),
            RunOutcome::AbortNop(error) => {
                Ok(VMOutcome::abort_but_nop_outcome_in_old_protocol(result_state, error))
            }
```

**File:** runtime/near-vm-runner/src/logic/logic.rs (L4564-4594)
```rust
    /// Creates an outcome with a no-op outcome.
    pub fn nop_outcome(error: FunctionCallError) -> VMOutcome {
        VMOutcome {
            // Note: Balance and storage fields are ignored on a failed outcome.
            balance: Balance::ZERO,
            storage_usage: 0,
            // Note: Fields below are added or merged when processing the
            // outcome. With 0 or the empty set, those are no-ops.
            return_data: ReturnData::None,
            burnt_gas: Gas::ZERO,
            used_gas: Gas::ZERO,
            compute_usage: 0,
            logs: Vec::new(),
            profile: ProfileDataV3::default(),
            aborted: Some(error),
            subsidized_amount: Balance::ZERO,
        }
    }

    /// Like `Self::abort()` but without feature `FixContractLoadingCost` it
    /// will return a NOP outcome. This is used for backwards-compatibility only.
    pub fn abort_but_nop_outcome_in_old_protocol(
        state: ExecutionResultState,
        error: FunctionCallError,
    ) -> VMOutcome {
        if state.config.fix_contract_loading_cost {
            Self::abort(state, error)
        } else {
            Self::nop_outcome(error)
        }
    }
```

**File:** runtime/near-vm-runner/src/tests/runtime_errors.rs (L111-128)
```rust
#[test]
fn test_infinite_initializer_export_not_found() {
    #[allow(deprecated)]
    test_builder()
        .wat(INFINITE_INITIALIZER_CONTRACT)
        .method("no-such-method")
        .protocol_version(FIX_CONTRACT_LOADING_COST)
        .expects(&[
            expect![[r#"
                VMOutcome: balance 0 storage_usage 0 return data None burnt gas 0 used gas 0
                Err: MethodNotFound
            "#]],
            expect![[r#"
                VMOutcome: balance 4 storage_usage 12 return data None burnt gas 104071548 used gas 104071548
                Err: MethodNotFound
            "#]],
        ]);
}
```

**File:** runtime/near-vm-runner/src/tests/runtime_errors.rs (L986-1025)
```rust
    /// Failure during preparation must remain free of gas charges for old versions
    /// but new versions must charge the loading gas.
    #[test]
    fn test_fn_loading_gas_protocol_upgrade_fail_preparing() {
        // This list covers all control flows that are expected to change
        // with the protocol feature.
        // Having a test for every possible preparation error would be even
        // better, to ensure triggering any of them will always remain
        // compatible with versions before this upgrade. Unfortunately, we
        // currently do not have tests ready to trigger each error.

        #[allow(deprecated)]
        test_builder()
            .wat(r#"(module (export "main" (func 0)))"#)
            .protocol_version(FIX_CONTRACT_LOADING_COST)
            .expects(&[
                expect![[r#"
                    VMOutcome: balance 4 storage_usage 12 return data None burnt gas 0 used gas 0
                    Err: PrepareError: Error happened while deserializing the module.
                "#]],
                expect![[r#"
                    VMOutcome: balance 4 storage_usage 12 return data None burnt gas 55053273 used gas 55053273
                    Err: PrepareError: Error happened while deserializing the module.
                "#]],
            ]);

        #[allow(deprecated)]
        test_builder()
            .wasm(&bad_import_global("wtf"))
            .protocol_version(FIX_CONTRACT_LOADING_COST)
            .expects(&[
                expect![[r#"
                    VMOutcome: balance 4 storage_usage 12 return data None burnt gas 0 used gas 0
                    Err: PrepareError: Error happened during instantiation.
                "#]],
                expect![[r#"
                    VMOutcome: balance 4 storage_usage 12 return data None burnt gas 99714368 used gas 99714368
                    Err: PrepareError: Error happened during instantiation.
                "#]],
            ]);
```

**File:** core/primitives-core/src/version.rs (L573-586)
```rust
            ProtocolFeature::FixContractLoadingError => 86,

            // Nightly features:
            ProtocolFeature::FixContractLoadingCost => 129,
            // TODO(#11201): When stabilizing this feature in mainnet, also remove the temporary code
            // that always enables this for mocknet (see config_mocknet function).
            ProtocolFeature::ShuffleShardAssignments => 143,
            ProtocolFeature::EarlyKickout => 152,
            // Spice is setup to include nightly, but not be part of it for now so that features
            // that are released before spice can be tested properly.
            ProtocolFeature::Spice => 180,
            // Place features that are not yet in Nightly below this line.
        }
    }
```

**File:** core/primitives-core/src/version.rs (L624-643)
```rust
/// Current protocol version used on the mainnet with all stable features.
const STABLE_PROTOCOL_VERSION: ProtocolVersion = 86;

// On nightly, pick big enough version to support all features.
const NIGHTLY_PROTOCOL_VERSION: ProtocolVersion = 156;

// TODO(spice): Once spice is mature and close to release make it part of nightly - at the point in
// time cargo feature for spice should be removed as well.
// For spice we want to include all nightly features, but for now we don't want nightly to run with
// spice.
const SPICE_PROTOCOL_VERSION: ProtocolVersion = 200;

/// Largest protocol version supported by the current binary.
pub const PROTOCOL_VERSION: ProtocolVersion = if cfg!(feature = "protocol_feature_spice") {
    SPICE_PROTOCOL_VERSION
} else if cfg!(feature = "nightly") {
    NIGHTLY_PROTOCOL_VERSION
} else {
    STABLE_PROTOCOL_VERSION
};
```
