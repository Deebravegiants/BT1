# [?] fix: right shift overflow to 0 (#8772)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2025-06-05
Source: https://github.com/noir-lang/noir/commit/7a252703d7f2c11409f9b8034df8224c438f768f
Type: security-commit

## Details
fix: right shift overflow to 0 (#8772)

## Patch
### compiler/noirc_evaluator/src/ssa/ir/instruction/binary.rs
```diff
@@ -130,21 +130,36 @@ pub(crate) fn eval_constant_binary_op(
 
             let lhs = try_convert_field_element_to_signed_integer(lhs, bit_size)?;
             let rhs = try_convert_field_element_to_signed_integer(rhs, bit_size)?;
-            // The divisor is being truncated into the type of the operand, which can potentially
-            // lead to the rhs being zero.
-            // If the rhs of a division is zero, attempting to evaluate the division will cause a compiler panic.
-            // Thus, we do not evaluate the division in this method, as we want to avoid triggering a panic,
-            // and the operation should be handled by ACIR generation.
-            if matches!(operator, BinaryOp::Div | BinaryOp::Mod) && rhs == 0 {
-                return None;
-            }
 
-            let result = function(lhs, rhs)?;
-            // Check for overflow
-            let two_pow_bit_size_minus_one = 1i128 << (bit_size - 1);
-            if result >= two_pow_bit_size_minus_one || result < -two_pow_bit_size_minus_one {
-                return None;
-            }
+            let result = function(lhs, rhs);
+            let result = match operator {
+                BinaryOp::Div | BinaryOp::Mod if rhs == 0 => {
+                    // The divisor is being truncated into the type of the operand, which can potentially
+                    // lead to the rhs being zero.
+                    // If the rhs of a division is zero, attempting to evaluate the division will cause a compiler panic.
+                    // Thus, we do not evaluate the division in this method, as we want to avoid triggering a panic,
+                    // and the operation should be handled by ACIR generation.
+                    return None;
+                }
+                BinaryOp::Shr => {
+                    if rhs >= bit_size as i128 {
+                        0
+                    } else {
+                        result?
+                    }
+                }
+
+                _ => {
+                    // Check for overflow
+                    let two_pow_bit_size_minus_one = 1i128 << (bit_size - 1);
+                    let result = result?;
+                    if result >= two_pow_bit_size_minus_one || result < -two_pow_bit_size_minus_one
+                    {
+                        return None;
+                    }
+                    result
+                }
+            };
             convert_signed_integer_to_field_element(result, bit_size)
         }
     };
```

### test_programs/execution_success/bit_shifts_comptime/src/main.nr
```diff
@@ -19,6 +19,8 @@ fn main(x: u64) {
     //regression for 6201
     let a: i16 = -769;
     assert_eq(a >> 3, -97);
+
+    regression_8310();
 }
 
 fn regression_2250() {
@@ -28,3 +30,9 @@ fn regression_2250() {
     let b: u32 = 1 >> 32;
     assert(b == 0);
 }
+
+fn regression_8310() {
+    let x: i64 = -356710612598522715;
+    let b = x >> 64;
+    assert(b == 0);
+}
```

### tooling/nargo_cli/tests/snapshots/execution_success/bit_shifts_comptime/execute__tests__expanded.snap
```diff
@@ -15,6 +15,7 @@ fn main(x: u64) {
     assert(((1 as u64) << 32) == 4294967296);
     let a: i16 = -769;
     assert((a >> 3) == -97);
+    regression_8310();
 }
 
 fn regression_2250() {
@@ -23,3 +24,9 @@ fn regression_2250() {
     let b: u32 = 1 >> 32;
     assert(b == 0);
 }
+
+fn regression_8310() {
+    let x: i64 = -356710612598522715;
+    let b: i64 = x >> 64;
+    assert(b == 0);
+}
```

### tooling/nargo_cli/tests/snapshots/execution_success/bit_shifts_comptime/execute__tests__force_brillig_false_inliner_-9223372036854775808.snap
```diff
@@ -45,7 +45,7 @@ expression: artifact
   "debug_symbols": "pZLPDoIwDMbfpeceYJugvIoxZEAxS5ZB5mZiiO9umeCfgxe8tFu//ZovXSfoqInn2rh+uEB1nKDxxlpzru3Q6mAGx9XpjrBe6+CJuAQfOlOj9uQCVC5ai3DVNqZHl1G7lIP2rGYI5DrO3LA3lubTHd909hsVUi6wkIcXvtvCq2ILX6zmRfEnX4oNvJTlwkul/uS/53fim26N//pxyKHKEUSKMkXF1hF23AChSLFMcQ+VQjhwM4Q8e6b8mRifZ3XV3ujG0rJKfXTtx2aF27gq6+6Nfmipi55mT0ljlw8=",
   "file_map": {
     "50": {
-      "source": "fn main(x: u64) {\n    let two: u64 = 2;\n    let three: u64 = 3;\n    // shifts on constant values\n    assert(two << 2 == 8);\n    assert((two << 3) / 8 == two);\n    assert((three >> 1) == 1);\n    // shifts on runtime values\n    assert(x << 1 == 128);\n    assert(x >> 2 == 16);\n\n    regression_2250();\n\n    //regression for 3481\n    assert(x << 63 == 0);\n\n    assert_eq((1 as u64) << 32, 0x0100000000);\n\n    //regression for 6201\n    let a: i16 = -769;\n    assert_eq(a >> 3, -97);\n}\n\nfn regression_2250() {\n    let a: u1 = 1 >> 1;\n    assert(a == 0);\n\n    let b: u32 = 1 >> 32;\n    assert(b == 0);\n}\n",
+      "source": "fn main(x: u64) {\n    let two: u64 = 2;\n    let three: u64 = 3;\n    // shifts on constant values\n    assert(two << 2 == 8);\n    assert((two << 3) / 8 == two);\n    assert((three >> 1) == 1);\n    // shifts on runtime values\n    assert(x << 1 == 128);\n    assert(x >> 2 == 16);\n\n    regression_2250();\n\n    //regression for 3481\n    assert(x << 63 == 0);\n\n    assert_eq((1 as u64) << 32, 0x0100000000);\n\n    //regression for 6201\n    let a: i16 = -769;\n    assert_eq(a >> 3, -97);\n\n    regression_8310();\n}\n\nfn regression_2250() {\n    let a: u1 = 1 >> 1;\n    assert(a == 0);\n\n    let b: u32 = 1 >> 32;\n    assert(b == 0);\n}\n\nfn regression_8310() {\n    let x: i64 = -356710612598522715;\n    let b = x >> 64;\n    assert(b == 0);\n}\n",
       "path": ""
     }
   },
```

### tooling/nargo_cli/tests/snapshots/execution_success/bit_shifts_comptime/execute__tests__force_brillig_false_inliner_0.snap
```diff
@@ -45,7 +45,7 @@ expression: artifact
   "debug_symbols": "pZLPDoIwDMbfpeceYJugvIoxZEAxS5ZB5mZiiO9umeCfgxe8tFu//ZovXSfoqInn2rh+uEB1nKDxxlpzru3Q6mAGx9XpjrBe6+CJuAQfOlOj9uQCVC5ai3DVNqZHl1G7lIP2rGYI5DrO3LA3lubTHd909hsVUi6wkIcXvtvCq2ILX6zmRfEnX4oNvJTlwkul/uS/53fim26N//pxyKHKEUSKMkXF1hF23AChSLFMcQ+VQjhwM4Q8e6b8mRifZ3XV3ujG0rJKfXTtx2aF27gq6+6Nfmipi55mT0ljlw8=",
   "file_map": {
     "50": {
-      "source": "fn main(x: u64) {\n    let two: u64 = 2;\n    let three: u64 = 3;\n    // shifts on constant values\n    assert(two << 2 == 8);\n    assert((two << 3) / 8 == two);\n    assert((three >> 1) == 1);\n    // shifts on runtime values\n    assert(x << 1 == 128);\n    assert(x >> 2 == 16);\n\n    regression_2250();\n\n    //regression for 3481\n    assert(x << 63 == 0);\n\n    assert_eq((1 as u64) << 32, 0x0100000000);\n\n    //regression for 6201\n    let a: i16 = -769;\n    assert_eq(a >> 3, -97);\n}\n\nfn regression_2250() {\n    let a: u1 = 1 >> 1;\n    assert(a == 0);\n\n    let b: u32 = 1 >> 32;\n    assert(b == 0);\n}\n",
+      "source": "fn main(x: u64) {\n    let two: u64 = 2;\n    let three: u64 = 3;\n    // shifts on constant values\n    assert(two << 2 == 8);\n    assert((two << 3) / 8 == two);\n    assert((three >> 1) == 1);\n    // shifts on runtime values\n    assert(x << 1 == 128);\n    assert(x >> 2 == 16);\n\n    regression_2250();\n\n    //regression for 3481\n    assert(x << 63 == 0);\n\n    assert_eq((1 as u64) << 32, 0x0100000000);\n\n    //regression for 6201\n    let a: i16 = -769;\n    assert_eq(a >> 3, -97);\n\n    regression_8310();\n}\n\nfn regression_2250() {\n    let a: u1 = 1 >> 1;\n    assert(a == 0);\n\n    let b: u32 = 1 >> 32;\n    assert(b == 0);\n}\n\nfn regression_8310() {\n    let x: i64 = -356710612598522715;\n    let b = x >> 64;\n    assert(b == 0);\n}\n",
       "path": ""
     }
   },
```

### tooling/nargo_cli/tests/snapshots/execution_success/bit_shifts_comptime/execute__tests__force_brillig_false_inliner_9223372036854775807.snap
```diff
@@ -45,7 +45,7 @@ expression: artifact
   "debug_symbols": "pZLPDoIwDMbfpeceYJugvIoxZEAxS5ZB5mZiiO9umeCfgxe8tFu//ZovXSfoqInn2rh+uEB1nKDxxlpzru3Q6mAGx9XpjrBe6+CJuAQfOlOj9uQCVC5ai3DVNqZHl1G7lIP2rGYI5DrO3LA3lubTHd909hsVUi6wkIcXvtvCq2ILX6zmRfEnX4oNvJTlwkul/uS/53fim26N//pxyKHKEUSKMkXF1hF23AChSLFMcQ+VQjhwM4Q8e6b8mRifZ3XV3ujG0rJKfXTtx2aF27gq6+6Nfmipi55mT0ljlw8=",
   "file_map": {
     "50": {
-      "source": "fn main(x: u64) {\n    let two: u64 = 2;\n    let three: u64 = 3;\n    // shifts on constant values\n    assert(two << 2 == 8);\n    assert((two << 3) / 8 == two);\n    assert((three >> 1) == 1);\n    // shifts on runtime values\n    assert(x << 1 == 128);\n    assert(x >> 2 == 16);\n\n    regression_2250();\n\n    //regression for 3481\n    assert(x << 63 == 0);\n\n    assert_eq((1 as u64) << 32, 0x0100000000);\n\n    //regression for 6201\n    let a: i16 = -769;\n    assert_eq(a >> 3, -97);\n}\n\nfn regression_2250() {\n    let a: u1 = 1 >> 1;\n    assert(a == 0);\n\n    let b: u32 = 1 >> 32;\n    assert(b == 0);\n}\n",
+      "source": "fn main(x: u64) {\n    let two: u64 = 2;\n    let three: u64 = 3;\n    // shifts on constant values\n    assert(two << 2 == 8);\n    assert((two << 3) / 8 == two);\n    assert((three >> 1) == 1);\n    // shifts on runtime values\n    assert(x << 1 == 128);\n    assert(x >> 2 == 16);\n\n    regression_2250();\n\n    //regression for 3481\n    assert(x << 63 == 0);\n\n    assert_eq((1 as u64) << 32, 0x0100000000);\n\n    //regression for 6201\n    let a: i16 = -769;\n    assert_eq(a >> 3, -97);\n\n    regression_8310();\n}\n\nfn regression_2250() {\n    let a: u1 = 1 >> 1;\n    assert(a == 0);\n\n    let b: u32 = 1 >> 32;\n    assert(b == 0);\n}\n\nfn regression_8310() {\n    let x: i64 = -356710612598522715;\n    let b = x >> 64;\n    assert(b == 0);\n}\n",
       "path": ""
     }
   },
```

### tooling/nargo_cli/tests/snapshots/execution_success/bit_shifts_comptime/execute__tests__force_brillig_true_inliner_-9223372036854775808.snap
```diff
@@ -38,7 +38,7 @@ expression: artifact
   "debug_symbols": "pZLBjoMgEIbfZc4cFBBbXqVpDCo2JAQN1U02xnffwdGtPfRiL3zi+P2MZGZobT09Khe6/gn6NkMdnffuUfm+MaPrA76dIUtLXoDOGeSKUILmiAvhuoJnhJzAQQuEIEjQElEQFKEkXAiYUjAQGQFTFIITBEESMEUtC4O9zWqM1qYuD33j3wwm2jCCDpP3DH6Mn9aPnoMJK0cTsZoxsKFFYmDnvE1PC3vZ2WeVC7HJXFz/9eKML9UZX+3Nc/WlX/ITvhDl5gspv/Tf7++OO9O4+DaJS0qKztTebttuCs2hOv4Oe2Wf5CH2jW2naFPSYZxxveHpkt+XdNof",
   "file_map": {
     "50": {
-      "source": "fn main(x: u64) {\n    let two: u64 = 2;\n    let three: u64 = 3;\n    // shifts on constant values\n    assert(two << 2 == 8);\n    assert((two << 3) / 8 == two);\n    assert((three >> 1) == 1);\n    // shifts on runtime values\n    assert(x << 1 == 128);\n    assert(x >> 2 == 16);\n\n    regression_2250();\n\n    //regression for 3481\n    assert(x << 63 == 0);\n\n    assert_eq((1 as u64) << 32, 0x0100000000);\n\n    //regression for 6201\n    let a: i16 = -769;\n    assert_eq(a >> 3, -97);\n}\n\nfn regression_2250() {\n    let a: u1 = 1 >> 1;\n    assert(a == 0);\n\n    let b: u32 = 1 >> 32;\n    assert(b == 0);\n}\n",
+      "source": "fn main(x: u64) {\n    let two: u64 = 2;\n    let three: u64 = 3;\n    // shifts on constant values\n    assert(two << 2 == 8);\n    assert((two << 3) / 8 == two);\n    assert((three >> 1) == 1);\n    // shifts on runtime values\n    assert(x << 1 == 128);\n    assert(x >> 2 == 16);\n\n    regression_2250();\n\n    //regression for 3481\n    assert(x << 63 == 0);\n\n    assert_eq((1 as u64) << 32, 0x0100000000);\n\n    //regression for 6201\n    let a: i16 = -769;\n    assert_eq(a >> 3, -97);\n\n    regression_8310();\n}\n\nfn regression_2250() {\n    let a: u1 = 1 >> 1;\n    assert(a == 0);\n\n    let b: u32 = 1 >> 32;\n    assert(b == 0);\n}\n\nfn regression_8310() {\n    let x: i64 = -356710612598522715;\n    let b = x >> 64;\n    assert(b == 0);\n}\n",
       "path": ""
     }
   },
```

### tooling/nargo_cli/tests/snapshots/execution_success/bit_shifts_comptime/execute__tests__force_brillig_true_inliner_0.snap
```diff
@@ -38,7 +38,7 @@ expression: artifact
   "debug_symbols": "pZLBjoMgEIbfZc4cFBBbXqVpDCo2JAQN1U02xnffwdGtPfRiL3zi+P2MZGZobT09Khe6/gn6NkMdnffuUfm+MaPrA76dIUtLXoDOGeSKUILmiAvhuoJnhJzAQQuEIEjQElEQFKEkXAiYUjAQGQFTFIITBEESMEUtC4O9zWqM1qYuD33j3wwm2jCCDpP3DH6Mn9aPnoMJK0cTsZoxsKFFYmDnvE1PC3vZ2WeVC7HJXFz/9eKML9UZX+3Nc/WlX/ITvhDl5gspv/Tf7++OO9O4+DaJS0qKztTebttuCs2hOv4Oe2Wf5CH2jW2naFPSYZxxveHpkt+XdNof",
   "file_map": {
     "50": {
-      "source": "fn main(x: u64) {\n    let two: u64 = 2;\n    let three: u64 = 3;\n    // shifts on constant values\n    assert(two << 2 == 8);\n    assert((two << 3) / 8 == two);\n    assert((three >> 1) == 1);\n    // shifts on runtime values\n    assert(x << 1 == 128);\n    assert(x >> 2 == 16);\n\n    regression_2250();\n\n    //regression for 3481\n    assert(x << 63 == 0);\n\n    assert_eq((1 as u64) << 32, 0x0100000000);\n\n    //regression for 6201\n    let a: i16 = -769;\n    assert_eq(a >> 3, -97);\n}\n\nfn regression_2250() {\n    let a: u1 = 1 >> 1;\n    assert(a == 0);\n\n    let b: u32 = 1 >> 32;\n    assert(b == 0);\n}\n",
+      "source": "fn main(x: u64) {\n    let two: u64 = 2;\n    let three: u64 = 3;\n    // shifts on constant values\n    assert(two << 2 == 8);\n    assert((two << 3) / 8 == two);\n    assert((three >> 1) == 1);\n    // shifts on runtime values\n    assert(x << 1 == 128);\n    assert(x >> 2 == 16);\n\n    regression_2250();\n\n    //regression for 3481\n    assert(x << 63 == 0);\n\n    assert_eq((1 as u64) << 32, 0x0100000000);\n\n    //regression for 6201\n    let a: i16 = -769;\n    assert_eq(a >> 3, -97);\n\n    regression_8310();\n}\n\nfn regression_2250() {\n    let a: u1 = 1 >> 1;\n    assert(a == 0);\n\n    let b: u32 = 1 >> 32;\n    assert(b == 0);\n}\n\nfn regression_8310() {\n    let x: i64 = -356710612598522715;\n    let b = x >> 64;\n    assert(b == 0);\n}\n",
       "path": ""
     }
   },
```

### tooling/nargo_cli/tests/snapshots/execution_success/bit_shifts_comptime/execute__tests__force_brillig_true_inliner_9223372036854775807.snap
```diff
@@ -38,7 +38,7 @@ expression: artifact
   "debug_symbols": "pZLBjoMgEIbfZc4cFBBbXqVpDCo2JAQN1U02xnffwdGtPfRiL3zi+P2MZGZobT09Khe6/gn6NkMdnffuUfm+MaPrA76dIUtLXoDOGeSKUILmiAvhuoJnhJzAQQuEIEjQElEQFKEkXAiYUjAQGQFTFIITBEESMEUtC4O9zWqM1qYuD33j3wwm2jCCDpP3DH6Mn9aPnoMJK0cTsZoxsKFFYmDnvE1PC3vZ2WeVC7HJXFz/9eKML9UZX+3Nc/WlX/ITvhDl5gspv/Tf7++OO9O4+DaJS0qKztTebttuCs2hOv4Oe2Wf5CH2jW2naFPSYZxxveHpkt+XdNof",
   "file_map": {
     "50": {
-      "source": "fn main(x: u64) {\n    let two: u64 = 2;\n    let three: u64 = 3;\n    // shifts on constant values\n    assert(two << 2 == 8);\n    assert((two << 3) / 8 == two);\n    assert((three >> 1) == 1);\n    // shifts on runtime values\n    assert(x << 1 == 128);\n    assert(x >> 2 == 16);\n\n    regression_2250();\n\n    //regression for 3481\n    assert(x << 63 == 0);\n\n    assert_eq((1 as u64) << 32, 0x0100000000);\n\n    //regression for 6201\n    let a: i16 = -769;\n    assert_eq(a >> 3, -97);\n}\n\nfn regression_2250() {\n    let a: u1 = 1 >> 1;\n    assert(a == 0);\n\n    let b: u32 = 1 >> 32;\n    assert(b == 0);\n}\n",
+      "source": "fn main(x: u64) {\n    let two: u64 = 2;\n    let three: u64 = 3;\n    // shifts on constant values\n    assert(two << 2 == 8);\n    assert((two << 3) / 8 == two);\n    assert((three >> 1) == 1);\n    // shifts on runtime values\n    assert(x << 1 == 128);\n    assert(x >> 2 == 16);\n\n    regression_2250();\n\n    //regression for 3481\n    assert(x << 63 == 0);\n\n    assert_eq((1 as u64) << 32, 0x0100000000);\n\n    //regression for 6201\n    let a: i16 = -769;\n    assert_eq(a >> 3, -97);\n\n    regression_8310();\n}\n\nfn regression_2250() {\n    let a: u1 = 1 >> 1;\n    assert(a == 0);\n\n    let b: u32 = 1 >> 32;\n    assert(b == 0);\n}\n\nfn regression_8310() {\n    let x: i64 = -356710612598522715;\n    let b = x >> 64;\n    assert(b == 0);\n}\n",
       "path": ""
     }
   },
```
