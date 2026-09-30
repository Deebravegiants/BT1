# [?] update crossbeam-deque to v0.8.1 to fix RUSTSEC-2021-0093

## Summary
Severity: Unknown
Chain: Move
Component: move-language/move
Published: 2021-08-23
Source: https://github.com/move-language/move/commit/6921e11e34e9abb731f3adfaa9efab59795f2c60
Type: security-commit

## Details
update crossbeam-deque to v0.8.1 to fix RUSTSEC-2021-0093

Fixes: #8996
Closes: #8999

## Patch
### Cargo.lock
```diff
@@ -1333,9 +1333,9 @@ dependencies = [
 
 [[package]]
 name = "crossbeam-deque"
-version = "0.8.0"
+version = "0.8.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "94af6efb46fef72616855b036a624cf27ba656ffc9be1b9a3c931cfc7749a9a9"
+checksum = "6455c0ca19f0d2fbf751b908d5c55c1f5cbc65e03c4225427254b46890bdde1e"
 dependencies = [
  "cfg-if 1.0.0",
  "crossbeam-epoch",
```

### common/workspace-hack/Cargo.toml
```diff
@@ -22,7 +22,7 @@ chrono = { version = "0.4.19", features = ["clock", "default", "libc", "oldtime"
 clap = { version = "2.33.3", features = ["ansi_term", "atty", "color", "default", "strsim", "suggestions", "vec_map"] }
 codespan-reporting = { version = "0.11.1", default-features = false, features = ["serde", "serialization"] }
 crossbeam-channel = { version = "0.5.1", features = ["crossbeam-utils", "default", "std"] }
-crossbeam-deque = { version = "0.8.0", features = ["crossbeam-epoch", "crossbeam-utils", "default", "std"] }
+crossbeam-deque = { version = "0.8.1", features = ["crossbeam-epoch", "crossbeam-utils", "default", "std"] }
 crossbeam-utils = { version = "0.8.3", features = ["default", "lazy_static", "std"] }
 either = { version = "1.6.1", features = ["default", "use_std"] }
 futures = { version = "0.3.12", features = ["alloc", "async-await", "default", "executor", "futures-executor", "std"] }
@@ -77,7 +77,7 @@ chrono = { version = "0.4.19", features = ["clock", "default", "libc", "oldtime"
 clap = { version = "2.33.3", features = ["ansi_term", "atty", "color", "default", "strsim", "suggestions", "vec_map"] }
 codespan-reporting = { version = "0.11.1", default-features = false, features = ["serde", "serialization"] }
 crossbeam-channel = { version = "0.5.1", features = ["crossbeam-utils", "default", "std"] }
-crossbeam-deque = { version = "0.8.0", features = ["crossbeam-epoch", "crossbeam-utils", "default", "std"] }
+crossbeam-deque = { version = "0.8.1", features = ["crossbeam-epoch", "crossbeam-utils", "default", "std"] }
 crossbeam-utils = { version = "0.8.3", features = ["default", "lazy_static", "std"] }
 either = { version = "1.6.1", features = ["default", "use_std"] }
 futures = { version = "0.3.12", features = ["alloc", "async-await", "default", "executor", "futures-executor", "std"] }
@@ -135,7 +135,7 @@ chrono = { version = "0.4.19", features = ["clock", "default", "libc", "oldtime"
 clap = { version = "2.33.3", features = ["ansi_term", "atty", "color", "default", "strsim", "suggestions", "vec_map"] }
 codespan-reporting = { version = "0.11.1", default-features = false, features = ["serde", "serialization"] }
 crossbeam-channel = { version = "0.5.1", features = ["crossbeam-utils", "default", "std"] }
-crossbeam-deque = { version = "0.8.0", features = ["crossbeam-epoch", "crossbeam-utils", "default", "std"] }
+crossbeam-deque = { version = "0.8.1", features = ["crossbeam-epoch", "crossbeam-utils", "default", "std"] }
 crossbeam-utils = { version = "0.8.3", features = ["default", "lazy_static", "std"] }
 either = { version = "1.6.1", features = ["default", "use_std"] }
 futures = { version = "0.3.12", features = ["alloc", "async-await", "default", "executor", "futures-executor", "std"] }
@@ -190,7 +190,7 @@ chrono = { version = "0.4.19", features = ["clock", "default", "libc", "oldtime"
 clap = { version = "2.33.3", features = ["ansi_term", "atty", "color", "default", "strsim", "suggestions", "vec_map"] }
 codespan-reporting = { version = "0.11.1", default-features = false, features = ["serde", "serialization"] }
 crossbeam-channel = { version = "0.5.1", features = ["crossbeam-utils", "default", "std"] }
-crossbeam-deque = { version = "0.8.0", features = ["crossbeam-epoch", "crossbeam-utils", "default", "std"] }
+crossbeam-deque = { version = "0.8.1", features = ["crossbeam-epoch", "crossbeam-utils", "default", "std"] }
 crossbeam-utils = { version = "0.8.3", features = ["default", "lazy_static", "std"] }
 either = { version = "1.6.1", features = ["default", "use_std"] }
 futures = { version = "0.3.12", features = ["alloc", "async-await", "default", "executor", "futures-executor", "std"] }
```
