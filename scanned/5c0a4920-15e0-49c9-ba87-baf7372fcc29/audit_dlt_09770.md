# [?] fix deadlock in tests

## Summary
Severity: Unknown
Chain: Flow
Component: onflow/flow-go
Published: 2025-08-28
Source: https://github.com/onflow/flow-go/commit/861dc15970d1fd218a954713fdb54cb6328ac718
Type: security-commit

## Details
fix deadlock in tests

## Patch
### storage/operation/guarantees_test.go
```diff
@@ -3,6 +3,7 @@ package operation_test
 import (
 	"testing"
 
+	"github.com/jordanschalm/lockctx"
 	"github.com/onflow/crypto"
 	"github.com/stretchr/testify/assert"
 	"github.com/stretchr/testify/require"
@@ -78,6 +79,7 @@ func TestIndexGuaranteedCollectionByBlockHashInsertRetrieve(t *testing.T) {
 
 func TestIndexGuaranteedCollectionByBlockHashMultipleBlocks(t *testing.T) {
 	dbtest.RunWithDB(t, func(t *testing.T, db storage.DB) {
+		lockManager := storage.NewTestingLockManager()
 		blockID1 := flow.Identifier{0x10}
 		blockID2 := flow.Identifier{0x20}
 		collID1 := flow.Identifier{0x01}
@@ -96,45 +98,38 @@ func TestIndexGuaranteedCollectionByBlockHashMultipleBlocks(t *testing.T) {
 		ids2 := flow.GetIDs(set2)
 
 		// insert block 1
-		lockManager := storage.NewTestingLockManager()
-		lctx1 := lockManager.NewContext()
-		err := lctx1.AcquireLock(storage.LockInsertBlock)
-		require.NoError(t, err)
-		defer lctx1.Release()
-
-		err = db.WithReaderBatchWriter(func(rw storage.ReaderBatchWriter) error {
-			for _, guarantee := range set1 {
-				if err := operation.UnsafeInsertGuarantee(lctx1, rw.Writer(), guarantee.CollectionID, guarantee); err != nil {
+		unittest.WithLock(t, lockManager, storage.LockInsertBlock, func(lctx lockctx.Context) error {
+			return db.WithReaderBatchWriter(func(rw storage.ReaderBatchWriter) error {
+				for _, guarantee := range set1 {
+					if err := operation.UnsafeInsertGuarantee(lctx, rw.Writer(), guarantee.CollectionID, guarantee); err != nil {
+						return err
+					}
+				}
+				if err := operation.IndexPayloadGuarantees(lctx, rw.Writer(), blockID1, ids1); err != nil {
 					return err
 				}
-			}
-			if err := operation.IndexPayloadGuarantees(lctx1, rw.Writer(), blockID1, ids1); err != nil {
-				return err
-			}
-			return nil
+				return nil
+			})
 		})
-		require.NoError(t, err)
 
 		// insert block 2
-		lctx2 := lockManager.NewContext()
-		require.NoError(t, lctx2.AcquireLock(storage.LockInsertBlock))
-		err = db.WithReaderBatchWriter(func(rw storage.ReaderBatchWriter) error {
-			for _, guarantee := range set2 {
-				if err := operation.UnsafeInsertGuarantee(lctx2, rw.Writer(), guarantee.CollectionID, guarantee); err != nil {
+		unittest.WithLock(t, lockManager, storage.LockInsertBlock, func(lctx lockctx.Context) error {
+			return db.WithReaderBatchWriter(func(rw storage.ReaderBatchWriter) error {
+				for _, guarantee := range set2 {
+					if err := operation.UnsafeInsertGuarantee(lctx, rw.Writer(), guarantee.CollectionID, guarantee); err != nil {
+						return err
+					}
+				}
+				if err := operation.IndexPayloadGuarantees(lctx, rw.Writer(), blockID2, ids2); err != nil {
 					return err
 				}
-			}
-			if err := operation.IndexPayloadGuarantees(lctx2, rw.Writer(), blockID2, ids2); err != nil {
-				return err
-			}
-			return nil
+				return nil
+			})
 		})
-		require.NoError(t, err)
-		lctx2.Release()
 
 		t.Run("should retrieve collections for block", func(t *testing.T) {
 			var actual1 []flow.Identifier
-			err = operation.LookupPayloadGuarantees(db.Reader(), blockID1, &actual1)
+			err := operation.LookupPayloadGuarantees(db.Reader(), blockID1, &actual1)
 			assert.NoError(t, err)
 			assert.ElementsMatch(t, []flow.Identifier{collID1}, actual1)
 
```
