# [?] Prevent bytesNeeded overflow (#2130)

## Summary
Severity: Unknown
Chain: Avalanche
Component: ava-labs/avalanchego
Published: 2023-10-03
Source: https://github.com/ava-labs/avalanchego/commit/257c0709787c53def71660c0be175a30a9752dbc
Type: security-commit

## Details
Prevent bytesNeeded overflow (#2130)

## Patch
### x/merkledb/codec_test.go
```diff
@@ -5,7 +5,9 @@ package merkledb
 
 import (
 	"bytes"
+	"encoding/binary"
 	"io"
+	"math"
 	"math/rand"
 	"testing"
 
@@ -261,3 +263,10 @@ func FuzzEncodeHashValues(f *testing.F) {
 		},
 	)
 }
+
+func TestCodecDecodePathLengthOverflowRegression(t *testing.T) {
+	codec := codec.(*codecImpl)
+	bytes := bytes.NewReader(binary.AppendUvarint(nil, math.MaxInt))
+	_, err := codec.decodePath(bytes, BranchFactor16)
+	require.ErrorIs(t, err, io.ErrUnexpectedEOF)
+}
```

### x/merkledb/path.go
```diff
@@ -203,10 +203,17 @@ func (p Path) bitsToShift(index int) byte {
 	return 7 - endBitIndex
 }
 
-// bytesNeeded returns the number of bytes needed to store the passed number of tokens
+// bytesNeeded returns the number of bytes needed to store the passed number of
+// tokens.
+//
+// Invariant: [tokens] is a non-negative, but otherwise untrusted, input and
+// this method must never overflow.
 func (p Path) bytesNeeded(tokens int) int {
-	// adding p.tokensPerByte - 1 causes the division to always round up
-	return (tokens + p.tokensPerByte - 1) / p.tokensPerByte
+	size := tokens / p.tokensPerByte
+	if tokens%p.tokensPerByte != 0 {
+		size++
+	}
+	return size
 }
 
 // Extend returns a new Path that equals the passed Path appended to the current Path
```
