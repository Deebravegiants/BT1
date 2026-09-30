# [?] gc: fix a potential deadlock

## Summary
Severity: Unknown
Chain: IPFS
Component: ipfs/kubo
Published: 2019-03-21
Source: https://github.com/ipfs/kubo/commit/6f4fc6ac31fed8242aea27931bb4d3bc452d39d6
Type: security-commit

## Details
gc: fix a potential deadlock

Events:

1. User triggers a GC.
2. User aborts the GC.
3. We fail to delete a block when the output channel is already full.

This is really unlikely to happen in practice but it's still incorrect.

Could be related to #6107

License: MIT
Signed-off-by: Steven Allen <steven@stebalien.com>

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
