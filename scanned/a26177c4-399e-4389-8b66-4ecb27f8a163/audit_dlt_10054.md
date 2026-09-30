# [?] Fix race condition in tests.

## Summary
Severity: Unknown
Chain: MultiversX
Component: multiversx/mx-chain-go
Published: 2025-09-01
Source: https://github.com/multiversx/mx-chain-go/commit/46cf3c4a45e06aa4c679f3ec938a2b8ab585453e
Type: security-commit

## Details
Fix race condition in tests.

## Patch
### dataRetriever/txpool/shardedTxPool_test.go
```diff
@@ -558,7 +558,7 @@ func TestShardedTxPool_OnProposedBlock_And_OnExecutedBlock(t *testing.T) {
 	t.Run("OnProposedBlock calls TxCache.OnProposedBlock", func(t *testing.T) {
 		t.Parallel()
 
-		err = pool.OnProposedBlock(nil, nil, nil, nil, nil)
+		err := pool.OnProposedBlock(nil, nil, nil, nil, nil)
 		require.ErrorContains(t, err, "nil block hash")
 
 		err = pool.OnProposedBlock(
@@ -574,7 +574,7 @@ func TestShardedTxPool_OnProposedBlock_And_OnExecutedBlock(t *testing.T) {
 	t.Run("OnExecutedBlock calls TxCache.OnExecutedBlock", func(t *testing.T) {
 		t.Parallel()
 
-		err = pool.OnExecutedBlock(nil)
+		err := pool.OnExecutedBlock(nil)
 		require.ErrorContains(t, err, "nil header handler")
 
 		err = pool.OnExecutedBlock(&block.HeaderV2{})
```
