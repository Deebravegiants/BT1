# [?] Depend on a tokio commit with the time wheel panic fix

## Summary
Severity: Unknown
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2020-12-14
Source: https://github.com/ZcashFoundation/zebra/commit/b8646fa78ed14c833c26d5337355d0323986f115
Type: security-commit

## Details
Depend on a tokio commit with the time wheel panic fix

Updates the tokio dependency to the commit that merged
tokio-rs/tokio#3229, which should fix the time wheel panic in #1452.

## Patch
### Cargo.lock
```diff
@@ -3158,17 +3158,16 @@ dependencies = [
 [[package]]
 name = "tokio"
 version = "0.3.5"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "a12a3eb39ee2c231be64487f1fcbe726c8f2514876a55480a5ab8559fc374252"
+source = "git+https://github.com/tokio-rs/tokio?rev=9706ca92a8deb69d6e29265f21424042fea966c5#9706ca92a8deb69d6e29265f21424042fea966c5"
 dependencies = [
  "autocfg",
  "bytes 0.6.0",
  "futures-core",
- "lazy_static",
  "libc",
  "memchr",
  "mio 0.7.6",
  "num_cpus",
+ "once_cell",
  "parking_lot",
  "pin-project-lite 0.2.0",
  "signal-hook-registry",
@@ -3181,8 +3180,7 @@ dependencies = [
 [[package]]
 name = "tokio-macros"
 version = "0.3.1"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "21d30fdbb5dc2d8f91049691aa1a9d4d4ae422a21c334ce8936e5886d30c5c45"
+source = "git+https://github.com/tokio-rs/tokio?rev=9706ca92a8deb69d6e29265f21424042fea966c5#9706ca92a8deb69d6e29265f21424042fea966c5"
 dependencies = [
  "proc-macro2 1.0.24",
  "quote 1.0.7",
```

### Cargo.toml
```diff
@@ -21,7 +21,13 @@ panic = "abort"
 panic = "abort"
 
 [patch.crates-io]
+# awaiting tower 0.4
 tower = { git = "https://github.com/tower-rs/tower", rev = "d4d1c67c6a0e4213a52abcc2b9df6cc58276ee39" }
-hyper = { git = "https://github.com/hyperium/hyper/", rev = "ed2b22a7f66899d338691552fbcb6c0f2f4e06b9" }
+
+# fix for #1452, should be included in tokio 0.3.6 or later
+tokio = { git = "https://github.com/tokio-rs/tokio", rev = "9706ca92a8deb69d6e29265f21424042fea966c5" }
+
+# awaiting stable versions which depend on tokio 0.3
+hyper = { git = "https://github.com/hyperium/hyper", rev = "ed2b22a7f66899d338691552fbcb6c0f2f4e06b9" }
 metrics = { git = "https://github.com/ZcashFoundation/metrics", rev = "971133128e5aebe3ad177acffc6154449736cfa2" }
 metrics-exporter-prometheus = { git = "https://github.com/ZcashFoundation/metrics", rev = "971133128e5aebe3ad177acffc6154449736cfa2" }
```
