# [?] Fix db panic on NewBatch after Close (#2201)

## Summary
Severity: Unknown
Chain: Avalanche
Component: ava-labs/avalanchego
Published: 2022-11-07
Source: https://github.com/ava-labs/avalanchego/commit/538bc902164cc86b67f90cacfcb72e1d1e30d83c
Type: security-commit

## Details
Fix db panic on NewBatch after Close (#2201)

## Patch
### database/encdb/db.go
```diff
@@ -34,6 +34,7 @@ type Database struct {
 	codec  codec.Manager
 	cipher cipher.AEAD
 	db     database.Database
+	closed bool
 }
 
 // New returns a new encrypted database
@@ -56,7 +57,7 @@ func (db *Database) Has(key []byte) (bool, error) {
 	db.lock.RLock()
 	defer db.lock.RUnlock()
 
-	if db.db == nil {
+	if db.closed {
 		return false, database.ErrClosed
 	}
 	return db.db.Has(key)
@@ -66,7 +67,7 @@ func (db *Database) Get(key []byte) ([]byte, error) {
 	db.lock.RLock()
 	defer db.lock.RUnlock()
 
-	if db.db == nil {
+	if db.closed {
 		return nil, database.ErrClosed
 	}
 	encVal, err := db.db.Get(key)
@@ -80,7 +81,7 @@ func (db *Database) Put(key, value []byte) error {
 	db.lock.Lock()
 	defer db.lock.Unlock()
 
-	if db.db == nil {
+	if db.closed {
 		return database.ErrClosed
 	}
 
@@ -95,7 +96,7 @@ func (db *Database) Delete(key []byte) error {
 	db.lock.Lock()
 	defer db.lock.Unlock()
 
-	if db.db == nil {
+	if db.closed {
 		return database.ErrClosed
 	}
 	return db.db.Delete(key)
@@ -124,7 +125,7 @@ func (db *Database) NewIteratorWithStartAndPrefix(start, prefix []byte) database
 	db.lock.RLock()
 	defer db.lock.RUnlock()
 
-	if db.db == nil {
+	if db.closed {
 		return &nodb.Iterator{Err: database.ErrClosed}
 	}
 	return &iterator{
@@ -137,7 +138,7 @@ func (db *Database) Compact(start, limit []byte) error {
 	db.lock.Lock()
 	defer db.lock.Unlock()
 
-	if db.db == nil {
+	if db.closed {
 		return database.ErrClosed
 	}
 	return db.db.Compact(start, limit)
@@ -147,25 +148,25 @@ func (db *Database) Close() error {
 	db.lock.Lock()
 	defer db.lock.Unlock()
 
-	if db.db == nil {
+	if db.closed {
 		return database.ErrClosed
 	}
-	db.db = nil
+	db.closed = true
 	return nil
 }
 
 func (db *Database) isClosed() bool {
 	db.lock.RLock()
 	defer db.lock.RUnlock()
 
-	return db.db == nil
+	return db.closed
 }
 
 func (db *Database) HealthCheck() (interface{}, error) {
 	db.lock.RLock()
 	defer db.lock.RUnlock()
 
-	if db.db == nil {
+	if db.closed {
 		return nil, database.ErrClosed
 	}
 	return db.db.HealthCheck()
@@ -202,7 +203,7 @@ func (b *batch) Write() error {
 	b.db.lock.Lock()
 	defer b.db.lock.Unlock()
 
-	if b.db.db == nil {
+	if b.db.closed {
 		return database.ErrClosed
 	}
 
```

### database/prefixdb/db.go
```diff
@@ -34,7 +34,8 @@ type Database struct {
 	// concurrently with another operation. All other operations can hold RLock.
 	lock sync.RWMutex
 	// The underlying storage
-	db database.Database
+	db     database.Database
+	closed bool
 }
 
 // New returns a new prefixed database
@@ -69,7 +70,7 @@ func (db *Database) Has(key []byte) (bool, error) {
 	db.lock.RLock()
 	defer db.lock.RUnlock()
 
-	if db.db == nil {
+	if db.closed {
 		return false, database.ErrClosed
 	}
 	prefixedKey := db.prefix(key)
@@ -85,7 +86,7 @@ func (db *Database) Get(key []byte) ([]byte, error) {
 	db.lock.RLock()
 	defer db.lock.RUnlock()
 
-	if db.db == nil {
+	if db.closed {
 		return nil, database.ErrClosed
 	}
 	prefixedKey := db.prefix(key)
@@ -102,7 +103,7 @@ func (db *Database) Put(key, value []byte) error {
 	db.lock.RLock()
 	defer db.lock.RUnlock()
 
-	if db.db == nil {
+	if db.closed {
 		return database.ErrClosed
 	}
 	prefixedKey := db.prefix(key)
@@ -118,7 +119,7 @@ func (db *Database) Delete(key []byte) error {
 	db.lock.RLock()
 	defer db.lock.RUnlock()
 
-	if db.db == nil {
+	if db.closed {
 		return database.ErrClosed
 	}
 	prefixedKey := db.prefix(key)
@@ -152,7 +153,7 @@ func (db *Database) NewIteratorWithStartAndPrefix(start, prefix []byte) database
 	db.lock.RLock()
 	defer db.lock.RUnlock()
 
-	if db.db == nil {
+	if db.closed {
 		return &nodb.Iterator{Err: database.ErrClosed}
 	}
 	prefixedStart := db.prefix(start)
@@ -170,7 +171,7 @@ func (db *Database) Compact(start, limit []byte) error {
 	db.lock.RLock()
 	defer db.lock.RUnlock()
 
-	if db.db == nil {
+	if db.closed {
 		return database.ErrClosed
 	}
 	return db.db.Compact(db.prefix(start), db.prefix(limit))
@@ -180,25 +181,25 @@ func (db *Database) Close() error {
 	db.lock.Lock()
 	defer db.lock.Unlock()
 
-	if db.db == nil {
+	if db.closed {
 		return database.ErrClosed
 	}
-	db.db = nil
+	db.closed = true
 	return nil
 }
 
 func (db *Database) isClosed() bool {
 	db.lock.RLock()
 	defer db.lock.RUnlock()
 
-	return db.db == nil
+	return db.closed
 }
 
 func (db *Database) HealthCheck() (interface{}, error) {
 	db.lock.RLock()
 	defer db.lock.RUnlock()
 
-	if db.db == nil {
+	if db.closed {
 		return nil, database.ErrClosed
 	}
 	return db.db.HealthCheck()
@@ -267,7 +268,7 @@ func (b *batch) Write() error {
 	b.db.lock.RLock()
 	defer b.db.lock.RUnlock()
 
-	if b.db.db == nil {
+	if b.db.closed {
 		return database.ErrClosed
 	}
 	return b.Batch.Write()
```

### database/test_database.go
```diff
@@ -21,6 +21,7 @@ var Tests = []func(t *testing.T, db Database){
 	TestSimpleKeyValue,
 	TestKeyEmptyValue,
 	TestSimpleKeyValueClosed,
+	TestNewBatchClosed,
 	TestBatchPut,
 	TestBatchDelete,
 	TestBatchReset,
@@ -201,6 +202,28 @@ func TestMemorySafetyDatabase(t *testing.T, db Database) {
 	}
 }
 
+// TestNewBatchClosed tests to make sure that calling NewBatch on a closed
+// database returns a batch that errors correctly.
+func TestNewBatchClosed(t *testing.T, db Database) {
+	require := require.New(t)
+
+	err := db.Close()
+	require.NoError(err)
+
+	batch := db.NewBatch()
+	require.NotNil(batch)
+
+	key := []byte("hello")
+	value := []byte("world")
+
+	err = batch.Put(key, value)
+	require.NoError(err)
+	require.Greater(batch.Size(), 0)
+
+	err = batch.Write()
+	require.ErrorIs(err, ErrClosed)
+}
+
 // TestBatchPut tests to make sure that batched writes work as expected.
 func TestBatchPut(t *testing.T, db Database) {
 	key := []byte("hello")
```
