# [?] fix(engine-primitives): Potential nil panic detected (#1598)

## Summary
Severity: Unknown
Chain: Berachain
Component: berachain/beacon-kit
Published: 2024-06-25
Source: https://github.com/berachain/beacon-kit/commit/4cb4a8b8c8bf005f1f78c413a37bff10531d3cc0
Type: security-commit

## Details
fix(engine-primitives): Potential nil panic detected (#1598)

## Patch
### mod/engine-primitives/pkg/engine-primitives/transactions.go
```diff
@@ -23,6 +23,7 @@ package engineprimitives
 import (
 	"sync"
 
+	"github.com/berachain/beacon-kit/mod/errors"
 	"github.com/berachain/beacon-kit/mod/primitives/pkg/common"
 	"github.com/berachain/beacon-kit/mod/primitives/pkg/constants"
 	"github.com/berachain/beacon-kit/mod/primitives/pkg/math"
@@ -50,10 +51,16 @@ var byteBufferPool = sync.Pool{
 func getBytes(size int) *byteBuffer {
 	//nolint:errcheck // its okay.
 	b := byteBufferPool.Get().(*byteBuffer)
-	if cap(b.Bytes) < size {
-		b.Bytes = make([]common.Root, size)
+	if b == nil {
+		b = &byteBuffer{
+			Bytes: make([]common.Root, size),
+		}
+	} else {
+		if b.Bytes == nil || cap(b.Bytes) < size {
+			b.Bytes = make([]common.Root, size)
+		}
+		b.Bytes = b.Bytes[:size]
 	}
-	b.Bytes = b.Bytes[:size]
 	return b
 }
 
@@ -71,6 +78,12 @@ func (txs Transactions) HashTreeRoot() (common.Root, error) {
 	var err error
 	roots := getBytes(len(txs))
 	defer byteBufferPool.Put(roots)
+
+	// Ensure roots.Bytes is not nil
+	if roots.Bytes == nil {
+		return common.Root{}, errors.New("failed to allocate byte buffer")
+	}
+
 	for i, tx := range txs {
 		roots.Bytes[i], err = ssz.MerkleizeByteSlice[math.U64, common.Root](tx)
 		if err != nil {
```
