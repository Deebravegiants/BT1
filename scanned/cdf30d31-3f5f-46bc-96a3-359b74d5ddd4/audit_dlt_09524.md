# [?] fix: health used errors not panics, and exit if errors/panics

## Summary
Severity: Unknown
Chain: Chainflip
Component: chainflip-io/chainflip-backend
Published: 2022-06-24
Source: https://github.com/chainflip-io/chainflip-backend/commit/59071c54d1ac3dd2a9db9c74b6f06d4263f3ad7c
Type: security-commit

## Details
fix: health used errors not panics, and exit if errors/panics

squash move

## Patch
### engine/src/health.rs
```diff
@@ -3,6 +3,7 @@
 //! Returns a HTTP 200 response to any request on {hostname}:{port}/health
 //! Method returns a Sender, allowing graceful termination of the infinite loop
 
+use anyhow::Context;
 use slog::o;
 use tokio::{
     io::{AsyncReadExt, AsyncWriteExt},
@@ -11,47 +12,33 @@ use tokio::{
 
 use crate::{logging::COMPONENT_KEY, settings};
 
-/// Configuration holder for the health server
-pub struct HealthMonitor {
-    bind_address: String,
-    logger: slog::Logger,
-}
+/// Start the health monitoring server
+pub fn start(
+    health_check_settings: &settings::HealthCheck,
+    logger: &slog::Logger,
+) -> impl futures::Future<Output = anyhow::Result<()>> + Send {
+    let bind_address = format!(
+        "{}:{}",
+        health_check_settings.hostname, health_check_settings.port
+    );
+    let logger =
+        logger.new(o!(COMPONENT_KEY => "health-check", "bind-address" => bind_address.clone()));
 
-impl HealthMonitor {
-    /// Instantiate a health monitoring server
-    pub fn new(health_check_settings: &settings::HealthCheck, logger: &slog::Logger) -> Self {
-        let bind_address = format!(
-            "{}:{}",
-            health_check_settings.hostname, health_check_settings.port
-        );
-        Self {
-            logger: logger
-                .new(o!(COMPONENT_KEY => "health-check", "bind-address" => bind_address.clone())),
-            bind_address,
-        }
-    }
+    slog::info!(logger, "Starting");
 
-    /// Start the health monitoring server
-    pub async fn run(&self) {
-        slog::info!(self.logger, "Starting");
-        let listener = TcpListener::bind(self.bind_address.clone())
+    async move {
+        let listener = TcpListener::bind(&bind_address)
             .await
-            .unwrap_or_else(|e| {
-                panic!(
-                    "Could not bind TCP listener to {}: {}",
-                    self.bind_address, e
-                )
-            });
+            .with_context(|| format!("Could not bind TCP listener to {}", bind_address))?;
 
-        let logger = self.logger.clone();
         loop {
             match listener.accept().await {
                 Ok((mut stream, _address)) => {
                     let mut buffer = [0; 1024];
                     stream
                         .read(&mut buffer)
                         .await
-                        .expect("Couldn't read stream into buffer");
+                        .context("Couldn't read stream into buffer")?;
 
                     let mut headers = [httparse::EMPTY_HEADER; 16];
                     let mut request = httparse::Request::new(&mut headers);
@@ -62,11 +49,11 @@ impl HealthMonitor {
                                 stream
                                     .write(http_200_response.as_bytes())
                                     .await
-                                    .expect("Could not write to health check stream");
+                                    .context("Could not write to health check stream")?;
                                 stream
                                     .flush()
                                     .await
-                                    .expect("Could not flush health check TCP stream");
+                                    .context("Could not flush health check TCP stream")?;
                             } else {
                                 slog::warn!(logger, "Requested health at invalid path: {:?}", request.path);
                             }
@@ -103,8 +90,7 @@ mod tests {
     async fn health_check_test() {
         let health_check = Settings::new_test().unwrap().health_check.unwrap();
         let logger = logging::test_utils::new_test_logger();
-        let health_monitor = HealthMonitor::new(&health_check, &logger);
-        health_monitor.run().await;
+        start(&health_check, &logger).await.unwrap();
 
         let request_test = |path: &'static str, expected_status: Option<reqwest::StatusCode>| {
             let health_check = health_check.clone();
```

### engine/src/main.rs
```diff
@@ -8,8 +8,7 @@ use chainflip_engine::{
         stake_manager::StakeManager,
         EthBroadcaster,
     },
-    health::HealthMonitor,
-    logging,
+    health, logging,
     multisig::{self, client::key_store::KeyStore, PersistentKeyDB},
     multisig_p2p,
     settings::{CommandLineOptions, Settings},
@@ -38,9 +37,7 @@ async fn main() {
     slog::info!(root_logger, "Start the engines! :broom: :broom: ");
 
     if let Some(health_check_settings) = &settings.health_check {
-        HealthMonitor::new(health_check_settings, &root_logger)
-            .run()
-            .await;
+        tokio::spawn(health::start(health_check_settings, &root_logger));
     }
 
     // Init web3 and eth broadcaster before connecting to SC, so we can diagnose these config errors, before
```
