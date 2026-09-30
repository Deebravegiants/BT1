# [?] fix: don't panic on already installed crypto provider

## Summary
Severity: Unknown
Chain: Fedimint
Component: fedimint/fedimint
Published: 2025-07-03
Source: https://github.com/fedimint/fedimint/commit/cff07b236080f05a018b9671f13c6ab9347e4a6b
Type: security-commit

## Details
fix: don't panic on already installed crypto provider

## Patch
### fedimint-api-client/src/api/mod.rs
```diff
@@ -61,7 +61,6 @@ use jsonrpsee_ws_client::{CustomCertStore, HeaderMap, HeaderValue};
 use jsonrpsee_ws_client::{WsClient, WsClientBuilder};
 use serde::{Deserialize, Serialize};
 use serde_json::Value;
-use tokio::sync::OnceCell;
 #[cfg(not(target_family = "wasm"))]
 use tokio_rustls::rustls::RootCertStore;
 #[cfg(all(feature = "tor", not(target_family = "wasm")))]
@@ -82,17 +81,9 @@ pub type SerdeOutputOutcome = SerdeModuleEncoding<DynOutputOutcome>;
 
 pub type OutputOutcomeResult<O> = result::Result<O, OutputOutcomeError>;
 
-static INSTALL_CRYPTO: OnceCell<()> = OnceCell::const_new();
-
 #[cfg(not(target_family = "wasm"))]
-async fn install_crypto_provider() {
-    INSTALL_CRYPTO
-        .get_or_init(|| async {
-            tokio_rustls::rustls::crypto::ring::default_provider()
-                .install_default()
-                .expect("Failed to install crypto");
-        })
-        .await;
+fn install_crypto_provider() {
+    let _ = tokio_rustls::rustls::crypto::ring::default_provider().install_default();
 }
 
 /// Set of api versions for each component (core + modules)
@@ -691,7 +682,7 @@ impl IClientConnector for WebsocketConnector {
 
         #[cfg(not(target_family = "wasm"))]
         let mut client = {
-            install_crypto_provider().await;
+            install_crypto_provider();
             let webpki_roots = webpki_roots::TLS_SERVER_ROOTS.iter().cloned();
             let mut root_certs = RootCertStore::empty();
             root_certs.extend(webpki_roots);
@@ -781,7 +772,7 @@ impl IClientConnector for TorConnector {
             .get(&peer_id)
             .ok_or_else(|| PeerError::InternalClientError(anyhow!("Invalid peer_id: {peer_id}")))?;
 
-        install_crypto_provider().await;
+        install_crypto_provider();
 
         let tor_config = TorClientConfig::default();
         let tor_client = TorClient::create_bootstrapped(tor_config)
```
