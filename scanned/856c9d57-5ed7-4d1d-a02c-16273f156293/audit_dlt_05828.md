# [?] [actix migration] Fix telemetry actor panic. (#14217)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2025-09-09
Source: https://github.com/near/nearcore/commit/b8e75ab3f3ec1270a484708b02f32b646c7f18c8
Type: security-commit

## Details
[actix migration] Fix telemetry actor panic. (#14217)

actix::spawn is no longer compatible with the new actor runtime.
Unfortunately this one was missed. It wasn't caught by any integration
tests because I suppose no test actually wanted to export a real
telemetry data point.

For already-migrated code, there are 3 more calls to actix::spawn in
Chunk Distribution Network code. Those would also crash if the code path
is enabled, but I'll do that in a separate PR in order to make this one
merge faster.

## Patch
### chain/telemetry/src/lib.rs
```diff
@@ -1,8 +1,12 @@
 mod metrics;
 
 use futures::FutureExt;
+use near_async::ActorSystem;
+use near_async::futures::FutureSpawnerExt;
 use near_async::messaging::{Actor, Handler};
 use near_async::time::{Duration, Instant};
+use near_async::tokio::TokioRuntimeHandle;
+use near_performance_metrics as _; // Suppress cargo machete
 use near_performance_metrics_macros::perf;
 use reqwest::Client;
 use std::ops::Sub;
@@ -37,21 +41,16 @@ pub struct TelemetryEvent {
 }
 
 pub struct TelemetryActor {
+    handle: TokioRuntimeHandle<TelemetryActor>,
     config: TelemetryConfig,
     client: Client,
     last_telemetry_update: Instant,
 }
 
-impl Default for TelemetryActor {
-    fn default() -> Self {
-        Self::new(TelemetryConfig::default())
-    }
-}
-
 impl Actor for TelemetryActor {}
 
 impl TelemetryActor {
-    pub fn new(config: TelemetryConfig) -> Self {
+    fn new(handle: TokioRuntimeHandle<TelemetryActor>, config: TelemetryConfig) -> Self {
         for endpoint in &config.endpoints {
             if endpoint.is_empty() {
                 panic!(
@@ -68,12 +67,24 @@ impl TelemetryActor {
 
         let reporting_interval = config.reporting_interval;
         Self {
+            handle,
             config,
             client,
             // Let the node report telemetry info at the startup.
             last_telemetry_update: Instant::now().sub(reporting_interval),
         }
     }
+
+    pub fn spawn_tokio_actor(
+        actor_system: ActorSystem,
+        config: TelemetryConfig,
+    ) -> TokioRuntimeHandle<TelemetryActor> {
+        let builder = actor_system.new_tokio_builder();
+        let handle = builder.handle();
+        let actor = TelemetryActor::new(handle.clone(), config);
+        builder.spawn_tokio_actor(actor);
+        handle
+    }
 }
 
 impl Handler<TelemetryEvent> for TelemetryActor {
@@ -89,8 +100,8 @@ impl Handler<TelemetryEvent> for TelemetryActor {
         for endpoint in &self.config.endpoints {
             let endpoint = endpoint.clone();
             let client = self.client.clone();
-            near_performance_metrics::actix::spawn(
-                "telemetry",
+            self.handle.spawn(
+                "send telemetry",
                 client
                     .post(endpoint.clone())
                     .header("Content-Type", "application/json")
```

### integration-tests/src/env/setup.rs
```diff
@@ -56,7 +56,7 @@ use near_primitives::version::{PROTOCOL_VERSION, get_protocol_upgrade_schedule};
 use near_store::adapter::StoreAdapter;
 use near_store::genesis::initialize_genesis_state;
 use near_store::test_utils::create_test_store;
-use near_telemetry::TelemetryActor;
+use near_telemetry::{TelemetryActor, TelemetryConfig};
 use nearcore::NightshadeRuntime;
 use num_rational::Ratio;
 use std::sync::Arc;
@@ -144,7 +144,8 @@ fn setup(
         ShardTracker::new(TrackedShardsConfig::AllShards, epoch_manager.clone(), signer.clone());
 
     let actor_system = ActorSystem::new();
-    let telemetry = actor_system.spawn_tokio_actor(TelemetryActor::default());
+    let telemetry =
+        TelemetryActor::spawn_tokio_actor(actor_system.clone(), TelemetryConfig::default());
     let config = {
         let mut base = ClientConfig::test(
             skip_sync_wait,
```

### integration-tests/src/tests/network/runner.rs
```diff
@@ -32,7 +32,7 @@ use near_primitives::network::PeerId;
 use near_primitives::test_utils::create_test_signer;
 use near_primitives::types::{AccountId, ValidatorId};
 use near_store::genesis::initialize_genesis_state;
-use near_telemetry::TelemetryActor;
+use near_telemetry::{TelemetryActor, TelemetryConfig};
 use nearcore::NightshadeRuntime;
 use std::collections::HashSet;
 use std::future::Future;
@@ -76,7 +76,8 @@ fn setup_network_node(
     );
 
     let actor_system = ActorSystem::new();
-    let telemetry_actor = actor_system.spawn_tokio_actor(TelemetryActor::default());
+    let telemetry_actor =
+        TelemetryActor::spawn_tokio_actor(actor_system.clone(), TelemetryConfig::default());
 
     let db = node_storage.into_inner(near_store::Temperature::Hot);
     let mut client_config = ClientConfig::test(false, 100, 200, num_validators, false, true, true);
```

### nearcore/src/lib.rs
```diff
@@ -345,7 +345,7 @@ pub fn start_with_config_and_synchronization(
     };
 
     let telemetry =
-        actor_system.spawn_tokio_actor(TelemetryActor::new(config.telemetry_config.clone()));
+        TelemetryActor::spawn_tokio_actor(actor_system.clone(), config.telemetry_config.clone());
     let chain_genesis = ChainGenesis::new(&config.genesis.config);
     let state_roots = near_store::get_genesis_state_roots(runtime.store())?
         .expect("genesis should be initialized.");
```
