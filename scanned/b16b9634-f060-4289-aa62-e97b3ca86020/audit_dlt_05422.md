# [?] Fix use after free accessing rodb cache nodes

## Summary
Severity: Unknown
Chain: Monad
Component: monad-crypto/monad
Published: 2025-07-10
Source: https://github.com/category-labs/monad/commit/07aa4f4461214cd447af6d58fe27603eb600d204
Type: security-commit

## Details
Fix use after free accessing rodb cache nodes

Since the ownership of the child nodes is implicitly implied by owning
the root node, share the node pointer only with requests that have the
same parent node. This will imply that they share root ownership as well
and can share the child pointer.

Add parent node to the key of inflights hash to ensure this property.

## Patch
### libs/db/src/monad/mpt/find_request_sender.hpp
```diff
@@ -14,11 +14,27 @@
 
 MONAD_MPT_NAMESPACE_BEGIN
 
+struct inflight_node_hasher
+{
+    constexpr size_t
+    operator()(std::pair<chunk_offset_t, Node *> const &v) const noexcept
+    {
+        return chunk_offset_t_hasher{}(v.first) ^
+               fnv1a_hash<Node *>()(v.second);
+    }
+};
+
+// Index in progress node ios by physical read offset and parent node pointer.
+// Nodes in cache are implicitly owned by taking reference to the root node.
+// Since result of io is shared between requests, they need to share the
+// root node to ensure proper ownership. Because nodes in cache are unique,
+// having a pointer to parent as key ensures requests share the same root node
+// as well.
 using inflight_node_t = unordered_dense_map<
-    chunk_offset_t,
+    std::pair<chunk_offset_t, Node *>,
     std::vector<std::function<MONAD_ASYNC_NAMESPACE::result<void>(
         NodeCursor, std::shared_ptr<Node>)>>,
-    chunk_offset_t_hasher>;
+    inflight_node_hasher>;
 
 template <class T>
 concept return_type =
@@ -163,7 +179,8 @@ struct find_request_sender<T>::find_receiver
                 sender->root_.node->set_next(branch_index, std::move(node_ptr));
             }
         }
-        auto it = sender->inflights_.find(next_offset);
+        auto it =
+            sender->inflights_.find(std::pair(next_offset, sender->root_.node));
         if (it != sender->inflights_.end()) {
             auto pendings = std::move(it->second);
             sender->inflights_.erase(it);
@@ -246,11 +263,13 @@ inline MONAD_ASYNC_NAMESPACE::result<void> find_request_sender<T>::operator()(
                     subtrie_with_sender_lifetime_;
                 return this->resume_(io_state, root);
             };
-            if (auto lt = inflights_.find(offset); lt != inflights_.end()) {
+            auto offset_node = std::pair(offset, node);
+            if (auto lt = inflights_.find(offset_node);
+                lt != inflights_.end()) {
                 lt->second.emplace_back(cont);
                 return success();
             }
-            inflights_[offset].emplace_back(cont);
+            inflights_[offset_node].emplace_back(cont);
             find_receiver receiver(this, io_state, branch);
             detail::initiate_async_read_update(
                 *aux_.io, std::move(receiver), receiver.bytes_to_read);
```
