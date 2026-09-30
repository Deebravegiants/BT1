# [?] add guard to avoid underflow and deleting needed nodesConfig

## Summary
Severity: Unknown
Chain: MultiversX
Component: multiversx/mx-chain-go
Published: 2026-07-09
Source: https://github.com/multiversx/mx-chain-go/commit/d5537def921ee26e794c8d6f1f344a3f74a4cac6
Type: security-commit

## Details
add guard to avoid underflow and deleting needed nodesConfig

## Patch
### sharding/nodesCoordinator/indexHashedNodesCoordinatorLite.go
```diff
@@ -67,10 +67,15 @@ func (ihnc *indexHashedNodesCoordinator) IsEpochInConfig(epoch uint32) bool {
 }
 
 func (ihnc *indexHashedNodesCoordinator) removeOlderEpochs(epoch uint32, maxDelta uint32) {
+	if epoch < maxDelta {
+		return
+	}
+	epochToRemove := epoch - maxDelta
+
 	ihnc.mutNodesConfig.Lock()
 	if len(ihnc.nodesConfig) >= int(maxDelta) {
 		for currEpoch := range ihnc.nodesConfig {
-			if currEpoch <= epoch-maxDelta {
+			if currEpoch <= epochToRemove {
 				delete(ihnc.nodesConfig, currEpoch)
 			}
 		}
```

### sharding/nodesCoordinator/indexHashedNodesCoordinatorLite_test.go
```diff
@@ -187,3 +187,46 @@ func TestIndexHashedNodesCoordinator_IsEpochInConfig(t *testing.T) {
 	exists = ihnc.IsEpochInConfig(epoch + 1)
 	assert.False(t, exists)
 }
+
+func TestIndexHashedNodesCoordinator_RemoveOlderEpochsShouldNotRemoveWhenEpochIsLessThanMaxDelta(t *testing.T) {
+	t.Parallel()
+
+	arguments := createArguments()
+	ihnc, err := NewIndexHashedNodesCoordinator(arguments)
+	require.Nil(t, err)
+
+	ihnc.nodesConfig[1] = &epochNodesConfig{}
+	ihnc.nodesConfig[2] = &epochNodesConfig{}
+	ihnc.nodesConfig[3] = &epochNodesConfig{}
+
+	ihnc.removeOlderEpochs(3, nodesCoordinatorStoredEpochs)
+
+	require.Len(t, ihnc.nodesConfig, 4)
+	require.Contains(t, ihnc.nodesConfig, uint32(0))
+	require.Contains(t, ihnc.nodesConfig, uint32(1))
+	require.Contains(t, ihnc.nodesConfig, uint32(2))
+	require.Contains(t, ihnc.nodesConfig, uint32(3))
+}
+
+func TestIndexHashedNodesCoordinator_RemoveOlderEpochsShouldRemoveOnlyOlderEpochs(t *testing.T) {
+	t.Parallel()
+
+	arguments := createArguments()
+	ihnc, err := NewIndexHashedNodesCoordinator(arguments)
+	require.Nil(t, err)
+
+	ihnc.nodesConfig[0] = &epochNodesConfig{}
+	ihnc.nodesConfig[1] = &epochNodesConfig{}
+	ihnc.nodesConfig[2] = &epochNodesConfig{}
+	ihnc.nodesConfig[3] = &epochNodesConfig{}
+	ihnc.nodesConfig[4] = &epochNodesConfig{}
+
+	ihnc.removeOlderEpochs(4, nodesCoordinatorStoredEpochs)
+
+	require.Len(t, ihnc.nodesConfig, 4)
+	require.NotContains(t, ihnc.nodesConfig, uint32(0))
+	require.Contains(t, ihnc.nodesConfig, uint32(1))
+	require.Contains(t, ihnc.nodesConfig, uint32(2))
+	require.Contains(t, ihnc.nodesConfig, uint32(3))
+	require.Contains(t, ihnc.nodesConfig, uint32(4))
+}
```
