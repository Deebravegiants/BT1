# [?] Fix int overflow

## Summary
Severity: Unknown
Chain: Phala
Component: Phala-Network/phala-blockchain
Published: 2022-05-10
Source: https://github.com/Phala-Network/phala-blockchain/commit/ce7d7a2b8a9b4bfa3f069428f80fdde08284f1c8
Type: security-commit

## Details
Fix int overflow

## Patch
### standalone/pherry/src/headers_cache.rs
```diff
@@ -317,11 +317,11 @@ async fn grab_storage_changes(
         return Ok(0);
     }
 
-    let to = start_at + count - 1;
+    let to = start_at.saturating_add(count - 1);
     let mut grabbed = 0;
 
     for from in (start_at..=to).step_by(batch_size as _) {
-        let to = to.min(from + batch_size - 1);
+        let to = to.min(from.saturating_add(batch_size - 1));
         let headers = crate::fetch_storage_changes(&api.client, None, from, to).await?;
         for header in headers {
             f(header)?;
```

### standalone/pherry/src/lib.rs
```diff
@@ -316,7 +316,7 @@ pub async fn batch_sync_storage_changes(
     let mut fetcher = prefetcher::PrefetchClient::new();
 
     for from in (from..=to).step_by(batch_size as _) {
-        let to = to.min(from + batch_size - 1);
+        let to = to.min(from.saturating_add(batch_size - 1));
         let storage_changes = fetcher
             .fetch_storage_changes(&api.client, cache, from, to)
             .await?;
```
