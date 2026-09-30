# [?] Fix MT cache data race (#650)

## Summary
Severity: Unknown
Chain: Polygon zkEVM
Component: 0xPolygon/zkevm-node
Published: 2022-05-17
Source: https://github.com/0xPolygon/zkevm-node/commit/df7bc4bb63d5bff6bec9eb072baad046ac07f88b
Type: security-commit

## Details
Fix MT cache data race (#650)

## Patch
### state/tree/cache.go
```diff
@@ -55,6 +55,9 @@ func newNodeCache() *nodeCache {
 func (nc *nodeCache) get(key []uint64) ([]uint64, error) {
 	keyStr := h4ToString(key)
 
+	nc.lock.Lock()
+	defer nc.lock.Unlock()
+
 	item, ok := nc.data[keyStr]
 	if !ok {
 		return nil, errMTNodeCacheItemNotFound
@@ -64,14 +67,14 @@ func (nc *nodeCache) get(key []uint64) ([]uint64, error) {
 
 // set inserts a new MT node cache entry.
 func (nc *nodeCache) set(key []uint64, value []uint64) error {
+	nc.lock.Lock()
+	defer nc.lock.Unlock()
+
 	if len(nc.data) >= maxMTNodeCacheEntries {
 		return errors.New("MT node cache is full")
 	}
 	keyStr := h4ToString(key)
 
-	nc.lock.Lock()
-	defer nc.lock.Unlock()
-
 	nc.data[keyStr] = value
 
 	return nil
```

### state/tree/cache_test.go
```diff
@@ -1,6 +1,7 @@
 package tree
 
 import (
+	"sync"
 	"testing"
 
 	"github.com/hermeznetwork/hermez-core/test/testutils"
@@ -145,3 +146,35 @@ func TestMTNodeCacheClear(t *testing.T) {
 
 	require.Zero(t, len(subject.data))
 }
+
+func TestConcurrentAccess(t *testing.T) {
+	subject := newNodeCache()
+	var wg sync.WaitGroup
+
+	const totalItems = 10
+	for i := 0; i < totalItems; i++ {
+		wg.Add(1)
+
+		go func(i int) {
+			defer wg.Done()
+
+			err := subject.set([]uint64{1, 1, 1, uint64(i)}, []uint64{uint64(i)})
+			require.NoError(t, err)
+		}(i)
+	}
+	wg.Wait()
+
+	for i := 0; i < totalItems; i++ {
+		wg.Add(1)
+
+		go func(i int) {
+			defer wg.Done()
+
+			value, err := subject.get([]uint64{1, 1, 1, uint64(i)})
+			require.NoError(t, err)
+
+			require.Equal(t, value, []uint64{uint64(i)})
+		}(i)
+	}
+	wg.Wait()
+}
```
