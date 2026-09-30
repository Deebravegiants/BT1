# [?] op-node: Fix race condition while closing OpNode (#7303)

## Summary
Severity: Unknown
Chain: Kroma
Component: kroma-network/kroma
Published: 2023-09-19
Source: https://github.com/kroma-network/kroma/commit/5d9369748e10db2272b168fab99b2f016f1bd0a4
Type: security-commit

## Details
op-node: Fix race condition while closing OpNode (#7303)

Before the `OpNode` closes it closes its data sources. If the runtime
config reloader goroutine is still using the data sources then it
may creates a goroutine panic. Specifically, when a `limitClient` is
used, it will be fail to write an in-flight request to its semaphore
after the client is closed.

## Patch
### op-node/node/node.go
```diff
@@ -49,6 +49,9 @@ type OpNode struct {
 	resourcesCtx   context.Context
 	resourcesClose context.CancelFunc
 
+	// Indicates when it's safe to close data sources used by the runtimeConfig bg loader
+	runtimeConfigReloaderDone chan struct{}
+
 	closed atomic.Bool
 }
 
@@ -197,9 +200,8 @@ func (n *OpNode) initRuntimeConfig(ctx context.Context, cfg *Config) error {
 			return l1Head, err
 		}
 
-		n.handleProtocolVersionsUpdate(ctx)
-
-		return l1Head, nil
+		err = n.handleProtocolVersionsUpdate(ctx)
+		return l1Head, err
 	}
 
 	// initialize the runtime config before unblocking
@@ -210,10 +212,10 @@ func (n *OpNode) initRuntimeConfig(ctx context.Context, cfg *Config) error {
 	}
 
 	// start a background loop, to keep reloading it at the configured reload interval
-	go func(ctx context.Context, reloadInterval time.Duration) {
+	reloader := func(ctx context.Context, reloadInterval time.Duration) bool {
 		if reloadInterval <= 0 {
 			n.log.Debug("not running runtime-config reloading background loop")
-			return
+			return false
 		}
 		ticker := time.NewTicker(reloadInterval)
 		defer ticker.Stop()
@@ -222,13 +224,30 @@ func (n *OpNode) initRuntimeConfig(ctx context.Context, cfg *Config) error {
 			case <-ticker.C:
 				// If the reload fails, we will try again the next interval.
 				// Missing a runtime-config update is not critical, and we do not want to overwhelm the L1 RPC.
-				if l1Head, err := reload(ctx); err != nil {
-					n.log.Warn("failed to reload runtime config", "err", err)
-				} else {
+				l1Head, err := reload(ctx)
+				switch err {
+				case errNodeHalt, nil:
 					n.log.Debug("reloaded runtime config", "l1_head", l1Head)
+					if err == errNodeHalt {
+						return true
+					}
+				default:
+					n.log.Warn("failed to reload runtime config", "err", err)
 				}
 			case <-ctx.Done():
-				return
+				return false
+			}
+		}
+	}
+
+	n.runtimeConfigReloaderDone = make(chan struct{})
+	// Manages the lifetime of reloader. In order to safely Close the OpNode
+	go func(ctx context.Context, reloadInterval time.Duration) {
+		halt := reloader(ctx, reloadInterval)
+		close(n.runtimeConfigReloaderDone)
+		if halt {
+			if err := n.Close(); err != nil {
+				n.log.Error("Failed to halt rollup", "err", err)
 			}
 		}
 	}(n.resourcesCtx, cfg.RuntimeConfigReloadInterval) // this keeps running after initialization
@@ -499,6 +518,11 @@ func (n *OpNode) Close() error {
 		}
 	}
 
+	// Wait for the runtime config loader to be done using the data sources before closing them
+	if n.runtimeConfigReloaderDone != nil {
+		<-n.runtimeConfigReloaderDone
+	}
+
 	// close L2 engine RPC client
 	if n.l2Source != nil {
 		n.l2Source.Close()
```

### op-node/node/superchain.go
```diff
@@ -2,18 +2,21 @@ package node
 
 import (
 	"context"
+	"errors"
 
 	"github.com/ethereum-optimism/optimism/op-node/rollup"
 	"github.com/ethereum/go-ethereum/eth/catalyst"
 	"github.com/ethereum/go-ethereum/params"
 )
 
-func (n *OpNode) handleProtocolVersionsUpdate(ctx context.Context) {
+var errNodeHalt = errors.New("opted to halt, unprepared for protocol change")
+
+func (n *OpNode) handleProtocolVersionsUpdate(ctx context.Context) error {
 	recommended := n.runCfg.RecommendedProtocolVersion()
 	required := n.runCfg.RequiredProtocolVersion()
 	// if the protocol version sources are disabled we do not process them
 	if recommended == (params.ProtocolVersion{}) && required == (params.ProtocolVersion{}) {
-		return
+		return nil
 	}
 	local := rollup.OPStackSupport
 	// forward to execution engine, and get back the protocol version that op-geth supports
@@ -30,20 +33,20 @@ func (n *OpNode) handleProtocolVersionsUpdate(ctx context.Context) {
 	catalyst.LogProtocolVersionSupport(n.log.New("node", "engine"), local, required, "required")
 
 	// We may need to halt the node, if the user opted in to handling incompatible protocol-version signals
-	n.HaltMaybe()
+	return n.haltMaybe()
 }
 
-// HaltMaybe halts the rollup node if the runtime config indicates an incompatible required protocol change
+// haltMaybe returns errNodeHalt if the runtime config indicates an incompatible required protocol change
 // and the node is configured to opt-in to halting at this protocol-change level.
-func (n *OpNode) HaltMaybe() {
+func (n *OpNode) haltMaybe() error {
 	local := rollup.OPStackSupport
 	required := n.runCfg.RequiredProtocolVersion()
 	if haltMaybe(n.rollupHalt, local.Compare(required)) { // halt if we opted in to do so at this granularity
 		n.log.Error("Opted to halt, unprepared for protocol change", "required", required, "local", local)
-		if err := n.Close(); err != nil {
-			n.log.Error("Failed to halt rollup", "err", err)
-		}
+		// Avoid deadlocking the runtime config reloader by closing the OpNode elsewhere
+		return errNodeHalt
 	}
+	return nil
 }
 
 // haltMaybe returns true when we should halt, given the halt-option and required-version comparison
```
