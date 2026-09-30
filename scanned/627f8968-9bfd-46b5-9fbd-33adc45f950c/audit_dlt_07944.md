# [?] fix(sae): Executor deadlock with duplicate verifications (#5690)

## Summary
Severity: Unknown
Chain: Avalanche
Component: ava-labs/avalanchego
Published: 2026-07-21
Source: https://github.com/ava-labs/avalanchego/commit/a9f00e53e2884107db88d83eb30557070b64e28a
Type: security-commit

## Details
fix(sae): Executor deadlock with duplicate verifications (#5690)

## Patch
### vms/saevm/sae/consensus.go
```diff
@@ -5,6 +5,7 @@ package sae
 
 import (
 	"context"
+	"errors"
 	"fmt"
 
 	"github.com/ava-labs/libevm/core"
@@ -38,6 +39,8 @@ func (vm *VM) GetPreference() *blocks.Block {
 	return vm.preference.Load()
 }
 
+var errUnverifiedBlock = errors.New("block not verified")
+
 // AcceptBlock marks the block as [accepted], resulting in:
 //   - All blocks settled by this block having their [blocks.Block.MarkSettled]
 //     method called; and
@@ -49,6 +52,19 @@ func (vm *VM) AcceptBlock(ctx context.Context, b *blocks.Block) error {
 	// - (D)isk then (M)emory then (I)nternal then e(X)ternal.
 	// - B accepted after all of B.Settles() settled
 
+	// If b was verified multiple times, we may be asked to accept a different
+	// instance of b than the one stored in [VM.consensusCritical]. Since other
+	// blocks may have grabbed references to the instance in
+	// [VM.consensusCritical], we must ensure that we accept that instance, not
+	// the one passed in.
+	//
+	// TODO(StephenButtolph): Look into simplifying the VM API to avoid footguns
+	// around multiple instances of the same block.
+	b, ok := vm.consensusCritical.Load(b.Hash())
+	if !ok {
+		return errUnverifiedBlock
+	}
+
 	settles := b.Settles()
 	{
 		batch := vm.db.NewBatch()
```

### vms/saevm/sae/sae.go
```diff
@@ -42,10 +42,10 @@ type syncMap[K comparable, V any] struct {
 	onDelete func(V)
 }
 
-// newSyncMap creates a concurrent-safe map, which automatically performs
-// `onStore` and `onDelete` if [syncMap.Store] and [syncMap.Delete] are called,
-// respectively. If either function is nil, or the key to be deleted doesn't
-// exist, no operation will be performed.
+// newSyncMap creates a concurrent-safe map. onStore is called when
+// [syncMap.Store] adds a new key, and onDelete is called when [syncMap.Delete]
+// removes an existing key. Storing an existing key and deleting a missing key
+// are no-ops. A nil onStore or onDelete is treated as a no-op.
 func newSyncMap[K comparable, V any](onStore func(V), onDelete func(V)) *syncMap[K, V] {
 	if onStore == nil {
 		onStore = func(V) {}
@@ -63,23 +63,28 @@ func newSyncMap[K comparable, V any](onStore func(V), onDelete func(V)) *syncMap
 
 func (m *syncMap[K, V]) Load(k K) (V, bool) {
 	m.mu.RLock()
+	defer m.mu.RUnlock()
+
 	v, ok := m.m[k]
-	m.mu.RUnlock()
 	return v, ok
 }
 
 func (m *syncMap[K, V]) Store(k K, v V) {
-	m.onStore(v)
 	m.mu.Lock()
-	m.m[k] = v
-	m.mu.Unlock()
+	defer m.mu.Unlock()
+
+	if _, ok := m.m[k]; !ok {
+		m.onStore(v)
+		m.m[k] = v
+	}
 }
 
 func (m *syncMap[K, V]) Delete(k K) {
 	m.mu.Lock()
+	defer m.mu.Unlock()
+
 	if v, ok := m.m[k]; ok {
 		m.onDelete(v)
+		delete(m.m, k)
 	}
-	delete(m.m, k)
-	m.mu.Unlock()
 }
```

### vms/saevm/sae/vm_test.go
```diff
@@ -1185,3 +1185,62 @@ func TestSettledGasTime(t *testing.T) {
 		}
 	}
 }
+
+// TestDuplicateVerify verifies that having two in-memory instances of the same
+// block doesn't corrupt the VM, regardless of which is accepted.
+func TestDuplicateVerify(t *testing.T) {
+	tests := []struct {
+		name        string
+		acceptIndex int
+	}{
+		{
+			name:        "accept_first",
+			acceptIndex: 0,
+		},
+		{
+			name:        "accept_second",
+			acceptIndex: 1,
+		},
+	}
+	for _, test := range tests {
+		t.Run(test.name, func(t *testing.T) {
+			ctx, sut := newSUT(t, 0)
+
+			first := sut.buildAndParseBlock(t, sut.lastAcceptedBlock(t))
+			second, err := sut.ParseBlock(ctx, first.Bytes())
+			require.NoError(t, err, "%T.ParseBlock(BuildBlock().Bytes())", sut.ChainVM)
+			blks := []snowman.Block{first, second}
+
+			// Consensus may call [block.WithVerifyContext.VerifyWithContext] on
+			// multiple instances of the same block. [VM.consensusCritical]
+			// isn't overridden, so the first instance verified is the one kept
+			// in the map.
+			for _, blk := range blks {
+				b := blk.(block.WithVerifyContext)
+				require.NoErrorf(t,
+					b.VerifyWithContext(ctx, &block.Context{}),
+					"%T.VerifyWithContext()",
+					blk,
+				)
+			}
+
+			parent := blks[test.acceptIndex]
+			require.NoErrorf(t, sut.SetPreference(ctx, parent.ID()), "%T.SetPreference([duplicated block's ID])", sut.ChainVM)
+			child, err := sut.BuildBlock(ctx)
+			require.NoErrorf(t, err, "%T.BuildBlock() with duplicated block as preference", sut.ChainVM)
+			// Loads the parent from [VM.consensusCritical].
+			require.NoErrorf(t, child.Verify(ctx), "%T.Verify() child of duplicated block", child)
+
+			// Accepting parent and child adds them to the execution queue.
+			require.NoError(t, parent.Accept(ctx), "parent.Accept()")
+			require.NoError(t, child.Accept(ctx), "child.Accept()")
+
+			// Inside the executor, execution results are read from
+			// [blocks.Block.ParentBlock]. When the ancestry differs from the
+			// accepted instance, a naive implementation would block child's
+			// execution forever.
+			childRaw := unwrap(t, child)
+			require.NoErrorf(t, childRaw.WaitUntilExecuted(ctx), "%T.WaitUntilExecuted()", childRaw)
+		})
+	}
+}
```
