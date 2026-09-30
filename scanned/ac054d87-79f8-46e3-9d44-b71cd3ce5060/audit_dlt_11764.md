# [?] fix: don't panic on current_block_height with an empty block store

## Summary
Severity: Unknown
Chain: Aleo
Component: AleoNet/snarkVM-test
Published: 2025-06-02
Source: https://github.com/AleoNet/snarkVM-test/commit/7ac619a6da83ae6d889d7236607152b24bb7339c
Type: security-commit

## Details
fix: don't panic on current_block_height with an empty block store

Signed-off-by: ljedrz <ljedrz@users.noreply.github.com>

## Patch
### ledger/store/src/block/mod.rs
```diff
@@ -1197,7 +1197,7 @@ impl<N: Network, B: BlockStorage<N>> BlockStore<N, B> {
 
     /// Returns the current block height.
     pub fn current_block_height(&self) -> u32 {
-        u32::try_from(self.tree.read().number_of_leaves()).unwrap() - 1
+        u32::try_from(self.tree.read().number_of_leaves()).unwrap().saturating_sub(1)
     }
 
     /// Returns the state root that contains the given `block height`.
@@ -1384,6 +1384,18 @@ mod tests {
 
     type CurrentNetwork = console::network::MainnetV0;
 
+    #[test]
+    fn test_current_block_height_empty() {
+        // Initialize a new block store.
+        let block_store = BlockStore::<CurrentNetwork, BlockMemory<_>>::open(StorageMode::new_test(None)).unwrap();
+
+        // Current_block_height shouldn't panic.
+        assert_eq!(block_store.current_block_height(), 0);
+
+        // Verify the equivalence of the alternative method.
+        assert_eq!(block_store.max_height().unwrap_or_default(), 0);
+    }
+
     #[test]
     fn test_insert_get_remove() {
         let rng = &mut TestRng::default();
```
