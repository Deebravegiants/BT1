# [?] fix: machine locator error handling prevents nil dereference

## Summary
Severity: Unknown
Chain: Arbitrum
Component: OffchainLabs/nitro
Published: 2026-03-19
Source: https://github.com/OffchainLabs/nitro/commit/af84ef3ce15a056e29adc6676492cd353a2c7a40
Type: security-commit

## Details
fix: machine locator error handling prevents nil dereference

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

## Patch
### changelog/jco-machine-locator-fix.md
```diff
@@ -0,0 +1,2 @@
+### Fixed
+- Fix nil-dereference and log format in `cmd/nitro/nitro.go` when machine locator creation fails; return early instead of falling through to dereference nil locator
```

### cmd/nitro/nitro.go
```diff
@@ -407,7 +407,7 @@ func mainImpl() int {
 	if nodeConfig.Node.ParentChainReader.Enable && nodeConfig.Validation.Wasm.EnableWasmrootsCheck {
 		err := checkWasmModuleRootCompatibility(ctx, nodeConfig.Validation.Wasm, l1Client, rollupAddrs)
 		if err != nil {
-			log.Warn("failed to check if node is compatible with on-chain WASM module root", "err", err)
+			log.Error("failed to check if node is compatible with on-chain WASM module root", "err", err)
 		}
 	}
 
@@ -416,7 +416,7 @@ func mainImpl() int {
 	if traceConfig.TracerName != "" {
 		tracer, err = tracers.LiveDirectory.New(traceConfig.TracerName, json.RawMessage(traceConfig.JSONConfig))
 		if err != nil {
-			log.Error("custom tracer error:", "name", traceConfig.TracerName, "err", err)
+			log.Error("custom tracer error", "name", traceConfig.TracerName, "err", err)
 			return 1
 		}
 		log.Info("enabling custom tracer", "name", traceConfig.TracerName)
@@ -452,6 +452,7 @@ func mainImpl() int {
 		deferFuncs = append(deferFuncs, func() { closeDb(consensusDB, "consensusDB") })
 	}
 	if err != nil {
+		log.Error("error opening consensus database", "err", err)
 		return 1
 	}
 
@@ -505,16 +506,17 @@ func mainImpl() int {
 			fatalErrChan,
 		)
 		if err != nil {
-			valNode = nil
-			log.Warn("couldn't init validation node", "err", err)
+			log.Error("couldn't init validation node", "err", err)
+			return 1
 		}
 	}
 
 	var wasmModuleRoot common.Hash
 	if liveNodeConfig.Get().Node.ValidatorRequired() {
 		locator, err := server_common.NewMachineLocator(liveNodeConfig.Get().Validation.Wasm.RootPath)
 		if err != nil {
-			log.Error("failed to create machine locator: %w", err)
+			log.Error("failed to create machine locator", "err", err)
+			return 1
 		}
 		wasmModuleRoot = locator.LatestWasmModuleRoot()
 	}
```
