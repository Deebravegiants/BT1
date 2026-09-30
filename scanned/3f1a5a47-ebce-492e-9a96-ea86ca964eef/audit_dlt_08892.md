# [?] fix(rpc/pending): serve empty instead of panicking on non-chaining pending data

## Summary
Severity: Unknown
Chain: Starknet
Component: software-mansion/pathfinder
Published: 2026-06-29
Source: https://github.com/software-mansion/pathfinder/commit/a8f2c78962f784c57086697e287cb571382fcea9
Type: security-commit

## Details
fix(rpc/pending): serve empty instead of panicking on non-chaining pending data

## Patch
### crates/rpc/src/pending.rs
```diff
@@ -91,13 +91,11 @@ impl PendingWatcher {
             //   - the pre-latest block does not exist and the pre-confirmed block is the
             //   child of our latest stored block.
             match pre_latest {
-                // Is pre-latest the next block?
-                Some(pre_latest) if pre_latest.block.number == latest.number + 1 => {
-                    assert_eq!(
-                        pre_latest.block.number + 1,
-                        pre_confirmed.number,
-                        "Pre-confirmed block should be child of pre-latest"
-                    );
+                // Is pre-latest the next block, with pre-confirmed as its child?
+                Some(pre_latest)
+                    if pre_latest.block.number == latest.number + 1
+                        && pre_latest.block.number + 1 == pre_confirmed.number =>
+                {
                     // Set pre-latest block parent state commitment, clone rest of the data.
                     let pre_latest = pre_latest.clone();
                     let pre_latest_state_update = pre_latest
@@ -120,15 +118,11 @@ impl PendingWatcher {
                         number: pre_confirmed.number,
                     }
                 }
-                // Is pre-latest already in the database?
-                Some(pre_latest) if pre_latest.block.number == latest.number => {
-                    // We'll ignore pre-latest data here but let's make sure everything is
-                    // still as expected.
-                    assert_eq!(
-                        pre_latest.block.number + 1,
-                        pre_confirmed.number,
-                        "Pre-confirmed block should be child of pre-latest"
-                    );
+                // Is pre-latest already in the database, with pre-confirmed as its child?
+                Some(pre_latest)
+                    if pre_latest.block.number == latest.number
+                        && pre_latest.block.number + 1 == pre_confirmed.number =>
+                {
                     // Set pre-latest data to `None`, pre-confirmed block parent state
                     // commitment and clone rest of the data.
                     let pre_confirmed_block = PendingBlocks {
@@ -203,8 +197,7 @@ pub fn find_finalized_tx_data(
             .pre_confirmed_tx_receipts_and_events()
             .iter()
             .find(|(r, _)| r.transaction_hash == tx_hash)
-            .cloned()
-            .expect("Receipt should exist if the transaction exists");
+            .cloned()?;
         return Some(FinalizedTxData {
             block_number: pending.pre_confirmed_block_number(),
             transaction: tx.clone(),
@@ -220,14 +213,11 @@ pub fn find_finalized_tx_data(
             .iter()
             .find(|t| t.hash == tx_hash)
         {
-            let (receipt, events) = pending
-                .pre_latest_tx_receipts_and_events()
-                .and_then(|rs| {
-                    rs.iter()
-                        .find(|(r, _)| r.transaction_hash == tx_hash)
-                        .cloned()
-                })
-                .expect("Receipt should exist if the transaction exists");
+            let (receipt, events) = pending.pre_latest_tx_receipts_and_events().and_then(|rs| {
+                rs.iter()
+                    .find(|(r, _)| r.transaction_hash == tx_hash)
+                    .cloned()
+            })?;
             return Some(FinalizedTxData {
                 block_number: pre_latest_block.number,
                 transaction: tx.clone(),
@@ -657,8 +647,9 @@ mod tests {
     }
 
     #[test]
-    #[should_panic]
-    fn pre_confirmed_is_not_child_of_pre_latest_panics() {
+    fn pre_confirmed_not_child_of_pre_latest_defaults_to_empty() {
+        // A pre-confirmed block that doesn't chain onto the pre-latest falls back
+        // to an empty pending block.
         let cache = Arc::new(PendingDataCache::new());
         let uut = PendingWatcher::new(cache.clone());
 
@@ -687,8 +678,11 @@ mod tests {
         tx.insert_block_header(&latest).unwrap();
 
         let pending = invalid_pre_confirmed_block_with_pre_latest(&latest);
-        cache.store(pending.clone());
-        let _ = uut.get(&tx, RpcVersion::V09).unwrap();
+        cache.store(pending);
+
+        let result = uut.get(&tx, RpcVersion::V09).unwrap();
+
+        pretty_assertions_sorted::assert_eq_sorted!(result, PendingData::empty(&latest));
     }
 
     fn empty_pre_confirmed_block(latest: &BlockHeader) -> PendingData {
```
