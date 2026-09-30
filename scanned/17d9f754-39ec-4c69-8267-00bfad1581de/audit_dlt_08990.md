# [?] [fix] #3155: Fix panic-hook for tests

## Summary
Severity: Unknown
Chain: Hyperledger Iroha
Component: hyperledger-iroha/iroha
Published: 2023-02-15
Source: https://github.com/hyperledger-iroha/iroha/commit/4ee707a3f52949c188f25104eb33c66ffb87276e
Type: security-commit

## Details
[fix] #3155: Fix panic-hook for tests

Signed-off-by: Daniil Polyakov <arjentix@gmail.com>

## Patch
### Cargo.lock
```diff
@@ -1623,12 +1623,9 @@ dependencies = [
 
 [[package]]
 name = "hermit-abi"
-version = "0.2.6"
+version = "0.3.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "ee512640fe35acbfb4bb779db6f0d80704c2cacfa2e39b601ef3e3f47d1ae4c7"
-dependencies = [
- "libc",
-]
+checksum = "fed44880c466736ef9a5c5b5facefb5ed0785676d0c02d612db14e54f0d84286"
 
 [[package]]
 name = "hex"
@@ -1815,12 +1812,12 @@ checksum = "24c3f4eff5495aee4c0399d7b6a0dc2b6e81be84242ffbfcf253ebacccc1d0cb"
 
 [[package]]
 name = "io-lifetimes"
-version = "1.0.4"
+version = "1.0.5"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "e7d6c6f8c91b4b9ed43484ad1a938e393caf35960fce7f82a040497207bd8e9e"
+checksum = "1abeb7a0dd0f8181267ff8adc397075586500b81b28a73e8a0208b00fc170fb3"
 dependencies = [
  "libc",
- "windows-sys 0.42.0",
+ "windows-sys 0.45.0",
 ]
 
 [[package]]
@@ -1854,6 +1851,7 @@ dependencies = [
  "serial_test",
  "supports-color 2.0.0",
  "thiserror",
+ "thread-local-panic-hook",
  "tokio",
  "vergen",
  "warp",
@@ -2346,14 +2344,14 @@ dependencies = [
 
 [[package]]
 name = "is-terminal"
-version = "0.4.2"
+version = "0.4.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "28dfb6c8100ccc63462345b67d1bbc3679177c75ee4bf59bf29c8b1d110b8189"
+checksum = "22e18b0a45d56fe973d6db23972bf5bc46f988a4a2385deac9cc29572f09daef"
 dependencies = [
- "hermit-abi 0.2.6",
- "io-lifetimes 1.0.4",
- "rustix 0.36.7",
- "windows-sys 0.42.0",
+ "hermit-abi 0.3.1",
+ "io-lifetimes 1.0.5",
+ "rustix 0.36.8",
+ "windows-sys 0.45.0",
 ]
 
 [[package]]
@@ -3497,16 +3495,16 @@ dependencies = [
 
 [[package]]
 name = "rustix"
-version = "0.36.7"
+version = "0.36.8"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "d4fdebc4b395b7fbb9ab11e462e20ed9051e7b16e42d24042c776eca0ac81b03"
+checksum = "f43abb88211988493c1abb44a70efa56ff0ce98f233b7b276146f1f3f7ba9644"
 dependencies = [
  "bitflags",
  "errno",
- "io-lifetimes 1.0.4",
+ "io-lifetimes 1.0.5",
  "libc",
  "linux-raw-sys 0.1.4",
- "windows-sys 0.42.0",
+ "windows-sys 0.45.0",
 ]
 
 [[package]]
@@ -4111,6 +4109,12 @@ dependencies = [
  "winapi",
 ]
 
+[[package]]
+name = "thread-local-panic-hook"
+version = "0.1.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "e70399498abd3ec85f99a2f2d765c8638588e20361678af93a9f47de96719743"
+
 [[package]]
 name = "thread_local"
 version = "1.1.4"
@@ -5054,19 +5058,43 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "5a3e1820f08b8513f676f7ab6c1f99ff312fb97b553d30ff4dd86f9f15728aa7"
 dependencies = [
  "windows_aarch64_gnullvm",
- "windows_aarch64_msvc 0.42.0",
- "windows_i686_gnu 0.42.0",
- "windows_i686_msvc 0.42.0",
- "windows_x86_64_gnu 0.42.0",
+ "windows_aarch64_msvc 0.42.1",
+ "windows_i686_gnu 0.42.1",
+ "windows_i686_msvc 0.42.1",
+ "windows_x86_64_gnu 0.42.1",
+ "windows_x86_64_gnullvm",
+ "windows_x86_64_msvc 0.42.1",
+]
+
+[[package]]
+name = "windows-sys"
+version = "0.45.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "75283be5efb2831d37ea142365f009c02ec203cd29a3ebecbc093d52315b66d0"
+dependencies = [
+ "windows-targets",
+]
+
+[[package]]
+name = "windows-targets"
+version = "0.42.1"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "8e2522491fbfcd58cc84d47aeb2958948c4b8982e9a2d8a2a35bbaed431390e7"
+dependencies = [
+ "windows_aarch64_gnullvm",
+ "windows_aarch64_msvc 0.42.1",
+ "windows_i686_gnu 0.42.1",
+ "windows_i686_msvc 0.42.1",
+ "windows_x86_64_gnu 0.42.1",
  "windows_x86_64_gnullvm",
- "windows_x86_64_msvc 0.42.0",
+ "windows_x86_64_msvc 0.42.1",
 ]
 
 [[package]]
 name = "windows_aarch64_gnullvm"
-version = "0.42.0"
+version = "0.42.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "41d2aa71f6f0cbe00ae5167d90ef3cfe66527d6f613ca78ac8024c3ccab9a19e"
+checksum = "8c9864e83243fdec7fc9c5444389dcbbfd258f745e7853198f365e3c4968a608"
 
 [[package]]
 name = "windows_aarch64_msvc"
@@ -5076,9 +5104,9 @@ checksum = "9bb8c3fd39ade2d67e9874ac4f3db21f0d710bee00fe7cab16949ec184eeaa47"
 
 [[package]]
 name = "windows_aarch64_msvc"
-version = "0.42.0"
+version = "0.42.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "dd0f252f5a35cac83d6311b2e795981f5ee6e67eb1f9a7f64eb4500fbc4dcdb4"
+checksum = "4c8b1b673ffc16c47a9ff48570a9d85e25d265735c503681332589af6253c6c7"
 
 [[package]]
 name = "windows_i686_gnu"
@@ -5088,9 +5116,9 @@ checksum = "180e6ccf01daf4c426b846dfc66db1fc518f074baa793aa7d9b9aaeffad6a3b6"
 
 [[package]]
 name = "windows_i686_gnu"
-version = "0.42.0"
+version = "0.42.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "fbeae19f6716841636c28d695375df17562ca208b2b7d0dc47635a50ae6c5de7"
+checksum = "de3887528ad530ba7bdbb1faa8275ec7a1155a45ffa57c37993960277145d640"
 
 [[package]]
 name = "windows_i686_msvc"
@@ -5100,9 +5128,9 @@ checksum = "e2e7917148b2812d1eeafaeb22a97e4813dfa60a3f8f78ebe204bcc88f12f024"
 
 [[package]]
 name = "windows_i686_msvc"
-version = "0.42.0"
+version = "0.42.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "84c12f65daa39dd2babe6e442988fc329d6243fdce47d7d2d155b8d874862246"
+checksum = "bf4d1122317eddd6ff351aa852118a2418ad4214e6613a50e0191f7004372605"
 
 [[package]]
 name = "windows_x86_64_gnu"
@@ -5112,15 +5140,15 @@ checksum = "4dcd171b8776c41b97521e5da127a2d86ad280114807d0b2ab1e462bc764d9e1"
 
 [[package]]
 name = "windows_x86_64_gnu"
-version = "0.42.0"
+version = "0.42.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "bf7b1b21b5362cbc318f686150e5bcea75ecedc74dd157d874d754a2ca44b0ed"
+checksum = "c1040f221285e17ebccbc2591ffdc2d44ee1f9186324dd3e84e99ac68d699c45"
 
 [[package]]
 name = "windows_x86_64_gnullvm"
-version = "0.42.0"
+version = "0.42.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "09d525d2ba30eeb3297665bd434a54297e4170c7f1a44cad4ef58095b4cd2028"
+checksum = "628bfdf232daa22b0d64fdb62b09fcc36bb01f05a3939e20ab73aaf9470d0463"
 
 [[package]]
 name = "windows_x86_64_msvc"
@@ -5130,9 +5158,9 @@ checksum = "c811ca4a8c853ef420abd8592ba53ddbbac90410fab6903b3e79972a631f7680"
 
 [[package]]
 name = "windows_x86_64_msvc"
-version = "0.42.0"
+version = "0.42.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "f40009d85759725a34da6d89a94e63d7bdc50a862acf0dbc7c8e488f1edcb6f5"
+checksum = "447660ad36a13288b1db4d4248e857b510e8c3a225c822ba4fb748c0aafecffd"
 
 [[package]]
 name = "wyz"
```

### cli/Cargo.toml
```diff
@@ -28,7 +28,7 @@ dev-telemetry = ["iroha_core/dev-telemetry", "iroha_telemetry"]
 schema-endpoint = ["iroha_schema_gen"]
 # Support internal testing infrastructure for integration tests.
 # Disable in production.
-test-network = []
+test-network = ["thread-local-panic-hook"]
 
 [badges]
 is-it-maintained-issue-resolution = { repository = "https://github.com/hyperledger/iroha" }
@@ -65,6 +65,7 @@ serial_test = "0.8.0"
 lazy_static = "1.4.0"
 owo-colors = { version = "3.5.0", features = ["supports-colors"] }
 supports-color = "2.0.0"
+thread-local-panic-hook = { version = "0.1.0", optional = true }
 
 [build-dependencies]
 anyhow = "1.0.68"
```

### cli/src/lib.rs
```diff
@@ -9,7 +9,7 @@
     clippy::std_instead_of_core,
     clippy::std_instead_of_alloc
 )]
-use std::{panic, sync::Arc};
+use std::sync::Arc;
 
 use color_eyre::eyre::{eyre, Result, WrapErr};
 use eyre::ContextCompat as _;
@@ -221,10 +221,30 @@ impl Iroha {
     }
 
     fn prepare_panic_hook(notify_shutdown: Arc<Notify>) {
-        let hook = panic::take_hook();
-        panic::set_hook(Box::new(move |info| {
-            hook(info);
-
+        #[cfg(not(feature = "test-network"))]
+        use std::panic::set_hook;
+
+        // This is a hot-fix for tests
+        //
+        // # Problem
+        //
+        // When running tests in parallel `std::panic::set_hook()` will be set
+        // the same for all threads. That means, that panic in one test can
+        // cause another test shutdown, which we don't want.
+        //
+        // # Downside
+        //
+        // A downside of this approach is that this panic hook will not work for
+        // threads created by Iroha itself (e.g. Sumeragi thread).
+        //
+        // # TODO
+        //
+        // Remove this when all Rust integrations tests will be converted to a
+        // separate Python tests.
+        #[cfg(feature = "test-network")]
+        use thread_local_panic_hook::set_hook;
+
+        set_hook(Box::new(move |info| {
             // What clippy suggests is much less readable in this case
             #[allow(clippy::option_if_let_else)]
             let panic_message = if let Some(message) = info.payload().downcast_ref::<&str>() {
@@ -240,7 +260,7 @@ impl Iroha {
                 |location| format!("{}:{}", location.file(), location.line()),
             );
 
-            iroha_logger::error!(panic_message, location, "A panic occured, shutting down");
+            iroha_logger::error!(panic_message, location, "A panic occurred, shutting down");
 
             // NOTE: shutdown all currently listening waiters
             notify_shutdown.notify_waiters();
@@ -464,8 +484,12 @@ impl Iroha {
 
         let handle = task::spawn(async move {
             tokio::select! {
-                _ = sigint.recv() => {},
-                _ = sigterm.recv() => {},
+                _ = sigint.recv() => {
+                    iroha_logger::info!("SIGINT received, shutting down...");
+                },
+                _ = sigterm.recv() => {
+                    iroha_logger::info!("SIGTERM received, shutting down...");
+                },
             }
 
             // NOTE: shutdown all currently listening waiters
@@ -563,6 +587,7 @@ pub mod style {
     }
 }
 
+#[cfg(not(feature = "test-network"))]
 #[cfg(test)]
 mod tests {
     use std::{iter::repeat, panic, thread};
```
