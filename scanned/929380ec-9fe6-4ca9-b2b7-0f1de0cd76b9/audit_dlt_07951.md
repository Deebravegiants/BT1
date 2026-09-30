# [?] fix panic if config duration is set to 0 (#765)

## Summary
Severity: Unknown
Chain: Avalanche
Component: ava-labs/avalanchego
Published: 2025-01-27
Source: https://github.com/ava-labs/avalanchego/commit/3148809c874a8e3fe53d874d62d2f7e158ea3d87
Type: security-commit

## Details
fix panic if config duration is set to 0 (#765)

## Patch
### plugin/evm/gossip.go
```diff
@@ -49,7 +49,7 @@ func newTxGossipHandler[T gossip.Gossipable](
 	maxMessageSize int,
 	throttlingPeriod time.Duration,
 	throttlingLimit int,
-	validators *p2p.Validators,
+	validators p2p.ValidatorSet,
 ) txGossipHandler {
 	// push gossip messages can be handled from any peer
 	handler := gossip.NewHandler(
```

### plugin/evm/validators.go
```diff
@@ -0,0 +1,19 @@
+// (c) 2019-2020, Ava Labs, Inc. All rights reserved.
+// See the file LICENSE for licensing terms.
+
+package evm
+
+import (
+	"context"
+
+	"github.com/ava-labs/avalanchego/ids"
+	"github.com/ava-labs/avalanchego/utils/set"
+)
+
+type validatorSet struct {
+	set set.Set[ids.NodeID]
+}
+
+func (v *validatorSet) Has(ctx context.Context, nodeID ids.NodeID) bool {
+	return v.set.Contains(nodeID)
+}
```

### plugin/evm/vm.go
```diff
@@ -1120,6 +1120,11 @@ func (vm *VM) initBlockBuilding() error {
 	vm.builder = vm.NewBlockBuilder(vm.toEngine)
 	vm.builder.awaitSubmittedTxs()
 
+	var p2pValidators p2p.ValidatorSet = &validatorSet{}
+	if vm.config.PullGossipFrequency.Duration > 0 {
+		p2pValidators = vm.p2pValidators
+	}
+
 	if vm.ethTxGossipHandler == nil {
 		vm.ethTxGossipHandler = newTxGossipHandler[*GossipEthTx](
 			vm.ctx.Log,
@@ -1129,7 +1134,7 @@ func (vm *VM) initBlockBuilding() error {
 			txGossipTargetMessageSize,
 			txGossipThrottlingPeriod,
 			txGossipThrottlingLimit,
-			vm.p2pValidators,
+			p2pValidators,
 		)
 	}
 
@@ -1146,7 +1151,7 @@ func (vm *VM) initBlockBuilding() error {
 			txGossipTargetMessageSize,
 			txGossipThrottlingPeriod,
 			txGossipThrottlingLimit,
-			vm.p2pValidators,
+			p2pValidators,
 		)
 	}
 
@@ -1171,15 +1176,20 @@ func (vm *VM) initBlockBuilding() error {
 		}
 	}
 
-	vm.shutdownWg.Add(2)
-	go func() {
-		gossip.Every(ctx, vm.ctx.Log, ethTxPushGossiper, vm.config.PushGossipFrequency.Duration)
-		vm.shutdownWg.Done()
-	}()
-	go func() {
-		gossip.Every(ctx, vm.ctx.Log, vm.ethTxPullGossiper, vm.config.PullGossipFrequency.Duration)
-		vm.shutdownWg.Done()
-	}()
+	if vm.config.PushGossipFrequency.Duration > 0 {
+		vm.shutdownWg.Add(1)
+		go func() {
+			gossip.Every(ctx, vm.ctx.Log, ethTxPushGossiper, vm.config.PushGossipFrequency.Duration)
+			vm.shutdownWg.Done()
+		}()
+	}
+	if vm.config.PullGossipFrequency.Duration > 0 {
+		vm.shutdownWg.Add(1)
+		go func() {
+			gossip.Every(ctx, vm.ctx.Log, vm.ethTxPullGossiper, vm.config.PullGossipFrequency.Duration)
+			vm.shutdownWg.Done()
+		}()
+	}
 
 	if vm.atomicTxPullGossiper == nil {
 		atomicTxPullGossiper := gossip.NewPullGossiper[*atomic.GossipAtomicTx](
@@ -1198,15 +1208,20 @@ func (vm *VM) initBlockBuilding() error {
 		}
 	}
 
-	vm.shutdownWg.Add(2)
-	go func() {
-		gossip.Every(ctx, vm.ctx.Log, vm.atomicTxPushGossiper, vm.config.PushGossipFrequency.Duration)
-		vm.shutdownWg.Done()
-	}()
-	go func() {
-		gossip.Every(ctx, vm.ctx.Log, vm.atomicTxPullGossiper, vm.config.PullGossipFrequency.Duration)
-		vm.shutdownWg.Done()
-	}()
+	if vm.config.PushGossipFrequency.Duration > 0 {
+		vm.shutdownWg.Add(1)
+		go func() {
+			gossip.Every(ctx, vm.ctx.Log, vm.atomicTxPushGossiper, vm.config.PushGossipFrequency.Duration)
+			vm.shutdownWg.Done()
+		}()
+	}
+	if vm.config.PullGossipFrequency.Duration > 0 {
+		vm.shutdownWg.Add(1)
+		go func() {
+			gossip.Every(ctx, vm.ctx.Log, vm.atomicTxPullGossiper, vm.config.PullGossipFrequency.Duration)
+			vm.shutdownWg.Done()
+		}()
+	}
 
 	return nil
 }
```
