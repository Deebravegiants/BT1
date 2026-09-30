# [?] core/vm: fix overflow in gas calculation formula

## Summary
Severity: Unknown
Chain: Scroll
Component: scroll-tech/go-ethereum
Published: 2017-06-28
Source: https://github.com/scroll-tech/go-ethereum/commit/bae7565231376bbd23474e2e91c99a21542ef47a
Type: security-commit

## Details
core/vm: fix overflow in gas calculation formula

## Patch
### core/vm/gas_table.go
```diff
@@ -17,7 +17,6 @@
 package vm
 
 import (
-	gmath "math"
 	"math/big"
 
 	"github.com/ethereum/go-ethereum/common"
@@ -28,15 +27,20 @@ import (
 // memoryGasCosts calculates the quadratic gas for memory expansion. It does so
 // only for the memory region that is expanded, not the total memory.
 func memoryGasCost(mem *Memory, newMemSize uint64) (uint64, error) {
-	// The maximum that will fit in a uint64 is max_word_count - 1
-	// anything above that will result in an overflow.
-	if newMemSize > gmath.MaxUint64-32 {
-		return 0, errGasUintOverflow
-	}
 
 	if newMemSize == 0 {
 		return 0, nil
 	}
+	// The maximum that will fit in a uint64 is max_word_count - 1
+	// anything above that will result in an overflow.
+	// Additionally, a newMemSize which results in a
+	// newMemSizeWords larger than 0x7ffffffff will cause the square operation
+	// to overflow.
+	// The constant 0xffffffffe0 is the highest number that can be used without
+	// overflowing the gas calculation
+	if newMemSize > 0xffffffffe0 {
+		return 0, errGasUintOverflow
+	}
 
 	newMemSizeWords := toWordSize(newMemSize)
 	newMemSize = newMemSizeWords * 32
```
