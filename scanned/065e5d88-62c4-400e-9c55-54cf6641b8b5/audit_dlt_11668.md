# [?] fix: remove panic from stop gap scan loop

## Summary
Severity: Unknown
Chain: Bitcoin
Component: bitcoindevkit/bdk
Published: 2025-09-29
Source: https://github.com/bitcoindevkit/bdk/commit/745f805068ce33ee830b497c28fd37eb4c1aafb1
Type: security-commit

## Details
fix: remove panic from stop gap scan loop

## Patch
### crates/esplora/src/async_ext.rs
```diff
@@ -184,10 +184,10 @@ async fn fetch_latest_blocks<S: Sleeper>(
     client: &esplora_client::AsyncClient<S>,
 ) -> Result<BTreeMap<u32, BlockHash>, Error> {
     Ok(client
-        .get_blocks(None)
+        .get_block_infos(None)
         .await?
         .into_iter()
-        .map(|b| (b.time.height, b.id))
+        .map(|b| (b.height, b.id))
         .collect())
 }
 
@@ -314,8 +314,11 @@ where
     type TxsOfSpkIndex = (u32, Vec<esplora_client::Tx>, HashSet<Txid>);
 
     let mut update = TxUpdate::<ConfirmationBlockTime>::default();
-    let mut last_index = Option::<u32>::None;
     let mut last_active_index = Option::<u32>::None;
+    // Use consecutive_unused so unused count drives stop gap.
+    let mut consecutive_unused = 0usize;
+    // Treat stop_gap = 0 as 1 while preserving original semantics for other values.
+    let gap_limit = stop_gap.max(1);
 
     loop {
         let handles = keychain_spks
@@ -352,8 +355,10 @@ where
         }
 
         for (index, txs, evicted) in handles.try_collect::<Vec<TxsOfSpkIndex>>().await? {
-            last_index = Some(index);
-            if !txs.is_empty() {
+            if txs.is_empty() {
+                consecutive_unused = consecutive_unused.saturating_add(1);
+            } else {
+                consecutive_unused = 0;
                 last_active_index = Some(index);
             }
             for tx in txs {
@@ -368,13 +373,7 @@ where
                 .extend(evicted.into_iter().map(|txid| (txid, start_time)));
         }
 
-        let last_index = last_index.expect("Must be set since handles wasn't empty.");
-        let gap_limit_reached = if let Some(i) = last_active_index {
-            last_index >= i.saturating_add(stop_gap as u32)
-        } else {
-            last_index + 1 >= stop_gap as u32
-        };
-        if gap_limit_reached {
+        if consecutive_unused >= gap_limit {
             break;
         }
     }
@@ -596,7 +595,10 @@ mod test {
         let res = chain_update(&client, &latest_blocks, &cp, &anchors).await;
         use esplora_client::Error;
         assert!(
-            matches!(*res.unwrap_err(), Error::HeaderHashNotFound(hash) if hash == genesis_hash),
+            matches!(
+                *res.unwrap_err(),
+                Error::HeaderHashNotFound(hash) if hash == genesis_hash
+            ),
             "`chain_update` should error if it can't connect to the local CP",
         );
 
```

### crates/esplora/src/blocking_ext.rs
```diff
@@ -170,9 +170,9 @@ fn fetch_latest_blocks(
     client: &esplora_client::BlockingClient,
 ) -> Result<BTreeMap<u32, BlockHash>, Error> {
     Ok(client
-        .get_blocks(None)?
+        .get_block_infos(None)?
         .into_iter()
-        .map(|b| (b.time.height, b.id))
+        .map(|b| (b.height, b.id))
         .collect())
 }
 
@@ -282,8 +282,11 @@ fn fetch_txs_with_keychain_spks<I: Iterator<Item = Indexed<SpkWithExpectedTxids>
     type TxsOfSpkIndex = (u32, Vec<esplora_client::Tx>, HashSet<Txid>);
 
     let mut update = TxUpdate::<ConfirmationBlockTime>::default();
-    let mut last_index = Option::<u32>::None;
     let mut last_active_index = Option::<u32>::None;
+    // Use consecutive_unused so unused count drives stop gap.
+    let mut consecutive_unused = 0usize;
+    // Treat stop_gap = 0 as 1 while preserving original semantics for other values.
+    let gap_limit = stop_gap.max(1);
 
     loop {
         let handles = keychain_spks
@@ -321,8 +324,10 @@ fn fetch_txs_with_keychain_spks<I: Iterator<Item = Indexed<SpkWithExpectedTxids>
 
         for handle in handles {
             let (index, txs, evicted) = handle.join().expect("thread must not panic")?;
-            last_index = Some(index);
-            if !txs.is_empty() {
+            if txs.is_empty() {
+                consecutive_unused = consecutive_unused.saturating_add(1);
+            } else {
+                consecutive_unused = 0;
                 last_active_index = Some(index);
             }
             for tx in txs {
@@ -337,13 +342,7 @@ fn fetch_txs_with_keychain_spks<I: Iterator<Item = Indexed<SpkWithExpectedTxids>
                 .extend(evicted.into_iter().map(|txid| (txid, start_time)));
         }
 
-        let last_index = last_index.expect("Must be set since handles wasn't empty.");
-        let gap_limit_reached = if let Some(i) = last_active_index {
-            last_index >= i.saturating_add(stop_gap as u32)
-        } else {
-            last_index + 1 >= stop_gap as u32
-        };
-        if gap_limit_reached {
+        if consecutive_unused >= gap_limit {
             break;
         }
     }
```
