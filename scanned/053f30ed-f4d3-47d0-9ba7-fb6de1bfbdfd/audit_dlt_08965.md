# [?] fix data race in unit test (#4918)

## Summary
Severity: Unknown
Chain: Hyperledger Fabric
Component: hyperledger/fabric
Published: 2024-07-04
Source: https://github.com/hyperledger/fabric/commit/2e4377e528a94943807fc330744492feddf02330
Type: security-commit

## Details
fix data race in unit test (#4918)

Signed-off-by: Fedor Partanskiy <fredprtnsk@gmail.com>

## Patch
### orderer/consensus/smartbft/util_network_test.go
```diff
@@ -554,7 +554,7 @@ func createBFTChainUsingMocks(t *testing.T, node *Node, configInfo *ConfigInfo)
 				return
 			}
 			t.Logf("Node %d requested SendTransaction to node %d", node.NodeId, targetNodeId)
-			err = node.sendRequest(node.NodeId, targetNodeId, message)
+			err := node.sendRequest(node.NodeId, targetNodeId, message)
 			require.NoError(t, err)
 		}).Maybe()
 	egressCommMock.EXPECT().SendConsensus(mock.Anything, mock.Anything).Run(
@@ -564,7 +564,7 @@ func createBFTChainUsingMocks(t *testing.T, node *Node, configInfo *ConfigInfo)
 				return
 			}
 			t.Logf("Node %d requested SendConsensus to node %d of type <%s>", node.NodeId, targetNodeId, reflect.TypeOf(message.GetContent()))
-			err = node.sendMessage(node.NodeId, targetNodeId, message)
+			err := node.sendMessage(node.NodeId, targetNodeId, message)
 			require.NoError(t, err)
 		}).Maybe()
 
```
