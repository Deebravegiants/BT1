# [?] store: Fix race condition in tests

## Summary
Severity: Unknown
Chain: The Graph
Component: graphprotocol/graph-node
Published: 2022-03-28
Source: https://github.com/graphprotocol/graph-node/commit/53b64050eba0a6282564b37b396620b1d965d3fd
Type: security-commit

## Details
store: Fix race condition in tests

Tests wait for the queue to be empty to see the result of changes; the code
previously emptied the queue before a possible error had been recorded,
which would cause test failures.

## Patch
### store/postgres/src/writable.rs
```diff
@@ -495,12 +495,13 @@ impl Queue {
                 // incorrect results.
                 let req = queue.queue.peek().await;
                 let res = graph::spawn_blocking_allow_panic(move || req.execute()).await;
-                // The request has been handled. It's now safe to remove it
-                // from the queue
-                queue.queue.pop().await;
 
                 match res {
-                    Ok(Ok(())) => { /* nothing to do  */ }
+                    Ok(Ok(())) => {
+                        // The request has been handled. It's now safe to remove it
+                        // from the queue
+                        queue.queue.pop().await;
+                    }
                     Ok(Err(e)) => {
                         error!(logger, "Subgraph writer failed"; "error" => e.to_string());
                         queue.record_err(e);
@@ -565,6 +566,8 @@ impl Queue {
         }
     }
 
+    /// Record the error `e`, mark the queue as poisoned, and remove all
+    /// pending requests. The queue can not be used anymore
     fn record_err(&self, e: StoreError) {
         *self.write_err.lock().unwrap() = Some(e);
         self.poisoned.store(true, Ordering::SeqCst);
```
