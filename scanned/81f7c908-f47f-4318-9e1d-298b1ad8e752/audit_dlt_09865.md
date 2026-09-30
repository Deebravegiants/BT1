# [?] fix(iota-rosetta): fix panic when setting usize::MAX max_concurrent_requests (#5258)

## Summary
Severity: Unknown
Chain: IOTA
Component: iotaledger/iota
Published: 2025-02-07
Source: https://github.com/iotaledger/iota/commit/0bf7a7627fe7ab701c86948c7e27929321547d31
Type: security-commit

## Details
fix(iota-rosetta): fix panic when setting usize::MAX max_concurrent_requests (#5258)

## Patch
### Cargo.lock
```diff
@@ -1876,7 +1876,7 @@ dependencies = [
  "bitflags 2.6.0",
  "cexpr",
  "clang-sys",
- "itertools 0.12.1",
+ "itertools 0.10.5",
  "lazy_static",
  "lazycell",
  "log",
@@ -8648,9 +8648,9 @@ dependencies = [
 
 [[package]]
 name = "jsonrpsee"
-version = "0.24.5"
+version = "0.24.8"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "126b48a5acc3c52fbd5381a77898cb60e145123179588a29e7ac48f9c06e401b"
+checksum = "834af00800e962dee8f7bfc0f60601de215e73e78e5497d733a2919da837d3c8"
 dependencies = [
  "jsonrpsee-client-transport",
  "jsonrpsee-core",
@@ -8666,9 +8666,9 @@ dependencies = [
 
 [[package]]
 name = "jsonrpsee-client-transport"
-version = "0.24.5"
+version = "0.24.8"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "bf679a8e0e083c77997f7c4bb4ca826577105906027ae462aac70ff348d02c6a"
+checksum = "def0fd41e2f53118bd1620478d12305b2c75feef57ea1f93ef70568c98081b7e"
 dependencies = [
  "base64 0.22.1",
  "futures-channel",
@@ -8691,9 +8691,9 @@ dependencies = [
 
 [[package]]
 name = "jsonrpsee-core"
-version = "0.24.5"
+version = "0.24.8"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "b0e503369a76e195b65af35058add0e6900b794a4e9a9316900ddd3a87a80477"
+checksum = "76637f6294b04e747d68e69336ef839a3493ca62b35bf488ead525f7da75c5bb"
 dependencies = [
  "async-trait",
  "bytes",
@@ -8718,9 +8718,9 @@ dependencies = [
 
 [[package]]
 name = "jsonrpsee-http-client"
-version = "0.24.5"
+version = "0.24.8"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "f2c0caba4a6a8efbafeec9baa986aa22a75a96c29d3e4b0091b0098d6470efb5"
+checksum = "87c24e981ad17798bbca852b0738bfb7b94816ed687bd0d5da60bfa35fa0fdc3"
 dependencies = [
  "async-trait",
  "base64 0.22.1",
@@ -8743,9 +8743,9 @@ dependencies = [
 
 [[package]]
 name = "jsonrpsee-proc-macros"
-version = "0.24.5"
+version = "0.24.8"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "fc660a9389e2748e794a40673a4155d501f32db667757cdb80edeff0306b489b"
+checksum = "6fcae0c6c159e11541080f1f829873d8f374f81eda0abc67695a13fc8dc1a580"
 dependencies = [
  "heck 0.5.0",
  "proc-macro-crate 3.2.0",
@@ -8756,9 +8756,9 @@ dependencies = [
 
 [[package]]
 name = "jsonrpsee-server"
-version = "0.24.5"
+version = "0.24.8"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "af6e6c9b6d975edcb443565d648b605f3e85a04ec63aa6941811a8894cc9cded"
+checksum = "66b7a3df90a1a60c3ed68e7ca63916b53e9afa928e33531e87f61a9c8e9ae87b"
 dependencies = [
  "futures-util",
  "http 1.1.0",
@@ -8783,9 +8783,9 @@ dependencies = [
 
 [[package]]
 name = "jsonrpsee-types"
-version = "0.24.5"
+version = "0.24.8"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "d8fb16314327cbc94fdf7965ef7e4422509cd5597f76d137bd104eb34aeede67"
+checksum = "ddb81adb1a5ae9182df379e374a79e24e992334e7346af4d065ae5b2acb8d4c6"
 dependencies = [
  "http 1.1.0",
  "serde",
@@ -8795,9 +8795,9 @@ dependencies = [
 
 [[package]]
 name = "jsonrpsee-wasm-client"
-version = "0.24.5"
+version = "0.24.8"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "e0da62b43702bd5640ea305d35df95da30abc878e79a7b4b01feda3beaf35d3c"
+checksum = "42e41af42ca39657313748174d02766e5287d3a57356f16756dbd8065b933977"
 dependencies = [
  "jsonrpsee-client-transport",
  "jsonrpsee-core",
@@ -8806,9 +8806,9 @@ dependencies = [
 
 [[package]]
 name = "jsonrpsee-ws-client"
-version = "0.24.5"
+version = "0.24.8"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "39aabf5d6c6f22da8d5b808eea1fab0736059f11fb42f71f141b14f404e5046a"
+checksum = "6f4f3642a292f5b76d8a16af5c88c16a0860f2ccc778104e5c848b28183d9538"
 dependencies = [
  "http 1.1.0",
  "jsonrpsee-client-transport",
@@ -9042,7 +9042,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "4979f22fdb869068da03c9f7528f8297c6fd2606bc3a4affe42e6a823fdb8da4"
 dependencies = [
  "cfg-if",
- "windows-targets 0.52.6",
+ "windows-targets 0.48.5",
 ]
 
 [[package]]
@@ -10586,7 +10586,7 @@ version = "0.7.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "af1844ef2428cc3e1cb900be36181049ef3d3193c63e43026cfe202983b27a56"
 dependencies = [
- "proc-macro-crate 3.2.0",
+ "proc-macro-crate 1.3.1",
  "proc-macro2",
  "quote",
  "syn 2.0.96",
@@ -11945,7 +11945,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "0c1318b19085f08681016926435853bbf7858f9c082d0999b80550ff5d9abe15"
 dependencies = [
  "bytes",
- "heck 0.5.0",
+ "heck 0.4.1",
  "itertools 0.13.0",
  "log",
  "multimap",
@@ -13905,7 +13905,7 @@ version = "0.8.5"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "03c3c6b7927ffe7ecaa769ee0e3994da3b8cafc8f444578982c83ecb161af917"
 dependencies = [
- "heck 0.5.0",
+ "heck 0.4.1",
  "proc-macro2",
  "quote",
  "syn 2.0.96",
@@ -15448,7 +15448,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "97fee6b57c6a41524a810daee9286c02d7752c4253064d0b05472833a438f675"
 dependencies = [
  "cfg-if",
- "rand 0.8.5",
+ "rand 0.7.3",
  "static_assertions",
 ]
 
@@ -16008,7 +16008,7 @@ version = "0.1.9"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "cf221c93e13a30d793f7645a0e7762c55d169dbb0a49671918a2319d289b10bb"
 dependencies = [
- "windows-sys 0.59.0",
+ "windows-sys 0.48.0",
 ]
 
 [[package]]
```

### crates/iota-rosetta/src/main.rs
```diff
@@ -193,11 +193,7 @@ impl RosettaServerCommand {
 
 async fn wait_for_iota_client(rpc_address: String) -> IotaClient {
     loop {
-        match IotaClientBuilder::default()
-            .max_concurrent_requests(usize::MAX)
-            .build(&rpc_address)
-            .await
-        {
+        match IotaClientBuilder::default().build(&rpc_address).await {
             Ok(client) => return client,
             Err(e) => {
                 warn!(
```

### crates/iota-sdk/src/lib.rs
```diff
@@ -149,7 +149,7 @@ pub const IOTA_MAINNET_URL: &str = "https://api.mainnet.iota.cafe";
 /// ```
 pub struct IotaClientBuilder {
     request_timeout: Duration,
-    max_concurrent_requests: usize,
+    max_concurrent_requests: Option<usize>,
     ws_url: Option<String>,
     ws_ping_interval: Option<Duration>,
     basic_auth: Option<(String, String)>,
@@ -159,7 +159,7 @@ impl Default for IotaClientBuilder {
     fn default() -> Self {
         Self {
             request_timeout: Duration::from_secs(60),
-            max_concurrent_requests: 256,
+            max_concurrent_requests: None,
             ws_url: None,
             ws_ping_interval: None,
             basic_auth: None,
@@ -176,7 +176,7 @@ impl IotaClientBuilder {
 
     /// Set the max concurrent requests allowed.
     pub fn max_concurrent_requests(mut self, max_concurrent_requests: usize) -> Self {
-        self.max_concurrent_requests = max_concurrent_requests;
+        self.max_concurrent_requests = Some(max_concurrent_requests);
         self
     }
 
@@ -247,24 +247,32 @@ impl IotaClientBuilder {
         let ws = if let Some(url) = self.ws_url {
             let mut builder = WsClientBuilder::default()
                 .max_request_size(2 << 30)
-                .max_concurrent_requests(self.max_concurrent_requests)
                 .set_headers(headers.clone())
                 .request_timeout(self.request_timeout);
 
             if let Some(duration) = self.ws_ping_interval {
                 builder = builder.enable_ws_ping(PingConfig::new().ping_interval(duration))
             }
 
+            if let Some(max_concurrent_requests) = self.max_concurrent_requests {
+                builder = builder.max_concurrent_requests(max_concurrent_requests);
+            }
+
             builder.build(url).await.ok()
         } else {
             None
         };
 
-        let http = HttpClientBuilder::default()
+        let mut http_builder = HttpClientBuilder::default()
             .max_request_size(2 << 30)
-            .set_headers(headers.clone())
-            .request_timeout(self.request_timeout)
-            .build(http)?;
+            .set_headers(headers)
+            .request_timeout(self.request_timeout);
+
+        if let Some(max_concurrent_requests) = self.max_concurrent_requests {
+            http_builder = http_builder.max_concurrent_requests(max_concurrent_requests);
+        }
+
+        let http = http_builder.build(http)?;
 
         let info = Self::get_server_info(&http, &ws).await?;
 
```
