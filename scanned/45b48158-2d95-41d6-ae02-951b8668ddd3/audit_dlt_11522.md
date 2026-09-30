# [?] fix: use WaitForTx to avoid race condition in TestPriorityByGasPrice

## Summary
Severity: Unknown
Chain: Celestia
Component: celestiaorg/celestia-app
Published: 2026-03-05
Source: https://github.com/celestiaorg/celestia-app/commit/b2040820f9ca84757c33a853a7d62fb2aa5330c3
Type: security-commit

## Details
fix: use WaitForTx to avoid race condition in TestPriorityByGasPrice

Replace direct Client.Tx() call with the existing WaitForTx helper
which polls until the transaction is indexed. The direct call was
failing in CI because the tx indexer hadn't caught up yet.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

## Patch
### app/test/priority_test.go
```diff
@@ -1,7 +1,6 @@
 package app_test
 
 import (
-	"encoding/hex"
 	"math/rand"
 	"sort"
 	"sync"
@@ -104,10 +103,8 @@ func (s *PriorityTestSuite) TestPriorityByGasPrice() {
 	// note: use rpc types because they contain the tx index
 	heightMap := make(map[int64][]*rpctypes.ResultTx)
 	for hash := range hashes {
-		// use the core rpc type because it contains the tx index
-		hash, err := hex.DecodeString(hash)
-		require.NoError(t, err)
-		coreRes, err := s.cctx.Client.Tx(s.cctx.GoContext(), hash, false)
+		// use WaitForTx to poll until the tx is indexed
+		coreRes, err := s.cctx.WaitForTx(hash, 10)
 		require.NoError(t, err)
 		heightMap[coreRes.Height] = append(heightMap[coreRes.Height], coreRes)
 	}
```
