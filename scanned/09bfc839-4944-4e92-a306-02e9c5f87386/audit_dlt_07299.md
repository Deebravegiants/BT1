# [?] fix: fix logical deadlock in the network  (#7318)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2022-08-16
Source: https://github.com/near/nearcore/commit/7f17a2bc9eb02ccafad3349d7164fb4cd36624b9
Type: security-commit

## Details
fix: fix logical deadlock in the network  (#7318)

We should send ChainInfo to net whenever it changes, but we've missed
one case: at the startup, theres' a change due to us getting the initial
info. If we don't do that, we can't start block processing, so the info
is never updated. So, let's just send the info on startup.

There's a python tests which uncovered this bug:

   $ python3 tests/sanity/block_sync_archival.py


While fixing this, I've also noticed a bug in the epoch manager, which failed to report validators for genesis block, so that is fixed as well. 

best reviewed per commit.

## Patch
### chain/client/src/client.rs
```diff
@@ -2032,7 +2032,7 @@ impl Client {
     /// send_network_chain_info() call site would be ugly (we just log the error).
     /// In theory we should already have the tip at the call-site, eg from
     /// check_And_update_doomslug_tip, but that would require a bigger refactor.
-    fn send_network_chain_info(&mut self) -> Result<(), Error> {
+    pub(crate) fn send_network_chain_info(&mut self) -> Result<(), Error> {
         let tip = self.chain.head()?;
         // convert config tracked shards
         // runtime will track all shards if config tracked shards is not empty
```

### chain/client/src/client_actor.rs
```diff
@@ -250,6 +250,8 @@ impl Actor for ClientActor {
 
         // Start catchup job.
         self.catchup(ctx);
+
+        self.client.send_network_chain_info().unwrap();
     }
 }
 
```
