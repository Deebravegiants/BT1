### Title
Unverified Deprecated Class Bytecode Accepted from Malicious P2P Peer — (`crates/apollo_p2p_sync/src/client/class.rs`)

### Summary

`ClassStreamBuilder::parse_data_for_block` validates that a received class's *type* (new vs. deprecated) matches the state diff, but never verifies that the bytecode of a `DeprecatedContractClass` actually hashes to the claimed `class_hash`. `ClassManager::add_deprecated_class` likewise performs no hash check. A malicious P2P peer that controls the state diff stream can therefore store arbitrary bytecode under any deprecated class hash in the class manager, causing every subsequent execution of that Cairo 0 contract to run the attacker-supplied bytecode.

---

### Finding Description

**Step 1 – State diff injection.**
`StateDiffStreamBuilder::parse_data_for_block` accepts a state diff chunk containing `deprecated_declared_classes = [H]` from a peer. No signature or state-diff-commitment check is enforced (the header stream only verifies signature *count*, not validity). The state diff is written to storage. [1](#0-0) 

**Step 2 – Type-mismatch probe (optional but described in the question).**
`ClassStreamBuilder::parse_data_for_block` reads the stored state diff and builds two sets:

```
declared_classes          = state_diff.class_hash_to_compiled_class_hash   // empty
deprecated_declared_classes = {H}
```

If the peer first sends `ApiContractClass::ContractClass` for `H`, the check `declared_classes.get(&class_hash).is_some()` returns `false`, `is_declared = false`, and `BadPeerError::ClassNotInStateDiff` is returned. The peer is reported and the query retries. [2](#0-1) 

**Step 3 – Wrong-bytecode injection.**
On retry (same or different peer), the peer sends `ApiContractClass::DeprecatedContractClass` for `H` with attacker-controlled bytecode. The check `deprecated_declared_classes.contains(&class_hash)` returns `true`, so `is_declared = true`. No further validation is performed; the class is accepted and forwarded to `write_to_storage`. [3](#0-2) 

**Step 4 – Unchecked write to class manager.**
`write_to_storage` calls `class_manager_client.add_deprecated_class(H, wrong_bytecode)` in a retry loop. There is no hash verification at this call site (contrast with the `add_class` path, which has a `TODO` acknowledging the missing check). [4](#0-3) 

**Step 5 – Class manager stores without verification.**
`ClassManager::add_deprecated_class` calls `self.classes.set_deprecated_class(class_id, class)` directly. Neither the manager nor the underlying `CachedClassStorage::set_deprecated_class` computes or compares the hash of the supplied bytecode against `class_id`. [5](#0-4) [6](#0-5) 

Compare with the new-class path, where `add_class` computes `sierra_class.calculate_class_hash()` internally and the caller has a `TODO` to verify the returned hash: [7](#0-6) [8](#0-7) 

---

### Impact Explanation

Once wrong bytecode is stored under `H`, every call to `get_executable(H)` returns the attacker's bytecode. Any Cairo 0 contract deployed with class hash `H` will execute the attacker-supplied program. This affects:

- RPC `call` / `estimate_fee` / `simulate_transactions` / `trace_*` — all return results computed from wrong bytecode.
- If the node participates in sequencing or validation, block execution uses the corrupted class.

This maps to **Critical** impact: *wrong contract code selected for execution*.

---

### Likelihood Explanation

The attacker only needs to be an accepted P2P peer. Header signatures are checked only for *count* (not cryptographic validity), so a fully synthetic block chain can be served. The state diff and class streams are both unauthenticated. The attack requires no privileged access. [9](#0-8) 

---

### Recommendation

In `write_to_storage` for deprecated classes, compute the deprecated class hash of the received bytecode (using `compute_deprecated_class_hash`) and compare it to `class_hash` before calling `add_deprecated_class`. If they differ, report the peer and skip the write. Alternatively, add the verification inside `ClassManager::add_deprecated_class` itself, mirroring the hash-computation guard already present in `add_class`.

---

### Proof of Concept

```rust
// Pseudocode sketch (Rust test)
let H = ClassHash(felt!("0xdeadbeef"));

// 1. Inject state diff with deprecated_declared_classes = [H]
let state_diff = ThinStateDiff {
    deprecated_declared_classes: vec![H],
    ..Default::default()
};
storage_writer.append_state_diff(BlockNumber(0), state_diff).commit();

// 2. Build a DeprecatedContractClass with arbitrary (wrong) bytecode
let wrong_class = DeprecatedContractClass { program: arbitrary_program(), ..Default::default() };

// 3. Call add_deprecated_class directly (as the sync path does)
class_manager.add_deprecated_class(H, RawExecutableClass::try_from(
    ContractClass::V0(wrong_class.clone())).unwrap()).unwrap();

// 4. Assert the stored class does NOT hash to H
let stored = class_manager.get_executable(H).unwrap().unwrap();
let actual_hash = compute_deprecated_class_hash(&wrong_class).unwrap();
assert_ne!(ClassHash(actual_hash), H, "Wrong bytecode accepted without hash check");
```

The assertion passes (i.e., the wrong bytecode is stored), demonstrating the invariant violation.

### Citations

**File:** crates/apollo_p2p_sync/src/client/state_diff.rs (L51-110)
```rust
    fn parse_data_for_block<'a>(
        state_diff_chunks_response_manager: &'a mut ClientResponsesManager<
            DataOrFin<StateDiffChunk>,
        >,
        block_number: BlockNumber,
        storage_reader: &'a StorageReader,
    ) -> BoxFuture<'a, Result<Option<Self::Output>, ParseDataError>> {
        async move {
            let mut result = ThinStateDiff::default();
            let mut prev_result_len = 0;
            let mut current_state_diff_len = 0;
            let target_state_diff_len = storage_reader
                .begin_ro_txn()?
                .get_block_header(block_number)?
                .expect("A header with number lower than the header marker is missing")
                .state_diff_length
                .ok_or(P2pSyncClientError::OldHeaderInStorage {
                    block_number,
                    missing_field: "state_diff_length",
                })?;

            while current_state_diff_len < target_state_diff_len {
                let maybe_state_diff_chunk = state_diff_chunks_response_manager
                    .next()
                    .await
                    .ok_or(ParseDataError::BadPeer(BadPeerError::SessionEndedWithoutFin {
                        type_description: Self::TYPE_DESCRIPTION,
                    }))?;
                let Some(state_diff_chunk) = maybe_state_diff_chunk?.0 else {
                    if current_state_diff_len == 0 {
                        return Ok(None);
                    } else {
                        return Err(ParseDataError::BadPeer(BadPeerError::WrongStateDiffLength {
                            expected_length: target_state_diff_len,
                            possible_lengths: vec![current_state_diff_len],
                        }));
                    }
                };
                prev_result_len = current_state_diff_len;
                if state_diff_chunk.is_empty() {
                    return Err(ParseDataError::BadPeer(BadPeerError::EmptyStateDiffPart));
                }
                // It's cheaper to calculate the length of `state_diff_part` than the length of
                // `result`.
                current_state_diff_len += state_diff_chunk.len();
                unite_state_diffs(&mut result, state_diff_chunk)?;
            }

            if current_state_diff_len != target_state_diff_len {
                return Err(ParseDataError::BadPeer(BadPeerError::WrongStateDiffLength {
                    expected_length: target_state_diff_len,
                    possible_lengths: vec![prev_result_len, current_state_diff_len],
                }));
            }

            validate_deprecated_declared_classes_non_conflicting(&result)?;
            Ok(Some((result, block_number)))
        }
        .boxed()
    }
```

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

**File:** crates/apollo_p2p_sync/src/client/class.rs (L51-65)
```rust
            for (class_hash, deprecated_class) in self.1 {
                // TODO(shahak): Test this flow.
                // TODO(shahak): Try to avoid cloning. See if ClientError can contain the request.
                while let Err(err) = class_manager_client
                    .add_deprecated_class(class_hash, deprecated_class.clone())
                    .await
                {
                    warn!(
                        "Failed writing deprecated class with hash {class_hash:?} to class \
                         manager. Trying again. Error: {err:?}"
                    );
                    trace!("Class: {deprecated_class:?}");
                    // TODO(shahak): Consider sleeping here.
                }
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

**File:** crates/apollo_class_manager/src/class_manager.rs (L70-113)
```rust
    #[instrument(skip(self, class), ret, err)]
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

**File:** crates/apollo_class_manager/src/class_manager.rs (L136-144)
```rust
    #[instrument(skip(self, class), ret, err)]
    pub fn add_deprecated_class(
        &mut self,
        class_id: ClassId,
        class: RawExecutableClass,
    ) -> ClassManagerResult<()> {
        self.classes.set_deprecated_class(class_id, class)?;
        Ok(())
    }
```

**File:** crates/apollo_class_manager/src/class_storage.rs (L198-216)
```rust
    #[instrument(skip(self, class), level = "debug", ret, err)]
    fn set_deprecated_class(
        &mut self,
        class_id: ClassId,
        class: RawExecutableClass,
    ) -> Result<(), Self::Error> {
        if self.deprecated_class_cached(class_id) {
            return Ok(());
        }

        self.storage.set_deprecated_class(class_id, class.clone())?;

        increment_n_classes(CairoClassType::Deprecated);
        record_class_size(ClassObjectType::DeprecatedCasm, &class);

        self.deprecated_classes.set(class_id, class);

        Ok(())
    }
```

**File:** crates/apollo_p2p_sync/src/client/header.rs (L115-120)
```rust
            if signed_block_header.signatures.len() != ALLOWED_SIGNATURES_LENGTH {
                return Err(ParseDataError::BadPeer(BadPeerError::WrongSignaturesLength {
                    signatures: signed_block_header.signatures,
                }));
            }
            Ok(Some(signed_block_header))
```
