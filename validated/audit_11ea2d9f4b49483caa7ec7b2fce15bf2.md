Now I have enough information to make a definitive assessment. Let me trace the full exploit path precisely.

### Title
P2P Class Sync Stores Wrong-Body Class Under Computed Hash, Causing RPC `get_class` to Return `CLASS_HASH_NOT_FOUND` for Legitimately Declared Classes — (`crates/apollo_p2p_sync/src/client/class.rs`)

---

### Summary

A malicious p2p peer can serve a syntactically valid but wrong Sierra class body `C'` (where `hash(C') = H' ≠ H`) paired with a legitimate state-diff class hash `H`. The p2p sync client's `write_to_storage` passes only the class body to `add_class` and **ignores the returned computed hash**. The class manager stores `C'` under `H'`, leaving nothing under `H`. Subsequently, `starknet_getClass(block_id=N, H)` returns `CLASS_HASH_NOT_FOUND` for a class that is legitimately declared in block `N`.

---

### Finding Description

**Step 1 — `parse_data_for_block` accepts `(C', H)` without body-hash verification.**

The peer sends the tuple `(api_contract_class=C', class_hash=H)`. The only check performed is whether `H` appears in the state diff (`is_declared`). There is no check that `hash(C') == H`. [1](#0-0) 

**Step 2 — `write_to_storage` calls `add_class(C')` and discards the returned hash.**

The loop variable `class_hash` holds `H` (from the state diff), but only `class` (the body `C'`) is forwarded to `add_class`. The `Ok(ClassHashes { class_hash: H', ... })` return value is silently discarded. The developer-acknowledged TODO confirms this gap: [2](#0-1) 

**Step 3 — `add_class` computes the hash from the body and stores under `H'`.**

`add_class` derives `class_hash` by calling `sierra_class.calculate_class_hash()` on the received body, yielding `H'`. It then stores `C'` under `H'`. Nothing is ever written under `H`. [3](#0-2) 

**Step 4 — RPC `get_class(N, H)` returns `CLASS_HASH_NOT_FOUND`.**

The RPC handler first calls `class_manager_client.get_sierra(H)` → `None` (class manager has nothing under `H`). It then falls through to `state_reader.get_class_definition_at` → `None` (p2p-synced nodes do not store Sierra bodies in state storage; they rely entirely on the class manager). The final fallback to `get_deprecated_class_definition_at` also returns `None`. The handler returns `CLASS_HASH_NOT_FOUND`. [4](#0-3) 

---

### Impact Explanation

Any client querying `starknet_getClass` for a legitimately declared class `H` on a p2p-synced node receives an authoritative-looking `CLASS_HASH_NOT_FOUND` error. Additionally, the execution state reader's `get_compiled_class` path calls `class_manager_client.get_executable(H)` → `None`, causing `StateError::UndeclaredClassHash(H)` for any contract invocation that requires class `H`. This corrupts both the RPC view and the execution environment for the affected class on the synced node.

---

### Likelihood Explanation

Any unauthenticated p2p peer that the syncing node connects to can trigger this. The p2p sync protocol is a low-trust data path explicitly listed in the allowed attack surfaces. The malicious peer only needs to serve one block's class response with a mismatched body. The node will accept it, advance the class manager marker, and the corruption is permanent until the node resyncs from scratch.

---

### Recommendation

In `write_to_storage`, after `add_class` succeeds, compare the returned `ClassHashes::class_hash` against the expected `class_hash` from the state diff. If they differ, treat it as a `BadPeerError`, report the peer, and abort sync for that session — consistent with how other peer misbehaviors are handled in `parse_data_for_block`.

```rust
let class_hashes = loop {
    match class_manager_client.add_class(class.clone()).await {
        Ok(hashes) => break hashes,
        Err(err) => { warn!(...); }
    }
};
if class_hashes.class_hash != class_hash {
    return Err(P2pSyncClientError::BadPeer(...));
}
```

---

### Proof of Concept

1. Syncing node requests classes for block `N` which declared class `H`.
2. Malicious peer responds with `(C', H)` where `C'` is a valid Sierra class with `hash(C') = H' ≠ H`.
3. `parse_data_for_block` accepts it (H is in state diff).
4. `write_to_storage` calls `add_class(C')` → class manager stores `C'` under `H'`; return value ignored.
5. `update_class_manager_block_marker` advances past block `N` — corruption is committed.
6. `starknet_getClass(block_id=N, class_hash=H)`:
   - `get_sierra(H)` → `None`
   - `get_class_definition_at(state_number, H)` → `None`
   - `get_deprecated_class_definition_at(state_number, H)` → `None`
   - Returns `CLASS_HASH_NOT_FOUND` ← wrong authoritative response for a declared class.

### Citations

**File:** crates/apollo_p2p_sync/src/client/class.rs (L35-48)
```rust
            for (class_hash, class) in self.0 {
                // We can't continue without writing to the class manager, so we'll keep retrying
                // until it succeeds.
                // TODO(shahak): Test this flow.
                // TODO(shahak): Verify class hash matches class manager response. report if not.
                // TODO(shahak): Try to avoid cloning. See if ClientError can contain the request.
                while let Err(err) = class_manager_client.add_class(class.clone()).await {
                    warn!(
                        "Failed writing class with hash {class_hash:?} to class manager. Trying \
                         again. Error: {err:?}"
                    );
                    trace!("Class: {class:?}");
                    // TODO(shahak): Consider sleeping here.
                }
```

**File:** crates/apollo_p2p_sync/src/client/class.rs (L131-148)
```rust
                let (is_declared, duplicate_class) = match api_contract_class {
                    ApiContractClass::ContractClass(contract_class) => (
                        declared_classes.get(&class_hash).is_some(),
                        declared_classes_result.insert(class_hash, contract_class).is_some(),
                    ),
                    ApiContractClass::DeprecatedContractClass(deprecated_contract_class) => (
                        deprecated_declared_classes.contains(&class_hash),
                        deprecated_declared_classes_result
                            .insert(class_hash, deprecated_contract_class)
                            .is_some(),
                    ),
                };

                if !is_declared {
                    return Err(ParseDataError::BadPeer(BadPeerError::ClassNotInStateDiff {
                        class_hash,
                    }));
                }
```

**File:** crates/apollo_class_manager/src/class_manager.rs (L71-113)
```rust
    pub async fn add_class(&mut self, class: RawClass) -> ClassManagerResult<ClassHashes> {
        let sierra_class = SierraContractClass::try_from(&class)?;
        let class_hash = sierra_class.calculate_class_hash();
        if let Ok(Some(executable_class_hash_v2)) =
            self.classes.get_executable_class_hash_v2(class_hash)
        {
            // Class already exists.
            return Ok(ClassHashes { class_hash, executable_class_hash_v2 });
        }

        let compilation_start_time = Instant::now();
        let (raw_executable_class, executable_class_hash_v2) =
            self.compiler.compile(class.clone()).await.map_err(|err| match err {
                SierraCompilerClientError::SierraCompilerError(error) => {
                    ClassManagerError::SierraCompiler { class_hash, error }
                }
                SierraCompilerClientError::ClientError(error) => {
                    ClassManagerError::Client(error.to_string())
                }
            })?;
        debug!(
            %class_hash,
            compiled_class_hash = %executable_class_hash_v2,
            compilation_elapsed_ms = compilation_start_time.elapsed().as_millis(),
            class_size_bytes =
                class.size().map_or("Failed to get class size".to_owned(), |size| size.to_string()),
            casm_size_bytes =
                raw_executable_class.size().map_or("Failed to get casm size".to_owned(), |size| size.to_string()),
            "Finished compiling class."
        );

        self.validate_class_length(&raw_executable_class)?;
        Self::validate_class_version(&sierra_class)?;
        self.classes.set_class(
            class_hash,
            class,
            executable_class_hash_v2,
            raw_executable_class,
        )?;

        let class_hashes = ClassHashes { class_hash, executable_class_hash_v2 };
        Ok(class_hashes)
    }
```

**File:** crates/apollo_rpc/src/v0_8/api/api_impl.rs (L620-657)
```rust
        // If class manager supplied, first check with it.
        if let Some(class_manager_client) = &self.class_manager_client {
            let optional_sierra_contract_class = class_manager_client
                .get_sierra(class_hash)
                .await
                .map_err(internal_server_error_with_msg)?;

            if let Some(sierra_contract_class) = optional_sierra_contract_class {
                let optional_class_definition_block_number = state_reader
                    .get_class_definition_block_number(&class_hash)
                    .map_err(internal_server_error)?;

                // Check if this class exists in the Cairo1 classes table.
                if optional_class_definition_block_number.is_some()
                    && optional_class_definition_block_number <= Some(block_number)
                {
                    return Ok(GatewayContractClass::Sierra(sierra_contract_class.into()));
                } else {
                    return Err(ErrorObjectOwned::from(CLASS_HASH_NOT_FOUND));
                }
            }
        }

        // The class might be a deprecated class. Search it first in the declared classes and if not
        // found, search in the deprecated classes.
        if let Some(class) = state_reader
            .get_class_definition_at(state_number, &class_hash)
            .map_err(internal_server_error)?
        {
            Ok(GatewayContractClass::Sierra(class.into()))
        } else {
            let class = state_reader
                .get_deprecated_class_definition_at(state_number, &class_hash)
                .map_err(internal_server_error)?
                .ok_or_else(|| ErrorObjectOwned::from(CLASS_HASH_NOT_FOUND))?;
            Ok(GatewayContractClass::Cairo0(class.try_into().map_err(internal_server_error)?))
        }
    }
```
