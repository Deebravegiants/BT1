# [?] fix: prevent panic in ChainDbFactory lock operations (op-rs/kona#2877)

## Summary
Severity: Unknown
Chain: Optimism
Component: ethereum-optimism/optimism
Published: 2025-09-29
Source: https://github.com/ethereum-optimism/optimism/commit/b82b49e1595f86eeda9632fc5c3c9690521dd3ff
Type: security-commit

## Details
fix: prevent panic in ChainDbFactory lock operations (op-rs/kona#2877)

Replace unwrap_or_else with proper error handling in ChainDbFactory
methods to prevent potential panics when RwLock is poisoned.

- Fix get_db() method to return StorageError::LockPoisoned instead of
panicking
- Fix report_metrics() method to handle lock acquisition failures
gracefully
- Add proper error logging for lock poisoning scenarios

## Patch
### crates/supervisor/storage/src/chaindb_factory.rs
```diff
@@ -106,7 +106,7 @@ impl ChainDbFactory {
     /// * `Ok(Arc<ChainDb>)` if the database exists.
     /// * `Err(StorageError)` if the database does not exist.
     pub fn get_db(&self, chain_id: ChainId) -> Result<Arc<ChainDb>, StorageError> {
-        let dbs = self.dbs.read().unwrap_or_else(|e| e.into_inner());
+        let dbs = self.dbs.read().map_err(|_| StorageError::LockPoisoned)?;
         dbs.get(&chain_id).cloned().ok_or_else(|| StorageError::DatabaseNotInitialised)
     }
 }
@@ -116,8 +116,13 @@ impl MetricsReporter for ChainDbFactory {
         let metrics_enabled = self.metrics_enabled.unwrap_or(false);
         if metrics_enabled {
             let dbs: Vec<Arc<ChainDb>> = {
-                let dbs_guard = self.dbs.read().unwrap_or_else(|e| e.into_inner());
-                dbs_guard.values().cloned().collect()
+                match self.dbs.read() {
+                    Ok(dbs_guard) => dbs_guard.values().cloned().collect(),
+                    Err(_) => {
+                        error!(target: "supervisor::storage", "Failed to acquire read lock for metrics reporting");
+                        return;
+                    }
+                }
             };
             for db in dbs {
                 db.report_metrics();
```
