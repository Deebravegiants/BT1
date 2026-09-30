# [?] fix: Unwind Rust panic on FFI boundary (#3288)

## Summary
Severity: Unknown
Chain: Starknet
Component: NethermindEth/juno
Published: 2025-11-21
Source: https://github.com/NethermindEth/juno/commit/d681791a3d4c6f72f7cc989615faad9c419fd2ca
Type: security-commit

## Details
fix: Unwind Rust panic on FFI boundary (#3288)

## Patch
### vm/rust/src/entrypoint/call/call.rs
```diff
@@ -13,7 +13,6 @@ use blockifier::{
     transaction::objects::{DeprecatedTransactionInfo, TransactionInfo},
 };
 use once_cell::sync::Lazy;
-use serde_json::json;
 use starknet_api::{
     contract_class::EntryPointType,
     core::{ClassHash, ContractAddress},
@@ -129,12 +128,11 @@ pub fn cairo_vm_call(
             );
             match e {
                 CallError::ContractError(revert_error, error_stack) => {
-                    let err_string = if structured_err_stack {
-                        error_stack_frames_to_json(error_stack).to_string()
+                    if structured_err_stack {
+                        JunoError::json_error(error_stack_frames_to_json(error_stack), None)
                     } else {
-                        json!(revert_error).to_string()
-                    };
-                    JunoError::block_error(err_string)
+                        JunoError::block_error(revert_error)
+                    }
                 }
                 CallError::Internal(e) | CallError::Custom(e) => JunoError::block_error(e),
             }
```

### vm/rust/src/entrypoint/execute/execute.rs
```diff
@@ -18,7 +18,6 @@ use crate::{
     state_reader::{state_reader::BlockHeight, JunoStateReader},
 };
 use serde::Deserialize;
-use serde_json::json;
 use std::{
     collections::VecDeque,
     ffi::{c_char, c_uchar},
@@ -138,15 +137,14 @@ pub fn cairo_vm_execute(
         )
         .map_err(|e| match e {
             ExecutionError::ExecutionError { error, error_stack } => {
-                let err_string = if err_stack {
-                    error_stack_frames_to_json(error_stack).to_string()
+                if err_stack {
+                    JunoError::json_error(error_stack_frames_to_json(error_stack), Some(txn_index))
                 } else {
-                    json!(error).to_string()
-                };
-                JunoError::tx_non_execution_error(err_string, txn_index)
+                    JunoError::tx_non_execution_error(error, txn_index)
+                }
             }
             ExecutionError::Internal(e) | ExecutionError::Custom(e) => {
-                JunoError::tx_non_execution_error(json!(e), txn_index)
+                JunoError::tx_non_execution_error(e, txn_index)
             }
         })?;
 
```

### vm/rust/src/error/juno.rs
```diff
@@ -1,21 +1,31 @@
+use serde_json::{json, Value};
+
 pub struct JunoError {
     pub msg: String,
     pub txn_index: i64,
     pub execution_failed: bool,
 }
 
 impl JunoError {
-    pub fn block_error<E: ToString>(err: E) -> Self {
+    pub fn json_error(err: Value, txn_index: Option<usize>) -> Self {
         Self {
             msg: err.to_string(),
+            txn_index: txn_index.map(|idx| idx as i64).unwrap_or(-1),
+            execution_failed: false,
+        }
+    }
+
+    pub fn block_error<E: ToString>(err: E) -> Self {
+        Self {
+            msg: json!(err.to_string()).to_string(),
             txn_index: -1,
             execution_failed: false,
         }
     }
 
     pub fn tx_non_execution_error<E: ToString>(err: E, txn_index: usize) -> Self {
         Self {
-            msg: err.to_string(),
+            msg: json!(err.to_string()).to_string(),
             txn_index: txn_index as i64,
             execution_failed: false,
         }
```

### vm/rust/src/ffi_entrypoint.rs
```diff
@@ -1,6 +1,7 @@
 use std::{
     collections::BTreeMap,
     ffi::{c_char, c_longlong, c_uchar, c_ulonglong, CStr, CString},
+    panic,
 };
 
 use crate::{
@@ -18,6 +19,18 @@ extern "C" {
     );
 }
 
+fn format_panic(payload: Box<dyn std::any::Any + Send>) -> String {
+    payload
+        .downcast_ref::<&str>()
+        .map(|s| s.to_string())
+        .unwrap_or_else(|| {
+            payload
+                .downcast_ref::<String>()
+                .map(|s| s.clone())
+                .unwrap_or("Unknown panic payload".into())
+        })
+}
+
 fn report_error(reader_handle: usize, err: JunoError) {
     let err_msg = CString::new(err.msg).unwrap();
     let execution_failed = if err.execution_failed { 1 } else { 0 };
@@ -80,18 +93,23 @@ pub extern "C" fn cairoVMCall(
     err_stack: c_uchar,
     return_state_diff: c_uchar,
 ) {
-    cairo_vm_call(
-        call_info_ptr,
-        block_info_ptr,
-        chain_info_ptr,
-        reader_handle,
-        max_steps,
-        initial_gas,
-        concurrency_mode,
-        err_stack,
-        return_state_diff,
+    panic::catch_unwind(|| {
+        cairo_vm_call(
+            call_info_ptr,
+            block_info_ptr,
+            chain_info_ptr,
+            reader_handle,
+            max_steps,
+            initial_gas,
+            concurrency_mode,
+            err_stack,
+            return_state_diff,
+        )
+    })
+    .map_or_else(
+        |err| report_error(reader_handle, JunoError::block_error(format_panic(err))),
+        |res| res.unwrap_or_else(|err| report_error(reader_handle, err)),
     )
-    .unwrap_or_else(|err| report_error(reader_handle, err));
 }
 
 #[no_mangle]
@@ -111,22 +129,27 @@ pub extern "C" fn cairoVMExecute(
     allow_binary_search: c_uchar,
     is_estimate_fee: c_uchar,
 ) {
-    cairo_vm_execute(
-        txns_json,
-        classes_json,
-        paid_fees_on_l1_json,
-        block_info_ptr,
-        chain_info_ptr,
-        reader_handle,
-        skip_charge_fee,
-        skip_validate,
-        err_on_revert,
-        concurrency_mode,
-        err_stack,
-        allow_binary_search,
-        is_estimate_fee,
+    panic::catch_unwind(|| {
+        cairo_vm_execute(
+            txns_json,
+            classes_json,
+            paid_fees_on_l1_json,
+            block_info_ptr,
+            chain_info_ptr,
+            reader_handle,
+            skip_charge_fee,
+            skip_validate,
+            err_on_revert,
+            concurrency_mode,
+            err_stack,
+            allow_binary_search,
+            is_estimate_fee,
+        )
+    })
+    .map_or_else(
+        |err| report_error(reader_handle, JunoError::block_error(format_panic(err))),
+        |res| res.unwrap_or_else(|err| report_error(reader_handle, err)),
     )
-    .unwrap_or_else(|err| report_error(reader_handle, err));
 }
 
 #[no_mangle]
```
