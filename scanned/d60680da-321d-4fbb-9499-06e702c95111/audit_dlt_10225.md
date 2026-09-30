# [?] Fix argument parsing crash

## Summary
Severity: Unknown
Chain: Penumbra
Component: penumbra-zone/penumbra
Published: 2022-09-14
Source: https://github.com/penumbra-zone/penumbra/commit/67868045a54dcce060fe1a3f55a49131e45f712c
Type: security-commit

## Details
Fix argument parsing crash

## Patch
### Cargo.lock
```diff
@@ -893,9 +893,9 @@ dependencies = [
 
 [[package]]
 name = "console-subscriber"
-version = "0.1.7"
+version = "0.1.8"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "e933c43a5db3779b3600cdab18856af2411ca2237e33ba8ab476d5d5b1a6c1e7"
+checksum = "22a3a81dfaf6b66bce5d159eddae701e3a002f194d378cbf7be5f053c281d9be"
 dependencies = [
  "console-api",
  "crossbeam-channel",
```

### tct/examples/tct-live-edit.rs
```diff
@@ -25,15 +25,15 @@ struct Args {
     /// This is good to set if exposing this server to concurrent users, because it prevents a DoS
     /// attack where someone keeps adding witnesses until the server runs out of memory and/or
     /// clients fall over because they can't handle the size of the tree.
-    #[clap(long, default_value = "usize::MAX")]
-    max_witnesses: usize,
+    #[clap(long)]
+    max_witnesses: Option<usize>,
     /// The maximum number of times an API call can ask the server to repeat the same operation,
     /// server-side.
     ///
     /// This does not rate-limit repeated requests, but prevents a single request from requiring
     /// more than a certain upper-bound of server-side work.
-    #[clap(long, default_value = "u16::MAX")]
-    max_repeat: u16,
+    #[clap(long)]
+    max_repeat: Option<u16>,
     /// The path to a TLS certificate file to use when serving the demo.
     #[clap(long, required_if("tls_key", "is_some"))]
     tls_cert: Option<PathBuf>,
@@ -59,10 +59,16 @@ async fn main() -> anyhow::Result<()> {
         ..Default::default()
     };
 
-    let app = live::edit(rng, tree, ext, args.max_witnesses, args.max_repeat)
-        .merge(key_control())
-        .merge(main_help())
-        .layer(TraceLayer::new_for_http());
+    let app = live::edit(
+        rng,
+        tree,
+        ext,
+        args.max_witnesses.unwrap_or(usize::MAX),
+        args.max_repeat.unwrap_or(u16::MAX),
+    )
+    .merge(key_control())
+    .merge(main_help())
+    .layer(TraceLayer::new_for_http());
     // TODO: add rate limit layer here
 
     let address = ([0, 0, 0, 0], args.port).into();
```
