# [?] Merge pull request #6112 from ipfs/fix/gc-deadlock

## Summary
Severity: Unknown
Chain: IPFS
Component: ipfs/kubo
Published: 2019-03-21
Source: https://github.com/ipfs/kubo/commit/c0c682780efd4eeac9d6013b96bfc93afb3a1579
Type: security-commit

## Details
Merge pull request #6112 from ipfs/fix/gc-deadlock

gc: fix a potential deadlock

## Patch
### pin/gc/gc.go
```diff
@@ -83,7 +83,7 @@ func GC(ctx context.Context, bs bstore.GCBlockstore, dstor dstore.Datastore, pn
 		var removed uint64
 
 	loop:
-		for {
+		for ctx.Err() == nil { // select may not notice that we're "done".
 			select {
 			case k, ok := <-keychan:
 				if !ok {
@@ -94,8 +94,11 @@ func GC(ctx context.Context, bs bstore.GCBlockstore, dstor dstore.Datastore, pn
 					removed++
 					if err != nil {
 						errors = true
-						output <- Result{Error: &CannotDeleteBlockError{k, err}}
-						//log.Errorf("Error removing key from blockstore: %s", err)
+						select {
+						case output <- Result{Error: &CannotDeleteBlockError{k, err}}:
+						case <-ctx.Done():
+							break loop
+						}
 						// continue as error is non-fatal
 						continue loop
 					}
```
