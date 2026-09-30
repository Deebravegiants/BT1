# [?] [db]fix counting_index data race (#3651)

## Summary
Severity: Unknown
Chain: IoTeX
Component: iotexproject/iotex-core
Published: 2022-10-12
Source: https://github.com/iotexproject/iotex-core/commit/436b7b54fe4894eb24074e1c43d193ceb55db2a8
Type: security-commit

## Details
[db]fix counting_index data race (#3651)

* [db]fix counting_index data race

* fix comments

## Patch
### db/counting_index.go
```diff
@@ -8,6 +8,7 @@ package db
 
 import (
 	"fmt"
+	"sync/atomic"
 
 	"github.com/pkg/errors"
 
@@ -109,7 +110,7 @@ func GetCountingIndex(kv KVStore, name []byte) (CountingIndex, error) {
 
 // Size returns the total number of keys so far
 func (c *countingIndex) Size() uint64 {
-	return c.size
+	return atomic.LoadUint64(&c.size)
 }
 
 // Add inserts a value into the index
@@ -121,13 +122,14 @@ func (c *countingIndex) Add(value []byte, inBatch bool) error {
 		return errors.Wrap(ErrInvalid, "cannot call Add in batch mode, call Commit() first to exit batch mode")
 	}
 	b := batch.NewBatch()
-	b.Put(c.bucket, byteutil.Uint64ToBytesBigEndian(c.size), value, fmt.Sprintf("failed to add %d-th item", c.size+1))
-	b.Put(c.bucket, CountKey, byteutil.Uint64ToBytesBigEndian(c.size+1), fmt.Sprintf("failed to update size = %d", c.size+1))
+	size := c.Size()
+	b.Put(c.bucket, byteutil.Uint64ToBytesBigEndian(size), value, fmt.Sprintf("failed to add %d-th item", size+1))
+	b.Put(c.bucket, CountKey, byteutil.Uint64ToBytesBigEndian(size+1), fmt.Sprintf("failed to update size = %d", size+1))
 	b.AddFillPercent(c.bucket, 1.0)
 	if err := c.kvStore.WriteBatch(b); err != nil {
 		return err
 	}
-	c.size++
+	atomic.AddUint64(&c.size, 1)
 	return nil
 }
 
@@ -136,22 +138,23 @@ func (c *countingIndex) addBatch(value []byte) error {
 	if c.batch == nil {
 		c.batch = batch.NewBatch()
 	}
-	c.batch.Put(c.bucket, byteutil.Uint64ToBytesBigEndian(c.size), value, fmt.Sprintf("failed to add %d-th item", c.size+1))
-	c.size++
+	size := c.Size()
+	c.batch.Put(c.bucket, byteutil.Uint64ToBytesBigEndian(size), value, fmt.Sprintf("failed to add %d-th item", size+1))
+	atomic.AddUint64(&c.size, 1)
 	return nil
 }
 
 // Get return value of key[slot]
 func (c *countingIndex) Get(slot uint64) ([]byte, error) {
-	if slot >= c.size {
+	if slot >= c.Size() {
 		return nil, errors.Wrapf(ErrNotExist, "slot: %d", slot)
 	}
 	return c.kvStore.Get(c.bucket, byteutil.Uint64ToBytesBigEndian(slot))
 }
 
 // Range return value of keys [start, start+count)
 func (c *countingIndex) Range(start, count uint64) ([][]byte, error) {
-	if start+count > c.size || count == 0 {
+	if start+count > c.Size() || count == 0 {
 		return nil, errors.Wrapf(ErrInvalid, "start: %d, count: %d", start, count)
 	}
 	return c.kvStore.Range(c.bucket, byteutil.Uint64ToBytesBigEndian(start), count)
@@ -162,11 +165,12 @@ func (c *countingIndex) Revert(count uint64) error {
 	if c.batch != nil {
 		return errors.Wrap(ErrInvalid, "cannot call Revert in batch mode, call Commit() first to exit batch mode")
 	}
-	if count == 0 || count > c.size {
+	size := c.Size()
+	if count == 0 || count > size {
 		return errors.Wrapf(ErrInvalid, "count: %d", count)
 	}
 	b := batch.NewBatch()
-	start := c.size - count
+	start := size - count
 	for i := uint64(0); i < count; i++ {
 		b.Delete(c.bucket, byteutil.Uint64ToBytesBigEndian(start+i), fmt.Sprintf("failed to delete %d-th item", start+i))
 	}
@@ -175,7 +179,7 @@ func (c *countingIndex) Revert(count uint64) error {
 	if err := c.kvStore.WriteBatch(b); err != nil {
 		return err
 	}
-	c.size = start
+	atomic.StoreUint64(&c.size, start)
 	return nil
 }
 
@@ -191,7 +195,8 @@ func (c *countingIndex) Commit() error {
 	if c.batch == nil {
 		return nil
 	}
-	c.batch.Put(c.bucket, CountKey, byteutil.Uint64ToBytesBigEndian(c.size), fmt.Sprintf("failed to update size = %d", c.size))
+	size := c.Size()
+	c.batch.Put(c.bucket, CountKey, byteutil.Uint64ToBytesBigEndian(size), fmt.Sprintf("failed to update size = %d", size))
 	c.batch.AddFillPercent(c.bucket, 1.0)
 	if err := c.kvStore.WriteBatch(c.batch); err != nil {
 		return err
@@ -214,7 +219,8 @@ func (c *countingIndex) Finalize() error {
 	if c.batch == nil {
 		return ErrInvalid
 	}
-	c.batch.Put(c.bucket, CountKey, byteutil.Uint64ToBytesBigEndian(c.size), fmt.Sprintf("failed to update size = %d", c.size))
+	size := c.Size()
+	c.batch.Put(c.bucket, CountKey, byteutil.Uint64ToBytesBigEndian(size), fmt.Sprintf("failed to update size = %d", size))
 	c.batch.AddFillPercent(c.bucket, 1.0)
 	c.batch = nil
 	return nil
```
