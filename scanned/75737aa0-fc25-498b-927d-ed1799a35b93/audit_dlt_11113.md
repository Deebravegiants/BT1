# [?] Fix server server panic

## Summary
Severity: Unknown
Chain: zkSync Lite
Component: matter-labs/zksync
Published: 2022-03-25
Source: https://github.com/matter-labs/zksync/commit/c629aa8eb836381d703d772fea071734a74f9211
Type: security-commit

## Details
Fix server server panic

Signed-off-by: deniallugo <deniallugo@gmail.com>

## Patch
### core/bin/server/src/main.rs
```diff
@@ -259,15 +259,15 @@ async fn run_server(components: &ComponentsToRun) {
                 chain_config.state_keeper.block_chunk_sizes,
             ));
             let private_config = PrivateApiConfig::from_env();
-            zksync_api::api_server::rest::start_server_thread_detached(
+            tasks.push(zksync_api::api_server::rest::start_server_thread_detached(
                 read_only_connection_pool.clone(),
                 RestApiConfig::from_env().bind_addr(),
                 contracts_config.contract_addr,
                 ticker,
                 sign_check_sender,
                 mempool_tx_request_sender,
                 private_config.url,
-            );
+            ));
         }
     }
 
```

### core/bin/zksync_api/src/api_server/rest/mod.rs
```diff
@@ -98,9 +98,8 @@ pub fn start_server_thread_detached(
     std::thread::Builder::new()
         .name("actix-rest-api".to_string())
         .spawn(move || {
-            let _panic_sentinel = ThreadPanicNotify(panic_sender.clone());
-
             actix_rt::System::new().block_on(async move {
+                let _panic_sentinel = ThreadPanicNotify(panic_sender.clone());
                 // TODO remove this config ZKS-815
                 let config = ZkSyncConfig::from_env();
 
```
