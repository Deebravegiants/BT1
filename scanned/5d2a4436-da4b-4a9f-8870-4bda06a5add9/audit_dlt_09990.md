# [?] Fix node writer reentrance causing non-contiguous writes in `async_write_node()`

## Summary
Severity: Unknown
Chain: Monad
Component: category-labs/monad
Published: 2026-02-18
Source: https://github.com/category-labs/monad/commit/cfbaf68474687b45a69d64b243454d01c8db5806
Type: security-commit

## Details
Fix node writer reentrance causing non-contiguous writes in `async_write_node()`

## Patch
### category/mpt/trie.cpp
```diff
@@ -1611,16 +1611,20 @@ async_write_node_result async_write_node(
                 node_writer->sender().remaining_buffer_bytes() == 0) {
                 // replace node writer
                 new_node_writer = replace_node_writer(aux, node_writer);
-                if (new_node_writer) {
-                    // initiate current node writer
-                    MONAD_DEBUG_ASSERT(
-                        node_writer->sender().written_buffer_bytes() ==
-                        node_writer->sender().buffer().size());
-                    node_writer->initiate();
-                    // shall be recycled by the i/o receiver
-                    node_writer.release();
-                    node_writer = std::move(new_node_writer);
+                if (!new_node_writer) {
+                    // Reentrance: the reentrant call may have interleaved
+                    // data into the writer, so continuing would make this
+                    // node non-contiguous on disk. Retry the entire write.
+                    goto retry;
                 }
+                // initiate current node writer
+                MONAD_DEBUG_ASSERT(
+                    node_writer->sender().written_buffer_bytes() ==
+                    node_writer->sender().buffer().size());
+                node_writer->initiate();
+                // shall be recycled by the i/o receiver
+                node_writer.release();
+                node_writer = std::move(new_node_writer);
             }
         }
     }
```
