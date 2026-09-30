# [?] fix(DSM): Handle overflowing/underflowing fee in `charge_direct` (#8443)

## Summary
Severity: Unknown
Chain: Internet Computer
Component: dfinity/ic
Published: 2026-01-22
Source: https://github.com/dfinity/ic/commit/538a765f942014a2d925fcec42ed95315c752f6c
Type: security-commit

## Details
fix(DSM): Handle overflowing/underflowing fee in `charge_direct` (#8443)

Handle very large fees which don't fit into `i64` or would cause the
instruction counter to underflow.

## Patch
### rs/embedders/src/wasmtime_embedder/linker.rs
```diff
@@ -176,8 +176,13 @@ fn charge_direct_fee(
         instruction_counter = system_api.out_of_instructions(instruction_counter)?;
     }
 
+    // If the fee can't fit into an i64 without overflowing, we'll run out of instructions anyway (even with DTS) so just fail.
+    let fee = fee.get().try_into().map_err(|_| {
+        HypervisorError::InstructionLimitExceeded(NumInstructions::from(instruction_limit as u64))
+    })?;
+
     // Now we can subtract the fee and store the new instruction counter.
-    instruction_counter -= fee.get() as i64;
+    instruction_counter = instruction_counter.saturating_sub(fee);
     store_value(&num_instructions_global, instruction_counter, caller)?;
 
     // If the instruction counter became negative after subtracting the fee,
@@ -641,7 +646,7 @@ pub fn syscalls<
                 let mut num_bytes = logging_charge_bytes(&mut caller, length)?;
                 let debug_print_is_enabled = debug_print_is_enabled(&mut caller, &feature_flags)?;
                 if debug_print_is_enabled {
-                    num_bytes += length;
+                    num_bytes = num_bytes.saturating_add(length);
                 }
                 charge_for_cpu_and_mem(&mut caller, overhead::DEBUG_PRINT, num_bytes)?;
                 let offset: usize = offset.try_into().expect("Failed to convert I to usize");
@@ -662,7 +667,7 @@ pub fn syscalls<
             move |mut caller: Caller<'_, StoreData>, offset: I, length: I| -> Result<(), _> {
                 let offset: usize = offset.try_into().expect("Failed to convert I to usize");
                 let length: usize = length.try_into().expect("Failed to convert I to usize");
-                let num_bytes = length + logging_charge_bytes(&mut caller, length)?;
+                let num_bytes = length.saturating_add(logging_charge_bytes(&mut caller, length)?);
                 charge_for_cpu_and_mem(&mut caller, overhead::TRAP, num_bytes)?;
                 with_memory_and_system_api(&mut caller, |system_api, memory| {
                     system_api.ic0_trap(offset, length, memory)
```

### rs/execution_environment/tests/hypervisor.rs
```diff
@@ -1,7 +1,7 @@
 use assert_matches::assert_matches;
 use candid::{CandidType, Decode, Encode};
 use ic_base_types::NumSeconds;
-use ic_config::subnet_config::SchedulerConfig;
+use ic_config::{flag_status::FlagStatus, subnet_config::SchedulerConfig};
 use ic_cycles_account_manager::ResourceSaturation;
 use ic_embedders::{
     wasm_utils::instrumentation::{WasmMemoryType, instruction_to_cost},
@@ -1080,6 +1080,56 @@ fn ic0_debug_print_out_of_bounds_works() {
     assert_eq!(result, WasmResult::Reply(vec![]));
 }
 
+#[test]
+fn ic0_debug_print_with_large_memory_wasm64() {
+    // Enable debug_print by disabling rate limiting
+    let mut config = ic_config::execution_environment::Config::default();
+    config
+        .embedders_config
+        .feature_flags
+        .rate_limiting_of_debug_prints = FlagStatus::Disabled;
+    let mut test = ExecutionTestBuilder::new()
+        .with_execution_config(config)
+        .build();
+    let wat = r#"
+        (module
+            (import "ic0" "debug_print" (func $ic0_debug_print (param i64) (param i64)))
+            (import "ic0" "msg_reply" (func $msg_reply))
+            (func $test (export "canister_update test")
+                (local $i i64)
+                ;; Call debug_print with offset 0 and large negative size
+                ;; (when interpreted as unsigned, this is a huge number)
+                i64.const 0
+                i64.const -9223372034854775815
+                call $ic0_debug_print
+                ;; Loop to a large count
+                (loop $my_loop
+                    local.get $i
+                    i64.const 1
+                    i64.add
+                    local.tee $i
+                    i64.const 9223372034854775815
+                    i64.lt_s
+                    br_if $my_loop
+                )
+                (call $msg_reply)
+            )
+            (memory i64 49000)
+        )"#;
+    // Give the canister a trillion cycles to ensure it doesn't run out
+    let initial_cycles = Cycles::new(1_000_000_000_000_000);
+    let canister_id = test
+        .canister_from_cycles_and_wat(initial_cycles, wat)
+        .unwrap();
+    // Calling debug_print with the large size argument should trap with InstructionLimitExceeded.
+    let result = test.ingress(canister_id, "test", vec![]);
+    let err = result.unwrap_err();
+    err.assert_contains(
+        ErrorCode::CanisterInstructionLimitExceeded,
+        "Canister exceeded the limit",
+    );
+}
+
 #[test]
 fn time_with_5_nanoseconds() {
     let mut test = ExecutionTestBuilder::new().build();
```
