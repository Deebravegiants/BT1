# [?] Fix overflow (#2361)

## Summary
Severity: Unknown
Chain: zkSync Lite
Component: matter-labs/zksync
Published: 2023-03-24
Source: https://github.com/matter-labs/zksync/commit/6c82ebcc3eb50239ffdc83295b6c2e7b9401e891
Type: security-commit

## Details
Fix overflow (#2361)

Signed-off-by: Danil <deniallugo@gmail.com>

## Patch
### core/bin/zksync_witness_generator/src/database.rs
```diff
@@ -262,12 +262,13 @@ impl DatabaseInterface for Database {
             .store_account_tree_cache(block, tree_cache)
             .await?;
 
-        connection
-            .chain()
-            .tree_cache_schema_bincode()
-            .remove_old_account_tree_cache(block - NUMBER_OF_STORED_ACCOUNT_TREE_CACHE)
-            .await?;
-
+        if block.0 > NUMBER_OF_STORED_ACCOUNT_TREE_CACHE {
+            connection
+                .chain()
+                .tree_cache_schema_bincode()
+                .remove_old_account_tree_cache(block - NUMBER_OF_STORED_ACCOUNT_TREE_CACHE)
+                .await?;
+        }
         Ok(())
     }
 
```

### core/lib/storage/src/chain/tree_cache/bincode_schema.rs
```diff
@@ -169,6 +169,7 @@ impl<'a, 'c> TreeCacheSchemaBincode<'a, 'c> {
         last_block: BlockNumber,
     ) -> QueryResult<()> {
         let start = Instant::now();
+
         loop {
             let res = sqlx::query!(
                 "DELETE 
```
