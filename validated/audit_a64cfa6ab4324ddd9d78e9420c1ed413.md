### Title
`SyncStateReader::get_compiled_class_hash` Panics via `todo!()` in Production Gateway Stateful Validation Path — (`File: crates/apollo_gateway/src/sync_state_reader.rs`)

### Summary

`SyncStateReader`, the production `BlockifierStateReader` implementation used by the gateway for stateful transaction validation, implements `get_compiled_class_hash` with a bare `todo!()` macro. Any code path during gateway stateful validation that reads the compiled class hash of a class not already in the `CachedState` cache will unconditionally panic, crashing the gateway process and halting all transaction admission.

### Finding Description

`SyncStateReader` implements the `BlockifierStateReader` trait for the gateway's stateful validation path. All methods are properly implemented except `get_compiled_class_hash`, which is a stub:

```rust
fn get_compiled_class_hash(&self, _class_hash: ClassHash) -> StateResult<CompiledClassHash> {
    todo!()
}
``` [1](#0-0) 

`SyncStateReader` is instantiated in `SyncStateReaderFactory::get_blockifier_state_reader_and_gateway_fixed_block_from_latest_block` and passed into `StatefulTransactionValidatorFactory::instantiate_validator`, which wraps it in `StateReaderAndContractManager` and then in `CachedState`: [2](#0-1) 

`StateReaderAndContractManager::get_compiled_class_hash` unconditionally delegates to the inner `state_reader`: [3](#0-2) 

`CachedState::get_compiled_class_hash` calls through to the underlying state reader on a cache miss: [4](#0-3) 

The call chain is:

```
gateway stateful validation
  → CachedState<StateReaderAndContractManager<SyncStateReader>>::get_compiled_class_hash
    → StateReaderAndContractManager::get_compiled_class_hash
      → SyncStateReader::get_compiled_class_hash
        → todo!()  ← PANIC
```

The trigger is any Declare V2/V3 transaction submitted to the gateway whose validation path reads the compiled class hash of a class not yet in the `CachedState` write cache. During `try_declare`, `set_compiled_class_hash` is called to write the new compiled class hash, but the initial value for that slot was never populated. When `to_state_diff()` is subsequently called (e.g., inside `StatefulValidator::validate` or `TransactionExecutor::execute`), `CachedState` must fetch the initial value from the underlying state reader, triggering the `todo!()` panic. [5](#0-4) 

### Impact Explanation

A single Declare V2/V3 transaction submitted to the gateway causes the gateway process to panic. Because `todo!()` is an unconditional panic (not a recoverable error), the gateway crashes entirely. All subsequent transaction admission — Invoke, DeployAccount, Declare — is halted until the process is restarted. This matches the **High** impact category: *Mempool/gateway/RPC admission rejects valid transactions before sequencing*.

### Likelihood Explanation

Declare V2/V3 transactions are standard, unprivileged user operations on Starknet. Any user can submit one. The `SyncStateReaderFactory` is the production factory wired into the gateway component. There is no guard, fallback, or feature flag preventing `get_compiled_class_hash` from being called on `SyncStateReader`. The `todo!()` is not behind a `#[cfg(test)]` gate. Likelihood is **High**.

### Recommendation

Implement `SyncStateReader::get_compiled_class_hash` by querying the state sync client for the compiled class hash at the stored `block_number`, analogous to how `get_nonce_at` and `get_class_hash_at` are implemented. If the state sync client does not yet expose a `get_compiled_class_hash_at` RPC, add that endpoint and implement the method, or return `CompiledClassHash::default()` for Cairo 0 / undeclared classes consistent with the contract of the trait.

### Proof of Concept

1. Start the sequencer with the gateway component enabled.
2. Submit a valid Declare V2 or V3 transaction to the gateway's `add_declare_transaction` endpoint.
3. The gateway's stateful validator calls `StatefulTransactionValidatorFactory::instantiate_validator`, creating a `CachedState<StateReaderAndContractManager<SyncStateReader>>`.
4. `perform_validations` dispatches to `self.execute(tx)` for the Declare transaction.
5. Inside execution, `try_declare` calls `state.set_compiled_class_hash(class_hash, compiled_class_hash)` — writing to the cache without first reading the initial value.
6. `to_state_diff()` is called; `CachedState` finds no initial value for the class hash and calls `self.state.get_compiled_class_hash(class_hash)`.
7. This reaches `SyncStateReader::get_compiled_class_hash` → `todo!()` → thread panic → gateway process crash.
8. All subsequent transaction submissions are rejected until the gateway is restarted. [1](#0-0) [6](#0-5) [3](#0-2)

### Citations

**File:** crates/apollo_gateway/src/sync_state_reader.rs (L197-199)
```rust
    fn get_compiled_class_hash(&self, _class_hash: ClassHash) -> StateResult<CompiledClassHash> {
        todo!()
    }
```

**File:** crates/apollo_gateway/src/sync_state_reader.rs (L539-549)
```rust
        let blockifier_state_reader = SyncStateReader::from_number(
            self.shared_state_sync_client.clone(),
            self.class_manager_client.clone(),
            latest_block_number,
            self.runtime.clone(),
        );
        let gateway_fixed_block_sync_state_client = GatewayFixedBlockSyncStateClient::new(
            self.shared_state_sync_client.clone(),
            latest_block_number,
        );
        Ok((blockifier_state_reader.into(), gateway_fixed_block_sync_state_client.into()))
```

**File:** crates/blockifier/src/state/state_reader_and_contract_manager.rs (L155-157)
```rust
    fn get_compiled_class_hash(&self, class_hash: ClassHash) -> StateResult<CompiledClassHash> {
        self.state_reader.get_compiled_class_hash(class_hash)
    }
```

**File:** crates/blockifier/src/state/cached_state.rs (L204-215)
```rust
    fn get_compiled_class_hash(&self, class_hash: ClassHash) -> StateResult<CompiledClassHash> {
        let mut cache = self.cache.borrow_mut();

        if cache.get_compiled_class_hash(class_hash).is_none() {
            let compiled_class_hash = self.state.get_compiled_class_hash(class_hash)?;
            cache.set_compiled_class_hash_initial_value(class_hash, compiled_class_hash);
        }

        let compiled_class_hash = cache
            .get_compiled_class_hash(class_hash)
            .unwrap_or_else(|| panic!("Cannot retrieve '{class_hash:?}' from the cache."));
        Ok(*compiled_class_hash)
```

**File:** crates/blockifier/src/transaction/transactions.rs (L387-407)
```rust
fn try_declare<S: State>(
    tx: &DeclareTransaction,
    state: &mut S,
    class_hash: ClassHash,
    compiled_class_hash: Option<CompiledClassHash>,
) -> TransactionExecutionResult<()> {
    match state.get_compiled_class(class_hash) {
        Err(StateError::UndeclaredClassHash(_)) => {
            // Class is undeclared; declare it.
            state.set_contract_class(class_hash, tx.contract_class().try_into()?)?;
            if let Some(compiled_class_hash) = compiled_class_hash {
                state.set_compiled_class_hash(class_hash, compiled_class_hash)?;
            }
            Ok(())
        }
        Err(error) => Err(error)?,
        Ok(_) => {
            // Class is already declared, cannot redeclare.
            Err(TransactionExecutionError::DeclareTransactionError { class_hash })
        }
    }
```
