# [?] fix(reth-bench): do not panic on empty results (#18570)

## Summary
Severity: Unknown
Chain: Ethereum
Component: paradigmxyz/reth
Published: 2025-09-19
Source: https://github.com/paradigmxyz/reth/commit/5bc507bfafe39f7691a68e51e41ab9c05b9fc86e
Type: security-commit

## Details
fix(reth-bench): do not panic on empty results (#18570)

## Patch
### bin/reth-bench/src/bench/new_payload_fcu.rs
```diff
@@ -169,7 +169,7 @@ impl Command {
         }
 
         // accumulate the results and calculate the overall Ggas/s
-        let gas_output = TotalGasOutput::new(gas_output_results);
+        let gas_output = TotalGasOutput::new(gas_output_results)?;
         info!(
             total_duration=?gas_output.total_duration,
             total_gas_used=?gas_output.total_gas_used,
```

### bin/reth-bench/src/bench/new_payload_only.rs
```diff
@@ -123,7 +123,7 @@ impl Command {
         }
 
         // accumulate the results and calculate the overall Ggas/s
-        let gas_output = TotalGasOutput::new(gas_output_results);
+        let gas_output = TotalGasOutput::new(gas_output_results)?;
         info!(
             total_duration=?gas_output.total_duration,
             total_gas_used=?gas_output.total_gas_used,
```

### bin/reth-bench/src/bench/output.rs
```diff
@@ -1,6 +1,7 @@
 //! Contains various benchmark output formats, either for logging or for
 //! serialization to / from files.
 
+use eyre::OptionExt;
 use reth_primitives_traits::constants::GIGAGAS;
 use serde::{ser::SerializeStruct, Serialize};
 use std::time::Duration;
@@ -145,15 +146,14 @@ pub(crate) struct TotalGasOutput {
 
 impl TotalGasOutput {
     /// Create a new [`TotalGasOutput`] from a list of [`TotalGasRow`].
-    pub(crate) fn new(rows: Vec<TotalGasRow>) -> Self {
+    pub(crate) fn new(rows: Vec<TotalGasRow>) -> eyre::Result<Self> {
         // the duration is obtained from the last row
-        let total_duration =
-            rows.last().map(|row| row.time).expect("the row has at least one element");
+        let total_duration = rows.last().map(|row| row.time).ok_or_eyre("empty results")?;
         let blocks_processed = rows.len() as u64;
         let total_gas_used: u64 = rows.into_iter().map(|row| row.gas_used).sum();
         let total_gas_per_second = total_gas_used as f64 / total_duration.as_secs_f64();
 
-        Self { total_gas_used, total_duration, total_gas_per_second, blocks_processed }
+        Ok(Self { total_gas_used, total_duration, total_gas_per_second, blocks_processed })
     }
 
     /// Return the total gigagas per second.
```
