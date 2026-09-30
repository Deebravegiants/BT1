# [?] Fix MerkleDB crash recovery (#2913)

## Summary
Severity: Unknown
Chain: Avalanche
Component: ava-labs/avalanchego
Published: 2024-04-04
Source: https://github.com/ava-labs/avalanchego/commit/cca7419b8745bbee1032aa137229c859bfbbcad6
Type: security-commit

## Details
Fix MerkleDB crash recovery (#2913)

## Patch
### x/merkledb/db.go
```diff
@@ -44,6 +44,19 @@ var (
 	valueNodePrefix        = []byte{1}
 	intermediateNodePrefix = []byte{2}
 
+	// cleanShutdownKey is used to flag that the database did (or did not)
+	// previously shutdown correctly.
+	//
+	// If this key has value [hadCleanShutdown] it must be true that all
+	// intermediate nodes of the trie are correctly populated on disk and that
+	// the [rootDBKey] has the correct key for the root node.
+	//
+	// If this key has value [didNotHaveCleanShutdown] the intermediate nodes of
+	// the trie may not be correct and the [rootDBKey] may not exist or point to
+	// a node that node longer exists.
+	//
+	// Regardless of the value of [cleanShutdownKey], the value nodes must
+	// always be persisted correctly.
 	cleanShutdownKey        = []byte(string(metadataPrefix) + "cleanShutdown")
 	rootDBKey               = []byte(string(metadataPrefix) + "root")
 	hadCleanShutdown        = []byte{1}
@@ -278,9 +291,25 @@ func newDatabase(
 		tokenSize:        BranchFactorToTokenSize[config.BranchFactor],
 	}
 
-	if err := trieDB.initializeRoot(); err != nil {
+	shutdownType, err := trieDB.baseDB.Get(cleanShutdownKey)
+	switch err {
+	case nil:
+	case database.ErrNotFound:
+		// If the marker wasn't found then the DB is being created for the first
+		// time and there is nothing to do.
+		shutdownType = hadCleanShutdown
+	default:
 		return nil, err
 	}
+	if bytes.Equal(shutdownType, didNotHaveCleanShutdown) {
+		if err := trieDB.rebuild(ctx, int(config.ValueNodeCacheSize)); err != nil {
+			return nil, err
+		}
+	} else {
+		if err := trieDB.initializeRoot(); err != nil {
+			return nil, err
+		}
+	}
 
 	// add current root to history (has no changes)
 	trieDB.history.record(&changeSummary{
@@ -292,21 +321,6 @@ func newDatabase(
 		nodes:  map[Key]*change[*node]{},
 	})
 
-	shutdownType, err := trieDB.baseDB.Get(cleanShutdownKey)
-	switch err {
-	case nil:
-		if bytes.Equal(shutdownType, didNotHaveCleanShutdown) {
-			if err := trieDB.rebuild(ctx, int(config.ValueNodeCacheSize)); err != nil {
-				return nil, err
-			}
-		}
-	case database.ErrNotFound:
-		// If the marker wasn't found then the DB is being created for the first
-		// time and there is nothing to do.
-	default:
-		return nil, err
-	}
-
 	// mark that the db has not yet been cleanly closed
 	err = trieDB.baseDB.Put(cleanShutdownKey, didNotHaveCleanShutdown)
 	return trieDB, err
@@ -460,8 +474,26 @@ func (db *merkleDB) Close() error {
 		return err
 	}
 
-	// Successfully wrote intermediate nodes.
-	return db.baseDB.Put(cleanShutdownKey, hadCleanShutdown)
+	var (
+		batch = db.baseDB.NewBatch()
+		err   error
+	)
+	// Write the root key
+	if db.root.IsNothing() {
+		err = batch.Delete(rootDBKey)
+	} else {
+		rootKey := encodeKey(db.root.Value().key)
+		err = batch.Put(rootDBKey, rootKey)
+	}
+	if err != nil {
+		return err
+	}
+
+	// Write the clean shutdown marker
+	if err := batch.Put(cleanShutdownKey, hadCleanShutdown); err != nil {
+		return err
+	}
+	return batch.Write()
 }
 
 func (db *merkleDB) PrefetchPaths(keys [][]byte) error {
@@ -978,13 +1010,7 @@ func (db *merkleDB) commitChanges(ctx context.Context, trieToCommit *view) error
 	// Update root in database.
 	db.root = changes.rootChange.after
 	db.rootID = changes.rootID
-
-	if db.root.IsNothing() {
-		return db.baseDB.Delete(rootDBKey)
-	}
-
-	rootKey := encodeKey(db.root.Value().key)
-	return db.baseDB.Put(rootDBKey, rootKey)
+	return nil
 }
 
 // moveChildViewsToDB removes any child views from the trieToCommit and moves them to the db
@@ -1166,12 +1192,11 @@ func (db *merkleDB) invalidateChildrenExcept(exception *view) {
 // Otherwise leave [db.root] as Nothing.
 func (db *merkleDB) initializeRoot() error {
 	rootKeyBytes, err := db.baseDB.Get(rootDBKey)
+	if errors.Is(err, database.ErrNotFound) {
+		return nil // Root isn't on disk.
+	}
 	if err != nil {
-		if !errors.Is(err, database.ErrNotFound) {
-			return err
-		}
-		// Root isn't on disk.
-		return nil
+		return err
 	}
 
 	// Root is on disk.
@@ -1181,8 +1206,7 @@ func (db *merkleDB) initializeRoot() error {
 	}
 
 	// First, see if root is an intermediate node.
-	var root *node
-	root, err = db.getEditableNode(rootKey, false /* hasValue */)
+	root, err := db.getEditableNode(rootKey, false /* hasValue */)
 	if err != nil {
 		if !errors.Is(err, database.ErrNotFound) {
 			return err
```

### x/merkledb/db_test.go
```diff
@@ -1287,3 +1287,46 @@ func TestGetChangeProofEmptyRootID(t *testing.T) {
 	)
 	require.ErrorIs(err, ErrEmptyProof)
 }
+
+func TestCrashRecovery(t *testing.T) {
+	require := require.New(t)
+
+	baseDB := memdb.New()
+	merkleDB, err := newDatabase(
+		context.Background(),
+		baseDB,
+		newDefaultConfig(),
+		&mockMetrics{},
+	)
+	require.NoError(err)
+
+	merkleDBBatch := merkleDB.NewBatch()
+	require.NoError(merkleDBBatch.Put([]byte("is this"), []byte("hope")))
+	require.NoError(merkleDBBatch.Put([]byte("expected?"), []byte("so")))
+	require.NoError(merkleDBBatch.Write())
+
+	expectedRoot, err := merkleDB.GetMerkleRoot(context.Background())
+	require.NoError(err)
+
+	// Do not `.Close()` the database to simulate a process crash.
+
+	newMerkleDB, err := newDatabase(
+		context.Background(),
+		baseDB,
+		newDefaultConfig(),
+		&mockMetrics{},
+	)
+	require.NoError(err)
+
+	value, err := newMerkleDB.Get([]byte("is this"))
+	require.NoError(err)
+	require.Equal([]byte("hope"), value)
+
+	value, err = newMerkleDB.Get([]byte("expected?"))
+	require.NoError(err)
+	require.Equal([]byte("so"), value)
+
+	rootAfterRecovery, err := newMerkleDB.GetMerkleRoot(context.Background())
+	require.NoError(err)
+	require.Equal(expectedRoot, rootAfterRecovery)
+}
```
