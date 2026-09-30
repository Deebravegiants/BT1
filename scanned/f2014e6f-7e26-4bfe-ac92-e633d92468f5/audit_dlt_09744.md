# [?] fix: race condition on consensus shutdown

## Summary
Severity: Unknown
Chain: Fedimint
Component: fedimint/fedimint
Published: 2025-04-28
Source: https://github.com/fedimint/fedimint/commit/87044ea5d3c9f8693af7639dbb2840835bbf7481
Type: security-commit

## Details
fix: race condition on consensus shutdown

## Patch
### fedimint-core/src/task.rs
```diff
@@ -69,6 +69,11 @@ impl TaskGroup {
         new_tg
     }
 
+    /// Is task group shutting down?
+    pub fn is_shutting_down(&self) -> bool {
+        self.inner.is_shutting_down()
+    }
+
     /// Tell all tasks in the group to shut down. This only initiates the
     /// shutdown process, it does not wait for the tasks to shut down.
     pub fn shutdown(&self) {
```

### fedimint-server/src/consensus/engine.rs
```diff
@@ -330,7 +330,24 @@ impl ConsensusEngine {
         loop {
             tokio::select! {
                 ordered_unit = ordered_unit_receiver.recv() => {
-                    let ordered_unit = ordered_unit.with_context(|| format!("Alepbft task exited prematurely. session_idx: {session_index}, item_idx: {item_index}"))?;
+                    let ordered_unit = ordered_unit.with_context(|| format!("Alepbft task exited prematurely. session_idx: {session_index}, item_idx: {item_index}")) ;
+                    let ordered_unit = match ordered_unit {
+                        Ok(o) => o,
+                        Err(err) => {
+                            // Chances are that alephbft is gone, because everything is shutting down
+                            //
+                            // If that's the case, yielding will simply not return, as our task
+                            // will not get executed anymore. This saves us from returning some "canceled"
+                            // state upwards, without reporting an error that isn't caused by this
+                            // task.
+                            while self.task_group.is_shutting_down() {
+                                info!(target: LOG_CONSENSUS, "Shutdown detected");
+                                sleep(Duration::from_millis(100)).await;
+                            }
+                            // Otherwise, just return the error upwards
+                            return Err(err);
+                        },
+                    };
 
                     if ordered_unit.round >= self.cfg.consensus.broadcast_rounds_per_session {
                         break;
```
