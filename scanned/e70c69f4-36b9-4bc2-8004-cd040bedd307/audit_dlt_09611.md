# [?] Fix reentrant dead lock of delete_all. (#894)

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2020-01-11
Source: https://github.com/Conflux-Chain/conflux-rust/commit/847d528e762b3e90dd7859759e0d36ab3d0c2472
Type: security-commit

## Details
Fix reentrant dead lock of delete_all. (#894)

## Patch
### core/src/storage/impls/delta_mpt/subtrie_visitor.rs
```diff
@@ -601,6 +601,7 @@ impl<'trie, 'db: 'trie> SubTrieVisitor<'trie, 'db> {
                 child_node,
                 ..
             } => {
+                drop(trie_node_ref);
                 let values = self
                     .new_visitor_for_subtree(child_node.clone().into())
                     .traversal(key, key_remaining)?;
```
