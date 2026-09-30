# [?] fix data race in tests

## Summary
Severity: Unknown
Chain: MultiversX
Component: multiversx/mx-chain-go
Published: 2025-12-23
Source: https://github.com/multiversx/mx-chain-go/commit/5e79fb61acec2a2d8b99cb8096a57df6897f2a44
Type: security-commit

## Details
fix data race in tests

## Patch
### process/missingData/missingDataResolver_test.go
```diff
@@ -567,7 +567,11 @@ func TestResolver_RequestMissingMetaHeadersBlocking(t *testing.T) {
 		require.Equal(t, process.ErrTimeIsOut, err)
 		require.False(t, mdr.allHeadersReceived())
 		require.False(t, mdr.allProofsReceived())
+
+		mutRequestedData.Lock()
+		defer mutRequestedData.Unlock()
 		require.Equal(t, len(expectedMetaHeadersRequested), len(requestedMetaHeaders))
+
 		for i := 0; i < len(expectedMetaHeadersRequested); i++ {
 			require.Contains(t, requestedMetaHeaders, expectedMetaHeadersRequested[i])
 		}
@@ -729,8 +733,14 @@ func TestResolver_RequestMissingShardHeadersBlocking(t *testing.T) {
 		require.Equal(t, process.ErrTimeIsOut, err)
 		require.False(t, mdr.allHeadersReceived())
 		require.False(t, mdr.allProofsReceived())
+
+		mutRequestedData.Lock()
 		require.ElementsMatch(t, expectedShardHeadersRequested, requestedShardHeaders)
+		mutRequestedData.Unlock()
+
+		mutRequestedProofs.Lock()
 		require.ElementsMatch(t, expectedShardHeadersRequested, requestedShardProofs)
+		mutRequestedProofs.Unlock()
 	})
 
 	t.Run("requesting missing shard headers with nonce gaps", func(t *testing.T) {
@@ -864,16 +874,26 @@ func TestResolver_RequestMissingShardHeadersBlocking(t *testing.T) {
 		require.Equal(t, process.ErrTimeIsOut, err)
 		require.False(t, mdr.allHeadersReceived())
 		require.False(t, mdr.allProofsReceived())
+
+		mutRequestedData.Lock()
 		require.ElementsMatch(t, expectedShardHeadersRequested, requestedShardHeaders)
+		mutRequestedData.Unlock()
+
+		mutRequestedProofs.Lock()
 		require.ElementsMatch(t, expectedShardHeadersRequested, requestedShardProofs)
+		mutRequestedProofs.Unlock()
 
+		mutRequestedProofs.Lock()
 		require.Len(t, requestProofNonces, 2)
 		require.ElementsMatch(t, requestProofNonces[1], []uint64{4})
 		require.ElementsMatch(t, requestProofNonces[2], []uint64{3, 4})
+		mutRequestedProofs.Unlock()
 
+		mutRequestedData.Lock()
 		require.Len(t, requestShardHeaderNonces, 2)
 		require.ElementsMatch(t, requestShardHeaderNonces[1], []uint64{4})
 		require.ElementsMatch(t, requestShardHeaderNonces[2], []uint64{3, 4})
+		mutRequestedData.Unlock()
 	})
 
 	t.Run("request missing shard headers and proofs, all received", func(t *testing.T) {
```
