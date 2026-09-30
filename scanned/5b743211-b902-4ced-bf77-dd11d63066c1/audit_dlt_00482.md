# [?] triedb/pathdb: fix 32-bit integer overflow in history trienode decoder (#33098)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2025-11-07
Source: https://github.com/ethereum/go-ethereum/commit/d2a5dba48f31031e8f9b1b4942a1e29e54d97079
Type: security-commit

## Details
triedb/pathdb: fix 32-bit integer overflow in history trienode decoder (#33098)

failed in 32bit:

```
--- FAIL: TestDecodeSingleCorruptedData (0.00s)
panic: runtime error: slice bounds out of range [:-1501805520] [recovered, repanicked]

goroutine 38872 [running]:
testing.tRunner.func1.2({0x838db20, 0xa355620})
	/opt/actions-runner/_work/_tool/go/1.25.3/x64/src/testing/testing.go:1872 +0x29b
testing.tRunner.func1()
	/opt/actions-runner/_work/_tool/go/1.25.3/x64/src/testing/testing.go:1875 +0x414
panic({0x838db20, 0xa355620})
	/opt/actions-runner/_work/_tool/go/1.25.3/x64/src/runtime/panic.go:783 +0x103
github.com/ethereum/go-ethereum/triedb/pathdb.decodeSingle({0x9e57500, 0x1432, 0x1432}, 0x0)
	/opt/actions-runner/_work/go-ethereum/go-ethereum/triedb/pathdb/history_trienode.go:399 +0x18d6
github.com/ethereum/go-ethereum/triedb/pathdb.TestDecodeSingleCorruptedData(0xa2db9e8)
	/opt/actions-runner/_work/go-ethereum/go-ethereum/triedb/pathdb/history_trienode_test.go:698 +0x180
testing.tRunner(0xa2db9e8, 0x83c86e8)
	/opt/actions-runner/_work/_tool/go/1.25.3/x64/src/testing/testing.go:1934 +0x114
created by testing.(*T).Run in goroutine 1
	/opt/actions-runner/_work/_tool/go/1.25.3/x64/src/testing/testing.go:1997 +0x4b4
FAIL	github.com/ethereum/go-ethereum/triedb/pathdb	41.453s
?   	github.com/ethereum/go-ethereum/version	[no test files]
FAIL
```

Found in
https://github.com/ethereum/go-ethereum/actions/runs/18912701345/job/53990136071?pr=33052

## Patch
### triedb/pathdb/history_trienode.go
```diff
@@ -19,9 +19,11 @@ package pathdb
 import (
 	"bytes"
 	"encoding/binary"
+	"errors"
 	"fmt"
 	"iter"
 	"maps"
+	"math"
 	"slices"
 	"sort"
 	"time"
@@ -386,12 +388,26 @@ func decodeSingle(keySection []byte, onValue func([]byte, int, int) error) ([]st
 		}
 		// Resolve the entry from key section
 		nShared, nn := binary.Uvarint(keySection[keyOff:]) // key length shared (varint)
+		if nn <= 0 {
+			return nil, fmt.Errorf("corrupted varint encoding for nShared at offset %d", keyOff)
+		}
 		keyOff += nn
 		nUnshared, nn := binary.Uvarint(keySection[keyOff:]) // key length not shared (varint)
+		if nn <= 0 {
+			return nil, fmt.Errorf("corrupted varint encoding for nUnshared at offset %d", keyOff)
+		}
 		keyOff += nn
 		nValue, nn := binary.Uvarint(keySection[keyOff:]) // value length (varint)
+		if nn <= 0 {
+			return nil, fmt.Errorf("corrupted varint encoding for nValue at offset %d", keyOff)
+		}
 		keyOff += nn
 
+		// Validate that the values can fit in an int to prevent overflow on 32-bit systems
+		if nShared > uint64(math.MaxUint32) || nUnshared > uint64(math.MaxUint32) || nValue > uint64(math.MaxUint32) {
+			return nil, errors.New("key size too large")
+		}
+
 		// Resolve unshared key
 		if keyOff+int(nUnshared) > len(keySection) {
 			return nil, fmt.Errorf("key length too long, unshared key length: %d, off: %d, section size: %d", nUnshared, keyOff, len(keySection))
```

### triedb/pathdb/history_trienode_test.go
```diff
@@ -694,7 +694,10 @@ func TestDecodeSingleCorruptedData(t *testing.T) {
 	// Test with corrupted varint in key section
 	corrupted := make([]byte, len(keySection))
 	copy(corrupted, keySection)
-	corrupted[5] = 0xFF // Corrupt varint
+	// Fill first 10 bytes with 0xFF to create a varint overflow (>64 bits)
+	for i := range 10 {
+		corrupted[i] = 0xFF
+	}
 	_, err = decodeSingle(corrupted, nil)
 	if err == nil {
 		t.Fatal("Expected error for corrupted varint")
```
