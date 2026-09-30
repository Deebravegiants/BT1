# [?] Fix to support overflow memory start and zero memory size in logs. (#389)

## Summary
Severity: Unknown
Chain: ZK
Component: scroll-tech/zkevm-circuits
Published: 2023-03-09
Source: https://github.com/scroll-tech/zkevm-circuits/commit/44b03b3616c1aed138c0417672f9d2db5c66dcf9
Type: security-commit

## Details
Fix to support overflow memory start and zero memory size in logs. (#389)

## Patch
### bus-mapping/src/circuit_input_builder/input_state_ref.rs
```diff
@@ -1574,4 +1574,39 @@ impl<'a> CircuitInputStateRef<'a> {
 
         Ok(copy_steps)
     }
+
+    pub(crate) fn gen_copy_steps_for_log(
+        &mut self,
+        exec_step: &mut ExecStep,
+        src_addr: u64,
+        bytes_left: u64,
+    ) -> Result<Vec<(u8, bool)>, Error> {
+        // Get memory data
+        let mem = self
+            .call_ctx()?
+            .memory
+            .read_chunk(src_addr.into(), bytes_left.into());
+
+        let mut copy_steps = Vec::with_capacity(bytes_left as usize);
+        for (idx, byte) in mem.iter().enumerate() {
+            let addr = src_addr + idx as u64;
+
+            // Read memory
+            self.memory_read(exec_step, (addr as usize).into(), *byte)?;
+
+            copy_steps.push((*byte, false));
+
+            // Write log
+            self.tx_log_write(
+                exec_step,
+                self.tx_ctx.id(),
+                self.tx_ctx.log_id + 1,
+                TxLogField::Data,
+                idx,
+                Word::from(*byte),
+            )?;
+        }
+
+        Ok(copy_steps)
+    }
 }
```

### bus-mapping/src/evm/opcodes/logs.rs
```diff
@@ -23,14 +23,18 @@ impl Opcode for Log {
         }
 
         // reconstruction
-        let offset = geth_step.stack.nth_last(0)?.as_usize();
-        let length = geth_step.stack.nth_last(1)?.as_usize();
+        let offset = geth_step.stack.nth_last(0)?;
+        let length = geth_step.stack.nth_last(1)?.as_u64();
 
         if length != 0 {
-            state
-                .call_ctx_mut()?
-                .memory
-                .extend_at_least(offset + length);
+            // Offset should be within range of Uint64 if length is non-zero.
+            let memory_length = offset
+                .as_u64()
+                .checked_add(length)
+                .and_then(|val| usize::try_from(val).ok())
+                .unwrap();
+
+            state.call_ctx_mut()?.memory.extend_at_least(memory_length);
         }
 
         Ok(vec![exec_step])
@@ -127,41 +131,6 @@ fn gen_log_step(
     Ok(exec_step)
 }
 
-fn gen_copy_steps(
-    state: &mut CircuitInputStateRef,
-    exec_step: &mut ExecStep,
-    src_addr: u64,
-    bytes_left: usize,
-) -> Result<Vec<(u8, bool)>, Error> {
-    // Get memory data
-    let mem = state
-        .call_ctx()?
-        .memory
-        .read_chunk(src_addr.into(), bytes_left.into());
-
-    let mut copy_steps = Vec::with_capacity(bytes_left);
-    for (idx, byte) in mem.iter().enumerate() {
-        let addr = src_addr + idx as u64;
-
-        // Read memory
-        state.memory_read(exec_step, (addr as usize).into(), *byte)?;
-
-        copy_steps.push((*byte, false));
-
-        // Write log
-        state.tx_log_write(
-            exec_step,
-            state.tx_ctx.id(),
-            state.tx_ctx.log_id + 1,
-            TxLogField::Data,
-            idx,
-            Word::from(*byte),
-        )?;
-    }
-
-    Ok(copy_steps)
-}
-
 fn gen_copy_event(
     state: &mut CircuitInputStateRef,
     geth_step: &GethExecStep,
@@ -170,12 +139,15 @@ fn gen_copy_event(
     let rw_counter_start = state.block_ctx.rwc;
 
     assert!(state.call()?.is_persistent, "Error: Call is not persistent");
-    let memory_start = geth_step.stack.nth_last(0)?.as_u64();
-    let msize = geth_step.stack.nth_last(1)?.as_usize();
 
-    let (src_addr, src_addr_end) = (memory_start, memory_start + msize as u64);
+    // Get low Uint64 for memory start as below reference. Memory size must be
+    // within range of Uint64, otherwise returns ErrGasUintOverflow.
+    // https://github.com/ethereum/go-ethereum/blob/b80f05bde2c4e93ae64bb3813b6d67266b5fc0e6/core/vm/instructions.go#L850
+    let memory_start = geth_step.stack.nth_last(0)?.low_u64();
+    let msize = geth_step.stack.nth_last(1)?.as_u64();
 
-    let steps = gen_copy_steps(state, exec_step, src_addr, msize)?;
+    let (src_addr, src_addr_end) = (memory_start, memory_start.checked_add(msize).unwrap());
+    let steps = state.gen_copy_steps_for_log(exec_step, src_addr, msize)?;
 
     Ok(CopyEvent {
         src_type: CopyDataType::Memory,
```

### zkevm-circuits/src/evm_circuit/execution/logs.rs
```diff
@@ -1,10 +1,10 @@
 use crate::{
     evm_circuit::{
         execution::ExecutionGadget,
-        param::N_BYTES_MEMORY_WORD_SIZE,
+        param::{N_BYTES_MEMORY_WORD_SIZE, N_BYTES_U64},
         step::ExecutionState,
         util::{
-            common_gadget::SameContextGadget,
+            common_gadget::{SameContextGadget, WordByteRangeGadget},
             constraint_builder::{
                 ConstraintBuilder, StepStateTransition,
                 Transition::{Delta, To},
@@ -26,6 +26,8 @@ use halo2_proofs::{circuit::Value, plonk::Error};
 #[derive(Clone, Debug)]
 pub(crate) struct LogGadget<F> {
     same_context: SameContextGadget<F>,
+    // TODO: It has a duplicate word with `memory_address`.
+    mstart_word: WordByteRangeGadget<F, N_BYTES_U64>,
     // memory address
     memory_address: MemoryAddressGadget<F>,
     phase2_topics: [Cell<F>; 4],
@@ -45,12 +47,13 @@ impl<F: Field> ExecutionGadget<F> for LogGadget<F> {
     const EXECUTION_STATE: ExecutionState = ExecutionState::LOG;
 
     fn configure(cb: &mut ConstraintBuilder<F>) -> Self {
-        let mstart = cb.query_cell_phase2();
+        let mstart_word = WordByteRangeGadget::construct(cb);
         let msize = cb.query_word_rlc();
 
         // Pop mstart_address, msize from stack
-        cb.stack_pop(mstart.expr());
+        cb.stack_pop(mstart_word.original_word());
         cb.stack_pop(msize.expr());
+
         // read tx id
         let tx_id = cb.call_context(None, CallContextFieldTag::TxId);
         // constrain not in static call
@@ -115,8 +118,16 @@ impl<F: Field> ExecutionGadget<F> for LogGadget<F> {
         }
 
         // check memory copy
+        let mstart = cb.query_cell_phase2();
         let memory_address = MemoryAddressGadget::construct(cb, mstart, msize);
 
+        cb.condition(mstart_word.overflow(), |cb| {
+            cb.require_zero(
+                "Memory size must be zero if memory start is overflow",
+                memory_address.has_length(),
+            );
+        });
+
         // Calculate the next memory size and the gas cost for this memory
         // access
         let memory_expansion = MemoryExpansionGadget::construct(cb, [memory_address.address()]);
@@ -169,6 +180,7 @@ impl<F: Field> ExecutionGadget<F> for LogGadget<F> {
 
         Self {
             same_context,
+            mstart_word,
             memory_address,
             phase2_topics,
             topic_selectors,
@@ -195,6 +207,8 @@ impl<F: Field> ExecutionGadget<F> for LogGadget<F> {
         let [memory_start, msize] =
             [step.rw_indices[0], step.rw_indices[1]].map(|idx| block.rws[idx].stack_value());
 
+        self.mstart_word.assign(region, offset, memory_start)?;
+
         let memory_address = self
             .memory_address
             .assign(region, offset, memory_start, msize)?;
@@ -270,15 +284,16 @@ mod test {
     fn log_gadget_simple() {
         // 1. tests for is_persistent = true cases
         // zero topic: log0
-        test_log_ok(&[], true);
+        test_log_ok(&[], true, None);
         // one topic: log1
-        test_log_ok(&[Word::from(0xA0)], true);
+        test_log_ok(&[Word::from(0xA0)], true, None);
         // two topics: log2
-        test_log_ok(&[Word::from(0xA0), Word::from(0xef)], true);
+        test_log_ok(&[Word::from(0xA0), Word::from(0xef)], true, None);
         // three topics: log3
         test_log_ok(
             &[Word::from(0xA0), Word::from(0xef), Word::from(0xb0)],
             true,
+            None,
         );
         // four topics: log4
         test_log_ok(
@@ -289,13 +304,14 @@ mod test {
                 Word::from(0x37),
             ],
             true,
+            None,
         );
 
         // 2. tests for is_persistent = false cases
         // log0
-        test_log_ok(&[], false);
+        test_log_ok(&[], false, None);
         // log1
-        test_log_ok(&[Word::from(0xA0)], false);
+        test_log_ok(&[Word::from(0xA0)], false, None);
         // log4
         test_log_ok(
             &[
@@ -305,6 +321,7 @@ mod test {
                 Word::from(0x37),
             ],
             false,
+            None,
         );
     }
 
@@ -327,8 +344,41 @@ mod test {
         ]);
     }
 
+    #[test]
+    fn log_gadget_with_overflow_mstart_and_zero_msize() {
+        let stack = Some(Stack {
+            mstart: Word::MAX,
+            msize: Word::zero(),
+        });
+
+        test_log_ok(&[], false, stack);
+        test_log_ok(&[Word::from(0xA0)], true, stack);
+        test_log_ok(&[Word::from(0xA0), Word::from(0xef)], false, stack);
+        test_log_ok(
+            &[Word::from(0xA0), Word::from(0xef), Word::from(0xb0)],
+            true,
+            stack,
+        );
+        test_log_ok(
+            &[
+                Word::from(0xA0),
+                Word::from(0xef),
+                Word::from(0xb0),
+                Word::from(0x37),
+            ],
+            true,
+            stack,
+        );
+    }
+
+    #[derive(Clone, Copy)]
+    struct Stack {
+        mstart: Word,
+        msize: Word,
+    }
+
     // test single log code and single copy log step
-    fn test_log_ok(topics: &[Word], is_persistent: bool) {
+    fn test_log_ok(topics: &[Word], is_persistent: bool, stack: Option<Stack>) {
         let mut pushdata = [0u8; 320];
         rand::thread_rng().try_fill(&mut pushdata[..]).unwrap();
         let mut code_prepare = prepare_code(&pushdata, 1);
@@ -345,15 +395,17 @@ mod test {
         let cur_op_code = log_codes[topic_count];
 
         // use more than 256 for testing offset rlc
-        let mstart = 0x102usize;
-        let msize = 0x20usize;
+        let stack = stack.unwrap_or(Stack {
+            mstart: 0x102_usize.into(),
+            msize: 0x20_usize.into(),
+        });
         let mut code = Bytecode::default();
         // make dynamic topics push operations
         for topic in topics {
             code.push(32, *topic);
         }
-        code.push(32, Word::from(msize));
-        code.push(32, Word::from(mstart));
+        code.push(32, stack.msize);
+        code.push(32, stack.mstart);
         code.write_op(cur_op_code);
         if is_persistent {
             code.write_op(OpcodeId::STOP);
```
