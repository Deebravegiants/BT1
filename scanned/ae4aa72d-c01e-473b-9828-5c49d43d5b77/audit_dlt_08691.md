# [?] fix race condition and update tests

## Summary
Severity: Unknown
Chain: Arbitrum
Component: OffchainLabs/nitro
Published: 2026-03-31
Source: https://github.com/OffchainLabs/nitro/commit/7e2f334ae49628ef19586a160ad37fb876293dfe
Type: security-commit

## Details
fix race condition and update tests

Signed-off-by: Igor Braga <5835477+bragaigor@users.noreply.github.com>

## Patch
### arbos/programs/native.go
```diff
@@ -64,8 +64,24 @@ func SetAllowFallback(enabled bool) {
 	log.Info("Compiler fallback for Stylus compilation configured", "enabled", enabled)
 }
 
+// configuredNativeStackSize stores the stack size set at startup so that
+// retryOnStackOverflow can always restore to the correct base value,
+// regardless of concurrent goroutines mutating the process-wide default.
+// Only written by SetInitialNativeStackSize (called once at node startup).
+var configuredNativeStackSize atomic.Uint64
+
+// SetInitialNativeStackSize configures the Wasmer coroutine stack size and
+// records it as the baseline for retry recovery. Call once at node startup.
+func SetInitialNativeStackSize(size uint64) {
+	SetNativeStackSize(size)
+	if size > 0 {
+		configuredNativeStackSize.Store(size)
+	}
+}
+
 // SetNativeStackSize configures the Wasmer coroutine stack size for Stylus execution.
 // If size is 0, the existing default (1 MB) is kept.
+// Does NOT update the configured baseline — use SetInitialNativeStackSize at startup.
 func SetNativeStackSize(size uint64) {
 	C.stylus_set_native_stack_size(u64(size))
 }
@@ -450,6 +466,11 @@ func callProgram(
 
 	savedGas := scope.Contract.Gas
 
+	// Snapshot the StateDB before the first attempt so we can revert any partial
+	// state changes (storage writes, subcalls) if the call hits a native stack
+	// overflow and we need to retry. Snapshot is cheap — it just records a journal ID.
+	snapshot := db.Snapshot()
+
 	// First attempt with the pre-compiled (singlepass) ASM.
 	status, output := doStylusCall(localAsm, calldata, stylusParams, evm, tracingInfo, scope, memoryModel, evmData, debug, runCtx)
 
@@ -458,7 +479,7 @@ func callProgram(
 			address, moduleHash,
 			scope, evm, tracingInfo, calldata, evmData, stylusParams,
 			memoryModel, runCtx, savedGas, debug,
-			db, code, params, program,
+			db, snapshot, code, params, program,
 		)
 	}
 
@@ -498,6 +519,7 @@ func retryOnStackOverflow(
 	savedGas uint64,
 	debug bool,
 	db vm.StateDB,
+	snapshot int,
 	code []byte,
 	params *StylusParams,
 	program Program,
@@ -521,35 +543,41 @@ func retryOnStackOverflow(
 		return userNativeStackOverflow, nil
 	}
 
-	// Retry with cranelift ASM.
+	// Retry with cranelift ASM. Revert any partial state changes the crashed
+	// singlepass attempt may have made via host I/O before the SIGSEGV.
+	db.RevertToSnapshot(snapshot)
 	scope.Contract.Gas = savedGas
 	status, output := doStylusCall(craneliftAsm, calldata, stylusParams, evm, tracingInfo, scope, memoryModel, evmData, debug, runCtx)
 	if status != userNativeStackOverflow {
 		return status, output
 	}
 
 	// Cranelift also overflowed — double the stack size once and retry with cranelift.
-	originalStackSize := GetNativeStackSize()
+	// Use the startup-configured value as the base so that concurrent goroutines
+	// always double from and restore to the same known-good value.
+	baseStackSize := configuredNativeStackSize.Load()
 	defer func() {
-		SetNativeStackSize(originalStackSize)
+		SetNativeStackSize(baseStackSize)
 		DrainStackPool()
 	}()
 
-	newStackSize := originalStackSize * 2
+	newStackSize := baseStackSize * 2
 	if newStackSize > maxNativeStackSize {
 		newStackSize = maxNativeStackSize
 	}
-	if newStackSize <= originalStackSize {
+	if newStackSize <= baseStackSize {
 		log.Error("native stack overflow at max stack size, giving up",
-			"program", address, "module", moduleHash, "stackSize", originalStackSize)
+			"program", address, "module", moduleHash, "stackSize", baseStackSize)
 		return userNativeStackOverflow, nil
 	}
 
 	log.Warn("native stack overflow with cranelift, doubling stack size",
-		"program", address, "oldSize", originalStackSize, "newSize", newStackSize)
+		"program", address, "oldSize", baseStackSize, "newSize", newStackSize)
 	SetNativeStackSize(newStackSize)
 	DrainStackPool()
 
+	// Revert any partial state changes from the cranelift attempt before retrying.
+	db.RevertToSnapshot(snapshot)
 	scope.Contract.Gas = savedGas
 	return doStylusCall(craneliftAsm, calldata, stylusParams, evm, tracingInfo, scope, memoryModel, evmData, debug, runCtx)
 }
```

### arbos/programs/testcompile.go
```diff
@@ -485,7 +485,7 @@ func testRetryOnStackOverflow() error {
 		return fmt.Errorf("failed setting target: %w", err)
 	}
 
-	SetNativeStackSize(32 * 1024)
+	SetInitialNativeStackSize(32 * 1024)
 	DrainStackPool()
 
 	gas := uint64(0xfffffffffffffff)
@@ -505,11 +505,12 @@ func testRetryOnStackOverflow() error {
 	allowFallback.Store(false)
 	runCtx := core.NewMessageCommitContext([]rawdb.WasmTarget{localTarget})
 
+	snapshot := db.Snapshot()
 	status, _ := retryOnStackOverflow(
 		common.Address{}, moduleHash,
 		scope, evm, nil, []byte{}, &EvmData{}, stylusParams,
 		memModel, runCtx, gas, true,
-		db, nil, nil, Program{version: 1},
+		db, snapshot, nil, nil, Program{version: 1},
 	)
 	if status != userNativeStackOverflow {
 		return fmt.Errorf("allowFallback=false: expected NativeStackOverflow, got %d", status)
@@ -524,7 +525,7 @@ func testRetryOnStackOverflow() error {
 		common.Address{}, moduleHash,
 		scope, evm, nil, []byte{}, &EvmData{}, stylusParams,
 		memModel, offChainCtx, gas, true,
-		db, nil, nil, Program{version: 1},
+		db, snapshot, nil, nil, Program{version: 1},
 	)
 	if status != userNativeStackOverflow {
 		return fmt.Errorf("off-chain: expected NativeStackOverflow, got %d", status)
@@ -669,7 +670,7 @@ func testStackDoublingGivesUp() error {
 	}
 
 	// Set the stack to exactly maxNativeStackSize.
-	SetNativeStackSize(maxNativeStackSize)
+	SetInitialNativeStackSize(maxNativeStackSize)
 	DrainStackPool()
 
 	gas := uint64(0xfffffffffffffff)
@@ -690,11 +691,12 @@ func testStackDoublingGivesUp() error {
 	runCtx := core.NewMessageCommitContext([]rawdb.WasmTarget{localTarget})
 	allowFallback.Store(true)
 
+	snapshot := db.Snapshot()
 	retryStatus, _ := retryOnStackOverflow(
 		common.Address{}, moduleHash,
 		scope, evm, nil, []byte{}, &EvmData{}, stylusParams,
 		memModel, runCtx, gas, true,
-		db, nil, nil, Program{version: 1},
+		db, snapshot, nil, nil, Program{version: 1},
 	)
 
 	// Cranelift at 100MB should succeed (out-of-ink or out-of-stack), not overflow.
@@ -736,7 +738,7 @@ func testCraneliftFallbackInRetry() error {
 	}
 
 	// Use a tiny stack so singlepass overflows.
-	SetNativeStackSize(32 * 1024)
+	SetInitialNativeStackSize(32 * 1024)
 	DrainStackPool()
 
 	gas := uint64(0xfffffffffffffff)
@@ -758,11 +760,12 @@ func testCraneliftFallbackInRetry() error {
 	runCtx := core.NewMessageCommitContext([]rawdb.WasmTarget{localTarget})
 	allowFallback.Store(true)
 
+	snapshot := db.Snapshot()
 	status, _ := retryOnStackOverflow(
 		common.Address{}, moduleHash,
 		scope, evm, nil, []byte{}, &EvmData{}, stylusParams,
 		memModel, runCtx, gas, true,
-		db, nil, nil, Program{version: 1},
+		db, snapshot, nil, nil, Program{version: 1},
 	)
 
 	// Cranelift should have succeeded (out-of-ink or out-of-stack, not overflow).
```

### crates/stylus/src/evm_api.rs
```diff
@@ -1,13 +1,14 @@
 // Copyright 2022-2026, Offchain Labs, Inc.
 // For license information, see https://github.com/OffchainLabs/nitro/blob/master/LICENSE.md
 
-use crate::GoSliceData;
 use arbutil::evm::{
     api::{EvmApiMethod, Gas, EVM_API_METHOD_REQ_OFFSET},
     req::RequestHandler,
 };
 use prover::RustSlice;
 
+use crate::GoSliceData;
+
 #[derive(Clone, Copy)]
 #[repr(C)]
 pub struct NativeRequestHandler {
```

### crates/stylus/src/run.rs
```diff
@@ -3,16 +3,19 @@
 
 #![allow(clippy::redundant_closure_call)]
 
-use crate::{env::Escape, native::NativeInstance};
 use arbutil::evm::{
     api::{DataReader, EvmApi, Ink},
     user::UserOutcome,
 };
 use eyre::{eyre, Result};
-use prover::machine::Machine;
-use prover::programs::{prelude::*, STYLUS_ENTRY_POINT};
+use prover::{
+    machine::Machine,
+    programs::{prelude::*, STYLUS_ENTRY_POINT},
+};
 use wasmer_types::TrapCode;
 
+use crate::{env::Escape, native::NativeInstance};
+
 pub trait RunProgram {
     fn run_main(&mut self, args: &[u8], config: StylusConfig, ink: Ink) -> Result<UserOutcome>;
 }
```

### execution/gethexec/executionengine.go
```diff
@@ -344,7 +344,7 @@ func (s *ExecutionEngine) Initialize(rustCacheCapacityMB uint32, targetConfig *S
 	}
 	s.wasmTargets = targetConfig.WasmTargets()
 	programs.SetAllowFallback(targetConfig.AllowFallback)
-	programs.SetNativeStackSize(targetConfig.NativeStackSize)
+	programs.SetInitialNativeStackSize(targetConfig.NativeStackSize)
 	return nil
 }
 
```

### execution/gethexec/wasmstorerebuilder.go
```diff
@@ -71,7 +71,7 @@ func RebuildWasmStore(ctx context.Context, wasmStore ethdb.KeyValueStore, execut
 	}
 	targets := targetConfig.WasmTargets()
 	programs.SetAllowFallback(targetConfig.AllowFallback)
-	programs.SetNativeStackSize(targetConfig.NativeStackSize)
+	programs.SetInitialNativeStackSize(targetConfig.NativeStackSize)
 
 	latestHeader := l2Blockchain.CurrentBlock()
 	arbosVersion := types.DeserializeHeaderExtraInformation(latestHeader).ArbOSFormatVersion
```
