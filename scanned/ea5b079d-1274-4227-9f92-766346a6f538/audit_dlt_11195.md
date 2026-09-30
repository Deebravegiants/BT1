# [?] blockifier,starknet_os: defensive hardening of panics and unchecked arithmetic (#14433)

## Summary
Severity: Unknown
Chain: Starknet
Component: starkware-libs/sequencer
Published: 2026-06-15
Source: https://github.com/starkware-libs/sequencer/commit/1cefdb68dfe42cf8da00f6dc994cc196430e2035
Type: security-commit

## Details
blockifier,starknet_os: defensive hardening of panics and unchecked arithmetic (#14433)

Batch of low-risk hardening fixes found by the nightly bug-hunt routine
(confirmed bugs 4, 6, 7, 10). All align with the "never panic on data
reachable from external input / prefer defensive arithmetic" guideline.

- starknet_os os_output: parse_messages_to_l1 and the messages-to-L2 loop
  used assert_eq! to verify the declared segment was fully consumed, and a
  raw `-=` that could underflow on a malformed output vector. Both now
  return a new OsOutputError::MessagesSegmentNotConsumed via checked_sub
  instead of panicking.
- blockifier GasCosts::from_raw: default_initial_gas_cost,
  entry_point_initial_budget and syscall_base_gas_cost used bare `*`, while
  the sibling OsConstants::from_raw computes the same values with
  checked_factor_mul(...).expect(...). Use the checked form so the two
  copies of these constants can't silently diverge (one wrapping, one
  aborting) in release.
- blockifier round_up_to_mb: `div_ceil(MB) * MB` wraps to 0 for sizes near
  u64::MAX; saturate to the largest multiple of MB that fits.
- starknet_os _get_tx_info_ptr: read `version` from a DeprecatedTxInfo
  pointer using CairoStruct::DeprecatedTxInfo instead of CairoStruct::TxInfo
  (behavior-preserving today since version is field 0 in both, but the
  pointer is a DeprecatedTxInfo* and the other accesses already use it).

Co-authored-by: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

## Patch
### crates/blockifier/src/blockifier_versioned_constants.rs
```diff
@@ -558,9 +558,11 @@ pub struct CairoNativeStackConfig {
 
 impl CairoNativeStackConfig {
     /// Rounds up the given size to the nearest multiple of MB.
+    /// Saturates to the largest multiple of MB that fits in a `u64` to avoid wrapping to 0 for
+    /// sizes close to `u64::MAX` (a 0-byte stack size would crash Cairo Native).
     pub fn round_up_to_mb(size: u64) -> u64 {
         const MB: u64 = 1024 * 1024;
-        size.div_ceil(MB) * MB
+        size.div_ceil(MB).checked_mul(MB).unwrap_or(u64::MAX / MB * MB)
     }
 
     /// Returns the stack size sufficient for running Cairo Native.
@@ -1073,9 +1075,18 @@ impl GasCosts {
         let base_costs = BaseGasCosts {
             step_gas_cost,
             memory_hole_gas_cost: os_constants.memory_hole_gas_cost.0,
-            default_initial_gas_cost: step_gas_cost * default_initial_gas_cost_in_steps.0,
-            entry_point_initial_budget: step_gas_cost * entry_point_initial_budget_in_steps.0,
-            syscall_base_gas_cost: step_gas_cost * syscall_base_gas_cost_in_steps.0,
+            default_initial_gas_cost: default_initial_gas_cost_in_steps
+                .checked_factor_mul(step_gas_cost)
+                .expect("The default initial gas cost should not overflow.")
+                .0,
+            entry_point_initial_budget: entry_point_initial_budget_in_steps
+                .checked_factor_mul(step_gas_cost)
+                .expect("The entry point initial budget should not overflow.")
+                .0,
+            syscall_base_gas_cost: syscall_base_gas_cost_in_steps
+                .checked_factor_mul(step_gas_cost)
+                .expect("The syscall base gas cost should not overflow.")
+                .0,
         };
 
         let summarize = |selector: SyscallSelector| match os_constants.syscall_gas_costs {
```

### crates/starknet_os/src/hint_processor/snos_deprecated_syscall_executor.rs
```diff
@@ -128,7 +128,7 @@ impl<'a, S: StateReader> SnosHintProcessor<'a, S> {
             call_info_tracker.call_info.call.class_hash.expect("No class hash was set.");
         let tx_version = *vm.get_integer(get_address_of_nested_fields_from_base_address(
             original_tx_info_start_ptr,
-            CairoStruct::TxInfo,
+            CairoStruct::DeprecatedTxInfo,
             vm,
             &["version"],
             syscall_handler.program,
```

### crates/starknet_os/src/io/os_output.rs
```diff
@@ -41,6 +41,11 @@ pub enum OsOutputError {
     ConvertToFullOutput,
     #[error("Output iterator not exhausted.")]
     OutputNotExhausted,
+    #[error(
+        "Messages to {segment_name} segment was not fully consumed: {remaining} felts unaccounted \
+         for."
+    )]
+    MessagesSegmentNotConsumed { segment_name: &'static str, remaining: usize },
 }
 
 pub(crate) fn wrap_missing<T>(val: Option<T>, val_name: &str) -> Result<T, OsOutputError> {
@@ -113,15 +118,22 @@ pub fn parse_messages_to_l1<It: Iterator<Item = Felt>>(
 
     while messages_to_l1_iter.peek().is_some() {
         let message = message_l1_from_output_iter(&mut messages_to_l1_iter)?;
-        messages_to_l1_segment_size -= message.payload.0.len() + MESSAGE_TO_L1_CONST_FIELD_SIZE;
+        let consumed_felts = message.payload.0.len() + MESSAGE_TO_L1_CONST_FIELD_SIZE;
+        messages_to_l1_segment_size = messages_to_l1_segment_size
+            .checked_sub(consumed_felts)
+            .ok_or(OsOutputError::MessagesSegmentNotConsumed {
+                segment_name: "L1",
+                remaining: messages_to_l1_segment_size,
+            })?;
         messages_to_l1.push(message);
     }
 
-    assert_eq!(
-        messages_to_l1_segment_size, 0,
-        "Expected messages to L1 segment to be consumed, but {messages_to_l1_segment_size} felts \
-         were left."
-    );
+    if messages_to_l1_segment_size != 0 {
+        return Err(OsOutputError::MessagesSegmentNotConsumed {
+            segment_name: "L1",
+            remaining: messages_to_l1_segment_size,
+        });
+    }
 
     Ok(messages_to_l1)
 }
@@ -263,14 +275,21 @@ impl TryFromOutputIter for OutputIterParsedData {
         while messages_to_l2_iter.peek().is_some() {
             let message =
                 MessageToL2::try_from_output_iter(&mut messages_to_l2_iter, private_keys)?;
-            messages_to_l2_segment_size -= message.payload.0.len() + MESSAGE_TO_L2_CONST_FIELD_SIZE;
+            let consumed_felts = message.payload.0.len() + MESSAGE_TO_L2_CONST_FIELD_SIZE;
+            messages_to_l2_segment_size = messages_to_l2_segment_size
+                .checked_sub(consumed_felts)
+                .ok_or(OsOutputError::MessagesSegmentNotConsumed {
+                segment_name: "L2",
+                remaining: messages_to_l2_segment_size,
+            })?;
             messages_to_l2.push(message);
         }
-        assert_eq!(
-            messages_to_l2_segment_size, 0,
-            "Expected messages to L2 segment to be consumed, but {messages_to_l2_segment_size} \
-             felts were left.",
-        );
+        if messages_to_l2_segment_size != 0 {
+            return Err(OsOutputError::MessagesSegmentNotConsumed {
+                segment_name: "L2",
+                remaining: messages_to_l2_segment_size,
+            });
+        }
         Ok(Self {
             common_os_output: CommonOsOutput {
                 initial_root,
```
