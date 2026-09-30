# [?] Fix execution driver panic which became possible due to synchronous tx execution (#21292)

## Summary
Severity: Unknown
Chain: Sui
Component: MystenLabs/sui
Published: 2025-02-20
Source: https://github.com/MystenLabs/sui/commit/b300c776acbc702fd888b7581f955bf1b8a56c02
Type: security-commit

## Details
Fix execution driver panic which became possible due to synchronous tx execution (#21292)

Crash found by antithesis.

I'm also removing the retry loop which has been disabled everywhere
except mainnet for some time.

## Patch
### crates/sui-core/src/execution_driver.rs
```diff
@@ -1,23 +1,18 @@
 // Copyright (c) Mysten Labs, Inc.
 // SPDX-License-Identifier: Apache-2.0
 
-use std::{
-    sync::{Arc, Weak},
-    time::Duration,
-};
+use std::sync::{Arc, Weak};
 
+use mysten_common::fatal;
 use mysten_metrics::{monitored_scope, spawn_monitored_task};
 use rand::{
     rngs::{OsRng, StdRng},
     Rng, SeedableRng,
 };
 use sui_macros::fail_point_async;
-use sui_protocol_config::Chain;
-use tokio::{
-    sync::{mpsc::UnboundedReceiver, oneshot, Semaphore},
-    time::sleep,
-};
-use tracing::{error, error_span, info, trace, Instrument};
+use sui_types::error::SuiError;
+use tokio::sync::{mpsc::UnboundedReceiver, oneshot, Semaphore};
+use tracing::{error_span, info, trace, warn, Instrument};
 
 use crate::authority::AuthorityState;
 use crate::transaction_manager::PendingCertificate;
@@ -26,10 +21,6 @@ use crate::transaction_manager::PendingCertificate;
 #[path = "unit_tests/execution_driver_tests.rs"]
 mod execution_driver_tests;
 
-// Execution should not encounter permanent failures, so any failure can and needs
-// to be retried.
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
@@ -134,26 +116,22 @@ pub async fn execution_process(
             if authority.is_tx_already_executed(&digest) {
                 return;
             }
-            let mut attempts = 0;
-            loop {
-                fail_point_async!("transaction_execution_delay");
-                attempts += 1;
-                let res = authority
-                    .try_execute_immediately(&certificate, expected_effects_digest, &epoch_store_clone)
-                    .await;
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
+            ).await {
+                Err(SuiError::ValidatorHaltedAtEpochEnd) => {
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
