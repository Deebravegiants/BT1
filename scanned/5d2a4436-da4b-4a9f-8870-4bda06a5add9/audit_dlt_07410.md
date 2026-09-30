# [?] fix(cli): add `--no-proxy` to disable `reqwest` proxying to prevent crash on macOS in sandboxed environments (#13155)

## Summary
Severity: Unknown
Chain: Tooling
Component: foundry-rs/foundry
Published: 2026-01-21
Source: https://github.com/foundry-rs/foundry/commit/6f27c7b548c8ed6ddb4a067d91ed5beb34f766d4
Type: security-commit

## Details
fix(cli): add `--no-proxy` to disable `reqwest` proxying to prevent crash on macOS in sandboxed environments (#13155)

* fix(common): prevent crash on macOS in sandboxed environments

Disable automatic system proxy detection when building reqwest HTTP
clients. On macOS, reqwest reads system proxy settings via
SCDynamicStore, which panics with 'Attempted to create a NULL object'
in sandboxed environments (e.g., Cursor IDE sandbox, App Sandbox, or
restricted shells).

Using no_proxy() disables the automatic usage of system proxies,
preventing the crash while maintaining HTTP functionality.

Note: This means system-level proxy settings (macOS System Preferences,
Windows Registry) are not automatically detected. Users who need proxy
support can configure it via environment variables or use --offline.

Fixes #12733

* fix(cli): add --no-proxy flag to prevent crash on macOS in sandboxed environments

Add a new --no-proxy CLI flag and eth_rpc_no_proxy config option to
disable automatic proxy detection. This helps users in sandboxed
environments (e.g., Cursor IDE sandbox, macOS App Sandbox) where
system proxy detection via SCDynamicStore causes crashes.

When enabled, HTTP_PROXY/HTTPS_PROXY environment variables and
system proxy settings will be ignored for RPC requests.

The flag is opt-in to preserve existing proxy functionality for
users who need it.

Fixes #12733

## Patch
### crates/cli/src/opts/rpc.rs
```diff
@@ -30,6 +30,14 @@ pub struct RpcOpts {
     #[arg(short = 'k', long = "insecure", default_value = "false")]
     pub accept_invalid_certs: bool,
 
+    /// Disable automatic proxy detection.
+    ///
+    /// Use this in sandboxed environments (e.g., Cursor IDE sandbox, macOS App Sandbox) where
+    /// system proxy detection causes crashes. When enabled, HTTP_PROXY/HTTPS_PROXY environment
+    /// variables and system proxy settings will be ignored.
+    #[arg(long = "no-proxy", alias = "disable-proxy", default_value = "false")]
+    pub no_proxy: bool,
+
     /// Use the Flashbots RPC URL with fast mode (<https://rpc.flashbots.net/fast>).
     ///
     /// This shares the transaction privately with all registered builders.
@@ -118,6 +126,9 @@ impl RpcOpts {
         if self.accept_invalid_certs {
             dict.insert("eth_rpc_accept_invalid_certs".into(), true.into());
         }
+        if self.no_proxy {
+            dict.insert("eth_rpc_no_proxy".into(), true.into());
+        }
         dict
     }
 
```

### crates/common/src/provider/mod.rs
```diff
@@ -100,6 +100,8 @@ pub struct ProviderBuilder {
     is_local: bool,
     /// Whether to accept invalid certificates.
     accept_invalid_certs: bool,
+    /// Whether to disable automatic proxy detection.
+    no_proxy: bool,
     /// Whether to output curl commands instead of making requests.
     curl_mode: bool,
 }
@@ -152,6 +154,7 @@ impl ProviderBuilder {
             headers: vec![],
             is_local,
             accept_invalid_certs: false,
+            no_proxy: false,
             curl_mode: false,
         }
     }
@@ -256,6 +259,15 @@ impl ProviderBuilder {
         self
     }
 
+    /// Sets whether to disable automatic proxy detection.
+    ///
+    /// This can help in sandboxed environments (e.g., Cursor IDE sandbox, macOS App Sandbox)
+    /// where system proxy detection via SCDynamicStore causes crashes.
+    pub fn no_proxy(mut self, no_proxy: bool) -> Self {
+        self.no_proxy = no_proxy;
+        self
+    }
+
     /// Sets whether to output curl commands instead of making requests.
     ///
     /// When enabled, the provider will print equivalent curl commands to stdout
@@ -278,6 +290,7 @@ impl ProviderBuilder {
             headers,
             is_local,
             accept_invalid_certs,
+            no_proxy,
             curl_mode,
         } = self;
         let url = url?;
@@ -301,6 +314,7 @@ impl ProviderBuilder {
             .with_headers(headers)
             .with_jwt(jwt)
             .accept_invalid_certs(accept_invalid_certs)
+            .no_proxy(no_proxy)
             .build();
         let client = ClientBuilder::default().layer(retry_layer).transport(transport, is_local);
 
@@ -335,6 +349,7 @@ impl ProviderBuilder {
             headers,
             is_local,
             accept_invalid_certs,
+            no_proxy,
             curl_mode,
         } = self;
         let url = url?;
@@ -360,6 +375,7 @@ impl ProviderBuilder {
             .with_headers(headers)
             .with_jwt(jwt)
             .accept_invalid_certs(accept_invalid_certs)
+            .no_proxy(no_proxy)
             .build();
 
         let client = ClientBuilder::default().layer(retry_layer).transport(transport, is_local);
```

### crates/common/src/provider/runtime_transport.rs
```diff
@@ -80,6 +80,8 @@ pub struct RuntimeTransport {
     timeout: std::time::Duration,
     /// Whether to accept invalid certificates.
     accept_invalid_certs: bool,
+    /// Whether to disable automatic proxy detection.
+    no_proxy: bool,
 }
 
 /// A builder for [RuntimeTransport].
@@ -90,6 +92,7 @@ pub struct RuntimeTransportBuilder {
     jwt: Option<String>,
     timeout: std::time::Duration,
     accept_invalid_certs: bool,
+    no_proxy: bool,
 }
 
 impl RuntimeTransportBuilder {
@@ -101,6 +104,7 @@ impl RuntimeTransportBuilder {
             jwt: None,
             timeout: REQUEST_TIMEOUT,
             accept_invalid_certs: false,
+            no_proxy: false,
         }
     }
 
@@ -128,6 +132,15 @@ impl RuntimeTransportBuilder {
         self
     }
 
+    /// Set whether to disable automatic proxy detection.
+    ///
+    /// This can help in sandboxed environments (e.g., Cursor IDE sandbox, macOS App Sandbox)
+    /// where system proxy detection via SCDynamicStore causes crashes.
+    pub fn no_proxy(mut self, no_proxy: bool) -> Self {
+        self.no_proxy = no_proxy;
+        self
+    }
+
     /// Builds the [RuntimeTransport] and returns it in a disconnected state.
     /// The runtime transport will then connect when the first request happens.
     pub fn build(self) -> RuntimeTransport {
@@ -138,6 +151,7 @@ impl RuntimeTransportBuilder {
             jwt: self.jwt,
             timeout: self.timeout,
             accept_invalid_certs: self.accept_invalid_certs,
+            no_proxy: self.no_proxy,
         }
     }
 }
@@ -165,6 +179,14 @@ impl RuntimeTransport {
             .timeout(self.timeout)
             .tls_built_in_root_certs(self.url.scheme() == "https")
             .danger_accept_invalid_certs(self.accept_invalid_certs);
+
+        // Disable automatic proxy detection if requested. This helps in sandboxed environments
+        // (e.g., Cursor IDE sandbox, macOS App Sandbox) where system proxy detection via
+        // SCDynamicStore causes crashes. See: https://github.com/foundry-rs/foundry/issues/12733
+        if self.no_proxy {
+            client_builder = client_builder.no_proxy();
+        }
+
         let mut headers = reqwest::header::HeaderMap::new();
 
         // If there's a JWT, add it to the headers if we can decode it.
```

### crates/config/src/lib.rs
```diff
@@ -286,6 +286,11 @@ pub struct Config {
     pub eth_rpc_url: Option<String>,
     /// Whether to accept invalid certificates for the rpc server.
     pub eth_rpc_accept_invalid_certs: bool,
+    /// Whether to disable automatic proxy detection for the rpc server.
+    ///
+    /// This can help in sandboxed environments (e.g., Cursor IDE sandbox, macOS App Sandbox)
+    /// where system proxy detection via SCDynamicStore causes crashes.
+    pub eth_rpc_no_proxy: bool,
     /// JWT secret that should be used for any rpc calls
     pub eth_rpc_jwt: Option<String>,
     /// Timeout that should be used for any rpc calls
@@ -2587,6 +2592,7 @@ impl Default for Config {
             memory_limit: 1 << 27, // 2**27 = 128MiB = 134_217_728 bytes
             eth_rpc_url: None,
             eth_rpc_accept_invalid_certs: false,
+            eth_rpc_no_proxy: false,
             eth_rpc_jwt: None,
             eth_rpc_timeout: None,
             eth_rpc_headers: None,
```

### crates/forge/tests/cli/config.rs
```diff
@@ -59,6 +59,7 @@ optimizer = false
 optimizer_runs = 200
 verbosity = 0
 eth_rpc_accept_invalid_certs = false
+eth_rpc_no_proxy = false
 ignored_error_codes = [
     "license",
     "code-size",
@@ -310,6 +311,7 @@ forgetest!(can_extract_config_values, |prj, cmd| {
         memory_limit: 1 << 27,
         eth_rpc_url: Some("localhost".to_string()),
         eth_rpc_accept_invalid_certs: false,
+        eth_rpc_no_proxy: false,
         eth_rpc_jwt: None,
         eth_rpc_timeout: None,
         eth_rpc_headers: None,
@@ -1215,6 +1217,7 @@ forgetest_init!(test_default_config, |prj, cmd| {
   "verbosity": 0,
   "eth_rpc_url": null,
   "eth_rpc_accept_invalid_certs": false,
+  "eth_rpc_no_proxy": false,
   "eth_rpc_jwt": null,
   "eth_rpc_timeout": null,
   "eth_rpc_headers": null,
```
