# [?] fix(store): Remove panic from `rewind` and `truncate` (#5233)

## Summary
Severity: Unknown
Chain: The Graph
Component: graphprotocol/graph-node
Published: 2024-02-27
Source: https://github.com/graphprotocol/graph-node/commit/9a20db721295aa3a777914b71f7f1d5e1cc4a114
Type: security-commit

## Details
fix(store): Remove panic from `rewind` and `truncate` (#5233)

## Patch
### store/postgres/src/deployment_store.rs
```diff
@@ -1328,14 +1328,14 @@ impl DeploymentStore {
     ) -> Result<StoreEvent, StoreError> {
         let conn = self.get_conn()?;
 
-        // Unwrap: If we are reverting then the block ptr is not `None`.
-        let block_ptr_from = Self::block_ptr_with_conn(&conn, site.cheap_clone())?.unwrap();
+        let block_ptr_from = Self::block_ptr_with_conn(&conn, site.cheap_clone())?;
 
         // Sanity check on block numbers
-        if block_ptr_from.number <= block_ptr_to.number {
+        let from_number = block_ptr_from.map(|ptr| ptr.number);
+        if from_number <= Some(block_ptr_to.number) {
             constraint_violation!(
                 "truncate must go backwards, but would go from block {} to block {}",
-                block_ptr_from.number,
+                from_number.unwrap_or(0),
                 block_ptr_to.number
             );
         }
@@ -1352,14 +1352,14 @@ impl DeploymentStore {
     ) -> Result<StoreEvent, StoreError> {
         let conn = self.get_conn()?;
 
-        // Unwrap: If we are reverting then the block ptr is not `None`.
-        let block_ptr_from = Self::block_ptr_with_conn(&conn, site.cheap_clone())?.unwrap();
+        let block_ptr_from = Self::block_ptr_with_conn(&conn, site.cheap_clone())?;
 
         // Sanity check on block numbers
-        if block_ptr_from.number <= block_ptr_to.number {
+        let from_number = block_ptr_from.map(|ptr| ptr.number);
+        if from_number <= Some(block_ptr_to.number) {
             constraint_violation!(
                 "rewind must go backwards, but would go from block {} to block {}",
-                block_ptr_from.number,
+                from_number.unwrap_or(0),
                 block_ptr_to.number
             );
         }
```
