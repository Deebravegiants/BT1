# [?] Fix genesis state download panic when running in debug mode (#4753)

## Summary
Severity: Unknown
Chain: Ethereum
Component: sigp/lighthouse
Published: 2023-09-21
Source: https://github.com/sigp/lighthouse/commit/a0478da99087e5f8f727864e055d179b9618c374
Type: security-commit

## Details
Fix genesis state download panic when running in debug mode (#4753)

## Issue Addressed

#4738 

## Proposed Changes

See the above issue for details. Went with option #2 to use the async reqwest client in `Eth2NetworkConfig` and propagate the async-ness.

## Patch
### Cargo.lock
```diff
@@ -2220,9 +2220,11 @@ dependencies = [
 name = "eth2_network_config"
 version = "0.2.0"
 dependencies = [
+ "bytes",
  "discv5",
  "eth2_config",
  "ethereum_ssz",
+ "futures",
  "logging",
  "pretty_reqwest_error",
  "reqwest",
@@ -2231,6 +2233,7 @@ dependencies = [
  "sha2 0.10.7",
  "slog",
  "tempfile",
+ "tokio",
  "types",
  "url",
  "zip",
```

### Dockerfile
```diff
@@ -1,4 +1,4 @@
-FROM rust:1.68.2-bullseye AS builder
+FROM rust:1.69.0-bullseye AS builder
 RUN apt-get update && apt-get -y upgrade && apt-get install -y cmake libclang-dev
 COPY . lighthouse
 ARG FEATURES
```

### account_manager/src/validator/exit.rs
```diff
@@ -10,7 +10,6 @@ use eth2_keystore::Keystore;
 use eth2_network_config::Eth2NetworkConfig;
 use safe_arith::SafeArith;
 use sensitive_url::SensitiveUrl;
-use slog::Logger;
 use slot_clock::{SlotClock, SystemTimeSlotClock};
 use std::path::{Path, PathBuf};
 use std::time::Duration;
@@ -79,12 +78,6 @@ pub fn cli_run<E: EthSpec>(matches: &ArgMatches, env: Environment<E>) -> Result<
     let password_file_path: Option<PathBuf> =
         clap_utils::parse_optional(matches, PASSWORD_FILE_FLAG)?;
 
-    let genesis_state_url: Option<String> =
-        clap_utils::parse_optional(matches, "genesis-state-url")?;
-    let genesis_state_url_timeout =
-        clap_utils::parse_required(matches, "genesis-state-url-timeout")
-            .map(Duration::from_secs)?;
-
     let stdin_inputs = cfg!(windows) || matches.is_present(STDIN_INPUTS_FLAG);
     let no_wait = matches.is_present(NO_WAIT);
     let no_confirmation = matches.is_present(NO_CONFIRMATION);
@@ -111,9 +104,6 @@ pub fn cli_run<E: EthSpec>(matches: &ArgMatches, env: Environment<E>) -> Result<
         &eth2_network_config,
         no_wait,
         no_confirmation,
-        genesis_state_url,
-        genesis_state_url_timeout,
-        env.core_context().log(),
     ))?;
 
     Ok(())
@@ -130,13 +120,10 @@ async fn publish_voluntary_exit<E: EthSpec>(
     eth2_network_config: &Eth2NetworkConfig,
     no_wait: bool,
     no_confirmation: bool,
-    genesis_state_url: Option<String>,
-    genesis_state_url_timeout: Duration,
-    log: &Logger,
 ) -> Result<(), String> {
     let genesis_data = get_geneisis_data(client).await?;
     let testnet_genesis_root = eth2_network_config
-        .genesis_validators_root::<E>(genesis_state_url.as_deref(), genesis_state_url_timeout, log)?
+        .genesis_validators_root::<E>()?
         .ok_or("Genesis state is unknown")?;
 
     // Verify that the beacon node and validator being exited are on the same network.
```

### account_manager/src/validator/slashing_protection.rs
```diff
@@ -7,7 +7,6 @@ use slashing_protection::{
 use std::fs::File;
 use std::path::PathBuf;
 use std::str::FromStr;
-use std::time::Duration;
 use types::{Epoch, EthSpec, PublicKeyBytes, Slot};
 
 pub const CMD: &str = "slashing-protection";
@@ -82,24 +81,12 @@ pub fn cli_run<T: EthSpec>(
     validator_base_dir: PathBuf,
 ) -> Result<(), String> {
     let slashing_protection_db_path = validator_base_dir.join(SLASHING_PROTECTION_FILENAME);
-
-    let genesis_state_url: Option<String> =
-        clap_utils::parse_optional(matches, "genesis-state-url")?;
-    let genesis_state_url_timeout =
-        clap_utils::parse_required(matches, "genesis-state-url-timeout")
-            .map(Duration::from_secs)?;
-
-    let context = env.core_context();
     let eth2_network_config = env
         .eth2_network_config
         .ok_or("Unable to get testnet configuration from the environment")?;
 
     let genesis_validators_root = eth2_network_config
-        .genesis_validators_root::<T>(
-            genesis_state_url.as_deref(),
-            genesis_state_url_timeout,
-            context.log(),
-        )?
+        .genesis_validators_root::<T>()?
         .ok_or_else(|| "Unable to get genesis state, has genesis occurred?".to_string())?;
 
     match matches.subcommand() {
```

### beacon_node/client/src/builder.rs
```diff
@@ -256,7 +256,7 @@ where
                     "Starting from known genesis state";
                 );
 
-                let genesis_state = genesis_state(&runtime_context, &config, log)?;
+                let genesis_state = genesis_state(&runtime_context, &config, log).await?;
 
                 builder.genesis_state(genesis_state).map(|v| (v, None))?
             }
@@ -276,7 +276,7 @@ where
                     .map_err(|e| format!("Unable to parse weak subj state SSZ: {:?}", e))?;
                 let anchor_block = SignedBeaconBlock::from_ssz_bytes(&anchor_block_bytes, &spec)
                     .map_err(|e| format!("Unable to parse weak subj block SSZ: {:?}", e))?;
-                let genesis_state = genesis_state(&runtime_context, &config, log)?;
+                let genesis_state = genesis_state(&runtime_context, &config, log).await?;
 
                 builder
                     .weak_subjectivity_state(anchor_state, anchor_block, genesis_state)
@@ -377,7 +377,7 @@ where
 
                 debug!(context.log(), "Downloaded finalized block");
 
-                let genesis_state = genesis_state(&runtime_context, &config, log)?;
+                let genesis_state = genesis_state(&runtime_context, &config, log).await?;
 
                 info!(
                     context.log(),
@@ -1083,7 +1083,7 @@ where
 }
 
 /// Obtain the genesis state from the `eth2_network_config` in `context`.
-fn genesis_state<T: EthSpec>(
+async fn genesis_state<T: EthSpec>(
     context: &RuntimeContext<T>,
     config: &ClientConfig,
     log: &Logger,
@@ -1097,6 +1097,7 @@ fn genesis_state<T: EthSpec>(
             config.genesis_state_url.as_deref(),
             config.genesis_state_url_timeout,
             log,
-        )?
+        )
+        .await?
         .ok_or_else(|| "Genesis state is unknown".to_string())
 }
```

### boot_node/src/config.rs
```diff
@@ -25,7 +25,7 @@ pub struct BootNodeConfig<T: EthSpec> {
 }
 
 impl<T: EthSpec> BootNodeConfig<T> {
-    pub fn new(
+    pub async fn new(
         matches: &ArgMatches<'_>,
         eth2_network_config: &Eth2NetworkConfig,
     ) -> Result<Self, String> {
@@ -99,7 +99,7 @@ impl<T: EthSpec> BootNodeConfig<T> {
 
                 if eth2_network_config.genesis_state_is_known() {
                     let genesis_state = eth2_network_config
-                        .genesis_state::<T>(genesis_state_url.as_deref(), genesis_state_url_timeout, &logger)?
+                        .genesis_state::<T>(genesis_state_url.as_deref(), genesis_state_url_timeout, &logger).await?
                         .ok_or_else(|| {
                             "The genesis state for this network is not known, this is an unsupported mode"
                                 .to_string()
```

### boot_node/src/lib.rs
```diff
@@ -7,7 +7,7 @@ mod cli;
 pub mod config;
 mod server;
 pub use cli::cli_app;
-use config::{BootNodeConfig, BootNodeConfigSerialization};
+use config::BootNodeConfig;
 use types::{EthSpec, EthSpecId};
 
 const LOG_CHANNEL_SIZE: usize = 2048;
@@ -81,20 +81,13 @@ fn main<T: EthSpec>(
         .build()
         .map_err(|e| format!("Failed to build runtime: {}", e))?;
 
-    // parse the CLI args into a useable config
-    let config: BootNodeConfig<T> = BootNodeConfig::new(bn_matches, eth2_network_config)?;
-
-    // Dump configs if `dump-config` or `dump-chain-config` flags are set
-    let config_sz = BootNodeConfigSerialization::from_config_ref(&config);
-    clap_utils::check_dump_configs::<_, T>(
+    // Run the boot node
+    runtime.block_on(server::run::<T>(
         lh_matches,
-        &config_sz,
-        &eth2_network_config.chain_spec::<T>()?,
-    )?;
+        bn_matches,
+        eth2_network_config,
+        log,
+    ))?;
 
-    // Run the boot node
-    if !lh_matches.is_present("immediate-shutdown") {
-        runtime.block_on(server::run(config, log));
-    }
     Ok(())
 }
```

### boot_node/src/server.rs
```diff
@@ -1,14 +1,37 @@
 //! The main bootnode server execution.
 
 use super::BootNodeConfig;
+use crate::config::BootNodeConfigSerialization;
+use clap::ArgMatches;
+use eth2_network_config::Eth2NetworkConfig;
 use lighthouse_network::{
     discv5::{enr::NodeId, Discv5, Discv5Event},
     EnrExt, Eth2Enr,
 };
 use slog::info;
 use types::EthSpec;
 
-pub async fn run<T: EthSpec>(config: BootNodeConfig<T>, log: slog::Logger) {
+pub async fn run<T: EthSpec>(
+    lh_matches: &ArgMatches<'_>,
+    bn_matches: &ArgMatches<'_>,
+    eth2_network_config: &Eth2NetworkConfig,
+    log: slog::Logger,
+) -> Result<(), String> {
+    // parse the CLI args into a useable config
+    let config: BootNodeConfig<T> = BootNodeConfig::new(bn_matches, eth2_network_config).await?;
+
+    // Dump configs if `dump-config` or `dump-chain-config` flags are set
+    let config_sz = BootNodeConfigSerialization::from_config_ref(&config);
+    clap_utils::check_dump_configs::<_, T>(
+        lh_matches,
+        &config_sz,
+        &eth2_network_config.chain_spec::<T>()?,
+    )?;
+
+    if lh_matches.is_present("immediate-shutdown") {
+        return Ok(());
+    }
+
     let BootNodeConfig {
         boot_nodes,
         local_enr,
@@ -65,8 +88,7 @@ pub async fn run<T: EthSpec>(config: BootNodeConfig<T>, log: slog::Logger) {
 
     // start the server
     if let Err(e) = discv5.start().await {
-        slog::crit!(log, "Could not start discv5 server"; "error" => %e);
-        return;
+        return Err(format!("Could not start discv5 server: {e:?}"));
     }
 
     // if there are peers in the local routing table, establish a session by running a query
@@ -82,8 +104,7 @@ pub async fn run<T: EthSpec>(config: BootNodeConfig<T>, log: slog::Logger) {
     let mut event_stream = match discv5.event_stream().await {
         Ok(stream) => stream,
         Err(e) => {
-            slog::crit!(log, "Failed to obtain event stream"; "error" => %e);
-            return;
+            return Err(format!("Failed to obtain event stream: {e:?}"));
         }
     };
 
```

### common/eth2_network_config/Cargo.toml
```diff
@@ -12,6 +12,7 @@ eth2_config = { path = "../eth2_config" }
 
 [dev-dependencies]
 tempfile = "3.1.0"
+tokio = "1.14.0"
 
 [dependencies]
 serde_yaml = "0.8.13"
@@ -26,3 +27,5 @@ url = "2.2.2"
 sensitive_url = { path = "../sensitive_url" }
 slog = "2.5.2"
 logging = { path = "../logging" }
+futures = "0.3.7"
+bytes = "1.1.0"
\ No newline at end of file
```

### common/eth2_network_config/src/lib.rs
```diff
@@ -11,10 +11,11 @@
 //! To add a new built-in testnet, add it to the `define_hardcoded_nets` invocation in the `eth2_config`
 //! crate.
 
+use bytes::Bytes;
 use discv5::enr::{CombinedKey, Enr};
 use eth2_config::{instantiate_hardcoded_nets, HardcodedNet};
 use pretty_reqwest_error::PrettyReqwestError;
-use reqwest::blocking::Client;
+use reqwest::{Client, Error};
 use sensitive_url::SensitiveUrl;
 use sha2::{Digest, Sha256};
 use slog::{info, warn, Logger};
@@ -127,14 +128,8 @@ impl Eth2NetworkConfig {
         self.genesis_state_source != GenesisStateSource::Unknown
     }
 
-    /// The `genesis_validators_root` of the genesis state. May download the
-    /// genesis state if the value is not already available.
-    pub fn genesis_validators_root<E: EthSpec>(
-        &self,
-        genesis_state_url: Option<&str>,
-        timeout: Duration,
-        log: &Logger,
-    ) -> Result<Option<Hash256>, String> {
+    /// The `genesis_validators_root` of the genesis state.
+    pub fn genesis_validators_root<E: EthSpec>(&self) -> Result<Option<Hash256>, String> {
         if let GenesisStateSource::Url {
             genesis_validators_root,
             ..
@@ -149,10 +144,8 @@ impl Eth2NetworkConfig {
                     )
                 })
         } else {
-            self.genesis_state::<E>(genesis_state_url, timeout, log)?
-                .map(|state| state.genesis_validators_root())
-                .map(Result::Ok)
-                .transpose()
+            self.get_genesis_state_from_bytes::<E>()
+                .map(|state| Some(state.genesis_validators_root()))
         }
     }
 
@@ -170,7 +163,7 @@ impl Eth2NetworkConfig {
     ///
     /// If the genesis state is configured to be downloaded from a URL, then the
     /// `genesis_state_url` will override the built-in list of download URLs.
-    pub fn genesis_state<E: EthSpec>(
+    pub async fn genesis_state<E: EthSpec>(
         &self,
         genesis_state_url: Option<&str>,
         timeout: Duration,
@@ -180,15 +173,7 @@ impl Eth2NetworkConfig {
         match &self.genesis_state_source {
             GenesisStateSource::Unknown => Ok(None),
             GenesisStateSource::IncludedBytes => {
-                let state = self
-                    .genesis_state_bytes
-                    .as_ref()
-                    .map(|bytes| {
-                        BeaconState::from_ssz_bytes(bytes.as_ref(), &spec).map_err(|e| {
-                            format!("Built-in genesis state SSZ bytes are invalid: {:?}", e)
-                        })
-                    })
-                    .ok_or("Genesis state bytes missing from Eth2NetworkConfig")??;
+                let state = self.get_genesis_state_from_bytes()?;
                 Ok(Some(state))
             }
             GenesisStateSource::Url {
@@ -200,9 +185,9 @@ impl Eth2NetworkConfig {
                     format!("Unable to parse genesis state bytes checksum: {:?}", e)
                 })?;
                 let bytes = if let Some(specified_url) = genesis_state_url {
-                    download_genesis_state(&[specified_url], timeout, checksum, log)
+                    download_genesis_state(&[specified_url], timeout, checksum, log).await
                 } else {
-                    download_genesis_state(built_in_urls, timeout, checksum, log)
+                    download_genesis_state(built_in_urls, timeout, checksum, log).await
                 }?;
                 let state = BeaconState::from_ssz_bytes(bytes.as_ref(), &spec).map_err(|e| {
                     format!("Downloaded genesis state SSZ bytes are invalid: {:?}", e)
@@ -228,6 +213,17 @@ impl Eth2NetworkConfig {
         }
     }
 
+    fn get_genesis_state_from_bytes<E: EthSpec>(&self) -> Result<BeaconState<E>, String> {
+        let spec = self.chain_spec::<E>()?;
+        self.genesis_state_bytes
+            .as_ref()
+            .map(|bytes| {
+                BeaconState::from_ssz_bytes(bytes.as_ref(), &spec)
+                    .map_err(|e| format!("Built-in genesis state SSZ bytes are invalid: {:?}", e))
+            })
+            .ok_or("Genesis state bytes missing from Eth2NetworkConfig")?
+    }
+
     /// Write the files to the directory.
     ///
     /// Overwrites files if specified to do so.
@@ -352,7 +348,7 @@ impl Eth2NetworkConfig {
 /// Try to download a genesis state from each of the `urls` in the order they
 /// are defined. Return `Ok` if any url returns a response that matches the
 /// given `checksum`.
-fn download_genesis_state(
+async fn download_genesis_state(
     urls: &[&str],
     timeout: Duration,
     checksum: Hash256,
@@ -384,12 +380,7 @@ fn download_genesis_state(
         );
 
         let client = Client::new();
-        let response = client
-            .get(url)
-            .header("Accept", "application/octet-stream")
-            .timeout(timeout)
-            .send()
-            .and_then(|r| r.error_for_status().and_then(|r| r.bytes()));
+        let response = get_state_bytes(timeout, url, client).await;
 
         match response {
             Ok(bytes) => {
@@ -419,6 +410,18 @@ fn download_genesis_state(
     ))
 }
 
+async fn get_state_bytes(timeout: Duration, url: Url, client: Client) -> Result<Bytes, Error> {
+    client
+        .get(url)
+        .header("Accept", "application/octet-stream")
+        .timeout(timeout)
+        .send()
+        .await?
+        .error_for_status()?
+        .bytes()
+        .await
+}
+
 /// Parses the `url` and joins the necessary state download path.
 fn parse_state_download_url(url: &str) -> Result<Url, String> {
     Url::parse(url)
@@ -463,11 +466,12 @@ mod tests {
         assert_eq!(spec, config.chain_spec::<GnosisEthSpec>().unwrap());
     }
 
-    #[test]
-    fn mainnet_genesis_state() {
+    #[tokio::test]
+    async fn mainnet_genesis_state() {
         let config = Eth2NetworkConfig::from_hardcoded_net(&MAINNET).unwrap();
         config
             .genesis_state::<E>(None, Duration::from_secs(1), &logging::test_logger())
+            .await
             .expect("beacon state can decode");
     }
 
```

### lcli/Dockerfile
```diff
@@ -1,7 +1,7 @@
 # `lcli` requires the full project to be in scope, so this should be built either:
 #  - from the `lighthouse` dir with the command: `docker build -f ./lcli/Dockerflie .`
 #  - from the current directory with the command: `docker build -f ./Dockerfile ../`
-FROM rust:1.68.2-bullseye AS builder
+FROM rust:1.69.0-bullseye AS builder
 RUN apt-get update && apt-get -y upgrade && apt-get install -y cmake libclang-dev
 COPY . lighthouse
 ARG PORTABLE
```

### lighthouse/Cargo.toml
```diff
@@ -4,7 +4,7 @@ version = "4.4.1"
 authors = ["Sigma Prime <contact@sigmaprime.io>"]
 edition = "2021"
 autotests = false
-rust-version = "1.68.2"
+rust-version = "1.69.0"
 
 [features]
 default = ["slasher-lmdb"]
```
