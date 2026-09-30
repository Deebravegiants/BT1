# [?] sui-rosetta: fix panic when setting usize::MAX max_concurrent_requests

## Summary
Severity: Unknown
Chain: Sui
Component: MystenLabs/sui
Published: 2025-01-22
Source: https://github.com/MystenLabs/sui/commit/46f235e8637cb271b84cc2af849f6af13e92a605
Type: security-commit

## Details
sui-rosetta: fix panic when setting usize::MAX max_concurrent_requests

This fixes a panic that was seen when rosetta constructs a jsonrpc
client with max_concurrent_requests of usize::MAX by changing how client
construction happens to have the default be to disable any limit in
concurrent requests (which is essentially what rosetta was trying to
do).

## Patch
### crates/sui-rosetta/src/main.rs
```diff
@@ -186,11 +186,7 @@ impl RosettaServerCommand {
 
 async fn wait_for_sui_client(rpc_address: String) -> SuiClient {
     loop {
-        match SuiClientBuilder::default()
-            .max_concurrent_requests(usize::MAX)
-            .build(&rpc_address)
-            .await
-        {
+        match SuiClientBuilder::default().build(&rpc_address).await {
             Ok(client) => return client,
             Err(e) => {
                 warn!("Error connecting to Sui RPC server [{rpc_address}]: {e}, retrying in 5 seconds.");
```

### crates/sui-sdk/src/lib.rs
```diff
@@ -139,7 +139,7 @@ pub const SUI_MAINNET_URL: &str = "https://fullnode.mainnet.sui.io:443";
 /// ```
 pub struct SuiClientBuilder {
     request_timeout: Duration,
-    max_concurrent_requests: usize,
+    max_concurrent_requests: Option<usize>,
     ws_url: Option<String>,
     ws_ping_interval: Option<Duration>,
     basic_auth: Option<(String, String)>,
@@ -149,7 +149,7 @@ impl Default for SuiClientBuilder {
     fn default() -> Self {
         Self {
             request_timeout: Duration::from_secs(60),
-            max_concurrent_requests: 256,
+            max_concurrent_requests: None,
             ws_url: None,
             ws_ping_interval: None,
             basic_auth: None,
@@ -166,7 +166,7 @@ impl SuiClientBuilder {
 
     /// Set the max concurrent requests allowed
     pub fn max_concurrent_requests(mut self, max_concurrent_requests: usize) -> Self {
-        self.max_concurrent_requests = max_concurrent_requests;
+        self.max_concurrent_requests = Some(max_concurrent_requests);
         self
     }
 
@@ -232,7 +232,6 @@ impl SuiClientBuilder {
         let ws = if let Some(url) = self.ws_url {
             let mut builder = WsClientBuilder::default()
                 .max_request_size(2 << 30)
-                .max_concurrent_requests(self.max_concurrent_requests)
                 .set_headers(headers.clone())
                 .request_timeout(self.request_timeout);
 
@@ -242,17 +241,25 @@ impl SuiClientBuilder {
                 );
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
-            .max_concurrent_requests(self.max_concurrent_requests)
             .set_headers(headers.clone())
-            .request_timeout(self.request_timeout)
-            .build(http)?;
+            .request_timeout(self.request_timeout);
+
+        if let Some(max_concurrent_requests) = self.max_concurrent_requests {
+            http_builder = http_builder.max_concurrent_requests(max_concurrent_requests);
+        }
+
+        let http = http_builder.build(http)?;
 
         let info = Self::get_server_info(&http, &ws).await?;
 
```
