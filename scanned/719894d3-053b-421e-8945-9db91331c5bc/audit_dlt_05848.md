# [?] fix: deflake //rs/tests/consensus:replica_determinism_test by allowing panics in "MR Batch Processor" thread (#10069)

## Summary
Severity: Unknown
Chain: Internet Computer
Component: dfinity/ic
Published: 2026-04-30
Source: https://github.com/dfinity/ic/commit/d35bc3c58fe100923178119e2abb623418fa170c
Type: security-commit

## Details
fix: deflake //rs/tests/consensus:replica_determinism_test by allowing panics in "MR Batch Processor" thread (#10069)

The `//rs/tests/consensus:replica_determinism_test` sometimes
[fails](https://dash.dm1-idx1.dfinity.network/invocation/74905fa6-4e55-4a7e-affd-2b4ebe411b4f?target=//rs/tests/consensus:replica_determinism_test#@407)
because the `assert_no_unallowed_log_patterns ` check finds a log of a
panic of the `MR Batch Processor` thread like:
```
thread 'MR Batch Processor' (1588) panicked at rs/state_manager/src/lib.rs:1036:17:
Unexpected sandbox state for canister ...
```
which is thrown because of the malicious behaviour which corrupts the
state of a node at a certain height.

Since this state corruption is by design we allow all panics in the `MR
Batch Processor` thread in this test.

## Patch
### rs/tests/consensus/replica_determinism_test.rs
```diff
@@ -180,6 +180,11 @@ fn main() -> Result<()> {
             "orchestrator_replica_process_start_attempts_total",
             3,
         )
+        // One of the nodes has a corrupted state which could cause a panic in the replica like:
+        //   thread 'MR Batch Processor' (1588) panicked at rs/state_manager/src/lib.rs:1036:17:
+        //   Unexpected sandbox state for canister ...
+        // Since this is expected we allow all panics in the "MR Batch Processor" thread:
+        .add_unallowed_log_pattern_except("panicked", "MR Batch Processor")
         .execute_from_args()?;
     Ok(())
 }
```
