# [?] kvdb: fix race condition in CacheWrapper.Flush()

## Summary
Severity: Unknown
Chain: Sonic
Component: 0xsoniclabs/sonic
Published: 2019-08-05
Source: https://github.com/0xsoniclabs/sonic/commit/34b74a3ecc7f25317b6330020f26308190a9bb22
Type: security-commit

## Details
kvdb: fix race condition in CacheWrapper.Flush()

## Patch
### src/kvdb/cache_wrapper.go
```diff
@@ -59,13 +59,16 @@ func (w *CacheWrapper) fullKey(key []byte) []byte {
 
 // Put puts key-value pair into the cache.
 func (w *CacheWrapper) Put(key []byte, value []byte) error {
+	w.lock.Lock()
+	defer w.lock.Unlock()
+	return w.put(key, value)
+}
+
+func (w *CacheWrapper) put(key []byte, value []byte) error {
 	if value == nil {
 		return errors.New("CacheWrapper: value is nil")
 	}
 
-	w.lock.Lock()
-	defer w.lock.Unlock()
-
 	key = w.fullKey(key)
 
 	w.modified.Put(string(key), common.CopyBytes(value))
@@ -226,7 +229,10 @@ func (w *CacheWrapper) ForEach(prefix []byte, do func(key, val []byte) bool) err
 func (w *CacheWrapper) Delete(key []byte) error {
 	w.lock.Lock()
 	defer w.lock.Unlock()
+	return w.delete(key)
+}
 
+func (w *CacheWrapper) delete(key []byte) error {
 	key = w.fullKey(key)
 
 	w.modified.Put(string(key), nil)
@@ -258,6 +264,8 @@ func (w *CacheWrapper) NotFlushedPairs() int {
 
 // Flushes current cache into parent DB.
 func (w *CacheWrapper) Flush() error {
+	w.lock.Lock()
+	defer w.lock.Unlock()
 	batch := w.parent.NewBatch()
 	for it := w.modified.Iterator(); it.Next(); {
 		var err error
@@ -291,7 +299,7 @@ func (w *CacheWrapper) Flush() error {
 
 // cacheBatch is a batch structure.
 type cacheBatch struct {
-	db     Database
+	db     *CacheWrapper
 	writes []kv
 	size   int
 }
@@ -312,13 +320,15 @@ func (b *cacheBatch) Delete(key []byte) error {
 
 // Write writes batch into db. Not atomic.
 func (b *cacheBatch) Write() error {
+	b.db.lock.Lock()
+	defer b.db.lock.Unlock()
 	for _, kv := range b.writes {
 		var err error
 
 		if kv.v == nil {
-			err = b.db.Delete(kv.k)
+			err = b.db.delete(kv.k)
 		} else {
-			err = b.db.Put(kv.k, kv.v)
+			err = b.db.put(kv.k, kv.v)
 		}
 
 		if err != nil {
```
