# [?] [fix] #2457: Fix tests flakiness related to shut down on panic (#2474)

## Summary
Severity: Unknown
Chain: Hyperledger Iroha
Component: hyperledger/iroha
Published: 2022-07-14
Source: https://github.com/hyperledger-iroha/iroha/commit/bf01205da95cf121f6789126f7317baf5c5aafd9
Type: security-commit

## Details
[fix] #2457: Fix tests flakiness related to shut down on panic (#2474)

* [fix] #2457: Add shut down on panic configuration

Signed-off-by: Ales Tsurko <ales.tsurko@gmail.com>

* [fix] #2457: Update docs

Signed-off-by: Ales Tsurko <ales.tsurko@gmail.com>

* [fix] #2457: Fix linter checks

Signed-off-by: Ales Tsurko <ales.tsurko@gmail.com>

## Patch
### Cargo.lock
```diff
@@ -1254,6 +1254,7 @@ checksum = "f73fe65f54d1e12b726f517d3e2135ca3125a437b6d998caf1962961f7172d9e"
 dependencies = [
  "futures-channel",
  "futures-core",
+ "futures-executor",
  "futures-io",
  "futures-sink",
  "futures-task",
@@ -1276,6 +1277,17 @@ version = "0.3.21"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "0c09fd04b7e4073ac7156a9539b57a484a8ea920f79c7c675d05d289ab6110d3"
 
+[[package]]
+name = "futures-executor"
+version = "0.3.21"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "9420b90cfa29e327d0429f19be13e7ddb68fa1cccb09d65e5706b8c7a749b8a6"
+dependencies = [
+ "futures-core",
+ "futures-task",
+ "futures-util",
+]
+
 [[package]]
 name = "futures-io"
 version = "0.3.21"
@@ -1700,6 +1712,7 @@ dependencies = [
  "parity-scale-codec",
  "serde",
  "serde_json",
+ "serial_test",
  "test_network",
  "thiserror",
  "tokio",
@@ -3311,6 +3324,32 @@ dependencies = [
  "serde",
 ]
 
+[[package]]
+name = "serial_test"
+version = "0.8.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "7eec42e7232e5ca56aa59d63af3c7f991fe71ee6a3ddd2d3480834cf3902b007"
+dependencies = [
+ "futures",
+ "lazy_static",
+ "log",
+ "parking_lot",
+ "serial_test_derive",
+]
+
+[[package]]
+name = "serial_test_derive"
+version = "0.8.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "f1b95bb2f4f624565e8fe8140c789af7e2082c0e0561b5a82a1b678baa9703dc"
+dependencies = [
+ "proc-macro-error",
+ "proc-macro2",
+ "quote",
+ "rustversion",
+ "syn",
+]
+
 [[package]]
 name = "sha-1"
 version = "0.9.8"
```

### cli/Cargo.toml
```diff
@@ -63,4 +63,5 @@ tokio = { version = "1.6.0", features = ["sync", "time", "rt", "io-util", "rt-mu
 warp = "0.3"
 
 [dev-dependencies]
+serial_test = "0.8.0"
 test_network = { version = "=2.0.0-pre-rc.5", path = "../core/test_network" }
```

### cli/src/config.rs
```diff
@@ -29,6 +29,8 @@ pub struct Configuration {
     pub private_key: PrivateKey,
     /// Disable coloring of the backtrace and error report on panic.
     pub disable_panic_terminal_colors: bool,
+    /// Iroha will shutdown on any panic if this option is set to `true`.
+    pub shutdown_on_panic: bool,
     /// `Kura` related configuration.
     #[config(inner)]
     pub kura: KuraConfiguration,
@@ -71,6 +73,7 @@ impl Default for Configuration {
             public_key,
             private_key,
             disable_panic_terminal_colors: bool::default(),
+            shutdown_on_panic: false,
             kura: KuraConfiguration::default(),
             sumeragi: sumeragi_configuration,
             torii: ToriiConfiguration::default(),
```

### cli/src/lib.rs
```diff
@@ -252,7 +252,9 @@ where
 
         Self::start_listening_signal(Arc::clone(&notify_shutdown))?;
 
-        Self::prepare_panic_hook(notify_shutdown);
+        if config.shutdown_on_panic {
+            Self::prepare_panic_hook(notify_shutdown);
+        }
 
         let torii = Some(torii);
         Ok(Self {
@@ -367,10 +369,13 @@ fn domains(configuration: &config::Configuration) -> [Domain; 1] {
 mod tests {
     use std::{panic, thread};
 
+    use serial_test::serial;
+
     use super::*;
 
-    #[tokio::test]
     #[allow(clippy::panic)]
+    #[tokio::test]
+    #[serial]
     async fn iroha_should_notify_on_panic() {
         let notify = Arc::new(Notify::new());
         let hook = panic::take_hook();
```

### docs/source/references/config.md
```diff
@@ -14,6 +14,7 @@ The following is the default configuration used by Iroha.
     "payload": "282ed9f3cf92811c3818dbc4ae594ed59dc1a2f78e4241e31924e101d6b1fb831c61faf8fe94e253b93114240394f79a607b7fa55f9e5a41ebec74b88055768b"
   },
   "DISABLE_PANIC_TERMINAL_COLORS": false,
+  "SHUTDOWN_ON_PANIC": false,
   "KURA": {
     "INIT_MODE": "strict",
     "BLOCK_STORE_PATH": "./blocks",
@@ -463,6 +464,16 @@ Has type `u64`. Can be configured via environment variable `QUEUE_TRANSACTION_TI
 86400000
 ```
 
+## `shutdown_on_panic`
+
+Iroha will shutdown on any panic if this option is set to `true`.
+
+Has type `bool`. Can be configured via environment variable `IROHA_SHUTDOWN_ON_PANIC`
+
+```json
+false
+```
+
 ## `sumeragi`
 
 `Sumeragi` related configuration.
```
