# [?] fix(invariant) - do not panic when evm call fails (#7994)

## Summary
Severity: Unknown
Chain: Tooling
Component: foundry-rs/foundry
Published: 2024-05-25
Source: https://github.com/foundry-rs/foundry/commit/d9e51e4807b62f101221a2fd36076c502399dbf9
Type: security-commit

## Details
fix(invariant) - do not panic when evm call fails (#7994)

fix(invariant) - remove expect when evm call

## Patch
### crates/evm/evm/src/executors/invariant/mod.rs
```diff
@@ -206,7 +206,9 @@ impl<'a> InvariantExecutor<'a> {
             let mut assume_rejects_counter = 0;
 
             while current_run < self.config.depth {
-                let tx = inputs.last().expect("no input generated");
+                let tx = inputs.last().ok_or_else(|| {
+                    TestCaseError::fail("No input generated to call fuzzed target.")
+                })?;
 
                 // Execute call from the randomly generated sequence and commit state changes.
                 let call_result = executor
@@ -216,7 +218,9 @@ impl<'a> InvariantExecutor<'a> {
                         tx.call_details.calldata.clone(),
                         U256::ZERO,
                     )
-                    .expect("could not make raw evm call");
+                    .map_err(|e| {
+                        TestCaseError::fail(format!("Could not make raw evm call: {}", e))
+                    })?;
 
                 if call_result.result.as_ref() == MAGIC_ASSUME {
                     inputs.pop();
@@ -229,8 +233,7 @@ impl<'a> InvariantExecutor<'a> {
                     }
                 } else {
                     // Collect data for fuzzing from the state changeset.
-                    let mut state_changeset =
-                        call_result.state_changeset.to_owned().expect("no changesets");
+                    let mut state_changeset = call_result.state_changeset.to_owned().unwrap();
 
                     if !&call_result.reverted {
                         collect_data(
```

### crates/evm/evm/src/executors/invariant/replay.rs
```diff
@@ -77,11 +77,7 @@ pub fn replay_run(
     let invariant_result = executor.call_raw(
         CALLER,
         invariant_contract.address,
-        invariant_contract
-            .invariant_function
-            .abi_encode_input(&[])
-            .expect("invariant should have no inputs")
-            .into(),
+        invariant_contract.invariant_function.abi_encode_input(&[])?.into(),
         U256::ZERO,
     )?;
     traces.push((TraceKind::Execution, invariant_result.traces.clone().unwrap()));
```

### crates/evm/evm/src/executors/invariant/result.rs
```diff
@@ -64,7 +64,7 @@ pub(crate) fn assert_invariants(
     let mut call_result = executor.call_raw(
         CALLER,
         invariant_contract.address,
-        func.abi_encode_input(&[]).expect("invariant should have no inputs").into(),
+        func.abi_encode_input(&[])?.into(),
         U256::ZERO,
     )?;
 
```

### crates/evm/evm/src/executors/mod.rs
```diff
@@ -674,9 +674,6 @@ pub struct RawCallResult {
     /// Scripted transactions generated from this call
     pub transactions: Option<BroadcastableTransactions>,
     /// The changeset of the state.
-    ///
-    /// This is only present if the changed state was not committed to the database (i.e. if you
-    /// used `call` and `call_raw` not `call_committing` or `call_raw_committing`).
     pub state_changeset: Option<StateChangeset>,
     /// The `revm::Env` after the call
     pub env: EnvWithHandlerCfg,
```
