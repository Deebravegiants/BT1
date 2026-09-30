# [?] tests: fix data race in HexPatriciaHashed parallel tests (#17423)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2025-10-11
Source: https://github.com/erigontech/erigon/commit/6e3af46634106bd6af1b12db5fe7788a7fd354b4
Type: security-commit

## Details
tests: fix data race in HexPatriciaHashed parallel tests (#17423)

Fixes #17422

## Patch
### execution/commitment/hex_patricia_hashed_test.go
```diff
@@ -22,6 +22,7 @@ import (
 	"fmt"
 	"math/rand"
 	"sort"
+	"sync"
 	"testing"
 	"time"
 
@@ -33,7 +34,8 @@ import (
 	"github.com/erigontech/erigon/common/length"
 )
 
-var randSrc *rand.Rand = rand.New(rand.NewSource(42)) // fixed seed
+var randSrc = rand.New(rand.NewSource(42)) // fixed seed
+var randMu sync.Mutex
 
 func Test_HexPatriciaHashed_ResetThenSingularUpdates(t *testing.T) {
 	t.Parallel()
@@ -1858,7 +1860,9 @@ func generatePlainKeysWithSameHashPrefix(tb testing.TB, constPrefix []byte, keyL
 		if constPrefix != nil {
 			copy(key, constPrefix)
 		}
+		randMu.Lock()
 		randSrc.Read(key[len(constPrefix):])
+		randMu.Unlock()
 
 		hashed := KeyToNibblizedHash(key)
 		if len(plainKeys) == 0 {
```
