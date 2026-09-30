# [?] Fix to handle successful run with Uint64 overflow for multiple opcodes (#1317)

## Summary
Severity: Unknown
Chain: ZK
Component: privacy-ethereum/zkevm-circuits
Published: 2023-04-28
Source: https://github.com/privacy-ethereum/zkevm-circuits/commit/22dd26396c0268ed7c7adfa236ff2d7954a9d470
Type: security-commit

## Details
Fix to handle successful run with Uint64 overflow for multiple opcodes (#1317)

### Description

Fix successful run cases with Uint64 overflow for multiple opcodes.

1. Add `WordByteRangeGadget` to constrain if Word is within the
specified byte range.

2. Add `WordByteCapGadget` to constrain if Word is within the specified
byte range (implemented by WordByteRangeGadget) and less than a maximum
cap (used to replace a WordByteRangeGadget and LtGadget).

3. Fix bus-mapping and zkevm-circuits to handle overflow cases. And add
unit-tests for these cases.

TODO: will try to handle memory offset overflow with zero length in
another PR (try to rebase for this local PR
https://github.com/scroll-tech/zkevm-circuits/pull/393) and related
issue
https://github.com/privacy-scaling-explorations/zkevm-circuits/issues/1301.

### Rationale

Reference detailed code in `go-etherum` as:

.
[BLOCKHASH](https://github.com/ethereum/go-ethereum/blob/master/core/vm/instructions.go#L438)
.
[CALLDATALOAD](https://github.com/ethereum/go-ethereum/blob/master/core/vm/instructions.go#L285)
.
[CALLDATACOPY](https://github.com/ethereum/go-ethereum/blob/master/core/vm/instructions.go#L306)
.
[CODECOPY](https://github.com/ethereum/go-ethereum/blob/master/core/vm/instructions.go#L364)
.
[EXTCODECOPY](https://github.com/ethereum/go-ethereum/blob/master/core/vm/instructions.go#L382)
.
[JUMPI](https://github.com/ethereum/go-ethereum/blob/master/core/vm/instructions.go#L550)

### Issue Link

Close
https://github.com/privacy-scaling-explorations/zkevm-circuits/issues/1276

### Type of change

- [X] Bug fix (non-breaking change which fixes an issue)

### How Has This Been Tested?

Add unit-test cases for Uint64 overflow values.

---------

Co-authored-by: Zhang Zhuo <mycinbrin@gmail.com>

## Patch
### bus-mapping/src/circuit_input_builder/input_state_ref.rs
```diff
@@ -20,7 +20,7 @@ use eth_types::{
     evm_types::{
         gas_utils::memory_expansion_gas_cost, Gas, GasCost, MemoryAddress, OpcodeId, StackAddress,
     },
-    Address, GethExecStep, ToAddress, ToBigEndian, ToWord, Word, H256, U256,
+    Address, Bytecode, GethExecStep, ToAddress, ToBigEndian, ToWord, Word, H256, U256,
 };
 use ethers_core::utils::{get_contract_address, get_create2_address};
 use std::cmp::max;
@@ -1348,4 +1348,63 @@ impl<'a> CircuitInputStateRef<'a> {
         }
         Ok(())
     }
+
+    /// Generate copy steps for bytecode.
+    pub(crate) fn gen_copy_steps_for_bytecode(
+        &mut self,
+        exec_step: &mut ExecStep,
+        bytecode: &Bytecode,
+        src_addr: u64,
+        dst_addr: u64,
+        src_addr_end: u64,
+        bytes_left: u64,
+    ) -> Result<Vec<(u8, bool)>, Error> {
+        let mut copy_steps = Vec::with_capacity(bytes_left as usize);
+        for idx in 0..bytes_left {
+            let addr = src_addr.checked_add(idx).unwrap_or(src_addr_end);
+            let step = if addr < src_addr_end {
+                let code = bytecode.code.get(addr as usize).unwrap();
+                (code.value, code.is_code)
+            } else {
+                (0, false)
+            };
+            copy_steps.push(step);
+            self.memory_write(exec_step, (dst_addr + idx).into(), step.0)?;
+        }
+
+        Ok(copy_steps)
+    }
+
+    /// Generate copy steps for call data.
+    pub(crate) fn gen_copy_steps_for_call_data(
+        &mut self,
+        exec_step: &mut ExecStep,
+        src_addr: u64,
+        dst_addr: u64,
+        src_addr_end: u64,
+        bytes_left: u64,
+    ) -> Result<Vec<(u8, bool)>, Error> {
+        let mut copy_steps = Vec::with_capacity(bytes_left as usize);
+        for idx in 0..bytes_left {
+            let addr = src_addr.checked_add(idx).unwrap_or(src_addr_end);
+            let value = if addr < src_addr_end {
+                let byte =
+                    self.call_ctx()?.call_data[(addr - self.call()?.call_data_offset) as usize];
+                if !self.call()?.is_root {
+                    self.push_op(
+                        exec_step,
+                        RW::READ,
+                        MemoryOp::new(self.call()?.caller_id, addr.into(), byte),
+                    );
+                }
+                byte
+            } else {
+                0
+            };
+            copy_steps.push((value, false));
+            self.memory_write(exec_step, (dst_addr + idx).into(), value)?;
+        }
+
+        Ok(copy_steps)
+    }
 }
```

### bus-mapping/src/evm/opcodes/calldatacopy.rs
```diff
@@ -3,7 +3,7 @@ use crate::{
     circuit_input_builder::{
         CircuitInputStateRef, CopyDataType, CopyEvent, ExecStep, NumberOrHash,
     },
-    operation::{CallContextField, MemoryOp, RW},
+    operation::CallContextField,
     Error,
 };
 use eth_types::GethExecStep;
@@ -20,13 +20,13 @@ impl Opcode for Calldatacopy {
         let mut exec_steps = vec![gen_calldatacopy_step(state, geth_step)?];
 
         // reconstruction
-        let memory_offset = geth_step.stack.nth_last(0)?.as_u64();
-        let data_offset = geth_step.stack.nth_last(1)?.as_u64();
-        let length = geth_step.stack.nth_last(2)?.as_usize();
+        let memory_offset = geth_step.stack.nth_last(0)?;
+        let data_offset = geth_step.stack.nth_last(1)?;
+        let length = geth_step.stack.nth_last(2)?;
         let call_ctx = state.call_ctx_mut()?;
         let memory = &mut call_ctx.memory;
 
-        memory.copy_from(memory_offset, &call_ctx.call_data, data_offset, length);
+        memory.copy_from(memory_offset, data_offset, length, &call_ctx.call_data);
 
         let copy_event = gen_copy_event(state, geth_step)?;
         state.push_copy(&mut exec_steps[0], copy_event);
@@ -92,64 +92,36 @@ fn gen_calldatacopy_step(
     Ok(exec_step)
 }
 
-fn gen_copy_steps(
-    state: &mut CircuitInputStateRef,
-    exec_step: &mut ExecStep,
-    src_addr: u64,
-    dst_addr: u64,
-    src_addr_end: u64,
-    bytes_left: u64,
-    is_root: bool,
-) -> Result<Vec<(u8, bool)>, Error> {
-    let mut copy_steps = Vec::with_capacity(bytes_left as usize);
-    for idx in 0..bytes_left {
-        let addr = src_addr + idx;
-        let value = if addr < src_addr_end {
-            let byte =
-                state.call_ctx()?.call_data[(addr - state.call()?.call_data_offset) as usize];
-            if !is_root {
-                state.push_op(
-                    exec_step,
-                    RW::READ,
-                    MemoryOp::new(state.call()?.caller_id, addr.into(), byte),
-                );
-            }
-            byte
-        } else {
-            0
-        };
-        copy_steps.push((value, false));
-        state.memory_write(exec_step, (dst_addr + idx).into(), value)?;
-    }
-
-    Ok(copy_steps)
-}
-
 fn gen_copy_event(
     state: &mut CircuitInputStateRef,
     geth_step: &GethExecStep,
 ) -> Result<CopyEvent, Error> {
     let rw_counter_start = state.block_ctx.rwc;
-    let memory_offset = geth_step.stack.nth_last(0)?.as_u64();
-    let data_offset = geth_step.stack.nth_last(1)?.as_u64();
+
+    let memory_offset = geth_step.stack.nth_last(0)?;
+    let data_offset = geth_step.stack.nth_last(1)?;
     let length = geth_step.stack.nth_last(2)?.as_u64();
 
     let call_data_offset = state.call()?.call_data_offset;
     let call_data_length = state.call()?.call_data_length;
-    let (src_addr, src_addr_end) = (
-        call_data_offset + data_offset,
-        call_data_offset + call_data_length,
-    );
+
+    let dst_addr = memory_offset.as_u64();
+    let src_addr_end = call_data_offset.checked_add(call_data_length).unwrap();
+
+    // Reset start offset to end offset if overflow.
+    let src_addr = u64::try_from(data_offset)
+        .ok()
+        .and_then(|offset| offset.checked_add(call_data_offset))
+        .unwrap_or(src_addr_end)
+        .min(src_addr_end);
 
     let mut exec_step = state.new_step(geth_step)?;
-    let copy_steps = gen_copy_steps(
-        state,
+    let copy_steps = state.gen_copy_steps_for_call_data(
         &mut exec_step,
         src_addr,
-        memory_offset,
+        dst_addr,
         src_addr_end,
         length,
-        state.call()?.is_root,
     )?;
 
     let (src_type, src_id) = if state.call()?.is_root {
@@ -165,7 +137,7 @@ fn gen_copy_event(
         src_addr_end,
         dst_type: CopyDataType::Memory,
         dst_id: NumberOrHash::Number(state.call()?.call_id),
-        dst_addr: memory_offset,
+        dst_addr,
         log_id: None,
         rw_counter_start,
         bytes: copy_steps,
```

### bus-mapping/src/evm/opcodes/calldataload.rs
```diff
@@ -23,73 +23,79 @@ impl Opcode for Calldataload {
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
+            // Stack push `0` as result if overflow.
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
@@ -20,18 +20,17 @@ impl Opcode for Codecopy {
         let mut exec_steps = vec![gen_codecopy_step(state, geth_step)?];
 
         // reconstruction
-
-        let dest_offset = geth_step.stack.nth_last(0)?.as_u64();
-        let code_offset = geth_step.stack.nth_last(1)?.as_u64();
-        let length = geth_step.stack.nth_last(2)?.as_u64();
+        let dst_offset = geth_step.stack.nth_last(0)?;
+        let code_offset = geth_step.stack.nth_last(1)?;
+        let length = geth_step.stack.nth_last(2)?;
 
         let code_hash = state.call()?.code_hash;
         let code = state.code(code_hash)?;
 
         let call_ctx = state.call_ctx_mut()?;
         let memory = &mut call_ctx.memory;
 
-        memory.copy_from(dest_offset, &code, code_offset, length as usize);
+        memory.copy_from(dst_offset, code_offset, length, &code);
 
         let copy_event = gen_copy_event(state, geth_step)?;
         state.push_copy(&mut exec_steps[0], copy_event);
@@ -65,56 +64,46 @@ fn gen_codecopy_step(
     Ok(exec_step)
 }
 
-fn gen_copy_steps(
-    state: &mut CircuitInputStateRef,
-    exec_step: &mut ExecStep,
-    src_addr: u64,
-    dst_addr: u64,
-    bytes_left: u64,
-    bytecode: &Bytecode,
-) -> Result<Vec<(u8, bool)>, Error> {
-    let mut steps = Vec::with_capacity(bytes_left as usize);
-    for idx in 0..bytes_left {
-        let addr = src_addr + idx;
-        let bytecode_element = bytecode.get(addr as usize).unwrap_or_default();
-        steps.push((bytecode_element.value, bytecode_element.is_code));
-        state.memory_write(exec_step, (dst_addr + idx).into(), bytecode_element.value)?;
-    }
-    Ok(steps)
-}
-
 fn gen_copy_event(
     state: &mut CircuitInputStateRef,
     geth_step: &GethExecStep,
 ) -> Result<CopyEvent, Error> {
     let rw_counter_start = state.block_ctx.rwc;
 
-    let dst_offset = geth_step.stack.nth_last(0)?.as_u64();
-    let code_offset = geth_step.stack.nth_last(1)?.as_u64();
+    let dst_offset = geth_step.stack.nth_last(0)?;
+    let code_offset = geth_step.stack.nth_last(1)?;
     let length = geth_step.stack.nth_last(2)?.as_u64();
 
     let code_hash = state.call()?.code_hash;
     let bytecode: Bytecode = state.code(code_hash)?.into();
-    let src_addr_end = bytecode.to_vec().len() as u64;
+    let code_size = bytecode.code.len() as u64;
+
+    let dst_addr = dst_offset.as_u64();
+    let src_addr_end = code_size;
+
+    // Reset start offset to end offset if overflow.
+    let src_addr = u64::try_from(code_offset)
+        .unwrap_or(src_addr_end)
+        .min(src_addr_end);
 
     let mut exec_step = state.new_step(geth_step)?;
-    let copy_steps = gen_copy_steps(
-        state,
+    let copy_steps = state.gen_copy_steps_for_bytecode(
         &mut exec_step,
-        code_offset,
-        dst_offset,
-        length,
         &bytecode,
+        src_addr,
+        dst_addr,
+        src_addr_end,
+        length,
     )?;
 
     Ok(CopyEvent {
         src_type: CopyDataType::Bytecode,
         src_id: NumberOrHash::Hash(code_hash),
-        src_addr: code_offset,
+        src_addr,
         src_addr_end,
         dst_type: CopyDataType::Memory,
         dst_id: NumberOrHash::Number(state.call()?.call_id),
-        dst_addr: dst_offset,
+        dst_addr,
         log_id: None,
         rw_counter_start,
         bytes: copy_steps,
```

### bus-mapping/src/evm/opcodes/extcodecopy.rs
```diff
@@ -24,9 +24,9 @@ impl Opcode for Extcodecopy {
 
         // reconstruction
         let address = geth_steps[0].stack.nth_last(0)?.to_address();
-        let dest_offset = geth_steps[0].stack.nth_last(1)?.as_u64();
-        let code_offset = geth_steps[0].stack.nth_last(2)?.as_u64();
-        let length = geth_steps[0].stack.nth_last(3)?.as_u64();
+        let dst_offset = geth_steps[0].stack.nth_last(1)?;
+        let code_offset = geth_step.stack.nth_last(2)?;
+        let length = geth_steps[0].stack.nth_last(3)?;
 
         let (_, account) = state.sdb.get_account(&address);
         let code_hash = account.code_hash;
@@ -35,7 +35,7 @@ impl Opcode for Extcodecopy {
         let call_ctx = state.call_ctx_mut()?;
         let memory = &mut call_ctx.memory;
 
-        memory.copy_from(dest_offset, &code, code_offset, length as usize);
+        memory.copy_from(dst_offset, code_offset, length, &code);
 
         let copy_event = gen_copy_event(state, geth_step)?;
         state.push_copy(&mut exec_steps[0], copy_event);
@@ -111,39 +111,15 @@ fn gen_extcodecopy_step(
     Ok(exec_step)
 }
 
-fn gen_copy_steps(
-    state: &mut CircuitInputStateRef,
-    exec_step: &mut ExecStep,
-    src_addr: u64,
-    dst_addr: u64,
-    src_addr_end: u64,
-    bytes_left: u64,
-    code: &Bytecode,
-) -> Result<Vec<(u8, bool)>, Error> {
-    let mut copy_steps = Vec::with_capacity(bytes_left as usize);
-    for idx in 0..bytes_left {
-        let addr = src_addr + idx;
-        let step = if addr < src_addr_end {
-            let code = code.code.get(addr as usize).unwrap();
-            (code.value, code.is_code)
-        } else {
-            (0, false)
-        };
-        copy_steps.push(step);
-        state.memory_write(exec_step, (dst_addr + idx).into(), step.0)?;
-    }
-
-    Ok(copy_steps)
-}
-
 fn gen_copy_event(
     state: &mut CircuitInputStateRef,
     geth_step: &GethExecStep,
 ) -> Result<CopyEvent, Error> {
     let rw_counter_start = state.block_ctx.rwc;
+
     let external_address = geth_step.stack.nth_last(0)?.to_address();
-    let memory_offset = geth_step.stack.nth_last(1)?.as_u64();
-    let data_offset = geth_step.stack.nth_last(2)?.as_u64();
+    let dst_offset = geth_step.stack.nth_last(1)?;
+    let code_offset = geth_step.stack.nth_last(2)?;
     let length = geth_step.stack.nth_last(3)?.as_u64();
 
     let account = state.sdb.get_account(&external_address).1;
@@ -154,28 +130,37 @@ fn gen_copy_event(
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
+
+    let dst_addr = dst_offset.as_u64();
+    let src_addr_end = code_size;
+
+    // Reset start offset to end offset if overflow.
+    let src_addr = u64::try_from(code_offset)
+        .unwrap_or(src_addr_end)
+        .min(src_addr_end);
+
     let mut exec_step = state.new_step(geth_step)?;
-    let copy_steps = gen_copy_steps(
-        state,
+    let copy_steps = state.gen_copy_steps_for_bytecode(
         &mut exec_step,
-        data_offset,
-        memory_offset,
+        &bytecode,
+        src_addr,
+        dst_addr,
         src_addr_end,
         length,
-        &code,
     )?;
+
     Ok(CopyEvent {
-        src_addr: data_offset,
+        src_addr,
         src_addr_end,
         src_type: CopyDataType::Bytecode,
         src_id: NumberOrHash::Hash(code_hash),
-        dst_addr: memory_offset,
+        dst_addr,
         dst_type: CopyDataType::Memory,
         dst_id: NumberOrHash::Number(state.call()?.call_id),
         log_id: None,
```

### bus-mapping/src/evm/opcodes/returndatacopy.rs
```diff
@@ -21,17 +21,16 @@ impl Opcode for Returndatacopy {
 
         // reconstruction
         let geth_step = &geth_steps[0];
-        let dest_offset = geth_step.stack.nth_last(0)?;
-        let offset = geth_step.stack.nth_last(1)?;
-        let size = geth_step.stack.nth_last(2)?;
+        let dst_offset = geth_step.stack.nth_last(0)?;
+        let src_offset = geth_step.stack.nth_last(1)?;
+        let length = geth_step.stack.nth_last(2)?;
 
         // can we reduce this clone?
         let return_data = state.call_ctx()?.return_data.clone();
 
         let call_ctx = state.call_ctx_mut()?;
         let memory = &mut call_ctx.memory;
-        let length = size.as_usize();
-        memory.copy_from(dest_offset.as_u64(), &return_data, offset.as_u64(), length);
+        memory.copy_from(dst_offset, src_offset, length, &return_data);
 
         let copy_event = gen_copy_event(state, geth_step)?;
         state.push_copy(&mut exec_steps[0], copy_event);
```

### eth-types/src/evm_types/memory.rs
```diff
@@ -329,17 +329,29 @@ impl Memory {
     }
 
     /// Copy source data to memory. Used in (ext)codecopy/calldatacopy.
-    pub fn copy_from(&mut self, dst_offset: u64, data: &[u8], data_offset: u64, length: usize) {
-        // https://github.com/ethereum/go-ethereum/blob/df52967ff6080a27243569020ff64cd956fb8362/core/vm/instructions.go#L312
+    pub fn copy_from(&mut self, dst_offset: Word, src_offset: Word, length: Word, data: &[u8]) {
+        // Reference go-ethereum `opCallDataCopy` function for defails.
+        // https://github.com/ethereum/go-ethereum/blob/bb4ac2d396de254898a5f44b1ea2086bfe5bd193/core/vm/instructions.go#L299
+
+        // `length` should be checked for overflow during gas cost calculation.
+        // Otherwise should return an out of gas error previously.
+        let length = length.as_usize();
         if length != 0 {
+            // `dst_offset` should be within range if length is non-zero.
+            // https://github.com/ethereum/go-ethereum/blob/bb4ac2d396de254898a5f44b1ea2086bfe5bd193/core/vm/common.go#L37
+            let dst_offset = dst_offset.as_u64();
+
+            // Reset data offset to the maximum value of Uint64 if overflow.
+            let src_offset = u64::try_from(src_offset).unwrap_or(u64::MAX);
+
             let minimal_length = dst_offset as usize + length;
             self.extend_at_least(minimal_length);
 
             let mem_starts = dst_offset as usize;
             let mem_ends = mem_starts + length;
             let dst_slice = &mut self.0[mem_starts..mem_ends];
             dst_slice.fill(0);
-            let data_starts = data_offset as usize;
+            let data_starts = src_offset as usize;
             let actual_length = std::cmp::min(
                 length,
                 data.len().checked_sub(data_starts).unwrap_or_default(),
```

### zkevm-circuits/src/evm_circuit/execution/blockhash.rs
```diff
@@ -4,14 +4,14 @@ use crate::{
         param::N_BYTES_U64,
         step::ExecutionState,
         util::{
-            common_gadget::SameContextGadget,
+            and,
+            common_gadget::{SameContextGadget, WordByteCapGadget},
             constraint_builder::{
                 ConstrainBuilderCommon, EVMConstraintBuilder, StepStateTransition,
                 Transition::Delta,
             },
-            from_bytes,
             math_gadget::LtGadget,
-            CachedRegion, Cell, RandomLinearCombination, Word,
+            CachedRegion, Cell, Word,
         },
         witness::{Block, Call, ExecStep, Transaction},
     },
@@ -26,10 +26,9 @@ use halo2_proofs::{circuit::Value, plonk::Error};
 #[derive(Clone, Debug)]
 pub(crate) struct BlockHashGadget<F> {
     same_context: SameContextGadget<F>,
-    block_number: RandomLinearCombination<F, N_BYTES_U64>,
+    block_number: WordByteCapGadget<F, N_BYTES_U64>,
     current_block_number: Cell<F>,
     block_hash: Word<F>,
-    block_lt: LtGadget<F, N_BYTES_U64>,
     diff_lt: LtGadget<F, N_BYTES_U64>,
 }
 
@@ -39,38 +38,39 @@ impl<F: Field> ExecutionGadget<F> for BlockHashGadget<F> {
     const EXECUTION_STATE: ExecutionState = ExecutionState::BLOCKHASH;
 
     fn configure(cb: &mut EVMConstraintBuilder<F>) -> Self {
-        let block_number = cb.query_word_rlc();
-        cb.stack_pop(block_number.expr());
-
         let current_block_number = cb.query_cell();
         cb.block_lookup(
             BlockContextFieldTag::Number.expr(),
             None,
             current_block_number.expr(),
         );
 
-        let block_lt = LtGadget::construct(
-            cb,
-            from_bytes::expr(&block_number.cells),
-            current_block_number.expr(),
-        );
+        let block_number = WordByteCapGadget::construct(cb, current_block_number.expr());
+        cb.stack_pop(block_number.original_word());
+
+        let block_hash = cb.query_word_rlc();
 
         let diff_lt = LtGadget::construct(
             cb,
             current_block_number.expr(),
-            257.expr() + from_bytes::expr(&block_number.cells),
+            257.expr() + block_number.valid_value(),
         );
 
-        let block_hash = cb.query_word_rlc();
-        cb.condition(block_lt.expr() * diff_lt.expr(), |cb| {
+        let is_valid = and::expr([block_number.lt_cap(), diff_lt.expr()]);
+
+        cb.condition(is_valid.expr(), |cb| {
             cb.block_lookup(
                 BlockContextFieldTag::BlockHash.expr(),
-                Some(from_bytes::expr(&block_number.cells)),
+                Some(block_number.valid_value()),
                 block_hash.expr(),
             );
         });
-        cb.condition(not::expr(block_lt.expr() * diff_lt.expr()), |cb| {
-            cb.require_zero("invalid range", block_hash.expr());
+
+        cb.condition(not::expr(is_valid), |cb| {
+            cb.require_zero(
+                "Invalid block number for block hash lookup",
+                block_hash.expr(),
+            );
         });
 
         cb.stack_push(block_hash.expr());
@@ -89,7 +89,6 @@ impl<F: Field> ExecutionGadget<F> for BlockHashGadget<F> {
             block_number,
             current_block_number,
             block_hash,
-            block_lt,
             diff_lt,
         }
     }
@@ -105,44 +104,29 @@ impl<F: Field> ExecutionGadget<F> for BlockHashGadget<F> {
     ) -> Result<(), Error> {
         self.same_context.assign_exec_step(region, offset, step)?;
 
+        let current_block_number = block.context.number;
+        let current_block_number = current_block_number
+            .to_scalar()
+            .expect("unexpected U256 -> Scalar conversion failure");
+
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
-        let block_number: F = block_number.to_scalar().unwrap();
+        self.block_number
+            .assign(region, offset, block_number, current_block_number)?;
 
-        let current_block_number = block.context.number;
-        self.current_block_number.assign(
-            region,
-            offset,
-            Value::known(
-                current_block_number
-                    .to_scalar()
-                    .expect("unexpected U256 -> Scalar conversion failure"),
-            ),
-        )?;
-        let current_block_number: F = current_block_number.to_scalar().unwrap();
+        self.current_block_number
+            .assign(region, offset, Value::known(current_block_number))?;
 
         self.block_hash.assign(
             region,
             offset,
             Some(block.rws[step.rw_indices[1]].stack_value().to_le_bytes()),
         )?;
 
-        self.block_lt
-            .assign(region, offset, block_number, current_block_number)?;
-
         self.diff_lt.assign(
             region,
             offset,
             current_block_number,
-            block_number + F::from(257),
+            F::from(u64::try_from(block_number).unwrap_or(u64::MAX)) + F::from(257),
         )?;
 
         Ok(())
@@ -155,7 +139,7 @@ mod test {
     use eth_types::{bytecode, U256};
     use mock::test_ctx::{helpers::*, TestContext};
 
-    fn test_ok(block_number: usize, current_block_number: u64) {
+    fn test_ok(block_number: U256, current_block_number: u64) {
         let code = bytecode! {
             PUSH32(block_number)
             BLOCKHASH
@@ -185,21 +169,26 @@ mod test {
 
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
@@ -1,25 +1,24 @@
 use crate::{
     evm_circuit::{
         execution::ExecutionGadget,
-        param::{N_BYTES_MEMORY_ADDRESS, N_BYTES_MEMORY_WORD_SIZE},
+        param::{N_BYTES_MEMORY_WORD_SIZE, N_BYTES_U64},
         step::ExecutionState,
         util::{
-            common_gadget::SameContextGadget,
+            common_gadget::{SameContextGadget, WordByteCapGadget},
             constraint_builder::{
                 ConstrainBuilderCommon, EVMConstraintBuilder, StepStateTransition,
                 Transition::{Delta, To},
             },
-            from_bytes,
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
@@ -28,7 +27,7 @@ use std::cmp::min;
 pub(crate) struct CallDataCopyGadget<F> {
     same_context: SameContextGadget<F>,
     memory_address: MemoryAddressGadget<F>,
-    data_offset: MemoryAddress<F>,
+    data_offset: WordByteCapGadget<F, N_BYTES_U64>,
     src_id: Cell<F>,
     call_data_length: Cell<F>,
     call_data_offset: Cell<F>, // Only used in the internal call
@@ -45,20 +44,19 @@ impl<F: Field> ExecutionGadget<F> for CallDataCopyGadget<F> {
     fn configure(cb: &mut EVMConstraintBuilder<F>) -> Self {
         let opcode = cb.query_cell();
 
-        let memory_offset = cb.query_cell_phase2();
-        let data_offset = cb.query_word_rlc();
+        let src_id = cb.query_cell();
+        let call_data_length = cb.query_cell();
+        let call_data_offset = cb.query_cell();
+
         let length = cb.query_word_rlc();
+        let memory_offset = cb.query_cell_phase2();
+        let data_offset = WordByteCapGadget::construct(cb, call_data_length.expr());
 
         // Pop memory_offset, data_offset, length from stack
         cb.stack_pop(memory_offset.expr());
-        cb.stack_pop(data_offset.expr());
+        cb.stack_pop(data_offset.original_word());
         cb.stack_pop(length.expr());
 
-        let memory_address = MemoryAddressGadget::construct(cb, memory_offset, length);
-        let src_id = cb.query_cell();
-        let call_data_length = cb.query_cell();
-        let call_data_offset = cb.query_cell();
-
         // Lookup the calldata_length and caller_address in Tx context table or
         // Call context table
         cb.condition(cb.curr.state.is_root.expr(), |cb| {
@@ -97,6 +95,7 @@ impl<F: Field> ExecutionGadget<F> for CallDataCopyGadget<F> {
 
         // Calculate the next memory size and the gas cost for this memory
         // access
+        let memory_address = MemoryAddressGadget::construct(cb, memory_offset, length);
         let memory_expansion = MemoryExpansionGadget::construct(cb, [memory_address.address()]);
         let memory_copier_gas = MemoryCopierGasGadget::construct(
             cb,
@@ -111,13 +110,23 @@ impl<F: Field> ExecutionGadget<F> for CallDataCopyGadget<F> {
             CopyDataType::Memory.expr(),
         );
         cb.condition(memory_address.has_length(), |cb| {
+            // Set source start to the minimun value of data offset and call data length.
+            let src_addr = call_data_offset.expr()
+                + select::expr(
+                    data_offset.lt_cap(),
+                    data_offset.valid_value(),
+                    call_data_length.expr(),
+                );
+
+            let src_addr_end = call_data_offset.expr() + call_data_length.expr();
+
             cb.copy_table_lookup(
                 src_id.expr(),
                 src_tag,
                 cb.curr.state.call_id.expr(),
                 CopyDataType::Memory.expr(),
-                call_data_offset.expr() + from_bytes::expr(&data_offset.cells),
-                call_data_offset.expr() + call_data_length.expr(),
+                src_addr,
+                src_addr_end,
                 memory_address.offset(),
                 memory_address.length(),
                 0.expr(), // for CALLDATACOPY rlc_acc is 0
@@ -175,15 +184,6 @@ impl<F: Field> ExecutionGadget<F> for CallDataCopyGadget<F> {
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
         let src_id = if call.is_root { tx.id } else { call.caller_id };
         self.src_id.assign(
             region,
@@ -202,6 +202,9 @@ impl<F: Field> ExecutionGadget<F> for CallDataCopyGadget<F> {
         self.call_data_offset
             .assign(region, offset, Value::known(F::from(call_data_offset)))?;
 
+        self.data_offset
+            .assign(region, offset, data_offset, F::from(call_data_length))?;
+
         // rw_counter increase from copy lookup is `length` memory writes + a variable
         // number of memory reads.
         let copy_rwc_inc = length
@@ -212,9 +215,10 @@ impl<F: Field> ExecutionGadget<F> for CallDataCopyGadget<F> {
                 // memory reads when reading from memory of caller is capped by call_data_length
                 // - data_offset.
                 min(
-                    length.low_u64(),
-                    call_data_length
-                        .checked_sub(data_offset.low_u64())
+                    length.as_u64(),
+                    u64::try_from(data_offset)
+                        .ok()
+                        .and_then(|offset| call_data_length.checked_sub(offset))
                         .unwrap_or_default(),
                 )
             };
@@ -261,8 +265,8 @@ mod test {
     fn test_root_ok(
         call_data_length: usize,
         memory_offset: usize,
-        data_offset: usize,
         length: usize,
+        data_offset: Word,
     ) {
         let bytecode = bytecode! {
             PUSH32(length)
@@ -300,14 +304,14 @@ mod test {
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
-            .op_calldatacopy(dst_offset, offset, length)
+            .op_calldatacopy(dst_offset, data_offset, length)
             STOP
         };
 
@@ -340,25 +344,31 @@ mod test {
 
     #[test]
     fn calldatacopy_gadget_simple() {
-        test_root_ok(0x40, 0x40, 0x00, 10);
-        test_internal_ok(0x40, 0x40, 0xA0, 0x10, 10);
+        test_root_ok(0x40, 0x40, 10, 0x00.into());
+        test_internal_ok(0x40, 0x40, 0xA0, 10, 0x10.into());
     }
 
     #[test]
     fn calldatacopy_gadget_large() {
-        test_root_ok(0x204, 0x103, 0x102, 0x101);
-        test_internal_ok(0x30, 0x204, 0x103, 0x102, 0x101);
+        test_root_ok(0x204, 0x103, 0x101, 0x102.into());
+        test_internal_ok(0x30, 0x204, 0x103, 0x101, 0x102.into());
     }
 
     #[test]
     fn calldatacopy_gadget_out_of_bound() {
-        test_root_ok(0x40, 0x40, 0x20, 40);
-        test_internal_ok(0x40, 0x20, 0xA0, 0x28, 10);
+        test_root_ok(0x40, 0x40, 40, 0x20.into());
+        test_internal_ok(0x40, 0x20, 0xA0, 10, 0x28.into());
     }
 
     #[test]
     fn calldatacopy_gadget_zero_length() {
-        test_root_ok(0x40, 0x40, 0x00, 0);
-        test_internal_ok(0x40, 0x40, 0xA0, 0x10, 0);
+        test_root_ok(0x40, 0x40, 0, 0x00.into());
+        test_internal_ok(0x40, 0x40, 0xA0, 0, 0x10.into());
+    }
+
+    #[test]
+    fn calldatacopy_gadget_data_offset_overflow() {
+        test_root_ok(0x40, 0x40, 0, Word::MAX);
+        test_internal_ok(0x40, 0x40, 0xA0, 0, Word::MAX);
     }
 }
```

### zkevm-circuits/src/evm_circuit/execution/calldataload.rs
```diff
@@ -1,23 +1,23 @@
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
+            common_gadget::{SameContextGadget, WordByteCapGadget},
             constraint_builder::{
                 ConstrainBuilderCommon, EVMConstraintBuilder, StepStateTransition,
                 Transition::Delta,
             },
-            from_bytes,
             memory_gadget::BufferReaderGadget,
-            not, CachedRegion, Cell, MemoryAddress,
+            not, select, CachedRegion, Cell,
         },
         witness::{Block, Call, ExecStep, Transaction},
     },
@@ -37,15 +37,16 @@ pub(crate) struct CallDataLoadGadget<F> {
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
+    /// is valid if within range of Uint64 and less than call_data_length.
+    data_offset: WordByteCapGadget<F, N_BYTES_U64>,
     /// Gadget to read from tx calldata, which we validate against the word
     /// pushed to stack.
     buffer_reader: BufferReaderGadget<F, N_BYTES_WORD, N_BYTES_MEMORY_ADDRESS>,
@@ -59,61 +60,84 @@ impl<F: Field> ExecutionGadget<F> for CallDataLoadGadget<F> {
     fn configure(cb: &mut EVMConstraintBuilder<F>) -> Self {
         let opcode = cb.query_cell();
 
-        let offset = cb.query_word_rlc();
-
-        // Pop the offset value from stack.
-        cb.stack_pop(offset.expr());
-
-        // Add a lookup constrain for TxId in the RW table.
         let src_id = cb.query_cell();
         let call_data_length = cb.query_cell();
         let call_data_offset = cb.query_cell();
 
-        let src_addr = from_bytes::expr(&offset.cells) + call_data_offset.expr();
-        let src_addr_end = call_data_length.expr() + call_data_offset.expr();
+        let data_offset = WordByteCapGadget::construct(cb, call_data_length.expr());
+        cb.stack_pop(data_offset.original_word());
+
+        cb.condition(
+            and::expr([data_offset.not_overflow(), cb.curr.state.is_root.expr()]),
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
 
-        cb.condition(cb.curr.state.is_root.expr(), |cb| {
-            cb.call_context_lookup(false.expr(), None, CallContextFieldTag::TxId, src_id.expr());
-            cb.call_context_lookup(
-                false.expr(),
-                None,
-                CallContextFieldTag::CallDataLength,
-                call_data_length.expr(),
-            );
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
+        cb.condition(
+            and::expr([
+                data_offset.not_overflow(),
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
+
+        // Set source start to the minimun value of data offset and call data length.
+        let src_addr = call_data_offset.expr()
+            + select::expr(
+                data_offset.lt_cap(),
+                data_offset.valid_value(),
                 call_data_length.expr(),
             );
-            cb.call_context_lookup(
-                false.expr(),
-                None,
-                CallContextFieldTag::CallDataOffset,
-                call_data_offset.expr(),
-            );
-        });
 
-        let buffer_reader = BufferReaderGadget::construct(cb, src_addr.clone(), src_addr_end);
+        let src_addr_end = call_data_offset.expr() + call_data_length.expr();
+
+        let buffer_reader = BufferReaderGadget::construct(cb, src_addr.expr(), src_addr_end);
 
-        let mut calldata_word = (0..N_BYTES_WORD)
+        let mut calldata_word: Vec<_> = (0..N_BYTES_WORD)
             .map(|idx| {
-                // for a root call, the call data comes from tx's data field.
+                // For a root call, the call data comes from tx's data field.
                 cb.condition(
-                    cb.curr.state.is_root.expr() * buffer_reader.read_flag(idx),
+                    and::expr([
+                        data_offset.not_overflow(),
+                        buffer_reader.read_flag(idx),
+                        cb.curr.state.is_root.expr(),
+                    ]),
                     |cb| {
                         cb.tx_context_lookup(
                             src_id.expr(),
@@ -123,9 +147,13 @@ impl<F: Field> ExecutionGadget<F> for CallDataLoadGadget<F> {
                         );
                     },
                 );
-                // for an internal call, the call data comes from memory.
+                // For an internal call, the call data comes from memory.
                 cb.condition(
-                    (1.expr() - cb.curr.state.is_root.expr()) * buffer_reader.read_flag(idx),
+                    and::expr([
+                        data_offset.not_overflow(),
+                        buffer_reader.read_flag(idx),
+                        not::expr(cb.curr.state.is_root.expr()),
+                    ]),
                     |cb| {
                         cb.memory_lookup(
                             0.expr(),
@@ -137,7 +165,7 @@ impl<F: Field> ExecutionGadget<F> for CallDataLoadGadget<F> {
                 );
                 buffer_reader.byte(idx)
             })
-            .collect::<Vec<Expression<F>>>();
+            .collect();
 
         // Since the stack items are in little endian form, we reverse the bytes
         // here.
@@ -146,7 +174,13 @@ impl<F: Field> ExecutionGadget<F> for CallDataLoadGadget<F> {
         // Add a lookup constraint for the 32-bytes that should have been pushed
         // to the stack.
         let calldata_word: [Expression<F>; N_BYTES_WORD] = calldata_word.try_into().unwrap();
-        cb.stack_push(cb.word_rlc(calldata_word));
+        let calldata_word = cb.word_rlc(calldata_word);
+        cb.require_zero(
+            "Stack push result must be 0 if stack pop offset is Uint64 overflow",
+            data_offset.overflow() * calldata_word.expr(),
+        );
+
+        cb.stack_push(calldata_word);
 
         let step_state_transition = StepStateTransition {
             rw_counter: Delta(cb.rw_counter_offset()),
@@ -160,10 +194,10 @@ impl<F: Field> ExecutionGadget<F> for CallDataLoadGadget<F> {
 
         Self {
             same_context,
-            offset,
             src_id,
             call_data_length,
             call_data_offset,
+            data_offset,
             buffer_reader,
         }
     }
@@ -179,62 +213,58 @@ impl<F: Field> ExecutionGadget<F> for CallDataLoadGadget<F> {
     ) -> Result<(), Error> {
         self.same_context.assign_exec_step(region, offset, step)?;
 
-        // set the value for bytes offset in calldata. This is where we start
-        // reading bytes from.
-        let data_offset = block.rws[step.rw_indices[0]].stack_value();
-
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
 
-        let mut calldata_bytes = vec![0u8; N_BYTES_WORD];
-        let (src_addr, src_addr_end) = (
-            data_offset.as_usize() + calldata_offset as usize,
-            calldata_length as usize + calldata_offset as usize,
-        );
+        let data_offset = block.rws[step.rw_indices[0]].stack_value();
+        let offset_not_overflow =
+            self.data_offset
+                .assign(region, offset, data_offset, F::from(call_data_length))?;
 
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
+        let data_offset = if offset_not_overflow {
+            data_offset.as_u64()
+        } else {
+            call_data_length
+        };
+        let src_addr_end = call_data_offset + call_data_length;
+        let src_addr = call_data_offset
+            .checked_add(data_offset)
+            .unwrap_or(src_addr_end)
+            .min(src_addr_end);
+
+        let mut calldata_bytes = vec![0u8; N_BYTES_WORD];
+        if offset_not_overflow {
+            for (i, byte) in calldata_bytes.iter_mut().enumerate() {
+                if call.is_root {
+                    // Fetch from tx call data.
+                    if src_addr + (i as u64) < tx.call_data_length as u64 {
+                        *byte = tx.call_data[src_addr as usize + i];
+                    }
+                } else {
+                    // Fetch from memory.
+                    if src_addr + (i as u64) < call.call_data_offset + call.call_data_length {
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
@@ -249,15 +279,15 @@ mod test {
     use eth_types::{bytecode, Word};
     use mock::{generate_mock_call_bytecode, MockCallBytecodeParams, TestContext};
 
-    fn test_bytecode(offset: usize) -> eth_types::Bytecode {
+    fn test_bytecode(offset: Word) -> eth_types::Bytecode {
         bytecode! {
-            PUSH32(Word::from(offset))
+            PUSH32(offset)
             CALLDATALOAD
             STOP
         }
     }
 
-    fn test_root_ok(offset: usize) {
+    fn test_root_ok(offset: Word) {
         let bytecode = test_bytecode(offset);
 
         CircuitTestBuilder::new_from_test_ctx(
@@ -266,7 +296,7 @@ mod test {
         .run();
     }
 
-    fn test_internal_ok(call_data_length: usize, call_data_offset: usize, offset: usize) {
+    fn test_internal_ok(call_data_length: usize, call_data_offset: usize, offset: Word) {
         let (addr_a, addr_b) = (mock::MOCK_ACCOUNTS[0], mock::MOCK_ACCOUNTS[1]);
 
         // code B gets called by code A, so the call is an internal call.
@@ -300,17 +330,23 @@ mod test {
 
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
@@ -1,19 +1,18 @@
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
+            common_gadget::{SameContextGadget, WordByteCapGadget},
             constraint_builder::{
                 ConstrainBuilderCommon, EVMConstraintBuilder, StepStateTransition, Transition,
             },
-            from_bytes,
             memory_gadget::{MemoryAddressGadget, MemoryCopierGasGadget, MemoryExpansionGadget},
-            not, CachedRegion, Cell, MemoryAddress,
+            not, select, CachedRegion, Cell,
         },
         witness::{Block, Call, ExecStep, Transaction},
     },
@@ -25,8 +24,9 @@ use super::ExecutionGadget;
 #[derive(Clone, Debug)]
 pub(crate) struct CodeCopyGadget<F> {
     same_context: SameContextGadget<F>,
-    /// Holds the memory address for the offset in code from where we read.
-    code_offset: MemoryAddress<F>,
+    /// Holds the memory address for the offset in code from where we
+    /// read. It is valid if within range of Uint64 and less than code_size.
+    code_offset: WordByteCapGadget<F, N_BYTES_U64>,
     /// Holds the size of the current environment's bytecode.
     code_size: Cell<F>,
     /// The code from current environment is copied to memory. To verify this
@@ -51,14 +51,15 @@ impl<F: Field> ExecutionGadget<F> for CodeCopyGadget<F> {
     fn configure(cb: &mut EVMConstraintBuilder<F>) -> Self {
         let opcode = cb.query_cell();
 
-        // Query elements to be popped from the stack.
-        let dst_memory_offset = cb.query_cell_phase2();
-        let code_offset = cb.query_word_rlc();
+        let code_size = cb.query_cell();
+
         let size = cb.query_word_rlc();
+        let dst_memory_offset = cb.query_cell_phase2();
+        let code_offset = WordByteCapGadget::construct(cb, code_size.expr());
 
         // Pop items from stack.
         cb.stack_pop(dst_memory_offset.expr());
-        cb.stack_pop(code_offset.expr());
+        cb.stack_pop(code_offset.original_word());
         cb.stack_pop(size.expr());
 
         // Construct memory address in the destionation (memory) to which we copy code.
@@ -68,7 +69,6 @@ impl<F: Field> ExecutionGadget<F> for CodeCopyGadget<F> {
         let code_hash = cb.curr.state.code_hash.clone();
 
         // Fetch the bytecode length from the bytecode table.
-        let code_size = cb.query_cell();
         cb.bytecode_length(code_hash.expr(), code_size.expr());
 
         // Calculate the next memory size and the gas cost for this memory
@@ -83,12 +83,19 @@ impl<F: Field> ExecutionGadget<F> for CodeCopyGadget<F> {
 
         let copy_rwc_inc = cb.query_cell();
         cb.condition(dst_memory_addr.has_length(), |cb| {
+            // Set source start to the minimun value of code offset and code size.
+            let src_addr = select::expr(
+                code_offset.lt_cap(),
+                code_offset.valid_value(),
+                code_size.expr(),
+            );
+
             cb.copy_table_lookup(
                 code_hash.expr(),
                 CopyDataType::Bytecode.expr(),
                 cb.curr.state.call_id.expr(),
                 CopyDataType::Memory.expr(),
-                from_bytes::expr(&code_offset.cells),
+                src_addr,
                 code_size.expr(),
                 dst_memory_addr.offset(),
                 dst_memory_addr.length(),
@@ -147,26 +154,17 @@ impl<F: Field> ExecutionGadget<F> for CodeCopyGadget<F> {
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
-
-        let code = block
+        let bytecode = block
             .bytecodes
             .get(&call.code_hash)
             .expect("could not find current environment's bytecode");
-        self.code_size.assign(
-            region,
-            offset,
-            Value::known(F::from(code.bytes.len() as u64)),
-        )?;
+
+        let code_size = bytecode.bytes.len() as u64;
+        self.code_size
+            .assign(region, offset, Value::known(F::from(code_size)))?;
+
+        self.code_offset
+            .assign(region, offset, code_offset, F::from(code_size))?;
 
         // assign the destination memory offset.
         let memory_address = self
@@ -202,16 +200,16 @@ mod tests {
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
@@ -226,13 +224,18 @@ mod tests {
 
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

### zkevm-circuits/src/evm_circuit/execution/error_invalid_jump.rs
```diff
@@ -4,30 +4,26 @@ use crate::{
         param::N_BYTES_PROGRAM_COUNTER,
         step::ExecutionState,
         util::{
-            and,
-            common_gadget::CommonErrorGadget,
+            common_gadget::{CommonErrorGadget, WordByteCapGadget},
             constraint_builder::{ConstrainBuilderCommon, EVMConstraintBuilder},
-            from_bytes,
-            math_gadget::{IsEqualGadget, IsZeroGadget, LtGadget},
-            select, sum, CachedRegion, Cell, Word,
+            math_gadget::{IsEqualGadget, IsZeroGadget},
+            CachedRegion, Cell,
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
+    dest: WordByteCapGadget<F, N_BYTES_PROGRAM_COUNTER>,
     code_len: Cell<F>,
     value: Cell<F>,
     is_code: Cell<F>,
-    dest_not_overflow: IsZeroGadget<F>,
-    dest_lt_code_len: LtGadget<F, N_BYTES_PROGRAM_COUNTER>,
     is_jump_dest: IsEqualGadget<F>,
     is_jumpi: IsEqualGadget<F>,
     phase2_condition: Cell<F>,
@@ -41,14 +37,8 @@ impl<F: Field> ExecutionGadget<F> for ErrorInvalidJumpGadget<F> {
     const EXECUTION_STATE: ExecutionState = ExecutionState::ErrorInvalidJump;
 
     fn configure(cb: &mut EVMConstraintBuilder<F>) -> Self {
-        let dest_word = cb.query_word_rlc();
-        let dest_not_overflow =
-            IsZeroGadget::construct(cb, sum::expr(&dest_word.cells[N_BYTES_PROGRAM_COUNTER..]));
-        let dest = select::expr(
-            dest_not_overflow.expr(),
-            from_bytes::expr(&dest_word.cells[..N_BYTES_PROGRAM_COUNTER]),
-            u64::MAX.expr(),
-        );
+        let code_len = cb.query_cell();
+        let dest = WordByteCapGadget::construct(cb, code_len.expr());
 
         let opcode = cb.query_cell();
         let value = cb.query_cell();
@@ -71,7 +61,7 @@ impl<F: Field> ExecutionGadget<F> for ErrorInvalidJumpGadget<F> {
         let is_condition_zero = IsZeroGadget::construct(cb, phase2_condition.expr());
 
         // Pop the value from the stack
-        cb.stack_pop(dest_word.expr());
+        cb.stack_pop(dest.original_word());
 
         cb.condition(is_jumpi.expr(), |cb| {
             cb.stack_pop(phase2_condition.expr());
@@ -80,39 +70,31 @@ impl<F: Field> ExecutionGadget<F> for ErrorInvalidJumpGadget<F> {
         });
 
         // Look up bytecode length
-        let code_len = cb.query_cell();
         cb.bytecode_length(cb.curr.state.code_hash.expr(), code_len.expr());
 
-        let dest_lt_code_len = LtGadget::construct(cb, dest.expr(), code_len.expr());
-
         // If destination is in valid range, lookup for the value.
-        cb.condition(
-            and::expr([dest_not_overflow.expr(), dest_lt_code_len.expr()]),
-            |cb| {
-                cb.bytecode_lookup(
-                    cb.curr.state.code_hash.expr(),
-                    dest.expr(),
-                    is_code.expr(),
-                    value.expr(),
-                );
-                cb.require_zero(
-                    "is_code is false or not JUMPDEST",
-                    is_code.expr() * is_jump_dest.expr(),
-                );
-            },
-        );
+        cb.condition(dest.lt_cap(), |cb| {
+            cb.bytecode_lookup(
+                cb.curr.state.code_hash.expr(),
+                dest.valid_value(),
+                is_code.expr(),
+                value.expr(),
+            );
+            cb.require_zero(
+                "is_code is false or not JUMPDEST",
+                is_code.expr() * is_jump_dest.expr(),
+            );
+        });
 
         let common_error_gadget =
             CommonErrorGadget::construct(cb, opcode.expr(), 3.expr() + is_jumpi.expr());
 
         Self {
             opcode,
-            dest_word,
+            dest,
             code_len,
             value,
             is_code,
-            dest_not_overflow,
-            dest_lt_code_len,
             is_jump_dest,
             is_jumpi,
             phase2_condition,
@@ -135,10 +117,6 @@ impl<F: Field> ExecutionGadget<F> for ErrorInvalidJumpGadget<F> {
         self.opcode
             .assign(region, offset, Value::known(F::from(opcode.as_u64())))?;
 
-        let dest = block.rws[step.rw_indices[0]].stack_value();
-        self.dest_word
-            .assign(region, offset, Some(dest.to_le_bytes()))?;
-
         let condition = if is_jumpi {
             block.rws[step.rw_indices[1]].stack_value()
         } else {
@@ -154,19 +132,11 @@ impl<F: Field> ExecutionGadget<F> for ErrorInvalidJumpGadget<F> {
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
-        } else {
-            u64::MAX
-        };
+        let dest = block.rws[step.rw_indices[0]].stack_value();
+        self.dest.assign(region, offset, dest, F::from(code_len))?;
 
         // set default value in case can not find value, is_code from bytecode table
+        let dest = u64::try_from(dest).unwrap_or(code_len);
         let mut code_pair = [0u8, 0u8];
         if dest < code_len {
             // get real value from bytecode table
@@ -184,9 +154,6 @@ impl<F: Field> ExecutionGadget<F> for ErrorInvalidJumpGadget<F> {
             F::from(OpcodeId::JUMPDEST.as_u64()),
         )?;
 
-        self.dest_lt_code_len
-            .assign(region, offset, F::from(dest), F::from(code_len))?;
-
         self.is_jumpi.assign(
             region,
             offset,
```
