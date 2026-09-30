# [?] Add `dummy_gen_create_ops` to avoid call stack empty panic (#454)

## Summary
Severity: Unknown
Chain: ZK
Component: privacy-ethereum/zkevm-circuits
Published: 2022-05-16
Source: https://github.com/privacy-ethereum/zkevm-circuits/commit/2693c32513a4a668ce33630f69a9896e849f3c3d
Type: security-commit

## Details
Add `dummy_gen_create_ops` to avoid call stack empty panic (#454)

* feat: add dummy_gen_create_ops and fix some statedb bugs

* fix: use push_op_reversible correctly

* feat: add dummy gen_selfdestruct_ops

* fix: use EXTCODEHASH to warm the address

## Patch
### Cargo.lock
```diff
@@ -1108,6 +1108,7 @@ dependencies = [
  "ethers-providers",
  "halo2_proofs",
  "hex",
+ "itertools",
  "lazy_static",
  "regex",
  "serde",
```

### bus-mapping/src/circuit_input_builder/input_state_ref.rs
```diff
@@ -8,8 +8,8 @@ use crate::{
     error::{get_step_reported_error, ExecError},
     exec_trace::OperationRef,
     operation::{
-        AccountField, CallContextField, CallContextOp, MemoryOp, Op, OpEnum, Operation, StackOp,
-        Target, RW,
+        AccountField, AccountOp, CallContextField, CallContextOp, MemoryOp, Op, OpEnum, Operation,
+        StackOp, Target, RW,
     },
     state_db::{CodeDB, StateDB},
     Error,
@@ -19,7 +19,6 @@ use eth_types::{
     Address, GethExecStep, ToAddress, ToBigEndian, Word, H256,
 };
 use ethers_core::utils::{get_contract_address, get_create2_address};
-use itertools::Itertools;
 
 /// Reference to the internal state of the CircuitInputBuilder in a particular
 /// [`ExecStep`].
@@ -266,6 +265,64 @@ impl<'a> CircuitInputStateRef<'a> {
         Ok(())
     }
 
+    /// Push 2 reversible [`AccountOp`] to update `sender` and `receiver`'s
+    /// balance by `value`, with `sender` being extraly charged with `fee`.
+    pub fn transfer_with_fee(
+        &mut self,
+        step: &mut ExecStep,
+        sender: Address,
+        receiver: Address,
+        value: Word,
+        fee: Word,
+    ) -> Result<(), Error> {
+        let (found, sender_account) = self.sdb.get_account(&sender);
+        if !found {
+            return Err(Error::AccountNotFound(sender));
+        }
+        let sender_balance_prev = sender_account.balance;
+        let sender_balance = sender_account.balance - value - fee;
+        self.push_op_reversible(
+            step,
+            RW::WRITE,
+            AccountOp {
+                address: sender,
+                field: AccountField::Balance,
+                value: sender_balance,
+                value_prev: sender_balance_prev,
+            },
+        )?;
+
+        let (found, receiver_account) = self.sdb.get_account(&receiver);
+        if !found {
+            return Err(Error::AccountNotFound(receiver));
+        }
+        let receiver_balance_prev = receiver_account.balance;
+        let receiver_balance = receiver_account.balance + value;
+        self.push_op_reversible(
+            step,
+            RW::WRITE,
+            AccountOp {
+                address: receiver,
+                field: AccountField::Balance,
+                value: receiver_balance,
+                value_prev: receiver_balance_prev,
+            },
+        )?;
+
+        Ok(())
+    }
+
+    /// Same functionality with `transfer_with_fee` but with `fee` set zero.
+    pub fn transfer(
+        &mut self,
+        step: &mut ExecStep,
+        sender: Address,
+        receiver: Address,
+        value: Word,
+    ) -> Result<(), Error> {
+        self.transfer_with_fee(step, sender, receiver, value, Word::zero())
+    }
+
     /// Fetch and return code for the given code hash from the code DB.
     pub fn code(&self, code_hash: H256) -> Result<Vec<u8>, Error> {
         self.code_db
@@ -304,21 +361,8 @@ impl<'a> CircuitInputStateRef<'a> {
     pub fn push_call(&mut self, call: Call, step: &GethExecStep) {
         let call_data = match call.kind {
             CallKind::Call | CallKind::CallCode | CallKind::DelegateCall | CallKind::StaticCall => {
-                let call_data = if step.memory.0.len() < call.call_data_offset as usize {
-                    &[]
-                } else {
-                    &step.memory.0[call.call_data_offset as usize..]
-                };
-                if call_data.len() < call.call_data_length as usize {
-                    // Expand call_data to expected size
-                    call_data
-                        .iter()
-                        .cloned()
-                        .pad_using(call.call_data_length as usize, |_| 0)
-                        .collect()
-                } else {
-                    call_data[..call.call_data_length as usize].to_vec()
-                }
+                step.memory
+                    .read_chunk(call.call_data_offset.into(), call.call_data_length.into())
             }
             CallKind::Create | CallKind::Create2 => Vec::new(),
         };
@@ -587,7 +631,24 @@ impl<'a> CircuitInputStateRef<'a> {
 
     /// Handle a return step caused by any opcode that causes a return to the
     /// previous call context.
-    pub fn handle_return(&mut self) -> Result<(), Error> {
+    pub fn handle_return(&mut self, step: &GethExecStep) -> Result<(), Error> {
+        let call = self.call()?.clone();
+
+        // Store deployed code if it's a successful create
+        if call.is_create() && call.is_success {
+            let offset = step.stack.nth_last(0)?;
+            let length = step.stack.nth_last(1)?;
+            let code = step
+                .memory
+                .read_chunk(offset.low_u64().into(), length.low_u64().into());
+            let code_hash = self.code_db.insert(code);
+            let (found, callee_account) = self.sdb.get_account_mut(&call.address);
+            if !found {
+                return Err(Error::AccountNotFound(call.address));
+            }
+            callee_account.code_hash = code_hash;
+        }
+
         // Handle reversion if this call doens't end successfully
         if !self.call()?.is_success {
             self.handle_reversion();
```

### bus-mapping/src/evm/opcodes.rs
```diff
@@ -11,7 +11,7 @@ use crate::{
 use core::fmt::Debug;
 use eth_types::{
     evm_types::{GasCost, MAX_REFUND_QUOTIENT_OF_GAS_USED},
-    GethExecStep, ToWord, Word,
+    GethExecStep, ToAddress, ToWord, Word,
 };
 use keccak256::EMPTY_HASH;
 use log::warn;
@@ -203,11 +203,18 @@ fn fn_gen_associated_ops(opcode_id: &OpcodeId) -> FnGenAssociatedOps {
         // OpcodeId::STATICCALL => {},
         // TODO: Handle REVERT by its own gen_associated_ops.
         OpcodeId::REVERT => Stop::gen_associated_ops,
-        // OpcodeId::SELFDESTRUCT => {},
+        OpcodeId::SELFDESTRUCT => {
+            warn!("Using dummy gen_selfdestruct_ops for opcode SELFDESTRUCT");
+            dummy_gen_selfdestruct_ops
+        }
         OpcodeId::CALLCODE | OpcodeId::DELEGATECALL | OpcodeId::STATICCALL => {
             warn!("Using dummy gen_call_ops for opcode {:?}", opcode_id);
             dummy_gen_call_ops
         }
+        OpcodeId::CREATE | OpcodeId::CREATE2 => {
+            warn!("Using dummy gen_create_ops for opcode {:?}", opcode_id);
+            dummy_gen_create_ops
+        }
         _ => {
             warn!("Using dummy gen_associated_ops for opcode {:?}", opcode_id);
             dummy_gen_associated_ops
@@ -252,6 +259,7 @@ pub fn gen_begin_tx_ops(state: &mut CircuitInputStateRef) -> Result<ExecStep, Er
         );
     }
 
+    // Increase caller's nonce
     let caller_address = call.caller_address;
     let nonce_prev = state.sdb.increase_nonce(&caller_address);
     state.push_op(
@@ -261,10 +269,11 @@ pub fn gen_begin_tx_ops(state: &mut CircuitInputStateRef) -> Result<ExecStep, Er
             address: caller_address,
             field: AccountField::Nonce,
             value: (nonce_prev + 1).into(),
-            value_prev: (nonce_prev).into(),
+            value_prev: nonce_prev.into(),
         },
     );
 
+    // Add caller and callee into access list
     for address in [call.caller_address, call.address] {
         state.sdb.add_account_to_access_list(address);
         state.push_op(
@@ -279,6 +288,7 @@ pub fn gen_begin_tx_ops(state: &mut CircuitInputStateRef) -> Result<ExecStep, Er
         );
     }
 
+    // Calculate intrinsic gas cost
     let call_data_gas_cost = state
         .tx
         .input
@@ -291,40 +301,18 @@ pub fn gen_begin_tx_ops(state: &mut CircuitInputStateRef) -> Result<ExecStep, Er
     } + call_data_gas_cost;
     exec_step.gas_cost = GasCost(intrinsic_gas_cost);
 
-    let (found, caller_account) = state.sdb.get_account_mut(&call.caller_address);
-    if !found {
-        return Err(Error::AccountNotFound(call.caller_address));
-    }
-    let caller_balance_prev = caller_account.balance;
-    let caller_balance = caller_account.balance - call.value - state.tx.gas_price * state.tx.gas;
-    state.push_op_reversible(
+    // Transfer with fee
+    state.transfer_with_fee(
         &mut exec_step,
-        RW::WRITE,
-        AccountOp {
-            address: call.caller_address,
-            field: AccountField::Balance,
-            value: caller_balance,
-            value_prev: caller_balance_prev,
-        },
+        call.caller_address,
+        call.address,
+        call.value,
+        state.tx.gas_price * state.tx.gas,
     )?;
 
-    let (found, callee_account) = state.sdb.get_account_mut(&call.address);
-    if !found {
-        return Err(Error::AccountNotFound(call.address));
-    }
-    let callee_balance_prev = callee_account.balance;
-    let callee_balance = callee_account.balance + call.value;
+    // Get code_hash of callee
+    let (_, callee_account) = state.sdb.get_account(&call.address);
     let code_hash = callee_account.code_hash;
-    state.push_op_reversible(
-        &mut exec_step,
-        RW::WRITE,
-        AccountOp {
-            address: call.address,
-            field: AccountField::Balance,
-            value: callee_balance,
-            value_prev: callee_balance_prev,
-        },
-    )?;
 
     // There are 4 branches from here.
     match (
@@ -547,15 +535,27 @@ fn dummy_gen_call_ops(
     geth_steps: &[GethExecStep],
 ) -> Result<Vec<ExecStep>, Error> {
     let geth_step = &geth_steps[0];
-    let exec_step = state.new_step(geth_step)?;
+    let mut exec_step = state.new_step(geth_step)?;
 
-    let call = state.call()?.clone();
-    let callee = state.parse_call(geth_step)?;
+    let tx_id = state.tx_ctx.id();
+    let call = state.parse_call(geth_step)?;
 
-    let (_, account) = state.sdb.get_account(&callee.address);
+    let (_, account) = state.sdb.get_account(&call.address);
     let callee_code_hash = account.code_hash;
 
-    state.push_call(callee.clone(), geth_step);
+    let is_warm = state.sdb.check_account_in_access_list(&call.address);
+    state.push_op_reversible(
+        &mut exec_step,
+        RW::WRITE,
+        TxAccessListAccountOp {
+            tx_id,
+            address: call.address,
+            is_warm: true,
+            is_warm_prev: is_warm,
+        },
+    )?;
+
+    state.push_call(call.clone(), geth_step);
 
     match (
         state.is_precompiled(&call.address),
@@ -565,10 +565,114 @@ fn dummy_gen_call_ops(
         (true, _) => Ok(vec![exec_step]),
         // 2. Call to account with empty code.
         (_, true) => {
-            state.handle_return()?;
+            state.handle_return(geth_step)?;
             Ok(vec![exec_step])
         }
         // 3. Call to account with non-empty code.
         (_, false) => Ok(vec![exec_step]),
     }
 }
+
+fn dummy_gen_create_ops(
+    state: &mut CircuitInputStateRef,
+    geth_steps: &[GethExecStep],
+) -> Result<Vec<ExecStep>, Error> {
+    let geth_step = &geth_steps[0];
+    let mut exec_step = state.new_step(geth_step)?;
+
+    let tx_id = state.tx_ctx.id();
+    let call = state.parse_call(geth_step)?;
+
+    // Increase caller's nonce
+    let nonce_prev = state.sdb.get_nonce(&call.caller_address);
+    state.push_op_reversible(
+        &mut exec_step,
+        RW::WRITE,
+        AccountOp {
+            address: call.caller_address,
+            field: AccountField::Nonce,
+            value: (nonce_prev + 1).into(),
+            value_prev: nonce_prev.into(),
+        },
+    )?;
+
+    // Add callee into access list
+    let is_warm = state.sdb.check_account_in_access_list(&call.address);
+    state.push_op_reversible(
+        &mut exec_step,
+        RW::WRITE,
+        TxAccessListAccountOp {
+            tx_id,
+            address: call.address,
+            is_warm: true,
+            is_warm_prev: is_warm,
+        },
+    )?;
+
+    state.push_call(call.clone(), geth_step);
+
+    // Increase callee's nonce
+    let nonce_prev = state.sdb.get_nonce(&call.address);
+    debug_assert!(nonce_prev == 0);
+    state.push_op_reversible(
+        &mut exec_step,
+        RW::WRITE,
+        AccountOp {
+            address: call.address,
+            field: AccountField::Nonce,
+            value: 1.into(),
+            value_prev: 0.into(),
+        },
+    )?;
+
+    state.transfer(
+        &mut exec_step,
+        call.caller_address,
+        call.address,
+        call.value,
+    )?;
+
+    if call.code_hash.to_fixed_bytes() == *EMPTY_HASH {
+        // 1. Create with empty initcode.
+        state.handle_return(geth_step)?;
+        Ok(vec![exec_step])
+    } else {
+        // 2. Create with non-empty initcode.
+        Ok(vec![exec_step])
+    }
+}
+
+fn dummy_gen_selfdestruct_ops(
+    state: &mut CircuitInputStateRef,
+    geth_steps: &[GethExecStep],
+) -> Result<Vec<ExecStep>, Error> {
+    let geth_step = &geth_steps[0];
+    let mut exec_step = state.new_step(geth_step)?;
+    let sender = state.call()?.address;
+    let receiver = geth_step.stack.last()?.to_address();
+
+    let is_warm = state.sdb.check_account_in_access_list(&receiver);
+    state.push_op_reversible(
+        &mut exec_step,
+        RW::WRITE,
+        TxAccessListAccountOp {
+            tx_id: state.tx_ctx.id(),
+            address: receiver,
+            is_warm: true,
+            is_warm_prev: is_warm,
+        },
+    )?;
+
+    let (found, receiver_account) = state.sdb.get_account(&receiver);
+    if !found {
+        return Err(Error::AccountNotFound(receiver));
+    }
+    let value = receiver_account.balance;
+    state.transfer(&mut exec_step, sender, receiver, value)?;
+
+    if state.call()?.is_persistent {
+        state.sdb.destruct_account(sender);
+    }
+
+    Ok(vec![exec_step])
+}
```

### bus-mapping/src/evm/opcodes/call.rs
```diff
@@ -31,8 +31,8 @@ impl Opcode for Call {
         let mut exec_step = state.new_step(geth_step)?;
 
         let tx_id = state.tx_ctx.id();
-        let call = state.call()?.clone();
-        let callee = state.parse_call(geth_step)?;
+        let current_call = state.call()?.clone();
+        let call = state.parse_call(geth_step)?;
 
         // NOTE: For `RwCounterEndOfReversion` we use the `0` value as a placeholder,
         // and later set the proper value in
@@ -42,17 +42,23 @@ impl Opcode for Call {
             (CallContextField::RwCounterEndOfReversion, 0.into()),
             (
                 CallContextField::IsPersistent,
-                (call.is_persistent as u64).into(),
+                (current_call.is_persistent as u64).into(),
+            ),
+            (
+                CallContextField::CallerAddress,
+                current_call.address.to_word(),
             ),
-            (CallContextField::CallerAddress, call.address.to_word()),
-            (CallContextField::IsStatic, (call.is_static as u64).into()),
-            (CallContextField::Depth, call.depth.into()),
+            (
+                CallContextField::IsStatic,
+                (current_call.is_static as u64).into(),
+            ),
+            (CallContextField::Depth, current_call.depth.into()),
         ] {
             state.push_op(
                 &mut exec_step,
                 RW::READ,
                 CallContextOp {
-                    call_id: call.call_id,
+                    call_id: current_call.call_id,
                     field,
                     value,
                 },
@@ -64,7 +70,7 @@ impl Opcode for Call {
                 &mut exec_step,
                 RW::READ,
                 StackOp {
-                    call_id: call.call_id,
+                    call_id: current_call.call_id,
                     address: geth_step.stack.nth_last_filled(i),
                     value: geth_step.stack.nth_last(i)?,
                 },
@@ -74,85 +80,56 @@ impl Opcode for Call {
             &mut exec_step,
             RW::WRITE,
             StackOp {
-                call_id: call.call_id,
+                call_id: current_call.call_id,
                 address: geth_step.stack.nth_last_filled(6),
-                value: (callee.is_success as u64).into(),
+                value: (call.is_success as u64).into(),
             },
         );
 
-        let is_warm_access = !state.sdb.add_account_to_access_list(callee.address);
+        let is_warm = state.sdb.check_account_in_access_list(&call.address);
         state.push_op_reversible(
             &mut exec_step,
             RW::WRITE,
             TxAccessListAccountOp {
                 tx_id,
-                address: callee.address,
+                address: call.address,
                 is_warm: true,
-                is_warm_prev: is_warm_access,
+                is_warm_prev: is_warm,
             },
         )?;
 
         // Switch to callee's call context
-        state.push_call(callee.clone(), geth_step);
+        state.push_call(call.clone(), geth_step);
 
         for (field, value) in [
             (CallContextField::RwCounterEndOfReversion, 0.into()),
             (
                 CallContextField::IsPersistent,
-                (callee.is_persistent as u64).into(),
+                (call.is_persistent as u64).into(),
             ),
         ] {
             state.push_op(
                 &mut exec_step,
                 RW::READ,
                 CallContextOp {
-                    call_id: callee.call_id,
+                    call_id: call.call_id,
                     field,
                     value,
                 },
             );
         }
 
-        let (found, caller_account) = state.sdb.get_account_mut(&callee.caller_address);
-        if !found {
-            return Err(Error::AccountNotFound(callee.caller_address));
-        }
-        let caller_balance_prev = caller_account.balance;
-        let caller_balance = caller_account.balance - callee.value;
-        caller_account.balance = caller_balance;
-        state.push_op_reversible(
+        state.transfer(
             &mut exec_step,
-            RW::WRITE,
-            AccountOp {
-                address: callee.caller_address,
-                field: AccountField::Balance,
-                value: caller_balance,
-                value_prev: caller_balance_prev,
-            },
+            call.caller_address,
+            call.address,
+            call.value,
         )?;
 
-        let (found, callee_account) = state.sdb.get_account_mut(&callee.address);
-        if !found {
-            return Err(Error::AccountNotFound(callee.address));
-        }
+        let (_, callee_account) = state.sdb.get_account(&call.address);
         let is_account_empty = callee_account.is_empty();
-        let callee_balance_prev = callee_account.balance;
-        let callee_balance = callee_account.balance + callee.value;
-        callee_account.balance = callee_balance;
-        state.push_op_reversible(
-            &mut exec_step,
-            RW::WRITE,
-            AccountOp {
-                address: callee.address,
-                field: AccountField::Balance,
-                value: callee_balance,
-                value_prev: callee_balance_prev,
-            },
-        )?;
-
-        let (_, account) = state.sdb.get_account(&callee.address);
-        let callee_nonce = account.nonce;
-        let callee_code_hash = account.code_hash;
+        let callee_nonce = callee_account.nonce;
+        let callee_code_hash = callee_account.code_hash;
         for (field, value) in [
             (AccountField::Nonce, callee_nonce),
             (AccountField::CodeHash, callee_code_hash.to_word()),
@@ -161,7 +138,7 @@ impl Opcode for Call {
                 &mut exec_step,
                 RW::READ,
                 AccountOp {
-                    address: callee.address,
+                    address: call.address,
                     field,
                     value,
                     value_prev: value,
@@ -173,14 +150,14 @@ impl Opcode for Call {
         // there isn't next geth_step (e.g. callee doesn't have code).
         let next_memory_word_size = [
             geth_step.memory.word_size() as u64,
-            (callee.call_data_offset + callee.call_data_length + 31) / 32,
-            (callee.return_data_offset + callee.return_data_length + 31) / 32,
+            (call.call_data_offset + call.call_data_length + 31) / 32,
+            (call.return_data_offset + call.return_data_length + 31) / 32,
         ]
         .into_iter()
         .max()
         .unwrap();
-        let has_value = !callee.value.is_zero();
-        let gas_cost = if is_warm_access {
+        let has_value = !call.value.is_zero();
+        let gas_cost = if is_warm {
             GasCost::WARM_ACCESS.as_u64()
         } else {
             GasCost::COLD_ACCOUNT_ACCESS.as_u64()
@@ -220,13 +197,13 @@ impl Opcode for Call {
                         &mut exec_step,
                         RW::WRITE,
                         CallContextOp {
-                            call_id: call.call_id,
+                            call_id: current_call.call_id,
                             field,
                             value,
                         },
                     );
                 }
-                state.handle_return()?;
+                state.handle_return(geth_step)?;
                 Ok(vec![exec_step])
             }
             // 3. Call to account with non-empty code.
@@ -254,56 +231,53 @@ impl Opcode for Call {
                         &mut exec_step,
                         RW::WRITE,
                         CallContextOp {
-                            call_id: call.call_id,
+                            call_id: current_call.call_id,
                             field,
                             value,
                         },
                     );
                 }
 
                 for (field, value) in [
-                    (CallContextField::CallerId, call.call_id.into()),
+                    (CallContextField::CallerId, current_call.call_id.into()),
                     (CallContextField::TxId, tx_id.into()),
-                    (CallContextField::Depth, callee.depth.into()),
+                    (CallContextField::Depth, call.depth.into()),
                     (
                         CallContextField::CallerAddress,
-                        callee.caller_address.to_word(),
+                        call.caller_address.to_word(),
                     ),
-                    (CallContextField::CalleeAddress, callee.address.to_word()),
+                    (CallContextField::CalleeAddress, call.address.to_word()),
                     (
                         CallContextField::CallDataOffset,
-                        callee.call_data_offset.into(),
+                        call.call_data_offset.into(),
                     ),
                     (
                         CallContextField::CallDataLength,
-                        callee.call_data_length.into(),
+                        call.call_data_length.into(),
                     ),
                     (
                         CallContextField::ReturnDataOffset,
-                        callee.return_data_offset.into(),
+                        call.return_data_offset.into(),
                     ),
                     (
                         CallContextField::ReturnDataLength,
-                        callee.return_data_length.into(),
+                        call.return_data_length.into(),
                     ),
-                    (CallContextField::Value, callee.value),
-                    (
-                        CallContextField::IsSuccess,
-                        (callee.is_success as u64).into(),
-                    ),
-                    (CallContextField::IsStatic, (callee.is_static as u64).into()),
+                    (CallContextField::Value, call.value),
+                    (CallContextField::IsSuccess, (call.is_success as u64).into()),
+                    (CallContextField::IsStatic, (call.is_static as u64).into()),
                     (CallContextField::LastCalleeId, 0.into()),
                     (CallContextField::LastCalleeReturnDataOffset, 0.into()),
                     (CallContextField::LastCalleeReturnDataLength, 0.into()),
                     (CallContextField::IsRoot, 0.into()),
                     (CallContextField::IsCreate, 0.into()),
-                    (CallContextField::CodeSource, callee.code_hash.to_word()),
+                    (CallContextField::CodeSource, call.code_hash.to_word()),
                 ] {
                     state.push_op(
                         &mut exec_step,
                         RW::READ,
                         CallContextOp {
-                            call_id: callee.call_id,
+                            call_id: call.call_id,
                             field,
                             value,
                         },
```

### bus-mapping/src/evm/opcodes/extcodehash.rs
```diff
@@ -8,7 +8,7 @@ use crate::{
     state_db::Account,
     Error,
 };
-use eth_types::{evm_types::GasCost, GethExecStep, ToAddress, ToWord, U256};
+use eth_types::{GethExecStep, ToAddress, ToWord, U256};
 
 #[derive(Debug, Copy, Clone)]
 pub(crate) struct Extcodehash;
@@ -58,12 +58,7 @@ impl Opcode for Extcodehash {
         }
 
         // Update transaction access list for external_address
-        let is_warm = match step.gas_cost {
-            GasCost::WARM_ACCESS => true,
-            GasCost::COLD_ACCOUNT_ACCESS => false,
-            _ => unreachable!(),
-        };
-        state.sdb.add_account_to_access_list(external_address);
+        let is_warm = state.sdb.check_account_in_access_list(&external_address);
         state.push_op_reversible(
             &mut exec_step,
             RW::WRITE,
@@ -171,7 +166,7 @@ mod extcodehash_tests {
         if is_warm {
             code.append(&bytecode! {
                 PUSH20(external_address.to_word())
-                BALANCE
+                EXTCODEHASH
                 POP
             });
         }
@@ -234,7 +229,8 @@ mod extcodehash_tests {
         let indices = transaction
             .steps()
             .iter()
-            .find(|step| step.exec_state == ExecState::Op(OpcodeId::EXTCODEHASH))
+            .filter(|step| step.exec_state == ExecState::Op(OpcodeId::EXTCODEHASH))
+            .last()
             .unwrap()
             .bus_mapping_instance
             .clone();
```

### bus-mapping/src/evm/opcodes/mload.rs
```diff
@@ -3,7 +3,7 @@ use crate::circuit_input_builder::{CircuitInputStateRef, ExecStep};
 use crate::Error;
 use core::convert::TryInto;
 use eth_types::evm_types::MemoryAddress;
-use eth_types::{GethExecStep, ToBigEndian, Word};
+use eth_types::{GethExecStep, ToBigEndian};
 
 /// Placeholder structure used to implement [`Opcode`] trait over it
 /// corresponding to the [`OpcodeId::MLOAD`](crate::evm::OpcodeId::MLOAD)
@@ -33,10 +33,7 @@ impl Opcode for Mload {
         let mut mem_read_addr: MemoryAddress = stack_value_read.try_into()?;
         // Accesses to memory that hasn't been initialized are valid, and return
         // 0.
-        let mem_read_value = geth_steps[1]
-            .memory
-            .read_word(mem_read_addr)
-            .unwrap_or_else(|_| Word::zero());
+        let mem_read_value = geth_steps[1].memory.read_word(mem_read_addr);
 
         //
         // First stack write
@@ -69,6 +66,7 @@ mod mload_tests {
         bytecode,
         evm_types::{OpcodeId, StackAddress},
         geth_types::GethData,
+        Word,
     };
     use itertools::Itertools;
     use mock::test_ctx::{helpers::*, TestContext};
```

### bus-mapping/src/evm/opcodes/stop.rs
```diff
@@ -17,8 +17,9 @@ impl Opcode for Stop {
         state: &mut CircuitInputStateRef,
         geth_steps: &[GethExecStep],
     ) -> Result<Vec<ExecStep>, Error> {
-        let exec_step = state.new_step(&geth_steps[0])?;
-        state.handle_return()?;
+        let geth_step = &geth_steps[0];
+        let exec_step = state.new_step(geth_step)?;
+        state.handle_return(geth_step)?;
         Ok(vec![exec_step])
     }
 }
```

### bus-mapping/src/state_db.rs
```diff
@@ -83,6 +83,9 @@ pub struct StateDB {
     // state before current transaction, to calculate gas cost for some opcodes like sstore.
     // So both dirty storage and committed storage are needed.
     dirty_storage: HashMap<(Address, Word), Word>,
+    // Accounts that have been through `SELFDESTRUCT` under the situation that `is_persistent` is
+    // `true`. These accounts will be reset once `commit_tx` is called.
+    destructed_account: HashSet<Address>,
     refund: u64,
 }
 
@@ -94,6 +97,7 @@ impl StateDB {
             access_list_account: HashSet::new(),
             access_list_account_storage: HashSet::new(),
             dirty_storage: HashMap::new(),
+            destructed_account: HashSet::new(),
             refund: 0,
         }
     }
@@ -173,6 +177,12 @@ impl StateDB {
         self.dirty_storage.insert((*addr, *key), *value);
     }
 
+    /// Get nonce of account with `addr`.
+    pub fn get_nonce(&mut self, addr: &Address) -> u64 {
+        let (_, account) = self.get_account(addr);
+        account.nonce.as_u64()
+    }
+
     /// Increase nonce of account with `addr` and return the previous value.
     pub fn increase_nonce(&mut self, addr: &Address) -> u64 {
         let (_, account) = self.get_account_mut(addr);
@@ -181,6 +191,11 @@ impl StateDB {
         nonce
     }
 
+    /// Check whether `addr` exists in account access list.
+    pub fn check_account_in_access_list(&self, addr: &Address) -> bool {
+        self.access_list_account.contains(addr)
+    }
+
     /// Add `addr` into account access list. Returns `true` if it's not in the
     /// access list before.
     pub fn add_account_to_access_list(&mut self, addr: Address) -> bool {
@@ -189,7 +204,13 @@ impl StateDB {
 
     /// Remove `addr` from account access list.
     pub fn remove_account_from_access_list(&mut self, addr: &Address) {
-        debug_assert!(self.access_list_account.remove(addr));
+        let exist = self.access_list_account.remove(addr);
+        debug_assert!(exist);
+    }
+
+    /// Check whether `(addr, key)` exists in account storage access list.
+    pub fn check_account_storage_in_access_list(&self, pair: &(Address, Word)) -> bool {
+        self.access_list_account_storage.contains(pair)
     }
 
     /// Add `(addr, key)` into account storage access list. Returns `true` if
@@ -200,12 +221,13 @@ impl StateDB {
 
     /// Remove `(addr, key)` from account storage access list.
     pub fn remove_account_storage_from_access_list(&mut self, pair: &(Address, Word)) {
-        debug_assert!(self.access_list_account_storage.remove(pair));
+        let exist = self.access_list_account_storage.remove(pair);
+        debug_assert!(exist);
     }
 
-    /// Check whether `(addr, key)` exists in account storage access list.
-    pub fn check_account_storage_in_access_list(&self, pair: &(Address, Word)) -> bool {
-        self.access_list_account_storage.contains(pair)
+    /// Set account as self destructed.
+    pub fn destruct_account(&mut self, addr: Address) {
+        self.destructed_account.insert(addr);
     }
 
     /// Retrieve refund.
@@ -229,6 +251,10 @@ impl StateDB {
             *ptr = value;
         }
         self.dirty_storage = HashMap::new();
+        for addr in self.destructed_account.clone() {
+            let (_, account) = self.get_account_mut(&addr);
+            *account = ACCOUNT_ZERO.clone();
+        }
         self.refund = 0;
     }
 }
```

### eth-types/Cargo.toml
```diff
@@ -14,3 +14,4 @@ regex = "1.5.4"
 serde = {version = "1.0.130", features = ["derive"] }
 serde_json = "1.0.66"
 uint = "0.9.1"
+itertools = "0.10"
```

### eth-types/src/evm_types/memory.rs
```diff
@@ -4,6 +4,7 @@ use crate::{DebugByte, ToBigEndian, Word};
 use core::convert::TryFrom;
 use core::ops::{Add, AddAssign, Index, IndexMut, Mul, MulAssign, Sub, SubAssign};
 use core::str::FromStr;
+use itertools::Itertools;
 use std::fmt;
 
 /// Represents a `MemoryAddress` of the EVM.
@@ -81,7 +82,7 @@ impl TryFrom<Word> for MemoryAddress {
 
 impl_from_usize_wrappers!(
     MemoryAddress = MemoryAddress,
-    (u8, u16, u32, usize, i32, i64)
+    (u8, u16, u32, u64, usize, i32, i64)
 );
 
 impl FromStr for MemoryAddress {
@@ -259,17 +260,25 @@ impl Memory {
 
     /// Reads an entire [`Word`] which starts at the provided [`MemoryAddress`]
     /// `addr` and finnishes at `addr + 32`.
-    pub fn read_word(&self, addr: MemoryAddress) -> Result<Word, Error> {
-        // Ensure that the memory is big enough to have values in the range
-        // `[addr, addr+32)`.
-        if self.0.len() < addr.0 + 32 {
-            return Err(Error::InvalidMemoryPointer);
-        }
+    pub fn read_word(&self, addr: MemoryAddress) -> Word {
+        Word::from_big_endian(&self.read_chunk(addr, MemoryAddress::from(32)))
+    }
 
-        // Now we know that the indexing will not panic.
-        Ok(Word::from_big_endian(
-            &self[addr..addr + MemoryAddress::from(32)],
-        ))
+    /// Reads an chunk of memory[offset..offset+length]. Zeros will be padded if
+    /// index out of range.
+    pub fn read_chunk(&self, offset: MemoryAddress, length: MemoryAddress) -> Vec<u8> {
+        let chunk = if self.0.len() < offset.0 {
+            &[]
+        } else {
+            &self.0[offset.0..]
+        };
+        let chunk = if chunk.len() < length.0 {
+            // Expand chunk to expected size
+            chunk.iter().cloned().pad_using(length.0, |_| 0).collect()
+        } else {
+            chunk[..length.0].to_vec()
+        };
+        chunk
     }
 
     /// Returns the size of memory in word.
@@ -336,7 +345,7 @@ mod memory_tests {
 
         // If we read a word at addr `0x40` we should get `0x80`.
         assert_eq!(
-            mem_map.read_word(MemoryAddress::from(0x40))?,
+            mem_map.read_word(MemoryAddress::from(0x40)),
             Word::from(0x80)
         );
 
```

### zkevm-circuits/src/evm_circuit/execution/call.rs
```diff
@@ -43,8 +43,8 @@ pub(crate) struct CallGadget<F> {
     value: Word<F>,
     is_success: Cell<F>,
     gas_is_u64: IsZeroGadget<F>,
-    is_warm_access: Cell<F>,
-    is_warm_access_prev: Cell<F>,
+    is_warm: Cell<F>,
+    is_warm_prev: Cell<F>,
     callee_reversion_info: ReversionInfo<F>,
     value_is_zero: IsZeroGadget<F>,
     cd_address: MemoryAddressGadget<F>,
@@ -123,13 +123,13 @@ impl<F: Field> ExecutionGadget<F> for CallGadget<F> {
         );
 
         // Add callee to access list
-        let is_warm_access = cb.query_bool();
-        let is_warm_access_prev = cb.query_bool();
+        let is_warm = cb.query_bool();
+        let is_warm_prev = cb.query_bool();
         cb.account_access_list_write(
             tx_id.expr(),
             callee_address.clone(),
-            is_warm_access.expr(),
-            is_warm_access_prev.expr(),
+            is_warm.expr(),
+            is_warm_prev.expr(),
             Some(&mut reversion_info),
         );
 
@@ -189,7 +189,7 @@ impl<F: Field> ExecutionGadget<F> for CallGadget<F> {
         );
         // Sum up gas cost
         let gas_cost = select::expr(
-            is_warm_access_prev.expr(),
+            is_warm_prev.expr(),
             GasCost::WARM_ACCESS.expr(),
             GasCost::COLD_ACCOUNT_ACCESS.expr(),
         ) + has_value.clone()
@@ -313,8 +313,8 @@ impl<F: Field> ExecutionGadget<F> for CallGadget<F> {
             value,
             is_success,
             gas_is_u64,
-            is_warm_access,
-            is_warm_access_prev,
+            is_warm,
+            is_warm_prev,
             callee_reversion_info,
             value_is_zero,
             cd_address,
@@ -361,8 +361,7 @@ impl<F: Field> ExecutionGadget<F> for CallGadget<F> {
                 step.rw_indices[13],
             ]
             .map(|idx| block.rws[idx].stack_value());
-        let (is_warm_access, is_warm_access_prev) =
-            block.rws[step.rw_indices[14]].tx_access_list_value_pair();
+        let (is_warm, is_warm_prev) = block.rws[step.rw_indices[14]].tx_access_list_value_pair();
         let [caller_balance_pair, callee_balance_pair, (callee_nonce, _), (callee_code_hash, _)] =
             [
                 step.rw_indices[17],
@@ -403,13 +402,10 @@ impl<F: Field> ExecutionGadget<F> for CallGadget<F> {
             offset,
             sum::value(&gas.to_le_bytes()[N_BYTES_GAS..]),
         )?;
-        self.is_warm_access
-            .assign(region, offset, Some(F::from(is_warm_access as u64)))?;
-        self.is_warm_access_prev.assign(
-            region,
-            offset,
-            Some(F::from(is_warm_access_prev as u64)),
-        )?;
+        self.is_warm
+            .assign(region, offset, Some(F::from(is_warm as u64)))?;
+        self.is_warm_prev
+            .assign(region, offset, Some(F::from(is_warm_prev as u64)))?;
         self.callee_reversion_info.assign(
             region,
             offset,
@@ -462,7 +458,7 @@ impl<F: Field> ExecutionGadget<F> for CallGadget<F> {
             Word::random_linear_combine(*EMPTY_HASH_LE, block.randomness),
         )?;
         let has_value = !value.is_zero();
-        let gas_cost = if is_warm_access_prev {
+        let gas_cost = if is_warm_prev {
             GasCost::WARM_ACCESS.as_u64()
         } else {
             GasCost::COLD_ACCOUNT_ACCESS.as_u64()
```

### zkevm-circuits/src/evm_circuit/witness.rs
```diff
@@ -1269,6 +1269,9 @@ fn tx_convert(tx: &circuit_input_builder::Transaction, id: usize, is_last_tx: bo
                     circuit_input_builder::CodeSource::Address(_) => {
                         CodeSource::Account(call.code_hash.to_word())
                     }
+                    circuit_input_builder::CodeSource::Memory => {
+                        CodeSource::Account(call.code_hash.to_word())
+                    }
                     _ => unimplemented!(),
                 },
                 rw_counter_end_of_reversion: call.rw_counter_end_of_reversion,
```
