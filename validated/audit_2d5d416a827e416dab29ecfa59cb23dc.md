### Title
Cairo 0 Class Declaration Not Verified Against State Number in RPC Execution State Reader — (`File: crates/apollo_rpc_execution/src/state_reader.rs`)

### Summary

`get_compiled_class` in `ExecutionStateReader` skips the declaration-existence check for Cairo 0 (deprecated) contract classes when the class manager handle is present. For Cairo 1 classes the code explicitly calls `is_contract_class_declared` and returns `UndeclaredClassHash` if the class was not declared at the queried `state_number`. For Cairo 0 classes this check is entirely absent (marked with a `TODO`). As a result, any RPC execution path that queries a historical state number will silently use a Cairo 0 class that was not yet declared at that state, producing an authoritative-looking wrong execution result.

### Finding Description

In `crates/apollo_rpc_execution/src/state_reader.rs`, `get_compiled_class` has two branches when the class manager handle is present:

```rust
// Cairo 1 branch — declaration IS verified
ContractClass::V1(casm_contract_class) => {
    let is_declared = is_contract_class_declared(
        &self.storage_reader.begin_ro_txn()...,
        &class_hash,
        self.state_number,
    )...;
    if is_declared {
        Ok(RunnableCompiledClass::V1(casm_contract_class.try_into()?))
    } else {
        Err(StateError::UndeclaredClassHash(class_hash))
    }
}
// Cairo 0 branch — declaration is NOT verified
// TODO(shahak): Verify cairo0 as well after get_class_definition_block_number is fixed.
ContractClass::V0(deprecated_contract_class) => {
    Ok(RunnableCompiledClass::V0(deprecated_contract_class.try_into()?))
}
```

The class manager is a global store: once a class is compiled and stored (e.g., when block N is committed), it is available for all subsequent queries regardless of the `state_number` being evaluated. For Cairo 1 classes the code cross-checks the class manager result against the storage-backed declaration index at the requested `state_number`. For Cairo 0 classes this cross-check is unconditionally skipped, so the class manager's answer is accepted as-is. [1](#0-0) 

### Impact Explanation

Every RPC endpoint that executes or simulates transactions against a historical block uses `ExecutionStateReader::get_compiled_class`. Affected endpoints include `starknet_call`, `starknet_estimateFee`, `starknet_simulateTransactions`, and `starknet_traceTransaction`. When a caller queries one of these endpoints at a block number that precedes the declaration of a Cairo 0 class, the execution engine will load and run the undeclared class instead of returning `ContractNotFound` / `UndeclaredClassHash`. The returned execution result, fee estimate, or trace is therefore wrong — it reflects a state that never existed on-chain — while appearing authoritative to the caller.

This matches the allowed impact: **"High. RPC execution, fee estimation, tracing, simulation, or pending view returns an authoritative-looking wrong value."**

### Likelihood Explanation

The trigger requires only an unprivileged RPC call. Any user who:
1. Knows a Cairo 0 class hash that was declared at block N, and
2. Calls any of the above RPC methods with `block_id = N-1` (or any earlier block)

will exercise the missing check. Cairo 0 classes are present on Starknet Mainnet and Goerli from the pre-Sierra era, so the precondition is trivially satisfied. No special privilege, key material, or network position is required.

### Recommendation

Apply the same `is_contract_class_declared` guard to the Cairo 0 branch that is already applied to the Cairo 1 branch. The TODO comment acknowledges the intent; the fix is to resolve the underlying `get_class_definition_block_number` issue for deprecated classes (see `get_deprecated_class_definition_block_number` in storage) and then add:

```rust
ContractClass::V0(deprecated_contract_class) => {
    let is_declared = is_cairo0_class_declared(
        &self.storage_reader.begin_ro_txn()...,
        &class_hash,
        self.state_number,
    )?;
    if is_declared {
        Ok(RunnableCompiledClass::V0(deprecated_contract_class.try_into()?))
    } else {
        Err(StateError::UndeclaredClassHash(class_hash))
    }
}
```

Until the storage fix is available, the class manager handle path for Cairo 0 classes should fall through to the storage-backed `get_contract_class` path, which already performs the correct state-number-bounded lookup.

### Proof of Concept

1. On a node that has synced past block N (where a Cairo 0 class `C` was declared), issue:
   ```
   starknet_call {
     request: { contract_address: <addr deploying C>, entry_point_selector: ..., calldata: ... },
     block_id: { block_number: N-1 }
   }
   ```
2. The `ExecutionStateReader` is constructed with `state_number = right_after_block(N-1)`.
3. `get_compiled_class(C)` is called. The class manager returns `ContractClass::V0(...)` because it was stored when block N was committed.
4. The Cairo 0 branch returns `Ok(RunnableCompiledClass::V0(...))` without checking whether `C` was declared at `state_number`.
5. Execution proceeds using the undeclared class and returns a result, whereas the correct answer is `ContractNotFound` / `UndeclaredClassHash`.

The Cairo 1 path at the same state number would correctly return `Err(StateError::UndeclaredClassHash(class_hash))` due to the `is_contract_class_declared` guard. [2](#0-1) [3](#0-2)

### Citations

**File:** crates/apollo_rpc_execution/src/state_reader.rs (L115-141)
```rust
        if let Some((class_manager_client, run_time_handle)) = &self.class_manager_handle {
            let contract_class = run_time_handle
                .block_on(class_manager_client.get_executable(class_hash))
                .map_err(|e| StateError::StateReadError(e.to_string()))?
                .ok_or(StateError::UndeclaredClassHash(class_hash))?;

            return match contract_class {
                ContractClass::V1(casm_contract_class) => {
                    let is_declared = is_contract_class_declared(
                        &self.storage_reader.begin_ro_txn().map_err(storage_err_to_state_err)?,
                        &class_hash,
                        self.state_number,
                    )
                    .map_err(|e| StateError::StateReadError(e.to_string()))?;

                    if is_declared {
                        Ok(RunnableCompiledClass::V1(casm_contract_class.try_into()?))
                    } else {
                        Err(StateError::UndeclaredClassHash(class_hash))
                    }
                }
                // TODO(shahak): Verify cairo0 as well after get_class_definition_block_number is
                // fixed.
                ContractClass::V0(deprecated_contract_class) => {
                    Ok(RunnableCompiledClass::V0(deprecated_contract_class.try_into()?))
                }
            };
```
