# [?] fix(client-wasm): install a panic hook so panics keep their message

## Summary
Severity: Unknown
Chain: Fedimint
Component: fedimint/fedimint
Published: 2026-08-24
Source: https://github.com/fedimint/fedimint/commit/ba0cdb50ad869ca0ec26d9461b638964ee52b50c
Type: security-commit

## Details
fix(client-wasm): install a panic hook so panics keep their message

`fedimint-client-wasm` installs no panic hook, so a panic inside one of
the RPC tasks handed to `wasm_bindgen_futures::spawn_local` traps with
a message-less `RuntimeError: unreachable executed` unhandled rejection
and the request never gets a response. The actual panic message and
Rust location never exist anywhere, which made a real crash in
fedimint-sdk's CI effectively undiagnosable (fedimint-sdk#330).

Install `console_error_panic_hook` from a `#[wasm_bindgen(start)]`
function, which runs when the module is instantiated, before any
export can be called, so the hook also covers panics outside
`RpcHandler`. The crate was already pinned in the workspace
dependencies.

The Cargo.lock changes beyond the new package are the resolver
re-pinning existing duplicate-version edges; recent lock commits flip
the same edges back and forth, and any cargo invocation regenerates
them, so they are left as generated.

Fixes #9045.

Assisted-by: Claude Fable 5 (claude-fable-5)

## Patch
### Cargo.lock
```diff
@@ -1736,6 +1736,16 @@ dependencies = [
  "tracing-subscriber",
 ]
 
+[[package]]
+name = "console_error_panic_hook"
+version = "0.1.7"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "a06aeb73f470f66dcdbf7223caeebb85984942f22f1adb2a088cf9668146bbbc"
+dependencies = [
+ "cfg-if",
+ "wasm-bindgen",
+]
+
 [[package]]
 name = "const-oid"
 version = "0.9.6"
@@ -2283,7 +2293,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "ccc2776f0c61eca1ca32528f85548abd1a4be8fb53d1b21c013e4f18da1e7090"
 dependencies = [
  "data-encoding",
- "syn 1.0.109",
+ "syn 2.0.104",
 ]
 
 [[package]]
@@ -2396,7 +2406,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "357422a457ccb850dc8f1c1680e0670079560feaad6c2e247e3f345c4fab8a3f"
 dependencies = [
  "heck 0.5.0",
- "indexmap 1.9.3",
+ "indexmap 2.9.0",
  "itertools 0.14.0",
  "proc-macro-crate",
  "proc-macro2",
@@ -2414,7 +2424,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "caef6056a5788d05d173cdc3c562ac28ae093828f851f69378b74e4e3d578e41"
 dependencies = [
  "heck 0.5.0",
- "indexmap 1.9.3",
+ "indexmap 2.9.0",
  "itertools 0.14.0",
  "proc-macro-crate",
  "proc-macro2",
@@ -2995,7 +3005,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "778e2ac28f6c47af28e4907f13ffd1e1ddbd400980a9abd7c8df189bf578a5ad"
 dependencies = [
  "libc",
- "windows-sys 0.52.0",
+ "windows-sys 0.60.2",
 ]
 
 [[package]]
@@ -3303,6 +3313,7 @@ version = "0.13.0-alpha"
 dependencies = [
  "anyhow",
  "async-trait",
+ "console_error_panic_hook",
  "fedimint-client-rpc",
  "fedimint-connectors",
  "fedimint-core",
@@ -7039,7 +7050,7 @@ dependencies = [
  "once_cell",
  "socket2 0.5.10",
  "tracing",
- "windows-sys 0.52.0",
+ "windows-sys 0.59.0",
 ]
 
 [[package]]
@@ -7142,7 +7153,7 @@ checksum = "e04d7f318608d35d4b61ddd75cbdaee86b023ebe2bd5a66ee0915f0bf93095a9"
 dependencies = [
  "hermit-abi",
  "libc",
- "windows-sys 0.52.0",
+ "windows-sys 0.59.0",
 ]
 
 [[package]]
@@ -7482,7 +7493,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "07033963ba89ebaf1584d767badaa2e8fcec21aedea6b8c0346d487d49c28667"
 dependencies = [
  "cfg-if",
- "windows-targets 0.48.5",
+ "windows-targets 0.53.2",
 ]
 
 [[package]]
@@ -8444,7 +8455,7 @@ dependencies = [
  "pin-project-lite",
  "rustc-hash",
  "rustls 0.23.38",
- "socket2 0.5.10",
+ "socket2 0.6.1",
  "thiserror 2.0.18",
  "tokio",
  "tokio-stream",
@@ -8487,7 +8498,7 @@ checksum = "bde7a5d5102f1cff03d482240f0ed20551661f63663620f4b26112ed751165e9"
 dependencies = [
  "cfg_aliases",
  "libc",
- "socket2 0.5.10",
+ "socket2 0.6.1",
  "tracing",
  "windows-sys 0.61.2",
 ]
@@ -9928,7 +9939,7 @@ dependencies = [
  "once_cell",
  "socket2 0.5.10",
  "tracing",
- "windows-sys 0.52.0",
+ "windows-sys 0.59.0",
 ]
 
 [[package]]
@@ -10463,7 +10474,7 @@ dependencies = [
  "errno",
  "libc",
  "linux-raw-sys 0.4.15",
- "windows-sys 0.52.0",
+ "windows-sys 0.59.0",
 ]
 
 [[package]]
@@ -10476,7 +10487,7 @@ dependencies = [
  "errno",
  "libc",
  "linux-raw-sys 0.9.4",
- "windows-sys 0.52.0",
+ "windows-sys 0.59.0",
 ]
 
 [[package]]
@@ -10556,7 +10567,7 @@ dependencies = [
  "security-framework",
  "security-framework-sys",
  "webpki-root-certs",
- "windows-sys 0.52.0",
+ "windows-sys 0.61.2",
 ]
 
 [[package]]
@@ -10784,7 +10795,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "5b55fb86dfd3a2f5f76ea78310a88f96c4ea21a3031f8d212443d56123fd0521"
 dependencies = [
  "libc",
- "windows-sys 0.52.0",
+ "windows-sys 0.61.2",
 ]
 
 [[package]]
@@ -11642,7 +11653,7 @@ dependencies = [
  "getrandom 0.3.3",
  "once_cell",
  "rustix 1.0.7",
- "windows-sys 0.52.0",
+ "windows-sys 0.59.0",
 ]
 
 [[package]]
@@ -13946,7 +13957,7 @@ version = "0.1.9"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "cf221c93e13a30d793f7645a0e7762c55d169dbb0a49671918a2319d289b10bb"
 dependencies = [
- "windows-sys 0.48.0",
+ "windows-sys 0.59.0",
 ]
 
 [[package]]
```

### fedimint-client-wasm/Cargo.toml
```diff
@@ -20,6 +20,7 @@ path = "src/lib.rs"
 [target.'cfg(target_family = "wasm")'.dependencies]
 anyhow = { workspace = true }
 async-trait = { workspace = true }
+console_error_panic_hook = { workspace = true }
 fedimint-client-rpc = { workspace = true }
 fedimint-connectors = { workspace = true }
 fedimint-core = { workspace = true }
```

### fedimint-client-wasm/src/lib.rs
```diff
@@ -8,6 +8,21 @@ use fedimint_cursed_redb::MemAndRedb;
 use wasm_bindgen::prelude::{JsError, JsValue, wasm_bindgen};
 use web_sys::FileSystemSyncAccessHandle;
 
+/// Runs automatically when the wasm module is instantiated, before any
+/// exported function can be called; calling it again is harmless.
+///
+/// Without a hook, a panic anywhere in the module (including the RPC tasks
+/// spawned via `wasm_bindgen_futures::spawn_local`) traps with a message-less
+/// `RuntimeError: unreachable executed` and the panic message and Rust
+/// location are lost. Log them to the console instead.
+///
+/// When triaging, trust the first logged panic: after it, the executor's
+/// poisoned state may log an unrelated `BorrowMutError` panic as well.
+#[wasm_bindgen(start)]
+fn install_panic_hook() {
+    console_error_panic_hook::set_once();
+}
+
 struct JsFunctionWrapper(js_sys::Function);
 
 impl RpcResponseHandler for JsFunctionWrapper {
```
