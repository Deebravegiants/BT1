# [?] Fix the race condition on mutate trie's toRoot

## Summary
Severity: Unknown
Chain: IoTeX
Component: iotexproject/iotex-core
Published: 2018-06-23
Source: https://github.com/iotexproject/iotex-core/commit/d1278edd5b6d73f8b08ca24c187e38ade2bd39ec
Type: security-commit

## Details
Fix the race condition on mutate trie's toRoot

## Patch
### trie/trie.go
```diff
@@ -95,8 +95,9 @@ func (t *trie) Upsert(key, value []byte) error {
 
 // Get an existing entry
 func (t *trie) Get(key []byte) ([]byte, error) {
-	t.mutex.RLock()
-	defer t.mutex.RUnlock()
+	// Use write lock because t.clear() will mutate toRoot
+	t.mutex.Lock()
+	defer t.mutex.Unlock()
 
 	ptr, size, err := t.query(key)
 	t.clear()
```
