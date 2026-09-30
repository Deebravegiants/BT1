# [?] store: Avoid panic if GRAPH_STORE_CONNECTION_MIN_IDLE exceeds pool_size

## Summary
Severity: Unknown
Chain: The Graph
Component: graphprotocol/graph-node
Published: 2022-04-21
Source: https://github.com/graphprotocol/graph-node/commit/6ab162376883f693466653b800e0180c52c94325
Type: security-commit

## Details
store: Avoid panic if GRAPH_STORE_CONNECTION_MIN_IDLE exceeds pool_size

## Patch
### store/postgres/src/connection_pool.rs
```diff
@@ -10,6 +10,7 @@ use graph::cheap_clone::CheapClone;
 use graph::constraint_violation;
 use graph::prelude::tokio;
 use graph::prelude::tokio::time::Instant;
+use graph::slog::warn;
 use graph::util::timed_rw_lock::TimedMutex;
 use graph::{
     prelude::{
@@ -727,12 +728,25 @@ impl PoolInner {
 
         // Connect to Postgres
         let conn_manager = ConnectionManager::new(postgres_url.clone());
+        let min_idle = ENV_VARS.store.connection_min_idle.filter(|min_idle| {
+            if *min_idle <= pool_size {
+                true
+            } else {
+                warn!(
+                    logger_pool,
+                    "Configuration error: min idle {} exceeds pool size {}, ignoring min idle",
+                    min_idle,
+                    pool_size
+                );
+                false
+            }
+        });
         let builder: Builder<ConnectionManager<PgConnection>> = Pool::builder()
             .error_handler(error_handler.clone())
             .event_handler(event_handler.clone())
             .connection_timeout(ENV_VARS.store.connection_timeout)
             .max_size(pool_size)
-            .min_idle(ENV_VARS.store.connection_min_idle)
+            .min_idle(min_idle)
             .idle_timeout(Some(ENV_VARS.store.connection_idle_timeout));
         let pool = builder.build_unchecked(conn_manager);
         let fdw_pool = fdw_pool_size.map(|pool_size| {
```
