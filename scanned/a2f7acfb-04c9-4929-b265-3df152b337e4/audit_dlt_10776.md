# [?] Merge pull request #4538 from oasisprotocol/kostko/fix/multihost-deadlock

## Summary
Severity: Unknown
Chain: Oasis
Component: oasisprotocol/oasis-core
Published: 2022-03-04
Source: https://github.com/oasisprotocol/oasis-core/commit/8b733410d39e68c61350c06f86ff96bd32f9d494
Type: security-commit

## Details
Merge pull request #4538 from oasisprotocol/kostko/fix/multihost-deadlock

go/runtime/host/multi: Release lock before calling into runtime

## Patch
### .changelog/4538.bugfix.md
```diff
@@ -0,0 +1 @@
+go/runtime/host/multi: Release lock before calling into runtime
```

### go/runtime/host/multi/multi.go
```diff
@@ -92,12 +92,18 @@ func (agg *Aggregate) GetInfo(ctx context.Context) (*protocol.RuntimeInfoRespons
 func (agg *Aggregate) Call(ctx context.Context, body *protocol.Body) (rsp *protocol.Body, err error) {
 	callFn := func() error {
 		agg.l.RLock()
-		defer agg.l.RUnlock()
-
 		if agg.active == nil {
+			agg.l.RUnlock()
 			return ErrNoActiveVersion
 		}
-		rsp, err = agg.active.host.Call(ctx, body)
+		host := agg.active.host
+		// Take care to release lock before calling into the runtime as otherwise this could lead
+		// to a deadlock in case the runtime makes a call that acquires the cross node lock and at
+		// the same time SetVersion is being called to update the version with the cross node lock
+		// acquired.
+		agg.l.RUnlock()
+
+		rsp, err = host.Call(ctx, body)
 		if err != nil {
 			// All protocol-level errors are permanent.
 			return backoff.Permanent(err)
```
