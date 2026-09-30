# [?] Fix P-chain Shutdown deadlock (#2686)

## Summary
Severity: Unknown
Chain: Avalanche
Component: ava-labs/avalanchego
Published: 2024-01-31
Source: https://github.com/ava-labs/avalanchego/commit/e4fa404c8be2e25be4d026322d0ee42b0ff45043
Type: security-commit

## Details
Fix P-chain Shutdown deadlock (#2686)

## Patch
### vms/platformvm/vm.go
```diff
@@ -9,7 +9,6 @@ import (
 	"fmt"
 	"math"
 	"net/http"
-	"sync"
 	"time"
 
 	"github.com/gorilla/rpc/v2"
@@ -95,7 +94,6 @@ type VM struct {
 	onShutdownCtx context.Context
 	// Call [onShutdownCtxCancel] to cancel [onShutdownCtx] during Shutdown()
 	onShutdownCtxCancel context.CancelFunc
-	awaitShutdown       sync.WaitGroup
 
 	// TODO: Remove after v1.11.x is activated
 	pruned utils.Atomic[bool]
@@ -221,13 +219,9 @@ func (vm *VM) Initialize(
 	}
 
 	vm.onShutdownCtx, vm.onShutdownCtxCancel = context.WithCancel(context.Background())
-	vm.awaitShutdown.Add(1)
-	go func() {
-		defer vm.awaitShutdown.Done()
-
-		// Invariant: Gossip must never grab the context lock.
-		vm.Network.Gossip(vm.onShutdownCtx)
-	}()
+	// TODO: Wait for this goroutine to exit during Shutdown once the platformvm
+	// has better control of the context lock.
+	go vm.Network.Gossip(vm.onShutdownCtx)
 
 	vm.Builder = blockbuilder.New(
 		mempool,
@@ -431,8 +425,6 @@ func (vm *VM) Shutdown(context.Context) error {
 	}
 
 	vm.onShutdownCtxCancel()
-	vm.awaitShutdown.Wait()
-
 	vm.Builder.ShutdownBlockTimer()
 
 	if vm.bootstrapped.Get() {
```
