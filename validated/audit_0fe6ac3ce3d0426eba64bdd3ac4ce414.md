No vulnerability found for this question.

**Analysis:**

`Code::from_arced_verified` in `types.rs` is a bare constructor that just wraps a pre-built `Arc<V>` into the `Code::Verified` variant — it performs no key binding at all [1](#0-0) . The actual custody-relevant binding between a `ModuleId` key and verified code happens one layer up in `ModuleCache::insert_verified_module`/`insert_deserialized_module`, which key the `DashMap`/`HashMap` entries and enforce a strict version ordering (`Ordering::Less` → error, `Ordering::Equal` → keep existing if already verified, `Ordering::Greater` → replace) before any `Code`/`ModuleCode` is stored [2](#0-1) [3](#0-2) .

Every call site that invokes `from_arced_verified`/`ModuleCode::from_arced_verified` derives both the `Arc<V>` and its associated key/extension from the same authoritative source at the same time — e.g. `into_verified_module_code_iter` re-fetches the module's extension from the state view using the *same* `key` that the verified code was cached under, rather than accepting attacker-supplied key/value pairs [4](#0-3) . There is no code path where a caller can pass a mismatched `(ModuleId, Arc<V>)` pair sourced from two different modules into this constructor.

Additionally, the republish/upgrade path explicitly avoids caching entirely during staging: `StagingModuleStorage` is annotated `NoOpLayoutCache` specifically "so that any speculative updates are not accidentally cached" during compatibility checking of a new module bundle against the old one [5](#0-4) , and compatibility is verified against the actual old module fetched from storage before any new module bytes are staged [6](#0-5) . On the block-executor side, republishing a module explicitly invalidates the global cache via `mark_overridden`, and any stale captured reads referencing the pre-upgrade `Arc` fail read-set validation and force re-execution — this is exercised directly in `test_global_and_block_cache_module_reads` [7](#0-6) . The Move-level `code.move` upgrade flow also enforces compatibility/coexistence checks (`check_upgradability`, `check_coexistence`) and there is an existing regression test guarding against exactly this class of cache-incoherence bug (`code_publishing_upgrade_loader_cache_consistency`, which documents that the loader cache is flushed on `AptosVM::new_session` specifically to prevent an old module version from staying active after upgrade) [8](#0-7) .

Since `from_arced_verified` never receives or determines the key it's stored under — that binding is always done correctly by the surrounding `ModuleCache`/`insert_verified_module` machinery with version checks and freshly-sourced extensions — there is no attacker-reachable path by which an old module's verified `Arc` gets silently reattached to a different, upgraded `ModuleId` in a way that changes ownership/authority over a resource-account-held code object.

### Citations

**File:** third_party/move/move-vm/types/src/code/cache/types.rs (L72-75)
```rust
    /// Returns new verified code from [Arc]ed instance.
    pub fn from_arced_verified(verified_code: Arc<V>) -> Self {
        Self::Verified(verified_code)
    }
```

**File:** third_party/move/move-vm/types/src/code/cache/module_cache.rs (L295-338)
```rust
    fn insert_verified_module(
        &self,
        key: Self::Key,
        verified_code: Self::Verified,
        extension: Arc<Self::Extension>,
        version: Self::Version,
    ) -> VMResult<Arc<ModuleCode<Self::Deserialized, Self::Verified, Self::Extension>>> {
        use hashbrown::hash_map::Entry::*;

        match self.module_cache.borrow_mut().entry(key) {
            Occupied(mut entry) => match version.cmp(&entry.get().version()) {
                Ordering::Less => Err(version_too_small_error!()),
                Ordering::Equal => {
                    if entry.get().module_code().code().is_verified() {
                        Ok(entry.get().module_code().clone())
                    } else {
                        let versioned_module = VersionedModuleCode::new(
                            ModuleCode::from_verified(verified_code, extension),
                            version,
                        );
                        let module = versioned_module.module_code().clone();
                        entry.insert(versioned_module);
                        Ok(module)
                    }
                },
                Ordering::Greater => {
                    let versioned_module = VersionedModuleCode::new(
                        ModuleCode::from_verified(verified_code, extension),
                        version,
                    );
                    let module = versioned_module.module_code().clone();
                    entry.insert(versioned_module);
                    Ok(module)
                },
            },
            Vacant(entry) => Ok(entry
                .insert(VersionedModuleCode::new(
                    ModuleCode::from_verified(verified_code, extension),
                    version,
                ))
                .module_code()
                .clone()),
        }
    }
```

**File:** third_party/move/move-vm/types/src/code/cache/module_cache.rs (L459-500)
```rust
    fn insert_verified_module(
        &self,
        key: Self::Key,
        verified_code: Self::Verified,
        extension: Arc<Self::Extension>,
        version: Self::Version,
    ) -> VMResult<Arc<ModuleCode<Self::Deserialized, Self::Verified, Self::Extension>>> {
        use dashmap::mapref::entry::Entry::*;

        match self.module_cache.entry(key) {
            Occupied(mut entry) => match version.cmp(&entry.get().version()) {
                Ordering::Less => Err(version_too_small_error!()),
                Ordering::Equal => {
                    if entry.get().module_code().code().is_verified() {
                        Ok(entry.get().module_code().clone())
                    } else {
                        let versioned_module = VersionedModuleCode::new(
                            ModuleCode::from_verified(verified_code, extension),
                            version,
                        );
                        let module = versioned_module.module_code().clone();
                        entry.insert(CachePadded::new(versioned_module));
                        Ok(module)
                    }
                },
                Ordering::Greater => {
                    let versioned_module = VersionedModuleCode::new(
                        ModuleCode::from_verified(verified_code, extension),
                        version,
                    );
                    let module = versioned_module.module_code().clone();
                    entry.insert(CachePadded::new(versioned_module));
                    Ok(module)
                },
            },
            Vacant(entry) => {
                let module = ModuleCode::from_verified(verified_code, extension);
                let v = entry.insert(CachePadded::new(VersionedModuleCode::new(module, version)));
                Ok(v.module_code().clone())
            },
        }
    }
```

**File:** aptos-move/aptos-vm-types/src/module_and_script_storage/state_view_adapter.rs (L122-154)
```rust
        let (state_view, verified_modules_iter) = self
            .storage
            .into_module_storage()
            .unpack_into_verified_modules_iter();

        Ok(verified_modules_iter
            .map(|(key, verified_code)| {
                // We have cached the module previously, so we must be able to find it in storage.
                let extension = state_view
                    .get_state_value(&StateKey::module_id(&key))
                    .map_err(|err| {
                        let msg = format!(
                            "Failed to retrieve module {}::{} from storage {:?}",
                            key.address(),
                            key.name(),
                            err
                        );
                        PanicError::CodeInvariantError(msg)
                    })?
                    .map_or_else(
                        || {
                            let msg = format!(
                                "Module {}::{} should exist, but it does not anymore",
                                key.address(),
                                key.name()
                            );
                            Err(PanicError::CodeInvariantError(msg))
                        },
                        |state_value| Ok(AptosModuleExtension::new(state_value)),
                    )?;

                let module = ModuleCode::from_arced_verified(verified_code, Arc::new(extension));
                Ok((key, Arc::new(module)))
```

**File:** third_party/move/move-vm/runtime/src/storage/publishing.rs (L93-130)
```rust
// Very important: no caching for staging module storage so that any speculative updates are not
// accidentally cached.
impl<M> NoOpLayoutCache for StagingModuleStorage<'_, M> {}

impl<'a, M: ModuleStorage> StagingModuleStorage<'a, M> {
    /// Returns new module storage with staged modules, running full compatability checks for them.
    pub fn create(
        sender: &AccountAddress,
        existing_module_storage: &'a M,
        module_bundle: Vec<Bytes>,
    ) -> VMResult<Self> {
        Self::create_with_compat_config(
            sender,
            Compatibility::full_check(),
            existing_module_storage,
            module_bundle,
        )
    }

    /// Returns new module storage with staged modules, checking compatibility based on the
    /// provided config.
    pub fn create_with_compat_config(
        sender: &AccountAddress,
        compatibility: Compatibility,
        existing_module_storage: &'a M,
        module_bundle: Vec<Bytes>,
    ) -> VMResult<Self> {
        // Create a new runtime environment, so that it is not shared with the existing one. This
        // is extremely important for correctness of module publishing: we need to make sure that
        // no speculative information is cached! By cloning the environment, we ensure that when
        // using this new module storage with changes, global caches are not accessed. Only when
        // the published module is committed, and its structs are accessed, their information will
        // be cached in the global runtime environment.
        //
        // Note: cloning the environment is relatively cheap because it only stores global caches
        // that cannot be invalidated by module upgrades using a shared pointer, so it is not a
        // deep copy. See implementation of Clone for this struct for more details.
        let staged_runtime_environment = existing_module_storage.runtime_environment().clone();
```

**File:** third_party/move/move-vm/runtime/src/storage/publishing.rs (L177-196)
```rust
            if compatibility.need_check_compat() {
                // INVARIANT:
                //   Old module must be metered at the caller side.
                if let Some(old_module_ref) =
                    existing_module_storage.unmetered_get_deserialized_module(addr, name)?
                {
                    if !is_framework_for_option_enabled
                        && is_enum_option_enabled
                        && old_module_ref.self_id().is_option()
                        && old_module_ref.self_id() == compiled_module.self_id()
                    {
                        // skip check for option module during publishing
                    } else {
                        let old_module = old_module_ref.as_ref();
                        compatibility
                            .check(old_module, &compiled_module)
                            .map_err(|e| e.finish(Location::Undefined))?;
                    }
                }
            }
```

**File:** aptos-move/block-executor/src/captured_reads.rs (L2320-2346)
```rust
        // Assume we republish this module: validation must fail.
        let a = mock_deserialized_code(100, MockExtension::new(8));
        global_module_cache.mark_overridden(&0);
        per_block_module_cache
            .insert_deserialized_module(
                0,
                a.code().deserialized().as_ref().clone(),
                a.extension().clone(),
                Some(10),
            )
            .unwrap();

        let valid = captured_reads.validate_module_reads(
            &global_module_cache,
            &per_block_module_cache,
            None,
        );
        assert!(!valid);

        // Assume we re-read the new correct version. Then validation should pass again.
        captured_reads.capture_per_block_cache_read(0, Some((a, Some(10))));
        assert!(captured_reads.validate_module_reads(
            &global_module_cache,
            &per_block_module_cache,
            None
        ));
        assert!(!global_module_cache.contains_not_overridden(&0));
```

**File:** aptos-move/e2e-move-tests/src/tests/code_publishing.rs (L215-255)
```rust
/// This test verifies that the cache incoherence bug on module upgrade is fixed. This bug
/// exposes itself by that after module upgrade the old version of the module stays
/// active until the MoveVM terminates. In order to workaround this until there is a better
/// fix, we flush the cache in `AptosVM::new_session`. One can verify the fix by commenting
/// the flush operation out, then this test fails.
///
/// TODO: for some reason this test did not capture a serious bug in `code::check_coexistence`.
#[test]
fn code_publishing_upgrade_loader_cache_consistency() {
    let mut h = MoveHarness::new();
    let acc = h.new_account_at(AccountAddress::from_hex_literal("0xcafe").unwrap());

    // Create a sequence of package upgrades
    let txns = vec![
        h.create_publish_package(
            &acc,
            &common::test_dir_path("code_publishing.data/pack_initial"),
            None,
            |_| {},
        ),
        // Compatible with above package
        h.create_publish_package(
            &acc,
            &common::test_dir_path("code_publishing.data/pack_upgrade_compat"),
            None,
            |_| {},
        ),
        // Not compatible with above package, but with first one.
        // Correct behavior: should create backward_incompatible error
        // Bug behavior: succeeds because is compared with the first module
        h.create_publish_package(
            &acc,
            &common::test_dir_path("code_publishing.data/pack_compat_first_not_second"),
            None,
            |_| {},
        ),
    ];
    let result = h.run_block(txns);
    assert_success!(result[0]);
    assert_success!(result[1]);
    assert_vm_status!(result[2], StatusCode::BACKWARD_INCOMPATIBLE_MODULE_UPDATE)
```
