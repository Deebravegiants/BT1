# [?] Fix pebbledb memory corruption (#3020)

## Summary
Severity: Unknown
Chain: Avalanche
Component: ava-labs/avalanchego
Published: 2024-05-15
Source: https://github.com/ava-labs/avalanchego/commit/138ce145dcd0144597dee5d7e22593d4f79cf1dc
Type: security-commit

## Details
Fix pebbledb memory corruption (#3020)

## Patch
### database/pebble/batch.go
```diff
@@ -56,26 +56,18 @@ func (b *batch) Write() error {
 		return database.ErrClosed
 	}
 
-	if !b.written {
-		// This batch has not been written to the database yet.
-		if err := updateError(b.batch.Commit(pebble.Sync)); err != nil {
+	if b.written {
+		// pebble doesn't support writing a batch twice so we have to clone the
+		// batch before writing it.
+		newBatch := b.db.pebbleDB.NewBatch()
+		if err := newBatch.Apply(b.batch, nil); err != nil {
 			return err
 		}
-		b.written = true
-		return nil
+		b.batch = newBatch
 	}
 
-	// pebble doesn't support writing a batch twice so we have to clone
-	// [b] and commit the clone.
-	batchClone := b.db.pebbleDB.NewBatch()
-
-	// Copy the batch.
-	if err := batchClone.Apply(b.batch, nil); err != nil {
-		return err
-	}
-
-	// Commit the new batch.
-	return updateError(batchClone.Commit(pebble.Sync))
+	b.written = true
+	return updateError(b.batch.Commit(pebble.Sync))
 }
 
 func (b *batch) Reset() {
```

### database/pebble/batch_test.go
```diff
@@ -17,7 +17,7 @@ func TestBatch(t *testing.T) {
 	require := require.New(t)
 	dirName := t.TempDir()
 
-	db, err := New(dirName, DefaultConfigBytes, logging.NoLog{}, "", prometheus.NewRegistry())
+	db, err := New(dirName, nil, logging.NoLog{}, "", prometheus.NewRegistry())
 	require.NoError(err)
 
 	batchIntf := db.NewBatch()
```

### database/pebble/db.go
```diff
@@ -4,7 +4,6 @@
 package pebble
 
 import (
-	"bytes"
 	"context"
 	"encoding/json"
 	"errors"
@@ -44,18 +43,8 @@ var (
 		MaxOpenFiles:                4096,
 		MaxConcurrentCompactions:    1,
 	}
-
-	DefaultConfigBytes []byte
 )
 
-func init() {
-	var err error
-	DefaultConfigBytes, err = json.Marshal(DefaultConfig)
-	if err != nil {
-		panic(err)
-	}
-}
-
 type Database struct {
 	lock          sync.RWMutex
 	pebbleDB      *pebble.DB
@@ -200,17 +189,18 @@ func (db *Database) Compact(start []byte, end []byte) error {
 	}
 
 	if end == nil {
-		// The database.Database spec treats a nil [limit] as a key after all keys
-		// but pebble treats a nil [limit] as a key before all keys in Compact.
-		// Use the greatest key in the database as the [limit] to get the desired behavior.
+		// The database.Database spec treats a nil [limit] as a key after all
+		// keys but pebble treats a nil [limit] as a key before all keys in
+		// Compact. Use the greatest key in the database as the [limit] to get
+		// the desired behavior.
 		it := db.pebbleDB.NewIter(&pebble.IterOptions{})
 
 		if !it.Last() {
 			// The database is empty.
 			return it.Close()
 		}
 
-		end = it.Key()
+		end = slices.Clone(it.Key())
 		if err := it.Close(); err != nil {
 			return err
 		}
@@ -273,7 +263,7 @@ func keyRange(start, prefix []byte) *pebble.IterOptions {
 		LowerBound: prefix,
 		UpperBound: prefixToUpperBound(prefix),
 	}
-	if bytes.Compare(start, prefix) == 1 {
+	if pebble.DefaultComparer.Compare(start, prefix) == 1 {
 		opt.LowerBound = start
 	}
 	return opt
```

### database/pebble/db_test.go
```diff
@@ -16,7 +16,7 @@ import (
 
 func newDB(t testing.TB) *Database {
 	folder := t.TempDir()
-	db, err := New(folder, DefaultConfigBytes, logging.NoLog{}, "pebble", prometheus.NewRegistry())
+	db, err := New(folder, nil, logging.NoLog{}, "pebble", prometheus.NewRegistry())
 	require.NoError(t, err)
 	return db.(*Database)
 }
```

### database/pebble/iterator.go
```diff
@@ -17,7 +17,7 @@ import (
 var (
 	_ database.Iterator = (*iter)(nil)
 
-	errCouldntGetValue = errors.New("couldnt get iterator value")
+	errCouldNotGetValue = errors.New("could not get iterator value")
 )
 
 type iter struct {
@@ -63,16 +63,16 @@ func (it *iter) Next() bool {
 		return false
 	}
 
-	it.nextKey = it.iter.Key()
-
-	var err error
-	it.nextVal, err = it.iter.ValueAndErr()
+	key := it.iter.Key()
+	value, err := it.iter.ValueAndErr()
 	if err != nil {
 		it.hasNext = false
-		it.err = fmt.Errorf("%w: %w", errCouldntGetValue, err)
+		it.err = fmt.Errorf("%w: %w", errCouldNotGetValue, err)
 		return false
 	}
 
+	it.nextKey = key
+	it.nextVal = value
 	return true
 }
 
@@ -122,6 +122,11 @@ func (it *iter) release() {
 		return
 	}
 
+	// Cloning these values ensures that calling it.Key() or it.Value() after
+	// releasing the iterator will not segfault.
+	it.nextKey = slices.Clone(it.nextKey)
+	it.nextVal = slices.Clone(it.nextVal)
+
 	// Remove the iterator from the list of open iterators.
 	it.db.openIterators.Remove(it)
 
```
