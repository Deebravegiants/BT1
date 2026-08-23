## Finding

### Title
Wasm compilation failures skip the loading-fee charge entirely, allowing free execution-time DoS via crafted contracts - (File: `runtime/near-vm-runner/src/wasmtime_runner/mod.rs`)

### Summary
`WasmtimeVM::with_compiled_and_loaded` charges the `contract_loading_base`/`contract_loading_bytes` fee *after* the wasm module has already been compiled/deserialized/linked, and — critically — skips charging that fee entirely when the compile step itself produces a `CompilationError`. Every validator that independently compiles the contract for the first time performs real, unbounded CPU work for zero gas, mirroring the minievm precompile bug class where expensive work is done before the error path returns without charging gas.

### Finding Description
`with_compiled_and_loaded` resolves the compiled artifact via a two-level cache. On a cache miss it calls `compile_and_cache`, which runs `compile_uncached` and stores either `CompiledContract::Code` or `CompiledContract::CompileModuleError` [1](#0-0) .

After this lookup/compile step, `before_loading_executable` only validates that `method_name` is non-empty and, gated by `fix_contract_loading_cost`, pre-charges the loading fee [2](#0-1) . On stable mainnet `fix_contract_loading_cost` is `false` (the fix activates only at nightly PV 129) [3](#0-2) , so no fee is charged here.

The loading fee is instead charged in `after_loading_executable`, but only in the success branch of `pre_result` — i.e., only when the compiled module was successfully deserialized/linked/`instantiate_pre`'d:
```rust
match pre_result {
    Ok(res) => {
        let result = gas_counter.after_loading_executable(&config, wasm_bytes);
        ...
        closure(gas_counter, res)
    }
    Err(e) => {
        let result =
            PreparationResult::OutcomeAbort(FunctionCallError::CompilationError(e));
        return Ok(PreparedContract { config, gas_counter, result });
    }
}
``` [4](#0-3) 

When `pre_result` is `Err(e)` (a `CompilationError` — e.g. the backend rejecting a module that structural preparation missed, explicitly called out as a "defense-in-depth" path in the spec) [5](#0-4) , the code returns an abort outcome directly, **never calling `after_loading_executable`**, so `contract_loading_base`/`contract_loading_bytes` (and thus any gas at all for the compile attempt) is never charged. This is the same defect pattern as the minievm precompile bug: real computation (`compile_uncached`, i.e. full wasmtime compilation of an up-to-max-size module) is performed before the point where gas is charged, and the error return path bypasses that charge.

Because the compiled/error result is cached per `ContractCacheKey` (keyed by code hash + config + vm hash) only in-process (`AnyCache`/on-disk cache) [6](#0-5) , this compile-and-fail work is repeated independently by **every validator** the first time each of them processes a receipt calling that contract, not amortized network-wide.

### Impact Explanation
An attacker can deploy a contract crafted to pass `prepare_v3`'s structural checks (size/limit checks enforced pre-compile) but that the wasmtime backend itself rejects during compilation (a `CompilationError`), then immediately invoke it with a `FunctionCall` receipt carrying minimal attached gas. Each validator that has not yet cached this contract pays the real wall-clock cost of compiling a maximal-size wasm module, while zero gas is burnt from the sender's account. This is a DoS/underpriced-computation vector: attacker-controlled unbounded computation with no corresponding gas cost, potentially causing chunk-application slowdowns or missed block-time targets across the validator set if repeated with many distinct contract hashes (defeating the cache).

### Likelihood Explanation
Reaching this path only requires an ordinary account to deploy a contract and issue a `FunctionCall` — no privileged or validator/P2P access needed. The main constraint is crafting wasm that reliably passes `prepare_v3` validation yet fails wasmtime's own compiler (a narrower, engine-version-dependent condition), and paying the storage/deploy cost for each distinct contract needed to force cache misses on other validators. This bounds — but does not eliminate — the attack's cost-effectiveness; feasibility depends on identifying inputs that trigger `CompilationError` at the backend level, which is plausible given the spec explicitly documents this as a known "defense-in-depth" fallback path.

### Recommendation
Charge the `contract_loading_base`/`contract_loading_bytes` fee (or an equivalent worst-case-bounded fee based on `wasm_code_bytes`) *before* attempting compilation, or immediately in the `Err(e)` branch of the `pre_result` match, rather than only on the success path. This aligns with the already-planned `fix_contract_loading_cost` pre-charge behavior; consider making that pre-charge (and closing the `CompilationError` gap specifically) apply unconditionally rather than being nightly-gated at PV 129.

### Proof of Concept
Not independently reproduced in this analysis (no execution environment available). The control-flow evidence supporting the claim is in `runtime/near-vm-runner/src/wasmtime_runner/mod.rs:686-834` and `runtime/near-vm-runner/src/logic/gas_counter.rs:229-272`, and is corroborated by the existing test `test_max_core_instance_size_breached`, which explicitly documents the pre-fix behavior as "zero-gas nop, loading work uncharged" for a `LoadingError` on an oversized-instance module [7](#0-6) . That test targets the deserialize-failure path (`fix_contract_loading_error`), which nearcore has already gated at PV 86 for this release; the `CompilationError` branch shown above uses the separate, still-unconditional `fix_contract_loading_cost`/`after_loading_executable` ordering, which remains unfixed on stable. Confirming an actual wasm input that produces `CompilationError` post-`prepare_v3` would require running the wasmtime backend directly, which is outside the scope of this read-only analysis.

### Citations

**File:** runtime/near-vm-runner/src/wasmtime_runner/mod.rs (L656-678)
```rust
    /// Inner Double-Checked-Lock: re-check + actual compile + cache write.
    fn compile_and_persist(
        &self,
        key: CryptoHash,
        code: &ContractCode,
        cache: &dyn ContractRuntimeCache,
        _lock_guard: MutexGuard<'_, ()>,
    ) -> Result<CachedArtifact, CacheError> {
        // The cache may have been populated while we waited on the per-key lock.
        if let Some(compiled) = read_cache(cache, &key)? {
            return Ok(compiled);
        }
        let serialized_or_error = self.compile_uncached(code);
        let record = CompiledContractInfo {
            wasm_bytes: code.code().len() as u64,
            compiled: match &serialized_or_error {
                Ok(serialized) => CompiledContract::Code(serialized.clone()),
                Err(err) => CompiledContract::CompileModuleError(err.clone()),
            },
        };
        cache.put(&key, record).map_err(CacheError::WriteError)?;
        Ok(serialized_or_error)
    }
```

**File:** runtime/near-vm-runner/src/wasmtime_runner/mod.rs (L812-833)
```rust
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
```

**File:** runtime/near-vm-runner/src/logic/gas_counter.rs (L234-255)
```rust
    #[cfg(feature = "wasmtime_vm")]
    pub(crate) fn before_loading_executable(
        &mut self,
        config: &near_parameters::vm::Config,
        method_name: &str,
        wasm_code_bytes: u64,
    ) -> std::result::Result<(), super::errors::FunctionCallError> {
        if method_name.is_empty() {
            let error = super::errors::FunctionCallError::MethodResolveError(
                super::errors::MethodResolveError::MethodEmptyName,
            );
            return Err(error);
        }
        if config.fix_contract_loading_cost {
            if self.add_contract_loading_fee(wasm_code_bytes).is_err() {
                let error =
                    super::errors::FunctionCallError::HostError(super::HostError::GasExceeded);
                return Err(error);
            }
        }
        Ok(())
    }
```

**File:** protocol-model/spec/contract-vm.md (L36-37)
```markdown
3. `before_loading_executable` (`gas_counter.rs:236`): reject empty `method_name` (`MethodResolveError::MethodEmptyName`); if `fix_contract_loading_cost` is set, pre-charge `add_contract_loading_fee` (`contract_loading_base` + `contract_loading_bytes * code_len`, `gas_counter.rs:225`) — on OOG return `HostError::GasExceeded` as an abort.
4. `after_loading_executable` (`gas_counter.rs:260`): if `fix_contract_loading_cost` is **not** set, charge the loading fee *after* loading instead (legacy ordering). On 2.13.0 mainnet `fix_contract_loading_cost` is `false` (the fix is nightly-only, PV 129), so the loading fee is charged post-load.
```

**File:** protocol-model/spec/contract-vm.md (L73-74)
```markdown
### 7. Compiled-contract caching
The cache key `ContractCacheKey::Version5` (`cache.rs:46`) hashes `code_hash`, `Config::non_crypto_hash()`, `vm_kind`, and the backend `vm_hash` (`get_contract_cache_key`, `:55`) — so any config/VM change invalidates all entries. Two levels: a per-VM in-memory `AnyCache` of loaded artifacts (`cache.rs:1058`, weight-bounded LRU) and an on-disk `FilesystemContractRuntimeCache` (`:302`) storing serialized executables or a `CompileModuleError`, with a size-bounded LRU eviction over the directory. Caching exists because compilation is expensive; the stored value carries `wasm_bytes` so the loading fee can be charged without re-reading source. `precompile_contract` (`cache.rs:1183`) warms the cache; `on_protocol_version_update` (`:862`) sweeps stale files at the `Wasmtime` cutover (PV 84).
```

**File:** protocol-model/spec/contract-vm.md (L105-105)
```markdown
- **Preparation defense-in-depth.** `CompilationError::WasmtimeCompileError` (`errors.rs:141`) is emitted if the backend rejects a module our own preparation pass should have caught.
```

**File:** runtime/near-vm-runner/src/tests/runtime_errors.rs (L50-61)
```rust
        match vm_kind {
            VMKind::Wasmtime => {
                // Pre-fix: zero-gas nop, loading work uncharged.
                let before = near_parameters::vm::Config {
                    fix_contract_loading_error: false,
                    ..base_config.clone()
                };
                let result = run(before);
                assert!(
                    matches!(result, Err(VMRunnerError::LoadingError(_))),
                    "pre-fix: expected LoadingError for oversized instance, got: {result:?}",
                );
```
