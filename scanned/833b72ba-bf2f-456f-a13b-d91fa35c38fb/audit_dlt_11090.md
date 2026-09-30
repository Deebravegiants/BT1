# [?] op-node: Fix panic after closing P2P (#13106)

## Summary
Severity: Unknown
Chain: Boba
Component: bobanetwork/boba
Published: 2024-11-26
Source: https://github.com/bobanetwork/boba/commit/51a036d2eca82ad947f4446733cffe12b55e96f4
Type: security-commit

## Details
op-node: Fix panic after closing P2P (#13106)

When the op-node is closed, it also closes the P2P node. To prevent future usage, `n.p2pNode` is set to `nil`. However, the AsyncGossiper can still sometimes send gossip messages to the `OpNode` struct after close. Since `n.p2pNode` is `nil` at this point, the node would panic. This PR updates the `OpNode` implementation to check for this case. Access is protected via a mutex to prevent concurrency problems.

## Patch
### op-node/node/node.go
```diff
@@ -5,6 +5,7 @@ import (
 	"errors"
 	"fmt"
 	"io"
+	gosync "sync"
 	"sync/atomic"
 	"time"
 
@@ -60,6 +61,7 @@ type OpNode struct {
 	l2Source  *sources.EngineClient // L2 Execution Engine RPC bindings
 	server    *rpcServer            // RPC server hosting the rollup-node API
 	p2pNode   *p2p.NodeP2P          // P2P node functionality
+	p2pMu     gosync.Mutex          // protects p2pNode
 	p2pSigner p2p.Signer            // p2p gossip application messages will be signed with this signer
 	tracer    Tracer                // tracer to get events for testing/debugging
 	runCfg    *RuntimeConfig        // runtime configurables
@@ -434,8 +436,9 @@ func (n *OpNode) initRPCServer(cfg *Config) error {
 	if err != nil {
 		return err
 	}
-	if n.p2pEnabled() {
-		server.EnableP2P(p2p.NewP2PAPIBackend(n.p2pNode, n.log, n.metrics))
+
+	if p2pNode := n.getP2PNodeIfEnabled(); p2pNode != nil {
+		server.EnableP2P(p2p.NewP2PAPIBackend(p2pNode, n.log, n.metrics))
 	}
 	if cfg.RPC.EnableAdmin {
 		server.EnableAdminAPI(NewAdminAPI(n.l2Driver, n.metrics, n.log))
@@ -487,6 +490,8 @@ func (n *OpNode) p2pEnabled() bool {
 }
 
 func (n *OpNode) initP2P(cfg *Config) (err error) {
+	n.p2pMu.Lock()
+	defer n.p2pMu.Unlock()
 	if n.p2pNode != nil {
 		panic("p2p node already initialized")
 	}
@@ -580,21 +585,21 @@ func (n *OpNode) PublishL2Payload(ctx context.Context, envelope *eth.ExecutionPa
 	n.tracer.OnPublishL2Payload(ctx, envelope)
 
 	// publish to p2p, if we are running p2p at all
-	if n.p2pEnabled() {
+	if p2pNode := n.getP2PNodeIfEnabled(); p2pNode != nil {
 		payload := envelope.ExecutionPayload
 		if n.p2pSigner == nil {
 			return fmt.Errorf("node has no p2p signer, payload %s cannot be published", payload.ID())
 		}
 		n.log.Info("Publishing signed execution payload on p2p", "id", payload.ID())
-		return n.p2pNode.GossipOut().PublishL2Payload(ctx, envelope, n.p2pSigner)
+		return p2pNode.GossipOut().PublishL2Payload(ctx, envelope, n.p2pSigner)
 	}
 	// if p2p is not enabled then we just don't publish the payload
 	return nil
 }
 
 func (n *OpNode) OnUnsafeL2Payload(ctx context.Context, from peer.ID, envelope *eth.ExecutionPayloadEnvelope) error {
 	// ignore if it's from ourselves
-	if n.p2pEnabled() && from == n.p2pNode.Host().ID() {
+	if p2pNode := n.getP2PNodeIfEnabled(); p2pNode != nil && from == p2pNode.Host().ID() {
 		return nil
 	}
 
@@ -615,7 +620,7 @@ func (n *OpNode) OnUnsafeL2Payload(ctx context.Context, from peer.ID, envelope *
 }
 
 func (n *OpNode) RequestL2Range(ctx context.Context, start, end eth.L2BlockRef) error {
-	if n.p2pEnabled() && n.p2pNode.AltSyncEnabled() {
+	if p2pNode := n.getP2PNodeIfEnabled(); p2pNode != nil && p2pNode.AltSyncEnabled() {
 		if unixTimeStale(start.Time, 12*time.Hour) {
 			n.log.Debug(
 				"ignoring request to sync L2 range, timestamp is too old for p2p",
@@ -624,7 +629,7 @@ func (n *OpNode) RequestL2Range(ctx context.Context, start, end eth.L2BlockRef)
 				"start_time", start.Time)
 			return nil
 		}
-		return n.p2pNode.RequestL2Range(ctx, start, end)
+		return p2pNode.RequestL2Range(ctx, start, end)
 	}
 	n.log.Debug("ignoring request to sync L2 range, no sync method available", "start", start, "end", end)
 	return nil
@@ -636,7 +641,7 @@ func unixTimeStale(timestamp uint64, duration time.Duration) bool {
 }
 
 func (n *OpNode) P2P() p2p.Node {
-	return n.p2pNode
+	return n.getP2PNodeIfEnabled()
 }
 
 func (n *OpNode) RuntimeConfig() ReadonlyRuntimeConfig {
@@ -671,13 +676,17 @@ func (n *OpNode) Stop(ctx context.Context) error {
 			result = multierror.Append(result, fmt.Errorf("error stopping sequencer: %w", err))
 		}
 	}
+
+	n.p2pMu.Lock()
 	if n.p2pNode != nil {
 		if err := n.p2pNode.Close(); err != nil {
 			result = multierror.Append(result, fmt.Errorf("failed to close p2p node: %w", err))
 		}
 		// Prevent further use of p2p.
 		n.p2pNode = nil
 	}
+	n.p2pMu.Unlock()
+
 	if n.p2pSigner != nil {
 		if err := n.p2pSigner.Close(); err != nil {
 			result = multierror.Append(result, fmt.Errorf("failed to close p2p signer: %w", err))
@@ -778,3 +787,13 @@ func (n *OpNode) HTTPEndpoint() string {
 	}
 	return fmt.Sprintf("http://%s", n.server.Addr().String())
 }
+
+func (n *OpNode) getP2PNodeIfEnabled() *p2p.NodeP2P {
+	if !n.p2pEnabled() {
+		return nil
+	}
+
+	n.p2pMu.Lock()
+	defer n.p2pMu.Unlock()
+	return n.p2pNode
+}
```
