# [?] go/runtime/host/sandbox: Fix possible data race

## Summary
Severity: Unknown
Chain: Oasis
Component: oasisprotocol/oasis-core
Published: 2020-06-17
Source: https://github.com/oasisprotocol/oasis-core/commit/2046573522997dfbcffd3fedfecd24c751dd7827
Type: security-commit

## Details
go/runtime/host/sandbox: Fix possible data race

The data race existed because the cancel function that is referenced inside a
goroutine waiting for initialization to complete was unintentionally
overwritten.

## Patch
### .changelog/3024.bugfix.md
```diff
@@ -0,0 +1,5 @@
+go/runtime/host/sandbox: Fix possible data race
+
+The data race existed because the cancel function that is referenced inside a
+goroutine waiting for initialization to complete was unintentionally
+overwritten.
```

### go/runtime/host/sandbox/sandbox.go
```diff
@@ -315,15 +315,15 @@ func (r *sandboxedRuntime) startProcess() (err error) {
 
 	// Perform common host initialization.
 	var rtVersion *version.Version
-	initCtx, cancel := context.WithTimeout(ctx, runtimeInitTimeout)
-	defer cancel()
+	initCtx, cancelInit := context.WithTimeout(ctx, runtimeInitTimeout)
+	defer cancelInit()
 	if rtVersion, err = pc.InitHost(initCtx, conn); err != nil {
 		return fmt.Errorf("failed to initialize connection: %w", err)
 	}
 
 	// Perform configuration-specific host initialization.
-	exInitCtx, cancel := context.WithTimeout(ctx, runtimeExtendedInitTimeout)
-	defer cancel()
+	exInitCtx, cancelExInit := context.WithTimeout(ctx, runtimeExtendedInitTimeout)
+	defer cancelExInit()
 	ev, err := r.cfg.HostInitializer(exInitCtx, r, *rtVersion, p, pc)
 	if err != nil {
 		return fmt.Errorf("failed to initialize connection: %w", err)
```
