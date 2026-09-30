# [?] Downgrade tokio to 0.3.4 to avoid a time wheel panic (#1453)

## Summary
Severity: Unknown
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2020-12-04
Source: https://github.com/ZcashFoundation/zebra/commit/b4a50fd99f8d56598ceeb60c2307fea068ab4778
Type: security-commit

## Details
Downgrade tokio to 0.3.4 to avoid a time wheel panic (#1453)

See tokio-rs/tokio#2789 for details. We were seeing this panic during
normal operation, not just at shutdown.

## Patch
### zebra-consensus/Cargo.toml
```diff
@@ -19,7 +19,7 @@ futures = "0.3.7"
 futures-util = "0.3.6"
 metrics = "0.12"
 thiserror = "1.0.22"
-tokio = { version = "0.3", features = ["time", "sync", "stream", "tracing"] }
+tokio = { version = "0.3.4", features = ["time", "sync", "stream", "tracing"] }
 tower = { version = "0.4", features = ["timeout", "util", "buffer"] }
 tower-util = "0.3"
 tracing = "0.1.22"
@@ -34,7 +34,7 @@ zebra-script = { path = "../zebra-script" }
 [dev-dependencies]
 rand = "0.7"
 spandoc = "0.2"
-tokio = { version = "0.3", features = ["full"] }
+tokio = { version = "0.3.4", features = ["full"] }
 tracing-error = "0.1.2"
 tracing-subscriber = "0.2.15"
 
```

### zebra-network/Cargo.toml
```diff
@@ -22,7 +22,7 @@ serde = { version = "1", features = ["serde_derive"] }
 thiserror = "1"
 
 futures = "0.3"
-tokio = { version = "0.3", features = ["net", "time", "stream", "tracing", "macros", "rt-multi-thread"] }
+tokio = { version = "0.3.4", features = ["net", "time", "stream", "tracing", "macros", "rt-multi-thread"] }
 tokio-util = { version = "0.5", features = ["codec"] }
 tower = { version = "0.4", features = ["retry", "discover", "load", "load-shed", "timeout", "util", "buffer"] }
 
```

### zebra-state/Cargo.toml
```diff
@@ -22,7 +22,7 @@ tower = { version = "0.4", features = ["buffer", "util"] }
 tracing = "0.1"
 tracing-error = "0.1.2"
 thiserror = "1.0.22"
-tokio = { version = "0.3", features = ["sync"] }
+tokio = { version = "0.3.4", features = ["sync"] }
 displaydoc = "0.1.7"
 rocksdb = "0.15.0"
 tempdir = "0.3.7"
@@ -37,7 +37,7 @@ zebra-test = { path = "../zebra-test/" }
 once_cell = "1.5"
 spandoc = "0.2"
 tempdir = "0.3.7"
-tokio = { version = "0.3", features = ["full"] }
+tokio = { version = "0.3.4", features = ["full"] }
 proptest = "0.10.1"
 proptest-derive = "0.2"
 primitive-types = "0.7.3"
```

### zebra-test/Cargo.toml
```diff
@@ -25,4 +25,4 @@ proptest = "0.10.1"
 tempdir = "0.3.7"
 
 [dev-dependencies]
-tokio = { version = "0.3", features = ["full"] }
+tokio = { version = "0.3.4", features = ["full"] }
```

### zebrad/Cargo.toml
```diff
@@ -21,7 +21,7 @@ rand = "0.7"
 
 hyper = { version = "0.14.0-dev", features = ["full"] }
 futures = "0.3"
-tokio = { version = "0.3", features = ["time", "rt-multi-thread", "stream", "macros", "tracing", "signal"] }
+tokio = { version = "0.3.4", features = ["time", "rt-multi-thread", "stream", "macros", "tracing", "signal"] }
 tower = { version = "0.4", features = ["hedge", "limit"] }
 pin-project = "0.4.23"
 
```
