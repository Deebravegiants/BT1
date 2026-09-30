# [?] fix(ssa): Handle OOB indexing of slice literals in `remove_unreachalbe_instructions` (#9999)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2025-09-25
Source: https://github.com/noir-lang/noir/commit/88bf5402b734dfdb1d6315fe181c0a9770144ff9
Type: security-commit

## Details
fix(ssa): Handle OOB indexing of slice literals in `remove_unreachalbe_instructions` (#9999)

## Patch
### compiler/noirc_evaluator/src/ssa/ir/types.rs
```diff
@@ -216,6 +216,8 @@ impl Type {
     /// to represent the type. This is 1 for every primitive type, and is the number of fields
     /// for any flattened tuple type.
     ///
+    /// Equivalent to `self.element_types().len()`, but doesn't consume the `self`.
+    ///
     /// Panics if `self` is not a [`Type::Array`] or [`Type::Slice`].
     pub(crate) fn element_size(&self) -> usize {
         match self {
```

### compiler/noirc_evaluator/src/ssa/opt/remove_if_else.rs
```diff
@@ -271,7 +271,7 @@ impl Context {
                 }
                 // Check if the item was made by a MakeArray instruction, which can create slices as well.
                 if let Some((array, typ)) = dfg.get_array_constant(value) {
-                    let length = array.len() / typ.element_types().len();
+                    let length = array.len() / typ.element_size();
                     return *entry.insert(length as u32);
                 }
                 // For non-constant slices we can't tell the size, which would mean we can't merge it.
```

### compiler/noirc_evaluator/src/ssa/opt/remove_unreachable_instructions.rs
```diff
@@ -281,9 +281,21 @@ impl Function {
                     if context.dfg.runtime().is_acir() =>
                 {
                     let array_type = context.dfg.type_of_value(*array);
-                    // We can only know a guaranteed out-of-bounds access for arrays, never for slices.
-                    let Type::Array(_, len) = array_type else {
-                        return;
+                    // We can only know a guaranteed out-of-bounds access for arrays,
+                    // and slices which have been declared as a literal.
+                    let len = match array_type {
+                        Type::Array(_, len) => len,
+                        Type::Slice(_) => {
+                            let Some(Instruction::MakeArray { elements, typ }) =
+                                context.dfg.get_local_or_global_instruction(*array)
+                            else {
+                                return;
+                            };
+                            // The index check expects `len` to be the logical length, like for arrays,
+                            // not the flattened size, so we need to divide by the number of items.
+                            (elements.len() / typ.element_size()) as u32
+                        }
+                        _ => return,
                     };
 
                     let array_op_always_fails = len == 0
@@ -844,6 +856,29 @@ mod test {
         "#);
     }
 
+    #[test]
+    fn removes_slice_literal_index_oob() {
+        let src = r#"
+        acir(inline) predicate_pure fn main f0 {
+          b0(v0: u32):
+            v1 = make_array [u1 1, u32 2, u64 3] : [(u1, u32, u64)]
+            v2 = array_get v1, index u32 4 -> u32
+            return v2
+        }
+        "#;
+        let ssa = Ssa::from_str(src).unwrap();
+        let ssa = ssa.remove_unreachable_instructions();
+
+        assert_ssa_snapshot!(ssa, @r#"
+        acir(inline) predicate_pure fn main f0 {
+          b0(v0: u32):
+            v4 = make_array [u1 1, u32 2, u64 3] : [(u1, u32, u64)]
+            constrain u1 0 == u1 1, "Index out of bounds"
+            unreachable
+        }
+        "#);
+    }
+
     #[test]
     fn removes_unreachable_instructions_from_dominated_blocks_normal_order() {
         let src = r#"
```

### test_programs/compile_success_no_bug/regression_9997/Nargo.toml
```diff
@@ -0,0 +1,6 @@
+[package]
+name = "regression_9997"
+type = "bin"
+authors = [""]
+
+[dependencies]
\ No newline at end of file
```

### test_programs/compile_success_no_bug/regression_9997/src/main.nr
```diff
@@ -0,0 +1,8 @@
+fn main(a: pub u32) -> pub Field {
+    if a == 0 {
+        let c: [&mut Field] = &[(&mut 1)];
+        1 / { (*c[3]) }
+    } else {
+        2
+    }
+}
```

### tooling/nargo_cli/tests/snapshots/compile_success_no_bug/regression_9997/execute__tests__expanded.snap
```diff
@@ -0,0 +1,12 @@
+---
+source: tooling/nargo_cli/tests/execute.rs
+expression: expanded_code
+---
+fn main(a: pub u32) -> pub Field {
+    if a == 0_u32 {
+        let c: [&mut Field] = &[&mut 1_Field];
+        1_Field / { *c[3_u32] }
+    } else {
+        2_Field
+    }
+}
```
