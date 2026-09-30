# [?] fix(blockstm): panic on unregistered store access (#26772)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cosmos/cosmos-sdk
Published: 2026-08-28
Source: https://github.com/cosmos/cosmos-sdk/commit/d76b62ebd8a8e81ea00c2925f35d60324b962db8
Type: security-commit

## Details
fix(blockstm): panic on unregistered store access (#26772)

Co-authored-by: Dmitry S <11892559+swift1337@users.noreply.github.com>

## Patch
### CHANGELOG.md
```diff
@@ -51,6 +51,7 @@ Ref: https://keepachangelog.com/en/1.0.0/
 
 ### Bug Fixes
 
+* (blockstm) [#26772](https://github.com/cosmos/cosmos-sdk/pull/26772) Panic with a descriptive error when accessing an unregistered store instead of silently using store index zero.
 * (x/genutil) [#26741](https://github.com/cosmos/cosmos-sdk/issues/26741) Preserve vote extension enable height when exporting genesis state.
 * (baseapp) [#26738](https://github.com/cosmos/cosmos-sdk/pull/26738) Return genesis transaction events in the first block's `FinalizeBlock` response so block indexers can observe them.
 
```

### internal/blockstm/mvmemory.go
```diff
@@ -2,6 +2,7 @@ package blockstm
 
 import (
 	"context"
+	"fmt"
 	"sync/atomic"
 
 	storetypes "github.com/cosmos/cosmos-sdk/store/v2/types"
@@ -104,7 +105,10 @@ func (mv *MVMemory) View(ctx context.Context, txn TxnIndex) *MultiMVMemoryView {
 }
 
 func (mv *MVMemory) newMVView(ctx context.Context, name storetypes.StoreKey, txn TxnIndex) MVView {
-	i := mv.stores[name]
+	i, ok := mv.stores[name]
+	if !ok {
+		panic(fmt.Sprintf("Block-STM accessed unregistered store %q", name.Name()))
+	}
 	return NewMVView(ctx, i, mv.storage[i], mv.GetMVStore(i), mv.scheduler, txn)
 }
 
```

### internal/blockstm/mvmemory_test.go
```diff
@@ -5,7 +5,7 @@ import (
 	"testing"
 	"time"
 
-	"github.com/test-go/testify/require"
+	"github.com/stretchr/testify/require"
 
 	storetypes "github.com/cosmos/cosmos-sdk/store/v2/types"
 )
@@ -148,6 +148,18 @@ func TestMVMemoryRecord(t *testing.T) {
 	}
 }
 
+func TestMVMemoryViewUnregisteredStore(t *testing.T) {
+	ctx := context.Background()
+	stores := map[storetypes.StoreKey]int{StoreKeyAuth: 0}
+	storage := NewMultiMemDB(stores)
+	mv := NewMVMemory(1, stores, MultiStoreToStorage(storage, stores), NewScheduler(1))
+
+	view := mv.View(ctx, 0)
+	require.PanicsWithValuef(t, `Block-STM accessed unregistered store "bank"`, func() {
+		view.GetKVStore(StoreKeyBank)
+	}, "accessing an unregistered store should panic")
+}
+
 func TestMVMemoryDelete(t *testing.T) {
 	ctx := context.Background()
 	nonceKey, balanceKey := []byte("nonce"), []byte("balance")
```
