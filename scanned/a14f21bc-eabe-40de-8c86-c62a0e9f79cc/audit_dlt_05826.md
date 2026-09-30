# [?] fix: Panic in mirror when cannot start indexing. (#14445)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2025-10-15
Source: https://github.com/near/nearcore/commit/6e70e39ca7ef972024c4f8dd159e76512d878a66
Type: security-commit

## Details
fix: Panic in mirror when cannot start indexing. (#14445)

If in `index_target_loop` we fail to start near node before we send
anything on `clients_tx` channel, `clients_tx` will be dropped which
would `clients_rx` panic with `RecvError` waiting on channel here:
https://github.com/near/nearcore/blob/ac2a2439b15cefdabfbc1d3f2c2891a3cc416e38/tools/mirror/src/lib.rs#L2018

That's not very useful in case something goes wrong since no information
about the original panic would be available. Instead it's better to
panic when something goes wrong before we are able to send message over
`clients_tx`.

## Patch
### tools/mirror/src/lib.rs
```diff
@@ -1772,9 +1772,10 @@ impl<T: ChainAccess> TxMirror<T> {
             validate_genesis: false,
         };
         let near_config =
-            indexer_config.load_near_config().context("failed to load near config")?;
+            indexer_config.load_near_config().context("failed to load near config").unwrap();
         let near_node = Indexer::start_near_node(&indexer_config, near_config.clone())
-            .context("failed to start near node")?;
+            .context("failed to start near node")
+            .unwrap();
         let target_indexer = Indexer::from_near_node(indexer_config, near_config, &near_node);
         let mut target_stream = target_indexer.streamer();
         let NearNode { client, view_client, rpc_handler, .. } = near_node;
@@ -1786,7 +1787,8 @@ impl<T: ChainAccess> TxMirror<T> {
             &view_client,
             &client,
         )
-        .await?;
+        .await
+        .unwrap();
         *target_height.write() = first_target_height;
         *target_head.write() = first_target_head;
         clients_tx
```
