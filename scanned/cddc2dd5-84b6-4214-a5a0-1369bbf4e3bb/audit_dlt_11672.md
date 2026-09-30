# [?] Merge bitcoindevkit/bdk#1603: fix(RUSTSEC-2024-0370): proc-macro-error is unmaintained

## Summary
Severity: Unknown
Chain: Bitcoin
Component: bitcoindevkit/bdk
Published: 2024-09-28
Source: https://github.com/bitcoindevkit/bdk/commit/9e47b6473093820937b81f669084fc06ad5161b2
Type: security-commit

## Details
Merge bitcoindevkit/bdk#1603: fix(RUSTSEC-2024-0370): proc-macro-error is unmaintained

d802d00a06035bec582eb5aadf0281f26bff6acd fix(RUSTSEC-2024-0370)!: bump `clap` to latest, removing transitive dependency on `proc-macro-error`. (Leonardo Lima)
45be3172a4abaa94ef2ff55784da31832bdd732a refactor(ci)!: update CI to build and test example in specific job (Leonardo Lima)
519728cd596c3bda60c6e70cbc12b611017e2d7f chore(examples)!: update all examples to have `example_` prefix (Leonardo Lima)
9b7b19586e1f74613f71b6c2403a7df419e13b65 chore: use path as `name` for cargo test targets (Leonardo Lima)
6e8f19607aff55b1949fc7e9f943a333b4fcfb8a fix(bdk_electrum): build with `--no-default-features` (Leonardo Lima)
33942ece8f2f1f0b3d85a201d659cde72a560646 fix(bdk_esplora): build with `--no-default-features` (Leonardo Lima)

Pull request description:

  A candidate for fixing #1593. It builds on top of #1615
  <!-- You can erase any parts of this template not applicable to your Pull Request. -->

  ### Description

  <!-- Describe the purpose of this PR, what's being adding and/or fixed -->

  In https://github.com/bitcoindevkit/bdk/issues/1593 it's mentioned that `proc-macro-error` is unmaintained for the
  past few years, with no fix other than using proc-macro-error2 instead.

  As on our scenario it's merely a transitive dependency of `clap`,
  through `clap_derive` feature, which in latest releases doesn't depend on
  `proc-macro-error` we can just bump it to latest.

  It's valid to note that by bumping it, both examples that relies on clap
  are no longer MSRV (1.63) compliant.

  That said, this PR does:

  - Standardize the example packages to have `example_` prefix.
  - Exclude examples from running in main `Build & Test` CI job.
  - Add new testing step to `Build & Test Example` CI job.
  - Bumps the `clap` to `4.5.17`.

  ### Notes to the reviewers

  <!-- In this section you can include notes directed to the reviewers, like explaining why some parts
  of the PR were done in a specific way -->

  ### Changelog notice

  <!-- Notice the release manager should include in the release tag message changelog -->
  <!-- See https://keepachangelog.com/en/1.0.0/ for examples -->

  - Standardize the example packages to have `example_` prefix.
  - Exclude examples from running in main `Build & Test` CI job.
  - Add new testing step to `Build & Test Example` CI job.
  - Bumps the `clap` to `4.5.17`.

  ### Checklists

  #### All Submissions:

  * [x] I've signed all my commits
  * [x] I followed the [contribution guidelines](https://github.com/bitcoindevkit/bdk/blob/master/CONTRIBUTING.md)
  * [x] I ran `cargo fmt` and `cargo clippy` before committing

  <!--
  #### New Features:

  * [ ] I've added tests for the new feature
  * [ ] I've added docs for the new feature
  -->

  #### Bugfixes:

  * [ ] This pull request breaks the existing API
  * [ ] I've added tests to reproduce the issue which are now passing
  * [x] I'm linking the issue being fixed by this PR

ACKs for top commit:
  ValuedMammal:
    ACK d802d00a06035bec582eb5aadf0281f26bff6acd

Tree-SHA512: 274ddcdf05175fa5bc9c78e81de9ce768b800942a2dd420abc415618948aa84b79f6542d8af0c9ba57adaca48ce91fb854546ece069bd4751598cca4ed8f7560

## Patch
### .github/workflows/cont_integration.yml
```diff
@@ -50,9 +50,9 @@ jobs:
           cargo update -p tokio --precise "1.38.1"
           cargo update -p tokio-util --precise "0.7.11"
       - name: Build
-        run: cargo build ${{ matrix.features }}
+        run: cargo build --workspace --exclude 'example_*' ${{ matrix.features }}
       - name: Test
-        run: cargo test ${{ matrix.features }}
+        run: cargo test --workspace --exclude 'example_*' ${{ matrix.features }}
 
   check-no-std:
     name: Check no_std
@@ -145,7 +145,7 @@ jobs:
           args: --all-features --all-targets -- -D warnings
 
   build-examples:
-    name: Build Examples
+    name: Build & Test Examples
     runs-on: ubuntu-latest
     strategy:
       matrix:
@@ -154,10 +154,10 @@ jobs:
           - example_bitcoind_rpc_polling
           - example_electrum
           - example_esplora
-          - wallet_electrum
-          - wallet_esplora_async
-          - wallet_esplora_blocking
-          - wallet_rpc
+          - example_wallet_electrum
+          - example_wallet_esplora_async
+          - example_wallet_esplora_blocking
+          - example_wallet_rpc
     steps:
       - name: checkout
         uses: actions/checkout@v2
```

### Cargo.toml
```diff
@@ -13,10 +13,10 @@ members = [
     "example-crates/example_electrum",
     "example-crates/example_esplora",
     "example-crates/example_bitcoind_rpc_polling",
-    "example-crates/wallet_electrum",
-    "example-crates/wallet_esplora_blocking",
-    "example-crates/wallet_esplora_async",
-    "example-crates/wallet_rpc",
+    "example-crates/example_wallet_electrum",
+    "example-crates/example_wallet_esplora_blocking",
+    "example-crates/example_wallet_esplora_async",
+    "example-crates/example_wallet_rpc",
 ]
 
 [workspace.package]
```

### crates/electrum/Cargo.toml
```diff
@@ -24,3 +24,7 @@ bdk_chain = { path = "../chain" }
 default = ["use-rustls"]
 use-rustls = ["electrum-client/use-rustls"]
 use-rustls-ring = ["electrum-client/use-rustls-ring"]
+
+[[test]]
+name = "test_electrum"
+required-features = ["use-rustls"]
```

### crates/esplora/Cargo.toml
```diff
@@ -27,10 +27,21 @@ bdk_testenv = { path = "../testenv", default-features = false }
 tokio = { version = "1", features = ["rt", "rt-multi-thread", "macros"] }
 
 [features]
-default = ["std", "async-https", "blocking-https-rustls"]
+default = ["std", "async-https", "blocking-https"]
 std = ["bdk_chain/std", "miniscript?/std"]
 async = ["async-trait", "futures", "esplora-client/async"]
 async-https = ["async", "esplora-client/async-https"]
 async-https-rustls = ["async", "esplora-client/async-https-rustls"]
+async-https-native = ["async", "esplora-client/async-https-native"]
 blocking = ["esplora-client/blocking"]
-blocking-https-rustls = ["esplora-client/blocking-https-rustls"]
+blocking-https = ["blocking", "esplora-client/blocking-https"]
+blocking-https-rustls = ["blocking", "esplora-client/blocking-https-rustls"]
+blocking-https-native = ["blocking", "esplora-client/blocking-https-native"]
+
+[[test]]
+name = "blocking_ext"
+required-features = ["blocking"]
+
+[[test]]
+name = "async_ext"
+required-features = ["async"]
```

### crates/esplora/README.md
```diff
@@ -26,8 +26,11 @@ bdk_esplora = { version = "0.3", features = ["async-https"] }
 To use the extension traits:
 ```rust
 // for blocking
+#[cfg(feature = "blocking")]
 use bdk_esplora::EsploraExt;
+
 // for async
+#[cfg(feature = "async")]
 use bdk_esplora::EsploraAsyncExt;
 ```
 
```

### example-crates/example_cli/Cargo.toml
```diff
@@ -12,7 +12,7 @@ bdk_file_store = { path = "../../crates/file_store" }
 bitcoin = { version = "0.32.0", features = ["base64"], default-features = false }
 
 anyhow = "1"
-clap = { version = "3.2.23", features = ["derive", "env"] }
+clap = { version = "4.5.17", features = ["derive", "env"] }
 rand = "0.8"
 serde = { version = "1", features = ["derive"] }
 serde_json = "1.0"
```

### example-crates/example_wallet_electrum/Cargo.toml
```diff
@@ -1,5 +1,5 @@
 [package]
-name = "wallet_electrum_example"
+name = "example_wallet_electrum"
 version = "0.2.0"
 edition = "2021"
 
```

### example-crates/example_wallet_esplora_async/Cargo.toml
```diff
@@ -1,5 +1,5 @@
 [package]
-name = "wallet_esplora_async"
+name = "example_wallet_esplora_async"
 version = "0.2.0"
 edition = "2021"
 
```

### example-crates/example_wallet_esplora_blocking/Cargo.toml
```diff
@@ -1,5 +1,5 @@
 [package]
-name = "wallet_esplora_blocking"
+name = "example_wallet_esplora_blocking"
 version = "0.2.0"
 edition = "2021"
 publish = false
```
