# [?] Merge pull request #12019 from smartcontractkit/fix/panic-on-undialed-rpc

## Summary
Severity: Unknown
Chain: Bridge
Component: smartcontractkit/ccip
Published: 2024-02-13
Source: https://github.com/smartcontractkit/ccip/commit/60bcb420fb36c62244a9296eb92fae7cb0939428
Type: security-commit

## Details
Merge pull request #12019 from smartcontractkit/fix/panic-on-undialed-rpc

do not call an RPC if it's not Alive (#11999)

## Patch
### common/client/multi_node.go
```diff
@@ -394,6 +394,10 @@ func (c *multiNode[CHAIN_ID, SEQ, ADDR, BLOCK_HASH, TX, TX_HASH, EVENT, EVENT_OP
 			// main node is used at the end for the return value
 			continue
 		}
+
+		if n.State() != nodeStateAlive {
+			continue
+		}
 		// Parallel call made to all other nodes with ignored return value
 		wg.Add(1)
 		go func(n SendOnlyNode[CHAIN_ID, RPC_CLIENT]) {
@@ -557,6 +561,10 @@ func (c *multiNode[CHAIN_ID, SEQ, ADDR, BLOCK_HASH, TX, TX_HASH, EVENT, EVENT_OP
 			// main node is used at the end for the return value
 			continue
 		}
+
+		if n.State() != nodeStateAlive {
+			continue
+		}
 		// Parallel send to all other nodes with ignored return value
 		// Async - we do not want to block the main thread with secondary nodes
 		// in case they are unreliable/slow.
```

### common/client/multi_node_test.go
```diff
@@ -3,7 +3,7 @@ package client
 import (
 	"errors"
 	"fmt"
-	big "math/big"
+	"math/big"
 	"math/rand"
 	"testing"
 	"time"
@@ -533,8 +533,10 @@ func TestMultiNode_BatchCallContextAll(t *testing.T) {
 		// setup ok and failed auxiliary nodes
 		okNode := newMockSendOnlyNode[types.ID, multiNodeRPCClient](t)
 		okNode.On("RPC").Return(okRPC).Once()
+		okNode.On("State").Return(nodeStateAlive).Once()
 		failedNode := newMockNode[types.ID, types.Head[Hashable], multiNodeRPCClient](t)
 		failedNode.On("RPC").Return(failedRPC).Once()
+		failedNode.On("State").Return(nodeStateAlive).Once()
 
 		// setup main node
 		mainNode := newMockNode[types.ID, types.Head[Hashable], multiNodeRPCClient](t)
@@ -555,6 +557,34 @@ func TestMultiNode_BatchCallContextAll(t *testing.T) {
 		require.NoError(t, err)
 		tests.RequireLogMessage(t, observedLogs, "Secondary node BatchCallContext failed")
 	})
+	t.Run("Skips nodes that are not alive", func(t *testing.T) {
+		// setup RPCs
+		okRPC := newMultiNodeRPCClient(t)
+		okRPC.On("BatchCallContext", mock.Anything, mock.Anything).Return(nil).Twice()
+
+		// setup ok and failed auxiliary nodes
+		okNode := newMockSendOnlyNode[types.ID, multiNodeRPCClient](t)
+		okNode.On("RPC").Return(okRPC).Once()
+		okNode.On("State").Return(nodeStateAlive).Once()
+		unhealthyNode := newMockNode[types.ID, types.Head[Hashable], multiNodeRPCClient](t)
+		unhealthyNode.On("State").Return(nodeStateUnreachable).Once()
+
+		// setup main node
+		mainNode := newMockNode[types.ID, types.Head[Hashable], multiNodeRPCClient](t)
+		mainNode.On("RPC").Return(okRPC)
+		nodeSelector := newMockNodeSelector[types.ID, types.Head[Hashable], multiNodeRPCClient](t)
+		nodeSelector.On("Select").Return(mainNode).Once()
+		mn := newTestMultiNode(t, multiNodeOpts{
+			selectionMode: NodeSelectionModeRoundRobin,
+			chainID:       types.RandomID(),
+			nodes:         []Node[types.ID, types.Head[Hashable], multiNodeRPCClient]{unhealthyNode, mainNode},
+			sendonlys:     []SendOnlyNode[types.ID, multiNodeRPCClient]{okNode},
+		})
+		mn.nodeSelector = nodeSelector
+
+		err := mn.BatchCallContextAll(tests.Context(t), nil)
+		require.NoError(t, err)
+	})
 }
 
 func TestMultiNode_SendTransaction(t *testing.T) {
@@ -601,9 +631,11 @@ func TestMultiNode_SendTransaction(t *testing.T) {
 		okNode := newMockSendOnlyNode[types.ID, multiNodeRPCClient](t)
 		okNode.On("RPC").Return(okRPC).Once()
 		okNode.On("String").Return("okNode")
+		okNode.On("State").Return(nodeStateAlive).Once()
 		failedNode := newMockNode[types.ID, types.Head[Hashable], multiNodeRPCClient](t)
 		failedNode.On("RPC").Return(failedRPC).Once()
 		failedNode.On("String").Return("failedNode")
+		failedNode.On("State").Return(nodeStateAlive).Once()
 
 		// setup main node
 		mainNode := newMockNode[types.ID, types.Head[Hashable], multiNodeRPCClient](t)
@@ -632,4 +664,38 @@ func TestMultiNode_SendTransaction(t *testing.T) {
 		tests.AssertLogEventually(t, observedLogs, "Sendonly node sent transaction")
 		tests.AssertLogEventually(t, observedLogs, "RPC returned error")
 	})
+	t.Run("Skips RPCs that are unhealthy", func(t *testing.T) {
+		// setup RPCs
+		okRPC := newMultiNodeRPCClient(t)
+		okRPC.On("SendTransaction", mock.Anything, mock.Anything).Return(nil).Once()
+
+		// setup ok and failed auxiliary nodes
+		unhealthySendOnlyNode := newMockSendOnlyNode[types.ID, multiNodeRPCClient](t)
+		unhealthySendOnlyNode.On("State").Return(nodeStateUnreachable).Once()
+		unhealthyNode := newMockNode[types.ID, types.Head[Hashable], multiNodeRPCClient](t)
+		unhealthyNode.On("State").Return(nodeStateUnreachable).Once()
+
+		// setup main node
+		mainNode := newMockNode[types.ID, types.Head[Hashable], multiNodeRPCClient](t)
+		mainNode.On("RPC").Return(okRPC)
+		nodeSelector := newMockNodeSelector[types.ID, types.Head[Hashable], multiNodeRPCClient](t)
+		nodeSelector.On("Select").Return(mainNode).Once()
+		mn := newTestMultiNode(t, multiNodeOpts{
+			selectionMode: NodeSelectionModeRoundRobin,
+			chainID:       types.RandomID(),
+			nodes:         []Node[types.ID, types.Head[Hashable], multiNodeRPCClient]{unhealthyNode, mainNode},
+			sendonlys:     []SendOnlyNode[types.ID, multiNodeRPCClient]{unhealthySendOnlyNode},
+			sendOnlyErrorParser: func(err error) SendTxReturnCode {
+				if err != nil {
+					return Fatal
+				}
+
+				return Successful
+			},
+		})
+		mn.nodeSelector = nodeSelector
+
+		err := mn.SendTransaction(tests.Context(t), nil)
+		require.NoError(t, err)
+	})
 }
```
