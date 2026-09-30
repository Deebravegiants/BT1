# [?] fix: autobatch: remove potential deadlock when a block is missing

## Summary
Severity: Unknown
Chain: Filecoin
Component: filecoin-project/lotus
Published: 2022-11-07
Source: https://github.com/filecoin-project/lotus/commit/385f787ffc66efd6fc5b67e716daa0353144cfe1
Type: security-commit

## Details
fix: autobatch: remove potential deadlock when a block is missing

Check the _underlying_ blockstore instead of recursing. Also, drop the
lock before we do that.

## Patch
### blockstore/autobatch.go
```diff
@@ -181,18 +181,22 @@ func (bs *AutobatchBlockstore) Get(ctx context.Context, c cid.Cid) (block.Block,
 	}
 
 	bs.stateLock.Lock()
-	defer bs.stateLock.Unlock()
 	v, ok := bs.flushingBatch.blockMap[c]
 	if ok {
+		bs.stateLock.Unlock()
 		return v, nil
 	}
 
 	v, ok = bs.bufferedBatch.blockMap[c]
 	if ok {
+		bs.stateLock.Unlock()
 		return v, nil
 	}
+	bs.stateLock.Unlock()
 
-	return bs.Get(ctx, c)
+	// We have to check the backing store one more time because it may have been flushed by the
+	// time we were able to take the lock above.
+	return bs.backingBs.Get(ctx, c)
 }
 
 func (bs *AutobatchBlockstore) DeleteBlock(context.Context, cid.Cid) error {
```

### blockstore/autobatch_test.go
```diff
@@ -5,6 +5,8 @@ import (
 	"testing"
 
 	"github.com/stretchr/testify/require"
+
+	ipld "github.com/ipfs/go-ipld-format"
 )
 
 func TestAutobatchBlockstore(t *testing.T) {
@@ -29,6 +31,10 @@ func TestAutobatchBlockstore(t *testing.T) {
 	require.NoError(t, err)
 	require.Equal(t, b2.RawData(), v2.RawData())
 
+	// Regression test for a deadlock.
+	_, err = ab.Get(ctx, b3.Cid())
+	require.True(t, ipld.IsNotFound(err))
+
 	require.NoError(t, ab.Flush(ctx))
 	require.NoError(t, ab.Shutdown(ctx))
 }
```

### blockstore/union_test.go
```diff
@@ -13,6 +13,7 @@ var (
 	b0 = blocks.NewBlock([]byte("abc"))
 	b1 = blocks.NewBlock([]byte("foo"))
 	b2 = blocks.NewBlock([]byte("bar"))
+	b3 = blocks.NewBlock([]byte("baz"))
 )
 
 func TestUnionBlockstore_Get(t *testing.T) {
```
