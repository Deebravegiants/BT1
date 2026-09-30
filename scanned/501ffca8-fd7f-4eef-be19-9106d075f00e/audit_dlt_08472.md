# [?] Fix mutable tree race condition

## Summary
Severity: Unknown
Chain: Sei
Component: sei-protocol/sei-chain
Published: 2023-03-10
Source: https://github.com/sei-protocol/sei-chain/commit/f3586f9502478f5052b3e92eae9c21c5b5d05f6a
Type: security-commit

## Details
Fix mutable tree race condition

## Patch
### sei-iavl/immutable_tree.go
```diff
@@ -3,7 +3,6 @@ package iavl
 import (
 	"fmt"
 	"strings"
-	"sync"
 
 	dbm "github.com/tendermint/tm-db"
 )
@@ -19,7 +18,6 @@ type ImmutableTree struct {
 	ndb                    *nodeDB
 	version                int64
 	skipFastStorageUpgrade bool
-	mtx                    *sync.Mutex
 }
 
 // NewImmutableTree creates both in-memory and persistent instances
@@ -32,7 +30,6 @@ func NewImmutableTree(db dbm.DB, cacheSize int, skipFastStorageUpgrade bool) *Im
 		// NodeDB-backed Tree.
 		ndb:                    newNodeDB(db, cacheSize, nil),
 		skipFastStorageUpgrade: skipFastStorageUpgrade,
-		mtx:                    &sync.Mutex{},
 	}
 }
 
@@ -42,7 +39,6 @@ func NewImmutableTreeWithOpts(db dbm.DB, cacheSize int, opts *Options, skipFastS
 		// NodeDB-backed Tree.
 		ndb:                    newNodeDB(db, cacheSize, opts),
 		skipFastStorageUpgrade: skipFastStorageUpgrade,
-		mtx:                    &sync.Mutex{},
 	}
 }
 
@@ -322,7 +318,6 @@ func (t *ImmutableTree) clone() *ImmutableTree {
 		ndb:                    t.ndb,
 		version:                t.version,
 		skipFastStorageUpgrade: t.skipFastStorageUpgrade,
-		mtx:                    t.mtx,
 	}
 }
 
```

### sei-iavl/mutable_tree.go
```diff
@@ -37,6 +37,7 @@ type MutableTree struct {
 	unsavedFastNodeRemovals  map[string]interface{} // FastNodes that have not yet been removed from disk
 	ndb                      *nodeDB
 	skipFastStorageUpgrade   bool // If true, the tree will work like no fast storage and always not upgrade fast storage
+	mtx                      *sync.Mutex
 }
 
 // NewMutableTree returns a new tree with the specified cache size and datastore.
@@ -47,7 +48,7 @@ func NewMutableTree(db dbm.DB, cacheSize int, skipFastStorageUpgrade bool) (*Mut
 // NewMutableTreeWithOpts returns a new tree with the specified options.
 func NewMutableTreeWithOpts(db dbm.DB, cacheSize int, opts *Options, skipFastStorageUpgrade bool) (*MutableTree, error) {
 	ndb := newNodeDB(db, cacheSize, opts)
-	head := &ImmutableTree{ndb: ndb, skipFastStorageUpgrade: skipFastStorageUpgrade, mtx: &sync.Mutex{}}
+	head := &ImmutableTree{ndb: ndb, skipFastStorageUpgrade: skipFastStorageUpgrade}
 
 	return &MutableTree{
 		ImmutableTree:            head,
@@ -59,6 +60,7 @@ func NewMutableTreeWithOpts(db dbm.DB, cacheSize int, opts *Options, skipFastSto
 		unsavedFastNodeRemovals:  make(map[string]interface{}),
 		ndb:                      ndb,
 		skipFastStorageUpgrade:   skipFastStorageUpgrade,
+		mtx:                      &sync.Mutex{},
 	}, nil
 }
 
@@ -532,7 +534,6 @@ func (tree *MutableTree) LazyLoadVersion(targetVersion int64) (toReturn int64, t
 		ndb:                    tree.ndb,
 		version:                targetVersion,
 		skipFastStorageUpgrade: tree.skipFastStorageUpgrade,
-		mtx:                    tree.mtx,
 	}
 	if len(rootHash) > 0 {
 		// If rootHash is empty then root of tree should be nil
@@ -609,7 +610,6 @@ func (tree *MutableTree) LoadVersion(targetVersion int64) (toReturn int64, toErr
 		ndb:                    tree.ndb,
 		version:                latestVersion,
 		skipFastStorageUpgrade: tree.skipFastStorageUpgrade,
-		mtx:                    tree.mtx,
 	}
 
 	if len(latestRoot) != 0 {
@@ -761,7 +761,6 @@ func (tree *MutableTree) GetImmutable(version int64) (*ImmutableTree, error) {
 			ndb:                    tree.ndb,
 			version:                version,
 			skipFastStorageUpgrade: tree.skipFastStorageUpgrade,
-			mtx:                    tree.mtx,
 		}, nil
 	}
 	tree.versions[version] = true
@@ -775,7 +774,6 @@ func (tree *MutableTree) GetImmutable(version int64) (*ImmutableTree, error) {
 		ndb:                    tree.ndb,
 		version:                version,
 		skipFastStorageUpgrade: tree.skipFastStorageUpgrade,
-		mtx:                    tree.mtx,
 	}, nil
 }
 
@@ -789,7 +787,6 @@ func (tree *MutableTree) Rollback() {
 			ndb:                    tree.ndb,
 			version:                0,
 			skipFastStorageUpgrade: tree.skipFastStorageUpgrade,
-			mtx:                    tree.mtx,
 		}
 	}
 	tree.orphans = map[string]int64{}
```
