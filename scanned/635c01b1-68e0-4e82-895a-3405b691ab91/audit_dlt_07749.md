# [?] fix(ress): avoid panic on Missing trie updates in ress provider witness construction (#18796)

## Summary
Severity: Unknown
Chain: Ethereum
Component: paradigmxyz/reth
Published: 2025-10-02
Source: https://github.com/paradigmxyz/reth/commit/661400e857b03b562bfb12ca42d82635c5864a93
Type: security-commit

## Details
fix(ress): avoid panic on Missing trie updates in ress provider witness construction (#18796)

## Patch
### crates/ress/provider/src/lib.rs
```diff
@@ -162,7 +162,14 @@ where
         let witness_state_provider = self.provider.state_by_block_hash(ancestor_hash)?;
         let mut trie_input = TrieInput::default();
         for block in executed_ancestors.into_iter().rev() {
-            trie_input.append_cached_ref(block.trie.as_ref().unwrap(), &block.hashed_state);
+            if let Some(trie_updates) = block.trie.as_ref() {
+                trie_input.append_cached_ref(trie_updates, &block.hashed_state);
+            } else {
+                trace!(target: "reth::ress_provider", ancestor = ?block.recovered_block().num_hash(), "Missing trie updates for ancestor block");
+                return Err(ProviderError::TrieWitnessError(
+                    "missing trie updates for ancestor".to_owned(),
+                ));
+            }
         }
         let mut hashed_state = db.into_state();
         hashed_state.extend(record.hashed_state);
```
