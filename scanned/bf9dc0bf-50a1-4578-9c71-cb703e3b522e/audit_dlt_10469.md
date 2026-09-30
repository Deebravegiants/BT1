# [?] fix(rpc): reject oversized max_response_body_size without panicking

## Summary
Severity: Unknown
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2026-08-13
Source: https://github.com/ZcashFoundation/zebra/commit/436b508b06e75a540d1b0b2c5ad4eac1ae54d9f3
Type: security-commit

## Details
fix(rpc): reject oversized max_response_body_size without panicking

## Patch
### zebra-rpc/CHANGELOG.md
```diff
@@ -5,6 +5,11 @@ All notable changes to this project are documented in this file.
 The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
 and this project adheres to [Semantic Versioning](https://semver.org).
 
+### Fixed
+
+- RPC server startup now returns an error instead of panicking when
+  `rpc.max_response_body_size` is larger than jsonrpsee supports.
+
 ## [16.0.0] - 2026-08-10
 
 ### Breaking Changes
```

### zebra-rpc/src/server.rs
```diff
@@ -123,6 +123,16 @@ impl RpcServer {
         // The largest RPC request is submitblock, which sends a full block
         // as a hex string (2x MAX_BLOCK_BYTES) plus a small JSON-RPC wrapper.
         let max_request_body_size = (MAX_BLOCK_BYTES as usize) * 2 + 1024;
+        let max_response_body_size = conf.max_response_body_size.try_into().map_err(|_| {
+            std::io::Error::new(
+                std::io::ErrorKind::InvalidInput,
+                format!(
+                    "rpc.max_response_body_size {} exceeds the maximum supported value {}",
+                    conf.max_response_body_size,
+                    u32::MAX,
+                ),
+            )
+        })?;
 
         let http_middleware_layer = if conf.enable_cookie_auth {
             let cookie = Cookie::default();
@@ -145,11 +155,7 @@ impl RpcServer {
             .http_only()
             .set_http_middleware(http_middleware)
             .set_rpc_middleware(rpc_middleware)
-            .max_response_body_size(
-                conf.max_response_body_size
-                    .try_into()
-                    .expect("should be valid"),
-            )
+            .max_response_body_size(max_response_body_size)
             .build(listen_addr)
             .await?;
 
```

### zebra-rpc/src/server/tests/vectors.rs
```diff
@@ -89,6 +89,57 @@ async fn rpc_server_spawn_unallocated_port_shutdown() {
     rpc_spawn_unallocated_port(true).await
 }
 
+/// Test that the RPC server returns an error when the configured max response body size
+/// is larger than the jsonrpsee server supports.
+#[tokio::test]
+#[cfg(target_pointer_width = "64")]
+async fn rpc_server_rejects_oversized_max_response_body_size() {
+    let _init_guard = zebra_test::init();
+
+    let conf = Config {
+        listen_addr: Some(SocketAddrV4::new(Ipv4Addr::LOCALHOST, 0).into()),
+        indexer_listen_addr: None,
+        parallel_cpu_threads: 0,
+        debug_force_finished_sync: false,
+        cookie_dir: Default::default(),
+        enable_cookie_auth: false,
+        max_response_body_size: u32::MAX as usize + 1,
+    };
+
+    let mempool: MockService<_, _, _, BoxError> = MockService::build().for_unit_tests();
+    let state: MockService<_, _, _, BoxError> = MockService::build().for_unit_tests();
+    let read_state: MockService<_, _, _, BoxError> = MockService::build().for_unit_tests();
+    let block_verifier_router: MockService<_, _, _, BoxError> =
+        MockService::build().for_unit_tests();
+
+    let (_tx, rx) = watch::channel(None);
+    let (rpc_impl, _) = RpcImpl::new(
+        Mainnet,
+        Default::default(),
+        false,
+        "RPC test",
+        "RPC test",
+        Buffer::new(mempool, 1),
+        Buffer::new(state, 1),
+        Buffer::new(read_state, 1),
+        Buffer::new(block_verifier_router, 1),
+        MockSyncStatus::default(),
+        NoChainTip,
+        MockAddressBookPeers::default(),
+        rx,
+        None,
+    );
+
+    let err = RpcServer::start(rpc_impl, conf)
+        .await
+        .expect_err("oversized max response body size should return an error");
+
+    let err = err.to_string();
+    assert!(err.contains("rpc.max_response_body_size"));
+    assert!(err.contains("4294967296"));
+    assert!(err.contains("4294967295"));
+}
+
 /// Test if the RPC server will spawn on an OS-assigned unallocated port.
 ///
 /// Set `do_shutdown` to true to close the server using the close handle.
```
