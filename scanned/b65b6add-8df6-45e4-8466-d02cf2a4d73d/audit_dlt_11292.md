# [?] fix: error on boolean shift overflow in interpreter (#9724)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2025-09-04
Source: https://github.com/noir-lang/noir/commit/387b9b20fed02cd4f06921e4315f0e7d056d92ff
Type: security-commit

## Details
fix: error on boolean shift overflow in interpreter (#9724)

## Patch
### compiler/noirc_evaluator/src/ssa/interpreter/mod.rs
```diff
@@ -1583,14 +1583,14 @@ fn interpret_u1_binary_op(
         BinaryOp::Xor => lhs ^ rhs,
         BinaryOp::Shl => {
             if rhs {
-                false
+                return Err(overflow());
             } else {
                 lhs
             }
         }
         BinaryOp::Shr => {
             if rhs {
-                false
+                return Err(overflow());
             } else {
                 lhs
             }
```

### compiler/noirc_evaluator/src/ssa/opt/constant_folding.rs
```diff
@@ -1858,6 +1858,25 @@ mod test {
         assert_ssa_does_not_change(src, Ssa::fold_constants);
     }
 
+    #[test]
+    fn do_not_inline_brillig_overflow() {
+        // Regression test for https://github.com/noir-lang/noir/issues/9694
+        // The call can be constant
+        let src = "
+            acir(inline) predicate_pure fn main f0 {
+            b0():
+                v2 = call f1(u1 0) -> u1
+                return v2
+            }
+            brillig(inline) predicate_pure fn func_5 f1 {
+            b0(v0: u1):
+                v2 = shl v0, u1 1
+                return v2
+            }
+        ";
+        assert_ssa_does_not_change(src, Ssa::fold_constants_with_brillig);
+    }
+
     #[test]
     fn does_not_deduplicate_calls_to_functions_which_differ_in_return_value_types() {
         // We have a few intrinsics which have a generic return value (generally for array lengths), we want
```
