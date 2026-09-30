# [?] Scheculer: avoid cost underflow

## Summary
Severity: Unknown
Chain: Phala
Component: Phala-Network/phala-blockchain
Published: 2022-10-08
Source: https://github.com/Phala-Network/phala-blockchain/commit/12418df38ffbf31d265b95fe9f5dff15cabe6732
Type: security-commit

## Details
Scheculer: avoid cost underflow

## Patch
### crates/phala-scheduler/src/request_scheduler.rs
```diff
@@ -96,9 +96,11 @@ pub struct ServingGuard<FlowId: FlowIdType> {
 
 impl<FlowId: FlowIdType> Drop for ServingGuard<FlowId> {
     fn drop(&mut self) {
-        let actual_cost = self
-            .actual_cost
-            .unwrap_or_else(|| self.start_time.elapsed().as_micros() as VirtualTime);
+        let actual_cost = self.actual_cost.unwrap_or_else(|| {
+            let cost = self.start_time.elapsed().as_nanos() as VirtualTime;
+            // Scale it in order to avoid underflow while dividing the cost by the weight.
+            cost << 32
+        });
         self.queue
             .inner
             .lock()
```

### crates/phala-scheduler/src/task_scheduler.rs
```diff
@@ -201,9 +201,11 @@ impl<TaskId: TaskIdType> SchedulerInner<TaskId> {
 impl<TaskId: TaskIdType> Drop for RunningGuard<TaskId> {
     fn drop(&mut self) {
         if let Some(inner) = self.queue.upgrade() {
-            let actual_cost = self
-                .actual_cost
-                .unwrap_or_else(|| self.start_time.elapsed().as_nanos() as VirtualTime);
+            let actual_cost = self.actual_cost.unwrap_or_else(|| {
+                let cost = self.start_time.elapsed().as_nanos() as VirtualTime;
+                // Scale it in order to avoid underflow while dividing the cost by the weight.
+                cost << 32
+            });
             let vruntime = actual_cost / self.weight.max(1) as VirtualTime;
             inner.lock().unwrap().park(&self.task_id, vruntime.max(1));
         }
```
