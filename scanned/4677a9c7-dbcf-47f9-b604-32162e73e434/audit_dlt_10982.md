# [?] fix: prover deadlock bug

## Summary
Severity: Unknown
Chain: ZK
Component: succinctlabs/sp1
Published: 2025-03-29
Source: https://github.com/succinctlabs/sp1/commit/e387e03eb38c80413cb164aebe351dd6ade5864c
Type: security-commit

## Details
fix: prover deadlock bug

## Patch
### crates/core/machine/src/utils/prove.rs
```diff
@@ -244,13 +244,15 @@ where
         record_gen_handles.push(handle);
     }
 
-    let pv_stream: Vec<u8> = checkpoint_generator_handle.await.unwrap()?;
-
     drop(records_tx);
     drop(deferred);
 
     // Run the prover and wait for all proofs to be sent.
     prover.prove_stream(pk, records_rx, proof_tx, challenger).await.unwrap();
+
+    // Wait for the checkpoint generator to finish.
+    let pv_stream: Vec<u8> = checkpoint_generator_handle.await.unwrap()?;
+
     // Get the cycles from the aggregate report.
     let report_aggregate = report_aggregate.lock().unwrap();
     let cycles = report_aggregate.total_instruction_count();
```
