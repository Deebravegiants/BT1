### Title
Zero-gas nop outcome on `VMRunnerError::LoadingError` allows chunk gas limit bypass - (File: `runtime/runtime/src/function_call.rs`)

### Summary

When the Wasmtime VM fails to deserialize a compiled contract module (e.g., a contract with 100k globals that breaches `max_core_instance_size`), `execute_function_call` in `function_call.rs` maps the `VMRunnerError::LoadingError` to `VMOutcome::nop_outcome(...)` with `burnt_gas = 0` and `used_gas = 0`. No gas is charged for the loading work actually performed by validators. This is the direct analog of the reported minievm bug: an error path that returns early without consuming gas, corrupting the gas accounting invariant.

### Finding Description

In `runtime/runtime/src/function_call.rs`, the match arm for `VMRunnerError::LoadingError` returns a zero-gas nop outcome:

```rust
Err(VMRunnerError::LoadingError(msg)) => {
    return Ok(VMOutcome::nop_outcome(FunctionCallError::LoadingError { msg }));
}
``` [1](#0-0) 

`VMOutcome::nop_outcome` explicitly sets `burnt_gas: Gas::ZERO` and `used_gas: Gas::ZERO`: [2](#0-1) 

This `VMRunnerError::LoadingError` is produced by the Wasmtime runner in `wasmtime_runner/mod.rs` when `Module::deserialize` fails and the `fix_contract_loading_error` flag is `false` (the default):

```rust
return Err(VMRunnerError::LoadingError(err.to_string()));
``` [3](#0-2) 

The `fix_contract_loading_error` flag defaults to `false` in the base parameters: [4](#0-3) 

The protocol upgrade file `86.yaml` introduces the fix by setting `fix_contract_loading_error: { old: false, new: true }`: [5](#0-4) 

The `FixContractLoadingError` protocol feature is defined in `version.rs` and described as charging the contract-loading fee instead of producing a zero-gas nop: [6](#0-5) 

The test in `runtime_errors.rs` explicitly documents the pre-fix behavior as "zero-gas nop, loading work uncharged": [7](#0-6) 

The trigger is a contract with 100k globals, which causes `Module::deserialize` to fail because the instance data (800 kB) exceeds the default `max_core_instance_size` (1 MiB) in the Wasmtime pooling allocator.

After `execute_function_call` returns the zero-gas outcome, `action_function_call` adds `outcome.burnt_gas` (zero) to the receipt result: [8](#0-7) 

### Impact Explanation

The corrupted protocol value is `gas_burnt` in the execution outcome — it is `0` instead of the actual contract-loading cost (`contract_loading_base + contract_loading_bytes * wasm_size`). This produces three concrete protocol-level corruptions:

1. **Chunk gas limit bypass**: The chunk's total `gas_burnt` is understated. The chunk producer can include more receipts than the gas limit should permit, because the loading work does not count against the limit. All validators agree on the zero value (deterministic), so there is no consensus divergence, but the gas limit invariant — that gas_burnt accurately bounds validator work per chunk — is violated.
2. **Incorrect gas refund**: The signer receives a full refund for gas that should have been burnt, paying nothing for the loading work performed on their behalf.
3. **Zero contract reward**: The contract owner receives no `burnt_gas_reward` for the loading work, violating the reward accounting invariant.

An attacker can deploy a contract with 100k globals (well within `max_contract_size = 4 MiB`) and spam calls to it. Each call forces validators to perform the full `Module::deserialize` attempt (CPU + memory) without it counting against the chunk gas limit, allowing the attacker to consume validator resources at a fraction of the intended cost.

### Likelihood Explanation

The trigger is fully attacker-controlled: any unprivileged user can deploy a contract with 100k globals via a standard `DeployContract` transaction and call it via the public RPC. The failure is deterministic and reproducible. The vulnerability is active when the Wasmtime VM is in use and `fix_contract_loading_error` is `false` (pre-protocol-version-86). The `86.yaml` upgrade file confirms this is a known pre-fix state in the current codebase.

### Recommendation

The fix is already present as the `FixContractLoadingError` protocol feature. Activating protocol version 86 enables `fix_contract_loading_error: true`, which causes the Wasmtime runner to convert the loading failure into a gas-bearing `FunctionCallError::LoadingError` abort (via `VMOutcome::abort`) instead of a zero-gas nop. As defense-in-depth, the `VMRunnerError::LoadingError` arm in `function_call.rs` (line 312–313) should also be updated to charge the loading fee before returning, so that any future code path that produces this error variant is also covered.

### Proof of Concept

1. Deploy a contract built from `near_test_contracts::contract_with_num_globals(100_000)` — this produces a valid WASM binary within `max_contract_size` but with instance data exceeding `max_core_instance_size`.
2. Submit a `FunctionCall` transaction targeting any method on this contract with `prepaid_gas = 300 TGas`.
3. Observe the execution outcome: `gas_burnt = 0` (only the base `new_action_receipt` execution fee is charged), while the Wasmtime runner performed the full `Module::deserialize` attempt.
4. The signer receives a full refund. Repeat at high frequency; each call consumes validator CPU without counting against the chunk gas limit.

### Citations

**File:** runtime/runtime/src/function_call.rs (L140-148)
```rust
    result.gas_burnt = result.gas_burnt.checked_add_result(outcome.burnt_gas)?;
    result.gas_burnt_for_function_call =
        result.gas_burnt_for_function_call.checked_add_result(outcome.burnt_gas)?;
    // Runtime in `generate_refund_receipts` takes care of using proper value for refunds.
    // It uses `gas_used` for success and `gas_burnt` for failures. So it's not an issue to
    // return a real `gas_used` instead of the `gas_burnt` into `ActionResult` even for
    // `FunctionCall`s error.
    result.gas_used = result.gas_used.checked_add_result(outcome.used_gas)?;
    result.compute_usage = safe_add_compute(result.compute_usage, outcome.compute_usage)?;
```

**File:** runtime/runtime/src/function_call.rs (L312-314)
```rust
        Err(VMRunnerError::LoadingError(msg)) => {
            return Ok(VMOutcome::nop_outcome(FunctionCallError::LoadingError { msg }));
        }
```

**File:** runtime/near-vm-runner/src/logic/logic.rs (L4565-4581)
```rust
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
```

**File:** runtime/near-vm-runner/src/wasmtime_runner/mod.rs (L755-763)
```rust
                        if self.config.fix_contract_loading_error {
                            let err = FunctionCallError::LoadingError { msg: err.to_string() };
                            return Ok((
                                err.size_bytes_approximate() as u64,
                                to_any((wasm_bytes, Ok(Err(err)))),
                            ));
                        }
                        return Err(VMRunnerError::LoadingError(err.to_string()));
                    }
```

**File:** core/parameters/res/runtime_configs/parameters.yaml (L291-291)
```yaml
fix_contract_loading_error: false
```

**File:** core/parameters/res/runtime_configs/86.yaml (L1-1)
```yaml
fix_contract_loading_error: { old: false, new: true }
```

**File:** core/primitives-core/src/version.rs (L442-446)
```rust
    /// Charge the contract-loading fee (and finalize as a gas-bearing abort
    /// rather than a zero-gas nop) when a compiled module fails to load at
    /// `Module::deserialize`.
    FixContractLoadingError,
}
```

**File:** runtime/near-vm-runner/src/tests/runtime_errors.rs (L14-58)
```rust
/// Compile and load a contract with 100k globals.
///
/// Each global produces 8 bytes of instance data, so globals alone add 800kB.
/// In total, that breaches the (default) limit of 1MiB for
/// `max_core_instance_size` for the Wasmtime pooling allocator, so loading the
/// module at `Module::deserialize` fails.
///
/// Pre-`FixContractLoadingError` this surfaces as `VMRunnerError::LoadingError`,
/// which the runtime maps to a zero-gas nop — the contract-loading work is left
/// uncharged. Post-feature the same failure finalizes as a gas-bearing abort
/// that charges the contract-loading fee. Either way it must not panic / crash
/// the node.
#[test]
fn test_max_core_instance_size_breached() {
    let wasm = near_test_contracts::contract_with_num_globals(100_000);

    super::with_vm_variants(|vm_kind| {
        let run = |config: near_parameters::vm::Config| {
            let code = ContractCode::new(wasm.clone(), None);
            let config = Arc::new(config);
            let fees = Arc::new(RuntimeFeesConfig::test());
            let mut ext = MockedExternal::with_code(code.clone_for_tests());
            let context = super::create_context(vec![]);
            let gas_counter = context.make_gas_counter(&config);
            vm_kind
                .runtime(config)
                .unwrap()
                .prepare(&ext, None, gas_counter, "main")
                .run(&mut ext, &context, fees)
        };

        let base_config = super::test_vm_config(Some(vm_kind));

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
