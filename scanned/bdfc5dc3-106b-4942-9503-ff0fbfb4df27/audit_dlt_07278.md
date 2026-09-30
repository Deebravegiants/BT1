# [?] fix: epoch manager deadlock (#12913)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2025-02-12
Source: https://github.com/near/nearcore/commit/0e2173040413579a8d447fdcacd112976d3abb5f
Type: security-commit

## Details
fix: epoch manager deadlock (#12913)

The fact that `EpochManagerHandle` is just a wrapper over
`Arc<RwLock<EpochManager>>` became a footgun. It is tempting to call its
own methods, like we did in `get_epoch_config` and `get_shard_config`
for a long time. But this leads to grabbing lock twice in read mode.
That's obvious thing to fix but I'll also tell how I discovered it.

We didn't hit it before, as RwLock allows multiple readers. However, the
deadlock may occur if we grab write lock exactly between 2 read calls.
This is an example from official docs:
https://doc.rust-lang.org/std/sync/struct.RwLock.html

When I reduced block time to 0.6s and further, it did happen to me -
between subsequent calls inside `get_epoch_config`,
`add_validator_proposals` was also called.

## Patch
### chain/epoch-manager/src/adapter.rs
```diff
@@ -675,7 +675,7 @@ impl EpochManagerAdapter for EpochManagerHandle {
 
     fn get_epoch_config(&self, epoch_id: &EpochId) -> Result<EpochConfig, EpochError> {
         let epoch_manager = self.read();
-        let protocol_version = self.get_epoch_info(epoch_id)?.protocol_version();
+        let protocol_version = epoch_manager.get_epoch_info(epoch_id)?.protocol_version();
         Ok(epoch_manager.get_epoch_config(protocol_version))
     }
 
@@ -691,7 +691,7 @@ impl EpochManagerAdapter for EpochManagerHandle {
 
     fn get_shard_config(&self, epoch_id: &EpochId) -> Result<ShardConfig, EpochError> {
         let epoch_manager = self.read();
-        let protocol_version = self.get_epoch_info(epoch_id)?.protocol_version();
+        let protocol_version = epoch_manager.get_epoch_info(epoch_id)?.protocol_version();
         let epoch_config = epoch_manager.get_epoch_config(protocol_version);
         Ok(ShardConfig::new(epoch_config))
     }
```
