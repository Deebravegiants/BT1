# [?] async rodb sender lifetime heap-use-after-free asan fix

## Summary
Severity: Unknown
Chain: Monad
Component: category-labs/monad
Published: 2024-10-15
Source: https://github.com/category-labs/monad/commit/b40a60291226eab39e53da2f18e18377bac1c8dc
Type: security-commit

## Details
async rodb sender lifetime heap-use-after-free asan fix

## Patch
### libs/db/src/monad/mpt/db.cpp
```diff
@@ -955,6 +955,7 @@ namespace detail
             auto it = inflights.find(sender->block_id);
             auto pendings = std::move(it->second);
             inflights.erase(it);
+            std::shared_ptr<Node> root{};
 
             bool const block_alive_after_read =
                 sender->context.aux.version_is_valid_ondisk(sender->block_id);
@@ -963,8 +964,15 @@ namespace detail
                     sender->root =
                         detail::deserialize_node_from_receiver_result(
                             std::move(buffer_), buffer_off, io_state);
+                    root = sender->root;
                     sender->res_root = {
                         NodeCursor{*sender->root.get()}, find_result::success};
+                    {
+                        AsyncContext::TrieRootCache::ConstAccessor acc;
+                        MONAD_ASSERT(
+                            sender->context.root_cache.find(
+                                acc, sender->block_id) == false);
+                    }
                     sender->context.root_cache.insert(
                         sender->block_id, sender->root);
                 }
@@ -979,7 +987,9 @@ namespace detail
             }
 
             for (auto &invoc : pendings) {
-                invoc(sender->root);
+                // Calling invoc() may invoke user code which deletes `sender`.
+                // It is no longer safe to rely on the `sender` lifetime
+                invoc(root);
             }
         }
     };
```
