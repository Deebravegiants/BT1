# [?] fix(tee-prover): mitigate panic on redeployments (#2764)

## Summary
Severity: Unknown
Chain: zkSync
Component: matter-labs/zksync-era
Published: 2024-09-02
Source: https://github.com/matter-labs/zksync-era/commit/178b38644f507c5f6d12ba862d0c699e87985dd7
Type: security-commit

## Details
fix(tee-prover): mitigate panic on redeployments (#2764)

## What ❔

We experienced `tee-prover` panic, likely due to the automatic
redeployment of the `proof-data-handler` in the `staging` environment.
We've been getting `503 Service Unavailable` errors for an extended
period when trying to reach
http://server-v2-proof-data-handler-internal.stage.matterlabs.corp/tee/proof_input,
which resulted in a panic after reaching the retry limit.

Relevant code causing the panic:

https://github.com/matter-labs/zksync-era/blob/8ed086afecfcad30bfda44fc4d29a00beea71cca/core/bin/zksync_tee_prover/src/tee_prover.rs#L201-L203

[Relevant
logs](https://grafana.matterlabs.dev/explore?schemaVersion=1&panes=%7B%223ss%22:%7B%22datasource%22:%22cduazndivuosga%22,%22queries%22:%5B%7B%22metrics%22:%5B%7B%22id%22:%221%22,%22type%22:%22logs%22%7D%5D,%22query%22:%22container_name:%5C%22zksync-tee-prover%5C%22%22,%22refId%22:%22A%22,%22datasource%22:%7B%22type%22:%22quickwit-quickwit-datasource%22,%22uid%22:%22cduazndivuosga%22%7D,%22alias%22:%22%22,%22bucketAggs%22:%5B%7B%22type%22:%22date_histogram%22,%22id%22:%222%22,%22settings%22:%7B%22interval%22:%22auto%22%7D,%22field%22:%22%22%7D%5D,%22timeField%22:%22%22%7D%5D,%22range%22:%7B%22from%22:%221724854712742%22,%22to%22:%221724855017388%22%7D%7D%7D&orgId=1).

## Why ❔

To mitigate panics on `proof-data-handler` redeployments.

## Checklist

- [x] PR title corresponds to the body of PR (we generate changelog
entries from PRs).
- [ ] Tests for the changes have been added / updated.
- [ ] Documentation comments have been added / updated.
- [x] Code has been formatted via `zk fmt` and `zk lint`.

## Patch
### Cargo.lock
```diff
@@ -5520,6 +5520,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "25996b82292a7a57ed3508f052cfff8640d38d32018784acd714758b43da9c8f"
 dependencies = [
  "secp256k1-sys",
+ "serde",
 ]
 
 [[package]]
@@ -9620,6 +9621,7 @@ version = "0.1.0"
 dependencies = [
  "anyhow",
  "async-trait",
+ "envy",
  "reqwest 0.12.5",
  "secp256k1",
  "serde",
```

### core/bin/zksync_tee_prover/Cargo.toml
```diff
@@ -14,8 +14,9 @@ publish = false
 [dependencies]
 anyhow.workspace = true
 async-trait.workspace = true
+envy.workspace = true
 reqwest.workspace = true
-secp256k1.workspace = true
+secp256k1 = { workspace = true, features = ["serde"] }
 serde = { workspace = true, features = ["derive"] }
 thiserror.workspace = true
 tokio = { workspace = true, features = ["full"] }
```

### core/bin/zksync_tee_prover/src/config.rs
```diff
@@ -1,12 +1,13 @@
-use std::path::PathBuf;
+use std::{path::PathBuf, time::Duration};
 
 use secp256k1::SecretKey;
+use serde::Deserialize;
 use url::Url;
 use zksync_env_config::FromEnv;
 use zksync_types::tee_types::TeeType;
 
 /// Configuration for the TEE prover.
-#[derive(Debug)]
+#[derive(Debug, Clone, Deserialize)]
 pub(crate) struct TeeProverConfig {
     /// The private key used to sign the proofs.
     pub signing_key: SecretKey,
@@ -16,24 +17,34 @@ pub(crate) struct TeeProverConfig {
     pub tee_type: TeeType,
     /// TEE proof data handler API.
     pub api_url: Url,
+    /// Number of retries for retriable errors before giving up on recovery (i.e., returning an error
+    /// from [`Self::run()`]).
+    pub max_retries: usize,
+    /// Initial back-off interval when retrying recovery on a retriable error. Each subsequent retry interval
+    /// will be multiplied by [`Self.retry_backoff_multiplier`].
+    pub initial_retry_backoff: Duration,
+    /// Multiplier for the back-off interval when retrying recovery on a retriable error.
+    pub retry_backoff_multiplier: f32,
+    /// Maximum back-off interval when retrying recovery on a retriable error.
+    pub max_backoff: Duration,
 }
 
 impl FromEnv for TeeProverConfig {
     /// Constructs the TEE Prover configuration from environment variables.
     ///
     /// Example usage of environment variables for tests:
     /// ```
-    /// export TEE_SIGNING_KEY="b50b38c8d396c88728fc032ece558ebda96907a0b1a9340289715eef7bf29deb"
-    /// export TEE_QUOTE_FILE="/tmp/test"  # run `echo test > /tmp/test` beforehand
-    /// export TEE_TYPE="sgx"
-    /// export TEE_API_URL="http://127.0.0.1:3320"
+    /// export TEE_PROVER_SIGNING_KEY="b50b38c8d396c88728fc032ece558ebda96907a0b1a9340289715eef7bf29deb"
+    /// export TEE_PROVER_ATTESTATION_QUOTE_FILE_PATH="/tmp/test"  # run `echo test > /tmp/test` beforehand
+    /// export TEE_PROVER_TEE_TYPE="sgx"
+    /// export TEE_PROVER_API_URL="http://127.0.0.1:3320"
+    /// export TEE_PROVER_MAX_RETRIES=10
+    /// export TEE_PROVER_INITIAL_RETRY_BACKOFF=1
+    /// export TEE_PROVER_RETRY_BACKOFF_MULTIPLIER=2.0
+    /// export TEE_PROVER_MAX_BACKOFF=128
     /// ```
     fn from_env() -> anyhow::Result<Self> {
-        Ok(Self {
-            signing_key: std::env::var("TEE_SIGNING_KEY")?.parse()?,
-            attestation_quote_file_path: std::env::var("TEE_QUOTE_FILE")?.parse()?,
-            tee_type: std::env::var("TEE_TYPE")?.parse()?,
-            api_url: std::env::var("TEE_API_URL")?.parse()?,
-        })
+        let config: Self = envy::prefixed("TEE_PROVER_").from_env()?;
+        Ok(config)
     }
 }
```

### core/bin/zksync_tee_prover/src/main.rs
```diff
@@ -32,8 +32,6 @@ fn main() -> anyhow::Result<()> {
         ObservabilityConfig::from_env().context("ObservabilityConfig::from_env()")?;
 
     let tee_prover_config = TeeProverConfig::from_env()?;
-    let attestation_quote_bytes = std::fs::read(tee_prover_config.attestation_quote_file_path)?;
-
     let prometheus_config = PrometheusConfig::from_env()?;
 
     let mut builder = ZkStackServiceBuilder::new()?;
@@ -45,12 +43,7 @@ fn main() -> anyhow::Result<()> {
 
     builder
         .add_layer(SigintHandlerLayer)
-        .add_layer(TeeProverLayer::new(
-            tee_prover_config.api_url,
-            tee_prover_config.signing_key,
-            attestation_quote_bytes,
-            tee_prover_config.tee_type,
-        ));
+        .add_layer(TeeProverLayer::new(tee_prover_config));
 
     if let Some(gateway) = prometheus_config.gateway_endpoint() {
         let exporter_config =
```

### core/bin/zksync_tee_prover/src/tee_prover.rs
```diff
@@ -1,7 +1,6 @@
-use std::{fmt, time::Duration};
+use std::fmt;
 
-use secp256k1::{ecdsa::Signature, Message, PublicKey, Secp256k1, SecretKey};
-use url::Url;
+use secp256k1::{ecdsa::Signature, Message, PublicKey, Secp256k1};
 use zksync_basic_types::H256;
 use zksync_node_framework::{
     service::StopReceiver,
@@ -11,32 +10,21 @@ use zksync_node_framework::{
 };
 use zksync_prover_interface::inputs::TeeVerifierInput;
 use zksync_tee_verifier::Verify;
-use zksync_types::{tee_types::TeeType, L1BatchNumber};
+use zksync_types::L1BatchNumber;
 
-use crate::{api_client::TeeApiClient, error::TeeProverError, metrics::METRICS};
+use crate::{
+    api_client::TeeApiClient, config::TeeProverConfig, error::TeeProverError, metrics::METRICS,
+};
 
 /// Wiring layer for `TeeProver`
 #[derive(Debug)]
 pub(crate) struct TeeProverLayer {
-    api_url: Url,
-    signing_key: SecretKey,
-    attestation_quote_bytes: Vec<u8>,
-    tee_type: TeeType,
+    config: TeeProverConfig,
 }
 
 impl TeeProverLayer {
-    pub fn new(
-        api_url: Url,
-        signing_key: SecretKey,
-        attestation_quote_bytes: Vec<u8>,
-        tee_type: TeeType,
-    ) -> Self {
-        Self {
-            api_url,
-            signing_key,
-            attestation_quote_bytes,
-            tee_type,
-        }
+    pub fn new(config: TeeProverConfig) -> Self {
+        Self { config }
     }
 }
 
@@ -56,34 +44,24 @@ impl WiringLayer for TeeProverLayer {
     }
 
     async fn wire(self, _input: Self::Input) -> Result<Self::Output, WiringError> {
+        let api_url = self.config.api_url.clone();
         let tee_prover = TeeProver {
-            config: Default::default(),
-            signing_key: self.signing_key,
-            public_key: self.signing_key.public_key(&Secp256k1::new()),
-            attestation_quote_bytes: self.attestation_quote_bytes,
-            tee_type: self.tee_type,
-            api_client: TeeApiClient::new(self.api_url),
+            config: self.config,
+            api_client: TeeApiClient::new(api_url),
         };
         Ok(LayerOutput { tee_prover })
     }
 }
 
 pub(crate) struct TeeProver {
     config: TeeProverConfig,
-    signing_key: SecretKey,
-    public_key: PublicKey,
-    attestation_quote_bytes: Vec<u8>,
-    tee_type: TeeType,
     api_client: TeeApiClient,
 }
 
 impl fmt::Debug for TeeProver {
     fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
         f.debug_struct("TeeProver")
             .field("config", &self.config)
-            .field("public_key", &self.public_key)
-            .field("attestation_quote_bytes", &self.attestation_quote_bytes)
-            .field("tee_type", &self.tee_type)
             .finish()
     }
 }
@@ -101,7 +79,7 @@ impl TeeProver {
                 let batch_number = verification_result.batch_number;
                 let msg_to_sign = Message::from_slice(root_hash_bytes)
                     .map_err(|e| TeeProverError::Verification(e.into()))?;
-                let signature = self.signing_key.sign_ecdsa(msg_to_sign);
+                let signature = self.config.signing_key.sign_ecdsa(msg_to_sign);
                 observer.observe();
                 Ok((signature, batch_number, verification_result.value_hash))
             }
@@ -111,17 +89,17 @@ impl TeeProver {
         }
     }
 
-    async fn step(&self) -> Result<Option<L1BatchNumber>, TeeProverError> {
-        match self.api_client.get_job(self.tee_type).await? {
+    async fn step(&self, public_key: &PublicKey) -> Result<Option<L1BatchNumber>, TeeProverError> {
+        match self.api_client.get_job(self.config.tee_type).await? {
             Some(job) => {
                 let (signature, batch_number, root_hash) = self.verify(*job)?;
                 self.api_client
                     .submit_proof(
                         batch_number,
                         signature,
-                        &self.public_key,
+                        public_key,
                         root_hash,
-                        self.tee_type,
+                        self.config.tee_type,
                     )
                     .await?;
                 Ok(Some(batch_number))
@@ -134,30 +112,6 @@ impl TeeProver {
     }
 }
 
-/// TEE prover configuration options.
-#[derive(Debug, Clone)]
-pub struct TeeProverConfig {
-    /// Number of retries for retriable errors before giving up on recovery (i.e., returning an error
-    /// from [`Self::run()`]).
-    pub max_retries: usize,
-    /// Initial back-off interval when retrying recovery on a retriable error. Each subsequent retry interval
-    /// will be multiplied by [`Self.retry_backoff_multiplier`].
-    pub initial_retry_backoff: Duration,
-    pub retry_backoff_multiplier: f32,
-    pub max_backoff: Duration,
-}
-
-impl Default for TeeProverConfig {
-    fn default() -> Self {
-        Self {
-            max_retries: 5,
-            initial_retry_backoff: Duration::from_secs(1),
-            retry_backoff_multiplier: 2.0,
-            max_backoff: Duration::from_secs(128),
-        }
-    }
-}
-
 #[async_trait::async_trait]
 impl Task for TeeProver {
     fn id(&self) -> TaskId {
@@ -167,24 +121,27 @@ impl Task for TeeProver {
     async fn run(self: Box<Self>, mut stop_receiver: StopReceiver) -> anyhow::Result<()> {
         tracing::info!("Starting the task {}", self.id());
 
+        let config = &self.config;
+        let attestation_quote_bytes = std::fs::read(&config.attestation_quote_file_path)?;
+        let public_key = config.signing_key.public_key(&Secp256k1::new());
         self.api_client
-            .register_attestation(self.attestation_quote_bytes.clone(), &self.public_key)
+            .register_attestation(attestation_quote_bytes, &public_key)
             .await?;
 
         let mut retries = 1;
-        let mut backoff = self.config.initial_retry_backoff;
+        let mut backoff = config.initial_retry_backoff;
         let mut observer = METRICS.job_waiting_time.start();
 
         loop {
             if *stop_receiver.0.borrow() {
                 tracing::info!("Stop signal received, shutting down TEE Prover component");
                 return Ok(());
             }
-            let result = self.step().await;
+            let result = self.step(&public_key).await;
             let need_to_sleep = match result {
                 Ok(batch_number) => {
                     retries = 1;
-                    backoff = self.config.initial_retry_backoff;
+                    backoff = config.initial_retry_backoff;
                     if let Some(batch_number) = batch_number {
                         observer.observe();
                         observer = METRICS.job_waiting_time.start();
@@ -198,14 +155,14 @@ impl Task for TeeProver {
                 }
                 Err(err) => {
                     METRICS.network_errors_counter.inc_by(1);
-                    if !err.is_retriable() || retries > self.config.max_retries {
+                    if !err.is_retriable() || retries > config.max_retries {
                         return Err(err.into());
                     }
-                    tracing::warn!(%err, "Failed TEE prover step function {retries}/{}, retrying in {} milliseconds.", self.config.max_retries, backoff.as_millis());
+                    tracing::warn!(%err, "Failed TEE prover step function {retries}/{}, retrying in {} milliseconds.", config.max_retries, backoff.as_millis());
                     retries += 1;
                     backoff = std::cmp::min(
-                        backoff.mul_f32(self.config.retry_backoff_multiplier),
-                        self.config.max_backoff,
+                        backoff.mul_f32(config.retry_backoff_multiplier),
+                        config.max_backoff,
                     );
                     true
                 }
```

### etc/nix/container-tee_prover.nix
```diff
@@ -28,7 +28,11 @@ nixsgxLib.mkSGXContainer {
       log_level = "error";
 
       env = {
-        TEE_API_URL.passthrough = true;
+        TEE_PROVER_API_URL.passthrough = true;
+        TEE_PROVER_MAX_RETRIES.passthrough = true;
+        TEE_PROVER_INITIAL_RETRY_BACKOFF_SECONDS.passthrough = true;
+        TEE_PROVER_RETRY_BACKOFF_MULTIPLIER.passthrough = true;
+        TEE_PROVER_MAX_BACKOFF_SECONDS.passthrough = true;
         API_PROMETHEUS_LISTENER_PORT.passthrough = true;
         API_PROMETHEUS_PUSHGATEWAY_URL.passthrough = true;
         API_PROMETHEUS_PUSH_INTERVAL_MS.passthrough = true;
```
