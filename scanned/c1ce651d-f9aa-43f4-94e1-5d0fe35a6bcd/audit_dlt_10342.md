# [?] fix race condition in switchable

## Summary
Severity: Unknown
Chain: Sonic
Component: 0xsoniclabs/sonic
Published: 2022-11-29
Source: https://github.com/0xsoniclabs/sonic/commit/6b2cfe24a2b386b254f642a59ac82e001091e2c7
Type: security-commit

## Details
fix race condition in switchable

## Patch
### gossip/store.go
```diff
@@ -17,10 +17,10 @@ import (
 	"github.com/Fantom-foundation/go-opera/gossip/evmstore"
 	"github.com/Fantom-foundation/go-opera/logger"
 	"github.com/Fantom-foundation/go-opera/utils/adapters/snap2kvdb"
+	"github.com/Fantom-foundation/go-opera/utils/dbutil/switchable"
 	"github.com/Fantom-foundation/go-opera/utils/eventid"
 	"github.com/Fantom-foundation/go-opera/utils/randat"
 	"github.com/Fantom-foundation/go-opera/utils/rlpstore"
-	"github.com/Fantom-foundation/go-opera/utils/switchable"
 )
 
 // Store is a node persistent storage working over physical key-value database.
```

### utils/dbutil/switchable/snapshot.go
```diff
@@ -5,6 +5,8 @@ import (
 
 	"github.com/Fantom-foundation/lachesis-base/kvdb"
 	"github.com/ethereum/go-ethereum/common"
+
+	"github.com/Fantom-foundation/go-opera/utils/dbutil/itergc"
 )
 
 type Snapshot struct {
@@ -16,7 +18,7 @@ func (s *Snapshot) SwitchTo(snap kvdb.Snapshot) kvdb.Snapshot {
 	s.mu.Lock()
 	defer s.mu.Unlock()
 	old := s.Snapshot
-	s.Snapshot = snap
+	s.Snapshot = itergc.Wrap(snap, &sync.Mutex{})
 	return old
 }
 
@@ -97,8 +99,8 @@ func (it *switchableIterator) mayReopen() {
 // Next scans key-value pair by key in lexicographic order. Looks in cache first,
 // then - in DB.
 func (it *switchableIterator) Next() bool {
-	it.mu.RLock()
-	defer it.mu.RUnlock()
+	it.mu.Lock()
+	defer it.mu.Unlock()
 
 	it.mayReopen()
 
@@ -116,8 +118,8 @@ func (it *switchableIterator) Next() bool {
 // Error returns any accumulated error. Exhausting all the key/value pairs
 // is not considered to be an error. A memory iterator cannot encounter errors.
 func (it *switchableIterator) Error() error {
-	it.mu.RLock()
-	defer it.mu.RUnlock()
+	it.mu.Lock()
+	defer it.mu.Unlock()
 
 	it.mayReopen()
 
@@ -141,8 +143,8 @@ func (it *switchableIterator) Value() []byte {
 // Release releases associated resources. Release should always succeed and can
 // be called multiple times without causing error.
 func (it *switchableIterator) Release() {
-	it.mu.RLock()
-	defer it.mu.RUnlock()
+	it.mu.Lock()
+	defer it.mu.Unlock()
 
 	it.mayReopen()
 
```

### utils/dbutil/switchable/snapshot_test.go
```diff
@@ -11,6 +11,8 @@ import (
 	"github.com/Fantom-foundation/lachesis-base/kvdb"
 	"github.com/Fantom-foundation/lachesis-base/kvdb/memorydb"
 	"github.com/stretchr/testify/require"
+
+	"github.com/Fantom-foundation/go-opera/utils/dbutil/dbcounter"
 )
 
 func decodePair(b []byte) (uint32, uint32) {
@@ -62,7 +64,7 @@ func TestSnapshot_SwitchTo(t *testing.T) {
 	const duration = time.Millisecond * 400
 
 	// fill DB with data
-	memdb := memorydb.New()
+	memdb := dbcounter.WrapStore(memorydb.New(), "", false)
 	for i := uint32(0); i < prefixes; i++ {
 		for j := uint32(0); j < keys; j++ {
 			key := append(bigendian.Uint32ToBytes(i), bigendian.Uint32ToBytes(j)...)
@@ -145,4 +147,6 @@ func TestSnapshot_SwitchTo(t *testing.T) {
 	time.Sleep(duration)
 	atomic.StoreUint32(&stop, 1)
 	wg.Wait()
+	switchable.Release()
+	require.NoError(memdb.Close())
 }
```
