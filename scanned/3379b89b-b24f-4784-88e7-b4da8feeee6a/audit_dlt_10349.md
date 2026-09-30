# [?] don't update Snaps field after start to prevent a race condition

## Summary
Severity: Unknown
Chain: Sonic
Component: 0xsoniclabs/sonic
Published: 2021-12-23
Source: https://github.com/0xsoniclabs/sonic/commit/01019ec487edb252b91f6c5bdd12af8998c1b246
Type: security-commit

## Details
don't update Snaps field after start to prevent a race condition

## Patch
### cmd/opera/launcher/snapshotcmd.go
```diff
@@ -204,7 +204,7 @@ func verifyState(ctx *cli.Context) error {
 	evmStore := gdb.EvmStore()
 	root := common.Hash(gdb.GetBlockState().FinalizedStateRoot)
 
-	err = evmStore.CreateEvmSnapshot(root, false, false)
+	err = evmStore.GenerateEvmSnapshot(root, false, false)
 	if err != nil {
 		log.Error("Failed to open snapshot tree", "err", err)
 		return err
```

### gossip/c_event_callbacks.go
```diff
@@ -147,11 +147,8 @@ func (s *Service) SwitchEpochTo(newEpoch idx.Epoch) error {
 	if newEpoch == s.store.GetEpoch() {
 		return errSameEpoch
 	}
-	err := s.store.GenerateSnapshotAt(common.Hash(bs.FinalizedStateRoot), true)
-	if err != nil {
-		return err
-	}
-	err = s.engine.Reset(newEpoch, es.Validators)
+	s.store.evm.RebuildEvmSnapshot(common.Hash(bs.FinalizedStateRoot))
+	err := s.engine.Reset(newEpoch, es.Validators)
 	if err != nil {
 		return err
 	}
```

### gossip/evmstore/store.go
```diff
@@ -1,6 +1,7 @@
 package evmstore
 
 import (
+	"errors"
 	"sync"
 
 	"github.com/Fantom-foundation/lachesis-base/hash"
@@ -103,7 +104,10 @@ func (s *Store) initCache() {
 	s.cache.EvmBlocks = s.makeCache(s.cfg.Cache.EvmBlocksSize, s.cfg.Cache.EvmBlocksNum)
 }
 
-func (s *Store) CreateEvmSnapshot(root common.Hash, rebuild, async bool) (err error) {
+func (s *Store) GenerateEvmSnapshot(root common.Hash, rebuild, async bool) (err error) {
+	if s.Snaps != nil {
+		return errors.New("EVM snapshot is already opened")
+	}
 	s.Snaps, err = snapshot.New(
 		s.EvmDb,
 		s.EvmState.TrieDB(),
@@ -119,7 +123,6 @@ func (s *Store) RebuildEvmSnapshot(root common.Hash) {
 	if s.Snaps == nil {
 		return
 	}
-
 	s.Snaps.Rebuild(root)
 }
 
```

### gossip/store.go
```diff
@@ -194,7 +194,7 @@ func (s *Store) GenerateSnapshotAt(root common.Hash, async bool) (err error) {
 }
 
 func (s *Store) generateSnapshotAt(evmStore *evmstore.Store, root common.Hash, rebuild, async bool) (err error) {
-	return evmStore.CreateEvmSnapshot(root, rebuild, async)
+	return evmStore.GenerateEvmSnapshot(root, rebuild, async)
 }
 
 // Commit changes.
```
