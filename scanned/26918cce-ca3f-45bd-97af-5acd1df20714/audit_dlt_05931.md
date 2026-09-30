# [?] fix: deadlock while racing `ipfs dag import` and `ipfs repo gc`

## Summary
Severity: Unknown
Chain: IPFS
Component: ipfs/kubo
Published: 2023-03-25
Source: https://github.com/ipfs/kubo/commit/bb020ea1ef8765f873e06ae4fd7f58c075b04edc
Type: security-commit

## Details
fix: deadlock while racing `ipfs dag import` and `ipfs repo gc`

This fixes a deadlock introduced in 1457b4fd4abff0bdcdccbacc26934cb7fa8e8a43.

We can't use the coreapi here because it will try to take the PinLock (RLock) again, so revert this small part of 1457b4fd4abff0bdcdccbacc26934cb7fa8e8a43.

This used cause a deadlock when concurrently running `ipfs dag import` concurrently with the GC.

The bug is that `ipfs dag import` takes an RLock with the PinLock.
*the cars are imported, leaving a wide window of time*
Then GC Takes a Lock on that same RWMutex while taking the GC Lock (it  blocks because it waits for the RLock to be released).
Then the car imports are finished and `ipfs dag import` tries to aqcuire the PinLock (doing an RLock) again in `Api().Pin`.

However at this point the RWMutex is starved, the runtime put a fence in front of RLocks if a Lock has been waiting for too lock (else you could have an endless stream of RLock / RUnlock forever delaying a Lock to ever go through).

The issue is that `ipfs dag import`'s original RLock which is blocking everyone will be released once it returns, which only happens when `Api().Pin` completes.

So we have a deadlock (ABA kind ?), because `ipfs dag import` waits on the GC Lock, which waits on `ipfs dag import`.

Calling the Pinner directly does not acquire the PinLock again, and thus does not have this issue.

## Patch
### core/commands/dag/import.go
```diff
@@ -10,7 +10,6 @@ import (
 	ipldlegacy "github.com/ipfs/go-ipld-legacy"
 	"github.com/ipfs/go-libipfs/files"
 	"github.com/ipfs/interface-go-ipfs-core/options"
-	"github.com/ipfs/interface-go-ipfs-core/path"
 	gocarv2 "github.com/ipld/go-car/v2"
 
 	"github.com/ipfs/kubo/core/commands/cmdenv"
@@ -108,6 +107,9 @@ func dagImport(req *cmds.Request, res cmds.ResponseEmitter, env cmds.Environment
 			}
 			return nil
 		}()
+		if err != nil {
+			return err
+		}
 	}
 
 	if err := batch.Commit(); err != nil {
@@ -125,11 +127,16 @@ func dagImport(req *cmds.Request, res cmds.ResponseEmitter, env cmds.Environment
 			ret := RootMeta{Cid: c}
 
 			// This will trigger a full read of the DAG in the pinner, to make sure we have all blocks.
-			// Ideally we would have a lighter merkledag.Walk() instead of the underlying merkledag.FetchDag,
-			// then pinner.PinWithMode().
-			err = api.Pin().Add(req.Context, path.IpldPath(c), options.Pin.Recursive(true))
-			if err != nil {
-				return err
+			// Ideally we would do colloring of the pinning state while importing the blocks
+			// and ensure the gray bucket is empty at the end (or use the network to download missing blocks).
+			if block, err := node.Blockstore.Get(req.Context, c); err != nil {
+				ret.PinErrorMsg = err.Error()
+			} else if nd, err := ipldlegacy.DecodeNode(req.Context, block); err != nil {
+				ret.PinErrorMsg = err.Error()
+			} else if err := node.Pinning.Pin(req.Context, nd, true); err != nil {
+				ret.PinErrorMsg = err.Error()
+			} else if err := node.Pinning.Flush(req.Context); err != nil {
+				ret.PinErrorMsg = err.Error()
 			}
 
 			return res.Emit(&CarImportOutput{Root: &ret})
```
