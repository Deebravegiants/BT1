### Title
Per-call WASM instantiation cost (globals/data-segments/element-segments re-initialization) is priced only by code byte size, not by actual instantiation work, allowing underpriced/near-free repeated execution - (File: `runtime/near-vm-runner/src/logic/gas_counter.rs`, `runtime/runtime-params-estimator/src/vm_estimator.rs`)

### Summary
The only fee charged for loading/instantiating a contract before executing a method is `contract_loading_base + contract_loading_bytes * code_len`, computed purely from the WASM binary's byte size [1](#0-0) . However, per-instantiation work performed by the VM backend on every `FunctionCall` — zero-initializing globals, copying active data segments into linear memory, and initializing active element segments into tables — scales with the *number* of these constructs, not with the WASM code's byte size, and is explicitly flagged in the estimator as adversarial/unpriced: `AdversarialLoadManyGlobals` ("Invocation cost with 100k zero-initialized globals. Exposes unbounded per-call Wasmtime global re-initialization not covered by gas"), `AdversarialLoadManyDataSegments`, and `AdversarialLoadManyElementSegments` (both similarly documented as "not covered by gas") [2](#0-1) . The estimator harness that exercises this (`adversarial_load_many_globals`/`_data_segments`/`_element_segments` and `measure_instantiation_overhead`) confirms this work happens on every invocation of the compiled/cached contract, separate from and unaccounted for by the loading fee [3](#0-2) .

### Finding Description
Every `FunctionCall` action against a deployed contract goes through `with_compiled_and_loaded` → `before_loading_executable`/`after_loading_executable`, which charge a single loading fee proportional to the code's byte length, and then `instance = pre.instantiate(&mut store)` actually instantiates the module (running Wasmtime's global/data-segment/element-segment initialization) before the metered "remaining_gas" call hook is even wired up [4](#0-3) . The loading fee's own doc comment states it "does not consider the structure of the contract code, only the size... A fee that takes the code structure into consideration could be added. But since that would have to happen after loading, we cannot pre-charge it" [5](#0-4) .

A contract author can craft a WASM module that is small in byte size (cheap to charge for loading/compilation) but contains a large number of globals, active data segments, or active element segments (within the `LimitConfig` structural bounds such as `max_globals_per_contract` enforced in `prepare.rs`/`prepare_v3.rs`). Each `FunctionCall` receipt against that contract then re-triggers the expensive per-instantiation initialization work in the VM backend, but the gas charged for it is only the small, byte-size-driven loading fee — none of the gas-metering machinery (`finite_wasm_gas`/`gas_opcodes`, `ExtCosts::pay_base`/`pay_per`) covers instantiation, since metering (the `call_hook` synchronizing `remaining_gas`) is only installed after `instantiate` completes [6](#0-5) .

This is directly analogous to the referenced CosmWasm advisory: specific WASM-adjacent operations (there, certain Wasm opcodes/host calls; here, module-instantiation-time initialization work) execute far more expensive computation than the gas charged for them implies, enabling a contract to consume disproportionate validator CPU time per unit of gas paid.

### Impact Explanation
An attacker can deploy a small contract with the maximum permitted number of globals/data-segments/element-segments and repeatedly invoke it via cheap `FunctionCall` receipts. Because gas is charged based on code byte size rather than instantiation cost, the attacker pays gas far below the actual CPU time consumed by validators on every call, effectively getting "free or underpriced execution." Because this happens on the hot path of every receipt execution (not compilation, which is cached), repeated exploitation at scale could slow down chunk production for validators (temporary chain-wide DoS/slowdown), matching the "free or underpriced execution... or unbounded resource use" acceptance criteria.

### Likelihood Explanation
The attack requires only deploying a WASM contract crafted with many globals/data-segments/element-segments (within existing structural `LimitConfig` caps) and submitting ordinary `FunctionCall` transactions/receipts — no privileged, validator-only, or network-layer access is needed. The underlying gap is explicitly acknowledged by nearcore's own estimator code comments ("not covered by gas"), indicating this is a known, currently-unpriced surface rather than a purely theoretical one. However, I could not fully verify from indexed content whether an additional, unaccounted structural fee has since been added upstream of these estimator markers (the `fix_contract_loading_cost`/`FixContractLoadingError` features change *when* the byte-size fee is charged, not *what* it accounts for), so likelihood should be validated further by checking whether any subsequent protocol version introduces a structural (globals/segments count) component to the loading or instantiation fee.

### Recommendation
Add a gas-cost component to contract loading/instantiation that scales with the number of globals, active data segments, and active element segments (in addition to the existing byte-size-based `contract_loading_bytes`/`contract_loading_base`), calibrated via the runtime-params-estimator's `AdversarialLoadManyGlobals`/`AdversarialLoadManyDataSegments`/`AdversarialLoadManyElementSegments` benchmarks so that worst-case instantiation time is properly priced under the 1 Tgas = 1ms rule. Since this cost cannot be pre-charged before parsing the module (per the existing loading-fee comment), consider deriving it from the WASM module's structural metadata during `prepare`/`prepare_v3` (which already inspects globals/segment counts for `LimitConfig` enforcement) and charging it as part of the pre-load fee, or tightening `max_globals_per_contract`/segment limits to bound worst-case instantiation cost within the currently-charged byte-size fee.

### Proof of Concept
1. Craft (or reuse) `near_test_contracts::contract_with_num_globals(N)`, `many_data_segments_contract(N)`, or `many_element_segments_contract(N)` with `N` near the `LimitConfig` maximum (e.g., ~50,000–100,000, per `runtime/near-test-contracts/src/lib.rs` and `runtime/runtime-params-estimator/src/vm_estimator.rs:168-184`) — the resulting WASM binary can remain small in bytes.
2. Deploy this contract and repeatedly invoke a trivial exported method (e.g., `main` with a bare `end` body, as used in `measure_instantiation_overhead`) via ordinary `FunctionCall` receipts.
3. Compare gas charged (`contract_loading_base + contract_loading_bytes * code_len`, small) against actual wall-clock time consumed per call, which the estimator itself measures via `adversarial_load_many_globals`/`_data_segments`/`_element_segments` in `runtime/runtime-params-estimator/src/vm_estimator.rs:168-223` — demonstrating the instantiation overhead is real, measurable, and unpriced by the gas charged.

### Citations

**File:** runtime/near-vm-runner/src/logic/gas_counter.rs (L216-227)
```rust
    /// Add a cost for loading the contract code in the VM.
    ///
    /// This cost does not consider the structure of the contract code, only the
    /// size. This is currently the only loading fee. A fee that takes the code
    /// structure into consideration could be added. But since that would have
    /// to happen after loading, we cannot pre-charge it. This is the main
    /// motivation to (only) have this simple fee.
    #[cfg(feature = "wasmtime_vm")]
    pub(crate) fn add_contract_loading_fee(&mut self, code_len: u64) -> Result<()> {
        self.pay_per(ExtCosts::contract_loading_bytes, code_len)?;
        self.pay_base(ExtCosts::contract_loading_base)
    }
```

**File:** runtime/runtime-params-estimator/src/cost.rs (L742-750)
```rust
    /// Invocation cost with 100k zero-initialized globals.
    /// Exposes unbounded per-call Wasmtime global re-initialization not covered by gas.
    AdversarialLoadManyGlobals,
    /// Invocation cost with 50k active data segments.
    /// Exposes unbounded per-call data-segment initialization not covered by gas.
    AdversarialLoadManyDataSegments,
    /// Invocation cost with 10k active element segments.
    /// Exposes unbounded per-call table-initialization work not covered by gas.
    AdversarialLoadManyElementSegments,
```

**File:** runtime/runtime-params-estimator/src/vm_estimator.rs (L168-223)
```rust
pub(crate) fn adversarial_load_many_globals(metric: GasMetric, vm_kind: VMKind) -> GasCost {
    let code = near_test_contracts::contract_with_num_globals(50_000);
    measure_instantiation_overhead(metric, vm_kind, &code)
}

pub(crate) fn adversarial_load_many_data_segments(metric: GasMetric, vm_kind: VMKind) -> GasCost {
    let code = near_test_contracts::many_data_segments_contract(50_000);
    measure_instantiation_overhead(metric, vm_kind, &code)
}

pub(crate) fn adversarial_load_many_element_segments(
    metric: GasMetric,
    vm_kind: VMKind,
) -> GasCost {
    let code = near_test_contracts::many_element_segments_contract(10_000);
    measure_instantiation_overhead(metric, vm_kind, &code)
}

/// Warm the compile cache, then measure N invocations (instantiation + trivial execution).
/// The function body is a bare `end`, so execution cost is negligible.
fn measure_instantiation_overhead(
    metric: GasMetric,
    vm_kind: VMKind,
    contract_bytes: &[u8],
) -> GasCost {
    let config_store = RuntimeConfigStore::new(None);
    let mut config = config_store.get_config(PROTOCOL_VERSION).wasm_config.as_ref().clone();
    config.vm_kind = vm_kind;
    let config = Arc::new(config);
    let fees = Arc::new(RuntimeFeesConfig::test());
    let code = ContractCode::new(contract_bytes.to_vec(), None);
    let cache = MockContractRuntimeCache::default();
    let mut fake_external = near_vm_runner::logic::mocks::mock_external::MockedExternal::with_code(
        code.clone_for_tests(),
    );

    let mut run_once = || {
        let context = create_context(vec![]);
        let gas_counter = context.make_gas_counter(&config);
        vm_kind
            .runtime(config.clone())
            .unwrap()
            .prepare(&fake_external, Some(&cache), gas_counter, "main")
            .run(&mut fake_external, &context, Arc::clone(&fees))
            .expect("fatal_error")
    };

    // Warm: compiles and caches the module; subsequent calls only instantiate + execute.
    run_once();

    let n = 10_usize;
    let start = GasCost::measure(metric);
    for _ in 0..n {
        run_once();
    }
    start.elapsed() / n as u64
```

**File:** runtime/near-vm-runner/src/wasmtime_runner/mod.rs (L1036-1089)
```rust
        let instance = match pre.instantiate(&mut store) {
            Ok(instance) => instance,
            Err(err) => {
                let err = err.into_vm_error()?;
                let Ctx { result_state, .. } = store.into_data();
                return Ok(VMOutcome::abort(result_state, err));
            }
        };
        // Pre-resolve the memory export here (on the real, post-instantiation
        // instance) so host functions don't need to resolve it lazily.
        //
        // The lazy Caller::get_module_export → module_for_instance().unwrap()
        // path panics when the Caller's instance is a Dummy host-side
        // trampoline for a re-exported host function (module_for_instance
        // returns None for Dummy instances). See test_panic_re_export and
        // test_trampoline_only_* for regression coverage.
        if let Export::Unresolved(memory_export) = store.data().memory {
            if let Some(Extern::Memory(memory)) =
                instance.get_module_export(&mut store, &memory_export)
            {
                store.data_mut().memory = Export::Resolved(memory);
            }
        }
        if let Some(global) = remaining_gas {
            let Some(Extern::Global(global)) = instance.get_module_export(&mut store, &global)
            else {
                panic!("gas global export was present on the module, but not on the instance");
            };
            store.call_hook(move |mut store, hook| {
                match hook {
                    CallHook::CallingHost | CallHook::ReturningFromWasm => {
                        let Val::I64(remaining_gas) = global.get(&mut store) else {
                            panic!("gas global export is not i64");
                        };
                        let ctx = store.data_mut();
                        let burned = ctx
                            .result_state
                            .gas_counter
                            .remaining_gas()
                            .saturating_sub(Gas::from_gas(remaining_gas as _));
                        if burned.as_gas() > 0 {
                            ctx.result_state.gas_counter.burn_gas(burned)?;
                        }
                    }
                    CallHook::ReturningFromHost | CallHook::CallingWasm => {
                        let remaining_gas = store.data().result_state.gas_counter.remaining_gas();
                        global
                            .set(&mut store, Val::I64(remaining_gas.as_gas() as _))
                            .expect("failed to set gas global export")
                    }
                }
                Ok(())
            });
        }
```
