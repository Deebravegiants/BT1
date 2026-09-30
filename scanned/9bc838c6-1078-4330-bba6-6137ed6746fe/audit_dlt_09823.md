# [?] [rpc] Fix nil pointer panic

## Summary
Severity: Unknown
Chain: Harmony
Component: harmony-one/harmony
Published: 2020-10-14
Source: https://github.com/harmony-one/harmony/commit/1df4054faf175ae9717803db672fddf7f533d1cb
Type: security-commit

## Details
[rpc] Fix nil pointer panic

## Patch
### rpc/tracer.go
```diff
@@ -772,7 +772,11 @@ func (s *PrivateDebugService) traceTx(ctx context.Context, message core.Message,
 		err    error
 	)
 
-	tracer = vm.NewStructLogger(config.LogConfig)
+	if config == nil {
+		tracer = vm.NewStructLogger(nil)
+	} else {
+		tracer = vm.NewStructLogger(config.LogConfig)
+	}
 
 	// Run the transaction with tracing enabled.
 	vmenv := vm.NewEVM(vmctx, statedb, s.hmy.BlockChain.Config(), vm.Config{Debug: true, Tracer: tracer})
```
