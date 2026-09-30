# [?] fix TOB-SCROLL-13： fix unconstrained opcodes allow nondeterministic execution (#633)

## Summary
Severity: Unknown
Chain: ZK
Component: scroll-tech/zkevm-circuits
Published: 2023-08-14
Source: https://github.com/scroll-tech/zkevm-circuits/commit/90ca1fc7908ff042d02a0f09653028ce15817919
Type: security-commit

## Details
fix TOB-SCROLL-13： fix unconstrained opcodes allow nondeterministic execution (#633)

* fix TOB-SCROLL-13

* some updates

* add notes

## Patch
### zkevm-circuits/src/evm_circuit/execution/error_code_store.rs
```diff
@@ -15,7 +15,10 @@ use crate::{
     util::Expr,
 };
 
-use eth_types::{evm_types::GasCost, Field};
+use eth_types::{
+    evm_types::{GasCost, OpcodeId},
+    Field,
+};
 
 use halo2_proofs::{circuit::Value, plonk::Error};
 
@@ -40,6 +43,12 @@ impl<F: Field> ExecutionGadget<F> for ErrorCodeStoreGadget<F> {
 
     fn configure(cb: &mut EVMConstraintBuilder<F>) -> Self {
         let opcode = cb.query_cell();
+        // constrain opcodes
+        cb.require_equal(
+            "ErrorCodeStore checking at RETURN in create context",
+            opcode.expr(),
+            OpcodeId::RETURN.expr(),
+        );
 
         let offset = cb.query_cell_phase2();
         let length = cb.query_word_rlc();
```

### zkevm-circuits/src/evm_circuit/execution/error_invalid_creation_code.rs
```diff
@@ -5,7 +5,7 @@ use crate::{
         step::ExecutionState,
         util::{
             common_gadget::CommonErrorGadget,
-            constraint_builder::EVMConstraintBuilder,
+            constraint_builder::{ConstrainBuilderCommon, EVMConstraintBuilder},
             from_bytes,
             math_gadget::IsEqualGadget,
             memory_gadget::{MemoryMask, MemoryWordAddress},
@@ -16,7 +16,7 @@ use crate::{
     util::Expr,
 };
 
-use eth_types::{Field, ToLittleEndian};
+use eth_types::{evm_types::OpcodeId, Field, ToLittleEndian};
 use halo2_proofs::{circuit::Value, plonk::Error};
 
 /// Gadget for code store oog and max code size exceed
@@ -39,7 +39,12 @@ impl<F: Field> ExecutionGadget<F> for ErrorInvalidCreationCodeGadget<F> {
 
     fn configure(cb: &mut EVMConstraintBuilder<F>) -> Self {
         let opcode = cb.query_cell();
-
+        // constrain opcodes
+        cb.require_equal(
+            "ErrorInvalidCreationCode checking at RETURN in create context",
+            opcode.expr(),
+            OpcodeId::RETURN.expr(),
+        );
         let first_byte = cb.query_cell();
 
         //let address = cb.query_word_rlc();
```

### zkevm-circuits/src/evm_circuit/execution/error_precompile_failed.rs
```diff
@@ -6,7 +6,7 @@ use crate::{
             constraint_builder::EVMConstraintBuilder,
             math_gadget::IsZeroGadget,
             memory_gadget::{CommonMemoryAddressGadget, MemoryAddressGadget},
-            CachedRegion, Cell, Word,
+            sum, CachedRegion, Cell, Word,
         },
     },
     table::CallContextFieldTag,
@@ -48,6 +48,20 @@ impl<F: Field> ExecutionGadget<F> for ErrorPrecompileFailedGadget<F> {
         let is_staticcall =
             IsZeroGadget::construct(cb, "", opcode.expr() - OpcodeId::STATICCALL.expr());
 
+        // constrain op code
+        // NOTE: this precompile gadget is for dummy use at the moment, the real error handling for
+        // precompile will be done in each precompile gadget in the future. won't add step
+        // state transition constraint here as well.
+        cb.require_true(
+            "opcode is one of [call, callcode, staticcall, delegatecall]",
+            sum::expr(vec![
+                is_call.expr(),
+                is_callcode.expr(),
+                is_delegatecall.expr(),
+                is_staticcall.expr(),
+            ]),
+        );
+
         // Use rw_counter of the step which triggers next call as its call_id.
         let callee_call_id = cb.curr.state.rw_counter.clone();
 
```

### zkevm-circuits/src/evm_circuit/execution/return_revert.rs
```diff
@@ -21,7 +21,10 @@ use crate::{
     util::Expr,
 };
 use bus_mapping::{circuit_input_builder::CopyDataType, state_db::CodeDB};
-use eth_types::{evm_types::GasCost, Field, ToScalar, U256};
+use eth_types::{
+    evm_types::{GasCost, OpcodeId},
+    Field, ToScalar, U256,
+};
 use ethers_core::utils::keccak256;
 use halo2_proofs::{circuit::Value, plonk::Error};
 
@@ -64,6 +67,13 @@ impl<F: Field> ExecutionGadget<F> for ReturnRevertGadget<F> {
 
         cb.opcode_lookup(opcode.expr(), 1.expr());
 
+        // constrain op codes
+        cb.require_in_set(
+            "RETURN_REVERT state is for RETURN or REVERT",
+            opcode.expr(),
+            vec![OpcodeId::RETURN.expr(), OpcodeId::REVERT.expr()],
+        );
+
         let offset = cb.query_cell_phase2();
         let length = cb.query_word_rlc();
         cb.stack_pop(offset.expr());
@@ -72,12 +82,6 @@ impl<F: Field> ExecutionGadget<F> for ReturnRevertGadget<F> {
 
         let is_success = cb.call_context(None, CallContextFieldTag::IsSuccess);
         cb.require_boolean("is_success is boolean", is_success.expr());
-        // cb.require_equal(
-        // "if is_success, opcode is RETURN. if not, opcode is REVERT",
-        // opcode.expr(),
-        // is_success.expr() * OpcodeId::RETURN.expr()
-        // + not::expr(is_success.expr()) * OpcodeId::REVERT.expr(),
-        // );
 
         // There are 4 cases non-mutually exclusive, A to D, to handle, depending on if
         // the call is, or is not, a create, root, or successful. See the specs at
```
