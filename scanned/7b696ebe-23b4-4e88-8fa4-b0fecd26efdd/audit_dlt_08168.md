# [?] fix(rpc): reject oversized max_response_body_size without panicking (#11259)

## Summary
Severity: Unknown
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2026-08-14
Source: https://github.com/ZcashFoundation/zebra/commit/e7ac22c60b8743a556ea4ca8d7c59df9f19e0dbd
Type: security-commit

## Details
fix(rpc): reject oversized max_response_body_size without panicking (#11259)

## Patch
### .changes/unreleased/zebra-rpc-breaking-20260814-213822.yaml
```diff
@@ -0,0 +1,4 @@
+project: zebra-rpc
+kind: breaking
+body: '`config::Config::max_response_body_size` now has type `u32` instead of `usize`. Convert existing `usize` values before assigning them ([#11259](https://github.com/ZcashFoundation/zebra/pull/11259)).'
+time: 2026-08-14T21:38:22.479052949Z
```

### .changes/unreleased/zebrad-breaking-20260814-213814.yaml
```diff
@@ -0,0 +1,4 @@
+project: zebrad
+kind: breaking
+body: '`rpc.max_response_body_size` is now limited to 4,294,967,295 bytes. Configurations with larger values must reduce the limit; they are rejected during configuration loading instead of causing an RPC server startup panic ([#11259](https://github.com/ZcashFoundation/zebra/pull/11259)).'
+time: 2026-08-14T21:38:14.567244223Z
```

### zebra-rpc/src/config/rpc.rs
```diff
@@ -67,7 +67,7 @@ pub struct Config {
     pub enable_cookie_auth: bool,
 
     /// The maximum size of the response body in bytes.
-    pub max_response_body_size: usize,
+    pub max_response_body_size: u32,
 }
 
 // This impl isn't derivable because it depends on features.
```

### zebra-rpc/src/server.rs
```diff
@@ -123,7 +123,6 @@ impl RpcServer {
         // The largest RPC request is submitblock, which sends a full block
         // as a hex string (2x MAX_BLOCK_BYTES) plus a small JSON-RPC wrapper.
         let max_request_body_size = (MAX_BLOCK_BYTES as usize) * 2 + 1024;
-
         let http_middleware_layer = if conf.enable_cookie_auth {
             let cookie = Cookie::default();
             cookie::write_to_disk(&cookie, &conf.cookie_dir)
@@ -145,11 +144,7 @@ impl RpcServer {
             .http_only()
             .set_http_middleware(http_middleware)
             .set_rpc_middleware(rpc_middleware)
-            .max_response_body_size(
-                conf.max_response_body_size
-                    .try_into()
-                    .expect("should be valid"),
-            )
+            .max_response_body_size(conf.max_response_body_size)
             .build(listen_addr)
             .await?;
 
```

### zebrad/tests/unit/config.rs
```diff
@@ -819,6 +819,28 @@ network = "Testnet"
     ZebradConfig::load(Some(config_path)).expect_err("Should fail to load invalid TOML");
 }
 
+#[test]
+fn config_oversized_rpc_max_response_body_size_errors() {
+    let _env = EnvGuard::new();
+
+    let temp_dir = TempDir::new().expect("create temp dir");
+    let config_path = temp_dir.path().join("oversized_rpc_config.toml");
+
+    let invalid_config = r#"
+[rpc]
+max_response_body_size = 4294967296
+"#;
+
+    fs::write(&config_path, invalid_config).expect("write oversized RPC config");
+
+    let error = ZebradConfig::load(Some(config_path))
+        .expect_err("Should fail to load oversized RPC max response body size");
+
+    let error = error.to_string();
+    assert!(error.contains("max_response_body_size"));
+    assert!(error.contains("4294967296"));
+}
+
 #[test]
 fn config_invalid_env_values_error() {
     let env = EnvGuard::new();
```
