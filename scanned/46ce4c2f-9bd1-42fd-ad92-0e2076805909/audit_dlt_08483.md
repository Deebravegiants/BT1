# [?] Add wait group to fix race condition

## Summary
Severity: Unknown
Chain: Sei
Component: sei-protocol/sei-chain
Published: 2024-06-25
Source: https://github.com/sei-protocol/sei-chain/commit/9efea3bcd6ab76ee83203ebe07bae9fe53f67b0e
Type: security-commit

## Details
Add wait group to fix race condition

## Patch
### sei-db/ss/pebbledb/db.go
```diff
@@ -44,8 +44,9 @@ var (
 )
 
 type Database struct {
-	storage *pebble.DB
-	config  config.StateStoreConfig
+	storage      *pebble.DB
+	asyncWriteWG sync.WaitGroup
+	config       config.StateStoreConfig
 	// Earliest version for db after pruning
 	earliestVersion int64
 
@@ -110,6 +111,7 @@ func New(dataDir string, config config.StateStoreConfig) (*Database, error) {
 	}
 	database := &Database{
 		storage:         db,
+		asyncWriteWG:    sync.WaitGroup{},
 		config:          config,
 		earliestVersion: earliestVersion,
 		pendingChanges:  make(chan VersionedChangesets, config.AsyncWriteBuffer),
@@ -126,7 +128,7 @@ func New(dataDir string, config config.StateStoreConfig) (*Database, error) {
 			},
 		)
 		database.streamHandler = streamHandler
-		go database.writeAsync()
+		go database.writeAsyncInBackground()
 	}
 	return database, nil
 }
@@ -138,13 +140,15 @@ func NewWithDB(storage *pebble.DB) *Database {
 }
 
 func (db *Database) Close() error {
-	err := db.storage.Close()
-	db.storage = nil
 	if db.streamHandler != nil {
 		db.streamHandler.Close()
 		db.streamHandler = nil
 		close(db.pendingChanges)
 	}
+	// Wait for the async writes to finish
+	db.asyncWriteWG.Wait()
+	err := db.storage.Close()
+	db.storage = nil
 	return err
 }
 
@@ -294,6 +298,7 @@ func (db *Database) ApplyChangesetAsync(version int64, changesets []*proto.Named
 			Version: version,
 		}
 		entry.Changesets = changesets
+		entry.Upgrades = nil
 		err := db.streamHandler.WriteNextEntry(entry)
 		if err != nil {
 			return err
@@ -307,17 +312,22 @@ func (db *Database) ApplyChangesetAsync(version int64, changesets []*proto.Named
 	return nil
 }
 
-func (db *Database) writeAsync() {
-	for db.streamHandler != nil {
-		for nextChange := range db.pendingChanges {
+func (db *Database) writeAsyncInBackground() {
+	db.asyncWriteWG.Add(1)
+	defer db.asyncWriteWG.Done()
+	for nextChange := range db.pendingChanges {
+		if db.streamHandler != nil {
 			version := nextChange.Version
 			for _, cs := range nextChange.Changesets {
-				db.ApplyChangeset(version, cs)
-
+				err := db.ApplyChangeset(version, cs)
+				if err != nil {
+					panic(err)
+				}
 			}
 			db.SetLatestVersion(version)
 		}
 	}
+
 }
 
 // Prune attempts to prune all versions up to and including the current version
```

### sei-db/ss/store_test.go
```diff
@@ -0,0 +1,58 @@
+package ss
+
+import (
+	"fmt"
+	"os"
+	"testing"
+
+	"github.com/cosmos/iavl"
+	"github.com/sei-protocol/sei-db/common/logger"
+	"github.com/sei-protocol/sei-db/config"
+	"github.com/sei-protocol/sei-db/proto"
+	"github.com/stretchr/testify/require"
+)
+
+func TestNewStateStore(t *testing.T) {
+	tempDir := os.TempDir()
+	ssConfig := config.StateStoreConfig{
+		DedicatedChangelog: true,
+		Backend:            string(PebbleDBBackend),
+		AsyncWriteBuffer:   10,
+		KeepRecent:         100,
+	}
+	stateStore, err := NewStateStore(logger.NewNopLogger(), tempDir, ssConfig)
+	require.NoError(t, err)
+	for i := 1; i < 10; i++ {
+		var changesets []*proto.NamedChangeSet
+		kvPair := &iavl.KVPair{
+			Delete: false,
+			Key:    []byte(fmt.Sprintf("key%d", i)),
+			Value:  []byte(fmt.Sprintf("value%d", i)),
+		}
+		var pairs []*iavl.KVPair
+		pairs = append(pairs, kvPair)
+		cs := iavl.ChangeSet{Pairs: pairs}
+		ncs := &proto.NamedChangeSet{
+			Name:      "storeA",
+			Changeset: cs,
+		}
+		changesets = append(changesets, ncs)
+		err := stateStore.ApplyChangesetAsync(int64(i), changesets)
+		require.NoError(t, err)
+	}
+	// Closing the state store without waiting for data to be fully flushed
+	err = stateStore.Close()
+	require.NoError(t, err)
+
+	// Reopen a new state store
+	stateStore, err = NewStateStore(logger.NewNopLogger(), tempDir, ssConfig)
+	require.NoError(t, err)
+
+	// Make sure key and values can be found
+	for i := 1; i < 10; i++ {
+		value, err := stateStore.Get("storeA", int64(i), []byte(fmt.Sprintf("key%d", i)))
+		require.NoError(t, err)
+		require.Equal(t, fmt.Sprintf("value%d", i), string(value))
+	}
+
+}
```

### sei-db/stream/changelog/changelog.go
```diff
@@ -57,11 +57,11 @@ func NewStream(logger logger.Logger, dir string, config Config) (*Stream, error)
 		isClosed: false,
 	}
 	// Finding the nextOffset to write
-	startIndex, err := log.FirstIndex()
+	lastIndex, err := log.LastIndex()
 	if err != nil {
 		return nil, err
 	}
-	stream.nextOffset = startIndex + 1
+	stream.nextOffset = lastIndex + 1
 	// Start the auto pruning goroutine
 	if config.KeepRecent > 0 {
 		go stream.StartPruning(config.KeepRecent, config.PruneInterval)
```
