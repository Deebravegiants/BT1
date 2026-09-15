# [?] [SharovBot] fix Amsterdam signer support and BAL non-determinism (#19434)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-03-02
Source: https://github.com/erigontech/erigon/commit/9d1c662dcb3436dfc636cbb5e4aaae1593c86c87
Type: security-commit

## Details
[SharovBot] fix Amsterdam signer support and BAL non-determinism (#19434)

**[SharovBot]** Fix Amsterdam signer support and BAL non-determinism in
parallel execution

## Summary

- **Amsterdam signer**: Add Amsterdam fork handling in `MakeSigner` and
`LatestSigner` so that `setCode` and `blob` tx types are supported when
only `AmsterdamTime` is configured (without `PragueTime`).
- **BAL non-determinism (parallel execution)**: Fix multiple sources of
non-deterministic BAL (EIP-7928) hashes during parallel tx execution:
- Sort `ApplyVersionedWrites` output by (Address, Path, Key) for
deterministic application order
- Sync `WaitGroup` before block finalization to ensure all prior tx
state is applied to `pe.rs`
- Flush merged writes (execution + finalize) to the version map so later
tx finalizations see the full post-tx state
- Read coinbase balance from the version map (via
`versionedStateReader`) rather than a stale `pe.rs` snapshot
- Sync `CodeHash` in `getStateObject` when code is loaded from the
version map, preventing the "revert to original" optimization from
incorrectly deleting code writes
- **Atomic version map flush**: `FlushVersionedWrites` now holds a
single lock for all writes, preventing concurrent workers from observing
a partially-flushed state (e.g. seeing `AddressPath` but not the
corresponding `CodePath` from the same transaction)

## Test plan

- [x] `execution/tests` package compiles without errors
- [x] `TestExecutionSpecBlockchainDevnet/amsterdam` passes in a single
run
- [x] `TestExecutionSpecBlockchainDevnet/amsterdam` passes 30
consecutive times with `-count=1`
- [x] `TestExecutionSpecBlockchainDevnet/prague/eip7702` passes (no
regression)

Fixes CI job:
https://github.com/erigontech/erigon/actions/runs/22296091141/job/64492938121

🤖 Generated with [Claude Code](https://claude.com/claude-code)

---------

Co-authored-by: Claude Opus 4.6 <noreply@anthropic.com>
Co-authored-by: Mark Holt <135143369+mh0lt@users.noreply.github.com>
Co-authored-by: Andrew Ashikhmin <34320705+yperbasis@users.noreply.github.com>

### execution/stagedsync/bal_create.go
```diff
@@ -42,6 +42,17 @@ func CreateBAL(blockNum uint64, txIO *state.VersionedIO, dataDir string) types.B
 		})
 
 		writes := txIO.WriteSet(txIndex)
+		// Sort writes by (Address, Path, Key) to ensure deterministic
+		// processing order regardless of Go map iteration order.
+		sort.Slice(writes, func(i, j int) bool {
+			if c := writes[i].Address.Cmp(writes[j].Address); c != 0 {
+				return c < 0
+			}
+			if writes[i].Path != writes[j].Path {
+				return writes[i].Path < writes[j].Path
+			}
+			return writes[i].Key.Cmp(writes[j].Key) < 0
+		})
 		// First pass: apply SelfDestructPath writes so the selfDestructed flag
 		// is up-to-date before balance/nonce/code writes are processed.
 		// The write slice order is non-deterministic, and a SelfDestructPath=false
```

### execution/stagedsync/exec3_parallel.go
```diff
@@ -1095,7 +1095,13 @@ func (result *execResult) finalize(prevReceipt *types.Receipt, engine rules.Engi
 		if engine != nil {
 			if postApplyMessageFunc := engine.GetPostApplyMessageFunc(); postApplyMessageFunc != nil {
 				execResult := result.ExecutionResult
-				coinbase, err := stateReader.ReadAccountData(result.Coinbase) // to generate logs we want the initial balance
+				// Use a versionedStateReader to get the coinbase balance
+				// deterministically from the block's version map (which
+				// includes fee-calc writes from prior txs) instead of
+				// reading from pe.rs whose content depends on apply-loop
+				// timing.
+				cbReader := state.NewVersionedStateReader(txIndex, nil, vm, stateReader)
+				coinbase, err := cbReader.ReadAccountData(result.Coinbase) // to generate logs we want the initial balance
 
 				if err != nil {
 					return nil, nil, nil, err
@@ -1570,15 +1576,29 @@ func (be *blockExecutor) nextResult(ctx context.Context, pe *parallelExecutor, r
 					be.blockIO.RecordReads(txVersion, mergedReads)
 				}
 				if len(addWrites) > 0 {
-					existing := be.blockIO.WriteSet(txVersion.TxIndex)
-					if len(existing) > 0 {
-						combined := append(state.VersionedWrites{}, existing...)
-						combined = append(combined, addWrites...)
-						be.blockIO.RecordWrites(txVersion, combined)
-					} else {
-						log.Info(fmt.Sprintf("writing %d, a: %v", len(addWrites), addWrites))
-						be.blockIO.RecordWrites(txVersion, addWrites)
-					}
+					// Merge finalization writes with existing execution writes.
+					// The finalization replays result.TxOut via ApplyVersionedWrites
+					// and adds fee calculation changes, but its VersionedWrites(true)
+					// may omit entries when the optimistic execution ran with stale
+					// state (e.g., an EIP-7702 delegation set by a prior tx was not
+					// visible). In that case the re-execution stored the correct
+					// writes in blockIO, but the finalization—which replays the
+					// potentially incomplete TxOut—drops them. Merging ensures that
+					// entries present in the execution writes but absent from the
+					// finalization writes are preserved, while finalization-only
+					// entries (fee calc, post-apply) are added.
+					existingWrites := be.blockIO.WriteSet(txVersion.TxIndex)
+					merged := MergeVersionedWrites(existingWrites, addWrites)
+					be.blockIO.RecordWrites(txVersion, merged)
+
+					// Flush the merged writes (including fee calc changes)
+					// to the version map so that subsequent per-tx
+					// finalizations see the full post-tx state (execution
+					// + fees) when reading via the version map fallback
+					// chain.  Without this, later txs' fee calc reads the
+					// coinbase balance without prior fees, producing
+					// non-deterministic BAL (EIP-7928) hashes.
+					be.versionMap.FlushVersionedWrites(merged, true, "")
 				}
 
 				stateUpdates := stateWriter.WriteSet()
```

### execution/state/intra_block_state.go
```diff
@@ -1551,6 +1551,20 @@ func (sdb *IntraBlockState) getStateObject(addr accounts.Address, recordRead boo
 	obj := newObject(sdb, addr, account, account)
 	if code != nil {
 		obj.code = code
+		// When code is loaded from the version map (written by a prior tx),
+		// synchronise the stateObject's CodeHash with the actual code.
+		// refreshVersionedAccount above may not have updated the account's
+		// CodeHash because the base-reader version (sdb.Version()) makes the
+		// version check (cversion.TxIndex > readVersion.TxIndex) fail for
+		// entries from earlier transactions.  Without this fix, the stale
+		// CodeHash causes the "revert to original" optimisation in SetCode
+		// to incorrectly delete code writes when clearing a delegation that
+		// was set by a prior transaction in the same block.
+		codeHash := accounts.InternCodeHash(crypto.Keccak256Hash(code))
+		if codeHash != obj.data.CodeHash {
+			obj.data.CodeHash = codeHash
+			obj.original.CodeHash = codeHash
+		}
 	}
 	sdb.setStateObject(addr, obj)
 	return obj, nil
@@ -2360,6 +2374,23 @@ func (sdb *IntraBlockState) VersionedWrites(checkDirty bool) VersionedWrites {
 // Apply entries in a given write set to StateDB. Note that this function does not change MVHashMap nor write set
 // of the current StateDB.
 func (sdb *IntraBlockState) ApplyVersionedWrites(writes VersionedWrites) error {
+	// Sort writes by (Address, Path, Key) to ensure deterministic processing
+	// order.  VersionedWrites come from WriteSet map iteration (Go maps have
+	// non-deterministic order).  Processing order matters because some paths
+	// (CodePath, SelfDestructPath) call GetOrNewStateObject which triggers a
+	// read from the stateReader.  If a BalancePath write for the same address
+	// has already been processed, the state object is already loaded and no
+	// read occurs; otherwise an extra read is recorded.  Different reads
+	// produce different EIP-7928 BAL hashes.
+	sort.Slice(writes, func(i, j int) bool {
+		if c := writes[i].Address.Cmp(writes[j].Address); c != 0 {
+			return c < 0
+		}
+		if writes[i].Path != writes[j].Path {
+			return writes[i].Path < writes[j].Path
+		}
+		return writes[i].Key.Cmp(writes[j].Key) < 0
+	})
 	for i := range writes {
 		path := writes[i].Path
 		val := writes[i].Val
```

### execution/state/versionedio.go
```diff
@@ -253,6 +253,15 @@ func (vr *versionedStateReader) ReadAccountData(address accounts.Address) (*acco
 		}
 	}
 
+	// Check version map for AddressPath — handles accounts created by
+	// prior transactions in the same block that aren't in the read set.
+	if vr.versionMap != nil {
+		if acc, ok := versionedUpdate[*accounts.Account](vr.versionMap, address, AddressPath, accounts.NilKey, vr.txIndex); ok && acc != nil {
+			updated := vr.applyVersionedUpdates(address, *acc)
+			return &updated, nil
+		}
+	}
+
 	if vr.stateReader != nil {
 		account, err := vr.stateReader.ReadAccountData(address)
 
@@ -326,6 +335,13 @@ func (vr versionedStateReader) ReadAccountStorage(address accounts.Address, key
 		return val, true, nil
 	}
 
+	// Check version map for storage written by prior transactions.
+	if vr.versionMap != nil {
+		if val, ok := versionedUpdate[uint256.Int](vr.versionMap, address, StoragePath, key, vr.txIndex); ok {
+			return val, true, nil
+		}
+	}
+
 	if vr.stateReader != nil {
 		return vr.stateReader.ReadAccountStorage(address, key)
 	}
@@ -356,6 +372,14 @@ func (vr versionedStateReader) ReadAccountCode(address accounts.Address) ([]byte
 		}
 	}
 
+	// Check version map for CodePath entries written by prior transactions
+	// (e.g. EIP-7702 delegation set by an earlier tx in the same block).
+	if vr.versionMap != nil {
+		if code, ok := versionedUpdate[[]byte](vr.versionMap, address, CodePath, accounts.NilKey, vr.txIndex); ok {
+			return code, nil
+		}
+	}
+
 	if vr.stateReader != nil {
 		return vr.stateReader.ReadAccountCode(address)
 	}
@@ -370,6 +394,12 @@ func (vr versionedStateReader) ReadAccountCodeSize(address accounts.Address) (in
 		}
 	}
 
+	if vr.versionMap != nil {
+		if code, ok := versionedUpdate[[]byte](vr.versionMap, address, CodePath, accounts.NilKey, vr.txIndex); ok {
+			return len(code), nil
+		}
+	}
+
 	if vr.stateReader != nil {
 		return vr.stateReader.ReadAccountCodeSize(address)
 	}
```

### execution/state/versionmap.go
```diff
@@ -126,6 +126,12 @@ func (vm *VersionMap) Write(addr accounts.Address, path AccountPath, key account
 	vm.mu.Lock()
 	defer vm.mu.Unlock()
 
+	vm.writeLocked(addr, path, key, v, data, complete)
+}
+
+// writeLocked performs the write without acquiring the lock.
+// Caller must hold vm.mu.Lock().
+func (vm *VersionMap) writeLocked(addr accounts.Address, path AccountPath, key accounts.StorageKey, v Version, data any, complete bool) {
 	cells := vm.getKeyCells(addr, path, key, func(addr accounts.Address, path AccountPath, key accounts.StorageKey) (cells *btree.Map[int, *WriteCell]) {
 		it, ok := vm.s[addr]
 		cells = &btree.Map[int, *WriteCell]{}
@@ -218,12 +224,21 @@ func (vm *VersionMap) Read(addr accounts.Address, path AccountPath, key accounts
 	return
 }
 
+// FlushVersionedWrites atomically flushes all writes to the version map
+// under a single lock acquisition. This prevents concurrent readers from
+// observing a partially-flushed state (e.g. seeing an AddressPath write
+// but not the corresponding CodePath write from the same transaction),
+// which could cause non-deterministic BAL (EIP-7928) hashes during
+// parallel execution.
 func (vm *VersionMap) FlushVersionedWrites(writes VersionedWrites, complete bool, tracePrefix string) {
+	vm.mu.Lock()
+	defer vm.mu.Unlock()
+
 	for _, v := range writes {
 		if vm.trace {
 			fmt.Println(tracePrefix, "FLSH", v.String())
 		}
-		vm.Write(v.Address, v.Path, v.Key, v.Version, v.Val, complete)
+		vm.writeLocked(v.Address, v.Path, v.Key, v.Version, v.Val, complete)
 	}
 }
 
```
