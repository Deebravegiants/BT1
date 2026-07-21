### Title
Unimplemented `get_compiled_class_hash` in `SyncStateReader` causes gateway panic on Declare V2/V3 admission - (File: `crates/apollo_gateway/src/sync_state_reader.rs`)

### Summary

`SyncStateReader`, the production state reader used by the gateway for stateful transaction validation, implements `BlockifierStateReader::get_compiled_class_hash` with `todo!()`. Any code path during stateful validation that reaches this method will panic and crash the gateway process, blocking all transaction admission.

### Finding Description

In `crates/apollo_gateway/src/sync_state_reader.rs`, the `BlockifierStateReader` implementation for `SyncStateReader` leaves `get_compiled_class_hash` unimplemented:

```rust
fn get_compiled_class_hash(&self, _class_hash: ClassHash) -> StateResult<CompiledClassHash> {
    todo!()
}
``` [1](#0-0) 

This is a production code path, not a test stub. `SyncStateReader` is the live reader constructed from `SyncStateReaderFactory` whenever at least one block exists: [2](#0-1) 

The `SyncOrGenesisStateReader` enum delegates `get_compiled_class_hash` directly to `SyncStateReader`: [3](#0-2) 

By contrast, `GenesisStateReader` (used only before the first block) has a correct implementation returning `CompiledClassHash::default()`: [4](#0-3) 

The `StateReader` trait documents `get_compiled_class_hash` as: *"Returns the compiled class hash of the given class hash. Returns `CompiledClassHash::default()` if no v1_class is found."* [5](#0-4) 

The blockifier's `CachedState` calls through to the underlying reader's `get_compiled_class_hash` whenever the value is not already cached. For a Declare V2/V3 transaction, the blockifier checks whether the compiled class hash is already stored before writing the new one — this read goes through `CachedState` → `SyncStateReader::get_compiled_class_hash` → `todo!()` → **panic**. [6](#0-5) 

### Impact Explanation

When the gateway has processed at least one block (i.e., `SyncStateReader` is active rather than `GenesisStateReader`) and a user submits a Declare V2/V3 transaction, the stateful validation path invokes `get_compiled_class_hash` on `SyncStateReader`, triggering the `todo!()` panic. The gateway process crashes, halting all transaction admission. This matches the **High** impact: *"Mempool/gateway/RPC admission accepts invalid transactions or rejects valid transactions before sequencing."*

### Likelihood Explanation

Declare V2/V3 transactions are standard, unprivileged operations on Starknet. Any user can submit one. The gateway is reachable over the network. Once the chain has produced its first block, `SyncStateReader` is always used, so the vulnerable path is permanently active in normal operation.

### Recommendation

Implement `get_compiled_class_hash` in `SyncStateReader` analogously to the other state-read methods: query the state sync client for the compiled class hash at `self.block_number`, returning `CompiledClassHash::default()` when the class is not found (matching the trait contract). As a short-term guard, replace `todo!()` with `Ok(CompiledClassHash::default())` to match the documented default behaviour and prevent the panic, then follow up with a correct implementation backed by the state sync client.

### Proof of Concept

1. Wait for the sequencer to produce at least one block (so `SyncStateReaderFactory` returns a `SyncStateReader`, not `GenesisStateReader`).
2. Construct a valid Declare V2/V3 transaction (Sierra class + compiled class hash) signed by any funded account.
3. Submit it to the gateway's `add_transaction` endpoint.
4. The gateway's stateful validation runs the blockifier against `SyncStateReader`. The blockifier calls `get_compiled_class_hash` to check whether the compiled class hash is already stored.
5. `SyncStateReader::get_compiled_class_hash` executes `todo!()`, panicking with *"not yet implemented"*.
6. The gateway process crashes; all subsequent transaction submissions are rejected until the process is restarted. [1](#0-0) [3](#0-2)

### Citations

**File:** crates/apollo_gateway/src/sync_state_reader.rs (L197-199)
```rust
    fn get_compiled_class_hash(&self, _class_hash: ClassHash) -> StateResult<CompiledClassHash> {
        todo!()
    }
```

**File:** crates/apollo_gateway/src/sync_state_reader.rs (L349-351)
```rust
    fn get_compiled_class_hash(&self, _class_hash: ClassHash) -> StateResult<CompiledClassHash> {
        Ok(CompiledClassHash::default())
    }
```

**File:** crates/apollo_gateway/src/sync_state_reader.rs (L443-450)
```rust
    fn get_compiled_class_hash(&self, class_hash: ClassHash) -> StateResult<CompiledClassHash> {
        match self {
            Self::Sync(state_reader) => state_reader.get_compiled_class_hash(class_hash),
            Self::Genesis(genesis_state_reader) => {
                genesis_state_reader.get_compiled_class_hash(class_hash)
            }
        }
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

**File:** crates/blockifier/src/state/state_api.rs (L44-46)
```rust
    /// Returns the compiled class hash of the given class hash.
    /// Returns CompiledClassHash::default() if no v1_class is found for the given class hash.
    fn get_compiled_class_hash(&self, class_hash: ClassHash) -> StateResult<CompiledClassHash>;
```

**File:** crates/blockifier/src/state/cached_state.rs (L1-5)
```rust
use std::cell::{Ref, RefCell};
use std::collections::{HashMap, HashSet};

use indexmap::IndexMap;
use starknet_api::abi::abi_utils::get_fee_token_var_address;
```
