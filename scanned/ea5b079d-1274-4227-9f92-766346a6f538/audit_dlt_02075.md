# [?] graph, store: Fix potential race condition in BoundedQueue.clear()

## Summary
Severity: Unknown
Chain: The Graph
Component: graphprotocol/graph-node
Published: 2022-03-18
Source: https://github.com/graphprotocol/graph-node/commit/224196b89904b1aa8fb7f5867f7cf4e6f54ff38d
Type: security-commit

## Details
graph, store: Fix potential race condition in BoundedQueue.clear()

Rather than clearing the queue by removing entries in bulk, which could
race against a pop at the same time, clear the queue by popping one entry
at a time.

## Patch
### graph/src/util/bounded_queue.rs
```diff
@@ -58,6 +58,24 @@ impl<T: Clone> BoundedQueue<T> {
         item
     }
 
+    /// Get an item from the queue without blocking; if the queue is empty,
+    /// return `None`
+    pub fn try_pop(&self) -> Option<T> {
+        let permit = match self.pop_semaphore.try_acquire() {
+            Err(_) => return None,
+            Ok(permit) => permit,
+        };
+        let item = self
+            .queue
+            .lock()
+            .unwrap()
+            .pop_front()
+            .expect("the queue is not empty");
+        permit.forget();
+        self.push_semaphore.add_permits(1);
+        Some(item)
+    }
+
     /// Take an item from the front of the queue and return a copy. If the
     /// queue is currently empty this method blocks until an item is
     /// available.
@@ -125,19 +143,8 @@ impl<T: Clone> BoundedQueue<T> {
         queue.iter().rev().fold(init, f)
     }
 
-    pub async fn clear(&self) {
-        let pushed = {
-            let mut queue = self.queue.lock().unwrap();
-            let pushed = queue.len();
-            queue.clear();
-            pushed
-        };
-        self.push_semaphore.add_permits(pushed);
-        let _permits = self
-            .pop_semaphore
-            .acquire_many(pushed as u32)
-            .await
-            .expect("we never close the pop_semaphore");
-        _permits.forget();
+    /// Clear the queue by popping entries until there are none left
+    pub fn clear(&self) {
+        while let Some(_) = self.try_pop() {}
     }
 }
```

### store/postgres/src/writable.rs
```diff
@@ -488,7 +488,7 @@ impl Queue {
                 if let Err(e) = res {
                     *queue.write_err.lock().unwrap() = Some(e);
                     queue.poisoned.store(true, Ordering::SeqCst);
-                    queue.queue.clear().await;
+                    queue.queue.clear();
                     return;
                 }
             }
```
