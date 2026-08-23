### Title
LinkError/LoadingError conversion embeds unbounded attacker-controlled `msg` into persisted `ExecutionError`, and the linking work that produces it can occur before the contract-loading fee is charged - (File: runtime/runtime/src/conversions.rs)

### Summary
`function_call_error::convert` (`runtime/runtime/src/conversions.rs:83-86`) turns `FunctionCallError::LinkError{msg}`/`LoadingError{msg}` into `FunctionCallError::ExecutionError(format!(...))`, which is stored verbatim in the `ActionError`/`ExecutionOutcome` and thus in the chunk witness. The `msg` originates from `wasmtime::Error::to_string()` in `IntoVMError::into_vm_error` (`runtime/near-vm-runner/src/wasmtime_runner/mod.rs:373-422`), which for unresolved-import failures echoes the offending import/export name straight from the attacker's wasm binary. Wasm import/export names are allowed up to `100_000` bytes each (per `docs/RuntimeSpec/Preparation.md:52`), so a crafted `DeployContract` can produce a large, attacker-controlled string that ends up persisted with no dedicated per-byte gas charge tied to the message length.

### Finding Description
The conversion path is:
`runtime/runtime/src/conversions.rs:83-86`
```rust
From::LinkError { msg } => Self::ExecutionError(format!("Link Error: {}", msg)),
From::LoadingError { msg } => Self::ExecutionError(format!("Loading Error: {}", msg)),
```
`msg` is fully attacker-influenced: it is produced by `cause.to_string()` in `IntoVMError::into_vm_error` (`runtime/near-vm-runner/src/wasmtime_runner/mod.rs:416-421`), which for `wasmtime::UnknownImportError` is a fixed short string, but for other link failures (e.g. wrong signature, module mismatch) falls through to `cause.to_string()`, which for wasmtime's linker errors typically embeds the module/name string taken directly from the wasm binary's import/export section. The wasm validation limits in `docs/RuntimeSpec/Preparation.md:52` explicitly allow each such UTF-8 string (e.g., an export or import name) to be up to `100_000` bytes, well within `max_contract_size` (4 MiB, `core/parameters/res/runtime_configs/parameters.yaml:279`).

Critically, `FunctionCallError::size_bytes_approximate()` (`runtime/near-vm-runner/src/logic/errors.rs:64-77`) is defined and does account for `msg.len()`, but it is used only as an **in-memory cache eviction weight** (`runtime/near-vm-runner/src/wasmtime_runner/mod.rs:756`, `766`, `778`) — not as a gas cost. There is no per-byte gas charge keyed to `msg.len()` when the `LinkError`/`LoadingError` is produced or persisted.

Additionally, per `runtime/near-vm-runner/src/wasmtime_runner/mod.rs:734-793` and the ordering documented in `protocol-model/spec/contract-vm.md` §3, the missing-memory-export check and `linker.instantiate_pre` link failure (both producing `LinkError`) happen in step 2, **before** `before_loading_executable`/`after_loading_executable` (step 3/4) which is where `add_contract_loading_fee` (`contract_loading_base + contract_loading_bytes * code_len`) is charged (`runtime/near-vm-runner/src/logic/gas_counter.rs:225`, `:248`, `:260`). When `PreparedContract::run` sees `PreparationResult::OutcomeAbort`/`OutcomeAbortButNopInOldProtocol` it returns immediately (`runtime/near-vm-runner/src/wasmtime_runner/mod.rs:1010-1017`) without ever reaching the loading-fee charging code. So a `LinkError` produced this way can bypass the one gas charge (`contract_loading_bytes * code_len`) that is proportional to contract size and could otherwise have offset the cost of generating/serializing a large error string.

### Impact Explanation
This maps to NEAR's "gas or storage metering bypass" / "unbounded resource use" bounty class. Concretely: an attacker can deploy a contract containing a crafted import (or an export whose resolution fails) with a name close to the `100_000`-byte-per-name limit, engineered to trigger `LinkError`/`LoadingError`. Every subsequent cheap `FunctionCall` (minimal `method_name`/`args`, so minimal `function_call_cost_per_byte` charge) against that contract deterministically fails to link and produces an `ExecutionOutcome` containing an `ExecutionError(String)` of up to tens of KB, persisted per-receipt into the outcome/witness, without a gas charge sized to that string. Because the link failure occurs before the loading fee is charged (in the `OutcomeAbort` fast path), the per-byte-of-code fee that would otherwise be loosely correlated to this cost may also be skipped. The net effect is uncharged growth of `ExecutionOutcome`/chunk witness data per call, at the cost of only a fixed, small `FunctionCall` base fee.

### Likelihood Explanation
Feasibility is high and fully within unprivileged capability: it requires only a `DeployContract` action with a crafted wasm binary (well under `max_contract_size` = 4 MiB) containing one or more import/export names near the documented `100_000`-byte limit, followed by ordinary `FunctionCall` actions. No special privileges, timing, or race conditions are needed, and the failure is deterministic and repeatable on every call to the deployed contract.

### Recommendation
- Bound the length of `msg` copied into `FunctionCallError::LinkError`/`LoadingError` (and subsequently `ExecutionError`) before it is persisted, e.g. truncate to a small fixed cap (matching the treatment of `max_total_log_length` for logs) independent of attacker-controlled identifier lengths.
- Ensure a gas/fee charge proportional to `msg.len()` (or to the truncated cap) is applied whenever an `ExecutionError` string is constructed from `LinkError`/`LoadingError`, mirroring how `size_bytes_approximate()` is already computed but currently only used for cache weighting.
- Reorder or guarantee that `add_contract_loading_fee` (proportional to `code_len`) is charged before any `OutcomeAbort` fast path returns for `LinkError`, so the code-size-proportional cost cannot be bypassed by link failures.

### Proof of Concept
Unit/integration test plan:
1. Build a wasm module (e.g., via `wasm_encoder`) with a single import from a bogus module name or an import whose name is a ~90 KB string designed to fail wasmtime linking (e.g., unresolved import), keeping total code size under `max_contract_size`.
2. Deploy the contract via `DeployContractAction`.
3. Call it via a `FunctionCallAction` with minimal `method_name`/`args`.
4. Assert: `outcome.aborted` is `Some(FunctionCallError::LinkError{msg})` with `msg.len()` on the order of the crafted import name.
5. Convert via `crate::conversions::Convert::convert` and assert the resulting `ExecutionError(String)` length is unbounded (equal to `msg.len()` plus a small prefix), demonstrating no truncation.
6. Assert the gas charged (`burnt_gas`/`used_gas`) for this call does **not** scale with `msg.len()` and is close to the fixed base `function_call_cost` (demonstrating the metering gap), and separately verify whether `contract_loading_bytes * code_len` was actually charged for this failing call (to confirm/deny the loading-fee-bypass sub-finding).