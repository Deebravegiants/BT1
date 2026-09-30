# [?] fix: Overflow checks for constant folding (#3420)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2023-11-03
Source: https://github.com/noir-lang/noir/commit/b7a6383cf9dc3bc4a71b9644352340c1e9339c81
Type: security-commit

## Details
fix: Overflow checks for constant folding (#3420)

## Patch
### compiler/noirc_evaluator/src/ssa/ir/instruction.rs
```diff
@@ -847,9 +847,12 @@ fn eval_constant_binary_op(
             if matches!(operator, BinaryOp::Div | BinaryOp::Mod) && rhs == 0 {
                 return None;
             }
-
-            let result = function(lhs, rhs);
-            truncate(result, *bit_size).into()
+            let result = function(lhs, rhs)?;
+            // Check for overflow
+            if result >= 2u128.pow(*bit_size) {
+                return None;
+            }
+            result.into()
         }
         Type::Numeric(NumericType::Signed { bit_size }) => {
             let function = operator.get_i128_function();
@@ -869,10 +872,14 @@ fn eval_constant_binary_op(
                 return None;
             }
 
-            let result = function(lhs, rhs);
+            let result = function(lhs, rhs)?;
+            // Check for overflow
+            if result >= 2i128.pow(*bit_size - 1) || result < -(2i128.pow(*bit_size - 1)) {
+                return None;
+            }
             let result =
                 if result >= 0 { result as u128 } else { (2i128.pow(*bit_size) + result) as u128 };
-            truncate(result, *bit_size).into()
+            result.into()
         }
         _ => return None,
     };
@@ -906,33 +913,33 @@ impl BinaryOp {
         }
     }
 
-    fn get_u128_function(self) -> fn(u128, u128) -> u128 {
+    fn get_u128_function(self) -> fn(u128, u128) -> Option<u128> {
         match self {
-            BinaryOp::Add => u128::wrapping_add,
-            BinaryOp::Sub => u128::wrapping_sub,
-            BinaryOp::Mul => u128::wrapping_mul,
-            BinaryOp::Div => u128::wrapping_div,
-            BinaryOp::Mod => u128::wrapping_rem,
-            BinaryOp::And => |x, y| x & y,
-            BinaryOp::Or => |x, y| x | y,
-            BinaryOp::Xor => |x, y| x ^ y,
-            BinaryOp::Eq => |x, y| (x == y) as u128,
-            BinaryOp::Lt => |x, y| (x < y) as u128,
+            BinaryOp::Add => u128::checked_add,
+            BinaryOp::Sub => u128::checked_sub,
+            BinaryOp::Mul => u128::checked_mul,
+            BinaryOp::Div => u128::checked_div,
+            BinaryOp::Mod => u128::checked_rem,
+            BinaryOp::And => |x, y| Some(x & y),
+            BinaryOp::Or => |x, y| Some(x | y),
+            BinaryOp::Xor => |x, y| Some(x ^ y),
+            BinaryOp::Eq => |x, y| Some((x == y) as u128),
+            BinaryOp::Lt => |x, y| Some((x < y) as u128),
         }
     }
 
-    fn get_i128_function(self) -> fn(i128, i128) -> i128 {
+    fn get_i128_function(self) -> fn(i128, i128) -> Option<i128> {
         match self {
-            BinaryOp::Add => i128::wrapping_add,
-            BinaryOp::Sub => i128::wrapping_sub,
-            BinaryOp::Mul => i128::wrapping_mul,
-            BinaryOp::Div => i128::wrapping_div,
-            BinaryOp::Mod => i128::wrapping_rem,
-            BinaryOp::And => |x, y| x & y,
-            BinaryOp::Or => |x, y| x | y,
-            BinaryOp::Xor => |x, y| x ^ y,
-            BinaryOp::Eq => |x, y| (x == y) as i128,
-            BinaryOp::Lt => |x, y| (x < y) as i128,
+            BinaryOp::Add => i128::checked_add,
+            BinaryOp::Sub => i128::checked_sub,
+            BinaryOp::Mul => i128::checked_mul,
+            BinaryOp::Div => i128::checked_div,
+            BinaryOp::Mod => i128::checked_rem,
+            BinaryOp::And => |x, y| Some(x & y),
+            BinaryOp::Or => |x, y| Some(x | y),
+            BinaryOp::Xor => |x, y| Some(x ^ y),
+            BinaryOp::Eq => |x, y| Some((x == y) as i128),
+            BinaryOp::Lt => |x, y| Some((x < y) as i128),
         }
     }
 }
```

### noir_stdlib/src/hash/poseidon.nr
```diff
@@ -20,7 +20,8 @@ pub fn config<M,N>(
     mds: [Field; N])
     -> PoseidonConfig<M,N> {
     // Input checks
-    assert(t as u8 * (rf + rp) == ark.len() as u8);
+    let mul = crate::wrapping_mul(t as u8, (rf + rp));
+    assert(mul == ark.len() as u8);
     assert(t * t == mds.len());
     assert(alpha != 0);
     
```

### tooling/nargo_cli/tests/execution_success/4_sub/src/main.nr
```diff
@@ -3,8 +3,4 @@ use dep::std;
 fn main(mut x: u32, y: u32, z: u32) {
     x = std::wrapping_sub(x,y);
     assert(x == z);
-
-    // Test constant underflow (regression for #2045)
-    let x = -1 as u4;
-    assert(x == 15);
 }
```

### tooling/nargo_cli/tests/execution_success/6_array/src/main.nr
```diff
@@ -25,7 +25,7 @@ fn main(x: [u32; 5], y: [u32; 5], mut z: u32, t: u32) {
     for i in 0..5 {
        z  = z + x[i]*y[i];
         for _i in 0..3 {
-            c = i as u32 - 2 as u32;
+            c = std::wrapping_sub(i as u32,2 as u32);
             z = std::wrapping_mul(z,c);
         }
     }
```
