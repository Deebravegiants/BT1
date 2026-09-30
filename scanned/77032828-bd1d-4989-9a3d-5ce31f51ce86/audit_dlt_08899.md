# [?] fix(gateway-client): don't panic on resolver errors

## Summary
Severity: Unknown
Chain: Starknet
Component: software-mansion/pathfinder
Published: 2026-02-27
Source: https://github.com/software-mansion/pathfinder/commit/ab30c323d59460321793f95d1c550fcfb3733637
Type: security-commit

## Details
fix(gateway-client): don't panic on resolver errors

## Patch
### crates/gateway-client/src/lib.rs
```diff
@@ -4,6 +4,7 @@ use std::result::Result;
 use std::sync::{Arc, RwLock};
 use std::time::Duration;
 
+use anyhow::Context;
 use pathfinder_common::prelude::*;
 use reqwest::Url;
 use starknet_gateway_types::error::SequencerError;
@@ -330,8 +331,10 @@ impl Client {
     pub fn with_urls(gateway: Url, feeder_gateway: Url, timeout: Duration) -> anyhow::Result<Self> {
         metrics::register();
 
-        let (resolved_gateway_addresses, resolved_feeder_gateway_addresses) =
-            (resolve_hosts(&gateway), resolve_hosts(&feeder_gateway));
+        let resolved_gateway_addresses =
+            resolve_hosts(&gateway).context("Resolving gateway URL")?;
+        let resolved_feeder_gateway_addresses =
+            resolve_hosts(&feeder_gateway).context("Resolving feeder gateway URL")?;
 
         Ok(Self {
             inner: std::sync::Arc::new(std::sync::RwLock::new(
@@ -354,19 +357,25 @@ impl Client {
         })
     }
 
+    /// Resolve the gateway and feeder gateway URLs and refresh the HTTP client
+    /// if the resolved addresses have changed.
+    ///
     /// Replaces the underlying `reqwest` HTTP client with a freshly built one,
     /// using the same timeout and settings as the original. Because all
     /// [Clone]s of this [Client] share the same [`std::sync::Arc`], the new
     /// connection pool becomes visible to every holder immediately.
     ///
-    /// Intended to be called periodically to enforce a maximum keep-alive age
-    /// on the underlying connection pool.
+    /// Intended to be called periodically to enforce reconnection to the
+    /// gateway and feeder gateway if their IP addresses change due to DNS
+    /// updates, without needing to restart the entire application.
     pub fn refresh(&self) -> anyhow::Result<()> {
         // Resolve the gateway URLs to detect any DNS changes. If the resolved addresses
         // have changed, we refresh the HTTP client to ensure that new connections are
         // made to the correct addresses.
-        let new_resolved_gateway_addresses = resolve_hosts(&self.gateway);
-        let new_resolved_feeder_gateway_addresses = resolve_hosts(&self.feeder_gateway);
+        let new_resolved_gateway_addresses =
+            resolve_hosts(&self.gateway).context("Resolving gateway URL")?;
+        let new_resolved_feeder_gateway_addresses =
+            resolve_hosts(&self.feeder_gateway).context("Resolving feeder gateway URL")?;
 
         tracing::trace!(
             ?new_resolved_feeder_gateway_addresses,
@@ -450,12 +459,14 @@ impl Client {
 }
 
 /// Resolve the URL to addresses.
-fn resolve_hosts(url: &Url) -> Vec<std::net::IpAddr> {
-    url.socket_addrs(|| None)
-        .expect("failed to resolve gateway URL")
+fn resolve_hosts(url: &Url) -> anyhow::Result<Vec<std::net::IpAddr>> {
+    let addresses = url
+        .socket_addrs(|| None)
+        .context("Resolving host name in URL")?
         .into_iter()
         .map(|socket_addr| socket_addr.ip())
-        .collect()
+        .collect();
+    Ok(addresses)
 }
 
 #[async_trait::async_trait]
```
