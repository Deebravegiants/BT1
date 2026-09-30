# [?] [fix] #1480: Shut down on panic (#2445)

## Summary
Severity: Unknown
Chain: Hyperledger Iroha
Component: hyperledger/iroha
Published: 2022-07-07
Source: https://github.com/hyperledger-iroha/iroha/commit/2c897f23f95e04d2a61077729b1ffef847acc199
Type: security-commit

## Details
[fix] #1480: Shut down on panic (#2445)

* [fix] #1480: Add panic hook to exit program on panic

Signed-off-by: Ales Tsurko <ales.tsurko@gmail.com>

* [fix] #1480: Use quit crate instead of process::exit

Signed-off-by: Ales Tsurko <ales.tsurko@gmail.com>

* [fix] #1480: Use tokio::Notify

Signed-off-by: Ales Tsurko <ales.tsurko@gmail.com>

* [fix] #1480: Update test

Signed-off-by: Ales Tsurko <ales.tsurko@gmail.com>

* [fix] #1480: Fix linter issues

Signed-off-by: Ales Tsurko <ales.tsurko@gmail.com>

## Patch
### cli/Cargo.toml
```diff
@@ -51,16 +51,16 @@ iroha_p2p = { version = "=2.0.0-pre-rc.5", path = "../p2p" }
 iroha_schema_gen = { version = "=2.0.0-pre-rc.5", path = "../schema/gen", optional = true }
 iroha_cli_derive = { version = "=2.0.0-pre-rc.5", path = "derive" }
 
+async-trait = "0.1"
+color-eyre = "0.5.11"
 eyre = "0.6.5"
 futures = { version = "0.3.17", default-features = false, features = ["std", "async-await"] }
 parity-scale-codec = { version = "2.3.1", default-features = false, features = ["derive"] }
 serde = { version = "1.0", features = ["derive"] }
 serde_json = "1.0"
-async-trait = "0.1"
+thiserror = "1.0.28"
 tokio = { version = "1.6.0", features = ["sync", "time", "rt", "io-util", "rt-multi-thread", "macros", "fs", "signal"] }
 warp = "0.3"
-thiserror = "1.0.28"
-color-eyre = "0.5.11"
 
 [dev-dependencies]
 test_network = { version = "=2.0.0-pre-rc.5", path = "../core/test_network" }
```

### cli/src/lib.rs
```diff
@@ -4,7 +4,7 @@
 //!
 //! `Iroha` is the main instance of the peer program. `Arguments`
 //! should be constructed externally: (see `main.rs`).
-use std::{path::PathBuf, sync::Arc};
+use std::{panic, path::PathBuf, sync::Arc};
 
 use color_eyre::eyre::{eyre, Result, WrapErr};
 use config::Configuration;
@@ -138,6 +138,14 @@ where
         .await
     }
 
+    fn prepare_panic_hook(notify_shutdown: Arc<Notify>) {
+        let hook = panic::take_hook();
+        panic::set_hook(Box::new(move |info| {
+            hook(info);
+            notify_shutdown.notify_one();
+        }));
+    }
+
     /// Create Iroha with specified broker, config, and genesis.
     ///
     /// # Errors
@@ -242,7 +250,9 @@ where
             Arc::clone(&notify_shutdown),
         );
 
-        Self::start_listening_signal(notify_shutdown)?;
+        Self::start_listening_signal(Arc::clone(&notify_shutdown))?;
+
+        Self::prepare_panic_hook(notify_shutdown);
 
         let torii = Some(torii);
         Ok(Self {
@@ -352,3 +362,24 @@ fn domains(configuration: &config::Configuration) -> [Domain; 1] {
     let key = configuration.genesis.account_public_key.clone();
     [Domain::from(GenesisDomain::new(key))]
 }
+
+#[cfg(test)]
+mod tests {
+    use std::{panic, thread};
+
+    use super::*;
+
+    #[tokio::test]
+    #[allow(clippy::panic)]
+    async fn iroha_should_notify_on_panic() {
+        let notify = Arc::new(Notify::new());
+        let hook = panic::take_hook();
+        <crate::Iroha>::prepare_panic_hook(Arc::clone(&notify));
+        let _res = thread::spawn(move || {
+            panic!("Test panic");
+        })
+        .join();
+        notify.notified().await;
+        panic::set_hook(hook);
+    }
+}
```
