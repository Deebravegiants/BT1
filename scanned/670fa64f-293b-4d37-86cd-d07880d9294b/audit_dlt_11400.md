# [?] Bug: fix to handle `destination` overflow in `ErrorInvalidJumpGadget` (#1258)

## Summary
Severity: Unknown
Chain: ZK
Component: privacy-ethereum/zkevm-circuits
Published: 2023-02-28
Source: https://github.com/privacy-ethereum/zkevm-circuits/commit/7f6a0c436fc29d13dc6dfc582d5742543ffe4613
Type: security-commit

## Details
Bug: fix to handle `destination` overflow in `ErrorInvalidJumpGadget` (#1258)

### Description

Reference go-ethereum function
[opJump](https://github.com/ethereum/go-ethereum/blob/master/core/vm/instructions.go#L538
) and
[validJumpdest](https://github.com/ethereum/go-ethereum/blob/master/core/vm/contract.go#L86),
try to handle `destination` overflow in `ErrorInvalidJumpGadget`.

### Issue Link

Close
https://github.com/privacy-scaling-explorations/zkevm-circuits/issues/1257

### Type of change

- [X] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing
functionality to not work as expected)
- [ ] This change requires a documentation update

### How Has This Been Tested?

Add a new test case `invalid_jump_dest_overflow`.

## Patch
### bus-mapping/src/evm/opcodes/error_invalid_jump.rs
```diff
@@ -1,7 +1,7 @@
 use crate::circuit_input_builder::{CircuitInputStateRef, ExecStep};
 use crate::evm::{Opcode, OpcodeId};
 use crate::Error;
-use eth_types::{GethExecStep, ToAddress, ToWord, Word};
+use eth_types::{GethExecStep, Word};
 
 #[derive(Debug, Copy, Clone)]
 pub(crate) struct InvalidJump;
@@ -22,15 +22,14 @@ impl Opcode for InvalidJump {
         // assert op code can only be JUMP or JUMPI
         assert!(geth_step.op == OpcodeId::JUMP || geth_step.op == OpcodeId::JUMPI);
         let is_jumpi = geth_step.op == OpcodeId::JUMPI;
-        let dest = geth_steps[0].stack.last()?.to_address();
         let mut condition: Word = Word::zero();
         if is_jumpi {
             condition = geth_step.stack.nth_last(1)?;
         }
         state.stack_read(
             &mut exec_step,
             geth_step.stack.last_filled(),
-            dest.to_word(),
+            geth_step.stack.last()?,
         )?;
         if is_jumpi {
             state.stack_read(
```

### zkevm-circuits/src/evm_circuit/execution/error_invalid_jump.rs
```diff
@@ -4,28 +4,30 @@ use crate::{
         param::N_BYTES_PROGRAM_COUNTER,
         step::ExecutionState,
         util::{
+            and,
             common_gadget::CommonErrorGadget,
             constraint_builder::ConstraintBuilder,
             from_bytes,
             math_gadget::{IsEqualGadget, IsZeroGadget, LtGadget},
-            CachedRegion, Cell, RandomLinearCombination,
+            select, sum, CachedRegion, Cell, Word,
         },
         witness::{Block, Call, ExecStep, Transaction},
     },
     util::Expr,
 };
-use eth_types::{evm_types::OpcodeId, Field, ToLittleEndian, Word};
+use eth_types::{evm_types::OpcodeId, Field, ToLittleEndian, U256};
 
 use halo2_proofs::{circuit::Value, plonk::Error};
 
 #[derive(Clone, Debug)]
 pub(crate) struct ErrorInvalidJumpGadget<F> {
     opcode: Cell<F>,
-    destination: RandomLinearCombination<F, N_BYTES_PROGRAM_COUNTER>,
-    code_length: Cell<F>,
+    dest_word: Word<F>,
+    code_len: Cell<F>,
     value: Cell<F>,
     is_code: Cell<F>,
-    within_range: LtGadget<F, N_BYTES_PROGRAM_COUNTER>,
+    dest_not_overflow: IsZeroGadget<F>,
+    dest_lt_code_len: LtGadget<F, N_BYTES_PROGRAM_COUNTER>,
     is_jump_dest: IsEqualGadget<F>,
     is_jumpi: IsEqualGadget<F>,
     phase2_condition: Cell<F>,
@@ -39,7 +41,15 @@ impl<F: Field> ExecutionGadget<F> for ErrorInvalidJumpGadget<F> {
     const EXECUTION_STATE: ExecutionState = ExecutionState::ErrorInvalidJump;
 
     fn configure(cb: &mut ConstraintBuilder<F>) -> Self {
-        let destination = cb.query_word_rlc();
+        let dest_word = cb.query_word_rlc();
+        let dest_not_overflow =
+            IsZeroGadget::construct(cb, sum::expr(&dest_word.cells[N_BYTES_PROGRAM_COUNTER..]));
+        let dest = select::expr(
+            dest_not_overflow.expr(),
+            from_bytes::expr(&dest_word.cells[..N_BYTES_PROGRAM_COUNTER]),
+            u64::MAX.expr(),
+        );
+
         let opcode = cb.query_cell();
         let value = cb.query_cell();
         let is_code = cb.query_cell();
@@ -61,44 +71,48 @@ impl<F: Field> ExecutionGadget<F> for ErrorInvalidJumpGadget<F> {
         let is_condition_zero = IsZeroGadget::construct(cb, phase2_condition.expr());
 
         // Pop the value from the stack
-        cb.stack_pop(destination.expr());
+        cb.stack_pop(dest_word.expr());
 
         cb.condition(is_jumpi.expr(), |cb| {
             cb.stack_pop(phase2_condition.expr());
             // if condition is zero, jump will not happen, so constrain condition not zero
             cb.require_zero("condition is not zero", is_condition_zero.expr());
         });
 
-        // look up bytecode length
-        let code_length = cb.query_cell();
-        cb.bytecode_length(cb.curr.state.code_hash.expr(), code_length.expr());
-        let dest_value = from_bytes::expr(&destination.cells);
-
-        let within_range = LtGadget::construct(cb, dest_value.expr(), code_length.expr());
-        //if not out of range, check `dest` is invalid
-        cb.condition(within_range.expr(), |cb| {
-            // if not out of range, Lookup real value
-            cb.bytecode_lookup(
-                cb.curr.state.code_hash.expr(),
-                dest_value.clone(),
-                is_code.expr(),
-                value.expr(),
-            );
-            cb.require_zero(
-                "is_code is false or not JUMPDEST",
-                is_code.expr() * is_jump_dest.expr(),
-            );
-        });
+        // Look up bytecode length
+        let code_len = cb.query_cell();
+        cb.bytecode_length(cb.curr.state.code_hash.expr(), code_len.expr());
+
+        let dest_lt_code_len = LtGadget::construct(cb, dest.expr(), code_len.expr());
+
+        // If destination is in valid range, lookup for the value.
+        cb.condition(
+            and::expr([dest_not_overflow.expr(), dest_lt_code_len.expr()]),
+            |cb| {
+                cb.bytecode_lookup(
+                    cb.curr.state.code_hash.expr(),
+                    dest.expr(),
+                    is_code.expr(),
+                    value.expr(),
+                );
+                cb.require_zero(
+                    "is_code is false or not JUMPDEST",
+                    is_code.expr() * is_jump_dest.expr(),
+                );
+            },
+        );
 
         let common_error_gadget =
             CommonErrorGadget::construct(cb, opcode.expr(), 3.expr() + is_jumpi.expr());
+
         Self {
             opcode,
-            destination,
-            code_length,
+            dest_word,
+            code_len,
             value,
             is_code,
-            within_range,
+            dest_not_overflow,
+            dest_lt_code_len,
             is_jump_dest,
             is_jumpi,
             phase2_condition,
@@ -118,39 +132,45 @@ impl<F: Field> ExecutionGadget<F> for ErrorInvalidJumpGadget<F> {
     ) -> Result<(), Error> {
         let opcode = step.opcode.unwrap();
         let is_jumpi = opcode == OpcodeId::JUMPI;
-
         self.opcode
             .assign(region, offset, Value::known(F::from(opcode.as_u64())))?;
-        let destination = block.rws[step.rw_indices[0]].stack_value();
+
+        let dest = block.rws[step.rw_indices[0]].stack_value();
+        self.dest_word
+            .assign(region, offset, Some(dest.to_le_bytes()))?;
+
         let condition = if is_jumpi {
             block.rws[step.rw_indices[1]].stack_value()
         } else {
-            Word::zero()
+            U256::zero()
         };
         let condition_rlc = region.word_rlc(condition);
-        self.destination.assign(
-            region,
-            offset,
-            Some(
-                destination.to_le_bytes()[..N_BYTES_PROGRAM_COUNTER]
-                    .try_into()
-                    .unwrap(),
-            ),
-        )?;
 
         let code = block
             .bytecodes
             .get(&call.code_hash)
             .expect("could not find current environment's bytecode");
-        let code_length = code.bytes.len() as u64;
-        self.code_length
-            .assign(region, offset, Value::known(F::from(code_length)))?;
+        let code_len = code.bytes.len() as u64;
+        self.code_len
+            .assign(region, offset, Value::known(F::from(code_len)))?;
+
+        let dest_overflow_hi = dest.to_le_bytes()[N_BYTES_PROGRAM_COUNTER..]
+            .iter()
+            .fold(0, |acc, val| acc + u64::from(*val));
+        self.dest_not_overflow
+            .assign(region, offset, F::from(dest_overflow_hi))?;
+
+        let dest = if dest_overflow_hi == 0 {
+            dest.low_u64()
+        } else {
+            u64::MAX
+        };
 
         // set default value in case can not find value, is_code from bytecode table
         let mut code_pair = [0u8, 0u8];
-        if destination.as_u64() < code_length {
+        if dest < code_len {
             // get real value from bytecode table
-            code_pair = code.get(destination.as_usize());
+            code_pair = code.get(dest as usize);
         }
 
         self.value
@@ -164,12 +184,8 @@ impl<F: Field> ExecutionGadget<F> for ErrorInvalidJumpGadget<F> {
             F::from(OpcodeId::JUMPDEST.as_u64()),
         )?;
 
-        self.within_range.assign(
-            region,
-            offset,
-            F::from(destination.as_u64()),
-            F::from(code_length),
-        )?;
+        self.dest_lt_code_len
+            .assign(region, offset, F::from(dest), F::from(code_len))?;
 
         self.is_jumpi.assign(
             region,
@@ -246,6 +262,19 @@ mod test {
         test_internal_jump_error(true);
     }
 
+    #[test]
+    fn invalid_jump_dest_overflow() {
+        let bytecode = bytecode! {
+            PUSH32(Word::MAX)
+            JUMP
+        };
+
+        CircuitTestBuilder::new_from_test_ctx(
+            TestContext::<2, 1>::simple_ctx_with_bytecode(bytecode).unwrap(),
+        )
+        .run();
+    }
+
     // internal call test
     struct Stack {
         gas: u64,
```
