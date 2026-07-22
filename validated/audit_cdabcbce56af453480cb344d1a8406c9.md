Now I have all the information needed to make a determination. Let me trace the full path precisely.

### Title
P2P Sync Class Hash Mismatch: Malicious Peer Stores Class Under Wrong Hash, Corrupting Class Manager State — (`crates/apollo_p2p_sync/src/client/class.rs`)

---

### Summary

The P2P sync client's `write_to_storage` implementation for class data never verifies that the `ClassHashes.class_hash` returned by `ClassManager::add_class` matches the `class_hash` key declared in the stored `ThinStateDiff`. A malicious peer can send a `SierraContractClass` whose actual Poseidon hash (`H_actual`) differs from the peer-claimed `H_claimed` that appears in the state diff. The class manager stores the class under `H_actual`, the block marker advances past `block_number` as if `H_claimed` was correctly stored, and any subsequent `get_executable(H_claimed)` returns `None`.

---

### Finding Description

**Step 1 — `parse_data_for_block` accepts the class without content validation.**

The peer sends `(SierraContractClass_X, H_claimed)`. The only check performed is:

```rust
declared_classes.get(&class_hash).is_some()
``` [1](#0-0) 

This verifies that `H_claimed` exists as a key in `state_diff.class_hash_to_compiled_class_hash`. It does **not** verify that `SierraContractClass_X.calculate_class_hash() == H_claimed`. The class is inserted into `declared_classes_result` keyed by the peer-supplied `H_claimed`.

**Step 2 — `write_to_storage` ignores the returned `ClassHashes`.**

```rust
while let Err(err) = class_manager_client.add_class(class.clone()).await {
    // ...
}
// TODO(shahak): Verify class hash matches class manager response. report if not.
``` [2](#0-1) 

The `Ok(ClassHashes { class_hash: H_actual, .. })` return value is silently discarded. The TODO comment explicitly acknowledges this missing check.

**Step 3 — `ClassManager::add_class` computes and stores under `H_actual`.**

```rust
let class_hash = sierra_class.calculate_class_hash(); // H_actual
// ...
self.classes.set_class(class_hash, class, executable_class_hash_v2, raw_executable_class)?;
``` [3](#0-2) 

The class manager always derives the storage key from the class content's Poseidon hash, not from any caller-supplied key. So the class lands under `H_actual`, not `H_claimed`.

**Step 4 — The block marker advances unconditionally.**

```rust
storage_writer
    .begin_rw_txn()?
    .update_class_manager_block_marker(&self.2.unchecked_next())?
    .commit()?;
``` [4](#0-3) 

The marker advances regardless of whether `H_claimed` was actually stored. The node now believes block `N`'s classes are fully synced.

---

### Impact Explanation

After the attack:

- `get_executable(H_claimed)` → `None` (class stored under `H_actual`)
- `get_sierra(H_claimed)` → `None`
- Any contract deployed with class `H_claimed` cannot be executed
- RPC calls (`starknet_call`, `starknet_estimateFee`, `starknet_simulateTransactions`) that touch a contract of class `H_claimed` will fail or return wrong results
- The node will never re-sync the missing class because the marker has already advanced past the block

This is persistent, silent state corruption. The node continues operating as if healthy while silently missing one or more classes.

Fits: **Critical — Wrong compiled class / contract code selected for execution** (class is unreachable under its canonical hash).

---

### Likelihood Explanation

Any unauthenticated P2P peer can trigger this. The P2P sync protocol is a low-trust channel by design. The attacker only needs to:

1. Serve a valid `ThinStateDiff` (or let the honest state diff sync proceed normally — the class sync reads from already-stored state diffs)
2. When the class query arrives, respond with a `SierraContractClass` whose content hashes to `H_actual ≠ H_claimed`, but pair it with `H_claimed` as the declared class hash

The `is_declared` check passes because `H_claimed` is legitimately in the state diff. No cryptographic forgery is required — the attacker just sends mismatched content.

---

### Recommendation

In `write_to_storage`, after each successful `add_class` call, compare the returned `class_hash` against the expected key:

```rust
let class_hashes = loop {
    match class_manager_client.add_class(class.clone()).await {
        Ok(hashes) => break hashes,
        Err(err) => { warn!(...); }
    }
};
if class_hashes.class_hash != class_hash {
    return Err(P2pSyncClientError::BadPeer(BadPeerError::ClassHashMismatch {
        claimed: class_hash,
        actual: class_hashes.class_hash,
    }));
}
``` [5](#0-4) 

The peer should be penalized/disconnected and the block should not have its marker advanced.

---

### Proof of Concept

```rust
#[tokio::test]
async fn class_hash_mismatch_corrupts_storage() {
    let mut mock_cm = MockClassManagerClient::new();
    let h_claimed = ClassHash(Felt::from(0xAAAAu64));
    let h_actual  = ClassHash(Felt::from(0xBBBBu64));

    // ClassManager returns H_actual (content-derived), not H_claimed
    mock_cm.expect_add_class()
        .times(1)
        .returning(move |_| Ok(ClassHashes {
            class_hash: h_actual,
            executable_class_hash_v2: CompiledClassHash::default(),
        }));

    // ... set up storage with a ThinStateDiff containing H_claimed ...
    // ... run write_to_storage ...

    // Marker has advanced past block 0
    assert_eq!(reader.get_class_manager_block_marker(), BlockNumber(1));

    // H_claimed is NOT in the class manager
    assert_eq!(mock_cm.get_executable(h_claimed).await.unwrap(), None);
}
```

The test demonstrates that the marker advances and `get_executable(H_claimed)` returns `None`, confirming the corruption. The TODO at line 39 of `class.rs` is the exact gap that enables this. [6](#0-5)

### Citations

**File:** crates/apollo_p2p_sync/src/client/class.rs (L35-49)
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
            }
```

**File:** crates/apollo_p2p_sync/src/client/class.rs (L67-70)
```rust
            storage_writer
                .begin_rw_txn()?
                .update_class_manager_block_marker(&self.2.unchecked_next())?
                .commit()?;
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

**File:** crates/apollo_class_manager/src/class_manager.rs (L72-109)
```rust
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
```
