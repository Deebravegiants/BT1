# [?] fix(debug): Fix RC underflow check (#7849)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2025-04-01
Source: https://github.com/noir-lang/noir/commit/f1afc0702c16f8b1770744c8ccaaae54f90656f2
Type: security-commit

## Details
fix(debug): Fix RC underflow check (#7849)

## Patch
### EXTERNAL_NOIR_LIBRARIES.yml
```diff
@@ -10,7 +10,7 @@ libraries:
     critical: true
   eddsa:
     repo: noir-lang/eddsa
-    timeout: 2
+    timeout: 3
     critical: true
   mimc:
     repo: noir-lang/mimc
```

### compiler/noirc_evaluator/src/brillig/brillig_gen/brillig_block.rs
```diff
@@ -881,6 +881,12 @@ impl<'block, Registers: RegisterAllocator> BrilligBlock<'block, Registers> {
                 // RC is always directly pointed by the array/vector pointer
                 self.brillig_context
                     .load_instruction(rc_register, array_or_vector.extract_register());
+
+                // Ensure we're not incrementing from 0 back to 1
+                if self.brillig_context.enable_debug_assertions() {
+                    self.assert_rc_neq_zero(rc_register);
+                }
+
                 self.brillig_context.codegen_usize_op_in_place(
                     rc_register,
                     BrilligBinaryOp::Add,
@@ -901,20 +907,7 @@ impl<'block, Registers: RegisterAllocator> BrilligBlock<'block, Registers> {
                 // and become usize::MAX, and then return to 1, then it will indicate
                 // an array as mutable when it probably shouldn't be.
                 if self.brillig_context.enable_debug_assertions() {
-                    let min_addr = ReservedRegisters::usize_one();
-                    let condition =
-                        SingleAddrVariable::new(self.brillig_context.allocate_register(), 1);
-                    self.brillig_context.memory_op_instruction(
-                        min_addr,
-                        rc_register,
-                        condition.address,
-                        BrilligBinaryOp::LessThan,
-                    );
-                    self.brillig_context.codegen_constrain(
-                        condition,
-                        Some("array ref-count underflow detected".to_owned()),
-                    );
-                    self.brillig_context.deallocate_single_addr(condition);
+                    self.assert_rc_neq_zero(rc_register);
                 }
 
                 self.brillig_context.codegen_usize_op_in_place(
@@ -1049,6 +1042,25 @@ impl<'block, Registers: RegisterAllocator> BrilligBlock<'block, Registers> {
         self.brillig_context.set_call_stack(CallStack::new());
     }
 
+    fn assert_rc_neq_zero(&mut self, rc_register: MemoryAddress) {
+        let zero = SingleAddrVariable::new(self.brillig_context.allocate_register(), 32);
+
+        self.brillig_context.const_instruction(zero, FieldElement::zero());
+
+        let condition = SingleAddrVariable::new(self.brillig_context.allocate_register(), 1);
+
+        self.brillig_context.memory_op_instruction(
+            zero.address,
+            rc_register,
+            condition.address,
+            BrilligBinaryOp::Equals,
+        );
+        self.brillig_context.not_instruction(condition, condition);
+        self.brillig_context
+            .codegen_constrain(condition, Some("array ref-count underflow detected".to_owned()));
+        self.brillig_context.deallocate_single_addr(condition);
+    }
+
     fn convert_ssa_function_call(
         &mut self,
         func_id: FunctionId,
```
