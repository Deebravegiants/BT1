# [?] [Tolk] Fix overflow detection on constant storeUint

## Summary
Severity: Unknown
Chain: TON
Component: ton-blockchain/ton
Published: 2025-08-18
Source: https://github.com/ton-blockchain/ton/commit/6e9ce41baaebad1b1d441372a0a302125d442a21
Type: security-commit

## Details
[Tolk] Fix overflow detection on constant storeUint

## Patch
### tolk-tester/tests/cells-slices.tolk
```diff
@@ -16,6 +16,16 @@ fun endCell(b: builder): cell
 fun beginParse(c: cell): slice
     asm "CTOS";
 
+@noinline
+fun triggerOverflowIntConst() {
+    return beginCell().storeInt(10, 4)
+}
+
+@noinline
+fun triggerOverflowUintConst() {
+    return beginCell().storeUint(123, 6)
+}
+
 @method_id(101)
 fun test1(): [int,int,int,int,int] {
     var b: builder = beginCell().storeUint(1, 32);
@@ -435,6 +445,30 @@ fun test34(p: int, n: int) {
     return b;
 }
 
+@method_id(135)
+fun test35(overflowMode: int) {
+    try {
+        val b: builder = match (overflowMode) {
+            1 => triggerOverflowIntConst(), 
+            2 => triggerOverflowUintConst(),
+            3 => beginCell().storeUint(10, -4),
+            4 => beginCell().storeInt(100, 1),
+            5 => beginCell().storeInt(1, 0),
+            6 => beginCell().storeInt(115792089237316195423570985008687907853269984665640564039457584007913129639935, 256),
+            7 => beginCell().storeInt(15, 4),
+            8 => beginCell().storeUint(1<<170, 169),
+            else => beginCell(),
+        };
+        return b.endCell().beginParse().loadUint(1) * 1000
+    }
+    catch (ex) { return ex }
+}
+
+@method_id(136)
+fun test36() {
+    return beginCell().storeInt(0, 0)
+}
+
 fun main(): int {
     return 0;
 }
@@ -469,6 +503,15 @@ fun main(): int {
 @testcase | 132 | 0   | BC{00080000000a}
 @testcase | 133 | 0   | BC{00020a}
 @testcase | 134 | 0 8 | BC{00020a}
+@testcase | 135 | 1   | 5
+@testcase | 135 | 2   | 5
+@testcase | 135 | 3   | 5
+@testcase | 135 | 4   | 5
+@testcase | 135 | 5   | 5
+@testcase | 135 | 6   | 5
+@testcase | 135 | 7   | 5
+@testcase | 135 | 8   | 5
+@testcase | 136 |     | BC{0000}
 
 We test that consequtive storeInt/storeUint with constants are joined into a single number
 
@@ -630,4 +673,32 @@ We test that consequtive storeInt/storeUint with constants are joined into a sin
   }>
 """
 
+@fif_codegen
+"""
+  triggerOverflowIntConst() PROC:<{ 
+    10 PUSHINT
+    NEWC
+    4 STI
+  }>
+"""
+
+@fif_codegen
+"""
+  triggerOverflowUintConst() PROC:<{ 
+    123 PUSHINT
+    NEWC
+    6 STU
+  }>
+"""
+
+@fif_codegen
+"""
+  test36() PROC:<{ 
+    0 PUSHINT
+    NEWC
+    OVER
+    STIX
+  }>
+"""
+
  */
```

### tolk-tester/tests/pack-unpack-1.tolk
```diff
@@ -7,6 +7,11 @@ struct Point {
     y: int32;
 }
 
+struct TwoU {
+    a: uint8
+    b: uint8
+}
+
 @method_id(101)
 fun test1(value: int) {
     var t: JustInt32 = { value };
@@ -84,6 +89,15 @@ fun test7(s: slice) {
     return (6, s.remainingBitsCount());
 }
 
+@method_id(108)
+fun test8(): cell | int {
+    try {
+        return TwoU{a:1<<10, b:0}.toCell()
+    } catch (ex) {
+        return ex
+    }
+}
+
 fun main(c: cell) {
     c as Cell<Point>;
     (c as Cell<Point>) as cell;
@@ -103,6 +117,7 @@ fun main(c: cell) {
 @testcase | 107 | x{09332}      | 4 12
 @testcase | 107 | x{2}          | 5 1
 @testcase | 107 | x{0234}       | 6 16
+@testcase | 108 |               | 5 1
 
 @fif_codegen
 """
```

### tolk/builtins.cpp
```diff
@@ -1093,12 +1093,10 @@ static AsmOp compile_store_int(std::vector<VarDescr>& res, std::vector<VarDescr>
   // purpose: to merge consecutive `b.storeUint(0, 1).storeUint(1, 1)` into one "1 PUSHINT + 2 STU",
   // when constant arguments are passed, keep them as a separate (fake) instruction, to be handled by optimizer later
   bool value_and_len_is_const = z.is_int_const() && x.is_int_const();
-  if (value_and_len_is_const && G.settings.optimization_level >= 2) {
+  if (value_and_len_is_const && x.int_const >= 0 && z.int_const > 0 && z.int_const <= 256 && G.settings.optimization_level >= 2) {
     // don't handle negative numbers or potential overflow, merging them is incorrect
-    bool value_is_safe = sgnd
-        ? x.int_const >= 0 && z.int_const < 64 && x.int_const < (1ULL << (z.int_const->to_long() - 1))
-        : x.int_const >= 0;
-    if (value_is_safe && z.int_const > 0 && z.int_const <= (255 + !sgnd)) {
+    int len = static_cast<int>(z.int_const->to_long());
+    if (x.int_const->fits_bits(len, sgnd)) {
       z.unused();
       x.unused();
       return AsmOp::Custom(loc, "MY_store_int"s + (sgnd ? "I " : "U ") + x.int_const->to_dec_string() + " " + z.int_const->to_dec_string(), 1);
```
