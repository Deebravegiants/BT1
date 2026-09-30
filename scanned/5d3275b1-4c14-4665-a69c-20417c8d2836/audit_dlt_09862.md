# [?] upstream(core): Fix execution driver panic which became possible due to synchronous tx execution (#8100)

## Summary
Severity: Unknown
Chain: IOTA
Component: iotaledger/iota
Published: 2025-08-05
Source: https://github.com/iotaledger/iota/commit/3ffe7fbb997635b6d3e7f728bc0e8139ae313a88
Type: security-commit

## Details
upstream(core): Fix execution driver panic which became possible due to synchronous tx execution (#8100)

- Upstream range: [v1.43.1, v1.44.3)
- Port commit:
-
https://github.com/MystenLabs/sui/commit/b300c776acbc702fd888b7581f955bf1b8a56c02
- Description:

Fix execution driver panic which became possible due to synchronous tx
execution.
Crash found by antithesis.
Removed the retry loop which has been disabled everywhere except mainnet
for some time.

Part of #5727

- [x] Basic tests (linting, compilation, formatting, unit/integration
tests)
- [ ] Patch-specific tests (correctness, functionality coverage)
- [ ] I have added tests that prove my fix is effective or that my
feature works
- [ ] I have checked that new and existing unit tests pass locally with
my changes

## Patch
### crates/iota-core/src/execution_driver.rs
```diff
@@ -2,34 +2,25 @@
 // Modifications Copyright (c) 2024 IOTA Stiftung
 // SPDX-License-Identifier: Apache-2.0
 
-use std::{
-    sync::{Arc, Weak},
-    time::Duration,
-};
+use std::sync::{Arc, Weak};
 
+use iota_common::fatal;
 use iota_macros::fail_point_async;
 use iota_metrics::{monitored_scope, spawn_monitored_task};
-use iota_protocol_config::Chain;
+use iota_types::error::IotaError;
 use rand::{
     Rng, SeedableRng,
     rngs::{OsRng, StdRng},
 };
-use tokio::{
-    sync::{Semaphore, mpsc::UnboundedReceiver, oneshot},
-    time::sleep,
-};
-use tracing::{Instrument, error, error_span, info, trace};
+use tokio::sync::{Semaphore, mpsc::UnboundedReceiver, oneshot};
+use tracing::{Instrument, error_span, info, trace, warn};
 
 use crate::{authority::AuthorityState, transaction_manager::PendingCertificate};
 
 #[cfg(test)]
 #[path = "unit_tests/execution_driver_tests.rs"]
 mod execution_driver_tests;
 
-// Execution should not encounter permanent failures, so any failure can and
-// needs to be retried.
-pub const EXECUTION_MAX_ATTEMPTS: u32 = 10;
-const EXECUTION_FAILURE_RETRY_INTERVAL: Duration = Duration::from_secs(1);
 const QUEUEING_DELAY_SAMPLING_RATIO: f64 = 0.05;
 
 /// When a notification that a new pending transaction is received we activate
@@ -45,15 +36,6 @@ pub async fn execution_process(
     let limit = Arc::new(Semaphore::new(num_cpus::get()));
     let mut rng = StdRng::from_rng(&mut OsRng).unwrap();
 
-    let is_mainnet = {
-        let Some(state) = authority_state.upgrade() else {
-            info!("Authority state has shutdown. Exiting ...");
-            return;
-        };
-
-        state.get_chain_identifier().chain() == Chain::Mainnet
-    };
-
     // Loop whenever there is a signal that a new transactions is ready to process.
     loop {
         let _scope = monitored_scope("ExecutionDriver::loop");
@@ -136,25 +118,22 @@ pub async fn execution_process(
             if let Ok(true) = authority.try_is_tx_already_executed(&digest) {
                 return;
             }
-            let mut attempts = 0;
-            loop {
-                fail_point_async!("transaction_execution_delay");
-                attempts += 1;
-                let res = authority
-                    .try_execute_immediately(&certificate, expected_effects_digest, &epoch_store_clone);
-                if let Err(e) = res {
-                    // Tighten this check everywhere except mainnet - if we don't see an increase in
-                    // these crashes we will remove the retries.
-                    if !is_mainnet || attempts == EXECUTION_MAX_ATTEMPTS {
-                        panic!("Failed to execute certified transaction {digest:?} after {attempts} attempts! error={e} certificate={certificate:?}");
-                    }
-                    // Assume only transient failure can happen. Permanent failure is probably
-                    // a bug. There is nothing that can be done to recover from permanent failures.
-                    error!(tx_digest=?digest, "Failed to execute certified transaction {digest:?}! attempt {attempts}, {e}");
-                    sleep(EXECUTION_FAILURE_RETRY_INTERVAL).await;
-                } else {
-                    break;
+
+            fail_point_async!("transaction_execution_delay");
+
+            match authority.try_execute_immediately(
+                &certificate,
+                expected_effects_digest,
+                &epoch_store_clone,
+            ) {
+                Err(IotaError::ValidatorHaltedAtEpochEnd) => {
+                    warn!("Could not execute transaction {digest:?} because validator is halted at epoch end. certificate={certificate:?}");
+                    return;
+                }
+                Err(e) => {
+                    fatal!("Failed to execute certified transaction {digest:?}! error={e} certificate={certificate:?}");
                 }
+                _ => (),
             }
             authority
                 .metrics
```
