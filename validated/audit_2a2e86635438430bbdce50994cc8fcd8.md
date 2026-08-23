### Title
Corrupted/incompatible cached `CompiledContract::CompileModuleError` deserialization panics the node instead of degrading to a cache miss - (File: `runtime/near-vm-runner/src/cache.rs`)

### Summary
`FilesystemContractRuntimeCache::get` calls `borsh::from_slice(&buffer)?` to deserialize the `CompilationError` payload of a cached `CompileModuleError` entry, and a deserialization failure is propagated as an `Err` all the way up through `VMRunnerError::CacheError` into `RuntimeError::StorageError(StorageError::StorageInconsistentState(...))`, which `apply_chunk` turns into an unconditional `panic!`. Because `CompileModuleError` entries are created for attacker-supplied invalid contracts and persisted to the on-disk cache, an attacker-deployed invalid contract combined with a client binary upgrade that changes the `CompilationError` borsh encoding can crash-loop upgraded validators.

### Finding Description
`CompiledContract` is a borsh `use_discriminant` enum with `CompileModuleError(CompilationError) = 0` and `Code(Vec<u8>) = 1` [1](#0-0) . When `FilesystemContractRuntimeCache::put` stores a compile failure, it writes only the raw borsh-serialized `CompilationError` bytes plus a trailing `ERROR_TAG` and length suffix — no schema/version tag is stored [2](#0-1) .

On `get`, the tag is read and, for `ERROR_TAG`, the payload is fed straight into `borsh::from_slice(&buffer)?` [3](#0-2) . Unlike the adjacent "unknown tag" branch, which explicitly treats a malformed file as a cache miss (`return Ok(None)`) [4](#0-3) , a `borsh::from_slice` failure on this line uses `?` and propagates as `std::io::Result::Err` from `get`.

That `Err` flows through the call chain without ever being downgraded to a benign miss:
- `read_cache`/`with_compiled_and_loaded` map it to `CacheError::ReadError` [5](#0-4) [6](#0-5) .
- This becomes `VMRunnerError::CacheError` [7](#0-6) .
- In `runtime/runtime/src/function_call.rs`, `VMRunnerError::CacheError(err)` is explicitly converted into `RuntimeError::StorageError(StorageError::StorageInconsistentState(...))` [8](#0-7) .
- `chain/chain/src/runtime/mod.rs::apply_chunk` maps `RuntimeError::StorageError` to `Error::StorageError`, then only two `StorageError` sub-variants (`FlatStorageBlockNotSupported`, `MissingTrieValue`) are forwarded as recoverable errors; every other `StorageError`, including `StorageInconsistentState`, is `panic!("{err}")` [9](#0-8) .

Exploit flow: an unprivileged attacker submits `DeployContract` with wasm that fails compilation (e.g., malformed/oversized module). The old binary compiles it, gets a `CompilationError`, and persists a `CompiledContract::CompileModuleError(err)` entry keyed by `(code_hash, vm_config_hash, vm_kind, vm_hash)` to the on-disk `FilesystemContractRuntimeCache` [10](#0-9) . The operator then upgrades the node binary. If the new binary's `CompilationError` type has a structurally different borsh encoding for the same discriminant (e.g., different fields/variant contents reachable under the same or a still-valid `use_discriminant` value) than what is on disk, `borsh::from_slice` on the stale bytes can fail (or, in the worse case, silently misinterpret bytes as a different but well-formed value of the new schema — not fully verifiable from this codebase without knowing the exact schema diff, but a failure is directly demonstrable and reachable). Any subsequent call to the same contract on the new binary triggers `get`, hits the failing `borsh::from_slice`, and the node panics in `apply_chunk`.

The comment at `cache.rs:700-705` even acknowledges this class of risk generally ("any failure here will result in the node terminating anyway") but the code's actual handling for a malformed *tag* is graceful (`Ok(None)`), while the handling for a malformed *payload* under a correctly-recognized tag is not — this asymmetry is the root cause.

### Impact Explanation
This is a **liveness/crash-loop** issue: any validator or RPC node that (a) previously cached a `CompileModuleError` entry for an attacker-controlled invalid contract and (b) is later run with a binary whose `CompilationError` borsh layout is incompatible with the stored bytes will panic on `apply_chunk` for any receipt calling that contract, and (depending on deployment automation) may crash-loop. Because this happens inside `apply_chunk`'s panic path rather than a graceful `RuntimeError`, it maps to a node/validator crash caused indirectly by attacker-controlled input, corresponding to the NEAR bounty "node crash" / liveness-impact class. It does not directly cause fund loss, but broad crash-looping of upgraded validators degrades chain liveness.

### Likelihood Explanation
Triggering the bug requires: (1) an attacker deploying an invalid contract prior to an upgrade so a `CompileModuleError` gets cached to disk, and (2) a binary upgrade that changes `CompilationError`'s borsh-serialized shape without invalidating/migrating the on-disk cache for entries under the same cache key. The `CompiledContract`/`CompilationError` types are explicitly annotated for `near_schema_checker_lib::ProtocolSchema`/protocol-schema tracking elsewhere in the codebase, suggesting schema changes to these types are anticipated over the software's lifetime, but no migration or versioning of the *on-disk cache payload* itself was found in the code reviewed (the only sweep found is `on_protocol_version_update`, gated to the Wasmtime protocol-version cutover, not to arbitrary CompilationError layout changes). Because the vulnerability requires an actual schema-incompatible binary upgrade to manifest, likelihood depends on the accumulation of unmigrated `CompilationError` variant/field changes across releases — plausible but not guaranteed on every upgrade. The reachable, provable component (a corrupted/incompatible payload under `ERROR_TAG` causing `get` to return `Err` instead of `Ok(None)`, and that `Err` being propagated to a `panic!`) is directly demonstrable today via a targeted unit/integration test, independent of exactly if/when NEAR ships a breaking `CompilationError` schema change.

### Recommendation
- In `FilesystemContractRuntimeCache::get`, treat a `borsh::from_slice` failure on the `ERROR_TAG` payload the same way the unknown-tag branch is treated: log and `return Ok(None)` (cache miss) instead of propagating `Err` via `?`.
- More generally, do not let `CacheError`/on-disk deserialization failures map to `StorageError::StorageInconsistentState` in `runtime/runtime/src/function_call.rs`, since that path is fatal (`panic!`) in `apply_chunk`; a corrupted/incompatible *compiled-contract cache* is not equivalent to state-trie inconsistency and should be recoverable by discarding the cache entry and recompiling.
- Add a schema/format version byte to the on-disk cache entry so future `CompilationError` schema changes can be detected up front and treated as cache misses rather than relying on borsh deserialization to fail loudly (or silently misparse).

### Proof of Concept
Integration test in `runtime/near-vm-runner/src/cache.rs` (or a new test module):
1. Construct a `FilesystemContractRuntimeCache::test()`.
2. Manually write a cache file for key `k`: write arbitrary bytes that do **not** correspond to a valid borsh encoding of `CompilationError` (e.g., a byte sequence with a valid `CompilationError` discriminant byte but truncated/garbage payload), followed by `ERROR_TAG` and an 8-byte `wasm_bytes` LE suffix — mirroring the layout `put` produces.
3. Call `cache.get(&k)`.
4. Assert `cache.get(&k)` returns `Ok(None)` (graceful miss), not `Err(_)`.
5. Currently, this assertion fails: `get` returns `Err(io::Error)` because of the unchecked `?` at `cache.rs:746`.
6. As a secondary integration-level check, add a test that drives this `Err` through `read_cache`/`with_compiled_and_loaded` and `runtime/runtime/src/function_call.rs::execute` to confirm it currently surfaces as `RuntimeError::StorageError(StorageError::StorageInconsistentState(..))`, and that `apply_chunk` in `chain/chain/src/runtime/mod.rs` panics on it (expected fix: it should not panic, and ideally the contract call should just recompile).

### Citations

**File:** runtime/near-vm-runner/src/cache.rs (L84-90)
```rust
#[derive(Debug, Clone, PartialEq, BorshDeserialize, BorshSerialize)]
#[borsh(use_discriminant = true)]
#[repr(u8)]
pub enum CompiledContract {
    CompileModuleError(crate::logic::errors::CompilationError) = 0,
    Code(Vec<u8>) = 1,
}
```

**File:** runtime/near-vm-runner/src/cache.rs (L657-669)
```rust
        match value.compiled {
            CompiledContract::CompileModuleError(e) => {
                borsh::to_writer(&mut file, &e)?;
                file.write_all(&[ERROR_TAG])?;
            }
            CompiledContract::Code(bytes) => {
                file.write_all(&bytes)?;
                // Writing the tag at the end gives us well aligned buffer of the data above which
                // is necessary for 0-copy deserialization later on.
                file.write_all(&[CODE_TAG])?;
            }
        }
        file.write_all(&value.wasm_bytes.to_le_bytes())?;
```

**File:** runtime/near-vm-runner/src/cache.rs (L744-747)
```rust
            ERROR_TAG => CompiledContractInfo {
                wasm_bytes,
                compiled: CompiledContract::CompileModuleError(borsh::from_slice(&buffer)?),
            },
```

**File:** runtime/near-vm-runner/src/cache.rs (L748-759)
```rust
            // File is malformed? For this code, since we're talking about a cache lets just treat
            // it as if there is no cached file as well. The cached file may eventually be
            // overwritten with a valid copy. And since we can compile a new copy, there doesn't
            // seem to be much reason to possibly crash the node due to this.
            _ => {
                tracing::debug!(
                    target: "vm",
                    message = "cached contract executable was found to be malformed",
                    key = %key
                );
                return Ok(None);
            }
```

**File:** runtime/near-vm-runner/src/wasmtime_runner/mod.rs (L141-149)
```rust
fn read_cache(
    cache: &dyn ContractRuntimeCache,
    key: &CryptoHash,
) -> Result<Option<CachedArtifact>, CacheError> {
    Ok(cache.get(key).map_err(CacheError::ReadError)?.map(|info| match info.compiled {
        CompiledContract::Code(module) => Ok(module),
        CompiledContract::CompileModuleError(err) => Err(err),
    }))
}
```

**File:** runtime/near-vm-runner/src/wasmtime_runner/mod.rs (L663-678)
```rust
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

**File:** runtime/near-vm-runner/src/wasmtime_runner/mod.rs (L704-708)
```rust
        let (wasm_bytes, pre_result) = cache.memory_cache().try_lookup(
            key,
            || {
                is_memory_hit = false;
                let cache_record = cache.get(&key).map_err(CacheError::ReadError)?;
```

**File:** runtime/near-vm-runner/src/logic/errors.rs (L11-19)
```rust
#[derive(Debug, thiserror::Error)]
pub enum VMRunnerError {
    /// An error that is caused by an operation on an inconsistent state.
    /// E.g. an integer overflow by using a value from the given context.
    #[error("{0}")]
    InconsistentStateError(InconsistentStateError),
    /// Error caused by caching.
    #[error("cache error: {0}")]
    CacheError(#[from] CacheError),
```

**File:** runtime/runtime/src/function_call.rs (L325-330)
```rust
        Err(VMRunnerError::CacheError(err)) => {
            metrics::FUNCTION_CALL_PROCESSED_CACHE_ERRORS
                .with_label_values::<&str>(&[(&err).into()])
                .inc();
            return Err(StorageError::StorageInconsistentState(err.to_string()).into());
        }
```

**File:** chain/chain/src/runtime/mod.rs (L1279-1289)
```rust
        ) {
            Ok(result) => Ok(result),
            Err(e) => match e {
                Error::StorageError(err) => match &err {
                    StorageError::FlatStorageBlockNotSupported(_)
                    | StorageError::MissingTrieValue(..) => Err(err.into()),
                    _ => panic!("{err}"),
                },
                _ => Err(e),
            },
        }
```
