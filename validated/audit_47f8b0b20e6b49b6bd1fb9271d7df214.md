## Analysis Result

Based on the investigation, this is a genuine analog vulnerability but its impact requires an important caveat I could not fully resolve: I was unable to confirm within the tool budget how `NewFileModuleStore`'s `cacheDir` parameter is actually wired from `core/services/cre/cre.go` config (empty string vs. explicit configured dir) in production deployments, which determines whether the vulnerable default path is actually reachable in a real node deployment.

### Title
Predictable shared-temp-directory WASM module cache accepted without ownership verification enabling local cache poisoning - (File: core/services/workflows/artifacts/v2/file_module_store.go)

### Summary
`FileModuleStore` resolves its on-disk workflow-module cache to a fixed, predictable path under the world-writable shared temp directory (`os.TempDir()/workflow-module-cache`) whenever no explicit cache directory is configured, and accepts that directory without verifying it isn't pre-created/owned by another local user — mirroring the CWE-377 "predictable temp directory without ownership verification" root cause in the reported Spring Boot `ApplicationTemp` advisory.

### Finding Description
`NewFileModuleStore` builds the cache directory as `filepath.Join(os.TempDir(), defaultCacheSubdir)` (a fixed, predictable name, `"workflow-module-cache"`) whenever `cacheDir` is empty. [1](#0-0) 

It then calls `os.MkdirAll(cacheDir, 0o755)`, which succeeds silently if the directory already exists (regardless of who created it or what its ownership/permissions are), and only checks that the directory is *writable*, not that it is *owned* by the chainlink process user: [2](#0-1) 

This is the same bug class as GHSA-wwpq-f5c3-7hvx: a predictable, shared-temp-directory path is trusted for storing sensitive/executable artifacts without verifying that a pre-existing directory (potentially planted by another local, unprivileged user before the chainlink node starts) is actually owned by the expected user.

Cached WASM binaries written into this store are later read back and executed as trusted workflow code without any additional signature/hash verification against the on-chain/registry source — `ensureLoaded` reads the binary straight from `p, cachedVersion, ok, err := m.store.GetModule(...)` and passes it to `m.factory(ctx, m.moduleConfig, binary, ...)`, which compiles and runs it as the workflow's WASM module: [3](#0-2) 

The only integrity check performed is an engine-version string match, not a content hash or digital signature: [4](#0-3) 

### Impact Explanation
If the module cache resolves to the default shared temp path and no other component validates the directory's ownership, a co-resident, unprivileged local attacker could pre-create `<tmp>/workflow-module-cache/<workflowID>/binary.wasm` for a target workflow ID before or while the chainlink process starts. Because `os.MkdirAll` does not fail on a pre-existing directory and no ownership check is performed, the attacker's planted binary could be picked up by `GetModule`/`ensureLoaded` and executed as if it were the legitimately-fetched workflow module — resulting in arbitrary WASM execution inside the node process (as the chainlink service user), potentially leading to secret disclosure (keys/credentials accessible to the workflow host environment) or further compromise. This matches the reported CVE's impact category (local attacker gains code-execution-adjacent control via a predictable temp path) although the CVE targeted session persistence and this analog targets the workflow WASM module cache.

### Likelihood Explanation
Exploitability depends on two conditions I could not fully verify given the read-only, index-limited environment: (1) whether the `cacheDir` argument passed from `core/services/cre/cre.go` is actually left empty in real deployments (falling back to the vulnerable shared-temp default) or is always explicitly configured to a private root-owned directory, and (2) the attacker needing local, unprivileged filesystem access to the host and the ability to predict/target a specific `workflowID` before the legitimate cache entry is created (a race with `StoreModule`/`cleanOnStartup`). If the default path is used in practice, likelihood is meaningful on shared/multi-tenant hosts; if `cacheDir` is always explicitly set to a controlled, node-owned directory in production configuration, this finding has no practical impact.

### Recommendation
- Never default the module cache to a fixed name inside the shared, world-writable `os.TempDir()`; use a process/user-specific directory (e.g., under `RootDir` or `os.UserCacheDir()`, as already done for `UserCache` in `core/cmd/shell.go`) with `0700` permissions.
- In `NewFileModuleStore`, verify ownership of a pre-existing `cacheDir` (e.g., compare file `Uid` against the current process UID) before trusting it, refusing to proceed or wiping/recreating it if ownership doesn't match, similar in spirit to `checkFilePermissions`'s ownership check via `utils.IsFileOwnedByChainlink`. [5](#0-4) 
- Add integrity verification (content hash/signature tied to the workflow registry source) before executing a cached binary in `ensureLoaded`, rather than relying solely on the engine-version string match.

### Proof of Concept
1. On a shared multi-user host, before the chainlink node starts (or is restarted), an unprivileged local user creates `os.TempDir()/workflow-module-cache/<target-workflow-id>/binary.wasm` containing an attacker-crafted WASM module, and `engine_version.txt` matching the current node's engine version string.
2. The chainlink node starts with no explicit workflow module cache directory configured, so `NewFileModuleStore("", false)` resolves `cacheDir` to the same predictable path and accepts the pre-existing, attacker-controlled directory via `os.MkdirAll`/`checkCacheDirWritable` without ownership verification. [6](#0-5) 
3. When the target workflow is scheduled, `EvictableModule.ensureLoaded` calls `m.store.GetModule(m.workflowID)`, finds the attacker's planted binary/version match, reads it, and compiles/executes it via the module factory as trusted workflow code. [3](#0-2) 

Note: I was not able to confirm, within the available tool budget, the exact default wiring of `cacheDir` from `core/services/cre/cre.go` in production configuration; if a background Devin session is available, I recommend verifying whether the empty/default path is ever reachable outside of tests before treating this as confirmed-exploitable in the shipped product.

### Citations

**File:** core/services/workflows/artifacts/v2/file_module_store.go (L24-57)
```go
func NewFileModuleStore(cacheDir string, cleanOnStartup bool) (*FileModuleStore, error) {
	if cacheDir == "" {
		cacheDir = filepath.Join(os.TempDir(), defaultCacheSubdir)
	}
	if cleanOnStartup {
		if err := os.RemoveAll(cacheDir); err != nil {
			return nil, fmt.Errorf("failed to clear module cache directory: %w", err)
		}
	}
	if err := os.MkdirAll(cacheDir, 0o755); err != nil {
		return nil, fmt.Errorf("failed to create module cache directory: %w", err)
	}
	if err := checkCacheDirWritable(cacheDir); err != nil {
		return nil, err
	}
	return &FileModuleStore{cacheDir: cacheDir}, nil
}

func checkCacheDirWritable(dir string) error {
	f, err := os.CreateTemp(dir, ".writecheck-*")
	if err != nil {
		return fmt.Errorf("module cache directory is not writable: %w", err)
	}
	name := f.Name()
	defer os.Remove(name)
	if _, err := f.Write([]byte{0}); err != nil {
		_ = f.Close()
		return fmt.Errorf("module cache directory is not writable: %w", err)
	}
	if err := f.Close(); err != nil {
		return fmt.Errorf("module cache directory is not writable: %w", err)
	}
	return nil
}
```

**File:** core/services/workflows/syncer/v2/evictable_module.go (L306-336)
```go
	// L3: read binary from disk and re-instantiate via the factory.
	p, cachedVersion, ok, err := m.store.GetModule(m.workflowID)
	if err != nil {
		return "", fmt.Errorf("failed to get module path: %w", err)
	}
	if !ok {
		return "", fmt.Errorf("no cached binary for workflow %s", m.workflowID)
	}
	if cachedVersion != m.engineVersion {
		m.metrics.recordVersionMismatch(ctx)
		lg := m.moduleConfig.Logger
		if lg != nil {
			lg.Warnw("rejecting cached module binary: engine version mismatch",
				"workflowID", m.workflowID,
				"cachedEngineVersion", cachedVersion,
				"currentEngineVersion", m.engineVersion)
		}
		if delErr := m.store.DeleteModule(m.workflowID); delErr != nil && lg != nil {
			lg.Warnw("failed to delete stale cached module", "workflowID", m.workflowID, "err", delErr)
		}
		return "", fmt.Errorf("%w (workflow_id=%s cached=%q current=%q)", ErrEngineVersionMismatch, m.workflowID, cachedVersion, m.engineVersion)
	}

	binary, err := os.ReadFile(p)
	if err != nil {
		return "", fmt.Errorf("failed to read cached binary: %w", err)
	}

	m.binarySize.Store(int64(len(binary)))

	mod, err := m.factory(ctx, m.moduleConfig, binary, m.moduleOpts...)
```

**File:** core/cmd/shell_local.go (L738-745)
```go
		owned, err := utils.IsFileOwnedByChainlink(fileInfo)
		if err != nil {
			lggr.Warn(err)
			continue
		}
		if !owned {
			lggr.Warnf("The file %v is not owned by the user running chainlink. This will be made mandatory in the future.", path)
		}
```
