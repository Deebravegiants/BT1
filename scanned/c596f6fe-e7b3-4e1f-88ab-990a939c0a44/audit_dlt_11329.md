# [?] fix: Prevent hoisting binary instructions which can overflow (#6672)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2024-12-02
Source: https://github.com/noir-lang/noir/commit/b4750d8dc13245bad81cbf7bef7010e3794e040a
Type: security-commit

## Details
fix: Prevent hoisting binary instructions which can overflow (#6672)

Co-authored-by: Tom French <15848336+TomAFrench@users.noreply.github.com>

## Patch
### compiler/noirc_evaluator/src/ssa/ir/instruction.rs
```diff
@@ -389,9 +389,22 @@ impl Instruction {
             // This should never be side-effectful
             MakeArray { .. } => false,
 
+            // Some binary math can overflow or underflow
+            Binary(binary) => match binary.operator {
+                BinaryOp::Add | BinaryOp::Sub | BinaryOp::Mul | BinaryOp::Div | BinaryOp::Mod => {
+                    true
+                }
+                BinaryOp::Eq
+                | BinaryOp::Lt
+                | BinaryOp::And
+                | BinaryOp::Or
+                | BinaryOp::Xor
+                | BinaryOp::Shl
+                | BinaryOp::Shr => false,
+            },
+
             // These can have different behavior depending on the EnableSideEffectsIf context.
-            Binary(_)
-            | Cast(_, _)
+            Cast(_, _)
             | Not(_)
             | Truncate { .. }
             | IfElse { .. }
```

### compiler/noirc_evaluator/src/ssa/opt/constant_folding.rs
```diff
@@ -1187,15 +1187,15 @@ mod test {
                 v2 = lt u32 1000, v0
                 jmpif v2 then: b1, else: b2
               b1():
-                v4 = add v0, u32 1
+                v4 = shl v0, u32 1
                 v5 = lt v0, v4
                 constrain v5 == u1 1
                 jmp b2()
               b2():
                 v7 = lt u32 1000, v0
                 jmpif v7 then: b3, else: b4
               b3():
-                v8 = add v0, u32 1
+                v8 = shl v0, u32 1
                 v9 = lt v0, v8
                 constrain v9 == u1 1
                 jmp b4()
@@ -1213,10 +1213,10 @@ mod test {
             brillig(inline) fn main f0 {
               b0(v0: u32):
                 v2 = lt u32 1000, v0
-                v4 = add v0, u32 1
+                v4 = shl v0, u32 1
                 jmpif v2 then: b1, else: b2
               b1():
-                v5 = add v0, u32 1
+                v5 = shl v0, u32 1
                 v6 = lt v0, v5
                 constrain v6 == u1 1
                 jmp b2()
@@ -1457,6 +1457,32 @@ mod test {
         assert_normalized_ssa_equals(ssa, src);
     }
 
+    #[test]
+    fn does_not_hoist_sub_to_common_ancestor() {
+        let src = "
+            acir(inline) fn main f0 {
+              b0(v0: u32):
+                v2 = eq v0, u32 0
+                jmpif v2 then: b4, else: b1
+              b4():
+                v5 = sub v0, u32 1
+                jmp b5()
+              b5():
+                return
+              b1():
+                jmpif v0 then: b3, else: b2
+              b3():
+                v4 = sub v0, u32 1 // We can't hoist this because v0 is zero here and it will lead to an underflow
+                jmp b5()
+              b2():
+                jmp b5()
+            }
+            ";
+        let ssa = Ssa::from_str(src).unwrap();
+        let ssa = ssa.fold_constants_using_constraints();
+        assert_normalized_ssa_equals(ssa, src);
+    }
+
     #[test]
     fn deduplicates_side_effecting_intrinsics() {
         let src = "
```
