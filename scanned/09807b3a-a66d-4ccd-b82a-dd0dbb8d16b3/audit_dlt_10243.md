# [?] Fix pherry panics while using headers-cache

## Summary
Severity: Unknown
Chain: Phala
Component: Phala-Network/phala-blockchain
Published: 2022-08-27
Source: https://github.com/Phala-Network/phala-blockchain/commit/7121d44cd34f3037fdbb7029540e68405bc7432b
Type: security-commit

## Details
Fix pherry panics while using headers-cache

## Patch
### standalone/pherry/src/headers_cache.rs
```diff
@@ -368,10 +368,10 @@ impl Client {
         let status = response.status();
         info!("Requested cache from {url} ({})", status.as_u16());
         if !status.is_success() {
-            return Err(anyhow!(
+            anyhow::bail!(
                 "Failed to fetch data from cache with status={}",
                 status.as_u16()
-            ));
+            );
         }
         let body = response.bytes().await.map_err(|err| {
             error!("Failed to read cache response: {err}");
```

### standalone/pherry/src/lib.rs
```diff
@@ -686,6 +686,10 @@ async fn maybe_sync_waiting_parablocks(
             .get_headers(info.headernum - 1)
             .await
             .unwrap_or_default();
+        if cached_headers.len() > 1 {
+            info!("The relaychain header is not staying at a justification checkpoint, skipping to sync paraheaders...");
+            return Ok(());
+        }
         if cached_headers.len() == 1 {
             fin_header = cached_headers
                 .remove(0)
@@ -702,7 +706,8 @@ async fn maybe_sync_waiting_parablocks(
     let (fin_header_num, proof) = match fin_header {
         Some(num) => num,
         None => {
-            return Err(anyhow!("The pRuntime is waiting for paraheaders, but pherry failed to get the fin_header_num"));
+            info!("No finalized paraheader found, skipping to sync paraheaders...");
+            return Ok(());
         }
     };
 
@@ -1142,6 +1147,7 @@ async fn bridge(
         }
         if args.parachain
             && !args.disable_sync_waiting_paraheaders
+            // `round == 0` is for old pruntimes which don't return `waiting_for_paraheaders`
             && (info.waiting_for_paraheaders || round == 0)
         {
             maybe_sync_waiting_parablocks(
```
