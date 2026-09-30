# [?] core/vm: Correct the Memory Gas Overflow condition

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2019-03-28
Source: https://github.com/celo-org/celo-blockchain/commit/157f09e5b64bd4ba8a579c4719cf504d68f4b925
Type: security-commit

## Details
core/vm: Correct the Memory Gas Overflow condition

previous overflow condition is too big to use.
0x7FFFFFFFF squre operation is overflowed uint64.

0x7FFFFFFFF^2 = 0x3F FFFF FFF0 0000 0001

## Patch
### core/vm/gas_table.go
```diff
@@ -32,11 +32,11 @@ func memoryGasCost(mem *Memory, newMemSize uint64) (uint64, error) {
 	// The maximum that will fit in a uint64 is max_word_count - 1
 	// anything above that will result in an overflow.
 	// Additionally, a newMemSize which results in a
-	// newMemSizeWords larger than 0x7ffffffff will cause the square operation
+	// newMemSizeWords larger than 0xFFFFFFFF will cause the square operation
 	// to overflow.
-	// The constant 0xffffffffe0 is the highest number that can be used without
+	// The constant 0x1FFFFFFFE0 is the highest number that can be used without
 	// overflowing the gas calculation
-	if newMemSize > 0xffffffffe0 {
+	if newMemSize > 0x1FFFFFFFE0 {
 		return 0, errGasUintOverflow
 	}
 
```
