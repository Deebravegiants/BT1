# [?] [Tolk] Fix several compiler crashes in corner cases

## Summary
Severity: Unknown
Chain: TON
Component: ton-blockchain/ton
Published: 2026-04-13
Source: https://github.com/ton-blockchain/ton/commit/782fbb9610932c641b246ab5babd69e4cbab2040
Type: security-commit

## Details
[Tolk] Fix several compiler crashes in corner cases

Those crashes were often caused by recursive computations
leading to stack overflow.

## Patch
### tolk-tester/tests/assignment-tests.tolk
```diff
@@ -209,6 +209,19 @@ fun test124() {
     return (a1, a18);
 }
 
+const C125: (int, int) = (1, 2);
+
+struct P125 {
+    x: int;
+}
+
+@method_id(125)
+fun test125() {
+    var x = 1;
+    (x, Point { x: C125.0, y: C125.1 }).0 = 5;
+    return x;
+}
+
 
 fun main(value: int, ) {
     var (x: int?, y,) = (autoInferIntNull(value), autoInferIntNull(value * 2));
@@ -231,6 +244,7 @@ fun main(value: int, ) {
 @testcase | 122 |        | 0 10 0
 @testcase | 123 |        | 13
 @testcase | 124 |        | 1 18
+@testcase | 125 |        | 5
 
 
 @fif_codegen
```

### tolk-tester/tests/cells-slices.tolk
```diff
@@ -639,6 +639,15 @@ fun test47() {
     )
 }
 
+@method_id(148)
+fun test48() {
+    var s = beginCell().storeUint(1, 8).endCell().beginParse();
+    slice.skipBits(mutate s, 1);
+    var b = beginCell();
+    val b2 = builder.storeAny<int32>(mutate b, 1);
+    return (s.remainingBitsCount(), b2.bitsCount());
+}
+
 fun main(): int {
     return 0;
 }
@@ -691,6 +700,7 @@ fun main(): int {
 @testcase | 144 |     | 0 0 0 0 -1 3820012610 -1 0 0
 @testcase | 146 |     | 64898 64898 30460 59911 15354 54467 54467 54467 15533 16598 20076 64898 64898 30460 11765
 @testcase | 147 |     | -1 0 0 0 -1 0 0 -1 0 -1 0 -1 0 777 -1 -1 -1
+@testcase | 148 |     | 7 32
 
 We test that consequtive storeInt/storeUint with constants are joined into a single number
 
```

### tolk-tester/tests/constants-tests.tolk
```diff
@@ -130,6 +130,24 @@ const shape1: [int, bool, int32] = [5, false, 7];
 const shape2: [int, (int, bool), Point?, Point?, ()] = [5, (6, true), {}, null, ()]
 const shape1_tens = (shape1.0, shape1.1);
 
+const nul_arr_i: array<int>? = [1]
+const nul_list_i: lisp_list<int>? = [1]
+const nul_list_i_n: lisp_list<int>? = null
+const coins_or_int8: coins | int8 = Wrapper { item: ton("0.05") }.item
+const arr_or_int: array<int> | int = []
+
+struct WithNullableArray {
+    x: array<int>?
+}
+
+struct WithNullableArrayDef {
+    x: array<int>? = [2]
+}
+
+const objWithNullableArray: WithNullableArray = { x: [1] }
+const objWithNullableArrayDef: WithNullableArrayDef = {}
+
+
 fun iget240(): MInt { return int240; }
 
 @pure
@@ -280,6 +298,26 @@ fun test22() {
     return (str1.beginParse().remainingBitsCount(), str3.remainingBitsCount());
 }
 
+@method_id(123)
+fun test123() {
+    return (nul_arr_i!, nul_list_i!, 777, nul_list_i_n)
+}
+
+@method_id(124)
+fun test124() {
+    return (
+        match (val ii = arr_or_int) { array<int> => ii.size(), int => ii },
+        match (val ii = coins_or_int8) { int8 => 0, coins => ii as int },
+    )
+}
+
+@method_id(125)
+fun test125() {
+    val manual = objWithNullableArray.x!;
+    val def = objWithNullableArrayDef.x!;
+    return (manual.size(), manual.get(0), def.size(), def.get(0));
+}
+
 fun main() {
     var i1: int = iget1();
     var i2: int = iget2();
@@ -326,6 +364,9 @@ fun main() {
 @testcase | 120 |   | [ 5 0 7 ] [ 5 [ 6 -1 ] [ 10 20 typeid-3 ] [ (null) (null) 0 ] [] ] 5 0
 @testcase | 121 |   | (null) (null) 0 
 @testcase | 122 |   | 48 64
+@testcase | 123 |   | [ 1 ] [ 1 (null) ] 777 (null) 0
+@testcase | 124 |   | 0 50000000
+@testcase | 125 |   | 1 1 1 2
 
-@code_hash 67723149647754803618590559478221789890530509010341373926517429131762844790728
+@code_hash 112630949630661007029774670083026056546591178981553693940505124712245440095740
 */
```

### tolk-tester/tests/generics-4.tolk
```diff
@@ -279,13 +279,13 @@ fun main() {
   test6() PROC:<{               //
     <b b> PUSHREF               //  p.init.USlot2
     -1 PUSHINT                  //  p.init.USlot2 '11=-1
-    FALSE                       //  p.init.USlot2 '11=-1 '12
-    TRUE                        //  p.init.USlot2 '11=-1 '12 '14
-    s0 s3 XCHG                  //  '14 '11=-1 '12 p.init.USlot2
-    CDEPTH                      //  '14 '11=-1 '12 '19
-    0 EQINT                     //  '14 '11=-1 '12 '21
-    0 NEQINT                    //  '14 '11=-1 '12 '18
-    s1 s3 s0 XCHG3              //  '11=-1 '12 '14 '18
+    0 PUSHINT                   //  p.init.USlot2 '11=-1 '12=0
+    TRUE                        //  p.init.USlot2 '11=-1 '12=0 '13
+    s0 s3 XCHG                  //  '13 '11=-1 '12=0 p.init.USlot2
+    CDEPTH                      //  '13 '11=-1 '12=0 '18
+    0 EQINT                     //  '13 '11=-1 '12=0 '20
+    0 NEQINT                    //  '13 '11=-1 '12=0 '17
+    s1 s3 s0 XCHG3              //  '11=-1 '12=0 '13 '17
   }>
 """
  */
```

### tolk-tester/tests/inference-tests.tolk
```diff
@@ -169,6 +169,13 @@ fun test12(): int {
     return 1;
 }
 
+fun test13(c: cell) {
+    while (c == null) {
+        var x = c;
+        __expect_type(x, "never");
+    }
+}
+
 
 fun main() {
     return 0;
```

### tolk-tester/tests/invalid-declaration/err-1388.tolk
```diff
@@ -0,0 +1,10 @@
+fun main() {
+}
+
+fun onInternalMessage(in: InMessage) {
+}
+
+/**
+@compilation_should_fail
+@stderr both `main` and `onInternalMessage` are not allowed
+ */
```

### tolk-tester/tests/invalid-declaration/err-1587.tolk
```diff
@@ -0,0 +1,16 @@
+struct Box<T> {
+    next: Box<T>
+}
+
+fun makeBox<T>(): Box<T> {
+    throw 101;
+}
+
+fun main() {
+    return makeBox<int>();
+}
+
+/**
+@compilation_should_fail
+@stderr struct `Box<int>` size is infinity due to recursive fields
+ */
```

### tolk-tester/tests/invalid-declaration/err-1799.tolk
```diff
@@ -0,0 +1,16 @@
+struct A {
+    x: int = B{}.y
+}
+
+struct B {
+    y: int = A{}.x
+}
+
+fun main() {
+    return 0;
+}
+
+/**
+@compilation_should_fail
+@stderr field `y` default value circularly references itself
+ */
```

### tolk-tester/tests/invalid-declaration/err-1843.tolk
```diff
@@ -0,0 +1,14 @@
+struct S {
+    x: int = C.x
+}
+
+const C: S = {};
+
+fun main(): int {
+    return 0;
+}
+
+/**
+@compilation_should_fail
+@stderr const `C` appears, directly or indirectly, in its own initializer
+ */
```

### tolk-tester/tests/invalid-declaration/err-1909.tolk
```diff
@@ -0,0 +1,12 @@
+
+fun onInternalMessage(in: InMessage) {
+    var body = (fun() {
+        return in.body;
+    })();
+    body.skipBits(0);
+}
+
+/**
+@compilation_should_fail
+@stderr capturing `InMessage` in a lambda is prohibited
+ */
```

### tolk-tester/tests/invalid-declaration/err-1974.tolk
```diff
@@ -0,0 +1,16 @@
+struct A<T = B> {
+    value: T
+}
+
+struct B<U = A> {
+    value: U
+}
+
+fun main(a: A) {
+    return a;
+}
+
+/**
+@compilation_should_fail
+@stderr type `A` circularly references itself
+ */
```

### tolk-tester/tests/invalid-declaration/err-1975.tolk
```diff
@@ -0,0 +1,11 @@
+type A<T = B> = T;
+type B<U = A> = U;
+
+fun main(): A {
+    return 0;
+}
+
+/**
+@compilation_should_fail
+@stderr type `A` circularly references itself
+ */
```
