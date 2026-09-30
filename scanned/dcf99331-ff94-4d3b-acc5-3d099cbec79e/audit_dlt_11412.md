# [?] Bug: fix to handle successful run when Uint64 overflow in `BLOCKHASH`, `CALLDATACOPY`, `CALLDATALOAD`, `CODECOPY` and `EXTCODECOPY` (#370)

## Summary
Severity: Unknown
Chain: ZK
Component: scroll-tech/zkevm-circuits
Published: 2023-03-07
Source: https://github.com/scroll-tech/zkevm-circuits/commit/bb216662f6e3de16bb5d0bd7727febd6419adca2
Type: security-commit

## Details
Bug: fix to handle successful run when Uint64 overflow in `BLOCKHASH`, `CALLDATACOPY`, `CALLDATALOAD`, `CODECOPY` and `EXTCODECOPY` (#370)

* Fix to handle data offset Uint64 overflow of `CALLDATACOPY`.

* Fix to handle block number Uint64 overflow of `BLOCKHASH`.

* Fix to handle data offset Uint64 overflow of `CALLDATALOAD`.

* Fix to handle code offset Uint64 overflow of `CODECOPY`.

* Fix to handle code offset Uint64 overflow of `EXTCODECOPY`.

* Add some comments.

---------

Co-authored-by: Zhang Zhuo <mycinbrin@gmail.com>

## Patch
### bus-mapping/src/evm/opcodes/calldatacopy.rs
```diff
@@ -18,7 +18,8 @@ impl Opcode for Calldatacopy {
 
         // reconstruction
         let memory_offset = geth_step.stack.nth_last(0)?.as_u64();
-        let data_offset = geth_step.stack.nth_last(1)?.as_u64();
+        // Reset data offset to the maximum value of Uint64 if overflow.
+        let data_offset = u64::try_from(geth_step.stack.nth_last(1)?).unwrap_or(u64::MAX);
         let length = geth_step.stack.nth_last(2)?.as_usize();
         let call_ctx = state.call_ctx_mut()?;
         let memory = &mut call_ctx.memory;
@@ -100,7 +101,7 @@ fn gen_copy_steps(
 ) -> Result<Vec<(u8, bool)>, Error> {
     let mut copy_steps = Vec::with_capacity(bytes_left as usize);
     for idx in 0..bytes_left {
-        let addr = src_addr + idx;
+        let addr = src_addr.checked_add(idx).unwrap_or(src_addr_end);
         let value = if addr < src_addr_end {
             let byte =
                 state.call_ctx()?.call_data[(addr - state.call()?.call_data_offset) as usize];
@@ -128,13 +129,17 @@ fn gen_copy_event(
 ) -> Result<CopyEvent, Error> {
     let rw_counter_start = state.block_ctx.rwc;
     let memory_offset = geth_step.stack.nth_last(0)?.as_u64();
-    let data_offset = geth_step.stack.nth_last(1)?.as_u64();
+    // Reset data offset to the maximum value of Uint64 if overflow.
+    let data_offset = u64::try_from(geth_step.stack.nth_last(1)?).unwrap_or(u64::MAX);
     let length = geth_step.stack.nth_last(2)?.as_u64();
 
     let call_data_offset = state.call()?.call_data_offset;
     let call_data_length = state.call()?.call_data_length;
+
     let (src_addr, src_addr_end) = (
-        call_data_offset + data_offset,
+        // Set source start to the minimum value of data offset and call data length for avoiding
+        // overflow.
+        call_data_offset + data_offset.min(call_data_length),
         call_data_offset + call_data_length,
     );
 
```

### bus-mapping/src/evm/opcodes/calldataload.rs
```diff
@@ -23,73 +23,81 @@ impl Opcode for Calldataload {
         let offset = geth_step.stack.nth_last(0)?;
         state.stack_read(&mut exec_step, geth_step.stack.nth_last_filled(0), offset)?;
 
-        let is_root = state.call()?.is_root;
-        if is_root {
-            state.call_context_read(
-                &mut exec_step,
-                state.call()?.call_id,
-                CallContextField::TxId,
-                state.tx_ctx.id().into(),
+        // Check if offset is Uint64 overflow.
+        let calldata_word = if let Ok(offset) = u64::try_from(offset) {
+            let is_root = state.call()?.is_root;
+            let call_id = state.call()?.call_id;
+            if is_root {
+                state.call_context_read(
+                    &mut exec_step,
+                    call_id,
+                    CallContextField::TxId,
+                    state.tx_ctx.id().into(),
+                );
+                state.call_context_read(
+                    &mut exec_step,
+                    call_id,
+                    CallContextField::CallDataLength,
+                    state.call()?.call_data_length.into(),
+                );
+            } else {
+                state.call_context_read(
+                    &mut exec_step,
+                    call_id,
+                    CallContextField::CallerId,
+                    state.call()?.caller_id.into(),
+                );
+                state.call_context_read(
+                    &mut exec_step,
+                    call_id,
+                    CallContextField::CallDataLength,
+                    state.call()?.call_data_length.into(),
+                );
+                state.call_context_read(
+                    &mut exec_step,
+                    call_id,
+                    CallContextField::CallDataOffset,
+                    state.call()?.call_data_offset.into(),
+                );
+            }
+
+            let call_data_offset = state.call()?.call_data_offset;
+            let call_data_length = state.call()?.call_data_length;
+            let (src_addr, src_addr_end, caller_id, call_data) = (
+                // Set source start to the minimum value of offset and call data length for
+                // avoiding overflow.
+                call_data_offset + offset.min(call_data_length),
+                call_data_offset + call_data_length,
+                state.call()?.caller_id,
+                state.call_ctx()?.call_data.to_vec(),
             );
-            state.call_context_read(
-                &mut exec_step,
-                state.call()?.call_id,
-                CallContextField::CallDataLength,
-                state.call()?.call_data_length.into(),
-            );
-        } else {
-            state.call_context_read(
-                &mut exec_step,
-                state.call()?.call_id,
-                CallContextField::CallerId,
-                state.call()?.caller_id.into(),
-            );
-            state.call_context_read(
-                &mut exec_step,
-                state.call()?.call_id,
-                CallContextField::CallDataLength,
-                state.call()?.call_data_length.into(),
-            );
-            state.call_context_read(
-                &mut exec_step,
-                state.call()?.call_id,
-                CallContextField::CallDataOffset,
-                state.call()?.call_data_offset.into(),
-            );
-        }
 
-        let call = state.call()?.clone();
-        let (src_addr, src_addr_end, caller_id, call_data) = (
-            call.call_data_offset as usize + offset.as_usize(),
-            call.call_data_offset as usize + call.call_data_length as usize,
-            call.caller_id,
-            state.call_ctx()?.call_data.to_vec(),
-        );
-        let calldata_word = (0..32)
-            .map(|idx| {
-                let addr = src_addr + idx;
-                if addr < src_addr_end {
-                    let byte = call_data[addr - call.call_data_offset as usize];
-                    if !is_root {
-                        // caller id as call_id
-                        state.push_op(
-                            &mut exec_step,
-                            RW::READ,
-                            MemoryOp::new(caller_id, (src_addr + idx).into(), byte),
-                        );
+            let calldata: Vec<_> = (0..32)
+                .map(|idx| {
+                    let addr = src_addr.checked_add(idx).unwrap_or(src_addr_end);
+                    if addr < src_addr_end {
+                        let byte = call_data[(addr - call_data_offset) as usize];
+                        if !is_root {
+                            state.push_op(
+                                &mut exec_step,
+                                RW::READ,
+                                MemoryOp::new(caller_id, (src_addr + idx).into(), byte),
+                            );
+                        }
+                        byte
+                    } else {
+                        0
                     }
-                    byte
-                } else {
-                    0
-                }
-            })
-            .collect::<Vec<u8>>();
+                })
+                .collect();
+
+            U256::from_big_endian(&calldata)
+        } else {
+            // Stack push `0` as result directly if overflow.
+            U256::zero()
+        };
 
-        state.stack_write(
-            &mut exec_step,
-            geth_step.stack.last_filled(),
-            U256::from_big_endian(&calldata_word),
-        )?;
+        state.stack_write(&mut exec_step, geth_step.stack.last_filled(), calldata_word)?;
 
         Ok(vec![exec_step])
     }
```

### bus-mapping/src/evm/opcodes/codecopy.rs
```diff
@@ -22,7 +22,8 @@ impl Opcode for Codecopy {
         // reconstruction
 
         let dest_offset = geth_step.stack.nth_last(0)?.as_u64();
-        let code_offset = geth_step.stack.nth_last(1)?.as_u64();
+        // Reset code offset to the maximum value of Uint64 if overflow.
+        let code_offset = u64::try_from(geth_step.stack.nth_last(1)?).unwrap_or(u64::MAX);
         let length = geth_step.stack.nth_last(2)?.as_u64();
 
         let code_hash = state.call()?.code_hash;
@@ -70,17 +71,24 @@ fn gen_copy_steps(
     exec_step: &mut ExecStep,
     src_addr: u64,
     dst_addr: u64,
+    src_addr_end: u64,
     bytes_left: u64,
     bytecode: &Bytecode,
 ) -> Result<Vec<(u8, bool)>, Error> {
-    let mut steps = Vec::with_capacity(bytes_left as usize);
+    let mut copy_steps = Vec::with_capacity(bytes_left as usize);
     for idx in 0..bytes_left {
-        let addr = src_addr + idx;
-        let bytecode_element = bytecode.get(addr as usize).unwrap_or_default();
-        steps.push((bytecode_element.value, bytecode_element.is_code));
-        state.memory_write(exec_step, (dst_addr + idx).into(), bytecode_element.value)?;
+        let addr = src_addr.checked_add(idx).unwrap_or(src_addr_end);
+        let step = if addr < src_addr_end {
+            let code = bytecode.code.get(addr as usize).unwrap();
+            (code.value, code.is_code)
+        } else {
+            (0, false)
+        };
+        copy_steps.push(step);
+        state.memory_write(exec_step, (dst_addr + idx).into(), step.0)?;
     }
-    Ok(steps)
+
+    Ok(copy_steps)
 }
 
 fn gen_copy_event(
@@ -90,27 +98,33 @@ fn gen_copy_event(
     let rw_counter_start = state.block_ctx.rwc;
 
     let dst_offset = geth_step.stack.nth_last(0)?.as_u64();
-    let code_offset = geth_step.stack.nth_last(1)?.as_u64();
+    // Reset code offset to the maximum value of Uint64 if overflow.
+    let code_offset = u64::try_from(geth_step.stack.nth_last(1)?).unwrap_or(u64::MAX);
     let length = geth_step.stack.nth_last(2)?.as_u64();
 
     let code_hash = state.call()?.code_hash;
     let bytecode: Bytecode = state.code(code_hash)?.into();
-    let src_addr_end = bytecode.to_vec().len() as u64;
+    let code_size = bytecode.code.len() as u64;
+    // Set source start to the minimum value of code offset and code size for
+    // avoiding overflow.
+    let src_addr = code_offset.min(code_size);
+    let src_addr_end = code_size;
 
     let mut exec_step = state.new_step(geth_step)?;
     let copy_steps = gen_copy_steps(
         state,
         &mut exec_step,
-        code_offset,
+        src_addr,
         dst_offset,
+        src_addr_end,
         length,
         &bytecode,
     )?;
 
     Ok(CopyEvent {
         src_type: CopyDataType::Bytecode,
         src_id: NumberOrHash::Hash(code_hash),
-        src_addr: code_offset,
+        src_addr,
         src_addr_end,
         dst_type: CopyDataType::Memory,
         dst_id: NumberOrHash::Number(state.call()?.call_id),
```

### bus-mapping/src/evm/opcodes/extcodecopy.rs
```diff
@@ -23,7 +23,8 @@ impl Opcode for Extcodecopy {
         // reconstruction
         let address = geth_steps[0].stack.nth_last(0)?.to_address();
         let dest_offset = geth_steps[0].stack.nth_last(1)?.as_u64();
-        let code_offset = geth_steps[0].stack.nth_last(2)?.as_u64();
+        // Reset code offset to the maximum value of Uint64 if overflow.
+        let code_offset = u64::try_from(geth_step.stack.nth_last(2)?).unwrap_or(u64::MAX);
         let length = geth_steps[0].stack.nth_last(3)?.as_u64();
 
         let (_, account) = state.sdb.get_account(&address);
@@ -118,13 +119,13 @@ fn gen_copy_steps(
     dst_addr: u64,
     src_addr_end: u64,
     bytes_left: u64,
-    code: &Bytecode,
+    bytecode: &Bytecode,
 ) -> Result<Vec<(u8, bool)>, Error> {
     let mut copy_steps = Vec::with_capacity(bytes_left as usize);
     for idx in 0..bytes_left {
-        let addr = src_addr + idx;
+        let addr = src_addr.checked_add(idx).unwrap_or(src_addr_end);
         let step = if addr < src_addr_end {
-            let code = code.code.get(addr as usize).unwrap();
+            let code = bytecode.code.get(addr as usize).unwrap();
             (code.value, code.is_code)
         } else {
             (0, false)
@@ -143,7 +144,8 @@ fn gen_copy_event(
     let rw_counter_start = state.block_ctx.rwc;
     let external_address = geth_step.stack.nth_last(0)?.to_address();
     let memory_offset = geth_step.stack.nth_last(1)?.as_u64();
-    let data_offset = geth_step.stack.nth_last(2)?.as_u64();
+    // Reset code offset to the maximum value of Uint64 if overflow.
+    let code_offset = u64::try_from(geth_step.stack.nth_last(2)?).unwrap_or(u64::MAX);
     let length = geth_step.stack.nth_last(3)?.as_u64();
 
     let account = state.sdb.get_account(&external_address).1;
@@ -154,24 +156,29 @@ fn gen_copy_event(
         H256::zero()
     };
 
-    let code: Bytecode = if exists {
+    let bytecode: Bytecode = if exists {
         state.code(code_hash)?.into()
     } else {
         Bytecode::default()
     };
-    let src_addr_end = code.code.len() as u64;
+    let code_size = bytecode.code.len() as u64;
+    // Set source start to the minimum value of code offset and code size for
+    // avoiding overflow.
+    let src_addr = code_offset.min(code_size);
+    let src_addr_end = code_size;
+
     let mut exec_step = state.new_step(geth_step)?;
     let copy_steps = gen_copy_steps(
         state,
         &mut exec_step,
-        data_offset,
+        src_addr,
         memory_offset,
         src_addr_end,
         length,
-        &code,
+        &bytecode,
     )?;
     Ok(CopyEvent {
-        src_addr: data_offset,
+        src_addr,
         src_addr_end,
         src_type: CopyDataType::Bytecode,
         src_id: NumberOrHash::Hash(code_hash),
```

### zkevm-circuits/src/evm_circuit/execution/blockhash.rs
```diff
@@ -4,11 +4,11 @@ use crate::{
         param::N_BYTES_U64,
         step::ExecutionState,
         util::{
-            common_gadget::SameContextGadget,
+            and,
+            common_gadget::{SameContextGadget, WordRangeGadget},
             constraint_builder::{ConstraintBuilder, StepStateTransition, Transition::Delta},
-            from_bytes,
             math_gadget::LtGadget,
-            CachedRegion, Cell, RandomLinearCombination, Word,
+            CachedRegion, Cell, Word,
         },
         witness::{Block, Call, ExecStep, Transaction},
     },
@@ -28,7 +28,7 @@ const NUM_PREV_BLOCK_ALLOWED: u64 = 257;
 #[derive(Clone, Debug)]
 pub(crate) struct BlockHashGadget<F> {
     same_context: SameContextGadget<F>,
-    block_number: RandomLinearCombination<F, N_BYTES_U64>,
+    block_number_word: WordRangeGadget<F>,
     current_block_number: Cell<F>,
     block_hash: Word<F>,
     block_lt: LtGadget<F, N_BYTES_U64>,
@@ -41,8 +41,9 @@ impl<F: Field> ExecutionGadget<F> for BlockHashGadget<F> {
     const EXECUTION_STATE: ExecutionState = ExecutionState::BLOCKHASH;
 
     fn configure(cb: &mut ConstraintBuilder<F>) -> Self {
-        let block_number = cb.query_word_rlc();
-        cb.stack_pop(block_number.expr());
+        let block_number_word = WordRangeGadget::construct(cb, N_BYTES_U64);
+        let block_number = block_number_word.valid_value_expr(N_BYTES_U64);
+        cb.stack_pop(block_number_word.original_word_expr());
 
         let current_block_number = cb.query_cell();
         // FIXME
@@ -52,28 +53,34 @@ impl<F: Field> ExecutionGadget<F> for BlockHashGadget<F> {
         //    current_block_number.expr(),
         //);
 
-        let block_lt = LtGadget::construct(
-            cb,
-            from_bytes::expr(&block_number.cells),
-            current_block_number.expr(),
-        );
+        let block_hash = cb.query_word_rlc();
 
+        let block_lt = LtGadget::construct(cb, block_number.expr(), current_block_number.expr());
         let diff_lt = LtGadget::construct(
             cb,
             current_block_number.expr(),
-            NUM_PREV_BLOCK_ALLOWED.expr() + from_bytes::expr(&block_number.cells),
+            NUM_PREV_BLOCK_ALLOWED.expr() + block_number.expr(),
         );
 
-        let block_hash = cb.query_word_rlc();
-        cb.condition(block_lt.expr() * diff_lt.expr(), |cb| {
+        let is_valid_block_number = and::expr([
+            block_number_word.within_range_expr(),
+            block_lt.expr(),
+            diff_lt.expr(),
+        ]);
+
+        cb.condition(is_valid_block_number.expr(), |cb| {
             cb.block_lookup(
                 BlockContextFieldTag::BlockHash.expr(),
-                from_bytes::expr(&block_number.cells),
+                block_number,
                 block_hash.expr(),
             );
         });
-        cb.condition(not::expr(block_lt.expr() * diff_lt.expr()), |cb| {
-            cb.require_zero("invalid range", block_hash.expr());
+
+        cb.condition(not::expr(is_valid_block_number), |cb| {
+            cb.require_zero(
+                "Invalid block number for block hash lookup",
+                block_hash.expr(),
+            );
         });
 
         cb.stack_push(block_hash.expr());
@@ -89,7 +96,7 @@ impl<F: Field> ExecutionGadget<F> for BlockHashGadget<F> {
         let same_context = SameContextGadget::construct(cb, opcode, step_state_transition);
         Self {
             same_context,
-            block_number,
+            block_number_word,
             current_block_number,
             block_hash,
             block_lt,
@@ -109,15 +116,8 @@ impl<F: Field> ExecutionGadget<F> for BlockHashGadget<F> {
         self.same_context.assign_exec_step(region, offset, step)?;
 
         let block_number = block.rws[step.rw_indices[0]].stack_value();
-        self.block_number.assign(
-            region,
-            offset,
-            Some(
-                block_number.to_le_bytes()[..N_BYTES_U64]
-                    .try_into()
-                    .unwrap(),
-            ),
-        )?;
+        self.block_number_word
+            .assign(region, offset, N_BYTES_U64, block_number)?;
         let block_number: F = block_number.to_scalar().unwrap();
 
         let current_block_number = block.context.ctxs[&tx.block_number].number;
@@ -158,7 +158,7 @@ mod test {
     use eth_types::{bytecode, U256};
     use mock::test_ctx::{helpers::*, TestContext};
 
-    fn test_ok(block_number: usize, current_block_number: u64) {
+    fn test_ok(block_number: U256, current_block_number: u64) {
         let code = bytecode! {
             PUSH32(block_number)
             BLOCKHASH
@@ -188,21 +188,26 @@ mod test {
 
     #[test]
     fn blockhash_gadget_simple() {
-        test_ok(0, 5);
-        test_ok(1, 5);
-        test_ok(2, 5);
-        test_ok(3, 5);
-        test_ok(4, 5);
-        test_ok(5, 5);
-        test_ok(6, 5);
+        test_ok(0.into(), 5);
+        test_ok(1.into(), 5);
+        test_ok(2.into(), 5);
+        test_ok(3.into(), 5);
+        test_ok(4.into(), 5);
+        test_ok(5.into(), 5);
+        test_ok(6.into(), 5);
     }
 
     #[test]
     fn blockhash_gadget_large() {
-        test_ok(0xcafe - 257, 0xcafeu64);
-        test_ok(0xcafe - 256, 0xcafeu64);
-        test_ok(0xcafe - 1, 0xcafeu64);
-        test_ok(0xcafe, 0xcafeu64);
-        test_ok(0xcafe + 1, 0xcafeu64);
+        test_ok((0xcafe - 257).into(), 0xcafeu64);
+        test_ok((0xcafe - 256).into(), 0xcafeu64);
+        test_ok((0xcafe - 1).into(), 0xcafeu64);
+        test_ok(0xcafe.into(), 0xcafeu64);
+        test_ok((0xcafe + 1).into(), 0xcafeu64);
+    }
+
+    #[test]
+    fn blockhash_gadget_block_number_overflow() {
+        test_ok(U256::MAX, 0xcafeu64);
     }
 }
```

### zkevm-circuits/src/evm_circuit/execution/calldatacopy.rs
```diff
@@ -1,25 +1,25 @@
 use crate::{
     evm_circuit::{
         execution::ExecutionGadget,
-        param::{N_BYTES_MEMORY_ADDRESS, N_BYTES_MEMORY_WORD_SIZE},
+        param::{N_BYTES_MEMORY_WORD_SIZE, N_BYTES_U64},
         step::ExecutionState,
         util::{
-            common_gadget::SameContextGadget,
+            common_gadget::{SameContextGadget, WordRangeGadget},
             constraint_builder::{
                 ConstraintBuilder, StepStateTransition,
                 Transition::{Delta, To},
             },
-            from_bytes,
+            math_gadget::LtGadget,
             memory_gadget::{MemoryAddressGadget, MemoryCopierGasGadget, MemoryExpansionGadget},
-            not, select, CachedRegion, Cell, MemoryAddress,
+            not, select, CachedRegion, Cell,
         },
         witness::{Block, Call, ExecStep, Transaction},
     },
     table::CallContextFieldTag,
     util::Expr,
 };
 use bus_mapping::{circuit_input_builder::CopyDataType, evm::OpcodeId};
-use eth_types::{evm_types::GasCost, Field, ToLittleEndian, ToScalar};
+use eth_types::{evm_types::GasCost, Field, ToScalar};
 use halo2_proofs::{circuit::Value, plonk::Error};
 
 use std::cmp::min;
@@ -28,7 +28,8 @@ use std::cmp::min;
 pub(crate) struct CallDataCopyGadget<F> {
     same_context: SameContextGadget<F>,
     memory_address: MemoryAddressGadget<F>,
-    data_offset: MemoryAddress<F>,
+    data_offset_word: WordRangeGadget<F>,
+    data_offset_lt_call_data_length: LtGadget<F, N_BYTES_U64>,
     src_id: Cell<F>,
     call_data_length: Cell<F>,
     call_data_offset: Cell<F>, // Only used in the internal call
@@ -45,19 +46,28 @@ impl<F: Field> ExecutionGadget<F> for CallDataCopyGadget<F> {
     fn configure(cb: &mut ConstraintBuilder<F>) -> Self {
         let opcode = cb.query_cell();
 
-        let memory_offset = cb.query_cell_phase2();
-        let data_offset = cb.query_word_rlc();
         let length = cb.query_word_rlc();
+        let memory_offset = cb.query_cell_phase2();
+        let data_offset_word = WordRangeGadget::construct(cb, N_BYTES_U64);
+
+        // Reset data offset to the maximum value of Uint64 if overflow.
+        let data_offset = select::expr(
+            data_offset_word.within_range_expr(),
+            data_offset_word.valid_value_expr(N_BYTES_U64),
+            u64::MAX.expr(),
+        );
 
         // Pop memory_offset, data_offset, length from stack
         cb.stack_pop(memory_offset.expr());
-        cb.stack_pop(data_offset.expr());
+        cb.stack_pop(data_offset_word.original_word_expr());
         cb.stack_pop(length.expr());
 
         let memory_address = MemoryAddressGadget::construct(cb, memory_offset, length);
         let src_id = cb.query_cell();
         let call_data_length = cb.query_cell();
         let call_data_offset = cb.query_cell();
+        let data_offset_lt_call_data_length =
+            LtGadget::construct(cb, data_offset.expr(), call_data_length.expr());
 
         // Lookup the calldata_length and caller_address in Tx context table or
         // Call context table
@@ -116,7 +126,13 @@ impl<F: Field> ExecutionGadget<F> for CallDataCopyGadget<F> {
                 src_tag,
                 cb.curr.state.call_id.expr(),
                 CopyDataType::Memory.expr(),
-                call_data_offset.expr() + from_bytes::expr(&data_offset.cells),
+                call_data_offset.expr()
+                    // Set source start to the minimun value of data offset and call data length.
+                    + select::expr(
+                        data_offset_lt_call_data_length.expr(),
+                        data_offset,
+                        call_data_length.expr(),
+                    ),
                 call_data_offset.expr() + call_data_length.expr(),
                 memory_address.offset(),
                 memory_address.length(),
@@ -148,7 +164,8 @@ impl<F: Field> ExecutionGadget<F> for CallDataCopyGadget<F> {
         Self {
             same_context,
             memory_address,
-            data_offset,
+            data_offset_word,
+            data_offset_lt_call_data_length,
             src_id,
             call_data_length,
             call_data_offset,
@@ -175,15 +192,9 @@ impl<F: Field> ExecutionGadget<F> for CallDataCopyGadget<F> {
         let memory_address = self
             .memory_address
             .assign(region, offset, memory_offset, length)?;
-        self.data_offset.assign(
-            region,
-            offset,
-            Some(
-                data_offset.to_le_bytes()[..N_BYTES_MEMORY_ADDRESS]
-                    .try_into()
-                    .unwrap(),
-            ),
-        )?;
+        let data_offset_within_range =
+            self.data_offset_word
+                .assign(region, offset, N_BYTES_U64, data_offset)?;
         let src_id = if call.is_root { tx.id } else { call.caller_id };
         self.src_id.assign(
             region,
@@ -202,6 +213,17 @@ impl<F: Field> ExecutionGadget<F> for CallDataCopyGadget<F> {
         self.call_data_offset
             .assign(region, offset, Value::known(F::from(call_data_offset)))?;
 
+        self.data_offset_lt_call_data_length.assign(
+            region,
+            offset,
+            F::from(if data_offset_within_range {
+                data_offset.as_u64()
+            } else {
+                u64::MAX
+            }),
+            F::from(call_data_length),
+        )?;
+
         // rw_counter increase from copy lookup is `length` memory writes + a variable
         // number of memory reads.
         let copy_rwc_inc = length
@@ -257,8 +279,8 @@ mod test {
     fn test_ok_root(
         call_data_length: usize,
         memory_offset: usize,
-        data_offset: usize,
         length: usize,
+        data_offset: Word,
     ) {
         let bytecode = bytecode! {
             PUSH32(length)
@@ -296,15 +318,15 @@ mod test {
         call_data_offset: usize,
         call_data_length: usize,
         dst_offset: usize,
-        offset: usize,
         length: usize,
+        data_offset: Word,
     ) {
         let (addr_a, addr_b) = (mock::MOCK_ACCOUNTS[0], mock::MOCK_ACCOUNTS[1]);
 
         // code B gets called by code A, so the call is an internal call.
         let code_b = bytecode! {
-            PUSH32(length)  // size
-            PUSH32(offset)     // offset
+            PUSH32(length) // size
+            PUSH32(data_offset) // data_offset
             PUSH32(dst_offset) // dst_offset
             CALLDATACOPY
             STOP
@@ -350,25 +372,31 @@ mod test {
 
     #[test]
     fn calldatacopy_gadget_simple() {
-        test_ok_root(0x40, 0x40, 0x00, 10);
-        test_ok_internal(0x40, 0x40, 0xA0, 0x10, 10);
+        test_ok_root(0x40, 0x40, 10, 0x00.into());
+        test_ok_internal(0x40, 0x40, 0xA0, 10, 0x10.into());
     }
 
     #[test]
     fn calldatacopy_gadget_large() {
-        test_ok_root(0x204, 0x103, 0x102, 0x101);
-        test_ok_internal(0x30, 0x204, 0x103, 0x102, 0x101);
+        test_ok_root(0x204, 0x103, 0x101, 0x102.into());
+        test_ok_internal(0x30, 0x204, 0x103, 0x101, 0x102.into());
     }
 
     #[test]
     fn calldatacopy_gadget_out_of_bound() {
-        test_ok_root(0x40, 0x40, 0x20, 40);
-        test_ok_internal(0x40, 0x20, 0xA0, 0x28, 10);
+        test_ok_root(0x40, 0x40, 40, 0x20.into());
+        test_ok_internal(0x40, 0x20, 0xA0, 10, 0x28.into());
     }
 
     #[test]
     fn calldatacopy_gadget_zero_length() {
-        test_ok_root(0x40, 0x40, 0x00, 0);
-        test_ok_internal(0x40, 0x40, 0xA0, 0x10, 0);
+        test_ok_root(0x40, 0x40, 0, 0x00.into());
+        test_ok_internal(0x40, 0x40, 0xA0, 0, 0x10.into());
+    }
+
+    #[test]
+    fn calldatacopy_gadget_data_offset_overflow() {
+        test_ok_root(0x40, 0x40, 0, Word::MAX);
+        test_ok_internal(0x40, 0x40, 0xA0, 0, Word::MAX);
     }
 }
```

### zkevm-circuits/src/evm_circuit/execution/calldataload.rs
```diff
@@ -1,20 +1,21 @@
 use bus_mapping::evm::OpcodeId;
-use eth_types::{Field, ToLittleEndian};
+use eth_types::Field;
 use halo2_proofs::{
     circuit::Value,
     plonk::{Error, Expression},
 };
 
 use crate::{
     evm_circuit::{
-        param::{N_BYTES_MEMORY_ADDRESS, N_BYTES_WORD},
+        param::{N_BYTES_MEMORY_ADDRESS, N_BYTES_U64, N_BYTES_WORD},
         step::ExecutionState,
         util::{
-            common_gadget::SameContextGadget,
+            and,
+            common_gadget::{SameContextGadget, WordRangeGadget},
             constraint_builder::{ConstraintBuilder, StepStateTransition, Transition::Delta},
-            from_bytes,
+            math_gadget::LtGadget,
             memory_gadget::BufferReaderGadget,
-            not, CachedRegion, Cell, MemoryAddress,
+            not, select, CachedRegion, Cell,
         },
         witness::{Block, Call, ExecStep, Transaction},
     },
@@ -34,15 +35,18 @@ pub(crate) struct CallDataLoadGadget<F> {
     /// Source of data, this is transaction ID for a root call and caller ID for
     /// an internal call.
     src_id: Cell<F>,
-    /// The bytes offset in calldata, from which we load a 32-bytes word.
-    offset: MemoryAddress<F>,
     /// The size of the call's data (tx input for a root call or calldata length
     /// of an internal call).
     call_data_length: Cell<F>,
     /// The offset from where call data begins. This is 0 for a root call since
     /// tx data starts at the first byte, but can be non-zero offset for an
     /// internal call.
     call_data_offset: Cell<F>,
+    /// The bytes offset in calldata, from which we load a 32-bytes word. It
+    /// could be Uint64 overflow.
+    offset_word: WordRangeGadget<F>,
+    /// Check if offset is less than calldata length.
+    offset_lt_call_data_length: LtGadget<F, N_BYTES_U64>,
     /// Gadget to read from tx calldata, which we validate against the word
     /// pushed to stack.
     buffer_reader: BufferReaderGadget<F, N_BYTES_WORD, N_BYTES_MEMORY_ADDRESS>,
@@ -56,61 +60,98 @@ impl<F: Field> ExecutionGadget<F> for CallDataLoadGadget<F> {
     fn configure(cb: &mut ConstraintBuilder<F>) -> Self {
         let opcode = cb.query_cell();
 
-        let offset = cb.query_word_rlc();
+        let offset_word = WordRangeGadget::construct(cb, N_BYTES_U64);
+
+        // Reset data offset to the maximum value of Uint64 if overflow.
+        let offset = select::expr(
+            offset_word.within_range_expr(),
+            offset_word.valid_value_expr(N_BYTES_U64),
+            u64::MAX.expr(),
+        );
 
         // Pop the offset value from stack.
-        cb.stack_pop(offset.expr());
+        cb.stack_pop(offset_word.original_word_expr());
 
         // Add a lookup constrain for TxId in the RW table.
         let src_id = cb.query_cell();
         let call_data_length = cb.query_cell();
         let call_data_offset = cb.query_cell();
-
-        let src_addr = from_bytes::expr(&offset.cells) + call_data_offset.expr();
-        let src_addr_end = call_data_length.expr() + call_data_offset.expr();
-
-        cb.condition(cb.curr.state.is_root.expr(), |cb| {
-            cb.call_context_lookup(false.expr(), None, CallContextFieldTag::TxId, src_id.expr());
-            cb.call_context_lookup(
-                false.expr(),
-                None,
-                CallContextFieldTag::CallDataLength,
+        let offset_lt_call_data_length =
+            LtGadget::construct(cb, offset.expr(), call_data_length.expr());
+
+        // Set source start to the minimun value of offset and call data length.
+        let src_addr = call_data_offset.expr()
+            + select::expr(
+                offset_lt_call_data_length.expr(),
+                offset,
                 call_data_length.expr(),
             );
-            cb.require_equal(
-                "if is_root then call_data_offset == 0",
-                call_data_offset.expr(),
-                0.expr(),
-            );
-        });
-        cb.condition(not::expr(cb.curr.state.is_root.expr()), |cb| {
-            cb.call_context_lookup(
-                false.expr(),
-                None,
-                CallContextFieldTag::CallerId,
-                src_id.expr(),
-            );
-            cb.call_context_lookup(
-                false.expr(),
-                None,
-                CallContextFieldTag::CallDataLength,
-                call_data_length.expr(),
-            );
-            cb.call_context_lookup(
-                false.expr(),
-                None,
-                CallContextFieldTag::CallDataOffset,
-                call_data_offset.expr(),
-            );
-        });
+        let src_addr_end = call_data_offset.expr() + call_data_length.expr();
+
+        cb.condition(
+            and::expr([
+                offset_word.within_range_expr(),
+                cb.curr.state.is_root.expr(),
+            ]),
+            |cb| {
+                cb.call_context_lookup(
+                    false.expr(),
+                    None,
+                    CallContextFieldTag::TxId,
+                    src_id.expr(),
+                );
+                cb.call_context_lookup(
+                    false.expr(),
+                    None,
+                    CallContextFieldTag::CallDataLength,
+                    call_data_length.expr(),
+                );
+                cb.require_equal(
+                    "if is_root then call_data_offset == 0",
+                    call_data_offset.expr(),
+                    0.expr(),
+                );
+            },
+        );
+
+        cb.condition(
+            and::expr([
+                offset_word.within_range_expr(),
+                not::expr(cb.curr.state.is_root.expr()),
+            ]),
+            |cb| {
+                cb.call_context_lookup(
+                    false.expr(),
+                    None,
+                    CallContextFieldTag::CallerId,
+                    src_id.expr(),
+                );
+                cb.call_context_lookup(
+                    false.expr(),
+                    None,
+                    CallContextFieldTag::CallDataLength,
+                    call_data_length.expr(),
+                );
+                cb.call_context_lookup(
+                    false.expr(),
+                    None,
+                    CallContextFieldTag::CallDataOffset,
+                    call_data_offset.expr(),
+                );
+            },
+        );
 
-        let buffer_reader = BufferReaderGadget::construct(cb, src_addr.clone(), src_addr_end);
+        let buffer_reader = BufferReaderGadget::construct(cb, src_addr.expr(), src_addr_end);
 
-        let mut calldata_word = (0..N_BYTES_WORD)
+        let mut calldata_word: Vec<_> = (0..N_BYTES_WORD)
             .map(|idx| {
-                // for a root call, the call data comes from tx's data field.
+                // For a root call, the call data comes from tx's data field.
                 cb.condition(
-                    cb.curr.state.is_root.expr() * buffer_reader.read_flag(idx),
+                    and::expr([
+                        offset_word.within_range_expr(),
+                        buffer_reader.read_flag(idx),
+                        cb.curr.state.is_root.expr(),
+                    ]),
                     |cb| {
                         cb.tx_context_lookup(
                             src_id.expr(),
@@ -120,9 +161,13 @@ impl<F: Field> ExecutionGadget<F> for CallDataLoadGadget<F> {
                         );
                     },
                 );
-                // for an internal call, the call data comes from memory.
+                // For an internal call, the call data comes from memory.
                 cb.condition(
-                    (1.expr() - cb.curr.state.is_root.expr()) * buffer_reader.read_flag(idx),
+                    and::expr([
+                        offset_word.within_range_expr(),
+                        buffer_reader.read_flag(idx),
+                        not::expr(cb.curr.state.is_root.expr()),
+                    ]),
                     |cb| {
                         cb.memory_lookup(
                             0.expr(),
@@ -134,7 +179,7 @@ impl<F: Field> ExecutionGadget<F> for CallDataLoadGadget<F> {
                 );
                 buffer_reader.byte(idx)
             })
-            .collect::<Vec<Expression<F>>>();
+            .collect();
 
         // Since the stack items are in little endian form, we reverse the bytes
         // here.
@@ -157,10 +202,11 @@ impl<F: Field> ExecutionGadget<F> for CallDataLoadGadget<F> {
 
         Self {
             same_context,
-            offset,
             src_id,
             call_data_length,
             call_data_offset,
+            offset_word,
+            offset_lt_call_data_length,
             buffer_reader,
         }
     }
@@ -176,62 +222,72 @@ impl<F: Field> ExecutionGadget<F> for CallDataLoadGadget<F> {
     ) -> Result<(), Error> {
         self.same_context.assign_exec_step(region, offset, step)?;
 
-        // set the value for bytes offset in calldata. This is where we start
-        // reading bytes from.
         let data_offset = block.rws[step.rw_indices[0]].stack_value();
+        let offset_within_range =
+            self.offset_word
+                .assign(region, offset, N_BYTES_U64, data_offset)?;
+        let data_offset = if offset_within_range {
+            data_offset.as_u64()
+        } else {
+            u64::MAX
+        };
 
-        // assign the calldata start and end cells.
-        self.offset.assign(
-            region,
-            offset,
-            Some(
-                data_offset.to_le_bytes()[..N_BYTES_MEMORY_ADDRESS]
-                    .try_into()
-                    .unwrap(),
-            ),
-        )?;
-
-        // assign to the buffer reader gadget.
-        let (calldata_length, calldata_offset, src_id) = if call.is_root {
-            (tx.call_data_length as u64, 0u64, tx.id as u64)
+        // Assign to the buffer reader gadget.
+        let (src_id, call_data_offset, call_data_length) = if call.is_root {
+            (tx.id, 0, tx.call_data_length as u64)
         } else {
-            (
-                call.call_data_length,
-                call.call_data_offset,
-                call.caller_id as u64,
-            )
+            (call.caller_id, call.call_data_offset, call.call_data_length)
         };
         self.src_id
-            .assign(region, offset, Value::known(F::from(src_id)))?;
+            .assign(region, offset, Value::known(F::from(src_id as u64)))?;
         self.call_data_length
-            .assign(region, offset, Value::known(F::from(calldata_length)))?;
+            .assign(region, offset, Value::known(F::from(call_data_length)))?;
         self.call_data_offset
-            .assign(region, offset, Value::known(F::from(calldata_offset)))?;
+            .assign(region, offset, Value::known(F::from(call_data_offset)))?;
+
+        self.offset_lt_call_data_length.assign(
+            region,
+            offset,
+            F::from(data_offset),
+            F::from(call_data_length),
+        )?;
 
         let mut calldata_bytes = vec![0u8; N_BYTES_WORD];
         let (src_addr, src_addr_end) = (
-            data_offset.as_usize() + calldata_offset as usize,
-            calldata_length as usize + calldata_offset as usize,
+            // Set source start to the minimun value of data offset and call data length.
+            call_data_offset
+                + if data_offset < call_data_length {
+                    data_offset
+                } else {
+                    call_data_length
+                },
+            call_data_offset + call_data_length,
         );
 
-        for (i, byte) in calldata_bytes.iter_mut().enumerate() {
-            if call.is_root {
-                // fetch from tx call data
-                if src_addr + i < tx.call_data_length {
-                    *byte = tx.call_data[src_addr + i];
-                }
-            } else {
-                // fetch from memory
-                if src_addr + i < (call.call_data_offset + call.call_data_length) as usize {
-                    *byte = block.rws[step.rw_indices[OFFSET_RW_MEMORY_INDICES + i]].memory_value();
+        if offset_within_range {
+            for (i, byte) in calldata_bytes.iter_mut().enumerate() {
+                if call.is_root {
+                    // Fetch from tx call data.
+                    if src_addr.checked_add(i as u64).unwrap() < tx.call_data_length as u64 {
+                        *byte = tx.call_data[src_addr as usize + i];
+                    }
+                } else {
+                    // Fetch from memory.
+                    if src_addr.checked_add(i as u64).unwrap()
+                        < call.call_data_offset + call.call_data_length
+                    {
+                        *byte =
+                            block.rws[step.rw_indices[OFFSET_RW_MEMORY_INDICES + i]].memory_value();
+                    }
                 }
             }
         }
+
         self.buffer_reader.assign(
             region,
             offset,
-            src_addr as u64,
-            src_addr_end as u64,
+            src_addr,
+            src_addr_end,
             &calldata_bytes,
             &[true; N_BYTES_WORD],
         )?;
@@ -246,9 +302,9 @@ mod test {
     use eth_types::{bytecode, ToWord, Word};
     use mock::TestContext;
 
-    fn test_root_ok(offset: usize) {
+    fn test_root_ok(offset: Word) {
         let bytecode = bytecode! {
-            PUSH32(Word::from(offset))
+            PUSH32(offset)
             CALLDATALOAD
             STOP
         };
@@ -259,12 +315,12 @@ mod test {
         .run();
     }
 
-    fn test_internal_ok(call_data_length: usize, call_data_offset: usize, offset: usize) {
+    fn test_internal_ok(call_data_length: usize, call_data_offset: usize, offset: Word) {
         let (addr_a, addr_b) = (mock::MOCK_ACCOUNTS[0], mock::MOCK_ACCOUNTS[1]);
 
         // code B gets called by code A, so the call is an internal call.
         let code_b = bytecode! {
-            PUSH32(Word::from(offset))
+            PUSH32(offset)
             CALLDATALOAD
             STOP
         };
@@ -308,17 +364,23 @@ mod test {
 
     #[test]
     fn calldataload_gadget_root() {
-        test_root_ok(0x00);
-        test_root_ok(0x08);
-        test_root_ok(0x10);
-        test_root_ok(0x2010);
+        test_root_ok(0x00.into());
+        test_root_ok(0x08.into());
+        test_root_ok(0x10.into());
+        test_root_ok(0x2010.into());
     }
 
     #[test]
     fn calldataload_gadget_internal() {
-        test_internal_ok(0x20, 0x00, 0x00);
-        test_internal_ok(0x20, 0x10, 0x10);
-        test_internal_ok(0x40, 0x20, 0x08);
-        test_internal_ok(0x1010, 0xff, 0x10);
+        test_internal_ok(0x20, 0x00, 0x00.into());
+        test_internal_ok(0x20, 0x10, 0x10.into());
+        test_internal_ok(0x40, 0x20, 0x08.into());
+        test_internal_ok(0x1010, 0xff, 0x10.into());
+    }
+
+    #[test]
+    fn calldataload_gadget_offset_overflow() {
+        test_root_ok(Word::MAX);
+        test_internal_ok(0x1010, 0xff, Word::MAX);
     }
 }
```

### zkevm-circuits/src/evm_circuit/execution/codecopy.rs
```diff
@@ -1,17 +1,17 @@
 use bus_mapping::{circuit_input_builder::CopyDataType, evm::OpcodeId};
-use eth_types::{evm_types::GasCost, Field, ToLittleEndian, ToScalar};
+use eth_types::{evm_types::GasCost, Field, ToScalar};
 use halo2_proofs::{circuit::Value, plonk::Error};
 
 use crate::{
     evm_circuit::{
-        param::{N_BYTES_MEMORY_ADDRESS, N_BYTES_MEMORY_WORD_SIZE},
+        param::{N_BYTES_MEMORY_WORD_SIZE, N_BYTES_U64},
         step::ExecutionState,
         util::{
-            common_gadget::SameContextGadget,
+            common_gadget::{SameContextGadget, WordRangeGadget},
             constraint_builder::{ConstraintBuilder, StepStateTransition, Transition},
-            from_bytes,
+            math_gadget::LtGadget,
             memory_gadget::{MemoryAddressGadget, MemoryCopierGasGadget, MemoryExpansionGadget},
-            not, CachedRegion, Cell, MemoryAddress,
+            not, select, CachedRegion, Cell,
         },
         witness::{Block, Call, ExecStep, Transaction},
     },
@@ -23,8 +23,11 @@ use super::ExecutionGadget;
 #[derive(Clone, Debug)]
 pub(crate) struct CodeCopyGadget<F> {
     same_context: SameContextGadget<F>,
-    /// Holds the memory address for the offset in code from where we read.
-    code_offset: MemoryAddress<F>,
+    /// Holds the memory address for the offset in code from where we
+    /// read (checked with Uint64 overflow).
+    code_offset_word: WordRangeGadget<F>,
+    /// Checks if code offset is less than code size.
+    code_offset_lt_code_size: LtGadget<F, N_BYTES_U64>,
     /// Holds the size of the current environment's bytecode.
     code_size: Cell<F>,
     /// The code from current environment is copied to memory. To verify this
@@ -50,13 +53,13 @@ impl<F: Field> ExecutionGadget<F> for CodeCopyGadget<F> {
         let opcode = cb.query_cell();
 
         // Query elements to be popped from the stack.
-        let dst_memory_offset = cb.query_cell_phase2();
-        let code_offset = cb.query_word_rlc();
         let size = cb.query_word_rlc();
+        let dst_memory_offset = cb.query_cell_phase2();
+        let code_offset_word = WordRangeGadget::construct(cb, N_BYTES_U64);
 
         // Pop items from stack.
         cb.stack_pop(dst_memory_offset.expr());
-        cb.stack_pop(code_offset.expr());
+        cb.stack_pop(code_offset_word.original_word_expr());
         cb.stack_pop(size.expr());
 
         // Construct memory address in the destionation (memory) to which we copy code.
@@ -69,6 +72,16 @@ impl<F: Field> ExecutionGadget<F> for CodeCopyGadget<F> {
         let code_size = cb.query_cell();
         cb.bytecode_length(code_hash.expr(), code_size.expr());
 
+        // Reset code offset to the maximum value of Uint64 if overflow.
+        let code_offset = select::expr(
+            code_offset_word.within_range_expr(),
+            code_offset_word.valid_value_expr(N_BYTES_U64),
+            u64::MAX.expr(),
+        );
+
+        let code_offset_lt_code_size =
+            LtGadget::construct(cb, code_offset.expr(), code_size.expr());
+
         // Calculate the next memory size and the gas cost for this memory
         // access. This also accounts for the dynamic gas required to copy bytes to
         // memory.
@@ -86,7 +99,12 @@ impl<F: Field> ExecutionGadget<F> for CodeCopyGadget<F> {
                 CopyDataType::Bytecode.expr(),
                 cb.curr.state.call_id.expr(),
                 CopyDataType::Memory.expr(),
-                from_bytes::expr(&code_offset.cells),
+                // Set source start to the minimum value of code offset and code size.
+                select::expr(
+                    code_offset_lt_code_size.expr(),
+                    code_offset,
+                    code_size.expr(),
+                ),
                 code_size.expr(),
                 dst_memory_addr.offset(),
                 dst_memory_addr.length(),
@@ -116,7 +134,8 @@ impl<F: Field> ExecutionGadget<F> for CodeCopyGadget<F> {
 
         Self {
             same_context,
-            code_offset,
+            code_offset_word,
+            code_offset_lt_code_size,
             code_size,
             dst_memory_addr,
             memory_expansion,
@@ -145,25 +164,29 @@ impl<F: Field> ExecutionGadget<F> for CodeCopyGadget<F> {
         let [dest_offset, code_offset, size] =
             [0, 1, 2].map(|i| block.rws[step.rw_indices[i]].stack_value());
 
-        // assign the code offset memory address.
-        self.code_offset.assign(
-            region,
-            offset,
-            Some(
-                code_offset.to_le_bytes()[..N_BYTES_MEMORY_ADDRESS]
-                    .try_into()
-                    .unwrap(),
-            ),
-        )?;
+        // assign the code offset word.
+        let code_offset_within_range =
+            self.code_offset_word
+                .assign(region, offset, N_BYTES_U64, code_offset)?;
 
-        let code = block
+        let bytecode = block
             .bytecodes
             .get(&call.code_hash)
             .expect("could not find current environment's bytecode");
-        self.code_size.assign(
+
+        let code_size = bytecode.bytes.len() as u64;
+        self.code_size
+            .assign(region, offset, Value::known(F::from(code_size)))?;
+
+        self.code_offset_lt_code_size.assign(
             region,
             offset,
-            Value::known(F::from(code.bytes.len() as u64)),
+            F::from(if code_offset_within_range {
+                code_offset.as_u64()
+            } else {
+                u64::MAX
+            }),
+            F::from(code_size),
         )?;
 
         // assign the destination memory offset.
@@ -200,16 +223,16 @@ mod tests {
     use eth_types::{bytecode, Word};
     use mock::TestContext;
 
-    fn test_ok(memory_offset: usize, code_offset: usize, size: usize, large: bool) {
+    fn test_ok(code_offset: Word, memory_offset: usize, size: usize, large: bool) {
         let mut code = bytecode! {};
         if large {
-            for _ in 0..0x101 {
+            for _ in 0..size {
                 code.push(1, Word::from(123));
             }
         }
         let tail = bytecode! {
             PUSH32(Word::from(size))
-            PUSH32(Word::from(code_offset))
+            PUSH32(code_offset)
             PUSH32(Word::from(memory_offset))
             CODECOPY
             STOP
@@ -224,13 +247,18 @@ mod tests {
 
     #[test]
     fn codecopy_gadget_simple() {
-        test_ok(0x00, 0x00, 0x20, false);
-        test_ok(0x20, 0x30, 0x30, false);
-        test_ok(0x10, 0x20, 0x42, false);
+        test_ok(0x00.into(), 0x00, 0x20, false);
+        test_ok(0x30.into(), 0x20, 0x30, false);
+        test_ok(0x20.into(), 0x10, 0x42, false);
     }
 
     #[test]
     fn codecopy_gadget_large() {
-        test_ok(0x103, 0x102, 0x101, true);
+        test_ok(0x102.into(), 0x103, 0x101, true);
+    }
+
+    #[test]
+    fn codecopy_gadget_code_offset_overflow() {
+        test_ok(Word::MAX, 0x103, 0x101, true);
     }
 }
```

### zkevm-circuits/src/evm_circuit/execution/extcodecopy.rs
```diff
@@ -1,15 +1,16 @@
 use crate::{
     evm_circuit::{
-        param::{N_BYTES_ACCOUNT_ADDRESS, N_BYTES_MEMORY_ADDRESS, N_BYTES_MEMORY_WORD_SIZE},
+        param::{N_BYTES_ACCOUNT_ADDRESS, N_BYTES_MEMORY_WORD_SIZE, N_BYTES_U64},
         step::ExecutionState,
         util::{
-            common_gadget::SameContextGadget,
+            common_gadget::{SameContextGadget, WordRangeGadget},
             constraint_builder::{
                 ConstraintBuilder, ReversionInfo, StepStateTransition, Transition,
             },
             from_bytes,
+            math_gadget::LtGadget,
             memory_gadget::{MemoryAddressGadget, MemoryCopierGasGadget, MemoryExpansionGadget},
-            not, select, CachedRegion, Cell, MemoryAddress, Word,
+            not, select, CachedRegion, Cell, Word,
         },
         witness::{Block, Call, ExecStep, Transaction},
     },
@@ -27,7 +28,8 @@ pub(crate) struct ExtcodecopyGadget<F> {
     same_context: SameContextGadget<F>,
     external_address_word: Word<F>,
     memory_address: MemoryAddressGadget<F>,
-    data_offset: MemoryAddress<F>,
+    code_offset_word: WordRangeGadget<F>,
+    code_offset_lt_code_size: LtGadget<F, N_BYTES_U64>,
     tx_id: Cell<F>,
     reversion_info: ReversionInfo<F>,
     is_warm: Cell<F>,
@@ -50,13 +52,13 @@ impl<F: Field> ExecutionGadget<F> for ExtcodecopyGadget<F> {
         let external_address =
             from_bytes::expr(&external_address_word.cells[..N_BYTES_ACCOUNT_ADDRESS]);
 
-        let memory_offset = cb.query_cell_phase2();
-        let data_offset = cb.query_word_rlc();
         let memory_length = cb.query_word_rlc();
+        let memory_offset = cb.query_cell_phase2();
+        let code_offset_word = WordRangeGadget::construct(cb, N_BYTES_U64);
 
         cb.stack_pop(external_address_word.expr());
         cb.stack_pop(memory_offset.expr());
-        cb.stack_pop(data_offset.expr());
+        cb.stack_pop(code_offset_word.original_word_expr());
         cb.stack_pop(memory_length.expr());
 
         let memory_address = MemoryAddressGadget::construct(cb, memory_offset, memory_length);
@@ -81,6 +83,16 @@ impl<F: Field> ExecutionGadget<F> for ExtcodecopyGadget<F> {
         let code_size = cb.query_cell();
         cb.bytecode_length(code_hash.expr(), code_size.expr());
 
+        // Reset code offset to the maximum value of Uint64 if overflow.
+        let code_offset = select::expr(
+            code_offset_word.within_range_expr(),
+            code_offset_word.valid_value_expr(N_BYTES_U64),
+            u64::MAX.expr(),
+        );
+
+        let code_offset_lt_code_size =
+            LtGadget::construct(cb, code_offset.expr(), code_size.expr());
+
         let memory_expansion = MemoryExpansionGadget::construct(cb, [memory_address.address()]);
         let memory_copier_gas = MemoryCopierGasGadget::construct(
             cb,
@@ -101,7 +113,12 @@ impl<F: Field> ExecutionGadget<F> for ExtcodecopyGadget<F> {
                 CopyDataType::Bytecode.expr(),
                 cb.curr.state.call_id.expr(),
                 CopyDataType::Memory.expr(),
-                from_bytes::expr(&data_offset.cells),
+                // Set source start to the minimum value of code offset and code size.
+                select::expr(
+                    code_offset_lt_code_size.expr(),
+                    code_offset,
+                    code_size.expr(),
+                ),
                 code_size.expr(),
                 memory_address.offset(),
                 memory_address.length(),
@@ -131,7 +148,8 @@ impl<F: Field> ExecutionGadget<F> for ExtcodecopyGadget<F> {
             same_context,
             external_address_word,
             memory_address,
-            data_offset,
+            code_offset_word,
+            code_offset_lt_code_size,
             tx_id,
             is_warm,
             reversion_info,
@@ -154,22 +172,17 @@ impl<F: Field> ExecutionGadget<F> for ExtcodecopyGadget<F> {
     ) -> Result<(), Error> {
         self.same_context.assign_exec_step(region, offset, step)?;
 
-        let [external_address, memory_offset, data_offset, memory_length] =
+        let [external_address, memory_offset, code_offset, memory_length] =
             [0, 1, 2, 3].map(|idx| block.rws[step.rw_indices[idx]].stack_value());
         self.external_address_word
             .assign(region, offset, Some(external_address.to_le_bytes()))?;
         let memory_address =
             self.memory_address
                 .assign(region, offset, memory_offset, memory_length)?;
-        self.data_offset.assign(
-            region,
-            offset,
-            Some(
-                data_offset.to_le_bytes()[..N_BYTES_MEMORY_ADDRESS]
-                    .try_into()
-                    .unwrap(),
-            ),
-        )?;
+
+        let code_offset_within_range =
+            self.code_offset_word
+                .assign(region, offset, N_BYTES_U64, code_offset)?;
 
         self.tx_id
             .assign(region, offset, Value::known(F::from(transaction.id as u64)))?;
@@ -188,18 +201,29 @@ impl<F: Field> ExecutionGadget<F> for ExtcodecopyGadget<F> {
         self.code_hash
             .assign(region, offset, region.word_rlc(code_hash))?;
 
-        let bytecode_len = if code_hash.is_zero() {
+        let code_size = if code_hash.is_zero() {
             0
         } else {
             block
                 .bytecodes
                 .get(&code_hash)
                 .expect("could not find external bytecode")
                 .bytes
-                .len()
+                .len() as u64
         };
         self.code_size
-            .assign(region, offset, Value::known(F::from(bytecode_len as u64)))?;
+            .assign(region, offset, Value::known(F::from(code_size)))?;
+
+        self.code_offset_lt_code_size.assign(
+            region,
+            offset,
+            F::from(if code_offset_within_range {
+                code_offset.as_u64()
+            } else {
+                u64::MAX
+            }),
+            F::from(code_size),
+        )?;
 
         self.copy_rwc_inc.assign(
             region,
@@ -246,8 +270,8 @@ mod test {
 
     fn test_ok(
         external_account: Option<Account>,
+        code_offset: Word,
         memory_offset: usize,
-        data_offset: usize,
         length: usize,
         is_warm: bool,
     ) {
@@ -267,7 +291,7 @@ mod test {
         }
         code.append(&bytecode! {
             PUSH32(length)
-            PUSH32(data_offset)
+            PUSH32(code_offset)
             PUSH32(memory_offset)
             PUSH20(external_address.to_word())
             #[start]
@@ -307,8 +331,8 @@ mod test {
 
     #[test]
     fn extcodecopy_empty_account() {
-        test_ok(None, 0x00, 0x00, 0x36, true); // warm account
-        test_ok(None, 0x00, 0x00, 0x36, false); // cold account
+        test_ok(None, 0x00.into(), 0x00, 0x36, true); // warm account
+        test_ok(None, 0x00.into(), 0x00, 0x36, false); // cold account
     }
 
     #[test]
@@ -319,7 +343,7 @@ mod test {
                 code: Bytes::from([10, 40]),
                 ..Default::default()
             }),
-            0x00,
+            0x00.into(),
             0x00,
             0x36,
             true,
@@ -331,7 +355,7 @@ mod test {
                 code: Bytes::from([10, 40]),
                 ..Default::default()
             }),
-            0x00,
+            0x00.into(),
             0x00,
             0x36,
             false,
@@ -346,7 +370,7 @@ mod test {
                 code: Bytes::from(rand_bytes_array::<256>()),
                 ..Default::default()
             }),
-            0x00,
+            0x00.into(),
             0x00,
             0x36,
             true,
@@ -357,7 +381,7 @@ mod test {
                 code: Bytes::from(rand_bytes_array::<256>()),
                 ..Default::default()
             }),
-            0x00,
+            0x00.into(),
             0x00,
             0x36,
             false,
@@ -372,8 +396,8 @@ mod test {
                 code: Bytes::from(rand_bytes_array::<64>()),
                 ..Default::default()
             }),
+            0x20.into(),
             0x00,
-            0x20,
             0x104,
             true,
         );
@@ -383,10 +407,36 @@ mod test {
                 code: Bytes::from(rand_bytes_array::<64>()),
                 ..Default::default()
             }),
+            0x20.into(),
             0x00,
-            0x20,
             0x104,
             false,
         );
     }
+
+    #[test]
+    fn extcodecopy_code_offset_overflow() {
+        test_ok(
+            Some(Account {
+                address: *EXTERNAL_ADDRESS,
+                code: Bytes::from(rand_bytes_array::<256>()),
+                ..Default::default()
+            }),
+            Word::MAX,
+            0x00,
+            0x36,
+            true,
+        );
+        test_ok(
+            Some(Account {
+                address: *EXTERNAL_ADDRESS,
+                code: Bytes::from(rand_bytes_array::<256>()),
+                ..Default::default()
+            }),
+            Word::MAX,
+            0x00,
+            0x36,
+            false,
+        );
+    }
 }
```

### zkevm-circuits/src/evm_circuit/util/common_gadget.rs
```diff
@@ -931,3 +931,60 @@ impl<F: Field> CommonErrorGadget<F> {
         Ok(1u64)
     }
 }
+
+/// Check if the passed in word is within the specified range.
+#[derive(Clone, Debug)]
+pub(crate) struct WordRangeGadget<F> {
+    original: Word<F>,
+    within_range: IsZeroGadget<F>,
+}
+
+impl<F: Field> WordRangeGadget<F> {
+    pub(crate) fn construct(cb: &mut ConstraintBuilder<F>, valid_bytes: usize) -> Self {
+        // Should use a Word directly if valid byte number is 32.
+        debug_assert!(valid_bytes < 32);
+
+        let original = cb.query_word_rlc();
+        let within_range = IsZeroGadget::construct(cb, sum::expr(&original.cells[valid_bytes..]));
+
+        Self {
+            original,
+            within_range,
+        }
+    }
+
+    /// Return true if within the range, false if overflow.
+    pub(crate) fn assign(
+        &self,
+        region: &mut CachedRegion<'_, '_, F>,
+        offset: usize,
+        valid_bytes: usize,
+        original: U256,
+    ) -> Result<bool, Error> {
+        self.original
+            .assign(region, offset, Some(original.to_le_bytes()))?;
+
+        let overflow_hi = original.to_le_bytes()[valid_bytes..]
+            .iter()
+            .fold(0, |acc, val| acc + u64::from(*val));
+        self.within_range
+            .assign(region, offset, F::from(overflow_hi))?;
+
+        Ok(overflow_hi == 0)
+    }
+
+    pub(crate) fn original_word_expr(&self) -> Expression<F> {
+        self.original.expr()
+    }
+
+    pub(crate) fn valid_value_expr(&self, valid_bytes: usize) -> Expression<F> {
+        // Should use a Word directly if valid byte number is 32.
+        debug_assert!(valid_bytes < 32);
+
+        from_bytes::expr(&self.original.cells[..valid_bytes])
+    }
+
+    pub(crate) fn within_range_expr(&self) -> Expression<F> {
+        self.within_range.expr()
+    }
+}
```
