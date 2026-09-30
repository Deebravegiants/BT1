# [?] Fix overflow cases of `ErrorReturnDataOutOfBound` (#1321)

## Summary
Severity: Unknown
Chain: ZK
Component: privacy-ethereum/zkevm-circuits
Published: 2023-03-15
Source: https://github.com/privacy-ethereum/zkevm-circuits/commit/2a1074a6aaed02f9774834c63bd7da60d4de2cd7
Type: security-commit

## Details
Fix overflow cases of `ErrorReturnDataOutOfBound` (#1321)

### Description

Fix overflow cases of `ErrorReturnDataOutOfBound` state. Found by
`testool` cases (`bufferSrcOffset_d108(fail)_g0_v0`).

### Type of change

- [X] Bug fix (non-breaking change which fixes an issue)

### How Has This Been Tested?

Refactor unit-test cases of `ErrorReturnDataOutOfBound` to 4 categories:
- data_offset > u64::MAX
- data_offset + size > U256::MAX
- data_offset + size (mod U256) > u64::MAX
- data_offset + size > return_data_length

## Patch
### bus-mapping/src/evm/opcodes/error_return_data_outofbound.rs
```diff
@@ -51,14 +51,15 @@ impl Opcode for ErrorReturnDataOutOfBound {
             "callee return data size should be correct"
         );
 
-        let end = data_offset + length;
+        let remainder_end = data_offset.overflowing_add(length).0;
         // check data_offset or end is u64 overflow, or
-        // last_callee_return_data_length < end
+        // last_callee_return_data_length < reaminder_end
         let data_offset_overflow = data_offset > Word::from(u64::MAX);
-        let end_overflow = end > Word::from(u64::MAX);
-        let end_exceed_length = Word::from(last_callee_return_data_length) < end;
+        let remainder_end_overflow = remainder_end > Word::from(u64::MAX);
+        let remainder_end_exceed_length =
+            Word::from(last_callee_return_data_length) < remainder_end;
         // one of three must hold at least one.
-        assert!(data_offset_overflow | end_overflow | end_exceed_length);
+        assert!(data_offset_overflow | remainder_end_overflow | remainder_end_exceed_length);
         // read last callee info
         state.call_context_read(
             &mut exec_step,
```

### zkevm-circuits/src/evm_circuit/execution/error_return_data_oo_bound.rs
```diff
@@ -8,30 +8,28 @@ use crate::{
             constraint_builder::ConstraintBuilder,
             from_bytes,
             math_gadget::{AddWordsGadget, IsZeroGadget, LtGadget},
-            not, CachedRegion, Cell,
+            not, or, sum, CachedRegion, Cell,
         },
         witness::{Block, Call, ExecStep, Transaction},
     },
     table::CallContextFieldTag,
     util::Expr,
 };
-use eth_types::{evm_types::OpcodeId, Field, ToScalar, U256};
-
+use eth_types::{evm_types::OpcodeId, Field, ToLittleEndian, ToScalar};
 use halo2_proofs::{circuit::Value, plonk::Error};
 
 #[derive(Clone, Debug)]
 pub(crate) struct ErrorReturnDataOutOfBoundGadget<F> {
     opcode: Cell<F>,
     memory_offset: Cell<F>,
-    sum: AddWordsGadget<F, 2, true>,
-    /// Holds the size of the last callee return data.
+    sum: AddWordsGadget<F, 2, false>,
+    // Hold the size of the last callee return data.
     return_data_length: Cell<F>,
-
-    is_data_offset_within_range: IsZeroGadget<F>,
-    // end = data_offset + length
-    is_end_within_range: IsZeroGadget<F>,
-    // when `end` not overflow, check if it exceeds return data size.
-    is_end_exceed_length: LtGadget<F, N_BYTES_U64>,
+    is_data_offset_within_u64: IsZeroGadget<F>,
+    // remainder_end = (data_offset + size) mod U256
+    is_remainder_end_within_u64: IsZeroGadget<F>,
+    // when remainder end is within Uint64, check if it exceeds return data size.
+    is_remainder_end_exceed_len: LtGadget<F, N_BYTES_U64>,
     common_error_gadget: CommonErrorGadget<F>,
 }
 
@@ -44,9 +42,8 @@ impl<F: Field> ExecutionGadget<F> for ErrorReturnDataOutOfBoundGadget<F> {
         let opcode = cb.query_cell();
         let memory_offset = cb.query_cell();
         let data_offset = cb.query_word_rlc();
-        let length = cb.query_word_rlc();
-        let end = cb.query_word_rlc();
-
+        let size = cb.query_word_rlc();
+        let remainder_end = cb.query_word_rlc();
         let return_data_length = cb.query_cell();
 
         cb.require_equal(
@@ -55,52 +52,62 @@ impl<F: Field> ExecutionGadget<F> for ErrorReturnDataOutOfBoundGadget<F> {
             OpcodeId::RETURNDATACOPY.expr(),
         );
 
-        // Pop memory_offset, offset, length from stack
+        // Pop memory_offset, offset, size from stack
         cb.stack_pop(memory_offset.expr());
         cb.stack_pop(data_offset.expr());
-        cb.stack_pop(length.expr());
+        cb.stack_pop(size.expr());
 
-        // read last callee return data length
+        // Read last callee return data length
         cb.call_context_lookup(
             false.expr(),
             None,
             CallContextFieldTag::LastCalleeReturnDataLength,
             return_data_length.expr(),
         );
 
-        // check `data_offset` u64 overflow
-        let data_offset_larger_u64 = from_bytes::expr(&data_offset.cells[8..]);
-        let is_data_offset_within_range = IsZeroGadget::construct(cb, data_offset_larger_u64);
+        // Check if `data_offset` is Uint64 overflow.
+        let data_offset_larger_u64 = sum::expr(&data_offset.cells[N_BYTES_U64..]);
+        let is_data_offset_within_u64 = IsZeroGadget::construct(cb, data_offset_larger_u64);
 
-        // check if `end` u64  overflow or not.
-        let sum = AddWordsGadget::construct(cb, [data_offset, length], end.clone());
+        // Check if `remainder_end` is Uint64 overflow.
+        let sum = AddWordsGadget::construct(cb, [data_offset, size], remainder_end.clone());
+        let is_end_u256_overflow = sum.carry().as_ref().unwrap();
 
-        let end_larger_u64 = from_bytes::expr(&end.cells[8..]);
-        let is_end_within_range = IsZeroGadget::construct(cb, end_larger_u64);
+        let remainder_end_larger_u64 = sum::expr(&remainder_end.cells[N_BYTES_U64..]);
+        let is_remainder_end_within_u64 = IsZeroGadget::construct(cb, remainder_end_larger_u64);
 
-        // check if `end` exceeds return data length
-        let is_end_exceed_length = LtGadget::construct(
+        // check if `remainder_end` exceeds return data length.
+        let is_remainder_end_exceed_len = LtGadget::construct(
             cb,
             return_data_length.expr(),
-            from_bytes::expr(&end.cells[..N_BYTES_U64]),
+            from_bytes::expr(&remainder_end.cells[..N_BYTES_U64]),
         );
-        // Any of [offset_out_of_range, end_out_of_range, end_exceed_length] occurs.
-        cb.require_in_set(
-            "Any of [offset_out_of_range, end_out_of_range, end_exceed_length] occurs",
-            not::expr(is_data_offset_within_range.expr())
-                + not::expr(is_end_within_range.expr())
-                + is_end_exceed_length.expr(),
-            vec![1.expr(), 2.expr(), 3.expr()],
+
+        // Need to check if `data_offset + size` is U256 overflow via `AddWordsGadget` carry. If
+        // yes, it should be also an error of return data out of bound.
+        cb.require_equal(
+            "Any of [data_offset > u64::MAX, data_offset + size > U256::MAX, remainder_end > u64::MAX, remainder_end > return_data_length] occurs",
+            or::expr([
+                // data_offset > u64::MAX
+                not::expr(is_data_offset_within_u64.expr()),
+                // data_offset + size > U256::MAX
+                is_end_u256_overflow.expr(),
+                // remainder_end > u64::MAX
+                not::expr(is_remainder_end_within_u64.expr()),
+                // remainder_end > return_data_length
+                is_remainder_end_exceed_len.expr(),
+            ]),
+            1.expr(),
         );
 
         let common_error_gadget = CommonErrorGadget::construct(cb, opcode.expr(), 6.expr());
 
         Self {
             opcode,
             memory_offset,
-            is_data_offset_within_range,
-            is_end_within_range,
-            is_end_exceed_length,
+            is_data_offset_within_u64,
+            is_remainder_end_within_u64,
+            is_remainder_end_exceed_len,
             sum,
             return_data_length,
             common_error_gadget,
@@ -127,9 +134,10 @@ impl<F: Field> ExecutionGadget<F> for ErrorReturnDataOutOfBoundGadget<F> {
         self.memory_offset
             .assign(region, offset, Value::known(F::from(dest_offset.as_u64())))?;
 
-        let end = data_offset + size;
+        let remainder_end = data_offset.overflowing_add(size).0;
+        self.sum
+            .assign(region, offset, [data_offset, size], remainder_end)?;
 
-        self.sum.assign(region, offset, [data_offset, size], end)?;
         let return_data_length = block.rws[step.rw_indices[3]].call_context_value();
         self.return_data_length.assign(
             region,
@@ -141,24 +149,27 @@ impl<F: Field> ExecutionGadget<F> for ErrorReturnDataOutOfBoundGadget<F> {
             ),
         )?;
 
-        // when u64::MAX < data_offset = true, not within u64 range.
-        let data_offset_overflow = U256::from(u64::MAX) < data_offset;
-        self.is_data_offset_within_range.assign(
-            region,
-            offset,
-            F::from(data_offset_overflow as u64),
-        )?;
-        // check `end` if u64 overflow.
-        let end_overflow = U256::from(u64::MAX) < end;
+        let data_offset_overflow = data_offset.to_le_bytes()[N_BYTES_U64..]
+            .iter()
+            .fold(0, |acc, val| acc + u64::from(*val));
+        self.is_data_offset_within_u64
+            .assign(region, offset, F::from(data_offset_overflow))?;
 
-        self.is_end_within_range
-            .assign(region, offset, F::from(end_overflow as u64))?;
+        let remainder_end_overflow = remainder_end.to_le_bytes()[N_BYTES_U64..]
+            .iter()
+            .fold(0, |acc, val| acc + u64::from(*val));
+        self.is_remainder_end_within_u64
+            .assign(region, offset, F::from(remainder_end_overflow))?;
 
         // check if it exceeds last callee return data length
-        let end_u64 = end.low_u64();
+        let remainder_end_u64 = remainder_end.low_u64();
         let return_length = return_data_length.to_scalar().unwrap();
-        self.is_end_exceed_length
-            .assign(region, offset, return_length, F::from(end_u64))?;
+        self.is_remainder_end_exceed_len.assign(
+            region,
+            offset,
+            return_length,
+            F::from(remainder_end_u64),
+        )?;
 
         self.common_error_gadget
             .assign(region, offset, block, call, step, 6)?;
@@ -176,7 +187,7 @@ mod test {
         return_data_offset: usize,
         return_data_size: usize,
         dest_offset: usize,
-        offset: u128,
+        offset: Word,
         size: usize,
         is_root: bool,
     ) {
@@ -260,18 +271,31 @@ mod test {
         CircuitTestBuilder::new_from_test_ctx(ctx).run();
     }
 
-    // test root & internal calls
+    // data_offset > u64::MAX
+    #[test]
+    fn test_return_data_oo_bound_data_offset_overflow() {
+        test_ok(0, 0x10, 0x20, Word::from(u64::MAX) + 1, 0x10, false);
+        test_ok(0, 0x10, 0x20, Word::MAX, 0, true);
+    }
+
+    // data_offset + size > U256::MAX
+    #[test]
+    fn test_return_data_oo_bound_data_offset_plus_size_word_overflow() {
+        test_ok(0, 0x10, 0x20, Word::MAX, 1, false);
+        test_ok(0, 0x10, 0x20, Word::MAX - 1000, 1001, true);
+    }
+
+    // data_offset + size > u64::MAX
+    #[test]
+    fn test_return_data_oo_bound_data_offset_plus_size_u64_overflow() {
+        test_ok(0, 0x10, 0x20, Word::from(u64::MAX), 1, false);
+        test_ok(0, 0x10, 0x20, Word::from(u64::MAX) - 100, 101, true);
+    }
+
+    // data_offset + size > return_data_length
     #[test]
-    fn returndatacopy_out_of_bound_error() {
-        // test root call cases: `end` exceed return data size
-        test_ok(0x00, 0x10, 0x20, 0x10, 0x10, true);
-        // test root call case: `end` exceed return data size
-        test_ok(0x00, 0x10, 0x20, 0x10, 0x10, true);
-        // test data offset u64 overflow
-        test_ok(0x00, 0x10, 0x20, u128::from(u64::MAX) + 1, 0x10, false);
-        // test end = data offset + length(size) overflow
-        test_ok(0x00, 0x10, 0x20, 0x1, 0x10, false);
-        // test end overflow with end > 0xff
-        test_ok(0x00, 0x10, 0x20, 0x1, 0xff, false);
+    fn test_return_data_oo_bound_exceed_return_data_length() {
+        test_ok(0, 0x10, 0x20, 0x10.into(), 0x10, false);
+        test_ok(0, 0x10, 0x20, 1.into(), 0xff, true);
     }
 }
```
