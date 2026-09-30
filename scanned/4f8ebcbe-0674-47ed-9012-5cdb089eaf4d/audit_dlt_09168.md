# [?] block_stream: Move check to prevent subtraction with overflow

## Summary
Severity: Unknown
Chain: The Graph
Component: graphprotocol/graph-node
Published: 2020-12-14
Source: https://github.com/graphprotocol/graph-node/commit/6dc5c31c3eed2acd17c665541d72495696073661
Type: security-commit

## Details
block_stream: Move check to prevent subtraction with overflow

## Patch
### chain/ethereum/src/block_stream.rs
```diff
@@ -252,14 +252,14 @@ where
         // Only continue if the subgraph block ptr is behind the head block ptr.
         // subgraph_ptr > head_ptr shouldn't happen, but if it does, it's safest to just stop.
         if let Some(ptr) = subgraph_ptr {
-            self.metrics
-                .blocks_behind
-                .set((head_ptr.number - ptr.number) as f64);
-
             if ptr.number >= head_ptr.number {
                 return Box::new(future::ok(ReconciliationStep::Done))
                     as Box<dyn Future<Item = _, Error = _> + Send>;
             }
+
+            self.metrics
+                .blocks_behind
+                .set((head_ptr.number - ptr.number) as f64);
         }
 
         // Subgraph ptr is behind head ptr.
```
