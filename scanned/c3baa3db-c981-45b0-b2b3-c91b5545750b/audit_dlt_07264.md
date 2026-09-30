# [?] node: Wrap datastore with mutex to prevent data race (#325)

## Summary
Severity: Unknown
Chain: Celestia
Component: celestiaorg/celestia-node
Published: 2022-01-04
Source: https://github.com/celestiaorg/celestia-node/commit/1449792c6d3cee593c35a3b7f7697e4169b47a99
Type: security-commit

## Details
node: Wrap datastore with mutex to prevent data race (#325)

* node: update vanilla datastore with Mutex one

Co-authored-by: Wondertan <hlibwondertan@gmail.com>

* update Changelog

Co-authored-by: Wondertan <hlibwondertan@gmail.com>

## Patch
### CHANGELOG-PENDING.md
```diff
@@ -32,3 +32,4 @@ Month, DD, YYYY
 - [header] Added missing `err` value in ErrorW logging calls. @jbowen93
 - [service/block, node/p2p] [Fix race conditions in TestExtendedHeaderBroadcast and TestFull_P2P_Streams.](https://github.com/celestiaorg/celestia-node/pull/288) [@jenyasd209](https://github.com/jenyasd209)
 - [ci: increase tokens ratio for dupl to fix false positive scenarios](https://github.com/celestiaorg/celestia-node/pull/314) [@Bidon15](https://github.com/Bidon15)
+- [node: update vanilla datastore with Mutex one](https://github.com/celestiaorg/celestia-node/pull/325) [@Bidon15](https://github.com/Bidon15)
```

### node/store_mem.go
```diff
@@ -4,6 +4,7 @@ import (
 	"sync"
 
 	"github.com/ipfs/go-datastore"
+	ds_sync "github.com/ipfs/go-datastore/sync"
 
 	"github.com/celestiaorg/celestia-node/core"
 	"github.com/celestiaorg/celestia-node/libs/keystore"
@@ -22,7 +23,7 @@ type memStore struct {
 func NewMemStore() Store {
 	return &memStore{
 		keys: keystore.NewMapKeystore(),
-		data: datastore.NewMapDatastore(),
+		data: ds_sync.MutexWrap(datastore.NewMapDatastore()),
 		core: core.NewMemStore(),
 	}
 }
```
