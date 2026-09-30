# [?] sync: Fix sync_block_from_best_peer_inner assert failed panic (#955)

## Summary
Severity: Unknown
Chain: Starcoin
Component: starcoinorg/starcoin
Published: 2020-07-25
Source: https://github.com/starcoinorg/starcoin/commit/100a01fb1c967d1b4dd0dc1b9d5787d45c9ba399
Type: security-commit

## Details
sync: Fix sync_block_from_best_peer_inner assert failed panic (#955)

## Patch
### sync/src/block_sync/mod.rs
```diff
@@ -156,7 +156,7 @@ where
         start: bool,
         download_address: Addr<DownloadActor<C>>,
     ) -> BlockSyncTaskRef<C> {
-        assert!(ancestor_header.number() < target_number);
+        debug_assert!(ancestor_header.number() < target_number);
         let address = BlockSyncTaskActor::create(move |_ctx| Self {
             ancestor_number: ancestor_header.number(),
             target_number,
```

### sync/src/download.rs
```diff
@@ -340,7 +340,6 @@ where
                     min_behind as usize,
                 )
                 .await?;
-
                 let block_sync_task = BlockSyncTaskActor::launch(
                     &ancestor_header,
                     latest_number,
@@ -449,6 +448,9 @@ where
                 {
                     Ok(ancestor) => {
                         if let Some(ancestor_header) = ancestor {
+                            if ancestor_header.number() >= end_number {
+                                return Ok(true);
+                            }
                             let block_sync_task = BlockSyncTaskActor::launch(
                                 &ancestor_header,
                                 end_number,
```
