# [?] ethdb/pebble: prevent shutdown-panic (#27238)

## Summary
Severity: Unknown
Chain: Ethereum Classic
Component: etclabscore/core-geth
Published: 2023-05-19
Source: https://github.com/etclabscore/core-geth/commit/99394adcb8e5d2708e773b838dc92b4a0896ed2d
Type: security-commit

## Details
ethdb/pebble: prevent shutdown-panic (#27238)

One difference between pebble and leveldb is that the latter returns error when performing Get on a closed database, the former does a panic. This may be triggered during shutdown (see #27237)

This PR changes the pebble driver so we check that the db is not closed already, for several operations. It also adds tests to the db test-suite, so the previously implicit assumption of "not panic:ing at ops on closed database" is covered by tests.

## Patch
### ethdb/dbtest/testsuite.go
```diff
@@ -376,6 +376,32 @@ func TestDatabaseSuite(t *testing.T, New func() ethdb.KeyValueStore) {
 			}
 		}
 	})
+
+	t.Run("OperatonsAfterClose", func(t *testing.T) {
+		db := New()
+		db.Put([]byte("key"), []byte("value"))
+		db.Close()
+		if _, err := db.Get([]byte("key")); err == nil {
+			t.Fatalf("expected error on Get after Close")
+		}
+		if _, err := db.Has([]byte("key")); err == nil {
+			t.Fatalf("expected error on Get after Close")
+		}
+		if err := db.Put([]byte("key2"), []byte("value2")); err == nil {
+			t.Fatalf("expected error on Put after Close")
+		}
+		if err := db.Delete([]byte("key")); err == nil {
+			t.Fatalf("expected error on Delete after Close")
+		}
+
+		b := db.NewBatch()
+		if err := b.Put([]byte("batchkey"), []byte("batchval")); err != nil {
+			t.Fatalf("expected no error on batch.Put after Close, got %v", err)
+		}
+		if err := b.Write(); err == nil {
+			t.Fatalf("expected error on batch.Write after Close")
+		}
+	})
 }
 
 // BenchDatabaseSuite runs a suite of benchmarks against a KeyValueStore database
```

### ethdb/memorydb/memorydb.go
```diff
@@ -244,6 +244,9 @@ func (b *batch) Write() error {
 	b.db.lock.Lock()
 	defer b.db.lock.Unlock()
 
+	if b.db.db == nil {
+		return errMemorydbClosed
+	}
 	for _, keyvalue := range b.writes {
 		if keyvalue.delete {
 			delete(b.db.db, string(keyvalue.key))
```

### ethdb/pebble/pebble.go
```diff
@@ -70,8 +70,9 @@ type Database struct {
 	seekCompGauge       metrics.Gauge // Gauge for tracking the number of table compaction caused by read opt
 	manualMemAllocGauge metrics.Gauge // Gauge for tracking amount of non-managed memory currently allocated
 
-	quitLock sync.Mutex      // Mutex protecting the quit channel access
+	quitLock sync.RWMutex    // Mutex protecting the quit channel and the closed flag
 	quitChan chan chan error // Quit channel to stop the metrics collection before closing the database
+	closed   bool            // keep track of whether we're Closed
 
 	log log.Logger // Contextual logger tracking the database path
 
@@ -221,23 +222,29 @@ func New(file string, cache int, handles int, namespace string, readonly bool) (
 func (d *Database) Close() error {
 	d.quitLock.Lock()
 	defer d.quitLock.Unlock()
-
 	// Allow double closing, simplifies things
-	if d.quitChan == nil {
+	if d.closed {
 		return nil
 	}
-	errc := make(chan error)
-	d.quitChan <- errc
-	if err := <-errc; err != nil {
-		d.log.Error("Metrics collection failed", "err", err)
+	d.closed = true
+	if d.quitChan != nil {
+		errc := make(chan error)
+		d.quitChan <- errc
+		if err := <-errc; err != nil {
+			d.log.Error("Metrics collection failed", "err", err)
+		}
+		d.quitChan = nil
 	}
-	d.quitChan = nil
-
 	return d.db.Close()
 }
 
 // Has retrieves if a key is present in the key-value store.
 func (d *Database) Has(key []byte) (bool, error) {
+	d.quitLock.RLock()
+	defer d.quitLock.RUnlock()
+	if d.closed {
+		return false, pebble.ErrClosed
+	}
 	_, closer, err := d.db.Get(key)
 	if err == pebble.ErrNotFound {
 		return false, nil
@@ -250,6 +257,11 @@ func (d *Database) Has(key []byte) (bool, error) {
 
 // Get retrieves the given key if it's present in the key-value store.
 func (d *Database) Get(key []byte) ([]byte, error) {
+	d.quitLock.RLock()
+	defer d.quitLock.RUnlock()
+	if d.closed {
+		return nil, pebble.ErrClosed
+	}
 	dat, closer, err := d.db.Get(key)
 	if err != nil {
 		return nil, err
@@ -262,19 +274,30 @@ func (d *Database) Get(key []byte) ([]byte, error) {
 
 // Put inserts the given value into the key-value store.
 func (d *Database) Put(key []byte, value []byte) error {
+	d.quitLock.RLock()
+	defer d.quitLock.RUnlock()
+	if d.closed {
+		return pebble.ErrClosed
+	}
 	return d.db.Set(key, value, pebble.NoSync)
 }
 
 // Delete removes the key from the key-value store.
 func (d *Database) Delete(key []byte) error {
+	d.quitLock.RLock()
+	defer d.quitLock.RUnlock()
+	if d.closed {
+		return pebble.ErrClosed
+	}
 	return d.db.Delete(key, nil)
 }
 
 // NewBatch creates a write-only key-value store that buffers changes to its host
 // database until a final write is called.
 func (d *Database) NewBatch() ethdb.Batch {
 	return &batch{
-		b: d.db.NewBatch(),
+		b:  d.db.NewBatch(),
+		db: d,
 	}
 }
 
@@ -481,6 +504,7 @@ func (d *Database) meter(refresh time.Duration) {
 // when Write is called. A batch cannot be used concurrently.
 type batch struct {
 	b    *pebble.Batch
+	db   *Database
 	size int
 }
 
@@ -505,6 +529,11 @@ func (b *batch) ValueSize() int {
 
 // Write flushes any accumulated data to disk.
 func (b *batch) Write() error {
+	b.db.quitLock.RLock()
+	defer b.db.quitLock.RUnlock()
+	if b.db.closed {
+		return pebble.ErrClosed
+	}
 	return b.b.Commit(pebble.NoSync)
 }
 
```
