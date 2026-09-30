# [?] Fix successful run case of `JUMPI` with zero `condition` and overflow `destination`. (#382)

## Summary
Severity: Unknown
Chain: ZK
Component: scroll-tech/zkevm-circuits
Published: 2023-03-08
Source: https://github.com/scroll-tech/zkevm-circuits/commit/3ebd844a859e23ffa9ee31ab9c289d1dac534462
Type: security-commit

## Details
Fix successful run case of `JUMPI` with zero `condition` and overflow `destination`. (#382)

## Patch
### .cargo/config.toml
```diff
@@ -2,3 +2,5 @@
 rustflags = ["-C", "link-args=-framework CoreFoundation -framework Security"]
 [net]
 git-fetch-with-cli = true
+[env]
+RUST_MIN_STACK = "16777216"
```

### zkevm-circuits/src/evm_circuit/execution/error_invalid_jump.rs
```diff
@@ -5,28 +5,26 @@ use crate::{
         step::ExecutionState,
         util::{
             and,
-            common_gadget::CommonErrorGadget,
+            common_gadget::{CommonErrorGadget, WordRangeGadget},
             constraint_builder::ConstraintBuilder,
-            from_bytes,
             math_gadget::{IsEqualGadget, IsZeroGadget, LtGadget},
-            select, sum, CachedRegion, Cell, Word,
+            select, CachedRegion, Cell,
         },
         witness::{Block, Call, ExecStep, Transaction},
     },
     util::Expr,
 };
-use eth_types::{evm_types::OpcodeId, Field, ToLittleEndian, U256};
+use eth_types::{evm_types::OpcodeId, Field, U256};
 
 use halo2_proofs::{circuit::Value, plonk::Error};
 
 #[derive(Clone, Debug)]
 pub(crate) struct ErrorInvalidJumpGadget<F> {
     opcode: Cell<F>,
-    dest_word: Word<F>,
+    dest_word: WordRangeGadget<F>,
     code_len: Cell<F>,
     value: Cell<F>,
     is_code: Cell<F>,
-    dest_not_overflow: IsZeroGadget<F>,
     dest_lt_code_len: LtGadget<F, N_BYTES_PROGRAM_COUNTER>,
     is_jump_dest: IsEqualGadget<F>,
     is_jumpi: IsEqualGadget<F>,
@@ -41,12 +39,10 @@ impl<F: Field> ExecutionGadget<F> for ErrorInvalidJumpGadget<F> {
     const EXECUTION_STATE: ExecutionState = ExecutionState::ErrorInvalidJump;
 
     fn configure(cb: &mut ConstraintBuilder<F>) -> Self {
-        let dest_word = cb.query_word_rlc();
-        let dest_not_overflow =
-            IsZeroGadget::construct(cb, sum::expr(&dest_word.cells[N_BYTES_PROGRAM_COUNTER..]));
+        let dest_word = WordRangeGadget::construct(cb, N_BYTES_PROGRAM_COUNTER);
         let dest = select::expr(
-            dest_not_overflow.expr(),
-            from_bytes::expr(&dest_word.cells[..N_BYTES_PROGRAM_COUNTER]),
+            dest_word.within_range_expr(),
+            dest_word.valid_value_expr(N_BYTES_PROGRAM_COUNTER),
             u64::MAX.expr(),
         );
 
@@ -71,7 +67,7 @@ impl<F: Field> ExecutionGadget<F> for ErrorInvalidJumpGadget<F> {
         let is_condition_zero = IsZeroGadget::construct(cb, phase2_condition.expr());
 
         // Pop the value from the stack
-        cb.stack_pop(dest_word.expr());
+        cb.stack_pop(dest_word.original_word_expr());
 
         cb.condition(is_jumpi.expr(), |cb| {
             cb.stack_pop(phase2_condition.expr());
@@ -87,7 +83,7 @@ impl<F: Field> ExecutionGadget<F> for ErrorInvalidJumpGadget<F> {
 
         // If destination is in valid range, lookup for the value.
         cb.condition(
-            and::expr([dest_not_overflow.expr(), dest_lt_code_len.expr()]),
+            and::expr([dest_word.within_range_expr(), dest_lt_code_len.expr()]),
             |cb| {
                 cb.bytecode_lookup(
                     cb.curr.state.code_hash.expr(),
@@ -111,7 +107,6 @@ impl<F: Field> ExecutionGadget<F> for ErrorInvalidJumpGadget<F> {
             code_len,
             value,
             is_code,
-            dest_not_overflow,
             dest_lt_code_len,
             is_jump_dest,
             is_jumpi,
@@ -136,8 +131,9 @@ impl<F: Field> ExecutionGadget<F> for ErrorInvalidJumpGadget<F> {
             .assign(region, offset, Value::known(F::from(opcode.as_u64())))?;
 
         let dest = block.rws[step.rw_indices[0]].stack_value();
-        self.dest_word
-            .assign(region, offset, Some(dest.to_le_bytes()))?;
+        let dest_within_range =
+            self.dest_word
+                .assign(region, offset, N_BYTES_PROGRAM_COUNTER, dest)?;
 
         let condition = if is_jumpi {
             block.rws[step.rw_indices[1]].stack_value()
@@ -154,14 +150,8 @@ impl<F: Field> ExecutionGadget<F> for ErrorInvalidJumpGadget<F> {
         self.code_len
             .assign(region, offset, Value::known(F::from(code_len)))?;
 
-        let dest_overflow_hi = dest.to_le_bytes()[N_BYTES_PROGRAM_COUNTER..]
-            .iter()
-            .fold(0, |acc, val| acc + u64::from(*val));
-        self.dest_not_overflow
-            .assign(region, offset, F::from(dest_overflow_hi))?;
-
-        let dest = if dest_overflow_hi == 0 {
-            dest.low_u64()
+        let dest = if dest_within_range {
+            dest.as_u64()
         } else {
             u64::MAX
         };
```

### zkevm-circuits/src/evm_circuit/execution/jumpi.rs
```diff
@@ -4,26 +4,25 @@ use crate::{
         param::N_BYTES_PROGRAM_COUNTER,
         step::ExecutionState,
         util::{
-            common_gadget::SameContextGadget,
+            common_gadget::{SameContextGadget, WordRangeGadget},
             constraint_builder::{
                 ConstraintBuilder, StepStateTransition,
                 Transition::{Delta, To},
             },
-            from_bytes,
             math_gadget::IsZeroGadget,
-            select, CachedRegion, Cell, RandomLinearCombination,
+            select, CachedRegion, Cell,
         },
         witness::{Block, Call, ExecStep, Transaction},
     },
     util::Expr,
 };
-use eth_types::{evm_types::OpcodeId, Field, ToLittleEndian};
+use eth_types::{evm_types::OpcodeId, Field};
 use halo2_proofs::plonk::Error;
 
 #[derive(Clone, Debug)]
 pub(crate) struct JumpiGadget<F> {
     same_context: SameContextGadget<F>,
-    destination: RandomLinearCombination<F, N_BYTES_PROGRAM_COUNTER>,
+    dest_word: WordRangeGadget<F>,
     phase2_condition: Cell<F>,
     is_condition_zero: IsZeroGadget<F>,
 }
@@ -34,11 +33,11 @@ impl<F: Field> ExecutionGadget<F> for JumpiGadget<F> {
     const EXECUTION_STATE: ExecutionState = ExecutionState::JUMPI;
 
     fn configure(cb: &mut ConstraintBuilder<F>) -> Self {
-        let destination = cb.query_word_rlc();
+        let dest_word = WordRangeGadget::construct(cb, N_BYTES_PROGRAM_COUNTER);
         let phase2_condition = cb.query_cell_phase2();
 
         // Pop the value from the stack
-        cb.stack_pop(destination.expr());
+        cb.stack_pop(dest_word.original_word_expr());
         cb.stack_pop(phase2_condition.expr());
 
         // Determine if the jump condition is met
@@ -47,8 +46,14 @@ impl<F: Field> ExecutionGadget<F> for JumpiGadget<F> {
 
         // Lookup opcode at destination when should_jump
         cb.condition(should_jump.clone(), |cb| {
+            cb.require_equal(
+                "JUMPI destination must be within range if condition is non-zero",
+                dest_word.within_range_expr(),
+                1.expr(),
+            );
+
             cb.opcode_lookup_at(
-                from_bytes::expr(&destination.cells),
+                dest_word.valid_value_expr(N_BYTES_PROGRAM_COUNTER),
                 OpcodeId::JUMPDEST.expr(),
                 1.expr(),
             );
@@ -58,7 +63,7 @@ impl<F: Field> ExecutionGadget<F> for JumpiGadget<F> {
         // delta 1.
         let next_program_counter = select::expr(
             should_jump,
-            from_bytes::expr(&destination.cells),
+            dest_word.valid_value_expr(N_BYTES_PROGRAM_COUNTER),
             cb.curr.state.program_counter.expr() + 1.expr(),
         );
 
@@ -75,7 +80,7 @@ impl<F: Field> ExecutionGadget<F> for JumpiGadget<F> {
 
         Self {
             same_context,
-            destination,
+            dest_word,
             phase2_condition,
             is_condition_zero,
         }
@@ -96,15 +101,8 @@ impl<F: Field> ExecutionGadget<F> for JumpiGadget<F> {
             [step.rw_indices[0], step.rw_indices[1]].map(|idx| block.rws[idx].stack_value());
         let condition = region.word_rlc(condition);
 
-        self.destination.assign(
-            region,
-            offset,
-            Some(
-                destination.to_le_bytes()[..N_BYTES_PROGRAM_COUNTER]
-                    .try_into()
-                    .unwrap(),
-            ),
-        )?;
+        self.dest_word
+            .assign(region, offset, N_BYTES_PROGRAM_COUNTER, destination)?;
         self.phase2_condition.assign(region, offset, condition)?;
         self.is_condition_zero
             .assign_value(region, offset, condition)?;
@@ -174,4 +172,18 @@ mod test {
         test_ok(rand_range(1 << 11..0x5fff), Word::zero());
         test_ok(rand_range(1 << 11..0x5fff), rand_word());
     }
+
+    #[test]
+    fn jumpi_gadget_with_zero_cond_and_overflow_dest() {
+        let bytecode = bytecode! {
+            PUSH32(Word::MAX)
+            PUSH32(Word::zero())
+            JUMPI
+        };
+
+        CircuitTestBuilder::new_from_test_ctx(
+            TestContext::<2, 1>::simple_ctx_with_bytecode(bytecode).unwrap(),
+        )
+        .run();
+    }
 }
```
