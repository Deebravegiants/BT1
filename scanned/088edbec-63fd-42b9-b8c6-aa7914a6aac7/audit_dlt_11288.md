# [?] fix(fuzz): Avoid OOB when `in_no_dynamic` mode (#9858)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2025-09-16
Source: https://github.com/noir-lang/noir/commit/cff071f622addc873475b2697dd50894df3b1bbe
Type: security-commit

## Details
fix(fuzz): Avoid OOB when `in_no_dynamic` mode (#9858)

## Patch
### compiler/noirc_evaluator/src/ssa/validation/dynamic_array_indices.rs
```diff
@@ -1,7 +1,7 @@
 use crate::{
     errors::{RtResult, RuntimeError},
     ssa::{
-        ir::{function::Function, instruction::Instruction},
+        ir::{dfg::DataFlowGraph, function::Function, instruction::Instruction, value::ValueId},
         ssa_gen::Ssa,
     },
 };
@@ -37,7 +37,7 @@ impl Function {
                         let array_type = self.dfg.type_of_value(*array);
                         let contains_reference = array_type.contains_reference();
 
-                        if contains_reference && self.dfg.get_numeric_constant(*index).is_none() {
+                        if contains_reference && !is_non_dynamic(&self.dfg, *index) {
                             let call_stack = self.dfg.get_instruction_call_stack(*instruction);
                             return Err(RuntimeError::DynamicIndexingWithReference { call_stack });
                         }
@@ -50,6 +50,16 @@ impl Function {
     }
 }
 
+/// Check if an value is a numeric constant, or a result of an instruction that only uses numeric constant inputs.
+fn is_non_dynamic(dfg: &DataFlowGraph, value: ValueId) -> bool {
+    // We could check if a non-constant-numeric value is a result of for example a binary an instruction that only
+    // takes numeric constant input. However, if we have such a value, it might be a result of an overflowing
+    // index expression that we could not simplify at runtime, which means most likely mem2reg could not eliminate
+    // the reference allocation either, so even if we classified such indexes as non-dynamic, since they only use
+    // known constants, we would just get another obscure error down the line with a less obvious call stack.
+    dfg.get_numeric_constant(value).is_some()
+}
+
 #[cfg(test)]
 mod tests {
     use crate::{errors::RuntimeError, ssa::ssa_gen::Ssa};
@@ -104,4 +114,27 @@ mod tests {
         let result = ssa.verify_no_dynamic_indices_to_references();
         assert!(result.is_ok());
     }
+
+    #[test]
+    fn error_on_index_overflow() {
+        // https://github.com/noir-lang/noir/issues/9853
+        // fn main() -> pub bool {
+        //     let mut e: [(&mut Field, bool); 1] = [((&mut -1), false)];
+        //     e[2147483648].1
+        // }
+        let src = r#"
+        acir(inline) predicate_pure fn main f0 {
+          b0():
+            v0 = allocate -> &mut Field
+            v2 = make_array [v0, u1 0] : [(&mut Field, u1); 1]
+            v5 = unchecked_mul u32 2147483648, u32 2
+            v7 = unchecked_add v5, u32 1
+            v8 = array_get v2, index v7 -> u1
+            return v8
+        }"#;
+
+        let ssa = Ssa::from_str(src).unwrap();
+        let result = ssa.verify_no_dynamic_indices_to_references();
+        assert!(matches!(result, Err(RuntimeError::DynamicIndexingWithReference { .. })));
+    }
 }
```

### tooling/ast_fuzzer/src/program/func.rs
```diff
@@ -910,24 +910,6 @@ impl<'a> FunctionContext<'a> {
         let Type::Slice(item_type) = src_type else {
             unreachable!("only expected to be called with Slice");
         };
-        // The rules around dynamic indexing is the same as for arrays.
-        let (mut idx_expr, idx_dyn) = if max_depth == 0 || bool::arbitrary(u)? {
-            // Avoid any stack overflow where we look for an index in the slice itself.
-            (self.gen_literal(u, &types::U32)?, false)
-        } else {
-            let no_dynamic =
-                self.in_no_dynamic || !self.unconstrained() && types::contains_reference(item_type);
-            let was_in_no_dynamic = std::mem::replace(&mut self.in_no_dynamic, no_dynamic);
-
-            // Choose a random index.
-            let (idx_expr, idx_dyn) =
-                self.gen_expr(u, &types::U32, max_depth.saturating_sub(1), Flags::NESTED)?;
-
-            assert!(!(no_dynamic && idx_dyn), "non-dynamic index expected");
-
-            self.in_no_dynamic = was_in_no_dynamic;
-            (idx_expr, idx_dyn)
-        };
 
         // Unless the slice is coming from an identifier or literal, we should create a let binding for it
         // to avoid doubling up any side effects, or double using local variables when it was created.
@@ -951,10 +933,29 @@ impl<'a> FunctionContext<'a> {
         // Get the runtime length.
         let len_expr = self.call_array_len(Expression::Ident(ident_1), src_type.clone());
 
-        // Take the modulo, but leave a small chance for index OOB.
-        if self.avoid_index_out_of_bounds(u)? {
-            idx_expr = expr::modulo(idx_expr, len_expr);
-        }
+        // The rules around dynamic indexing is the same as for arrays.
+        let (idx_expr, idx_dyn) = if max_depth == 0 || bool::arbitrary(u)? {
+            // Avoid any stack overflow where we look for an index in the slice itself.
+            (self.gen_literal(u, &types::U32)?, false)
+        } else {
+            let no_dynamic =
+                self.in_no_dynamic || !self.unconstrained() && types::contains_reference(item_type);
+            let was_in_no_dynamic = std::mem::replace(&mut self.in_no_dynamic, no_dynamic);
+
+            // Choose a random index.
+            let (mut idx_expr, idx_dyn) =
+                self.gen_expr(u, &types::U32, max_depth.saturating_sub(1), Flags::NESTED)?;
+
+            assert!(!(no_dynamic && idx_dyn), "non-dynamic index expected");
+
+            // Take the modulo, but leave a small chance for index OOB.
+            if self.avoid_index_out_of_bounds(u)? {
+                idx_expr = expr::modulo(idx_expr, len_expr);
+            }
+
+            self.in_no_dynamic = was_in_no_dynamic;
+            (idx_expr, idx_dyn)
+        };
 
         // Access the item by index
         let item_expr = access_item(self, ident_2, idx_expr);
@@ -2291,8 +2292,12 @@ impl<'a> FunctionContext<'a> {
     /// on a specific array or slice access operation.
     ///
     /// If [Config::avoid_index_out_of_bounds] is turned on, then this is always `true`.
+    ///
+    /// It also returns `true` when `in_no_dynamic` mode is on, because an overflowing
+    /// index might not be simplified out of the SSA in ACIR, and end up being considered
+    /// a dynamic index, and leave reference allocations until ACIR gen, where they fail.
     fn avoid_index_out_of_bounds(&self, u: &mut Unstructured) -> arbitrary::Result<bool> {
-        if self.config().avoid_index_out_of_bounds {
+        if self.config().avoid_index_out_of_bounds || self.in_no_dynamic {
             return Ok(true);
         }
         // Avoid OOB with 90% chance.
```
